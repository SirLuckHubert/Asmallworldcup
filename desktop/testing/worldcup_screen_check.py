"""The new World Cup screen (29 Oct): it draws in every state and every click still works.

    python3 worldcup_screen_check.py      (pictures: out/wc2_*.png)"""
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


random.seed(6)
r = Run(save={"coins": 4200, "xp": 900}); g = r.g
check(rf.WC_V2, "the new World Cup screen is on")
g.mode = "wc"; g.wc_slot = "normal"; g.state = rf.SELECT
r.frames(60)
r.shot("wc2_empty", half=False)
flags, arrow, nodes = g.select_layout()
check(len(flags) == len(g.teams) and len(nodes) == len(rf.ROUNDS), "a flag per nation, a disc per round")
check(len(g.diff_rects) == 3, "EASY / MEDIUM / HARD switch")
r.click(flags[2].center)
check(g.team == 2, "clicking a flag picks that nation (%s)" % g.team)
r.click(g.diff_rects[2].center)
check(g.difficulty == 2, "the switch sets HARD")
r.click(g.diff_rects[0].center)
check(g.difficulty == 0, "...and EASY")
r.shot("wc2_team", half=False)
r.click(arrow.center)
check(g.roulette is not None, "PLAY draws an opponent")
r.click(flags[5].center)
check(g.team == 2, "the nations are locked while the draw runs")
for k in range(600):
    r.frames(1)
    if g.roulette and g.roulette["landed"]:
        break
check(g.roulette is not None and g.roulette["landed"], "the draw lands")
r.frames(60)
r.shot("wc2_landed", half=False)
r.click(rf.WIDTH // 2, 300)
check(g.state == rf.LINEUP and len(g.opponents) == 1, "a click after the draw goes to the line-up")
# a run in progress, then the champion screen, then Impossible: they all draw
g.state = rf.SELECT
g.opponents, g.results, g.round = [9, 6], [(2, 1), (3, 0)], 2
r.frames(30); r.shot("wc2_run", half=False)
fl2, ar2, _ = g.select_layout()
r.click(fl2[7].center)
check(g.team == 2, "a run in progress keeps its nation")
g.opponents = list(range(3, 10)); g.results = [(1, 0)] * 7; g.round = 7
r.frames(30); r.shot("wc2_champions", half=False)
check(not g.can_start(), "after the final there's nothing left to play")
g.new_tournament(None)
g.wc_slot = "impossible"
r.frames(30); r.shot("wc2_impossible", half=False)
g.select_layout()
check(g.diff_rects == [], "Impossible has no difficulty switch")
g.wc_slot = "normal"
print("%d failed %s" % (len(fails), fails))
sys.exit(1 if fails else 0)
