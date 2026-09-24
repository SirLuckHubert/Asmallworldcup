// aSmallWorldCup — sign-in, cloud saves, bans, patch notes, and the page itself.
// Static site: everything runs in the browser against Firebase.

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
  getAuth, GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import {
  getFirestore, doc, getDoc, setDoc, onSnapshot, serverTimestamp, collection, getDocs,
  addDoc, query, orderBy, limit, deleteDoc,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";
import { firebaseConfig, ADMIN_EMAIL, GAME_PATH } from "./firebase-config.js?v=2026-09-25c";
import { checkText, tidyUsername, usernameKey } from "./words.js?v=2026-09-25c";
import { rankOf, rankLine, badgeSvg, holdsTop10, TIERS, TOP10, TOP10_MIN, START_RP } from "./ranks.js?v=2026-09-25c";

const SAVE_KEY = "aswc_save";          // the game reads/writes this in localStorage
const SAVE_DEBOUNCE = 2000;            // ms of quiet before a save goes to the cloud

window.__aswcBooted = true;            // the watchdog in index.html checks this

// The stylesheet carries a --build marker. If it is missing, the browser (or GitHub's
// CDN) is serving an old style.css, which leaves the page half-styled.
const CSS_BUILD = getComputedStyle(document.documentElement).getPropertyValue("--build").trim();
if (!CSS_BUILD) {
  const bar = document.createElement("div");
  bar.style.cssText = "position:fixed;left:0;right:0;top:0;z-index:999;padding:10px 14px;" +
    "background:#ffd23f;color:#1d1400;font:600 14px/1.4 system-ui,sans-serif;text-align:center";
  bar.textContent = "This page loaded an old or missing style.css — press Ctrl+Shift+R " +
    "(Cmd+Shift+R on a Mac). If it keeps happening, re-upload style.css to the repo.";
  document.addEventListener("DOMContentLoaded", () => document.body.prepend(bar));
}

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
    date: "2026-09-25",
    title: "Online, ranked, chat",
    body: "RANKED ONLINE is in the Play menu: you're matched with whoever else is looking, and the match runs straight between the two browsers.\n" +
          "Six tiers with three divisions each, Elite above them and a Top 10 badge for the ten best on the ladder. Win +28, draw +4, loss -18, plus 2 a goal.\n" +
          "Pick a username (12 characters), chat here or from inside a match with the quick messages, and report anything out of order — the filter catches the obvious stuff, the report button gets the rest.",
  },
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
let auth, db, playerRef = null, me = null, topTen = [], ladderSize = 0;

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
  me = {
    uid: user.uid,
    username: snap.exists() ? (snap.data().username || "") : "",
    rp: snap.exists() && typeof snap.data().rp === "number" ? snap.data().rp : START_RP,
    wins: (snap.exists() && snap.data().wins) || 0,
    losses: (snap.exists() && snap.data().losses) || 0,
    muted: !!(snap.exists() && snap.data().muted),
  };
  show(app);
  watchBan();
  watchNotes();
  watchPoll();
  showUsernameCard();
  watchChat();
  loadBoard();
  drawTiers();
});

// a ban lands while you're playing: pull the game straight away
let banWatch = null;
function watchBan() {
  if (banWatch) banWatch();
  banWatch = onSnapshot(playerRef, (s) => {
    if (!s.exists()) return;
    const d = s.data() || {};
    if (d.banned === true) {
      stopGame();
      $("banReason").textContent = d.banReason || "This account can't play at the moment.";
      show(bannedView);
      return;
    }
    // a ranked match on the game page, or the admin, can change any of this while you sit here
    if (me) {
      const moved = (typeof d.rp === "number" && d.rp !== me.rp) || (d.username || "") !== me.username;
      me.rp = typeof d.rp === "number" ? d.rp : me.rp;
      me.wins = d.wins || 0;
      me.losses = d.losses || 0;
      me.muted = !!d.muted;
      if (d.username) me.username = d.username;
      showUsernameCard();
      if (moved) loadBoard(); else drawMyRank();
    }
  }, () => {});
}

// ---------------------------------------------------------------- the game
// The game runs on play.html, filling the whole window. This page just sends you there.
let pending = null, saveTimer = null, lastSent = "";

async function startGame() {
  $("startBtn").disabled = true;
  $("loadNote").hidden = false;
  $("loadNote").textContent = "Opening the game…";
  try {                                   // don't send anyone to a blank page
    const probe = await fetch(GAME_PATH, { method: "HEAD", cache: "no-store" });
    if (!probe.ok) return gameMissing(probe.status);
  } catch (err) {
    return gameMissing(err.message || "network error");
  }
  location.href = "play.html";
}

function gameMissing(why) {
  $("startBtn").disabled = false;
  $("loadNote").hidden = false;
  $("loadNote").innerHTML = "Couldn't load <b>" + new URL(GAME_PATH, location.href).pathname +
    "</b> (" + why + ").<br>Upload the pygbag build so that folder sits next to this page, " +
    "or change GAME_PATH in firebase-config.js.";
  toast("Game files not found — see the message on the pitch", 5000);
}

function stopGame() {
  flushSave();
  if ($("startBtn")) $("startBtn").disabled = false;
  if ($("loadNote")) $("loadNote").hidden = true;
}

$("startBtn").onclick = startGame;
$("heroPlay").onclick = playNow;
$("ctaPlay").onclick = playNow;

function playNow() {
  if (!app.hidden) return startGame();                  // signed in: straight to the pitch
  const target = bannedView.hidden ? gate : bannedView;
  target.scrollIntoView({ behavior: "smooth", block: "center" });
}

// ---------------------------------------------------------------- saves
// The game itself syncs from play.html; this page only writes when it hands out a poll reward.
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
    pending = text;
  }
}

function setSync(state) {
  const dot = $("syncDot"), text = $("syncText");
  if (!dot) return;
  dot.className = "dot" + (state === "ok" ? " on" : state === "error" ? " err" : "");
  text.textContent = state === "saving" ? "Saving…"
    : state === "ok" ? "Progress saved to your account"
    : state === "error" ? "Couldn't save — check your connection"
    : "Progress saves to your account";
}

// ---------------------------------------------------------------- username
function showUsernameCard() {
  const card = $("nameCard");
  const needs = !me.username;
  card.hidden = !needs;
  $("startBtn").disabled = needs;
  if (needs) {
    $("nameWhy").textContent = "You need a name before you can play.";
    $("nameInput").value = "";
  }
}

$("nameSave").onclick = saveUsername;
$("nameInput").addEventListener("keydown", (e) => { if (e.key === "Enter") saveUsername(); });

async function saveUsername() {
  const wanted = tidyUsername($("nameInput").value);
  const verdict = checkText(wanted, { username: true });
  if (!verdict.ok) {
    $("nameWhy").textContent = verdict.why;
    if (verdict.level === "hate") {
      fileReport({ about: me.uid, aboutName: wanted, text: wanted, reason: "username", auto: true });
    }
    return;
  }
  const key = usernameKey(wanted);
  $("nameSave").disabled = true;
  try {
    const taken = await getDoc(doc(db, "usernames", key));
    if (taken.exists() && taken.data().uid !== me.uid) {
      $("nameWhy").textContent = "Someone already has that one.";
      $("nameSave").disabled = false;
      return;
    }
    await setDoc(doc(db, "usernames", key), { uid: me.uid, username: wanted, at: serverTimestamp() });
    await setDoc(playerRef, { username: wanted, usernameKey: key, rp: me.rp, updatedAt: serverTimestamp() },
                 { merge: true });
    me.username = wanted;
    $("nameWhy").textContent = "";
    toast("You're " + wanted + " from now on");
    showUsernameCard();
    drawMyRank();
    loadBoard();
  } catch (err) {
    $("nameWhy").textContent = "Couldn't save that: " + (err.code || err);
  }
  $("nameSave").disabled = false;
}

// ---------------------------------------------------------------- ranked
function drawTiers() {
  const row = $("tierRow");
  if (!row) return;
  row.textContent = "";
  const mine = rankOf(me ? me.rp : 0, isTopTen());
  for (const t of TIERS.concat([TOP10])) {
    const cell = document.createElement("div");
    const fake = t.key === "top10" ? rankOf(9999, true) : rankOf(t.at + 1);
    cell.innerHTML = badgeSvg(fake, 34) + t.name;
    if (t.key === mine.key) cell.className = "on";
    row.appendChild(cell);
  }
}

function isTopTen() {
  return !!me && holdsTop10(topTen.indexOf(me.uid), me.rp, ladderSize);
}

function drawMyRank() {
  if (!me) return;
  // Top 10 sits on top of your tier rather than replacing it, so both are shown
  const tier = rankOf(me.rp);
  const top = isTopTen();
  $("myBadge").innerHTML = badgeSvg(rankOf(me.rp, top), 56);
  $("myRankName").textContent = top ? "Top 10" : tier.label;
  $("myRankLine").textContent = (me.username ? me.username + " · " : "") + me.rp + " RP"
    + (top ? " · " + tier.label : "");
  $("myRankFill").style.width = Math.round(tier.progress * 100) + "%";
  $("myRecord").textContent = (me.wins || 0) + "W · " + (me.losses || 0) + "L"
    + (tier.next ? "  ·  " + Math.max(0, tier.next - me.rp) + " RP to the next step" : "");
}

async function loadBoard() {
  const rows = $("boardRows");
  try {
    const snap = await getDocs(query(collection(db, "players"), orderBy("rp", "desc"), limit(25)));
    const list = snap.docs.map((d) => ({ uid: d.id, ...d.data() })).filter((p) => p.username);
    topTen = list.slice(0, TOP10_MIN).map((p) => p.uid);
    ladderSize = list.length;
    rows.textContent = "";
    if (!list.length) {
      rows.innerHTML = '<tr><td colspan="6" class="muted">Nobody has played a ranked match yet.</td></tr>';
    }
    list.forEach((p, i) => {
      const top = holdsTop10(i, p.rp, list.length);
      const tier = rankOf(p.rp || 0);
      const rank = rankOf(p.rp || 0, top);
      rank.label = top ? "Top 10 · " + tier.label : tier.label;
      const tr = document.createElement("tr");
      if (p.uid === me.uid) tr.style.background = "rgba(62,240,138,.07)";
      const cells = [String(i + 1), p.username, "", String(Math.round(p.rp || 0)),
                     String(p.wins || 0), String(p.losses || 0)];
      cells.forEach((text, c) => {
        const td = document.createElement("td");
        if (c >= 3) td.className = "num";
        if (c === 2) {
          td.innerHTML = '<span class="rank-badge">' + badgeSvg(rank, 22) + "<span>" + rank.label + "</span></span>";
        } else {
          td.textContent = text;
        }
        tr.appendChild(td);
      });
      rows.appendChild(tr);
    });
  } catch (err) {
    rows.innerHTML = '<tr><td colspan="6" class="muted">Couldn\'t read the ladder: ' + (err.code || err) + "</td></tr>";
  }
  drawMyRank();
  drawTiers();
}
$("boardRefresh").onclick = loadBoard;

// ---------------------------------------------------------------- chat
let chatStop = null;

function watchChat() {
  $("chatInput").disabled = false;
  $("chatSend").disabled = false;
  if (chatStop) chatStop();
  const q = query(collection(db, "chat"), orderBy("at", "desc"), limit(60));
  chatStop = onSnapshot(q, (snap) => {
    const rows = snap.docs.map((d) => ({ id: d.id, ...d.data() })).reverse();
    drawChat(rows);
  }, (err) => {
    $("chatLog").innerHTML = '<p class="muted" style="padding:18px">Chat is unavailable: ' + (err.code || err) + "</p>";
  });
}

function drawChat(rows) {
  const box = $("chatLog");
  const stick = box.scrollTop + box.clientHeight > box.scrollHeight - 60;
  box.textContent = "";
  if (!rows.length) {
    box.innerHTML = '<p class="muted" style="padding:18px">Nothing yet — say hello.</p>';
    return;
  }
  for (const m of rows) {
    const line = document.createElement("div");
    line.className = "chat-msg";
    const who = document.createElement("span");
    who.className = "who" + (m.uid === me.uid ? " mine" : "");
    who.textContent = m.username || "player";
    const body = document.createElement("span");
    body.className = "body";
    body.textContent = m.text || "";
    const when = document.createElement("time");
    when.textContent = m.at && m.at.toDate ? m.at.toDate().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "";
    const flag = document.createElement("button");
    flag.className = "flag";
    flag.title = "Report this message";
    flag.textContent = "⚑ report";
    flag.onclick = () => openReport({ about: m.uid, aboutName: m.username, text: m.text, msgId: m.id });
    line.append(who, body, when, flag);
    box.appendChild(line);
  }
  if (stick) box.scrollTop = box.scrollHeight;
}

$("chatSend").onclick = sendChat;
$("chatInput").addEventListener("keydown", (e) => { if (e.key === "Enter") sendChat(); });

async function sendChat() {
  const text = $("chatInput").value.trim();
  if (!text || !me) return;
  if (!me.username) { toast("Pick a username first"); return; }
  if (me.muted) { toast("You're muted — the admin turned your chat off", 4000); return; }
  const verdict = checkText(text);
  if (!verdict.ok) {
    toast(verdict.why, 4000);
    if (verdict.level === "hate") {
      fileReport({ about: me.uid, aboutName: me.username, text, reason: "auto-blocked", auto: true });
    }
    return;
  }
  $("chatInput").value = "";
  try {
    await addDoc(collection(db, "chat"), {
      uid: me.uid, username: me.username, text: text.slice(0, 200), at: serverTimestamp(),
    });
  } catch (err) {
    toast(err.code === "permission-denied" ? "You're muted" : "Message didn't send", 4000);
  }
}

// ---------------------------------------------------------------- reports
let reporting = null;

function openReport(what) {
  reporting = what;
  $("reportWhat").textContent = (what.aboutName || "player") + ": " + (what.text || "").slice(0, 120);
  $("reportBox").hidden = false;
}
$("reportCancel").onclick = () => { $("reportBox").hidden = true; reporting = null; };
$("reportSend").onclick = async () => {
  if (!reporting) return;
  await fileReport({ ...reporting, reason: $("reportReason").value });
  $("reportBox").hidden = true;
  reporting = null;
  toast("Reported — thanks, the admin will look at it");
};

async function fileReport(what) {
  if (!me) return;
  try {
    await addDoc(collection(db, "reports"), {
      by: me.uid, byName: me.username || "player",
      about: what.about || "", aboutName: what.aboutName || "",
      text: (what.text || "").slice(0, 200),
      reason: what.reason || "other",
      msgId: what.msgId || "",
      at: serverTimestamp(), done: false,
    });
  } catch (err) {
    if (!what.auto) toast("Couldn't send that report: " + (err.code || err), 4000);
  }
}

// ---------------------------------------------------------------- the admin's poll
// site/poll holds the question; each answer is a document in polls/<id>/votes/<uid>, and the
// reward goes straight into the player's save.
let poll = null, myVote = null, pollBusy = false;

function watchPoll() {
  onSnapshot(doc(db, "site", "poll"), async (snap) => {
    poll = snap.exists() ? snap.data() : null;
    if (!poll || !poll.open || !poll.id || !Array.isArray(poll.options) || !poll.options.length) {
      $("pollCard").hidden = true;
      return;
    }
    myVote = null;
    try {
      const mine = await getDoc(doc(db, "polls", poll.id, "votes", auth.currentUser.uid));
      if (mine.exists()) myVote = mine.data().choice;
    } catch (err) { /* first time, or offline */ }
    drawPoll();
  }, () => { $("pollCard").hidden = true; });
}

function rewardWords(p) {
  const n = Number(p.reward || 0);
  if (!n) return "";
  return n + " " + (p.currency === "coins" ? "coins" : "Star Points");
}

function drawPoll(counts) {
  const card = $("pollCard");
  card.hidden = false;
  $("pollQ").textContent = poll.question || "What do you think?";
  const box = $("pollOptions");
  box.textContent = "";
  const total = counts ? counts.reduce((a, b) => a + b, 0) : 0;
  poll.options.forEach((text, i) => {
    const b = document.createElement("button");
    b.className = "btn" + (myVote === i ? " mine" : "");
    const label = document.createElement("span");
    label.textContent = text;
    b.appendChild(label);
    if (counts) {
      const pct = total ? Math.round((counts[i] / total) * 100) : 0;
      const bar = document.createElement("i");
      bar.className = "bar";
      bar.style.width = pct + "%";
      const num = document.createElement("span");
      num.className = "pct";
      num.textContent = pct + "%";
      b.append(bar, num);
    }
    if (myVote === null) b.onclick = () => answerPoll(i);
    else b.disabled = true;
    box.appendChild(b);
  });
  const reward = rewardWords(poll);
  $("pollReward").textContent = myVote === null
    ? (reward ? "Answer and " + reward + " land in your account." : "One tap, no wrong answers.")
    : (reward ? "Thanks — " + reward + " added. It'll be there next time the game loads."
              : "Thanks for answering.");
}

async function answerPoll(choice) {
  if (pollBusy || myVote !== null || !poll || !auth.currentUser) return;
  pollBusy = true;
  const uid = auth.currentUser.uid;
  try {
    await setDoc(doc(db, "polls", poll.id, "votes", uid), {
      choice,
      name: auth.currentUser.displayName || "Player",
      at: serverTimestamp(),
    });
  } catch (err) {
    pollBusy = false;
    toast(err.code === "permission-denied" ? "You've already answered this one" : "Couldn't send that: " + err.code, 4000);
    return;
  }
  myVote = choice;

  // pay them, into the cloud save the game loads
  const amount = Number(poll.reward || 0);
  if (amount > 0) {
    try {
      const snap = await getDoc(playerRef);
      const save = JSON.parse((snap.exists() && snap.data().save) || "{}");
      const key = poll.currency === "coins" ? "coins" : "star_points";
      save[key] = Number(save[key] || 0) + amount;
      save.polls_done = save.polls_done || {};
      save.polls_done[poll.id] = choice;
      const text = JSON.stringify(save);
      await setDoc(playerRef, { save: text, updatedAt: serverTimestamp() }, { merge: true });
      lastSent = text;
      try { localStorage.setItem(SAVE_KEY, text); } catch (e) { /* ignore */ }
      setSync("ok");
      toast("+" + rewardWords(poll), 4000);
    } catch (err) {
      toast("Answer saved, but the reward didn't go through: " + (err.code || err), 5000);
    }
  }
  pollBusy = false;
  drawPoll();
  showPollResults();
}

async function showPollResults() {
  if (!poll) return;
  try {
    const votes = await getDocs(collection(db, "polls", poll.id, "votes"));
    const counts = poll.options.map(() => 0);
    votes.forEach((v) => {
      const c = v.data().choice;
      if (counts[c] !== undefined) counts[c] += 1;
    });
    drawPoll(counts);
  } catch (err) { /* players may not be allowed to read every vote - that's fine */ }
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
