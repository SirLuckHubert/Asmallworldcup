// Mail: a message from you to a player, with coins, star points or players attached.
//
// Mail lives inside the save file, which is the one thing the game and the site already
// share. The admin console writes a message straight into a player's save; a message for
// everyone goes in site/mail and is merged into each player's save the next time they
// open the game. The game shows the inbox and hands out whatever is attached.

export const MAIL_KEEP = 40;          // the game keeps the newest forty

export function newId() {
  return "m" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
}

/** One message, ready to drop into a save. */
export function makeMail({ from = "HUBI", subject = "", body = "", gift = null, id = null } = {}) {
  const out = {
    id: id || newId(),
    at: new Date().toISOString().slice(0, 10),
    from: String(from || "HUBI").slice(0, 24),
    subject: String(subject || "MESSAGE").slice(0, 60),
    body: String(body || "").slice(0, 900),
    read: false,
    claimed: false,
  };
  const g = tidyGift(gift);
  if (g) out.gift = g;
  return out;
}

/** Only the parts of a gift that are worth carrying. */
export function tidyGift(gift) {
  if (!gift) return null;
  const coins = Math.max(0, Math.floor(Number(gift.coins) || 0));
  const sp = Math.max(0, Math.floor(Number(gift.sp) || 0));
  const cards = (gift.cards || []).filter(Boolean).slice(0, 6);
  if (!coins && !sp && !cards.length) return null;
  return { coins, sp, cards };
}

export function giftWords(gift, cardName) {
  const g = tidyGift(gift);
  if (!g) return "";
  const bits = [];
  if (g.coins) bits.push(g.coins + " coins");
  if (g.sp) bits.push(g.sp + " star points");
  for (const id of g.cards) bits.push(cardName ? cardName(id) : id);
  return bits.join(" + ");
}

/** Add a message to a save object (newest first, capped). Returns the save. */
export function addMail(save, msg) {
  const box = Array.isArray(save.mail) ? save.mail : [];
  box.unshift(msg);
  save.mail = box.slice(0, MAIL_KEEP);
  return save;
}

/**
 * Merge the messages meant for everyone into a player's save.
 * Returns true if anything was added - the caller then writes the save back.
 */
export function mergeBroadcast(save, items) {
  if (!save || !Array.isArray(items) || !items.length) return false;
  const box = Array.isArray(save.mail) ? save.mail : [];
  const have = new Set(box.map((m) => m && m.id));
  const seen = Array.isArray(save.mail_seen) ? save.mail_seen : [];
  const dropped = new Set(seen);                 // read and deleted: don't bring it back
  let added = false;
  for (const item of items) {
    if (!item || !item.id || have.has(item.id) || dropped.has(item.id)) continue;
    box.unshift({ ...item, read: false, claimed: false });
    have.add(item.id);
    added = true;
  }
  if (!added) return false;
  box.sort((a, b) => String(b.at || "").localeCompare(String(a.at || "")));
  save.mail = box.slice(0, MAIL_KEEP);
  save.mail_seen = Array.from(new Set(seen.concat(items.map((i) => i && i.id).filter(Boolean)))).slice(-120);
  return true;
}

/** Parse a save, merge, and hand back the new text - or null if nothing changed. */
export function mergeIntoSaveText(text, items) {
  let save;
  try {
    save = JSON.parse(text || "{}");
  } catch (err) {
    return null;
  }
  if (!save || typeof save !== "object") return null;
  if (!mergeBroadcast(save, items)) return null;
  return JSON.stringify(save);
}
