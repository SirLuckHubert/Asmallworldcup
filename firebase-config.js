// ---------------------------------------------------------------------------
// aSmallWorldCup — Firebase project (already filled in).
//
// This is Hubi's project "asmallworldcup-8f491". The apiKey here is meant to be
// public: it only identifies the project. What actually protects the data is
// firestore.rules, so keep those published in the console.
//
// If the project is ever rebuilt, replace the block below with the values from
// Firebase console -> Project settings -> Your apps -> </> Web.
// ---------------------------------------------------------------------------

export const firebaseConfig = {
  apiKey: "AIzaSyA9TXxGL3ydbD_iLuUl5bHDCTous0VZJCk",
  authDomain: "asmallworldcup-8f491.firebaseapp.com",
  projectId: "asmallworldcup-8f491",
  storageBucket: "asmallworldcup-8f491.firebasestorage.app",
  messagingSenderId: "444768295058",
  appId: "1:444768295058:web:7bfad1676a0cc3cf8dae4b",
};

// The one account that can see everyone's saves, ban players and hand out cards.
// This is also written into firestore.rules - change it in BOTH places.
export const ADMIN_EMAIL = "24hbielak@stjosephsrush.com";

// Where the pygbag build lives, relative to this page (build_web.sh puts it here).
export const GAME_PATH = "game/index.html";
