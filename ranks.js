// Ranked ladder: rank points, tiers and badges.
//
// Six tiers with three divisions each (III is the lowest, I the highest), then Elite with no
// divisions, and TOP 10 — held only by whoever is in the top ten of the leaderboard right now.

export const TIERS = [
  { key: "bronze",   name: "Bronze",   at: 0,    colour: "#c47b3f", glow: "#ffb066", divisions: 3 },
  { key: "silver",   name: "Silver",   at: 300,  colour: "#b9c4cc", glow: "#e8f2f7", divisions: 3 },
  { key: "gold",     name: "Gold",     at: 700,  colour: "#e8b62c", glow: "#ffe27a", divisions: 3 },
  { key: "platinum", name: "Platinum", at: 1200, colour: "#49c9c0", glow: "#9bfff6", divisions: 3 },
  { key: "diamond",  name: "Diamond",  at: 1800, colour: "#5aa9ff", glow: "#b6dbff", divisions: 3 },
  { key: "elite",    name: "Elite",    at: 2500, colour: "#a06bff", glow: "#dcc4ff", divisions: 1 },
];

export const TOP10 = { key: "top10", name: "Top 10", colour: "#ffd23f", glow: "#fff2b8" };

// Top 10 is a badge you take off someone, so it only exists on a ladder with ten ranked
// players on it, and Bronze players never wear it however empty the ladder is.
export const TOP10_MIN = 10;
export const TOP10_RP = 300;

/** Does this player hold the Top 10 badge? place is their 0-based row on the ladder. */
export function holdsTop10(place, rp, ladderSize) {
  return ladderSize >= TOP10_MIN && place >= 0 && place < TOP10_MIN
    && (Number(rp) || 0) >= TOP10_RP;
}

export const START_RP = 0;            // everyone opens at the bottom of Bronze III
export const RP_WIN = 28;
export const RP_LOSS = -18;
export const RP_DRAW = 4;
export const RP_GOAL = 2;             // per goal scored, win or lose
export const RP_FLOOR = 0;

/** Where a rank-point total sits: tier, division and progress to the next step. */
export function rankOf(rp, topTen = false) {
  const points = Math.max(0, Math.round(Number(rp) || 0));
  if (topTen) {
    return { ...TOP10, rp: points, label: "Top 10", division: 0, next: null, progress: 1 };
  }
  let tier = TIERS[0], idx = 0;
  TIERS.forEach((t, i) => { if (points >= t.at) { tier = t; idx = i; } });
  const ceiling = TIERS[idx + 1] ? TIERS[idx + 1].at : tier.at + 900;
  const span = ceiling - tier.at;
  const into = points - tier.at;

  let division = 0, label = tier.name, nextAt = ceiling;
  if (tier.divisions > 1) {
    const step = span / tier.divisions;
    const d = Math.min(tier.divisions - 1, Math.floor(into / step));
    division = tier.divisions - d;                 // III -> II -> I
    label = tier.name + " " + "I".repeat(division);
    nextAt = Math.round(tier.at + (d + 1) * step);
  }
  return {
    key: tier.key, name: tier.name, colour: tier.colour, glow: tier.glow,
    rp: points, division, label,
    next: nextAt, progress: Math.max(0, Math.min(1, (points - (nextAt - (span / tier.divisions))) / (span / tier.divisions))),
  };
}

export function rpAfter(rp, result, goalsFor = 0) {
  const base = result === "win" ? RP_WIN : result === "draw" ? RP_DRAW : RP_LOSS;
  const gained = base + (result === "loss" ? 0 : RP_GOAL * Math.min(5, goalsFor));
  return Math.max(RP_FLOOR, Math.round((Number(rp) || 0) + gained));
}

/** The badge as an inline SVG string — a shield with the tier's divisions marked. */
export function badgeSvg(rank, size = 48) {
  const { colour, glow, division, key } = rank;
  const pips = [];
  for (let i = 0; i < division; i++) {
    pips.push(`<rect x="${13 + i * 7}" y="40" width="4" height="6" rx="1" fill="${glow}"/>`);
  }
  const crown = (key === "top10" || key === "elite")
    ? `<path d="M12 15l5 5 7-9 7 9 5-5v8H12z" fill="${glow}" opacity=".95"/>`
    : "";
  const star = key === "top10"
    ? `<path d="M24 22l2.6 5.4 5.9.8-4.3 4.1 1 5.9-5.2-2.8-5.2 2.8 1-5.9-4.3-4.1 5.9-.8z" fill="#2a1c00"/>`
    : `<path d="M24 20l3 6 6-6-2 12H17l-2-12 6 6z" fill="#0d1710" opacity=".55"/>`;
  return `<svg viewBox="0 0 48 52" width="${size}" height="${size * 52 / 48}" aria-hidden="true">
    <defs><linearGradient id="g${key}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="${glow}"/><stop offset="1" stop-color="${colour}"/>
    </linearGradient></defs>
    <path d="M24 2l18 6v18c0 11-8 19-18 24C14 45 6 37 6 26V8z" fill="url(#g${key})" stroke="#07120b" stroke-width="2"/>
    <path d="M24 7l13 4.4V26c0 8.4-5.9 14.9-13 19-7.1-4.1-13-10.6-13-19V11.4z" fill="#0a1a10" opacity=".35"/>
    ${crown}${star}${pips.join("")}
  </svg>`;
}

/** Small helper for lists: "Gold II · 812 RP" */
export function rankLine(rank) {
  return rank.label + " · " + rank.rp + " RP";
}
