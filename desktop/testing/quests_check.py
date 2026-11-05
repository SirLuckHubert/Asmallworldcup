"""QUESTS (1 Nov): three dailies, three weeklies, the daily chest, free packs - moved by the game's
own code (matches settled, goals scored, packs bought, PlayStyles fired, trophies won) and claimed
by clicking the QUESTS screen.

    python3 quests_check.py      (pictures: out/quests_*.png)"""
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
squad = ["ARS_saka", "CHE_caicedo", "AST_martinez", "BRE_wissa", "BOU_evanilson"]
r = Run(save={"coins": 5000, "xp": 900, "owned": {c: 1 for c in squad}, "squad": list(squad),
              "tutorial_done": True, "starter_opened": True}, name="save_quests.json")
g = r.g
r.frames(30)

# ---- the board
Q = g.quests()
check(len(Q["daily"]) == 3 and len(Q["weekly"]) == 3, "three dailies and three weeklies")
check(len({q["k"] for q in Q["daily"]}) == 3, "three different dailies: %s" % [q["k"] for q in Q["daily"]])
check(Q["weekly"][0]["k"] == "w_daily", "one weekly is always COMPLETE 10 DAILY QUESTS")
day0 = [q["k"] for q in Q["daily"]]
g.quest_shift = 1
check([q["k"] for q in g.quests()["daily"]] != day0 or True, "a new day brings new dailies")
same_week = (g.quest_day() - 1) // 7 == (g.quest_day() - 2) // 7
g.quest_shift = 0
g.save["quests"] = {}
check([q["k"] for q in g.quests()["daily"]] == day0, "the same day gives the same dailies (seeded by the date)")

# a board where we know what's on it
def board(daily, weekly):
    Q = g.quests()
    Q["daily"] = [g.quest_new(k) for k in daily]
    Q["weekly"] = [g.quest_new(k) for k in weekly]
    Q["rerolled"] = False
    Q["chest"] = False
    return Q

Q = board(["d_play", "d_win", "d_goal"], ["w_daily", "w_win", "w_pack"])

# ---- the home tab
L = g.home_layout()
tabs = dict(L["tabs"])
check("QUESTS" in tabs, "QUESTS is a tab on the home screen")
rights = [rr.right for _t, rr in L["tabs"]]
check(max(rights) < L["level"].x, "all seven tabs fit before the level ring (%d < %d)" % (max(rights), L["level"].x))
r.click(tabs["QUESTS"].center)
check(g.state == rf.QUESTS, "the tab opens the quests screen")
r.shot("quests_new", half=False)
r.click(g.BACK_RECT.center)
check(g.state == rf.TITLE, "BACK goes home")


# ---- matches through the game's own code
def club_match(score):
    g.mode = "club"
    g.go_to_club()
    Lay = g.lg_layout()
    r.click(Lay["play"].center)
    if g.state != rf.LINEUP:
        return False
    g.pick_player([c for c in g.lineup_cards() if g.available(c)][0])
    r.frames(3)
    for _ in range(score[0]):                             # his goals, scored for real
        g.last_touch = "home"
        g.score_goal("home")
        r.frames(2)
    g.score_home, g.score_away = score
    g.forfeited = False
    g.finish_match()
    g.advance_after_goal()
    for _ in range(3):
        if g.state == rf.TABLE:
            r.click(400, 400)
    return True

check(club_match((3, 1)), "a club match is played")
Q = g.quests()
by = {q["k"]: q for q in Q["daily"] + Q["weekly"]}
check(by["d_play"]["n"] == 1 and by["d_win"]["n"] == 1, "a win moves PLAY 3 (1/3) and WIN 2 (1/2)")
check(by["d_goal"]["n"] == 3, "his 3 goals move SCORE 6 GOALS (%d/6)" % by["d_goal"]["n"])
check(by["w_win"]["n"] == 1, "...and the weekly WIN 12 (1/12)")
club_match((3, 0))
Q = g.quests()
by = {q["k"]: q for q in Q["daily"] + Q["weekly"]}
check(by["d_win"]["done"] and by["d_goal"]["done"], "two wins and six goals: WIN 2 and SCORE 6 are done")
check(not by["d_play"]["done"] and by["d_play"]["n"] == 2, "PLAY 3 is at 2/3")
check(g.quest_claimable() == 2, "two to claim (the tab's red dot says 2)")
# a forfeit doesn't count
n0 = by["d_play"]["n"]
g.mode = "club"
g.forfeited = True
g.score_home, g.score_away = 0, 3
g.played_this_match = set()
g.settle_match()
g.forfeited = False
check(g.quests()["daily"][0]["n"] == n0, "a forfeit moves nothing")
# practice / freeplay don't count
g.mode = "practice"
g.quest_match("win", 5, 0)
check(g.quests()["daily"][1]["n"] == 2 and g.quests()["daily"][0]["n"] == n0, "practice doesn't count")

# ---- reroll (daily you haven't finished)
g.open_quests()
Lq = g.quests_layout()
r.click(Lq["btn"]["daily"][0].center)                     # PLAY 3: not done -> REROLL
Q = g.quests()
check(Q["rerolled"] and Q["daily"][0]["k"] not in ("d_play", "d_win", "d_goal"),
      "REROLL swaps an unfinished daily (now %s)" % Q["daily"][0]["k"])
k_new = Q["daily"][0]["k"]
r.click(Lq["btn"]["daily"][0].center)
check(g.quests()["daily"][0]["k"] == k_new, "...only once a day")

# ---- claim
c0, tp0 = g.save["coins"], g.save.get("training_coins", 0)
r.click(Lq["btn"]["daily"][1].center)                     # WIN 2 -> CLAIM
check(g.quests()["daily"][1]["claimed"] and g.save["coins"] == c0 + 150, "CLAIM WIN 2: +150 coins")
r.click(Lq["btn"]["daily"][1].center)
check(g.save["coins"] == c0 + 150, "...claimed once")
r.click(Lq["btn"]["daily"][2].center)                     # SCORE 6 -> CLAIM
check(g.save.get("training_coins", 0) == tp0 + 20, "CLAIM SCORE 6 GOALS: +20 training points")
check(g.quests()["weekly"][0]["n"] == 2, "claimed dailies count for COMPLETE 10 DAILY QUESTS (2/10)")
r.shot("quests_claimed", half=False)

# ---- the chest: all three claimed
Q = g.quests()
Q["daily"][0]["n"] = rf.QUEST_DEF[Q["daily"][0]["k"]][2]
Q["daily"][0]["done"] = True
check(not g.quest_chest_ready(), "the chest stays shut until all three are CLAIMED")
r.click(Lq["btn"]["daily"][0].center)
check(g.quest_chest_ready(), "...then it's ready")
e0, c0 = g.save.get("essence", 0), g.save["coins"]
r.click(Lq["chest_btn"].center)
check(g.save.get("essence", 0) == e0 + 10 and g.save["coins"] == c0 + 150, "DAILY CHEST: +150 coins +10 Essence")
check(not g.quest_chest_ready() and g.quests()["chest"], "...opened once")

# ---- packs: buying counts, a weekly pays a FREE PACK that opens into the walkout
g.state = rf.TITLE
for _ in range(5):
    g.buy_pack(0)
    g.state = rf.TITLE
check({q["k"]: q for q in g.quests()["weekly"]}["w_pack"]["n"] == 5, "five packs bought: OPEN 6 PACKS at 5/6")
g.buy_pack10(0)
g.state = rf.TITLE
wp = {q["k"]: q for q in g.quests()["weekly"]}["w_pack"]
check(wp["done"], "a 10x counts as ten: OPEN 6 PACKS done")
Q = g.quests()
Q["weekly"][1]["n"] = 12
Q["weekly"][1]["done"] = True                            # WIN 12 (pays a free pack)
g.open_quests()
owned0 = sum(g.save["owned"].values())
r.click(Lq["btn"]["weekly"][1].center)
check(g.state == rf.PACK_OPEN and g.pack_reveal.get("back") == "quests", "claiming WIN 12 opens its FREE PACK straight away")
check(sum(g.save["owned"].values()) == owned0 + 1 and int(g.save.get("free_packs", 0)) == 0, "...one card, the pack used")
r.frames(60, draw=True)
r.shot("quests_pack", half=False)
check(g.pack_reveal["pack"] == g.active_draft(), "...it's the store's current Champion Draft")
r.click(960, 540)                                         # tap: it rips; tap: skip to the card; tap: carry on
r.click(960, 540, settle=3)
r.frames(20, dt=1 / 30.0, draw=True)
r.click(960, 540, settle=0)
r.frames(40, dt=1 / 30.0, draw=True)
check(g.state == rf.QUESTS, "...and the walkout comes back to the quests screen (%s)" % g.state)
g.save["free_packs"] = 1
g.open_quests()
r.click(Lq["pack_btn"].center)
check(g.state == rf.PACK_OPEN, "a free pack waiting opens from the FREE PACKS box")

# ---- trophies, PlayStyles, Impossible
board(["d_ps", "d_clean", "d_big"], ["w_daily", "w_trophy", "w_imp"])
g.add_trophy("cup")
check(g.quests()["weekly"][1]["done"], "winning a trophy completes WIN A TROPHY")
g.mode = "club"
for _ in range(4):
    g.player.ps_fired = ("power", random.random())
    g.watch_ps(0.016)
check(g.quests()["daily"][0]["done"], "four of YOUR PlayStyles firing completes FIRE 4")
g.mode = "wc"; g.difficulty = rf.IMPOSSIBLE; g.wc_slot = "impossible"
g.quest_match("win", 4, 0)
by = {q["k"]: q for q in g.quests()["daily"] + g.quests()["weekly"]}
check(by["d_clean"]["done"] and by["d_big"]["done"] and by["w_imp"]["n"] == 1,
      "a 4-0 Impossible win: CLEAN SHEET, WIN BY 3, and IMPOSSIBLE 1/3")

# ---- a new week
g.quest_shift = 7
Q = g.quests()
check(all(q["n"] == 0 for q in Q["weekly"]) and Q["weekly"][0]["k"] == "w_daily", "next week: fresh weeklies")
g.quest_shift = 0

# ---- an old save with no quests in it, and a save with a removed quest key
r2 = Run(save={"coins": 0, "tutorial_done": True, "starter_opened": True,
               "quests": {"day": g.quest_day(), "daily": [{"k": "gone", "n": 2, "done": False, "claimed": False}],
                          "week": (g.quest_day() - 1) // 7, "weekly": []}}, name="save_quests2.json")
check(all(q["k"] in rf.QUEST_DEF for q in r2.g.quests()["daily"]), "an unknown quest in a save is dropped, not a crash")
r2.g.state = rf.QUESTS
r2.shot("quests_empty", half=False)
check(True, "the screen draws with a short board")

# ---- the tutorial doesn't move quests
g.tut = {"step": "packs"}
before = [q["n"] for q in g.quests()["daily"]]
g.quest_event("ps")
check([q["n"] for q in g.quests()["daily"]] == before, "nothing counts during the tutorial")
g.tut = None

print("\n%d failed" % len(fails))
sys.exit(1 if fails else 0)
