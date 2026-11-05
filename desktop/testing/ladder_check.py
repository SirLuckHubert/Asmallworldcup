"""THE LADDER (29 Oct): club mode as three divisions + the Champions Cup, with a twist and a bonus
objective every match.

    python3 ladder_check.py      (pictures: out/lg_*.png)

Plays seasons by setting each match's score and blowing full time through the game's own code."""
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


random.seed(11)
squad = ["ARS_saka", "CHE_caicedo", "AST_martinez", "BRE_wissa", "BOU_evanilson"]
r = Run(save={"coins": 1000, "xp": 900, "owned": {c: 1 for c in squad}, "squad": list(squad),
              "tutorial_done": True, "starter_opened": True})
g = r.g
L = g.ladder()
sizes = [len(g.div_members(d)) for d in range(3)]
check(sizes == [7, 7, 7], "21 clubs in three divisions of 7: %s" % sizes)
check(L["mine"] == 2, "your club starts in %s" % rf.DIVISIONS[L["mine"]])
top = [rf.CLUBS[i][0] for i in g.div_members(0)]
check("ARS" in top and "MCI" in top and "SUN" not in top, "the strongest clubs are in the Premier League: %s" % top)
g.mode = "club"; g.go_to_club()
r.frames(30)
r.shot("lg_hub_new", half=False)
Lay = g.lg_layout()


def play(score, check_coins=False):
    """Click PLAY, pick a player, set the score, full time, back through the table."""
    r.click(Lay["play"].center)
    if g.state != rf.LINEUP:
        return False
    g.pick_player([c for c in g.lineup_cards() if g.available(c)][0])
    r.frames(3)
    g.score_home, g.score_away = score
    if score[0] > 0 and score[1] > 0:
        g.match_low = -1
    coins0 = g.save["coins"]
    g.finish_match()
    g.advance_after_goal()
    return g.save["coins"] - coins0


earned = play((3, 0))
check(g.state == rf.TABLE, "after the match: the result screen")
check(g.lg is not None and len(g.lg["members"]) == 8, "a division of 8 (7 clubs + you)")
check(g.table[g.user_idx]["pts"] == 3 or g.lg["last"]["twist"] == "derby", "a win is 3 points (6 on derby day)")
check(earned >= rf.REWARD["win"], "a win pays coins (%d)" % earned)
others_played = sum(1 for i in g.lg["members"] if g.table[i]["p"] == 1)
check(others_played == 8, "everyone in the division played matchday 1 (%d)" % others_played)
r.frames(20); r.shot("lg_result", half=False)
r.click(400, 400)
check(g.state == rf.CLUB, "a click goes back to the hub")
r.frames(20); r.shot("lg_hub_season", half=False)
# twists really change the physics
g.match_twist = "rain"; g.apply_twist()
check(rf.TWIST["grip"] < 1.0 and rf.TWIST["roll"] < 1.0, "RAIN: less grip, the ball skips")
g.match_twist = "moon"; g.apply_twist()
check(rf.TWIST["grav"] < 0.8, "LOW GRAVITY: everything falls slower")
g.match_twist = "giant"; g.apply_twist()
check(g.ball.radius > rf.BALL_RADIUS * 1.3, "GIANT BALL: radius %d" % g.ball.radius)
g.match_twist = "wind"; g.half = 1; g.apply_twist()
w1 = rf.TWIST["wind"]; g.half = 2; g.apply_twist()
check(w1 > 0 > rf.TWIST["wind"], "WINDY: it turns round at half time")
g.clear_twist()
check(g.ball.radius == rf.BALL_RADIUS and rf.TWIST["grav"] == 1.0, "and everything goes back after")
# objectives
g.score_home, g.score_away, g.forfeited, g.match_low, g.first_goal = 3, 1, False, -1, "away"
check(g.objective_done("comeback") and g.objective_done("three") and g.objective_done("win2"),
      "objectives read the match: comeback, 3 goals, by 2")
check(not g.objective_done("clean") and not g.objective_done("first"), "...and fail when they should")
# win the rest of the season: promoted, and the other clubs moved too
for k in range(rf.CLUB_ROUNDS - 1):
    play((4, 0))
    r.click(400, 400)
    if g.state == rf.TABLE:
        r.frames(10); r.shot("lg_season_end", half=False)
        r.click(400, 400)
end = g.lg["end"]
check(end is not None and end["result"] in ("champions", "promoted"), "won every match: %s" % (end and end["result"]))
check(g.ladder()["mine"] == 1, "up to the CHAMPIONSHIP")
sizes = [len(g.div_members(d)) for d in range(3)]
check(sizes == [7, 7, 7], "the divisions still hold 7 clubs each after the moves: %s" % sizes)
check(len(end["up"]) == 4 and len(end["down"]) == 4, "2 up and 2 down between each pair of divisions")
mail = g.mail_list()
check(mail and mail[0].get("gift", {}).get("coins"), "the season's rewards are in the mail")
check(g.state == rf.CLUB and g.lg_phase() == "over", "back at the hub, season over")
r.frames(20); r.shot("lg_hub_next", half=False)
# a new season starts in the Championship
play((2, 1))
check(g.lg["div"] == 1, "season 2 is in the Championship")
r.click(400, 400)
# jump to the Premier League and finish top: the Champions Cup follows
g.ladder()["mine"] = 0
g.lg = None
g.go_to_club()
for k in range(rf.CLUB_ROUNDS):
    play((5, 0))
    for _ in range(3):
        if g.state == rf.TABLE:
            r.click(400, 400)
check(g.lg_phase() == "cup", "top of the Premier League: into the CHAMPIONS CUP")
r.frames(20); r.shot("lg_hub_cup", half=False)
boost_before = None
r.click(Lay["play"].center)
g.pick_player([c for c in g.lineup_cards() if g.available(c)][0])
check(g.cpu_card is not None and g.cpu_card.get("boosted"), "the cup's clubs are boosted")
g.score_home, g.score_away = 2, 0
g.finish_match(); g.advance_after_goal()
r.click(400, 400)
play((1, 0))
r.frames(10); r.shot("lg_cup_won", half=False)
check(g.lg["cup"]["won"] is True, "won the semi and the final: CHAMPIONS CUP WINNERS")
cards = (g.mail_list()[0].get("gift") or {}).get("cards") or []
check(cards and g.card_pool(g.cards[cards[0]]) == "A", "the cup pays a pool A card (%s)" % cards)
r.click(400, 400)
# the save keeps the ladder and the season
g.write_save()
g.lg_restore()
check(g.lg is not None and g.lg_phase() == "over", "the ladder and the season survive a save and a load")
print("%d failed %s" % (len(fails), fails))
sys.exit(1 if fails else 0)
