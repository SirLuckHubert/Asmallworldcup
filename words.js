// Language filter for usernames and chat.
//
// It normalises first (lower-case, strip accents, undo leet-speak, collapse repeats and
// separators) so "n1gg3r", "f.u.c.k" and "shiiiit" are all caught, then checks the text
// against three lists: slurs and hate terms (hard block, reported to the admin), strong
// profanity, and milder insults. Nothing here is shown to players — they just get
// "pick something else".

const LEET = {
  "0": "o", "1": "i", "!": "i", "|": "i", "3": "e", "4": "a", "@": "a", "5": "s", "$": "s",
  "7": "t", "+": "t", "8": "b", "9": "g", "6": "g", "2": "z", "£": "l", "€": "e",
};

// separators people hide words behind
const STRIP = /[\s._\-*'"`~^()[\]{}<>\/\\,;:?!#%&=]+/g;

export function normalise(text) {
  let s = String(text || "").toLowerCase();
  s = s.normalize("NFKD").replace(/[̀-ͯ]/g, "");     // accents
  s = s.replace(/[​-‏⁠﻿]/g, "");           // zero-width tricks
  s = s.split("").map((c) => LEET[c] || c).join("");
  s = s.replace(STRIP, "");
  s = s.replace(/(.)\1{2,}/g, "$1$1");                         // shiiiit -> shiit
  return s;
}

// a second, harsher pass: every run of a repeated letter becomes one ("shiiit" -> "shit").
// Only used for words of 4+ letters, or it would fire on everyday text.
export function squash(text) {
  return normalise(text).replace(/(.)\1+/g, "$1");
}

// ---- slurs and hate terms: always blocked, and the admin is told
const HATE = [
  "nigger", "nigga", "niger", "niger", "negro", "coon", "jigaboo", "porchmonkey",
  "chink", "ching chong", "gook", "jap", "nip", "slant eye", "zipperhead",
  "paki", "curry muncher", "towelhead", "raghead", "sandnigger", "camel jockey",
  "spic", "wetback", "beaner", "greaser",
  "kike", "yid", "heeb", "zionazi", "jewrat", "gasthejews", "hitlerdidnothingwrong",
  "heilhitler", "seigheil", "whitepower", "kkk", "lynch",
  "faggot", "fagot", "fag", "dyke", "tranny", "shemale", "trannie", "homo",
  "retard", "retarded", "spastic", "mongoloid", "cripple",
  "gypsy", "gyppo", "pikey", "abo", "wog", "darkie", "half caste",
  "rapist", "pedophile", "paedophile", "pedo", "nonce", "molester",
  "killyourself", "kysbro", "kys", "neckyourself", "hangyourself",
  "terrorist", "isis", "nazi", "genocide",
];

// ---- strong profanity: blocked in usernames and chat
const STRONG = [
  "fuck", "fucking", "fucker", "motherfucker", "fk", "fuk", "phuck",
  "shit", "bullshit", "shite", "cunt", "twat", "wanker", "wank", "bollocks",
  "bastard", "bitch", "whore", "slut", "hoe", "prick", "dick", "cock", "penis",
  "vagina", "pussy", "boobs", "tits", "titties", "arse", "ass", "asshole", "arsehole",
  "porn", "porno", "xxx", "hentai", "nsfw", "sex", "sexy", "orgasm", "cum", "jizz",
  "masturbate", "blowjob", "handjob", "anal", "rape", "rapey", "horny", "milf",
  "nude", "nudes", "onlyfans", "erection", "testicle", "scrotum", "cumshot",
];

// ---- milder stuff: blocked in usernames, and in chat too (school audience)
const MILD = [
  "crap", "damn", "piss", "pissed", "bugger", "bloody hell", "git", "moron", "idiot",
  "stupid", "loser", "ugly", "fatty", "smelly", "dumbass", "dumbarse", "jackass",
  "suckmy", "shutup", "trash", "garbage human", "noob", "skid", "cheater", "hacker",
  "drugs", "cocaine", "weed", "meth", "heroin", "vape", "alcohol", "beer", "vodka",
];

// impersonation and other names nobody should take
const RESERVED = [
  "admin", "administrator", "mod", "moderator", "staff", "owner", "official",
  "aswc", "asmallworldcup", "system", "server", "support", "help", "null", "undefined",
  "hubi", "sirluckhubert", "everyone", "here", "you", "me",
];

const ALL = [
  ...HATE.map((w) => ({ word: normalise(w), level: "hate" })),
  ...STRONG.map((w) => ({ word: normalise(w), level: "strong" })),
  ...MILD.map((w) => ({ word: normalise(w), level: "mild" })),
];

// words that legitimately contain a blocked word as a substring
const SAFE_WORDS = [
  "assist", "assassin", "class", "classic", "glass", "pass", "passing", "grass", "bass",
  "massive", "mass", "compass", "embassy", "assess", "brass", "cassette", "assembly",
  "hoefer", "shoe", "shoes", "cocktail", "peacock", "hancock", "scunthorpe", "penistone",
  "analyse", "analysis", "analytics", "canal", "banal", "titan", "constitution", "dickens",
  "sextet", "essex", "sussex", "middlesex", "cumbria", "cumberland", "documents", "circumstance",
  "accumulate", "scumbag", "specialist", "therapist", "grapes", "arsenal", "assassins",
].map(normalise);

/**
 * Check a username or message.
 * @returns {{ok: boolean, level?: "hate"|"strong"|"mild"|"reserved"|"format", why?: string}}
 */
export function checkText(raw, { username = false } = {}) {
  const text = String(raw || "");
  if (!text.trim()) return { ok: false, level: "format", why: "Type something first." };

  if (username) {
    if (text.length > 12) return { ok: false, level: "format", why: "12 characters max." };
    if (text.length < 3) return { ok: false, level: "format", why: "At least 3 characters." };
    if (!/^[A-Za-z0-9 _.-]+$/.test(text)) {
      return { ok: false, level: "format", why: "Letters, numbers, spaces, - _ . only." };
    }
  } else if (text.length > 200) {
    return { ok: false, level: "format", why: "That's too long for one message." };
  }

  const flat = normalise(text);
  const tight = squash(text);
  if (!flat) return { ok: false, level: "format", why: "Type something first." };

  if (username && RESERVED.map(normalise).includes(flat)) {
    return { ok: false, level: "reserved", why: "That name is taken by the game." };
  }

  // a word only counts if it isn't sitting inside an innocent word
  const hit = (hay, safeList, minLen) => {
    for (const { word, level } of ALL) {
      if (!word || word.length < minLen) continue;
      let from = 0;
      while (true) {
        const at = hay.indexOf(word, from);
        if (at === -1) break;
        const covered = safeList.some((safe) => {
          let s = 0;
          while (true) {
            const sa = hay.indexOf(safe, s);
            if (sa === -1) return false;
            if (sa <= at && sa + safe.length >= at + word.length) return true;
            s = sa + 1;
          }
        });
        if (!covered) return level;
        from = at + 1;
      }
    }
    return null;
  };

  const level = hit(flat, SAFE_WORDS, 3)
    || hit(tight, SAFE_WORDS.map((w) => w.replace(/(.)\1+/g, "$1")), 4);
  if (level) {
    return {
      ok: false,
      level,
      why: level === "hate"
        ? "That's not going in this game. Repeat it and you're banned."
        : "Keep it clean — pick something else.",
    };
  }
  return { ok: true };
}

export function tidyUsername(raw) {
  return String(raw || "").replace(/\s+/g, " ").trim().slice(0, 12);
}

// a stable key so "Hubi", "hubi" and "H u b i" can't all exist at once
export function usernameKey(name) {
  return normalise(name).slice(0, 24) || "_";
}
