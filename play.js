// aSmallWorldCup — the game on its own, filling the window.
// Same save sync as the site page: the game writes localStorage and calls window.aswcSave(),
// bridge.js passes it up here, and this pushes it to the player's Firebase document.

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
  getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import {
  getFirestore, doc, getDoc, setDoc, onSnapshot, serverTimestamp,
  collection, addDoc, query, orderBy, limit, runTransaction,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";
import { firebaseConfig, GAME_PATH, ADMIN_EMAIL, ADS_CLIENT, ADS_TEST } from "./firebase-config.js?v=2026-11-06h";
import { Net } from "./net.js?v=2026-11-06h";
import { rankOf, rpAfter, rankLine, START_RP } from "./ranks.js?v=2026-11-06h";
import { checkText } from "./words.js?v=2026-11-06h";
import { mergeIntoSaveText } from "./mail.js?v=2026-11-06h";

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
    owner: String(user.email || "").toLowerCase() === String(ADMIN_EMAIL).toLowerCase(),   // 6 Nov
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

  let cloud = typeof d.save === "string" && d.save.length > 2 ? d.save : null;
  // messages sent to everyone are merged in even for a player with no save yet
  let base = cloud;
  if (!base) {
    try { base = localStorage.getItem(SAVE_KEY) || "{}"; } catch (err) { base = "{}"; }
  }
  const merged = await withBroadcastMail(base);
  if (merged) cloud = merged;
  if (cloud) {
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

/**
 * Messages the admin sent to everyone live in site/mail. Merge any the player hasn't got
 * into their save before the game loads it, and push the save back so it sticks.
 */
async function withBroadcastMail(text) {
  try {
    const snap = await getDoc(doc(db, "site", "mail"));
    let items = snap.exists() && Array.isArray(snap.data().items) ? snap.data().items : [];
    try {                                                 // + whatever Scout RNG sent you (coins, a player)
      const ls = await getDoc(doc(db, "lounge", playerRef.id));
      if (ls.exists() && Array.isArray(ls.data().mail)) items = items.concat(ls.data().mail);
    } catch (err) { /* no lounge doc yet */ }
    const merged = mergeIntoSaveText(text, items);
    if (!merged) return null;
    await setDoc(playerRef, { save: merged, updatedAt: serverTimestamp() }, { merge: true });
    lastSent = merged;
    return merged;
  } catch (err) {
    return null;                                          // mail is never worth blocking play
  }
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
    const old = net;
    net = null;
    if (tellThem) {
      old.send({ t: "left" });
      setTimeout(() => old.cleanup(), 400);     // let "left" get there before the line closes
    } else {
      old.cleanup();
    }
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
    // 6 Nov: the owner's two profile pictures unlock only for the admin account
    if (frame) frame.contentWindow.postMessage({ type: "aswc-owner", owner: !!(me && me.owner) }, location.origin);
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
  } else if (e.data.type === "aswc-ad") {
    showRewardAd();
  } else if (e.data.type === "aswc-code") {
    codePrompt();
  } else if (e.data.type === "aswc-result" && e.data.result) {
    let res = null;
    try { res = JSON.parse(e.data.result); } catch (err) { return; }
    if (res) recordResult(res);
  }
});

window.addEventListener("beforeunload", () => { if (net) net.cleanup(); });

// ---------------------------------------------------------------- codes (6 Nov)
// The game's CODES button posts "aswc-code"; this asks for the code, checks it in Firestore and uses it
// up for this account in one go (a transaction: the claim + one more "used"), then hands the game
// "aswc-coderesult" {ok, why, code, gift}.
function codeAnswer(msg) {
  if (frame) frame.contentWindow.postMessage(Object.assign({ type: "aswc-coderesult" }, msg), location.origin);
}

async function redeemCode(raw) {
  const code = String(raw || "").toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 20);
  if (!code) return codeAnswer({ ok: false, why: "empty" });
  if (!me || !db) return codeAnswer({ ok: false, why: "offline" });
  const ref = doc(db, "codes", code);
  const claim = doc(db, "codes", code, "claims", me.uid);
  try {
    const gift = await runTransaction(db, async (tx) => {
      const c = await tx.get(ref);
      if (!c.exists()) throw new Error("nocode");
      const d = c.data();
      if (d.expires && Date.now() > d.expires) throw new Error("expired");
      if ((d.used || 0) >= (d.max || 0)) throw new Error("full");
      if ((await tx.get(claim)).exists()) throw new Error("used");
      tx.update(ref, { used: (d.used || 0) + 1 });
      tx.set(claim, { at: Date.now(), name: String(me.username || "").slice(0, 24) });
      return { gems: d.gems || 0, coins: d.coins || 0, packs: d.packs || 0 };
    });
    codeAnswer({ ok: true, code, gift });
  } catch (err) {
    const why = ["nocode", "expired", "full", "used"].includes(err && err.message) ? err.message : "error";
    codeAnswer({ ok: false, why, code });
  }
}

function codePrompt() {
  const box = document.createElement("div");
  box.style.cssText = "position:fixed;inset:0;z-index:50;display:flex;align-items:center;justify-content:center;" +
    "background:rgba(4,8,24,.72);font-family:system-ui,sans-serif";
  box.innerHTML = '<form style="background:#101a3e;border:2px solid #7fd8ff;border-radius:18px;padding:26px 30px;' +
    'width:min(360px,86vw);text-align:center;color:#fff"><div style="font-size:22px;font-weight:800;margin-bottom:12px">' +
    'Enter a code</div><input id="codeIn" maxlength="20" autocomplete="off" autocapitalize="characters" ' +
    'style="width:100%;box-sizing:border-box;font:inherit;font-size:22px;font-weight:800;letter-spacing:2px;' +
    'text-align:center;text-transform:uppercase;padding:10px;border-radius:12px;border:1px solid #7f8fc0;' +
    'background:#060c24;color:#fff;margin-bottom:16px"><br><button type="submit" style="font:inherit;font-weight:800;' +
    'padding:10px 22px;border-radius:12px;border:0;background:#38e0b8;color:#04221c;margin-right:10px;cursor:pointer">' +
    'REDEEM</button><button type="button" id="codeNo" style="font:inherit;padding:10px 18px;border-radius:12px;' +
    'border:1px solid #7f8fc0;background:transparent;color:#cfd8ff;cursor:pointer">CANCEL</button></form>';
  document.body.appendChild(box);
  const input = box.querySelector("#codeIn");
  input.focus();
  box.querySelector("form").onsubmit = (ev) => { ev.preventDefault(); const v = input.value; box.remove(); redeemCode(v); };
  box.querySelector("#codeNo").onclick = () => { box.remove(); codeAnswer({ ok: false, why: "cancel" }); };
}

// ---------------------------------------------------------------- rewarded ads (6 Nov, Season 1)
// The game's WATCH AD button posts "aswc-ad" up to here. Google's H5 Games Ads (the Ad Placement API)
// shows the ad over the page; the game hears back "aswc-adresult" {ok, why} and pays the gems only
// when ok. Google asks for the ad to start from a click on the page itself, so when an ad is ready a
// small "watch it?" box comes up and its button starts the ad.
let adsLoaded = false, adBusy = false;

function adAnswer(ok, why) {
  adBusy = false;
  if (frame) frame.contentWindow.postMessage({ type: "aswc-adresult", ok: !!ok, why: why || "" }, location.origin);
}

function loadAds() {
  if (adsLoaded) return;
  adsLoaded = true;
  window.adsbygoogle = window.adsbygoogle || [];
  window.adBreak = window.adConfig = function (o) { window.adsbygoogle.push(o); };
  const s = document.createElement("script");
  s.async = true;
  s.crossOrigin = "anonymous";
  s.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + encodeURIComponent(ADS_CLIENT);
  s.setAttribute("data-ad-client", ADS_CLIENT);
  s.setAttribute("data-ad-frequency-hint", "30s");
  if (ADS_TEST) s.setAttribute("data-adbreak-test", "on");
  document.head.appendChild(s);
  window.adConfig({ preloadAdBreaks: "on", sound: "on" });
}

function adPrompt(onWatch, onSkip) {
  const box = document.createElement("div");
  box.style.cssText = "position:fixed;inset:0;z-index:50;display:flex;align-items:center;justify-content:center;" +
    "background:rgba(4,8,24,.72);font-family:system-ui,sans-serif";
  box.innerHTML = '<div style="background:#101a3e;border:2px solid #7fd8ff;border-radius:18px;padding:26px 30px;' +
    'max-width:360px;text-align:center;color:#fff"><div style="font-size:22px;font-weight:800;margin-bottom:8px">' +
    'Watch a short ad?</div><div style="opacity:.8;margin-bottom:18px">Watch it to the end for GEMS.</div>' +
    '<button id="adGo" style="font:inherit;font-weight:800;padding:10px 22px;border-radius:12px;border:0;' +
    'background:#38e0b8;color:#04221c;margin-right:10px;cursor:pointer">WATCH</button>' +
    '<button id="adNo" style="font:inherit;padding:10px 18px;border-radius:12px;border:1px solid #7f8fc0;' +
    'background:transparent;color:#cfd8ff;cursor:pointer">NOT NOW</button></div>';
  document.body.appendChild(box);
  box.querySelector("#adGo").onclick = () => { box.remove(); onWatch(); };
  box.querySelector("#adNo").onclick = () => { box.remove(); onSkip(); };
}

function showRewardAd() {
  if (!ADS_CLIENT) return adAnswer(false, "noads");
  if (adBusy) return;
  adBusy = true;
  loadAds();
  let answered = false, viewed = false;
  const done = (ok, why) => { if (!answered) { answered = true; adAnswer(ok, why); } };
  try {
    window.adBreak({
      type: "reward",
      name: "gems",
      beforeReward: (showAdFn) => adPrompt(() => showAdFn(), () => done(false, "skipped")),
      adDismissed: () => done(false, "skipped"),
      adViewed: () => { viewed = true; done(true, ""); },
      adBreakDone: (info) => done(viewed, viewed ? "" : ((info && info.breakStatus) || "noad")),
    });
  } catch (err) {
    done(false, "noad");
  }
}

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
