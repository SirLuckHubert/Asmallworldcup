// Player titles: the little name badge you wear on the ladder and in chat.
//
// Some unlock themselves from what the ladder already knows (matches played, rank,
// who is top of the board). The rest are handed out from the admin console.
// A player's document carries `titles` (what they own) and `title` (what they wear).

export const TITLES = [
  {
    id: "beta",
    name: "Beta Player",
    how: "Played during the beta",
    colour: "#6B7280", light: "#D1D5DB",
  },
  {
    id: "supporter",
    name: "Early Supporter",
    how: "Supported the game before full release",
    colour: "#3B82F6", light: "#93C5FD",
  },
  {
    id: "veteran",
    name: "World Cup Veteran",
    how: "Play 100 matches",
    colour: "#16A34A", light: "#BBF7D0",
    auto: (p) => played(p) >= 100,
    progress: (p) => [Math.min(played(p), 100), 100],
  },
  {
    id: "firstgen",
    name: "First Generation",
    how: "Create an account during Season 1",
    colour: "#7C3AED", light: "#C4B5FD",
  },
  {
    id: "founder",
    name: "Founding Player",
    how: "Play within the first week of release",
    colour: "#F59E0B", light: "#FDE68A",
  },
  {
    id: "elite",
    name: "Elite Player",
    how: "Reach a high leaderboard rank",
    colour: "#EF4444", light: "#FCA5A5",
    auto: (p) => (Number(p.rp) || 0) >= 1200,          // Platinum and above
    progress: (p) => [Math.min(Number(p.rp) || 0, 1200), 1200],
  },
  {
    id: "king",
    name: "Leaderboard King",
    how: "Finish #1 on the leaderboard",
    colour: "#EAB308", light: "#FEF08A",
    auto: (p) => p.place === 1 && (Number(p.rp) || 0) > 0,
  },
  {
    id: "champion",
    name: "World Champion",
    how: "Win a tournament",
    colour: "#06B6D4", light: "#A5F3FC",
  },
  {
    id: "legend",
    name: "Legendary Player",
    how: "Given for something special",
    colour: "#F97316", light: "#FDBA74",
  },
  {
    id: "immortal",
    name: "Immortal",
    how: "The rarest one there is",
    colour: "#A855F7", light: "#F0ABFC",
    glow: true,
  },
  {
    id: "messi",
    name: "Messi",
    how: "Given by the admin — for the ones who play like him",
    colour: "#38BDF8", light: "#BAE6FD",
    glow: true,
  },
  {
    id: "ronaldo",
    name: "Ronaldo",
    how: "Given by the admin — for the ones who finish like him",
    colour: "#DC2626", light: "#FECACA",
    glow: true,
  },
];

export const TITLE_BY_ID = Object.fromEntries(TITLES.map((t) => [t.id, t]));

/** Matches played, from the ladder record. */
export function played(p) {
  return (Number(p.wins) || 0) + (Number(p.losses) || 0) + (Number(p.draws) || 0);
}

/**
 * Everything this player should own: what the admin gave them, plus whatever they
 * have earned. `player` needs wins/losses/draws/rp, and `place` (1-based) if known.
 */
export function ownedTitles(player) {
  const p = player || {};
  const given = Array.isArray(p.titles) ? p.titles.filter((id) => TITLE_BY_ID[id]) : [];
  const earned = TITLES.filter((t) => t.auto && t.auto(p)).map((t) => t.id);
  return TITLES.filter((t) => given.includes(t.id) || earned.includes(t.id)).map((t) => t.id);
}

/** The ones a player has earned but doesn't have written down yet. */
export function newlyEarned(player) {
  const have = Array.isArray(player.titles) ? player.titles : [];
  return TITLES.filter((t) => t.auto && t.auto(player) && !have.includes(t.id)).map((t) => t.id);
}

/** The title they are wearing, if they still own it. */
export function wornTitle(player) {
  const p = player || {};
  if (!p.title) return null;
  return ownedTitles(p).includes(p.title) ? TITLE_BY_ID[p.title] : null;
}

/** The badge itself, as an element (used on the ladder, in chat and on the card). */
export function titleChip(title, { small = false } = {}) {
  const span = document.createElement("span");
  span.className = "title-chip" + (small ? " sm" : "") + (title.glow ? " glow" : "");
  span.textContent = title.name;
  span.style.setProperty("--tc", title.colour);
  span.style.setProperty("--tl", title.light);
  return span;
}

/** Same thing as a string, for places that build HTML. */
export function titleChipHtml(title, { small = false } = {}) {
  const cls = "title-chip" + (small ? " sm" : "") + (title.glow ? " glow" : "");
  const safe = String(title.name).replace(/[<>&]/g, "");
  return `<span class="${cls}" style="--tc:${title.colour};--tl:${title.light}">${safe}</span>`;
}
