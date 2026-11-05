"""The PROFILE tab (29 Oct): your club, level, best card, collection, the trophy cabinet and your
numbers - and the trophies really get counted.

    python3 profile_check.py      (pictures: out/profile_*.png)"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Run, rf

fails = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


random.seed(8)
squad = ["ARS_saka", "CHE_caicedo", "AST_martinez", "BRE_wissa", "BOU_evanilson"]
r = Run(save={"coins": 1000, "xp": 2400, "owned": {c: 1 for c in squad}, "squad": list(squad),
              "tutorial_done": True, "starter_opened": True})
g = r.g
r.frames(60)
L = g.home_layout()
tab = dict(L["tabs"]).get("PROFILE")
check(tab is not None, "PROFILE is a tab on the home screen")
r.click(tab.center)
check(g.state == rf.PROFILE, "the tab opens the profile")
r.frames(30)
r.shot("profile_empty", half=False)
check(sum(g.trophy_count(k[0]) for k in g.TROPHIES) == 0, "a new save has an empty cabinet")
r.click(g.BACK_RECT.center)
check(g.state == rf.TITLE, "BACK goes home")
r.click(L["level"].center)
check(g.state == rf.PROFILE, "the level ring opens it too")
# win a World Cup final through the game's own code
g.mode = "wc"; g.wc_slot = "normal"; g.difficulty = 1
g.new_tournament(0)
g.opponents = list(range(1, 8)); g.results = [(1, 0)] * 6; g.round = 6
g.score_home, g.score_away = 2, 1
g.forfeited = False
g.settle_match()
check(g.trophy_count("wc") == 1 and g.trophies().get("wc_medium") == 1, "winning the final puts a WORLD CUP in")
check(g.save["stats"]["all"]["p"] == 1 and g.save["stats"]["all"]["w"] == 1, "...and the match is counted")
# a perfect season in League One through the ladder
g.mode = "club"
g.go_to_club()
Lay = g.lg_layout()
for k in range(rf.CLUB_ROUNDS):
    r.click(Lay["play"].center)
    g.pick_player([c for c in g.lineup_cards() if g.available(c)][0])
    g.score_home, g.score_away = 3, 0
    g.finish_match(); g.advance_after_goal()
    for _ in range(3):
        if g.state == rf.TABLE:
            r.click(400, 400)
check(g.trophy_count("league_2") == 1, "winning League One puts its trophy in")
check(g.trophy_count("promotions") == 1, "...a promotion")
check(g.trophy_count("perfect") == 1, "...and, all 7 won, a PERFECT SEASON")
check(g.save["stats"]["all"]["p"] == 8 and g.save["stats"]["club"]["w"] == 7, "8 matches counted, 7 club wins")
g.add_trophy("cup"); g.add_trophy("wc_hard"); g.add_trophy("wc_hard")
g.open_profile()
r.frames(30)
r.shot("profile_trophies", half=False)
check(g.trophy_count("wc") == 3, "World Cups add up across difficulties (%d)" % g.trophy_count("wc"))
# an old save: titles and cups come back out of the ladder's history
r2 = Run(save={"coins": 0, "tutorial_done": True, "starter_opened": True,
               "ladder": dict(g.save["ladder"], cups=2)}, name="save_old.json")
check(r2.g.trophy_count("league_2") == 1 and r2.g.trophy_count("cup") == 2,
      "a save from before trophies were counted gets its titles and cups back")
print("%d failed %s" % (len(fails), fails))
sys.exit(1 if fails else 0)
