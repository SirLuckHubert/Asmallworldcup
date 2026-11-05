A SMALL WORLD CUP - complete game + testing (1 Nov 2026)

    asmallworldcup/
      game/              THE WHOLE GAME - runs on its own
      testing/           the checks, kept apart (never needed to play)
      HOW_TO_UPLOAD.txt
      .gitignore

PLAY IT
  cd game
  py ragdoll_football.py          (Windows)     or     python3 ragdoll_football.py

  Needs Python 3 and pygame (pip install pygame). Nothing else.

WHAT'S IN game/
  ragdoll_football.py   the game, with everything up to today (PlayStyles, stats rework, slide,
                        World Cup ratings, drafts page, flag cards, Limit Breakers, progression,
                        new home screen, new World Cup screen, Champion Draft A,
                        classic physics, the club ladder, the profile + trophy cabinet,
                        THE GAUNTLET, PlayStyles you can see, play 30% faster again (1 Nov),
                        a ball that's always round, spins and dips,
                        QUESTS: 3 daily + 3 weekly, the daily chest, free packs,
                        Star Signings in three cards by tier (gold crystal / World Cup / club),
                        STAR SIGNINGS market: any player for Star Points, search, watchlist, release,
                        SIGNATURE ARCHIVE + tokens, the MARIO KEMPES (128) Game Box,
                        the new pack walkout (swipe to tear), Champion Drafts A/B/C and
                        Limit Breakers A/B rotating every 10 minutes, World's Game
                        evolutions, level 3 purple PlayStyles)
  openingpack.mp3       the pack-opening song (made by make_openingpack.py, on the walkout's beats)
  ARG.png ... SPA.png   the 12 World Cup flags
  sprites/              all 1,343 images: every World Cup and club player, badges, robots, card
                        templates and figures, packs, stadiums, menus, Star Signings, No. 10,
                        Limit Breakers, the World's Game, PlayStyle badges
  make_*.py, cards*.py, cardfig.py
                        the scripts that DRAW all of that - only needed to change the art:
                          make_sprites.py   players, kits, badges, robots
                          make_art.py       cards, packs, stadiums, menus, Star Signings, No. 10
                          make_flags.py     the 12 flags
                          make_limitbreakers.py, make_wc_flagcards.py, make_playstyle_icons.py,
                          make_wc_specials.py, make_card_figures.py (+ cards17/cards_lb/cards_wg)
                          make_sig_card.py  the Signature card (World Cup shape, emerald + gold)
                          make_signature.py Neymar Jr's autograph (smooth + pixel versions)
                          make_trophies.py  the trophy cabinet's 9 trophies (from the Canva
                                            art in art_src/trophies)
                          make_champ_cards.py  the Champion Draft A card in each club's colours,
                                            its pack, and the Ecuador / Ghana / DR Congo flags
                                            (players: cards_champ.py via make_card_figures.py)
                          make_pack_scene.py   the walkout's globe, close-up, bursts, stadium
                          make_wg_evo.py       the World's Game card at its four evolution stages
                          make_openingpack.py  writes openingpack.mp3 (needs ffmpeg for the mp3)
                          make_star_gold.py    the gold crystal Star Signing card (cards_star.py: their figures)
                          make_kempes.py       Kempes's autograph, Game Box, backdrop, match look (cards_sig.py: figure)

THE ONE THING NOT IN IT: your music and sounds
  The .mp3 / .ogg files (ballkick1, playingmusic1/2, menu1, cheering, shock...) are your own,
  so they aren't here. Copy them from your old folder into game/ and the game picks them up.
  Without them it still plays - it makes its own kick and whistle sounds - there's just no music.
  The exception: openingpack.mp3 IS here now, made for the new walkout (rip 0.30, flag 2.0,
  position 3.5, crest 5.0, card 7.0). If you copy this game over your old folder it replaces
  your own openingpack.mp3 - keep a copy of yours first if you want it back.

TESTING (testing/)
  pip install pillow
  cd testing
  python3 run_all.py
  Eighteen checks (the Signature Archive + Kempes, Star Signing cards, daily + weekly quests, the pack walkout on the song's beats, World's Game evolutions, stats + slide, PlayStyles, progression, Limit Breakers, a full CPU match,
  the team sheet + half-time sub offline and online, the home screen, Champion Draft A,
  classic physics - gravity, drag and bounce measured off the original game - the new
  World Cup screen, the club ladder: divisions, twists, objectives, the Champions Cup - and
  the profile tab with its trophy cabinet, and THE GAUNTLET: ten rungs, halves,
  twists, boosts, THE MACHINE).
  They play the real game from ../game with no window and never touch your save.
  On this exact folder: everything passed.
  Two measuring tools (not checks):
    python3 card_gap.py            each card's throw, throw wait and shot off the same run-up
    python3 playstyle_rates.py 120 how often every PlayStyle fires per minute of CPU play
    python3 machine_scout.py       THE MACHINE's scouting: what each strong card's stats do in
                                   each twist (shot, throw reach, throws a second). Re-run with
                                   --write after balance changes and it updates the game.
    (machine_sim.py is the experiment that showed CPU v CPU win rates can't rank cards - kept
     with its explanation, not needed)
