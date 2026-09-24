// Admin console: every player's save, bans, card grants and patch notes.
// Only the admin account can read or write any of this - see firestore.rules.

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
  getAuth, GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import {
  getFirestore, collection, getDocs, doc, getDoc, setDoc, updateDoc, deleteDoc,
  serverTimestamp, query, orderBy, limit, where,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";
import { firebaseConfig, ADMIN_EMAIL } from "./firebase-config.js?v=2026-09-26e";
import { rankOf, rankLine, START_RP } from "./ranks.js?v=2026-09-26e";
import { tidyUsername, usernameKey, checkText } from "./words.js?v=2026-09-26e";
import { TITLES, ownedTitles, wornTitle, titleChip } from "./titles.js?v=2026-09-26e";

const $ = (id) => document.getElementById(id);
const fb = initializeApp(firebaseConfig);
const auth = getAuth(fb);
const db = getFirestore(fb);

let players = [];         // [{uid, ...data}]
let current = null;       // the uid being edited
let cards = [];

let toastTimer = null;
function toast(msg, ms = 2600) {
  const t = $("toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove("show"), ms);
}

$("signin").onclick = () => signInWithPopup(auth, new GoogleAuthProvider()).catch((e) => toast(e.code, 4000));
$("signout").onclick = () => signOut(auth);
$("switch").onclick = (e) => { e.preventDefault(); signOut(auth); };

onAuthStateChanged(auth, async (user) => {
  const isAdmin = user && (user.email || "").toLowerCase() === ADMIN_EMAIL.toLowerCase();
  $("gate").hidden = !!isAdmin;
  $("app").hidden = !isAdmin;
  $("wrongAccount").hidden = !(user && !isAdmin);
  $("accountChip").hidden = !isAdmin;
  $("signout").hidden = !isAdmin;
  if (!isAdmin) return;
  $("avatar").src = user.photoURL || "";
  $("uname").textContent = user.displayName || user.email;
  await loadCards();
  await loadPlayers();
  await loadNotes();
  await loadPoll();
  await loadReports();
  await loadChat();
});

// ---------------------------------------------------------------- cards
async function loadCards() {
  if (cards.length) return;
  try {
    cards = await (await fetch("cards.json")).json();
  } catch (err) {
    cards = [];
    toast("cards.json missing - card names won't autocomplete", 4000);
  }
  const list = $("cardList");
  list.textContent = "";
  for (const c of cards) {
    const o = document.createElement("option");
    o.value = `${c.name} (${c.rating} ${c.pos}) [${c.id}]`;
    list.appendChild(o);
  }
}

function cardIdFrom(text) {
  const m = String(text).match(/\[([^\]]+)\]\s*$/);
  if (m) return m[1];
  const t = text.trim().toLowerCase();
  const hit = cards.find((c) => c.id.toLowerCase() === t)
    || cards.find((c) => c.name.toLowerCase() === t)
    || cards.find((c) => c.name.toLowerCase().startsWith(t));
  return hit ? hit.id : null;
}

// ---------------------------------------------------------------- players
async function loadPlayers() {
  $("rows").innerHTML = '<tr><td colspan="7" class="muted">Loading…</td></tr>';
  try {
    let snap;
    try {
      snap = await getDocs(query(collection(db, "players"), orderBy("lastSeen", "desc"), limit(500)));
    } catch (err) {
      snap = await getDocs(collection(db, "players"));      // no index / no lastSeen yet
    }
    players = snap.docs.map((d) => ({ uid: d.id, ...d.data() }));
  } catch (err) {
    $("rows").innerHTML = `<tr><td colspan="7" class="muted">Couldn't read players: ${err.code || err}</td></tr>`;
    return;
  }
  drawPlayers();
}
$("refresh").onclick = loadPlayers;
$("search").oninput = drawPlayers;

function saveOf(p) {
  try { return JSON.parse(p.save || "{}"); } catch (err) { return {}; }
}

function levelOf(save) {           // matches xp_to_next() in the game: 200 + 100*n
  let xp = Number(save.xp || 0), level = 1, need = 300;
  while (xp >= need) { xp -= need; level += 1; need = 200 + 100 * level; }
  return level;
}

function drawPlayers() {
  const q = $("search").value.trim().toLowerCase();
  const rows = $("rows");
  rows.textContent = "";
  const list = players.filter((p) => !q
    || (p.name || "").toLowerCase().includes(q) || (p.email || "").toLowerCase().includes(q));
  $("count").textContent = `— ${players.length} signed in, ${players.filter((p) => p.banned).length} banned`;
  if (!list.length) {
    rows.innerHTML = '<tr><td colspan="7" class="muted">Nobody yet.</td></tr>';
    return;
  }
  for (const p of list) {
    const save = saveOf(p);
    const tr = document.createElement("tr");
    if (p.banned) tr.className = "banned";
    const seen = p.lastSeen && p.lastSeen.toDate ? p.lastSeen.toDate().toLocaleString() : "—";
    const cells = [
      (p.username || p.name || "Player") + (p.banned ? " (banned)" : "") + (p.muted ? " (muted)" : ""),
      p.email || "",
      String(levelOf(save)),
      String(save.coins ?? 0),
      String(Object.keys(save.owned || {}).length),
      seen,
    ];
    cells.forEach((text, i) => {
      const td = document.createElement("td");
      if (i >= 2 && i <= 4) td.className = "num";
      td.textContent = text;
      tr.appendChild(td);
    });
    const td = document.createElement("td");
    const b = document.createElement("button");
    b.className = "btn btn-sm";
    b.textContent = "Open";
    b.onclick = () => openPlayer(p.uid);
    td.appendChild(b);
    tr.appendChild(td);
    rows.appendChild(tr);
  }
}

async function openPlayer(uid) {
  const snap = await getDoc(doc(db, "players", uid));
  if (!snap.exists()) return toast("That player is gone");
  const p = { uid, ...snap.data() };
  current = uid;
  players = players.map((x) => (x.uid === uid ? p : x));
  $("editor").hidden = false;
  $("editTitle").textContent = `${p.name || "Player"} — ${p.email || uid}`;
  $("ban").hidden = !!p.banned;
  $("unban").hidden = !p.banned;
  $("banReason").value = p.banReason || "";
  $("saveText").value = JSON.stringify(saveOf(p), null, 1);
  $("mute").hidden = !!p.muted;
  $("unmute").hidden = !p.muted;
  $("editName").value = p.username || "";
  $("editRp").value = typeof p.rp === "number" ? p.rp : START_RP;
  $("rankNow").textContent = rankLine(rankOf(p.rp || 0));
  $("editHint").textContent = p.banned ? "This account is banned." : "";
  drawAdminTitles(p);
  $("editor").scrollIntoView({ behavior: "smooth", block: "start" });
}

// ---------------------------------------------------------------- titles
// `titles` on the player document is the admin's list. The ones with a rule of their own
// (100 matches, a high rank, top of the ladder) are worked out from the record instead,
// so they show here as earned and can't be handed out or taken away.
function drawAdminTitles(p) {
  const grid = $("adminTitles");
  if (!grid) return;
  const given = Array.isArray(p.titles) ? p.titles : [];
  const owned = ownedTitles(p);
  const worn = wornTitle(p);
  $("titleWorn").textContent = worn ? "Wearing: " + worn.name : "Wearing nothing";
  grid.textContent = "";
  for (const t of TITLES) {
    const auto = !!t.auto;
    const has = given.includes(t.id);
    const earned = owned.includes(t.id) && !has;
    const card = document.createElement("button");
    card.className = "title-card" + (has || earned ? " owned" : "") + (has ? " on" : "");
    card.style.setProperty("--tc", t.colour);
    card.style.setProperty("--tl", t.light);
    card.disabled = auto;
    card.appendChild(titleChip(t));
    const how = document.createElement("span");
    how.className = "how";
    how.textContent = t.how;
    card.appendChild(how);
    const state = document.createElement("span");
    state.className = "state";
    state.textContent = auto ? (earned ? "Earned by playing" : "Not earned yet")
      : has ? "Given — click to take back" : "Click to give";
    card.appendChild(state);
    card.onclick = () => toggleTitle(t.id);
    grid.appendChild(card);
  }
}

async function toggleTitle(id) {
  if (!current) return;
  const p = players.find((x) => x.uid === current) || {};
  const given = Array.isArray(p.titles) ? p.titles.slice() : [];
  const at = given.indexOf(id);
  if (at >= 0) given.splice(at, 1); else given.push(id);
  const patch = { titles: given, updatedAt: serverTimestamp() };
  if (at >= 0 && p.title === id) patch.title = "";      // taking back what they wear
  try {
    await setDoc(doc(db, "players", current), patch, { merge: true });
    p.titles = given;
    if (patch.title === "") p.title = "";
    drawAdminTitles(p);
    drawPlayers();
    toast(at >= 0 ? "Title taken back" : "Title given");
  } catch (err) {
    toast("Write failed: " + (err.code || err), 5000);
  }
}

async function patchSave(fn, note) {
  if (!current) return;
  let save;
  try {
    save = JSON.parse($("saveText").value || "{}");
  } catch (err) {
    return toast("The JSON in the box isn't valid - fix it first", 4000);
  }
  fn(save);
  $("saveText").value = JSON.stringify(save, null, 1);
  await pushSave(save, note);
}

async function pushSave(save, note) {
  try {
    await updateDoc(doc(db, "players", current), { save: JSON.stringify(save), updatedAt: serverTimestamp() });
    toast(note || "Saved");
    const p = players.find((x) => x.uid === current);
    if (p) p.save = JSON.stringify(save);
    drawPlayers();
  } catch (err) {
    toast("Write failed: " + (err.code || err), 5000);
  }
}

$("saveJson").onclick = () => patchSave(() => {}, "Save file written");
$("reload").onclick = () => current && openPlayer(current);

$("wipe").onclick = async () => {
  if (!current) return;
  if (!confirm("Wipe this player's progress? They start from scratch.")) return;
  await pushSave({}, "Save wiped");
  openPlayer(current);
};

$("giveCard").onclick = () => {
  const id = cardIdFrom($("cardPick").value);
  if (!id) return toast("Pick a card from the list", 3500);
  const card = cards.find((c) => c.id === id);
  patchSave((save) => {
    save.owned = save.owned || {};
    save.owned[id] = (save.owned[id] || 0) + 1;
    save.stamina = save.stamina || {};
    if (save.stamina[id] === undefined) save.stamina[id] = 100;
  }, `Gave ${card ? card.name : id}`);
};

$("giveCoins").onclick = () => {
  const n = Number($("coins").value || 0);
  patchSave((save) => { save.coins = Math.max(0, Number(save.coins || 0) + n); }, `${n >= 0 ? "+" : ""}${n} coins`);
};

$("giveSp").onclick = () => {
  const n = Number($("sp").value || 0);
  patchSave((save) => { save.star_points = Math.max(0, Number(save.star_points || 0) + n); },
            `${n >= 0 ? "+" : ""}${n} star points`);
};

$("ban").onclick = () => setBan(true);
$("unban").onclick = () => setBan(false);

async function setBan(on) {
  if (!current) return;
  try {
    await updateDoc(doc(db, "players", current), {
      banned: on,
      banReason: on ? ($("banReason").value.trim() || "Banned by the admin.") : "",
    });
    toast(on ? "Banned" : "Unbanned");
    const p = players.find((x) => x.uid === current);
    if (p) { p.banned = on; p.banReason = $("banReason").value.trim(); }
    $("ban").hidden = on;
    $("unban").hidden = !on;
    $("editHint").textContent = on ? "This account is banned." : "";
    drawPlayers();
  } catch (err) {
    toast("Write failed: " + (err.code || err), 5000);
  }
}

// ---------------------------------------------------------------- moderation
$("mute").onclick = () => setMute(true);
$("unmute").onclick = () => setMute(false);

async function setMute(on) {
  if (!current) return;
  try {
    await updateDoc(doc(db, "players", current), { muted: on });
    const p = players.find((x) => x.uid === current);
    if (p) p.muted = on;
    $("mute").hidden = on;
    $("unmute").hidden = !on;
    toast(on ? "Muted in chat" : "Unmuted");
    drawPlayers();
  } catch (err) {
    toast("Write failed: " + (err.code || err), 5000);
  }
}

$("saveName").onclick = async () => {
  if (!current) return;
  const wanted = tidyUsername($("editName").value);
  if (!wanted) return toast("Type a name first");
  const verdict = checkText(wanted, { username: true });
  if (!verdict.ok && verdict.level !== "reserved") return toast(verdict.why, 4000);
  try {
    await setDoc(doc(db, "usernames", usernameKey(wanted)), {
      uid: current, username: wanted, at: serverTimestamp(),
    });
    await updateDoc(doc(db, "players", current), { username: wanted, usernameKey: usernameKey(wanted) });
    const p = players.find((x) => x.uid === current);
    if (p) p.username = wanted;
    toast("Renamed to " + wanted);
    drawPlayers();
  } catch (err) {
    toast("Write failed: " + (err.code || err), 5000);
  }
};

$("saveRp").onclick = async () => {
  if (!current) return;
  const rp = Math.max(0, Math.round(Number($("editRp").value || 0)));
  try {
    await updateDoc(doc(db, "players", current), { rp });
    const p = players.find((x) => x.uid === current);
    if (p) p.rp = rp;
    $("rankNow").textContent = rankLine(rankOf(rp));
    toast("Set to " + rankLine(rankOf(rp)));
    drawPlayers();
  } catch (err) {
    toast("Write failed: " + (err.code || err), 5000);
  }
};

// ---------------------------------------------------------------- reports
let reports = [];

async function loadReports() {
  const box = $("reportList");
  try {
    const snap = await getDocs(query(collection(db, "reports"), orderBy("at", "desc"), limit(80)));
    reports = snap.docs.map((d) => ({ id: d.id, ...d.data() }));
  } catch (err) {
    box.textContent = "Couldn't read reports: " + (err.code || err);
    return;
  }
  drawReports();
}
$("reportsRefresh").onclick = loadReports;
$("showDone").onchange = drawReports;

function drawReports() {
  const box = $("reportList");
  const showDone = $("showDone").checked;
  const list = reports.filter((r) => showDone || !r.done);
  $("reportCount").textContent = "— " + reports.filter((r) => !r.done).length + " waiting";
  box.textContent = "";
  if (!list.length) {
    box.textContent = showDone ? "Nothing reported yet." : "Nothing waiting. ";
    return;
  }
  for (const r of list) {
    const card = document.createElement("div");
    card.className = "result";
    card.style.cssText = "border:1px solid var(--edge);border-radius:12px;padding:14px;margin-bottom:12px";
    if (r.done) card.style.opacity = ".55";

    const head = document.createElement("div");
    head.className = "top";
    const who = document.createElement("span");
    who.innerHTML = "<b>" + (r.aboutName || "player") + "</b> reported by " + (r.byName || "someone")
      + " · " + (r.reason || "other");
    const when = document.createElement("span");
    when.className = "muted";
    when.textContent = r.at && r.at.toDate ? r.at.toDate().toLocaleString() : "";
    head.append(who, when);

    const text = document.createElement("p");
    text.className = "muted";
    text.style.margin = "8px 0 12px";
    text.textContent = '"' + (r.text || "") + '"';

    const row = document.createElement("div");
    row.className = "row";
    const open = document.createElement("button");
    open.className = "btn btn-sm";
    open.textContent = "Open player";
    open.onclick = () => r.about && openPlayer(r.about);
    const mute = document.createElement("button");
    mute.className = "btn btn-sm btn-danger";
    mute.textContent = "Mute them";
    mute.onclick = async () => {
      if (!r.about) return;
      await updateDoc(doc(db, "players", r.about), { muted: true }).catch(() => {});
      toast("Muted");
    };
    const del = document.createElement("button");
    del.className = "btn btn-sm btn-danger";
    del.textContent = "Delete message";
    del.hidden = !r.msgId;
    del.onclick = async () => {
      await deleteDoc(doc(db, "chat", r.msgId)).catch(() => {});
      toast("Message deleted");
      loadChat();
    };
    const done = document.createElement("button");
    done.className = "btn btn-sm";
    done.textContent = r.done ? "Reopen" : "Mark handled";
    done.onclick = async () => {
      await updateDoc(doc(db, "reports", r.id), { done: !r.done }).catch(() => {});
      r.done = !r.done;
      drawReports();
    };
    row.append(open, mute, del, done);
    card.append(head, text, row);
    box.appendChild(card);
  }
}

// ---------------------------------------------------------------- chat moderation
async function loadChat() {
  const box = $("chatAdmin");
  let rows = [];
  try {
    const snap = await getDocs(query(collection(db, "chat"), orderBy("at", "desc"), limit(40)));
    rows = snap.docs.map((d) => ({ id: d.id, ...d.data() }));
  } catch (err) {
    box.textContent = "Couldn't read chat: " + (err.code || err);
    return;
  }
  box.textContent = "";
  if (!rows.length) { box.textContent = "No messages yet."; return; }
  for (const m of rows) {
    const line = document.createElement("div");
    line.className = "chat-msg";
    line.style.padding = "6px 0";
    const who = document.createElement("span");
    who.className = "who";
    who.textContent = m.username || "player";
    const body = document.createElement("span");
    body.className = "body";
    body.textContent = m.text || "";
    const del = document.createElement("button");
    del.className = "btn btn-sm btn-danger";
    del.textContent = "Delete";
    del.onclick = async () => {
      await deleteDoc(doc(db, "chat", m.id)).catch(() => {});
      loadChat();
    };
    const mute = document.createElement("button");
    mute.className = "btn btn-sm";
    mute.textContent = "Mute";
    mute.onclick = async () => {
      await updateDoc(doc(db, "players", m.uid), { muted: true }).catch(() => {});
      toast("Muted " + (m.username || "them"));
    };
    line.append(who, body, del, mute);
    box.appendChild(line);
  }
}
$("chatRefresh").onclick = loadChat;

// ---------------------------------------------------------------- poll
const pollRef = doc(db, "site", "poll");
let poll = null;

async function loadPoll() {
  try {
    const s = await getDoc(pollRef);
    poll = s.exists() ? s.data() : null;
  } catch (err) {
    poll = null;
  }
  fillPollForm();
  await pollResults();
}

function fillPollForm() {
  const open = !!(poll && poll.open);
  $("pollState").textContent = poll
    ? (open ? "— live since " + (poll.postedAt || "just now") : "— closed")
    : "";
  $("pollClose").hidden = !open;
  if (!poll) return;
  $("pollQuestion").value = poll.question || "";
  (poll.options || []).forEach((o, i) => { if ($("pollOpt" + i)) $("pollOpt" + i).value = o; });
  $("pollReward").value = poll.reward != null ? poll.reward : 300;
  $("pollCurrency").value = poll.currency || "sp";
}

function pollFormValues() {
  const options = [0, 1, 2, 3].map((i) => $("pollOpt" + i).value.trim()).filter(Boolean);
  return {
    question: $("pollQuestion").value.trim(),
    options,
    reward: Math.max(0, Number($("pollReward").value || 0)),
    currency: $("pollCurrency").value,
  };
}

$("pollPost").onclick = async () => {
  const v = pollFormValues();
  if (!v.question) return toast("Write a question first");
  if (v.options.length < 2) return toast("Give them at least two answers");
  const id = "p" + Date.now().toString(36);
  try {
    await setDoc(pollRef, {
      id, open: true, postedAt: new Date().toISOString().slice(0, 16).replace("T", " "),
      updatedAt: serverTimestamp(), ...v,
    });
    poll = { id, open: true, ...v };
    toast("Poll is live — players see it as soon as they open the site");
    fillPollForm();
    await pollResults();
  } catch (err) {
    toast("Couldn't post it: " + (err.code || err), 5000);
  }
};

$("pollClose").onclick = async () => {
  if (!poll) return;
  try {
    await updateDoc(pollRef, { open: false, updatedAt: serverTimestamp() });
    poll.open = false;
    toast("Poll closed — the card disappears for players");
    fillPollForm();
  } catch (err) {
    toast("Couldn't close it: " + (err.code || err), 5000);
  }
};

$("pollRefresh").onclick = () => pollResults();

async function pollResults() {
  const box = $("pollResults");
  if (!poll || !poll.id) {
    box.textContent = "No poll posted yet.";
    return;
  }
  let votes = [];
  try {
    const snap = await getDocs(collection(db, "polls", poll.id, "votes"));
    votes = snap.docs.map((d) => d.data());
  } catch (err) {
    box.textContent = "Couldn't read the votes: " + (err.code || err);
    return;
  }
  const counts = (poll.options || []).map(() => 0);
  for (const v of votes) if (counts[v.choice] !== undefined) counts[v.choice] += 1;
  const total = votes.length;

  box.textContent = "";
  const head = document.createElement("p");
  head.className = "muted";
  head.style.margin = "0 0 14px";
  head.textContent = total + (total === 1 ? " answer" : " answers")
    + (poll.reward ? "  ·  " + (total * poll.reward) + " " + (poll.currency === "coins" ? "coins" : "Star Points") + " handed out" : "");
  box.appendChild(head);

  (poll.options || []).forEach((text, i) => {
    const pct = total ? Math.round((counts[i] / total) * 100) : 0;
    const row = document.createElement("div");
    row.className = "result";
    const top = document.createElement("div");
    top.className = "top";
    const left = document.createElement("span");
    left.textContent = text;
    const right = document.createElement("b");
    right.textContent = counts[i] + "  ·  " + pct + "%";
    top.append(left, right);
    const track = document.createElement("div");
    track.className = "track";
    const fill = document.createElement("div");
    fill.className = "fill";
    fill.style.width = pct + "%";
    track.appendChild(fill);
    row.append(top, track);
    box.appendChild(row);
  });

  if (total) {
    const who = document.createElement("p");
    who.className = "muted";
    who.style.marginTop = "12px";
    who.textContent = "Answered: " + votes.map((v) => v.name || "player").slice(0, 25).join(", ")
      + (total > 25 ? " and " + (total - 25) + " more" : "");
    box.appendChild(who);
  }
}

// ---------------------------------------------------------------- patch notes
let notes = [];
const notesRef = doc(db, "site", "patchNotes");

async function loadNotes() {
  try {
    const s = await getDoc(notesRef);
    notes = s.exists() && Array.isArray(s.data().entries) ? s.data().entries : [];
  } catch (err) {
    notes = [];
  }
  $("noteDate").value = new Date().toISOString().slice(0, 10);
  drawNotes();
}

function drawNotes() {
  const box = $("noteList");
  box.textContent = "";
  notes.forEach((n, i) => {
    const art = document.createElement("article");
    art.className = "note";
    const h = document.createElement("h3");
    h.textContent = n.title || "Update";
    const t = document.createElement("time");
    t.textContent = n.date || "";
    const d = document.createElement("div");
    d.textContent = n.body || "";
    const del = document.createElement("button");
    del.className = "btn btn-sm btn-danger";
    del.textContent = "Delete";
    del.style.marginTop = "10px";
    del.onclick = async () => {
      notes.splice(i, 1);
      await writeNotes("Note deleted");
    };
    art.append(h, t, d, del);
    box.appendChild(art);
  });
}

async function writeNotes(msg) {
  try {
    await setDoc(notesRef, { entries: notes, updatedAt: serverTimestamp() });
    toast(msg || "Patch notes updated");
    drawNotes();
  } catch (err) {
    toast("Write failed: " + (err.code || err), 5000);
  }
}

$("addNote").onclick = async () => {
  const title = $("noteTitle").value.trim();
  const body = $("noteBody").value.trim();
  if (!title && !body) return toast("Write something first");
  notes.unshift({ date: $("noteDate").value.trim(), title, body });
  notes = notes.slice(0, 40);
  $("noteTitle").value = "";
  $("noteBody").value = "";
  await writeNotes("Posted");
};
