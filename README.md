# A Small World Cup (fan game) — web version

Everything needed to put the game on `https://<your-github-name>.github.io/<repo>/`:
Google sign-in, progress saved to each player's account, bans, and an admin console
that can read every save and hand out cards.

```
web/
  index.html          the page players see: sign-in, the game, patch notes
  app.js              sign-in, cloud saves, ban checks, patch notes
  admin.html/.js      admin console (locked to 24hbielak@stjosephsrush.com)
  firebase-config.js  <- the only file you have to edit
  firestore.rules     paste into Firebase so nobody can read anyone else's save
  bridge.js           lets the game inside the frame talk to the page
  cards.json          card list for the admin's "give a card" box
  style.css
  build_web.sh        builds the game into web/game/ with pygbag
  game/               (created by build_web.sh - the actual browser build)
```

---

## 1. Firebase (5 minutes, free)

1. <https://console.firebase.google.com> → **Add project** (Analytics not needed).
2. **Build → Authentication → Get started → Google → Enable**, pick a support email, Save.
   Then **Settings → Authorised domains → Add domain** → `<your-github-name>.github.io`
   (and `localhost` while you're testing).
3. **Build → Firestore Database → Create database → Production mode**.
   Open the **Rules** tab, paste everything from `firestore.rules`, **Publish**.
4. Gear icon → **Project settings → Your apps → `</>` (Web)** → register an app.
   Copy the `firebaseConfig` values into **`firebase-config.js`**.

That's the only file with your details in it. The API key there is public by design —
the rules file is what actually protects the data.

## 2. Convert the audio to .ogg

Browsers don't reliably decode the mp3s. Next to the game:

```bash
for f in *.mp3; do ffmpeg -i "$f" -c:a libvorbis -q:a 4 "${f%.mp3}.ogg"; done
```

The game prefers `.ogg` over `.mp3` everywhere now, so the desktop version picks them up too
and you can delete the mp3s if you want a smaller download.

## 3. Build the game for the browser

```bash
pip install pygbag
bash web/build_web.sh
```

That copies `ragdoll_football.py` to `main.py`, bundles the sprites and `.ogg` files,
runs pygbag, drops the result in `web/game/` and hooks `bridge.js` into it.

Test it before pushing:

```bash
python3 -m http.server -d web 8000     # http://localhost:8000
```

## 4. Publish

Commit everything and push, then **repo → Settings → Pages → Source: Deploy from a branch**,
branch `main`, folder `/web` (or move the contents of `web/` to the repo root and pick `/`).

## How saving works

* The game writes its save into the browser's `localStorage`, then calls `window.aswcSave(...)`.
* `bridge.js` passes that up to the page, which writes it to `players/<your uid>.save` in Firestore
  (debounced, so it isn't hammered).
* On sign-in the page pulls that save back down and puts it in `localStorage` **before** the game starts,
  so you carry on where you left off on any computer.
* Signed out, the game still works — progress just stays in that browser.

## Admin (24hbielak@stjosephsrush.com)

Sign in with that account and an **Admin console** button appears on the game page.

* **Players** — everyone who has signed in, with level, coins, card count and last seen.
* **Open** a player to see and edit their actual save file, give them any card
  (including **Pedro Neto 150**, which nothing else in the game can hand out), add coins or star points,
  or wipe their progress.
* **Ban / Unban** — a banned player is kicked out of the game straight away, can't sign back in
  and can't write to their save. The reason you type is what they see.
* **Patch notes** — whatever you post here shows under the game for everyone.

The rules file enforces all of this on the server: a normal player can only read and write their
own save, can't change their own ban state, and can't see anyone else's data — even if they poke at
the page's code.

## Things worth knowing

* The admin email is in **two** places: `firebase-config.js` and `firestore.rules`. Change both.
* Free Firebase (Spark) is plenty here: a save is a few KB and each player writes one every couple of seconds at most.
* `cards.json` is generated from the game's card list. Regenerate it if you add cards.
* Ren Aoyagi is switched off in this build (`REN_IN_GAME = False` in the game file) — his card,
  art and abilities are still in there if you want him back.
