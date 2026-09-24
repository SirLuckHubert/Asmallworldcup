// aSmallWorldCup — sign-in, cloud saves, bans, patch notes, and the page itself.
// Static site: everything runs in the browser against Firebase.

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

// sections fade in as they arrive (defined early: the patch notes use it on first paint)
const revealObserver = ("IntersectionObserver" in window)
  ? new IntersectionObserver((rows) => {
      for (const row of rows) {
        if (row.isIntersecting) { row.target.classList.add("in"); revealObserver.unobserve(row.target); }
      }
    }, { rootMargin: "0px 0px -8% 0px", threshold: .08 })
  : null;

function revealWatch(el) {
  if (revealObserver) revealObserver.observe(el); else el.classList.add("in");
}

const DEFAULT_NOTES = [
  {
    date: "2026-09-24",
    title: "Smoother in the browser",
    body: "The web build now draws at the pixel resolution instead of scaling a full-size frame, caches rotated sprites and text, and uses a bigger audio buffer — no more crackling.\n" +
          "Touch works properly: drag anywhere on the pitch on an iPad, and there's a pause button next to the clock.",
  },
  {
    date: "2026-09-23",
    title: "Web version",
    body: "Sign in with Google and your cards, coins, squad and season are saved to your account.\n" +
          "The ball is 40% slower and takes the movement of whatever body part touches it — run into it and it goes with you.\n" +
          "New card: Pedro Neto (150, Chelsea).",
  },
];

let toastTimer = null;
function toast(msg, ms = 2800) {
  const t = $("toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove("show"), ms);
}

// which of the three panels in the play card is showing
function show(which) {
  for (const el of [gate, app, bannedView]) {
    if (el) el.hidden = el !== which;
  }
}

function setSignedIn(user, isAdmin) {
  const chip = $("accountChip");
  if (chip) chip.hidden = !user;
  $("navSignin").hidden = !!user;
  $("signout").hidden = !user;
  $("adminLink").hidden = !(user && isAdmin);
  $("adminTag").hidden = !(user && isAdmin);
}

// ---------------------------------------------------------------- firebase
let auth, db, playerRef = null;

function setupNeeded(why) {
  show(gate);
  gate.innerHTML = '<div class="state-pane"><h3>Setup needed</h3><p>' + why + "</p></div>";
}

show(gate);                                   // until Firebase tells us who you are
if (String(firebaseConfig.apiKey || "").startsWith("PASTE")) {
  setupNeeded("firebase-config.js still has the placeholder values. Follow the steps at the top of " +
              "that file (and paste firestore.rules into Firebase), then reload.");
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

async function doSignIn() {
  if (!auth) return;
  try {
    await signInWithPopup(auth, new GoogleAuthProvider());
  } catch (err) {
    toast(err.code === "auth/popup-blocked" ? "Allow popups for this site to sign in"
                                            : "Sign-in failed: " + (err.code || err), 4500);
  }
}
const doSignOut = () => auth && signOut(auth);

$("signin").onclick = doSignIn;
$("navSignin").onclick = doSignIn;
$("signout").onclick = doSignOut;
$("signout2").onclick = doSignOut;

if (auth) onAuthStateChanged(auth, async (user) => {
  if (!user) {
    setSignedIn(null, false);
    show(gate);
    stopGame();
    return;
  }
  playerRef = doc(db, "players", user.uid);
  let snap;
  try {
    snap = await getDoc(playerRef);
  } catch (err) {
    toast("Could not reach your save: " + (err.code || err), 5000);
    return;
  }

  const isAdmin = (user.email || "").toLowerCase() === ADMIN_EMAIL.toLowerCase();
  $("avatar").src = user.photoURL || "";
  $("uname").textContent = user.displayName || user.email;
  setSignedIn(user, isAdmin);

  if (snap.exists() && snap.data().banned === true) {
    $("banReason").textContent = snap.data().banReason || "This account can't play at the moment.";
    show(bannedView);
    return;
  }

  // keep the player card up to date (name and photo can change)
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
  frame.title = "aSmallWorldCup";
  frame.allow = "autoplay; fullscreen; gamepad; xr-spatial-tracking";
  frame.setAttribute("allowfullscreen", "");            // older Safari / iPad
  frame.setAttribute("webkitallowfullscreen", "");
  frame.src = GAME_PATH;
  frame.onload = () => { $("cover").hidden = true; };
  frame.onerror = () => toast("Game files missing — run build_web.sh", 5000);
  $("holder").appendChild(frame);
  setTimeout(() => {
    if (frame && !$("cover").hidden) $("loadNote").textContent = "Still loading… (big download the first time)";
  }, 9000);
}

function stopGame() {
  flushSave();
  if (frame) { frame.remove(); frame = null; }
  if ($("cover")) $("cover").hidden = false;
  if ($("play")) $("play").disabled = false;
  if ($("loadNote")) $("loadNote").hidden = true;
  leaveFullscreen();
}

$("play").onclick = startGame;

// Play Now anywhere on the page: scroll to the game, sign in first if needed
function playNow() {
  const target = app.hidden ? (bannedView.hidden ? gate : bannedView) : app;
  target.scrollIntoView({ behavior: "smooth", block: "center" });
  if (!app.hidden) startGame();
}
$("heroPlay").onclick = playNow;
$("ctaPlay").onclick = playNow;

// ---------------------------------------------------------------- fullscreen
// pygame's own fullscreen does nothing in pygbag, so the page does it. iPad Safari has no
// element fullscreen at all, so there is a CSS stand-in that fills the window.
const stage = () => app;

function fsElement() {
  return document.fullscreenElement || document.webkitFullscreenElement || null;
}

function enterFullscreen() {
  const el = stage();
  const req = el.requestFullscreen || el.webkitRequestFullscreen || el.webkitRequestFullScreen
           || el.mozRequestFullScreen || el.msRequestFullscreen;
  if (req) {
    try {
      const out = req.call(el);
      if (out && out.catch) out.catch(() => fakeFullscreen(true));
      return;
    } catch (err) { /* falls through to the stand-in */ }
  }
  fakeFullscreen(true);
}

function leaveFullscreen() {
  if (fsElement()) {
    const exit = document.exitFullscreen || document.webkitExitFullscreen || document.webkitCancelFullScreen;
    if (exit) { try { exit.call(document); } catch (err) { /* ignore */ } }
  }
  fakeFullscreen(false);
}

function fakeFullscreen(on) {
  document.body.classList.toggle("fake-fs", on);
  $("exitFs").hidden = !on;
  $("fullscreen").hidden = on;
}

$("fullscreen").onclick = () => (fsElement() || document.body.classList.contains("fake-fs"))
  ? leaveFullscreen() : enterFullscreen();
$("exitFs").onclick = leaveFullscreen;

document.addEventListener("fullscreenchange", syncFsButtons);
document.addEventListener("webkitfullscreenchange", syncFsButtons);
function syncFsButtons() {
  const on = !!fsElement();
  $("exitFs").hidden = !on;
  $("fullscreen").hidden = on;
}
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && document.body.classList.contains("fake-fs")) leaveFullscreen();
});

// ---------------------------------------------------------------- save sync
// the game calls window.aswcSave(text) inside the frame; bridge.js posts it up here
window.addEventListener("message", (e) => {
  if (e.origin !== location.origin || !e.data) return;
  if (e.data.type === "aswc-ready") {
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

window.addEventListener("beforeunload", flushSave);
setInterval(flushSave, 30000);              // slow heartbeat while you play

function setSync(state) {
  const dot = $("syncDot"), text = $("syncText");
  if (!dot) return;
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
  for (const n of entries.slice(0, 8)) {
    const wrap = document.createElement("article");
    wrap.className = "note reveal";
    const t = document.createElement("time");
    t.textContent = n.date || "";
    const h = document.createElement("h3");
    h.textContent = n.title || "Update";
    const d = document.createElement("div");
    d.textContent = n.body || "";
    wrap.append(t, h, d);
    box.appendChild(wrap);
    revealWatch(wrap);
  }
}
renderNotes(DEFAULT_NOTES);                 // something to read before Firebase answers

document.querySelectorAll(".reveal:not(.in)").forEach(revealWatch);

// mobile menu
const burger = $("burger"), navLinks = $("navLinks");
burger.onclick = () => navLinks.classList.toggle("open");
navLinks.addEventListener("click", (e) => {
  if (e.target.tagName === "A") navLinks.classList.remove("open");
});

// a missing screenshot shouldn't leave a hole in the grid
document.querySelectorAll(".shot img").forEach((img) => {
  img.addEventListener("error", () => { img.closest(".shot").hidden = true; });
});
