// Admin console: every player's save, bans, card grants and patch notes.
// Only the admin account can read or write any of this - see firestore.rules.

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
  getAuth, GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import {
  getFirestore, collection, getDocs, doc, getDoc, setDoc, updateDoc, serverTimestamp, query, orderBy, limit,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";
import { firebaseConfig, ADMIN_EMAIL } from "./firebase-config.js";

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
  if (!isAdmin) return;
  $("avatar").src = user.photoURL || "";
  $("uname").textContent = user.displayName || user.email;
  await loadCards();
  await loadPlayers();
  await loadNotes();
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
      (p.name || "Player") + (p.banned ? " (banned)" : ""),
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
    b.className = "small ghost";
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
  $("editHint").textContent = p.banned ? "This account is banned." : "";
  $("editor").scrollIntoView({ behavior: "smooth", block: "start" });
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
    del.className = "small danger";
    del.textContent = "Delete";
    del.style.marginTop = "8px";
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
