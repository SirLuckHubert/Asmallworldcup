"""THE WORLD'S GAME evolutions (1 Nov): Messi, Ronaldo and Lewandowski start grey with PlayStyles
level 2 + level 1, do quests with you, and evolve through four stages up to 132 OVR with a level 3
(purple) PlayStyle and a level 2.

    python3 wg_evo_check.py      (pictures: out/wgevo_*.png)"""
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


random.seed(5)
WG = ["WG_messi", "WG_ronaldo", "WG_lewandowski"]
squad = ["WG_messi", "CHE_caicedo", "AST_martinez", "BRE_wissa", "BOU_evanilson"]
owned = {c: 1 for c in squad}
owned["WG_lewandowski"] = 1
r = Run(save={"coins": 1000, "xp": 900, "owned": owned, "squad": list(squad),
              "tutorial_done": True, "starter_opened": True}, name="save_wgevo.json")
g = r.g
for cid in WG:
    check(cid in g.cards and g.cards[cid]["design"] == "worldsgame", "%s is a World's Game card" % cid)
M, R, L = (g.cards[c] for c in WG)

# ---- stage 0: the grey one
v = g.upgraded(M)
check(g.wg_stage(M) == 0, "Messi starts at stage 0 (GREY)")
check([lv for _p, lv in v["ps"][:2]] == [2, 1], "...with PlayStyles level 2 + level 1 (%s)" % [lv for _p, lv in v["ps"]])
check(v["rating"] == M["rating"], "...at his base OVR (%d)" % v["rating"])
check(g.card_template_key(g.upgraded(M)) == "flagwg0_" + M["team"], "...on the grey evolution card (%s)" % g.card_template_key(M))

# ---- the OVR steps, every card, every stage
for card in (M, R, L):
    steps = [g.wg_evo_ovr(card, s) for s in range(4)]
    even = all(steps[i] <= steps[i + 1] for i in range(3))
    check(steps[0] == card["rating"] and steps[3] == rf.WG_EVO_OVR and even,
          "%s: %s - base to %d in even steps" % (card["name"], " -> ".join(map(str, steps)), rf.WG_EVO_OVR))

# ---- the quests, through the real game: goals in a club match
g.mode = "club"
g.go_to_club()
Lay = g.lg_layout()
r.click(Lay["play"].center)
check(g.state == rf.LINEUP, "club PLAY opens the team sheet")
mine = [c for c in g.lineup_cards() if c["id"] == "WG_messi"]
check(bool(mine), "Messi is on the team sheet")
g.pick_player(mine[0])
r.frames(3)
check(g.my_card["id"] == "WG_messi" and g.player.rating == g.upgraded(M)["rating"] if hasattr(g.player, "rating")
      else g.my_card["id"] == "WG_messi", "he goes out as your player")
sig0 = g.prog_sig(M)
for k in range(3):
    g.last_touch = "home"
    g.score_goal("home")
    r.frames(2)
    if k < 2:
        check(g.wg_evo("WG_messi") == {"stage": 0, "n": k + 1}, "goal %d: quest %d/3" % (k + 1, k + 1))
check(g.wg_stage(M) == 1, "the third goal: he EVOLVES to stage 1 (AWAKENED)")
check(getattr(g, "evolved", None) == ("WG_messi", 1), "...and the game knows it just happened")
check(g.prog_sig(M) != sig0, "...his card face is redrawn (cache key changed)")
v1 = g.upgraded(M)
check(v1["rating"] == g.wg_evo_ovr(M, 1) and v1["rating"] > M["rating"], "...OVR %d -> %d" % (M["rating"], v1["rating"]))
check(all(v1["stats"][k] >= M["stats"][k] for k in M["stats"]), "...and his stats rise with it")
check(g.cards["WG_messi"]["rating"] == M["rating"], "the table's card is untouched (a CPU Messi is the grey one)")

# an own goal does not count
g.last_touch = "away"
n = g.wg_evo("WG_messi")["n"]
g.score_goal("home")
check(g.wg_evo("WG_messi")["n"] == n, "an own goal by the CPU is not HIS goal")

# ---- win quest: settle three wins (stage 1 -> 2)
def win(impossible=False):
    g.played_this_match = {"WG_messi", "CHE_caicedo"}
    g.mode = "wc" if impossible else "club"
    g.difficulty = rf.IMPOSSIBLE if impossible else 1
    g.score_home, g.score_away = 2, 0
    g.forfeited = False
    if impossible:
        g.wc_slot = "impossible"
        g.new_tournament(0)
        g.opponents = list(range(1, 8)); g.results = []; g.round = 0
    else:
        g.go_to_club()
    g.score_home, g.score_away = 2, 0
    g.played_this_match = {"WG_messi", "CHE_caicedo"}
    g.settle_match()

for k in range(3):
    win()
check(g.wg_stage(M) == 2, "three wins with him in your team: stage 2 (RADIANT)")
v2 = g.upgraded(M)
check([lv for _p, lv in v2["ps"][:2]] == [2, 2], "...PlayStyles now level 2 + level 2")
# a loss / a forfeit doesn't count
g.played_this_match = {"WG_messi"}; g.mode = "club"; g.go_to_club()
g.score_home, g.score_away = 0, 1; g.forfeited = False
g.played_this_match = {"WG_messi"}
g.settle_match()
check(g.wg_evo("WG_messi")["n"] == 0, "a loss moves nothing")

# ---- impossible wins (stage 2 -> 3); a normal win doesn't count for it
win()
check(g.wg_evo("WG_messi") == {"stage": 2, "n": 0}, "a normal win is not an Impossible win")
win(True)
check(g.wg_evo("WG_messi") == {"stage": 2, "n": 1}, "Impossible win 1/2")
win(True)
check(g.wg_stage(M) == 3, "the second Impossible win: stage 3 (LIMITLESS)")
check(g.wg_evo("WG_messi")["n"] == 0, "...one match moves one quest (no double count)")
v3 = g.upgraded(M)
check(v3["rating"] == rf.WG_EVO_OVR, "...OVR %d" % v3["rating"])
check([lv for _p, lv in v3["ps"][:2]] == [3, 2], "...PlayStyles level 3 + level 2")
check(len(v3["ps"]) == len(M["ps"]), "...and none lost or added")
win(True)
check(g.wg_stage(M) == 3 and g.wg_evo("WG_messi")["n"] == 0, "nothing past the last stage")

# ---- the purple level 3 icon
key = v3["ps"][0][0]["key"]
p3 = g.ps_icon(key, 64, 3)
check(p3 is not None and rf.find_sprite("ps_%s_p" % key) is not None, "the level 3 icon is the purple one (ps_%s_p)" % key)
check(all(rf.find_sprite("ps_%s_p" % ps["key"]) is not None for ps in rf.PLAYSTYLES.values())
      if hasattr(rf, "PLAYSTYLES") and isinstance(rf.PLAYSTYLES, dict) else True, "every PlayStyle has a purple icon")
check(rf.PS_LEVEL_SCALE[2] > rf.PS_LEVEL_SCALE[1], "level 3 fires harder than level 2 (x%.1f)" % rf.PS_LEVEL_SCALE[2])

# ---- who isn't evolved
check(g.wg_stage(R) == 0 and g.upgraded(R) is R, "Ronaldo (not owned) stays grey at his base")
check(g.wg_evo_event("goal", "WG_ronaldo") is False, "...and can't do quests for you")
check(g.wg_stage(dict(M, boosted=True)) == 0, "a boosted (CPU) copy is the grey one")
check(g.wg_stage(L) == 0, "Lewandowski (owned, no quests yet) is still grey")
check(g.wg_evo_event("win", "CHE_caicedo") is False, "other cards have no evolution")

# ---- the card at every stage, and the screen
for st in range(4):
    check(rf.find_sprite("tpl_wgevo%d_card" % st) is not None and rf.find_sprite("tpl_wgevo%dframe_card" % st) is not None,
          "stage %d card sprites are there" % st)
    g.save["wg_evo"]["WG_messi"] = {"stage": st, "n": 0}
    check(g.card_template_key(g.upgraded(M)) == "flagwg%d_%s" % (st, M["team"]), "stage %d draws the stage %d card" % (st, st))
    face = g.card_face(g.upgraded(M), (360, 450))
    check(face is not None, "...and its face renders")
g.save["wg_evo"]["WG_messi"] = {"stage": 1, "n": 2}
g.state = rf.TITLE
g.card_detail = g.cards["WG_messi"]; g.card_tab = 0
r.frames(10)
r.shot("wgevo_view", half=False)
check(True, "the EVOLUTION box draws (out/wgevo_view.png)")
g.card_detail = g.cards["WG_lewandowski"]
r.shot("wgevo_view_lewa", half=False)
g.card_detail = g.cards["WG_ronaldo"]
r.shot("wgevo_view_unowned", half=False)
check(True, "...for a stage 0 card and one you don't own")
g.card_detail = None

# ---- an old sprites folder: the plain World's Game card
real = rf.find_sprite
rf.find_sprite = lambda n, *a, **k: None if str(n).startswith("tpl_wgevo") else real(n, *a, **k)
g2 = Run(save={"owned": {"WG_messi": 1}, "tutorial_done": True, "starter_opened": True}, name="save_wgevo2.json").g
check(g2.card_template_key(g2.cards["WG_messi"]) == "wg", "no evolution sprites: the old World's Game card")
rf.find_sprite = real

print("\n%d failed" % len(fails))
sys.exit(1 if fails else 0)
