UPDATE (6 Nov): a lot less lag in the browser + admin gifts for Scout RNG
==========================================================================
1. FIREBASE RULES CHANGED AGAIN - publish them first:
   console.firebase.google.com > asmallworldcup-8f491 > Firestore Database > Rules
   delete everything, paste ALL of firestore.rules from this folder, Publish.
   (New: Scout RNG gifts are the admin's to write - players can't give themselves any.)
2. Copy everything in this folder into your repo folder (GitHub Desktop > Repository >
   Show in Explorer) and say Replace. It's only the changed files - nothing gets deleted.
   If desktop/game/openingpack.mp3 is still in the repo, delete it.
3. GitHub Desktop: summary "Optimising update + Scout RNG gifts", Commit to main, Push origin.
4. Site: Ctrl+Shift+R, the footer should say build 2026-11-06b. Press Play.

Admin: open a player in admin.html - the new Scout RNG box gives them players, fragments
and potions in the roll game. "Scout RNG gift to everyone" further down gives it to all.

Still laggy? play.html?fps=1 shows the frame rate - send me the number (home and match).
