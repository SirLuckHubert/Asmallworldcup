// SCOUT RNG (6 Nov 2026) - the roll game on the website.
//
// Roll for players like Sol's RNG: every card in the game has a "1 in N" chance, rarer the
// higher it's rated. Rolls are checked rarest first, each one passing with luck / N, so the
// odds on the screen are the real odds. No sign-in needed; signed in, it saves to your account.
//
// Only the coins are real. Up to five rolled players work for you and make coins every hour
// (300 an hour at most) into a vault that holds a day's worth (7,200). Signed in, the vault
// is sent to your club as game mail. Rolls also give FRAGMENTS: 100,000 of them swap for
// any 120-128 player, sent to the game the same way. A free pack every 30 seconds holds
// potions (luck, speed), fragments or extra rolls.
//
// Everything runs in the browser, like the game's own save: the numbers below are the rules.

import { makeMail } from "./mail.js?v=2026-11-06a";

export const RULES = {
  rollMs: 1000, speedMs: 500,            // roll cooldown, and with a Speed Potion
  bonusEvery: 10,                        // every 10th roll is a bonus roll at 2x luck
  packMs: 30000, packMax: 5,             // a free pack every 30 s, up to 5 waiting
  squad: 5, rateCap: 300, vaultCap: 7200, // coins an hour (all five together), and the vault
  fragGoal: 100000,                      // fragments for one 120-128 player
};

export const TIERS = [
  { key: "Common",    col: "#b7c2d6", frag: 0,     coin: 1 },
  { key: "Uncommon",  col: "#62e88a", frag: 0,     coin: 2 },
  { key: "Rare",      col: "#4fa8ff", frag: 1,     coin: 5 },
  { key: "Epic",      col: "#b98bff", frag: 3,     coin: 10 },
  { key: "Legendary", col: "#ffd24a", frag: 15,    coin: 20 },
  { key: "Mythic",    col: "#ff5fa2", frag: 90,    coin: 40 },
  { key: "Exalted",   col: "#ff7b3d", frag: 800,   coin: 75 },
  { key: "Glitched",  col: "#7dfcff", frag: 20000, coin: 120 },
];
const TIER = Object.fromEntries(TIERS.map((t, i) => [t.key, { ...t, i }]));

export const POTIONS = {
  lucky:   { name: "Lucky Potion",   short: "LUCKY",   col: "#62e88a", luck: 2,   secs: 60,  what: "2x luck for 60 s" },
  super:   { name: "Super Lucky",    short: "SUPER",   col: "#4fa8ff", luck: 5,   secs: 60,  what: "5x luck for 60 s" },
  mega:    { name: "Mega Lucky",     short: "MEGA",    col: "#b98bff", luck: 10,  secs: 30,  what: "10x luck for 30 s" },
  speed:   { name: "Speed Potion",   short: "SPEED",   col: "#ffd24a", speed: true, secs: 90, what: "rolls twice as fast for 90 s" },
  miracle: { name: "Miracle Potion", short: "MIRACLE", col: "#7dfcff", luck: 100, rolls: 5,  what: "100x luck on your next 5 rolls" },
};
// what a free pack can hold (weights)
const PACK = [
  ["lucky", 34], ["bag", 25], ["speed", 20], ["super", 12], ["mega", 6], ["triple", 2.5], ["miracle", 0.5],
];

const $ = (id) => document.getElementById(id);
const fmt = (n) => Math.floor(n).toLocaleString();
const now = () => Date.now();

let CARDS = [], BY_ID = {}, GROUPS = [], EXCHANGE = [];
let S = null;                       // the state
let api = null;                     // set while signed in: { uid, username, load, save, sendMail, board }
let cooling = 0, autoOn = false, busy = false, saveTimer = null, cloudTimer = null;
const recent = [];

// ------------------------------------------------------------------ state
function fresh() {
  const t = now();
  return { v: 1, rolls: 0, frags: 0, owned: {}, squad: [], packs: 1, packAt: t,
           inv: { lucky: 1, super: 0, mega: 0, speed: 0, miracle: 0 }, active: {}, miracle: 0,
           vault: 0, vaultAt: t, best: null, sent: 0, swaps: 0 };
}

function clean(s) {
  const f = fresh();
  if (!s || typeof s !== "object" || s.v !== 1) return f;
  const out = { ...f, ...s };
  out.owned = {};
  for (const [id, n] of Object.entries(s.owned || {})) if (BY_ID[id] && n > 0) out.owned[id] = Math.floor(n);
  out.squad = (Array.isArray(s.squad) ? s.squad : []).filter((id) => out.owned[id]).slice(0, RULES.squad);
  out.inv = { ...f.inv, ...(s.inv || {}) };
  for (const k of Object.keys(out.inv)) out.inv[k] = Math.max(0, Math.floor(Number(out.inv[k]) || 0));
  out.active = typeof s.active === "object" && s.active ? s.active : {};
  for (const k of ["rolls", "frags", "packs", "vault", "miracle", "sent", "swaps"]) out[k] = Math.max(0, Number(out[k]) || 0);
  out.packs = Math.min(RULES.packMax, out.packs);
  out.vault = Math.min(RULES.vaultCap, out.vault);
  if (out.best && !BY_ID[out.best.id]) out.best = null;
  return out;
}

const localKey = () => "aswc_scout_v1" + (api ? "_" + api.uid : "");
function readLocal(key) {
  try { return JSON.parse(localStorage.getItem(key) || "null"); } catch (err) { return null; }
}
function saveLocal() {
  try { localStorage.setItem(localKey(), JSON.stringify(S)); } catch (err) { /* private mode */ }
}
function changed(important = false) {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(saveLocal, 400);
  if (api) {
    clearTimeout(cloudTimer);
    cloudTimer = setTimeout(pushCloud, important ? 50 : 5000);
  }
}
async function pushCloud() {
  if (!api) return;
  try {
    await api.save({
      state: JSON.stringify(S), rolls: S.rolls,
      bestN: S.best ? S.best.n : 0, bestId: S.best ? S.best.id : "", bestName: S.best ? S.best.name : "",
      username: api.username || "",
    });
  } catch (err) { console.warn("scout save failed", err); }
}

// ------------------------------------------------------------------ the clock: packs, vault, potions
function rate() {
  let sum = 0;
  for (const id of S.squad) sum += TIER[BY_ID[id].tier].coin;
  return Math.min(RULES.rateCap, sum);
}
function accrue() {
  const t = now();
  // packs
  if (S.packs >= RULES.packMax) S.packAt = t;
  else {
    const n = Math.floor((t - S.packAt) / RULES.packMs);
    if (n > 0) {
      S.packs = Math.min(RULES.packMax, S.packs + n);
      S.packAt = S.packs >= RULES.packMax ? t : S.packAt + n * RULES.packMs;
    }
  }
  // the vault
  const dt = Math.max(0, t - S.vaultAt);
  S.vault = Math.min(RULES.vaultCap, S.vault + rate() * dt / 3600000);
  S.vaultAt = t;
  // potions that ran out
  for (const [k, until] of Object.entries(S.active)) if (until <= t) delete S.active[k];
}
function luckNow(bonus) {
  let luck = 1;
  for (const k of Object.keys(S.active)) if (POTIONS[k] && POTIONS[k].luck) luck += POTIONS[k].luck - 1;
  if (bonus) luck *= 2;
  if (S.miracle > 0) luck *= POTIONS.miracle.luck;
  return luck;
}
const speedOn = () => !!S.active.speed;

// ------------------------------------------------------------------ rolling
function pick(luck) {
  for (const g of GROUPS) {
    if (Math.random() < luck * g.cards.length / g.n) return g.cards[Math.floor(Math.random() * g.cards.length)];
  }
  const last = GROUPS[GROUPS.length - 1].cards;
  return last[Math.floor(Math.random() * last.length)];
}

function take(card) {
  const first = !S.owned[card.id];
  S.owned[card.id] = (S.owned[card.id] || 0) + 1;
  S.frags += TIER[card.tier].frag;
  S.rolls += 1;
  if (!S.best || card.n > S.best.n) S.best = { id: card.id, n: card.n, name: card.name };
  // a new card fills an empty squad slot by itself
  if (first && S.squad.length < RULES.squad) S.squad.push(card.id);
  recent.unshift(card.id);
  recent.length = Math.min(recent.length, 10);
  return first;
}

function oneRoll(extraLuck = 1) {
  accrue();
  const bonus = (S.rolls + 1) % RULES.bonusEvery === 0;
  const luck = luckNow(bonus) * extraLuck;
  if (S.miracle > 0) S.miracle -= 1;
  const card = pick(luck);
  const first = take(card);
  return { card, first, luck, bonus };
}

async function roll() {
  if (busy || now() < cooling || !CARDS.length) return;
  busy = true;
  const res = oneRoll();
  cooling = now() + (speedOn() ? RULES.speedMs : RULES.rollMs);
  await spin(res.card, autoOn);
  await reveal(res);
  busy = false;
  changed(TIER[res.card.tier].i >= TIER.Legendary.i);
  draw();
  if (autoOn) setTimeout(roll, Math.max(30, cooling - now()));
}

// ------------------------------------------------------------------ the stage
function img(card) { return "media/p/" + card.img; }

function spin(final, quick) {
  return new Promise((done) => {
    const pic = $("scPic"), name = $("scName"), odds = $("scOdds"), tier = $("scTier");
    $("scStage").classList.remove("hit");
    $("scStage").classList.add("spinning");
    const frames = quick ? 4 : 7;
    let k = 0;
    const step = () => {
      if (k >= frames) { $("scStage").classList.remove("spinning"); done(); return; }
      const c = k === frames - 1 ? final : CARDS[Math.floor(Math.random() * CARDS.length)];
      pic.src = img(c);
      name.textContent = c.name;
      odds.textContent = "1 in " + fmt(c.n);
      tier.textContent = c.tier;
      $("scStage").style.setProperty("--tc", TIER[c.tier].col);
      k += 1;
      setTimeout(step, quick ? 45 : 40 + k * 12);
    };
    step();
  });
}

function reveal(res) {
  return new Promise((done) => {
    const { card, first, bonus } = res;
    const t = TIER[card.tier];
    const stage = $("scStage");
    stage.style.setProperty("--tc", t.col);
    stage.classList.add("hit");
    $("scNew").hidden = !first;
    $("scBonus").hidden = !bonus;
    $("scCount").textContent = "×" + S.owned[card.id];
    if (t.i < TIER.Legendary.i) { done(); return; }
    // a big one: the cutscene (skip with a click)
    const cut = $("scCut");
    cut.style.setProperty("--tc", t.col);
    cut.className = "sc-cut on t-" + card.tier.toLowerCase();
    $("scCutTier").textContent = card.tier;
    $("scCutName").textContent = card.name;
    $("scCutOdds").textContent = "1 in " + fmt(card.n);
    $("scCutPic").src = img(card);
    const ms = t.i >= TIER.Exalted.i ? 3200 : t.i >= TIER.Mythic.i ? 2400 : 1600;
    let ended = false;
    const end = () => { if (ended) return; ended = true; cut.className = "sc-cut"; done(); };
    cut.onclick = end;
    setTimeout(end, ms);
  });
}

// ------------------------------------------------------------------ packs and potions
function openPack() {
  accrue();
  if (S.packs < 1 || busy) return;
  if (S.packs >= RULES.packMax) S.packAt = now();
  S.packs -= 1;
  const total = PACK.reduce((a, p) => a + p[1], 0);
  let r = Math.random() * total, kind = PACK[0][0];
  for (const [k, w] of PACK) { if ((r -= w) < 0) { kind = k; break; } }
  let line;
  if (kind === "bag") {
    const n = 5 + Math.floor(Math.random() * 16);
    S.frags += n;
    line = "+" + n + " fragments";
  } else if (kind === "triple") {
    const got = [oneRoll(3), oneRoll(3), oneRoll(3)].map((x) => x.card);
    const top = got.sort((a, b) => b.n - a.n)[0];
    line = "3 rolls at 3x luck — best: " + top.name + " (1 in " + fmt(top.n) + ")";
  } else {
    S.inv[kind] = (S.inv[kind] || 0) + 1;
    line = POTIONS[kind].name + " — " + POTIONS[kind].what;
  }
  const pop = $("scPackPop");
  pop.textContent = line;
  pop.style.setProperty("--pc", kind === "bag" ? "#ffd24a" : kind === "triple" ? "#ff5fa2" : POTIONS[kind].col);
  pop.classList.remove("show"); void pop.offsetWidth; pop.classList.add("show");
  $("scPack").classList.remove("pop"); void $("scPack").offsetWidth; $("scPack").classList.add("pop");
  changed();
  draw();
}

function drink(k) {
  accrue();
  if (!S.inv[k]) return;
  S.inv[k] -= 1;
  const p = POTIONS[k];
  if (p.rolls) S.miracle += p.rolls;
  else S.active[k] = Math.max(now(), S.active[k] || 0) + p.secs * 1000;   // the same potion again: longer
  changed();
  draw();
}

// ------------------------------------------------------------------ squad, vault, fragments
function toggleSquad(id) {
  accrue();
  const i = S.squad.indexOf(id);
  if (i >= 0) S.squad.splice(i, 1);
  else if (S.squad.length < RULES.squad) S.squad.push(id);
  else { note("Your squad is full — take someone out first."); return; }
  changed();
  draw();
}
function bestSquad() {
  accrue();
  S.squad = Object.keys(S.owned).sort((a, b) => BY_ID[b].n - BY_ID[a].n).slice(0, RULES.squad);
  changed();
  draw();
}

async function collect() {
  accrue();
  const coins = Math.floor(S.vault);
  if (coins < 1) { note("Nothing in the vault yet — put players in your squad."); return; }
  if (!api) { note("Sign in (top right) to send the coins to your club. They'll wait here."); return; }
  const btn = $("scCollect");
  btn.disabled = true;
  try {
    await api.sendMail(makeMail({
      from: "SCOUT RNG", subject: coins.toLocaleString() + " COINS FROM YOUR SCOUTS",
      body: "What your Scout RNG squad made while you were away. Claim it here.", gift: { coins },
    }));
    S.vault -= coins;
    S.sent += coins;
    changed(true);
    note(coins.toLocaleString() + " coins sent — claim them in the game's MAIL.");
  } catch (err) {
    note("Couldn't send them: " + (err.code || err));
  }
  btn.disabled = false;
  draw();
}

function openSwap() {
  if (S.frags < RULES.fragGoal) return;
  if (!api) { note("Sign in to swap fragments for a player — he goes straight to your club."); return; }
  const grid = $("scSwapGrid");
  grid.textContent = "";
  for (const c of EXCHANGE) {
    const b = document.createElement("button");
    b.className = "sc-swap-card";
    b.innerHTML = '<img loading="lazy" alt=""><span></span>';
    b.querySelector("img").src = img(c);
    b.querySelector("span").textContent = c.name;
    b.onclick = () => {
      for (const x of grid.children) x.classList.remove("sel");
      b.classList.add("sel");
      swapPick = c;
      $("scSwapGo").disabled = false;
      $("scSwapGo").textContent = "Swap for " + c.name + " (" + c.r + ")";
    };
    grid.appendChild(b);
  }
  swapPick = null;
  $("scSwapGo").disabled = true;
  $("scSwapGo").textContent = "Pick a player";
  $("scSwap").hidden = false;
}
let swapPick = null;
async function swap() {
  const card = swapPick;
  if (!card || S.frags < RULES.fragGoal || !api) return;
  $("scSwapGo").disabled = true;
  try {
    await api.sendMail(makeMail({
      from: "SCOUT RNG", subject: card.name.toUpperCase() + " JOINS YOUR CLUB",
      body: "Swapped for " + RULES.fragGoal.toLocaleString() + " fragments in Scout RNG.", gift: { cards: [card.id] },
    }));
    S.frags -= RULES.fragGoal;
    S.swaps += 1;
    changed(true);
    $("scSwap").hidden = true;
    note(card.name + " is on his way — claim him in the game's MAIL.");
  } catch (err) {
    note("Couldn't swap: " + (err.code || err));
  }
  draw();
}

let noteTimer = null;
function note(text) {
  const n = $("scNote");
  n.textContent = text;
  n.classList.add("show");
  clearTimeout(noteTimer);
  noteTimer = setTimeout(() => n.classList.remove("show"), 4200);
}

// ------------------------------------------------------------------ drawing
const bottle = (col) =>
  '<svg viewBox="0 0 24 32" aria-hidden="true"><path d="M9 2h6v6l5 7v12a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V15l5-7z" fill="' + col +
  '" fill-opacity=".9" stroke="#fff" stroke-width="1.4"/><rect x="8" y="1" width="8" height="4" rx="1.5" fill="#fff"/>' +
  '<path d="M7 19h10" stroke="#fff" stroke-opacity=".6" stroke-width="1.4"/></svg>';

function draw() {
  if (!S) return;
  accrue();
  const t = now();
  // luck line
  const bonusIn = RULES.bonusEvery - (S.rolls % RULES.bonusEvery);
  $("scLuck").textContent = luckNow(bonusIn === 1).toFixed(1).replace(/\.0$/, "") + "x";
  $("scBonusIn").textContent = bonusIn === 1 ? "next roll is a BONUS roll" : "bonus roll in " + bonusIn;
  $("scRolls").textContent = fmt(S.rolls);
  $("scBest").textContent = S.best ? S.best.name + " · 1 in " + fmt(S.best.n) : "—";
  const left = Math.max(0, cooling - t);
  $("scRoll").classList.toggle("cool", left > 0 || busy);
  $("scAuto").classList.toggle("on", autoOn);
  $("scAuto").textContent = autoOn ? "Auto: on" : "Auto: off";

  // active potions
  const act = $("scActive");
  act.textContent = "";
  for (const [k, until] of Object.entries(S.active)) {
    const p = POTIONS[k];
    if (!p) continue;
    const el = document.createElement("span");
    el.className = "sc-act";
    el.style.setProperty("--pc", p.col);
    el.style.setProperty("--p", Math.max(0, Math.min(1, (until - t) / (p.secs * 1000))));
    el.textContent = p.short + " " + Math.ceil((until - t) / 1000) + "s";
    act.appendChild(el);
  }
  if (S.miracle > 0) {
    const el = document.createElement("span");
    el.className = "sc-act";
    el.style.setProperty("--pc", POTIONS.miracle.col);
    el.style.setProperty("--p", S.miracle / 5);
    el.textContent = "MIRACLE ×" + S.miracle;
    act.appendChild(el);
  }

  // the pack
  $("scPacks").textContent = "×" + S.packs;
  const ready = S.packs > 0;
  $("scPackBtn").disabled = !ready;
  const pleft = S.packs >= RULES.packMax ? 0 : RULES.packMs - (t - S.packAt);
  $("scPackTime").textContent = S.packs >= RULES.packMax ? "Full — open one" : "Next in " + Math.ceil(pleft / 1000) + "s";
  $("scPackRing").style.setProperty("--p", S.packs >= RULES.packMax ? 1 : 1 - pleft / RULES.packMs);
  $("scPack").classList.toggle("ready", ready);

  // potions you hold
  const inv = $("scInv");
  if (!inv.dataset.built) {
    for (const k of Object.keys(POTIONS)) {
      const b = document.createElement("button");
      b.className = "sc-pot";
      b.dataset.k = k;
      b.title = POTIONS[k].name + " — " + POTIONS[k].what;
      b.innerHTML = bottle(POTIONS[k].col) + '<span class="pn">' + POTIONS[k].short + '</span><span class="pc"></span>';
      b.onclick = () => drink(k);
      inv.appendChild(b);
    }
    inv.dataset.built = "1";
  }
  for (const b of inv.children) {
    const n = S.inv[b.dataset.k] || 0;
    b.querySelector(".pc").textContent = "×" + n;
    b.disabled = n < 1;
  }

  // squad
  const sq = $("scSquad");
  sq.textContent = "";
  for (let i = 0; i < RULES.squad; i++) {
    const id = S.squad[i];
    const slot = document.createElement("button");
    slot.className = "sc-slot" + (id ? " full" : "");
    if (id) {
      const c = BY_ID[id];
      slot.style.setProperty("--tc", TIER[c.tier].col);
      slot.innerHTML = '<img alt="">' + '<span class="sn"></span><span class="sr">+' + TIER[c.tier].coin + "/h</span>";
      slot.querySelector("img").src = img(c);
      slot.querySelector(".sn").textContent = c.name;
      slot.title = "Take " + c.name + " out";
      slot.onclick = () => toggleSquad(id);
    } else {
      slot.innerHTML = '<span class="sn">Empty</span><span class="sr">pick below</span>';
      slot.onclick = () => $("scIndex").scrollIntoView({ behavior: "smooth", block: "start" });
    }
    sq.appendChild(slot);
  }
  const r = rate();
  $("scRate").textContent = r + " / " + RULES.rateCap;
  $("scRateFill").style.width = (100 * r / RULES.rateCap) + "%";

  // vault
  $("scVault").textContent = fmt(S.vault);
  $("scVaultFill").style.width = (100 * S.vault / RULES.vaultCap) + "%";
  $("scVaultNote").textContent = S.vault >= RULES.vaultCap ? "Full — collect it or your scouts stop earning"
    : r ? "Full in " + hrs((RULES.vaultCap - S.vault) / r) : "Put players in your squad to start earning";
  $("scCollect").textContent = api ? "Send to my club" : "Sign in to collect";

  // fragments
  $("scFrags").textContent = fmt(S.frags);
  $("scFragFill").style.width = Math.min(100, 100 * S.frags / RULES.fragGoal) + "%";
  $("scSwapBtn").disabled = S.frags < RULES.fragGoal;

  drawIndex();
}
function hrs(h) {
  if (h < 1) return Math.max(1, Math.round(h * 60)) + " min";
  return (h < 10 ? h.toFixed(1) : Math.round(h)) + " h";
}

let indexKey = "";
function drawIndex() {
  const filter = $("scFilter").value;
  const owned = Object.keys(S.owned).length;
  $("scIndexCount").textContent = owned + " / " + CARDS.length + " scouted";
  const key = filter + "|" + owned + "|" + S.squad.join(",") + "|" + Object.values(S.owned).reduce((a, b) => a + b, 0);
  if (key === indexKey) return;
  indexKey = key;
  const grid = $("scGrid");
  grid.textContent = "";
  for (const c of CARDS) {
    const have = S.owned[c.id] || 0;
    if (filter === "owned" && !have) continue;
    if (filter === "missing" && have) continue;
    if (filter !== "all" && filter !== "owned" && filter !== "missing" && c.tier !== filter) continue;
    const b = document.createElement("button");
    b.className = "sc-cell" + (have ? " have" : "") + (S.squad.includes(c.id) ? " in" : "");
    b.style.setProperty("--tc", TIER[c.tier].col);
    if (have) {
      b.innerHTML = '<img loading="lazy" alt=""><span class="cn"></span><span class="co"></span>';
      b.querySelector("img").src = img(c);
      b.querySelector(".cn").textContent = c.name + (have > 1 ? " ×" + have : "");
      b.title = (S.squad.includes(c.id) ? "Take out of" : "Put in") + " your squad · +" + TIER[c.tier].coin + " coins/h";
      b.onclick = () => toggleSquad(c.id);
    } else {
      b.innerHTML = '<span class="q">?</span><span class="cn">' + c.tier + '</span><span class="co"></span>';
      b.disabled = true;
    }
    b.querySelector(".co").textContent = "1 in " + fmt(c.n);
    grid.appendChild(b);
  }
}

// the rarest pulls on the site
export async function drawBoard() {
  const box = $("scBoard");
  if (!box) return;
  if (!api) { box.innerHTML = '<li class="muted">Sign in to see everyone\'s rarest pulls.</li>'; return; }
  try {
    const rows = await api.board();
    box.textContent = "";
    if (!rows.length) { box.innerHTML = '<li class="muted">No pulls yet — be the first.</li>'; return; }
    rows.forEach((r, i) => {
      const c = BY_ID[r.bestId];
      if (!c) return;
      const li = document.createElement("li");
      li.style.setProperty("--tc", TIER[c.tier].col);
      li.innerHTML = '<span class="bp">' + (i + 1) + '</span><img alt=""><span class="bw"><b></b><span></span></span><span class="bo"></span>';
      li.querySelector("img").src = img(c);
      li.querySelector("b").textContent = r.username || "player";
      li.querySelector(".bw span").textContent = c.name + " · " + c.tier;
      li.querySelector(".bo").textContent = "1 in " + fmt(c.n);
      box.appendChild(li);
    });
  } catch (err) {
    box.innerHTML = '<li class="muted">Couldn\'t load the pulls.</li>';
  }
}

// ------------------------------------------------------------------ start, sign in, sign out
let booted = null;
export function rngBoot() { booted = booted || boot(); return booted; }
async function boot() {
  const root = $("scout");
  if (!root) return;
  try {
    CARDS = await (await fetch("rng_cards.json?v=2026-11-06a")).json();
  } catch (err) {
    root.querySelector(".sc-stage").innerHTML = '<p class="muted">Scout RNG couldn\'t load its cards. Reload the page.</p>';
    return;
  }
  CARDS.sort((a, b) => b.n - a.n);
  BY_ID = Object.fromEntries(CARDS.map((c) => [c.id, c]));
  const g = {};
  for (const c of CARDS) (g[c.n] = g[c.n] || []).push(c);
  GROUPS = Object.keys(g).map(Number).sort((a, b) => b - a).map((n) => ({ n, cards: g[n] }));
  EXCHANGE = CARDS.filter((c) => c.x).sort((a, b) => b.r - a.r || a.name.localeCompare(b.name));
  try {
    // only offer players the game on this site knows (cards.json is its card list): a card the game
    // doesn't have would be thrown away when the mail is claimed
    const known = new Set((await (await fetch("cards.json?v=2026-11-06a")).json()).map((c) => c.id));
    if (known.size) EXCHANGE = EXCHANGE.filter((c) => known.has(c.id));
  } catch (err) { /* no list: offer them all */ }

  S = clean(readLocal(localKey()));
  const sel = $("scFilter");
  for (const t of TIERS) { const o = document.createElement("option"); o.value = t.key; o.textContent = t.key; sel.appendChild(o); }
  sel.onchange = () => { indexKey = ""; drawIndex(); };
  $("scRoll").onclick = roll;
  $("scAuto").onclick = () => { autoOn = !autoOn; draw(); if (autoOn) roll(); };
  $("scPackBtn").onclick = openPack;
  $("scBestBtn").onclick = bestSquad;
  $("scCollect").onclick = collect;
  $("scSwapBtn").onclick = openSwap;
  $("scSwapClose").onclick = () => { $("scSwap").hidden = true; };
  $("scSwapGo").onclick = swap;
  document.addEventListener("keydown", (e) => {
    if (e.code !== "Space" || !root.matches(":hover") || /INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) return;
    e.preventDefault();
    roll();
  });
  window.addEventListener("beforeunload", saveLocal);
  document.addEventListener("visibilitychange", () => { if (document.hidden) { saveLocal(); if (api) pushCloud(); } });
  $("scPic").src = S.best ? img(BY_ID[S.best.id]) : "media/p/_back.svg";
  $("scName").textContent = S.best ? "Your best: " + S.best.name : "Press ROLL";
  $("scOdds").textContent = S.best ? "1 in " + fmt(S.best.n) : "266 players to find";
  $("scTier").textContent = S.best ? BY_ID[S.best.id].tier : "Scout RNG";
  if (S.best) $("scStage").style.setProperty("--tc", TIER[BY_ID[S.best.id].tier].col);
  draw();
  setInterval(draw, 500);
  drawBoard();
}

/** Signed in: switch to the account's progress (a guest's progress moves in the first time). */
export async function rngSignedIn(account) {
  await rngBoot();
  if (!CARDS.length) return;
  saveLocal();
  const guest = readLocal("aswc_scout_v1");
  api = account;
  let cloud = null;
  try {
    const d = await api.load();
    if (d && typeof d.state === "string") cloud = JSON.parse(d.state);
  } catch (err) { console.warn("scout load failed", err); }
  const mine = readLocal(localKey());
  const pickOf = [cloud, mine, guest].filter(Boolean).sort((a, b) => (b.rolls || 0) - (a.rolls || 0))[0];
  S = clean(pickOf);
  if (pickOf === guest && guest && guest.rolls) {
    try { localStorage.removeItem("aswc_scout_v1"); } catch (err) { /* fine */ }
  }
  saveLocal();
  changed(true);
  indexKey = "";
  draw();
  drawBoard();
}

export async function rngSignedOut() {
  await rngBoot();
  if (!CARDS.length) return;
  saveLocal();
  api = null;
  S = clean(readLocal(localKey()));
  indexKey = "";
  draw();
  drawBoard();
}

export function rngUsername(name) {
  if (api) { api.username = name; changed(); }
}
