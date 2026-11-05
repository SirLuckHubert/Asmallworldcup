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
import { firebaseConfig, ADMIN_EMAIL, GAME_PATH } from "./firebase-config.js?v=2026-11-06a";
import { checkText, tidyUsername, usernameKey } from "./words.js?v=2026-11-06a";
import { rankOf, rankLine, badgeSvg, holdsTop10, TIERS, TOP10, TOP10_MIN, START_RP } from "./ranks.js?v=2026-11-06a";
import { TITLES, TITLE_BY_ID, ownedTitles, wornTitle, titleChip } from "./titles.js?v=2026-11-06a";
import { mergeIntoSaveText } from "./mail.js?v=2026-11-06a";
import { rngBoot, rngSignedIn, rngSignedOut, rngUsername } from "./rng.js?v=2026-11-06a";

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
    date: "2026-11-06",
    title: "Scout RNG, and a new leaderboard",
    body: "Scout RNG is on the site: roll for any of the 266 players, each one a 1-in-something, no sign-in needed. A free pack every 30 seconds with Lucky, Super, Mega, Speed and Miracle potions.\n" +
          "Put five players in your squad and they earn real coins for your club — up to 300 an hour, into a vault that holds 24 hours. Signed in, the coins go to the game's mail. 100,000 fragments swap for any 120–128 player.\n" +
          "The ranked leaderboard has a podium for the top three, tier colours, RP bars and win rates.",
  },
  {
    date: "2026-11-05",
    title: "Strong players, cheaper",
    body: "Star Signings prices are capped for players rated 80 to 119: a 100 costs 15,000 Star Points at most, a 119 at most 40,000. Legends rated 120 and up keep their prices.\n" +
          "Neymar Jr's Game Box is gone: he's signed in the Signature Archive only now.",
  },
  {
    date: "2026-11-02",
    title: "Mario Kempes, 128",
    body: "A new Signature card with its own Game Box and a holo frame: the autograph dims, then a light runs along it, and petals blow across the card.\n" +
          "The Signature Archive: Signature Tokens only come from archive quests. The first one opens at level 10 — win the World Cup final against the Netherlands scoring 3+, beat THE MACHINE, and win the Premier League on hard.",
  },
  {
    date: "2026-11-01",
    title: "Star Signings market, quests, faster football",
    body: "Star Signings is a market now: every player in the game, searchable, with a watchlist. Release duplicates for Star Points and sign who you want.\n" +
          "Daily and weekly quests, with a chest and free packs. The game plays 30% faster, the ball is always round, and it spins and dips.",
  },
  {
    date: "2026-10-30",
    title: "The Gauntlet",
    body: "Ten opponents in a row, a limited number of halves for your squad, matchday twists from rung 4, and THE MACHINE at the top.",
  },
  {
    date: "2026-10-29",
    title: "The Club Ladder",
    body: "Club football is a ladder: League One, the Championship and the Premier League. Top two go up, bottom two go down, the Premier League's top four play the Champions Cup. Every matchday rolls a twist — rain, low gravity, a giant ball, wind or a derby — and a bonus objective.",
  },
  {
    date: "2026-10-26",
    title: "PlayStyles",
    body: "Eighteen PlayStyles at three levels, shown on every card, firing in the moments they're for: a Power Shot when you hit it hard, a Precision Header when you meet it in the air.",
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

rngBoot();                                     // Scout RNG works signed out too

function scoutAccount(uid) {
  // what Scout RNG needs from Firebase: its own doc (lounge/<uid>) and the rarest-pulls board
  const ref = doc(db, "lounge", uid);
  return {
    uid,
    username: (me && me.username) || "",
    async load() { const s = await getDoc(ref); return s.exists() ? s.data() : null; },
    async save(fields) { await setDoc(ref, { ...fields, updatedAt: serverTimestamp() }, { merge: true }); },
    async sendMail(item) {
      const s = await getDoc(ref);
      const old = s.exists() && Array.isArray(s.data().mail) ? s.data().mail : [];
      await setDoc(ref, { mail: [item].concat(old).slice(0, 20), updatedAt: serverTimestamp() }, { merge: true });
    },
    async board() {
      const q = await getDocs(query(collection(db, "lounge"), orderBy("bestN", "desc"), limit(10)));
      return q.docs.map((d) => d.data()).filter((r) => r.bestId);
    },
  };
}

if (auth) onAuthStateChanged(auth, async (user) => {
  if (!user) {
    rngSignedOut();
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

  // put the cloud save where the game will look for it (same origin as the iframe),
  // with any message the admin sent to everyone merged in
  let cloud = snap.exists() && typeof snap.data().save === "string" && snap.data().save.length > 2
    ? snap.data().save : null;
  let base = cloud;
  if (!base) {
    try { base = localStorage.getItem(SAVE_KEY) || "{}"; } catch (err) { base = "{}"; }
  }
  const merged = await withBroadcastMail(base);      // a new player gets the news too
  if (merged) cloud = merged;
  if (cloud) {
    try { localStorage.setItem(SAVE_KEY, cloud); } catch (err) { /* private mode */ }
  }
  const d0 = snap.exists() ? snap.data() : {};
  me = {
    uid: user.uid,
    username: d0.username || "",
    rp: typeof d0.rp === "number" ? d0.rp : START_RP,
    wins: d0.wins || 0,
    losses: d0.losses || 0,
    draws: d0.draws || 0,
    muted: !!d0.muted,
    titles: Array.isArray(d0.titles) ? d0.titles : [],
    title: d0.title || "",
    place: 0,                       // filled in by the ladder
  };
  show(app);
  rngSignedIn(scoutAccount(user.uid));
  watchBan();
  watchNotes();
  watchPoll();
  showUsernameCard();
  drawTitles();
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
      me.draws = d.draws || 0;
      me.titles = Array.isArray(d.titles) ? d.titles : [];
      me.title = d.title || "";
      if (d.username) me.username = d.username;
      drawTitles();
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
    return null;                                          // mail never blocks anything
  }
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
    rngUsername(wanted);
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
  // the tiers as a ladder, top down: badge, name, the RP it starts at - yours lit
  const row = $("tierRow");
  if (!row) return;
  row.textContent = "";
  const mine = rankOf(me ? me.rp : 0, isTopTen());
  for (const t of [TOP10].concat(TIERS.slice().reverse())) {
    const cell = document.createElement("div");
    const fake = t.key === "top10" ? rankOf(9999, true) : rankOf(t.at + 1);
    const at = t.key === "top10" ? "Top ten on the board" : (t.at ? t.at.toLocaleString() + "+ RP" : "Everyone starts here");
    cell.innerHTML = badgeSvg(fake, 34) + '<span class="tn">' + t.name + '</span><span class="ta">' + at + "</span>";
    cell.style.setProperty("--tc", t.colour);
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
  const line = $("myRankLine");
  line.textContent = (me.username ? me.username + " · " : "") + me.rp + " RP"
    + (top ? " · " + tier.label : "");
  const worn = wornTitle(me);
  if (worn) {
    line.classList.add("name-line");
    line.appendChild(document.createTextNode(" "));
    line.appendChild(titleChip(worn, { small: true }));
  }
  $("myRankFill").style.width = Math.round(tier.progress * 100) + "%";
  $("myRecord").textContent = (me.wins || 0) + "W · " + (me.losses || 0) + "L"
    + (tier.next ? "  ·  " + Math.max(0, tier.next - me.rp) + " RP to the next step" : "");
}

function nameNode(p, place) {
  const line = document.createElement("span");
  line.className = "name-line";
  const nm = document.createElement("b");
  nm.textContent = p.username;
  line.appendChild(nm);
  const worn = wornTitle({ ...p, place });
  if (worn) line.appendChild(titleChip(worn, { small: true }));
  if (me && p.uid === me.uid) {
    const you = document.createElement("span");
    you.className = "you-tag";
    you.textContent = "You";
    line.appendChild(you);
  }
  return line;
}

function winPct(p) {
  const played = (p.wins || 0) + (p.losses || 0) + (p.draws || 0);
  return played ? Math.round(100 * (p.wins || 0) / played) + "%" : "–";
}

async function loadBoard() {
  const list0 = $("boardList"), podium = $("podium"), you = $("boardYou");
  try {
    const snap = await getDocs(query(collection(db, "players"), orderBy("rp", "desc"), limit(25)));
    const list = snap.docs.map((d) => ({ uid: d.id, ...d.data() })).filter((p) => p.username);
    topTen = list.slice(0, TOP10_MIN).map((p) => p.uid);
    ladderSize = list.length;
    list0.textContent = "";
    podium.textContent = "";
    $("boardCount").textContent = list.length ? list.length + " on the board" : "";
    if (!list.length) {
      list0.innerHTML = '<li class="board-empty">Nobody has played a ranked match yet — be the first.</li>';
    }
    const ranked = list.map((p, i) => {
      const top = holdsTop10(i, p.rp, list.length);
      const tier = rankOf(p.rp || 0);
      const rank = rankOf(p.rp || 0, top);
      rank.label = top ? "Top 10 · " + tier.label : tier.label;
      if (me && p.uid === me.uid) { me.place = i + 1; me.draws = p.draws || 0; }
      return { p, i, tier, rank };
    });

    // the top three on a podium: second, first, third
    for (const k of [1, 0, 2]) {
      const r = ranked[k];
      if (!r) continue;
      const box = document.createElement("div");
      box.className = "pod pod-" + (k + 1) + (me && r.p.uid === me.uid ? " me" : "");
      box.style.setProperty("--tc", r.tier.colour);
      const medal = document.createElement("span");
      medal.className = "medal";
      medal.textContent = String(k + 1);
      const badge = document.createElement("span");
      badge.className = "pod-badge";
      badge.innerHTML = badgeSvg(r.rank, k === 0 ? 78 : 62);
      const nm = nameNode(r.p, k + 1);
      nm.classList.add("pod-name");
      const lab = document.createElement("span");
      lab.className = "pod-tier";
      lab.textContent = r.rank.label;
      const rp = document.createElement("span");
      rp.className = "pod-rp";
      rp.innerHTML = "<b>" + Math.round(r.p.rp || 0).toLocaleString() + "</b> RP";
      const rec = document.createElement("span");
      rec.className = "pod-rec";
      rec.textContent = (r.p.wins || 0) + "W · " + (r.p.losses || 0) + "L · " + winPct(r.p);
      const step = document.createElement("span");
      step.className = "pod-step";
      step.textContent = String(k + 1);
      box.append(medal, badge, nm, lab, rp, rec, step);
      podium.appendChild(box);
    }

    // everyone else as rows
    for (const r of ranked.slice(3)) {
      const li = document.createElement("li");
      li.className = "brow" + (me && r.p.uid === me.uid ? " me" : "");
      li.style.setProperty("--tc", r.tier.colour);
      const place = document.createElement("span");
      place.className = "place";
      place.textContent = String(r.i + 1);
      const who = document.createElement("span");
      who.className = "who";
      who.appendChild(nameNode(r.p, r.i + 1));
      const rk = document.createElement("span");
      rk.className = "rk";
      rk.innerHTML = badgeSvg(r.rank, 26) + "<span>" + r.rank.label + "</span>";
      const rp = document.createElement("span");
      rp.className = "rp r";
      rp.innerHTML = "<b>" + Math.round(r.p.rp || 0).toLocaleString() + '</b><i style="--p:' +
        Math.round((r.tier.progress || 0) * 100) + '%"></i>';
      const wl = document.createElement("span");
      wl.className = "r wl";
      wl.textContent = (r.p.wins || 0) + "–" + (r.p.losses || 0);
      const pct = document.createElement("span");
      pct.className = "r pct";
      pct.textContent = winPct(r.p);
      li.append(place, who, rk, rp, wl, pct);
      list0.appendChild(li);
    }
    if (list.length && list.length <= 3) {
      list0.innerHTML = '<li class="board-empty">The rest of the board is waiting for players.</li>';
    }

    // you, if you're not on the board
    if (me && me.username && !list.some((p) => p.uid === me.uid)) {
      you.hidden = false;
      you.innerHTML = "";
      const tier = rankOf(me.rp);
      you.style.setProperty("--tc", tier.colour);
      you.innerHTML = '<span class="place">–</span><span class="who"></span><span class="rk">' + badgeSvg(tier, 26) +
        "<span>" + tier.label + '</span></span><span class="rp r"><b>' + Math.round(me.rp).toLocaleString() +
        '</b></span><span class="r wl">' + (me.wins || 0) + "–" + (me.losses || 0) + '</span><span class="r pct">' +
        winPct(me) + "</span>";
      you.querySelector(".who").appendChild(nameNode({ ...me }, 0));
    } else {
      you.hidden = true;
    }
  } catch (err) {
    list0.innerHTML = '<li class="board-empty">Couldn\'t read the ladder: ' + (err.code || err) + "</li>";
  }
  drawMyRank();
  drawTiers();
  drawTitles();
}
$("boardRefresh").onclick = loadBoard;

// ---------------------------------------------------------------- titles
// Owning a title is worked out, not stored: the admin's list plus whatever the ladder
// says you have earned. So there is nothing to fake by editing the page - the badge
// other people see is recomputed from your record.
const SEEN_KEY = "aswc_titles_seen";

function drawTitles() {
  const grid = $("titleGrid");
  if (!grid || !me) return;
  const owned = ownedTitles(me);
  const worn = wornTitle(me);
  grid.textContent = "";
  for (const t of TITLES) {
    const have = owned.includes(t.id);
    const on = worn && worn.id === t.id;
    const card = document.createElement("button");
    card.className = "title-card" + (have ? " owned" : "") + (on ? " on" : "");
    card.style.setProperty("--tc", t.colour);
    card.style.setProperty("--tl", t.light);
    card.disabled = !have;
    card.appendChild(titleChip(t));
    const how = document.createElement("span");
    how.className = "how";
    how.textContent = t.how;
    card.appendChild(how);
    if (!have && t.progress) {
      const [now, goal] = t.progress(me);
      const bar = document.createElement("div");
      bar.className = "title-bar";
      const fill = document.createElement("i");
      fill.style.width = Math.round(Math.min(1, now / goal) * 100) + "%";
      bar.appendChild(fill);
      card.appendChild(bar);
    }
    const state = document.createElement("span");
    state.className = "state";
    state.textContent = on ? "Wearing this" : have ? "Click to wear" : "Locked";
    card.appendChild(state);
    card.onclick = () => wearTitle(t.id);
    grid.appendChild(card);
  }
  $("titleCount").textContent = owned.length + " / " + TITLES.length;
  $("titleHint").textContent = owned.length
    ? "Click one to wear it — it shows next to your name on the ladder and in chat."
    : "You haven't got any yet. Play ranked matches, or wait for one to be handed out.";
  $("titleClear").hidden = !worn;
  announceNew(owned);
  drawMyRank();
}

function announceNew(owned) {
  let seen = [];
  try { seen = JSON.parse(localStorage.getItem(SEEN_KEY) || "[]"); } catch (err) { seen = []; }
  const fresh = owned.filter((id) => !seen.includes(id));
  if (fresh.length && seen.length !== 0) {
    const t = TITLE_BY_ID[fresh[0]];
    toast("New title: " + t.name + (fresh.length > 1 ? " (+" + (fresh.length - 1) + " more)" : ""), 5000);
  }
  try { localStorage.setItem(SEEN_KEY, JSON.stringify(owned)); } catch (err) { /* private mode */ }
}

async function wearTitle(id) {
  if (!me || !playerRef) return;
  if (id && !ownedTitles(me).includes(id)) return;
  const next = me.title === id ? "" : id;          // clicking the one you wear takes it off
  me.title = next;
  drawTitles();
  loadBoard();
  try {
    await setDoc(playerRef, { title: next, updatedAt: serverTimestamp() }, { merge: true });
  } catch (err) {
    toast("Couldn't save that: " + (err.code || err), 4000);
  }
}
$("titleClear").onclick = () => wearTitle("");

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
    if (m.title && TITLE_BY_ID[m.title]) {
      const chip = titleChip(TITLE_BY_ID[m.title], { small: true });
      who.appendChild(document.createTextNode(" "));
      who.appendChild(chip);
    }
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
      uid: me.uid, username: me.username, title: (wornTitle(me) || {}).id || "",
      text: text.slice(0, 200), at: serverTimestamp(),
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
