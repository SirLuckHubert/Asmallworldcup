// A SMALL WORLD CUP fan game - sign-in, cloud saves, bans, patch notes.
// Static page: everything runs in the browser against Firebase.

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
  getAuth, GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import {
  getFirestore, doc, getDoc, setDoc, onSnapshot, serverTimestamp,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";
import { firebaseConfig, ADMIN_EMAIL, GAME_PATH } from "./firebase-config.js";

const SAVE_KEY = "aswc_save";          // the game reads/writes this in localStorage
const SAVE_DEBOUNCE = 2000;            // ms of quiet before a save goes to the cloud

window.__aswcBooted = true;            // the watchdog in index.html checks this

const $ = (id) => document.getElementById(id);
const gate = $("gate"), app = $("app"), bannedView = $("banned");

const DEFAULT_NOTES = [
  {
    date: "2026-09-23",
    title: "Web version",
    body: "The game now runs in the browser. Sign in with Google and your cards, coins, squad and season are saved to your account.\n" +
          "The ball is 40% slower and now takes the movement of whatever body part touches it — run into it and it goes with you.\n" +
          "New card: Pedro Neto (150, Chelsea). Ren Aoyagi has left the game.",
  },
];

let toastTimer = null;
function toast(msg, ms = 2600) {
  const t = $("toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove("show"), ms);
}

function show(which) {
  for (const el of [gate, app, bannedView]) el.hidden = el !== which;
}

// ---------------------------------------------------------------- firebase
let auth, db, me = null, playerRef = null;

function setupNeeded(why) {
  document.body.innerHTML =
    '<div class="wrap"><section class="panel"><h2>Setup needed</h2>' +
    '<p class="muted">' + why + '</p></section></div>';
}

show(gate);                                   // until Firebase tells us who you are
if (String(firebaseConfig.apiKey || "").startsWith("PASTE")) {
  setupNeeded("firebase-config.js still has the placeholder values. Follow the steps at the top " +
              "of that file (and paste firestore.rules into Firebase), then reload.");
} else {
  try {
    const fb = initializeApp(firebaseConfig);
    auth = getAuth(fb);
    db = getFirestore(fb);
  } catch (err) {
    console.error(err);
    setupNeeded("Firebase wouldn't start: " + (err.code || err.message || err));
  }
}

$("signin").onclick = async () => {
  if (!auth) return;
  try {
    await signInWithPopup(auth, new GoogleAuthProvider());
  } catch (err) {
    toast(err.code === "auth/popup-blocked" ? "Allow popups to sign in" : "Sign-in failed: " + err.code, 4000);
  }
};
const doSignOut = () => auth && signOut(auth);
$("signout").onclick = doSignOut;
$("signout2").onclick = doSignOut;

if (auth) onAuthStateChanged(auth, async (user) => {
  me = user;
  if (!user) {
    show(gate);
    stopGame();
    return;
  }
  playerRef = doc(db, "players", user.uid);
  let snap;
  try {
    snap = await getDoc(playerRef);
  } catch (err) {
    toast("Could not reach your save: " + err.code, 5000);
    return;
  }

  if (snap.exists() && snap.data().banned === true) {
    $("banReason").textContent = snap.data().banReason || "This account can't play at the moment.";
    show(bannedView);
    return;
  }

  // keep the player card up to date (name/photo can change)
  const profile = {
    name: user.displayName || "Player",
    email: user.email || "",
    photo: user.photoURL || "",
    lastSeen: serverTimestamp(),
  };
  if (!snap.exists()) profile.banned = false;
  try {
    await setDoc(playerRef, profile, { merge: true });
  } catch (err) {
    console.warn("profile write failed", err);
  }

  $("avatar").src = user.photoURL || "";
  $("uname").textContent = user.displayName || user.email;
  const isAdmin = (user.email || "").toLowerCase() === ADMIN_EMAIL.toLowerCase();
  $("adminTag").hidden = !isAdmin;
  $("adminLink").hidden = !isAdmin;

  // put the cloud save where the game will look for it (same origin as the iframe)
  const cloud = snap.exists() ? snap.data().save : null;
  if (typeof cloud === "string" && cloud.length > 2) {
    try { localStorage.setItem(SAVE_KEY, cloud); } catch (err) { /* private mode */ }
  }
  show(app);
  watchBan();
  watchNotes();
});

// a ban lands while you're playing: pull the game straight away
let banWatch = null;
function watchBan() {
  if (banWatch) banWatch();
  banWatch = onSnapshot(playerRef, (s) => {
    if (s.exists() && s.data().banned === true) {
      stopGame();
      $("banReason").textContent = s.data().banReason || "This account can't play at the moment.";
      show(bannedView);
    }
  }, () => {});
}

// ---------------------------------------------------------------- the game
let frame = null, pending = null, saveTimer = null, lastSent = "";

function startGame() {
  if (frame) return;
  $("loadNote").hidden = false;
  $("play").disabled = true;
  frame = document.createElement("iframe");
  frame.title = "Ragdoll Football";
  frame.allow = "autoplay; fullscreen; gamepad";
  frame.src = GAME_PATH;
  frame.onload = () => { $("cover").hidden = true; };
  frame.onerror = () => toast("Game files missing - run build_web.sh", 5000);
  $("holder").appendChild(frame);
  setTimeout(() => {
    if (frame && !$("cover").hidden) $("loadNote").textContent = "Still loading… (large download the first time)";
  }, 9000);
}

function stopGame() {
  flushSave();
  if (frame) { frame.remove(); frame = null; }
  $("cover").hidden = false;
  $("play").disabled = false;
  $("loadNote").hidden = true;
}

$("play").onclick = startGame;
$("fullscreen").onclick = () => {
  const el = $("holder");
  if (document.fullscreenElement) document.exitFullscreen();
  else el.requestFullscreen && el.requestFullscreen();
};

// the game calls window.aswcSave(text) inside the frame; bridge.js posts it up here
window.addEventListener("message", (e) => {
  if (e.origin !== location.origin || !e.data) return;
  if (e.data.type === "aswc-ready") {
    // hand the frame the save we loaded from the cloud
    let text = null;
    try { text = localStorage.getItem(SAVE_KEY); } catch (err) { /* ignore */ }
    if (text && frame) frame.contentWindow.postMessage({ type: "aswc-load", save: text }, location.origin);
  } else if (e.data.type === "aswc-save" && typeof e.data.save === "string") {
    queueSave(e.data.save);
  }
});

function queueSave(text) {
  pending = text;
  setSync("saving");
  clearTimeout(saveTimer);
  saveTimer = setTimeout(flushSave, SAVE_DEBOUNCE);
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
      show(bannedView);
    } else {
      pending = text;                       // try again on the next save
    }
  }
}

window.addEventListener("beforeunload", () => {
  // best effort: the browser may not wait for this
  flushSave();
});
setInterval(flushSave, 30000);              // and a slow heartbeat while you play

function setSync(state) {
  const dot = $("syncDot"), text = $("syncText");
  dot.className = "dot" + (state === "ok" ? " on" : state === "error" ? " err" : "");
  text.textContent = state === "saving" ? "Saving…"
    : state === "ok" ? "Progress saved to your account"
    : state === "error" ? "Couldn't save — check your connection"
    : "Progress saves to your account";
}

// ---------------------------------------------------------------- patch notes
function watchNotes() {
  const ref = doc(db, "site", "patchNotes");
  onSnapshot(ref, (s) => {
    const entries = (s.exists() && Array.isArray(s.data().entries) && s.data().entries.length)
      ? s.data().entries : DEFAULT_NOTES;
    renderNotes(entries);
  }, () => renderNotes(DEFAULT_NOTES));
}

function renderNotes(entries) {
  const box = $("notes");
  box.textContent = "";
  for (const n of entries.slice(0, 12)) {
    const wrap = document.createElement("article");
    wrap.className = "note";
    const h = document.createElement("h3");
    h.textContent = n.title || "Update";
    const t = document.createElement("time");
    t.textContent = n.date || "";
    const d = document.createElement("div");
    d.textContent = n.body || "";
    wrap.append(h, t, d);
    box.appendChild(wrap);
  }
}
