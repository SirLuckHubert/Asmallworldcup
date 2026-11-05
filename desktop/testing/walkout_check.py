"""THE WALKOUT (31 Oct): the new pack opening, on the beats of Hubi's pack song.

    python3 walkout_check.py      (pictures: out/wk_*.png)

Plays openings through the game's own loop (real frames, real clicks) and times when each scene
first appears: the pack opening, the globe, the FLAG at 2.0 s, the POSITION at 3.5 s, the CREST
at 5.0 s, the stadium, the card at 7.0 s. Then skip, continue, 10x, the old sprites fallback."""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Run, rf, pygame

fails = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


random.seed(3)
r = Run(save={"coins": 10 ** 7, "xp": 2400, "tutorial_done": True, "starter_opened": True}, name="save_wk.json")
g = r.g
r.frames(10)
import time as _time                                  # Draft A in the store (the drafts rotate)
g.draft_offset = (int(_time.time() // 3600) + 1) * 3600 + 5 - _time.time()   # (on the hour: every group at A)
check(g.active_draft() == 1, "Draft A is in the store for these checks")
check(g.wk_ok(), "the walkout's pictures are all in sprites/")

# ---- record when each scene first draws
first = {}
WATCH = ("wk_pack_opens", "wk_blit_globe", "wk_rings", "wk_chevrons", "wk_streamers",
         "wk_stadium", "blit_card")


def watch():
    for name in WATCH:
        real = getattr(type(g), name)

        def wrap(*a, _real=real, _name=name, **k):
            pr = g.pack_reveal
            if pr and pr.get("opened") and _name not in first:
                first[_name] = pr["t"]
            return _real(g, *a, **k)
        setattr(g, name, wrap)


watch()
tells = []
_timed_opens = g.wk_pack_opens                            # (the scene timer above, kept underneath)


def _opens(w, pr, t, art, cx, cy, theme, tell, end):
    if t >= g.WK_TEAR_AT:
        tells.append(tell)
    return _timed_opens(w, pr, t, art, cx, cy, theme, tell, end)


g.wk_pack_opens = _opens


def opening(cid, tier, secs, shots=()):
    first.clear()
    g.pack_reveal = {"card": g.cards[cid], "tier": tier, "count": 1, "pack": 1, "t": 0.0, "opened": False}
    g.state = rf.PACK_OPEN
    r.frames(3, dt=1 / 30.0, draw=True)
    r.click(960, 540)                                    # (a fresh screen ignores clicks for a moment)
    check(g.pack_reveal["opened"], "%s (%s): a tap opens it" % (cid, tier))
    todo = sorted(shots)
    n = int(secs * 30)
    for _ in range(n):
        r.frames(1, dt=1 / 30.0, draw=True)
        while todo and g.pack_reveal["t"] >= todo[0]:
            r.shot("wk_%s_%s_%.1f" % (cid, tier, todo.pop(0)), half=False)
    return dict(first)


def near(t, beat, slack=0.12):
    return t is not None and beat - 0.01 <= t <= beat + slack


F, P, C = rf.PACK_BEATS
LAND = rf.PACK_CARD_AT
# ---- pool A, on the song's beats
f = opening("INT_messi", "A", 9.5, shots=(0.5, 2.4, 4.0, 5.4, 6.8, 9.0))
check(near(f.get("wk_pack_opens"), 0.0, 0.1), "the pack opens first (%.2f)" % f.get("wk_pack_opens", -1))
check(near(f.get("wk_blit_globe"), g.WK_OPEN_END, 0.1), "the globe comes out of the light (%.2f)" % f.get("wk_blit_globe", -1))
check(near(f.get("wk_rings"), F), "the FLAG lands on the beat: %.2f s (song %.1f)" % (f.get("wk_rings", -1), F))
check(near(f.get("wk_chevrons"), P), "the POSITION on the beat: %.2f s (song %.1f)" % (f.get("wk_chevrons", -1), P))
check(near(f.get("wk_streamers"), C), "the CREST on the beat: %.2f s (song %.1f)" % (f.get("wk_streamers", -1), C))
check(near(f.get("wk_stadium"), g.WK_DARK), "into the stadium (%.2f)" % f.get("wk_stadium", -1))
check(near(f.get("blit_card"), LAND), "the card walks out on the beat: %.2f s (song %.1f)" % (f.get("blit_card", -1), LAND))
pr = g.pack_reveal
check(pr.get("wk_landed") and len(pr.get("wk_parts", [])) > 20, "pyro and confetti when he lands")
r.frames(30 * 20, dt=1 / 30.0, draw=True)                    # twenty seconds of the stadium
check(len(g.pack_reveal.get("wk_parts", [])) <= 700, "the confetti never piles up (%d)" % len(g.pack_reveal["wk_parts"]))
check(g.pack_reveal.get("wk_pyro_n", 0) >= 6, "pool A: pyro every 3 seconds (%d)" % g.pack_reveal.get("wk_pyro_n", 0))
# ---- themes
check(g.wk_theme(g.cards["INT_messi"], "A") == "A" and g.wk_theme(g.cards["CHE_palmer"], "B") == "B"
      and g.wk_theme(g.cards["LB_salah"], "A") == "L" and g.wk_theme(g.cards["BAR_pedri"], "C") == "C",
      "purple for pool A, blue for B, crimson for Limit Breakers, slate for C")
f = opening("LB_salah", "A", 7.5, shots=(2.4, 7.4))
check(near(f.get("blit_card"), LAND), "a Limit Breaker walks out too")
f = opening("CHE_palmer", "B", 7.6, shots=(2.4, 7.5))
check(near(f.get("wk_rings"), F) and near(f.get("blit_card"), LAND), "pool B: the same story")
# ---- pool C: it rips too (white light), then straight to the stadium - no cutscene
f = opening("BAR_pedri", "C", 1.6, shots=(0.4, 1.5))
check(near(f.get("wk_pack_opens"), 0.0, 0.1) and "wk_blit_globe" not in f and near(f.get("wk_stadium"), g.WK_C_OPEN),
      "pool C: the rip, then the stadium at %.2f s" % f.get("wk_stadium", -1))
check(near(f.get("blit_card"), g.opening_done_at("C"), 0.1), "pool C: the card at %.2f s" % f.get("blit_card", -1))
# ---- THE TELL (31 Oct): the light out of the rip says the pool - and never lies
for cid, tier in (("BAR_pedri", "C"), ("CHE_palmer", "B"), ("INT_messi", "A"), ("LB_salah", "A")):
    tells[:] = []
    opening(cid, tier, 0.8)
    want = rf.LB_RED if cid.startswith("LB_") else g.WK_TELL[tier]
    check(tells and all(tc == want for tc in tells), "%s (%s): the light is %s, all the way" % (cid, tier, want))
check(not hasattr(g, "wk_chain") and not hasattr(g, "wk_crack_overlay"), "no fake-outs (Hubi: removed)")
# ---- SWIPE TO TEAR (31 Oct)
g.pack_reveal = {"card": g.cards["INT_messi"], "tier": "A", "count": 1, "pack": 1, "t": 0.0, "opened": False}
g.state = rf.PACK_OPEN
r.frames(15, dt=1 / 30.0, draw=True)
rect = g.pack_reveal["wk_rect"]
seam_y = rect.y + g.wk_pack_pieces(g.pack_reveal, None, "A")[3]


def ev(kind, x, y, **k):
    pygame.event.post(pygame.event.Event(kind, pos=(int(x), int(y)), **k))


ev(pygame.MOUSEBUTTONDOWN, rect.x + 20, seam_y, button=1)
for x in range(rect.x + 20, rect.x + int(rect.w * 0.45), 20):     # half way, then let go
    ev(pygame.MOUSEMOTION, x, seam_y)
ev(pygame.MOUSEBUTTONUP, rect.x + int(rect.w * 0.45), seam_y, button=1)
r.frames(3, dt=1 / 30.0, draw=True)
r.shot("wk_swipe_half", half=False)
sw = g.pack_reveal.get("swipe")
check(not g.pack_reveal["opened"] and sw and sw["hi"] - sw["lo"] > rect.w * 0.35,
      "half a swipe: torn half way, still sealed")
ev(pygame.MOUSEBUTTONDOWN, rect.x + int(rect.w * 0.45), seam_y, button=1)
for x in range(rect.x + int(rect.w * 0.45), rect.right - 10, 20):
    ev(pygame.MOUSEMOTION, x, seam_y)
r.frames(2, dt=1 / 30.0, draw=True)
pr = g.pack_reveal
check(pr["opened"] and pr.get("wk_swiped") and g.WK_TEAR_AT <= pr["t"] < g.WK_TEAR_AT + 0.2,
      "the rest of the swipe: it RIPS (%.2f s - the rip, on the song)" % pr["t"])
ev(pygame.MOUSEBUTTONUP, rect.right - 10, seam_y, button=1)
r.frames(8, dt=1 / 30.0, draw=True)
r.shot("wk_swipe_rip", half=False)
f0 = {}
for _ in range(int(7.2 * 30)):
    r.frames(1, dt=1 / 30.0, draw=True)
    if g.pack_reveal.get("wk_landed") and "land" not in f0:
        f0["land"] = g.pack_reveal["t"]
check(near(f0.get("land"), LAND), "a swiped pack still walks out on the beat (%.2f)" % f0.get("land", -1))
# ---- skip, then continue
f = opening("INT_messi", "A", 2.5)
r.click(960, 540, settle=0)
r.frames(2, dt=1 / 30.0, draw=True)
check(g.pack_reveal["t"] >= LAND and g.pack_reveal.get("wk_landed"), "a click skips to the card")
r.frames(20, dt=1 / 30.0, draw=True)
r.shot("wk_skipped", half=False)
r.click(960, 540, settle=0)
r.frames(40, dt=1 / 30.0, draw=True)
check(g.state != rf.PACK_OPEN, "then a click carries on (%s)" % g.state)
# ---- a real pack, and a real 10x
g.state = rf.TITLE
coins = g.save["coins"]
check(g.buy_pack(1) and g.state == rf.PACK_OPEN and not g.pack_reveal["opened"], "buying a pack: it waits for a tap")
r.frames(5, dt=1 / 30.0, draw=True)
r.shot("wk_idle", half=False)
r.click(960, 540)
r.click(960, 540, settle=3)
r.frames(20, dt=1 / 30.0, draw=True)
r.click(960, 540, settle=0)
r.frames(40, dt=1 / 30.0, draw=True)
check(g.state != rf.PACK_OPEN and g.save["coins"] < coins, "bought, opened, skipped, carried on")
g.state = rf.TITLE
g.buy_pack10(1)
check(g.state == rf.PACK_OPEN and g.pack_reveal.get("multi"), "10x: the best card walks out first")
r.click(960, 540)
r.click(960, 540, settle=3)
r.frames(20, dt=1 / 30.0, draw=True)
r.click(960, 540, settle=0)
r.frames(40, dt=1 / 30.0, draw=True)
check(g.state != rf.PACK_OPEN, "...then on to all ten (%s)" % g.state)
# ---- an old sprites folder: the old opening still works
g._wk_ok = False
g.pack_reveal = {"card": g.cards["INT_messi"], "tier": "A", "count": 1, "pack": 1, "t": 0.0, "opened": True}
g.state = rf.PACK_OPEN
try:
    r.frames(60, dt=1 / 30.0, draw=True)
    ok = True
except Exception as e:
    ok = False
    print(e)
check(ok, "without the walkout's pictures: the old opening")
g._wk_ok = None
print("%d failed %s" % (len(fails), fails))
sys.exit(1 if fails else 0)
