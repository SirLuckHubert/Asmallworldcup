# A Small World Cup (fan game) — web version

Everything needed to put the game on `https://<your-github-name>.github.io/<repo>/`:
Google sign-in, progress saved to each player's account, bans, and an admin console
that can read every save and hand out cards.

```
web/
  index.html          the site: hero, the game, features, screenshots, modes, how to play, patch notes
  style.css           the whole look (dark pitch UI, glass cards, motion)
  app.js              sign-in, cloud saves, ban checks, patch notes, fullscreen, scroll reveals
  admin.html/.js      admin console (locked to 24hbielak@stjosephsrush.com)
  firebase-config.js  <- the only file you have to edit
  firestore.rules     paste into Firebase so nobody can read anyone else's save
  bridge.js           lets the game inside the frame talk to the page (saves, online play, chat)
  play.html/.js       the game on its own page, full window, plus matchmaking and the ladder write
  net.js              matchmaking through Firestore, then a direct WebRTC link between the players
  ranks.js            the ranked ladder: rank points, six tiers, divisions, Top 10, badge drawing
  words.js            the language filter used on usernames and every chat message
  cards.json          card list for the admin's "give a card" box
  shots/*.png         the screenshots on the home page (regenerate whenever the game changes)
  bump_build.py       stamps a new build string on every file (run it before you upload)
  build_web.sh        builds the game into web/game/ with pygbag
  convert_audio.sh    turns the mp3s into the .ogg files the browser needs
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
python3 web/serve_local.py        # http://localhost:8000
```

**Don't use `python3 -m http.server` for the game.** On `localhost` pygbag flips into DEV MODE
and fetches the Python/pygame runtime from `http://localhost:8000/cdn/...` instead of the real
CDN. A plain web server has nothing there, so you get a grey canvas and
`ImportError: cannot import name 'Vector2' from 'pygame'` in the console. `serve_local.py` is a
normal static server that forwards those `/cdn/` requests to `pygame-web.github.io`, so what you
see locally is what the live site does. GitHub Pages never enters dev mode, so nothing extra is
needed there.

The page itself (`index.html`, sign-in, patch notes) is fine to preview with any server — it's only
the `game/` folder that needs pygbag's.

## 4. Publish

**Before you upload, stamp the build:**

```bash
python3 web/bump_build.py            # or: python3 web/bump_build.py 2026-10-01b
```

That bumps the `?v=` on the stylesheet, every script and every module they import, plus the
`--build` marker and the footer tag. Browsers (and GitHub's CDN) cache each of those files
separately, so without a fresh stamp you can end up running the new `app.js` against last week's
`ranks.js` — which is exactly how the half-styled page and the "nothing works" reports happen.

Commit everything and push, then **repo → Settings → Pages → Source: Deploy from a branch**,
branch `main`, folder `/web` (or move the contents of `web/` to the repo root and pick `/`).

## How saving works

* The game writes its save into the browser's `localStorage`, then calls `window.aswcSave(...)`.
* `bridge.js` passes that up to the page, which writes it to `players/<your uid>.save` in Firestore
  (debounced, so it isn't hammered).
* On sign-in the page pulls that save back down and puts it in `localStorage` **before** the game starts,
  so you carry on where you left off on any computer.
* Signed out, the game still works — progress just stays in that browser.

## Pages

| file | what it is |
| --- | --- |
| `index.html` | the site: hero, launch card, features, screenshots, modes, how to play, patch notes |
| `play.html` | the game on its own, filling the whole window (this is what Start the game opens) |
| `admin.html` | admin console: players, saves, bans, card grants, polls, patch notes |
| `check.html` | diagnostics for the live site |

## Usernames

Everyone picks one before they can play: 3-12 characters, letters, numbers, spaces, `- _ .` only.
It's claimed in a `usernames/<key>` document, so two people can't take the same name (and
"Hubi", "hubi" and "H u b i" all collapse to the same key). `words.js` checks it first — the same
filter chat uses. A name that trips the hate list is refused *and* quietly filed as a report.

## Ranked online

**RANKED ONLINE** on the game's Play menu (it only appears in the browser build — the desktop one
has no page to talk to).

* The page puts you in `queue/<uid>`, finds anyone else waiting, and the two browsers then swap one
  WebRTC offer/answer through `matches/<id>`. After that the match runs **peer to peer** on a data
  channel — Firestore only carries the handshake, so the rally speed is your connection, not a
  database round trip. If you both press Play in the same second you both start as hosts; the one
  with the lower id gives way and joins the other a few seconds later.
* The **host simulates the match** and sends 18 snapshots a second (both dolls, the ball, the score,
  the clock). The guest sends its throws and slides onto each snapshot instead of snapping to it.
* The guest's world is **mirrored**, so both players always see themselves on the left kicking right.
* Full time, both sides report the score and the page updates the ladder.

### Rank points and tiers

| tier | from | divisions |
| --- | --- | --- |
| Bronze | 0 | III · II · I |
| Silver | 300 | III · II · I |
| Gold | 700 | III · II · I |
| Platinum | 1200 | III · II · I |
| Diamond | 1800 | III · II · I |
| Elite | 2500 | — |
| **Top 10** | held by the ten highest on the ladder | — |

Win +28, draw +4, loss -18, plus 2 a goal (up to 5 goals) on a win or a draw, never below 0.
Everyone starts at 0 RP in Bronze III. **Top 10** is a badge, not a score: it only exists once ten
players are ranked and never goes to someone still in Bronze, so nobody wears it on an empty ladder.
The numbers live in `ranks.js` (`RP_WIN`, `RP_LOSS`, `RP_DRAW`, `RP_GOAL`, `TIERS`).

## Chat and reports

One chat, two places: the section on the site and the bottom-left corner of an online match (the
**CHAT** button opens six quick messages — typing a paragraph mid-rally was never going to work).
Every message goes through `words.js` **before** it is sent and the rules refuse anything from a
muted or banned account, so a modified page can't get round it either.

Every message on the site has a **⚑ report** button: pick a reason, and it lands in the admin's
Reports list with the message attached. Anything the filter flags as hate is reported automatically.

## Admin (24hbielak@stjosephsrush.com)

Sign in with that account and an **Admin console** button appears on the game page.

* **Players** — everyone who has signed in, with level, coins, card count and last seen.
* **Open** a player to see and edit their actual save file, give them any card
  (including **Pedro Neto 150**, which nothing else in the game can hand out), add coins or star points,
  or wipe their progress.
* **Ban / Unban** — a banned player is kicked out of the game straight away, can't sign back in
  and can't write to their save. The reason you type is what they see.
* **Mute / Unmute** — a muted player can still play, but can't post in chat. Enforced by the rules,
  and their own page tells them why nothing is sending.
* **Rename** — change someone's username (the old claim is released, the new one taken).
* **Rank points** — set a player's RP; the console shows the tier that lands them in.
* **Reports** — everything players have flagged, newest first, with the message, who reported it and
  who wrote it. Mark one done and it drops out of the list (tick **Show handled** to see them again).
  One click from a report takes you to that player's editor to mute or ban them.
* **Chat** — the last messages as they arrive, and you can delete any of them.
* **Patch notes** — whatever you post here shows under the game for everyone.
* **Poll** — ask a question with up to four answers and a reward (300 Star Points by default, or
  coins). It appears on the home page for everyone who is signed in; answering once pays the reward
  straight into their save and the console shows live results and who answered. **Close poll** takes
  the card away. Players can't answer twice — the rules only allow one vote document each.

The rules file enforces all of this on the server: a normal player can only read and write their
own save, can't change their own ban state, and can't see anyone else's data — even if they poke at
the page's code.

## Firestore collections

| path | who writes it |
| --- | --- |
| `players/<uid>` | the player (their own save, username, rank record) and the admin |
| `usernames/<key>` | claimed once by the player, released/renamed by the admin |
| `chat/<id>` | any signed-in player who isn't muted or banned; the admin can delete |
| `reports/<id>` | filed by players, readable **only** by the admin |
| `polls/<pollId>/votes/<uid>` | one answer per player, never editable |
| `queue/<uid>`, `matches/<id>` | throwaway matchmaking documents |
| `site/patchNotes`, `site/poll` | the admin only |

No composite indexes are needed — every query is a single field with a limit.
**Re-publish `firestore.rules` whenever you upload a new version of it**, or the new collections
stay locked and chat/ranked silently fail.

## Something looks wrong on the live site? Open /check.html

`check.html` reports what the browser actually sees: which build of `style.css` is live, whether
`app.js`, `firebase-config.js` and `cards.json` are there, whether the game build is where
`GAME_PATH` points, and whether `bridge.js` is hooked into the game page. It tells you what to fix.

Two things that have bitten this site:

* **Half-styled page** (yellow buttons, giant SVG icons, unstyled nav) = an **old `style.css`** is
  being served — the page is the new one, the stylesheet isn't. The stylesheet now carries a
  `--build` marker and the page shows a yellow warning bar when it doesn't match, so you'll know
  straight away. Hard refresh (Ctrl+Shift+R); if it persists, re-upload `style.css` and wait a
  minute for GitHub's CDN.
* **No game on the page.** You have to be signed in and press **Start the game** — the frame is only
  created then. If the build is missing you now get a message on the pitch saying which path failed
  instead of an empty box.

Keep the empty **`.nojekyll`** file at the repo root: it stops GitHub running the build through
Jekyll, which can skip files in the pygbag output.

## Playing on an iPad / phone

Touch is handled by the game itself: drag anywhere on the pitch to throw. Menus are all tap targets,
and a pause button sits next to the match clock so you never need an Esc key. The page's **Fullscreen**
button uses the real fullscreen API where it exists and falls back to a full-window CSS mode on iPad
Safari, which doesn't allow element fullscreen.

## If the browser build feels slow

The web build already draws at 640x360 (the game's own pixel resolution) instead of scaling a
1920x1080 frame, caches rotated sprites, text and translucent panels, and caps physics catch-up at
three steps a frame. If you still see stutter, close other tabs first - pygbag shares one CPU core
with everything else on the page.

## Progression

Coins were halved on 24 Sep: win 50, draw 25, loss 10, +2 a goal, level-ups pay 50 x level, freeplay
pays 5-50. Pack prices didn't change, so everything takes about twice as long to earn. The numbers
live at the top of `ragdoll_football.py` (`REWARD`, `REWARD_PER_GOAL`, `LEVEL_UP_COINS`, `FREE_REWARD`).

## Things worth knowing

* The admin email is in **two** places: `firebase-config.js` and `firestore.rules`. Change both.
* Free Firebase (Spark) is plenty here: a save is a few KB and each player writes one every couple of seconds at most.
* `cards.json` is generated from the game's card list. Regenerate it if you add cards.
* Online play needs **two people on the site at the same time** — there are no bots on the ladder.
  If nobody else is searching you get "nobody else is looking for a game right now" after a minute.
* The WebRTC link uses Google's free STUN servers and no TURN server, so two players both behind a
  strict/corporate NAT may fail to connect (the game says so and drops you back to the menu).
  If that ever becomes common, a TURN server is the fix — the ICE list is at the top of `net.js`.
* Ren Aoyagi is switched off in this build (`REN_IN_GAME = False` in the game file) — his card,
  art and abilities are still in there if you want him back.
