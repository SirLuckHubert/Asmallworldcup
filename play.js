// aSmallWorldCup — the game on its own, filling the window.
// Same save sync as the site page: the game writes localStorage and calls window.aswcSave(),
// bridge.js passes it up here, and this pushes it to the player's Firebase document.

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
  getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import {
  getFirestore, doc, getDoc, setDoc, onSnapshot, serverTimestamp,
  collection, addDoc, query, orderBy, limit,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";
import { firebaseConfig, GAME_PATH } from "./firebase-config.js?v=2026-09-26e";
import { Net } from "./net.js?v=2026-09-26e";
import { rankOf, rpAfter, rankLine, START_RP } from "./ranks.js?v=2026-09-26e";
import { checkText } from "./words.js?v=2026-09-26e";

const SAVE_KEY = "aswc_save";
const SAVE_DEBOUNCE = 2000;
const $ = (id) => document.getElementById(id);

let auth, db, playerRef = null, frame = null;
let pending = null, saveTimer = null, lastSent = "";
let me = null;                 // {uid, username, rp, muted, banned}
let net = null;                // the peer connection while a match is on
let chatStop = null;

function pane(which) {
  for (const id of ["gate", "banned", "loading"]) $(id).hidden = id !== which;
}

function problem(title, note) {
  $("loadTitle").textContent = title;
  $("loadNote").innerHTML = note;
  pane("loading");
}

// ---------------------------------------------------------------- firebase
if (String(firebaseConfig.apiKey || "").startsWith("PASTE")) {
  problem("Setup needed", "firebase-config.js still has the placeholder values.");
} else {
  try {
    const fb = initializeApp(firebaseConfig);
    auth = getAuth(fb);
    db = getFirestore(fb);
  } catch (err) {
    problem("Couldn't start", "Firebase wouldn't load: " + (err.code || err.message || err));
  }
}

$("signin").onclick = async () => {
  if (!auth) return;
  try {
    await signInWithPopup(auth, new GoogleAuthProvider());
  } catch (err) {
    $("gate").querySelector("p").textContent =
      err.code === "auth/popup-blocked" ? "Allow popups for this site, then try again."
                                        : "Sign-in failed: " + (err.code || err);
  }
};

if (auth) onAuthStateChanged(auth, async (user) => {
  if (!user) {
    stopGame();
    pane("gate");
    return;
  }
  playerRef = doc(db, "players", user.uid);
  let snap;
  try {
    snap = await getDoc(playerRef);
  } catch (err) {
    problem("Couldn't reach your save", "Firebase said: " + (err.code || err) +
            "<br>You can still play from the site page.");
    return;
  }

  if (snap.exists() && snap.data().banned === true) {
    $("banReason").textContent = snap.data().banReason || "This account can't play at the moment.";
    pane("banned");
    return;
  }

  try {
    await setDoc(playerRef, {
      name: user.displayName || "Player",
      email: user.email || "",
      photo: user.photoURL || "",
      lastSeen: serverTimestamp(),
      ...(snap.exists() ? {} : { banned: false }),
    }, { merge: true });
  } catch (err) {
    console.warn("profile write failed", err);
  }

  const d = snap.exists() ? snap.data() : {};
  me = {
    uid: user.uid,
    username: d.username || (user.displayName || "Player").slice(0, 12),
    rp: typeof d.rp === "number" ? d.rp : START_RP,
    muted: !!d.muted,
  };
  if (!d.username) {
    // they haven't picked a name yet: the site page does that, send them there
    problem("Pick a username first", 'Head back to the site and choose a name \u2014 ' +
            'it shows in chat and on the ladder. <br><a class="btn" href="index.html" ' +
            'style="margin-top:14px;display:inline-block">Back to the site</a>');
    return;
  }

  const cloud = d.save || null;
  if (typeof cloud === "string" && cloud.length > 2) {
    try { localStorage.setItem(SAVE_KEY, cloud); } catch (err) { /* private mode */ }
  }
  watchBan();
  watchChat();
  startGame();
});

function watchBan() {
  onSnapshot(playerRef, (s) => {
    if (s.exists() && s.data().banned === true) {
      stopGame();
      $("banReason").textContent = s.data().banReason || "This account can't play at the moment.";
      pane("banned");
    }
  }, () => {});
}

// ---------------------------------------------------------------- the game
async function startGame() {
  if (frame) return;
  try {
    const probe = await fetch(GAME_PATH, { method: "HEAD", cache: "no-store" });
    if (!probe.ok) {
      problem("Game files missing", "Couldn't load <b>" + new URL(GAME_PATH, location.href).pathname +
              "</b> (" + probe.status + "). Upload the pygbag build next to this page.");
      return;
    }
  } catch (err) {
    problem("Game files missing", "Couldn't load the game: " + (err.message || err));
    return;
  }
  frame = document.createElement("iframe");
  frame.title = "aSmallWorldCup";
  // pass switches straight through: play.html?fps=1 -> the game shows its frame rate,
  // play.html?big=1 -> full-size canvas instead of the small one
  const flags = location.search && location.search.length > 1 ? location.search : "";
  frame.allow = "autoplay; fullscreen; gamepad; xr-spatial-tracking";
  frame.setAttribute("allowfullscreen", "");
  frame.setAttribute("webkitallowfullscreen", "");
  frame.src = GAME_PATH + flags;
  frame.onload = () => { pane(null); };          // the game takes the window
  $("stage").appendChild(frame);
  setTimeout(() => {
    if (frame && !$("loading").hidden) $("loadNote").textContent = "Still loading… (big download the first time)";
  }, 9000);
}

function stopGame() {
  flushSave();
  if (frame) { frame.remove(); frame = null; }
}

// ---------------------------------------------------------------- talking to the game
const toGame = (msg) => {
  if (frame && frame.contentWindow) {
    frame.contentWindow.postMessage({ type: "aswc-net", msg: JSON.stringify(msg) }, location.origin);
  }
};
const netState = (up) => {
  if (frame && frame.contentWindow) {
    frame.contentWindow.postMessage({ type: "aswc-netstate", up: !!up }, location.origin);
  }
};

let match = null;          // {ranked, oppUid, oppName, started}

async function findMatch(wants) {
  if (!me || net) return;
  setSync("saving");
  toGame({ t: "searching" });
  net = new Net(db, me.uid);
  net.onState = (state, opp) => {
    netState(state === "playing");
    if (state === "playing") setSync("playing");
  };
  net.onMessage = (msg) => {
    if (!msg) return;
    if (msg.t === "chat") {
      showChat(msg.from || "rival", msg.text || "");
    } else {
      toGame(msg);                       // snapshots and inputs go straight through
    }
  };

  const profile = {
    username: me.username,
    rp: me.rp,
    card: wants.card || null,
    rank: rankLine(rankOf(me.rp)),
  };
  try {
    const found = await net.findMatch(profile, { ranked: wants.ranked !== false });
    const opp = found.opponent || {};
    match = { ranked: wants.ranked !== false, oppUid: opp.uid || null, oppName: opp.username || "Rival", started: Date.now() };
    toGame({
      t: "start",
      role: found.role,
      name: me.username,
      oppName: match.oppName,
      card: wants.card || null,
      oppCard: opp.card || null,
      rank: rankLine(rankOf(me.rp)),
      oppRank: opp.rank || "",
      ranked: match.ranked,
    });
  } catch (err) {
    toGame({ t: "nomatch", why: (err.message || "no game found").toUpperCase() });
    netState(false);
    if (net) { net.cleanup(); net = null; }
  }
}

function endMatch(tellThem) {
  if (net) {
    if (tellThem) net.send({ t: "left" });
    net.cleanup();
    net = null;
  }
  match = null;
  netState(false);
  setSync("ok");
}

// ---------------------------------------------------------------- ranked result
async function recordResult(res) {
  if (!me || !playerRef) return;
  const mine = Number(res.home || 0), theirs = Number(res.away || 0);
  const outcome = mine > theirs ? "win" : mine === theirs ? "draw" : "loss";
  const before = me.rp;
  const after = match && match.ranked ? rpAfter(before, outcome, mine) : before;
  me.rp = after;
  try {
    const snap = await getDoc(playerRef);
    const d = snap.exists() ? (snap.data() || {}) : {};
    await setDoc(playerRef, {
      rp: after,
      wins: (d.wins || 0) + (outcome === "win" ? 1 : 0),
      losses: (d.losses || 0) + (outcome === "loss" ? 1 : 0),
      draws: (d.draws || 0) + (outcome === "draw" ? 1 : 0),
      lastResult: { outcome, mine, theirs, at: serverTimestamp(), opp: match ? match.oppName : "" },
      updatedAt: serverTimestamp(),
    }, { merge: true });
  } catch (err) {
    console.warn("ranked write failed", err);
  }
  const rank = rankOf(after);
  toGame({ t: "chat", from: "LADDER", text: (after - before >= 0 ? "+" : "") + (after - before) + " RP  ·  " + rank.label });
  endMatch(false);
}

// ---------------------------------------------------------------- chat
function showChat(from, text) {
  toGame({ t: "chat", from, text });
}

function watchChat() {
  if (chatStop) chatStop();
  const q = query(collection(db, "chat"), orderBy("at", "desc"), limit(12));
  let first = true;
  chatStop = onSnapshot(q, (snap) => {
    const rows = snap.docs.map((d) => d.data()).reverse();
    if (first) { first = false; return; }            // don't replay the backlog into the game
    const last = rows[rows.length - 1];
    if (last && last.uid !== (me && me.uid)) showChat(last.username || "player", last.text || "");
  }, () => {});
}

async function sendChat(text) {
  if (!me) return;
  const clean = checkText(text);
  if (!clean.ok) {
    showChat("GAME", "THAT MESSAGE WASN'T SENT");
    return;
  }
  if (me.muted) {
    showChat("GAME", "YOU'RE MUTED");
    return;
  }
  try {
    await addDoc(collection(db, "chat"), {
      uid: me.uid, username: me.username, text: String(text).slice(0, 200), at: serverTimestamp(),
    });
  } catch (err) {
    showChat("GAME", "MESSAGE DIDN'T SEND");
  }
  if (net && net.connected) net.send({ t: "chat", from: me.username, text: String(text).slice(0, 200) });
}

// ---------------------------------------------------------------- saves
window.addEventListener("message", (e) => {
  if (e.origin !== location.origin || !e.data) return;
  if (e.data.type === "aswc-ready") {
    let text = null;
    try { text = localStorage.getItem(SAVE_KEY); } catch (err) { /* ignore */ }
    if (text && frame) frame.contentWindow.postMessage({ type: "aswc-load", save: text }, location.origin);
  } else if (e.data.type === "aswc-save" && typeof e.data.save === "string") {
    pending = e.data.save;
    setSync("saving");
    clearTimeout(saveTimer);
    saveTimer = setTimeout(flushSave, SAVE_DEBOUNCE);
  } else if (e.data.type === "aswc-net" && e.data.msg) {
    let msg = null;
    try { msg = JSON.parse(e.data.msg); } catch (err) { return; }
    if (!msg) return;
    if (msg.t === "find") findMatch(msg);
    else if (msg.t === "cancel" || msg.t === "leave") endMatch(msg.t === "leave");
    else if (net && net.connected) net.send(msg);          // snapshots / inputs / chat
  } else if (e.data.type === "aswc-chat" && e.data.text) {
    sendChat(e.data.text);
  } else if (e.data.type === "aswc-result" && e.data.result) {
    let res = null;
    try { res = JSON.parse(e.data.result); } catch (err) { return; }
    if (res) recordResult(res);
  }
});

window.addEventListener("beforeunload", () => { if (net) net.cleanup(); });

async function flushSave() {
  clearTimeout(saveTimer);
  if (!pending || !playerRef || pending === lastSent) return;
  const text = pending;
  pending = null;
  try {
    await setDoc(playerRef, { save: text, updatedAt: serverTimestamp() }, { merge: true });
    lastSent = text;
    setSync("ok");
  } catch (err) {
    setSync("error");
    if (err.code === "permission-denied") {
      stopGame();
      pane("banned");
    } else {
      pending = text;
    }
  }
}

window.addEventListener("beforeunload", flushSave);
setInterval(flushSave, 30000);

// Nothing sits over the game except the fullscreen button, so the save state only
// speaks up when it has something to say.
function setSync(state) {
  const note = $("note");
  if (!note) return;
  if (state === "error") {
    note.textContent = "Couldn't save — check your connection";
    note.hidden = false;
  } else if (state === "playing") {
    note.hidden = true;
  } else {
    note.hidden = true;
  }
}

// ---------------------------------------------------------------- fullscreen
// The window is already the game; this is for hiding the browser's own chrome.
function fullscreenOn() {
  return !!(document.fullscreenElement || document.webkitFullscreenElement);
}

$("fs").onclick = () => {
  const el = document.documentElement;
  if (fullscreenOn()) {
    (document.exitFullscreen || document.webkitExitFullscreen || (() => {})).call(document);
    return;
  }
  const req = el.requestFullscreen || el.webkitRequestFullscreen || el.webkitRequestFullScreen;
  if (req) {
    try { const out = req.call(el); if (out && out.catch) out.catch(() => {}); } catch (err) { /* iPad */ }
  }
};

for (const ev of ["fullscreenchange", "webkitfullscreenchange"]) {
  document.addEventListener(ev, () => {
    document.body.classList.toggle("fs-on", fullscreenOn());
    $("fs").textContent = fullscreenOn() ? "\u2715" : "\u26F6";
    $("fs").title = fullscreenOn() ? "Leave fullscreen" : "Fullscreen";
  });
}

// F also works, since the game itself never uses it
window.addEventListener("keydown", (e) => {
  if ((e.key === "f" || e.key === "F") && !e.metaKey && !e.ctrlKey && !e.altKey) $("fs").click();
});
