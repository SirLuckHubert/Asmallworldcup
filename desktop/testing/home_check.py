"""The new home screen (28 Oct): it draws, and every button goes where it should.

    python3 home_check.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Run, pygame, rf
fails = []
def check(name, ok, info=""):
    print(("PASS " if ok else "FAIL ") + name + ("   " + info if info else ""))
    if not ok: fails.append(name)

def fresh():
    r = Run(save={"coins": 4200}, name="home.json"); g = r.g
    g.state = rf.TITLE; g.menu_page = "main"; g.tut = None
    r.frames(2, draw=True)
    return r, g

r, g = fresh()
check("the new home is on", rf.HOME_V2)
try:
    for _ in range(3):
        g.draw()
    ok = True
except Exception as e:
    ok = False; print(e)
check("it draws", ok)
L = g.home_layout()
def click(rect):
    g.title_click(pygame.Vector2(rect.centerx, rect.centery))

for tab, want in (("PLAY", "play page"), ("STORE", rf.STORE), ("TEAM", rf.MYCLUB)):
    r, g = fresh()
    rect = [rr for t, rr in g.home_layout()["tabs"] if t == tab][0]
    click(rect)
    got = "play page" if (g.state == rf.TITLE and g.menu_page == "play") else g.state
    check("top bar %s goes to its screen" % tab, got == want, str(got))
r, g = fresh(); rect = [rr for t, rr in g.home_layout()["tabs"] if t == "MAIL"][0]; click(rect)
check("top bar MAIL opens the mail", g.state == rf.MAIL, str(g.state))
r, g = fresh(); click(g.home_layout()["quit"])
check("the power button quits", g.quit_requested)
r, g = fresh(); click(g.home_layout()["play"])
check("PLAY starts the featured mode (World Cup -> pick a nation)", g.state == rf.SELECT and g.mode == "wc", str(g.state))
r, g = fresh(); g.play_tab = 1; g.draw(); click(g.home_layout()["play"])
check("the featured mode follows the PLAY tab you last picked (club)", g.mode == "club" and g.state == rf.CLUB)
r, g = fresh(); click(g.home_layout()["change"])
check("CHANGE MODE opens the PLAY screen", g.state == rf.TITLE and g.menu_page == "play")
r, g = fresh(); click(g.home_layout()["pack"])
check("the pack tile opens the newest pack (whichever of its rotation is in)",
      g.state == rf.PACKS and g.view_pack == g.shown_pack(len(rf.PACK_NAMES) - 1),
      "%s %s" % (g.state, getattr(g, "view_pack", None)))
r, g = fresh(); click(g.home_layout()["event"])
check("the event tile opens the Game Box", g.state == rf.EVENT, str(g.state))
r, g = fresh(); click(g.home_layout()["plate"])
check("the nameplate opens the hero's card", g.card_detail is not None)
r, g = fresh(); g.tut = {"step": "packs"}
tgt = g.tutorial_target()
store = [rr for t, rr in g.home_layout()["tabs"] if t == "STORE"][0]
check("the tutorial still points at STORE", tgt == [store])
g.tut = None
# the hero: your best owned card with a figure, else the fallback
r, g = fresh()
figs = [c for c in g.cards.values() if c["id"] in g.card_figs]
best = max(figs, key=lambda c: c["rating"])
g.save["owned"][best["id"]] = 1
check("the hero is your best card with a figure", g.home_hero_card()["id"] == best["id"], best["name"])
for key, *_ in rf.Game.PLAY_TABS:                       # every featured mode draws
    g.play_tab = [k for k, *_ in rf.Game.PLAY_TABS].index(key); g.draw()
check("every featured mode draws", True)
print("\n%d failed" % len(fails), fails)
sys.exit(1 if fails else 0)
