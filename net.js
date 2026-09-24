// Online play: matchmaking through Firestore, then a direct WebRTC data channel between the
// two players. Firestore only carries the handshake (a few writes), so the match itself runs
// peer to peer at normal game latency rather than at database speed.
//
// The host simulates the match and sends snapshots; the guest sends its throws. All of that
// lives in the game — this file is the pipe.

import {
  doc, getDoc, setDoc, updateDoc, deleteDoc, onSnapshot, collection, getDocs,
  query, where, limit, serverTimestamp,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

const ICE = {
  iceServers: [
    { urls: ["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302"] },
  ],
};

export class Net {
  constructor(db, uid) {
    this.db = db;
    this.uid = uid;
    this.pc = null;
    this.chan = null;
    this.matchId = null;
    this.role = null;              // "host" | "guest"
    this.stop = [];                // snapshot unsubscribers
    this.onMessage = () => {};
    this.onState = () => {};       // "searching" | "found" | "connecting" | "playing" | "ended"
    this.opponent = null;
  }

  say(state, extra) { this.onState(state, extra); }

  /** Find someone waiting, or wait to be found. Resolves once the channel is open. */
  async findMatch(profile, { ranked = true, timeout = 60000 } = {}) {
    this.cleanup();
    this.say("searching");
    const queueRef = collection(this.db, "queue");
    let joined = null;

    // is anyone already waiting?
    try {
      joined = await this.lookForHost(ranked, false);
    } catch (err) {
      throw new Error("matchmaking unavailable (" + (err.code || err.message) + ")");
    }

    if (joined) return this.joinAsGuest(joined, profile, ranked);
    return this.waitAsHost(profile, ranked, timeout);
  }

  /**
   * Someone in the queue we could join. Two players who press Play in the same second both
   * end up waiting as hosts, so a waiting host re-runs this with paired=true: it then only
   * takes a rival whose id sorts below its own, which makes exactly one of the pair give way.
   */
  async lookForHost(ranked, paired) {
    const waiting = await getDocs(query(collection(this.db, "queue"), where("ranked", "==", ranked), limit(8)));
    for (const d of waiting.docs) {
      if (d.id === this.uid) continue;
      const data = d.data() || {};
      if (Date.now() - (data.at || 0) > 45000) continue;   // stale
      if (paired) {
        if (!data.matchId) continue;                       // not ready to be joined yet
        if (d.id >= this.uid) continue;                    // let them join us instead
      }
      // a queue document only exists while its host is still waiting: both sides delete it
      // as soon as the channel opens, so anything here is fair game.
      return { id: d.id, ...data };
    }
    return null;
  }

  // ---------------------------------------------------------------- host
  async waitAsHost(profile, ranked, timeout) {
    this.role = "host";
    this.matchId = "m" + this.uid.slice(0, 6) + Date.now().toString(36);
    await setDoc(doc(this.db, "queue", this.uid), {
      ...profile, uid: this.uid, ranked, at: Date.now(), matchId: null,
    });

    this.pc = new RTCPeerConnection(ICE);
    this.chan = this.pc.createDataChannel("aswc", { ordered: false, maxRetransmits: 0 });
    this.wireChannel();

    const matchRef = doc(this.db, "matches", this.matchId);
    const offer = await this.pc.createOffer();
    await this.pc.setLocalDescription(offer);
    await this.iceSettled();
    await setDoc(matchRef, {
      host: { ...profile, uid: this.uid },
      offer: JSON.stringify(this.pc.localDescription),
      ranked, at: serverTimestamp(),
    });
    await updateDoc(doc(this.db, "queue", this.uid), { matchId: this.matchId });

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        clearInterval(rescan);
        this.cleanup();
        reject(new Error("nobody else is looking for a game right now"));
      }, timeout);

      // both of us pressed Play at once? one of us switches to being the guest
      const rescan = setInterval(async () => {
        if (this.connected || this.role !== "host") return;
        let rival = null;
        try { rival = await this.lookForHost(ranked, true); } catch (err) { return; }
        if (!rival || this.connected) return;
        clearInterval(rescan);
        clearTimeout(timer);
        try { await deleteDoc(doc(this.db, "matches", this.matchId)); } catch (err) { /* fine */ }
        this.cleanup();
        try {
          resolve(await this.joinAsGuest(rival, profile, ranked));
        } catch (err) {
          reject(err);
        }
      }, 3500);

      this.stop.push(onSnapshot(matchRef, async (snap) => {
        const data = snap.data();
        if (!data || !data.answer || this.pc.currentRemoteDescription) return;
        this.opponent = data.guest || null;
        this.say("found", this.opponent);
        try {
          await this.pc.setRemoteDescription(JSON.parse(data.answer));
        } catch (err) { /* already set */ }
      }, () => {}));

      this.ready = () => {
        clearTimeout(timer);
        clearInterval(rescan);
        resolve({ role: "host", opponent: this.opponent, matchId: this.matchId });
      };
    });
  }

  // ---------------------------------------------------------------- guest
  async joinAsGuest(host, profile, ranked) {
    this.role = "guest";
    this.matchId = host.matchId;
    if (!this.matchId) {                       // host hasn't written its offer yet
      this.matchId = await this.waitForMatchId(host.id);
    }
    const matchRef = doc(this.db, "matches", this.matchId);
    const snap = await getDoc(matchRef);
    const data = snap.data();
    if (!data || !data.offer) throw new Error("that game vanished — try again");
    this.opponent = data.host || null;
    this.say("found", this.opponent);

    this.pc = new RTCPeerConnection(ICE);
    this.pc.ondatachannel = (e) => { this.chan = e.channel; this.wireChannel(); };
    await this.pc.setRemoteDescription(JSON.parse(data.offer));
    const answer = await this.pc.createAnswer();
    await this.pc.setLocalDescription(answer);
    await this.iceSettled();
    await updateDoc(matchRef, {
      answer: JSON.stringify(this.pc.localDescription),
      guest: { ...profile, uid: this.uid },
    });
    try { await deleteDoc(doc(this.db, "queue", host.id)); } catch (err) { /* host cleans up too */ }

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.cleanup();
        reject(new Error("couldn't connect to that player"));
      }, 20000);
      this.ready = () => { clearTimeout(timer); resolve({ role: "guest", opponent: this.opponent, matchId: this.matchId }); };
    });
  }

  async waitForMatchId(hostId) {
    for (let i = 0; i < 20; i++) {
      const s = await getDoc(doc(this.db, "queue", hostId));
      const id = s.exists() ? s.data().matchId : null;
      if (id) return id;
      await new Promise((r) => setTimeout(r, 400));
    }
    throw new Error("that game vanished — try again");
  }

  // ---------------------------------------------------------------- plumbing
  /** Gather ICE candidates into the description instead of trickling them through Firestore. */
  iceSettled() {
    return new Promise((resolve) => {
      if (this.pc.iceGatheringState === "complete") return resolve();
      const done = () => {
        if (this.pc.iceGatheringState === "complete") {
          this.pc.removeEventListener("icegatheringstatechange", done);
          resolve();
        }
      };
      this.pc.addEventListener("icegatheringstatechange", done);
      setTimeout(resolve, 2500);            // good enough: send what we have
    });
  }

  wireChannel() {
    this.chan.onopen = () => {
      this.say("playing", this.opponent);
      if (this.ready) this.ready();
      this.tidyQueue();
    };
    this.chan.onclose = () => this.say("ended");
    this.chan.onerror = () => this.say("ended");
    this.chan.onmessage = (e) => {
      let msg = null;
      try { msg = JSON.parse(e.data); } catch (err) { return; }
      this.onMessage(msg);
    };
  }

  send(msg) {
    if (!this.chan || this.chan.readyState !== "open") return false;
    try { this.chan.send(JSON.stringify(msg)); return true; } catch (err) { return false; }
  }

  get connected() { return !!this.chan && this.chan.readyState === "open"; }

  async tidyQueue() {
    try { await deleteDoc(doc(this.db, "queue", this.uid)); } catch (err) { /* fine */ }
  }

  cleanup() {
    for (const off of this.stop) { try { off(); } catch (err) { /* ignore */ } }
    this.stop = [];
    if (this.chan) { try { this.chan.close(); } catch (err) { /* ignore */ } this.chan = null; }
    if (this.pc) { try { this.pc.close(); } catch (err) { /* ignore */ } this.pc = null; }
    this.tidyQueue();
  }
}
