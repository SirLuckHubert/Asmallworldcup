"""THE BROWSER'S OWN CODE PATHS (5 Nov): the game believes it is in the browser here.

    python3 web_paths_check.py

The browser build draws some screens differently to stay smooth - still pages (Star Signings and
the pack store painted once and copied), cut-down glass panels, still flags, lighter confetti.
None of that runs in the other checks (they are the desktop game). This makes sure it looks the
same as painting the normal way, follows the mouse and the save, and never crashes."""
import os
import random
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class LS:
    def __init__(self): self.d = {}
    def getItem(self, k): return self.d.get(k)
    def setItem(self, k, v): self.d[k] = v


class Win:
    localStorage = LS()
    def aswcSave(self, t): pass


fake = types.ModuleType("platform")
fake.window = Win()
sys.modules["platform"] = fake
_real = sys.platform
sys.platform = "emscripten"
from harness import Run, rf, pygame
sys.platform = _real

fails = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


check(rf.WEB_BUILD, "the game thinks it is in the browser")
random.seed(3)
r = Run(save={"coins": 10 ** 6, "xp": 2400, "tutorial_done": True, "starter_opened": True, "star_points": 500000},
        name="save_web.json")
g = r.g
for cid in list(g.cards)[:60]:
    g.save["owned"][cid] = 1
g.tut = None
g.save["coins"] = 10 ** 6
was = (g.state, g.menu_page)
# the loading screen's warm-up, as boot() runs it
for fn in (lambda: g.draw_store(g.world), lambda: g.draw_packs(g.world), g.warm_flags,
           lambda: (g.warm_stars_cards(), g.draw_stars(g.world)), g.warm_walkout, g.warm_menus):
    fn()
check((g.state, g.menu_page) == was and not g.toasts, "warming the menus leaves you where you were, no toasts")


def frame():
    random.seed(1)
    g.draw()
    return g.world.im.convert("RGB").tobytes()


def same_as_normal(name, setup, hover=(5, 5)):
    setup()
    r.hover(*hover)
    r.frames(3, draw=True)
    real = rf.Game.still_page
    rf.Game.still_page = lambda self, w, key, paint, moving=None: paint(w)
    a = frame()
    rf.Game.still_page = real
    g._still_page = None
    frame()
    b = frame()
    off = sum(1 for x, y in zip(a, b) if abs(x - y) > 24) // 3
    check(off < 1500, "%s: the kept page looks like the painted one (%d pixels differ)" % (name, off))


same_as_normal("Star Signings", lambda: g.open_stars("players"))
same_as_normal("Star Signings, mouse on a card", lambda: g.open_stars("players"), hover=(640, 400))
same_as_normal("the pack store", lambda: g.open_packs())

# it follows the mouse and the save
g.open_stars("players")
r.hover(5, 5)
r.frames(2, draw=True)
k1 = g._still_page[0]
r.hover(640, 400)
r.frames(1, draw=True)
check(g._still_page[0] != k1, "moving onto a card repaints the page (its hover)")
k2 = g._still_page[0]
r.frames(3, draw=True)
check(g._still_page[0] == k2, "...and a still mouse doesn't")
g.save["watchlist"] = list(g.save.get("watchlist", [])) + [g.ss_players()[0]["id"]]
r.frames(1, draw=True)
check(g._still_page[0] != k2, "the page changes when the save does (watchlist)")
g.ss_scroll(1)
k3 = g._still_page[0]
r.frames(1, draw=True)
check(g._still_page[0] != k3, "scrolling repaints it")
g.open_packs()
r.frames(2, draw=True)
check(g._still_page[0][0] == "packs", "the pack store keeps its own page")
g.draft_target = 400
r.frames(30, draw=True)
check(abs(g.draft_x - min(400, g.draft_max_scroll())) < 2, "the drafts still glide when you scroll them (%.0f)" % g.draft_x)

# the walkout on the browser's paths, start to finish
g.state = rf.TITLE
check(g.buy_pack(0) and g.state == rf.PACK_OPEN, "buying a pack opens it")
r.frames(20, dt=1 / 30.0, draw=True)
r.click(960, 540)
while g.state == rf.PACK_OPEN and g.pack_reveal["t"] < 9.0:
    r.frames(1, dt=1 / 30.0, draw=True)
check(g.pack_reveal.get("wk_landed"), "the card lands")
g.pack_reveal = {"card": g.cards["INT_messi"], "tier": "A", "count": 1, "pack": 1, "t": 0.0, "opened": False}
g.state = rf.PACK_OPEN
r.frames(20, dt=1 / 30.0, draw=True)
r.click(960, 540)
while g.state == rf.PACK_OPEN and g.pack_reveal["t"] < 9.5:
    r.frames(1, dt=1 / 30.0, draw=True)
n = len(g.pack_reveal.get("wk_parts", []))
check(g.pack_reveal.get("wk_landed") and 0 < n <= 450, "a pool A card: confetti, lighter in the browser (%d pieces)" % n)
# Season 1 (6 Nov): the pass and the locker in the browser, the ad round trip through the page's hooks
Win.ad_answer = ""
Win.aswcAd = lambda self, what: setattr(Win, "ad_answer", '{"ok": true}')
Win.aswcAdPoll = lambda self: (Win.ad_answer, setattr(Win, "ad_answer", ""))[0]
Win.aswcOwner = lambda self: True
g.card_detail = None                                       # (the walkout above left its card open)
g.open_pass()
r.frames(10, draw=True)
gems = int(g.save.get("gems", 0))
g.watch_ad()                                               # (ads are off for now, the path stays)
r.frames(3, draw=True)
check(int(g.save.get("gems", 0)) == gems + rf.GEMS_PER_AD, "browser: an ad watched through the page's hooks pays gems")
# codes: the button in the ad's slot, clicked the browser's way, round trip through the hooks
Win.code_answer = ""
Win.aswcCode = lambda self: setattr(Win, "code_answer",
                                     '{"ok": true, "code": "WEBTEST", "gift": {"gems": 40, "coins": 0, "packs": 0}}')
Win.aswcCodePoll = lambda self: (Win.code_answer, setattr(Win, "code_answer", ""))[0]
gems = int(g.save.get("gems", 0))
ax, ay = g.pass_layout()["ad"].center
r.click(ax / 3.0, ay / 3.0)                                # (the browser's mouse is in 640 x 360 points)
r.frames(3, draw=True)
check(int(g.save.get("gems", 0)) == gems + 40, "browser: ENTER A CODE through the page's hooks pays the code")
import time as _t
t0 = _t.time()
r.frames(30, draw=True)
check(True, "the pass draws in the browser (%.1f ms a frame here)" % ((_t.time() - t0) / 30 * 1000))
g._owner_seen = None
check(g.pfp_owned("owner_live"), "browser: the page's owner flag opens the owner pictures")
g.open_locker("pfp")
r.frames(10, draw=True)
g.locker_tab = "ball"
r.frames(10, draw=True)
check(g.state == rf.LOCKER, "the locker draws in the browser")
# the glass budget holds
check(g._web_glass_px <= g.GLASS_BUDGET_PX, "glass panels stay in their budget (%.1f Mpx)" % (g._web_glass_px / 1e6))
print("ALL PASS" if not fails else "%d FAILED" % len(fails))
sys.exit(1 if fails else 0)
