"""THE GAUNTLET (30 Oct): ten opponents, each one harder, one loss ends it, THE MACHINE at the top.

    python3 gauntlet_check.py      (pictures: out/gt_*.png)

Plays whole runs through the game's own code: PLAY, pick a player, the half-time sub, set the
score, full time, back to the stairs."""
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


random.seed(4)
squad = ["ARS_saka", "CHE_caicedo", "AST_martinez", "BRE_wissa", "BOU_evanilson"]
r = Run(save={"coins": 1000, "xp": 2400, "owned": {c: 1 for c in squad}, "squad": list(squad),
              "tutorial_done": True, "starter_opened": True}, name="save_gt.json")
g = r.g
r.frames(30)
# ---- it's a tab in PLAY, and the home screen can feature it
keys = [t[0] for t in g.PLAY_TABS]
check("gauntlet" in keys, "THE GAUNTLET is a tab in PLAY")
g.state = rf.TITLE
g.menu_page = "play"
g.play_tab = keys.index("gauntlet")
r.frames(10)
r.shot("gt_play_tab", half=False)
g.menu_page = "main"
r.frames(5)
r.shot("gt_home_feature", half=False)
g.play_go("gauntlet")
check(g.state == rf.GAUNTLET and g.mode == "gauntlet", "its button opens the Gauntlet")
r.frames(20)
r.shot("gt_hub_fresh", half=False)
L = g.gt_layout()
r.click(L["play"].center)
run = g.gt_run()
check(run is not None and len(run["opps"]) == rf.GT_LEN == 10, "START RUN draws all ten opponents")
specs = [tuple(o) for o in run["opps"][:-1]]
check(len(set(specs)) == len(specs), "nobody twice in one run")
check(run["opps"][-1][0] == "machine", "number 10 is THE MACHINE")
st = [g.gt_strength(k) for k in range(9)]
inside = all(rf.GT_RUNGS[k][1][0] - 3 <= st[k] <= rf.GT_RUNGS[k][1][1] + 3 for k in range(9))
check(inside and st[8] >= 115 and st[0] <= 90, "each rung's team is in its strength window: %s" % st)
check(all(run["twists"][k] == "normal" for k in range(3)) and
      all(run["twists"][k] in rf.GT_PLAYABLE_TWISTS for k in range(3, 9)), "twists from rung 4: %s" % run["twists"])
check(sorted(run["squad"]) == sorted(squad) and all(v == 100 for v in run["stam"].values()), "your five, all fresh")
r.frames(20)
r.shot("gt_hub_run", half=False)
r.hover(L["steps"][8].centerx, L["steps"][8].centery)
r.frames(5)
r.shot("gt_hub_scout", half=False)


def play_rung(score, first=None, second=None):
    """PLAY, pick a player, the half-time sub, the score, full time."""
    g.gt_modal = None
    k = g.gt_rung()
    r.click(L["play"].center)
    if g.state == rf.GAUNTLET and g.gt_reveal is not None:
        return "reveal"
    if g.state != rf.LINEUP:
        return "no lineup (%s)" % g.state
    ok = [c for c in g.lineup_cards() if g.available(c)]
    g.pick_player(first or ok[0])
    r.frames(3)
    info = {"twist": rf.TWIST.copy(), "start": (g.score_home, g.score_away), "cpu": g.cpu_card,
            "skill": g.brain.skill, "impossible": g.brain.impossible}
    g.start_sub()
    if second is not None:
        g.sub["pick"] = second["id"]
    else:                                           # the freshest card that isn't the first-half one
        rest = [c for c in g.lineup_cards() if g.available(c) and c["id"] != g.my_card["id"]]
        if rest:
            g.sub["pick"] = max(rest, key=lambda c: g.stamina_of(c))["id"]
    g.end_sub_pick()
    g.kick_off_second_half()
    g.score_home, g.score_away = score
    g.finish_match()
    g.advance_after_goal()
    return info


coins0 = g.save["coins"]
info = play_rung((2, 0))
check(isinstance(info, dict) and g.state == rf.GAUNTLET, "a rung is a full match, then back to the stairs")
check(g.gt_modal and g.gt_modal["kind"] == "cleared" and g.gt_run()["rung"] == 1, "rung 1 cleared")
check(g.save["coins"] - coins0 >= rf.GT_RUNGS[0][6], "it pays (%d)" % (g.save["coins"] - coins0))
spent = sum(100 - v for v in g.gt_run()["stam"].values())
want = sum(g.half_cost(g.cards[c]) for c in g.played_this_match)
check(spent == want and len(g.played_this_match) == 2, "two halves, %d%% between them (RELENTLESS pays less)" % spent)
full = {c: g.gt_halves_left(c, 100) for c in squad}
check(all(v in (4, 6) for v in full.values()), "4 halves a card, 6 with RELENTLESS: %s" % full)
check(info["skill"] == rf.GT_RUNGS[0][2] and not info["impossible"], "rung 1: a MEDIUM brain")
r.frames(10)
r.shot("gt_cleared", half=False)
r.click(400, 400)
check(g.gt_modal is None, "a click closes it")
# ---- climb to rung 9, checking what each rung does
for k in range(1, 9):
    info = play_rung((3, 1))
    row = rf.GT_RUNGS[k]
    tw = g.gt_run()["twists"][k] if g.gt_run() else None
    if k == 3:
        check(info["twist"] != {"grav": 1.0, "grip": 1.0, "roll": 1.0, "wind": 0.0} or tw == "giant",
              "rung 4's twist (%s) is in the physics" % tw)
        check(info["skill"] == 0.95, "rung 4: a HARD brain")
    if row[5]:
        check(info["start"] == (0, 1), "rung %d starts 1-0 down (%s)" % (k + 1, info["start"]))
    if row[4]:
        check(info["cpu"].get("boosted") and info["cpu"]["rating"] >= g.cards[info["cpu"]["id"]]["rating"] + row[4][0],
              "rung %d's opponent is boosted +%d" % (k + 1, row[4][0]))
check(g.gt_run()["rung"] == 9, "nine cleared: THE MACHINE is next")
left = sum(g.gt_halves_left(c) for c in g.gt_run()["squad"])
check(left == sum(full.values()) - 18, "18 halves played, %d left for THE MACHINE" % left)
check(rf.TWIST == {"grav": 1.0, "grip": 1.0, "roll": 1.0, "wind": 0.0}, "the twist is cleared between matches")
g.gt_modal = None
r.frames(5)
r.shot("gt_hub_machine_next", half=False)
# ---- THE MACHINE
res = play_rung((1, 0))
check(res == "reveal", "THE MACHINE makes an entrance first")
r.frames(130)
r.shot("gt_reveal_mid", half=False)
r.frames(120)
r.shot("gt_reveal", half=False)
mt = g.gt_run()["twists"][9]
ids = g.gt_machine_ids(mt)
check(len(ids) == 3 and all(i in g.cards for i in ids), "its three for %s: %s" % (mt, ids))
r.click(400, 400)
check(g.state == rf.LINEUP, "a click: on to the lineup")
ok = [c for c in g.lineup_cards() if g.available(c)]
g.pick_player(ok[0])
r.frames(3)
check(g.brain.impossible and g.brain.skill == 1.0, "THE MACHINE thinks like Impossible")
check(g.cpu_card["id"] == ids[0] and g.cpu_card.get("boosted"), "its measured best starts, boosted")
r.frames(150)
r.shot("gt_machine_sheet", half=False)
for _ in range(600):
    if g.state == rf.VERSUS:
        r.frames(1)
g.versus = None
if g.state == rf.VERSUS:
    g.state = rf.KICKOFF
r.frames(90)
r.shot("gt_machine_match", half=False)
g.start_sub(); g.end_sub_pick(); g.kick_off_second_half()
check(g.cpu_card["id"] in ids, "its half-time sub comes from the same three")
mail0 = len(g.mail_list())
g.score_home, g.score_away = 2, 1
g.finish_match()
r.frames(20)
r.shot("gt_machine_fulltime", half=False)
g.advance_after_goal()
check(g.gt_run() is None and g.gt()["wins"] == 1 and g.gt()["best"] == 10, "THE MACHINE beaten: run over, won")
check(g.trophy_count("gauntlet") == 1, "the Gauntlet trophy is in the cabinet")
m = g.mail_list()[0]
cards = (m.get("gift") or {}).get("cards") or []
check(len(g.mail_list()) == mail0 + 1 and m["gift"]["coins"] == rf.GT_WIN_COINS and cards and
      g.card_pool(g.cards[cards[0]]) == "A", "the mail: %d coins and a pool A card" % rf.GT_WIN_COINS)
check(not g.brain.impossible, "and the CPU is back to normal after")
r.frames(10)
r.shot("gt_won", half=False)
r.click(400, 400)
# ---- a run that ends on rung 1
r.click(L["play"].center)
check(g.gt_run() is not None and g.gt()["runs"] == 2, "a second run")
play_rung((0, 1))
check(g.gt_run() is None and g.gt_modal["kind"] == "lost", "one loss: the run is over")
check(g.gt()["best"] == 10, "the best stays")
r.frames(10)
r.shot("gt_lost", half=False)
r.click(400, 400)
# ---- ESC / BACK out of the lineup goes back to the stairs; the run survives a save and a load
r.click(L["play"].center)
r.click(L["play"].center)
check(g.state == rf.LINEUP, "lineup for rung 1")
r.click(g.BACK_RECT.center)
check(g.state == rf.GAUNTLET, "BACK from the lineup: the stairs")
g.write_save()
r2 = Run(name="save_gt.json", keep=True)
check(r2.g.gt_run() is not None and r2.g.gt_run()["opps"] == g.gt_run()["opps"], "the run survives a save and a load")
# ---- abandon
q = L["quit"].center
r.click(q)
check(g.gt_run() is not None, "ABANDON asks first")
r.click(q)
check(g.gt_run() is None, "...and abandons on the second click")
# ---- the profile has room for nine
g.open_profile()
r.frames(20)
r.shot("gt_profile", half=False)
check(len(g.TROPHIES) == 9, "nine trophies in the cabinet")
print("%d failed %s" % (len(fails), fails))
sys.exit(1 if fails else 0)
