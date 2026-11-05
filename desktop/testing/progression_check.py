"""Training points, feeding, gem ranks and skill points - clicked through the real screen."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Run, rf, OUT, pygame
fails = []
def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok: fails.append(msg)

T = "LB_isco"                       # the card we train (pool B, 117)
r = Run(save={"tutorial_done": True, "training_coins": 800, "puzzle_points": 200,
              "owned": {T: 1, "LB_weghorst": 2, "LB_tadic": 1, "LB_maguire": 1, "LB_yamal": 1},
              "squad": ["LB_yamal"], "starter_opened": True})
g = r.g
base = dict(g.cards[T])
check(sum(rf.LEVEL_XP) == 4640 and rf.card_level(0)[0] == 1 and rf.card_level(4640)[0] == 30
      and rf.card_level(4639)[0] == 29, "the level curve: 1 -> 30 over %d XP" % sum(rf.LEVEL_XP))
check(rf.level_stat_bonus(1) == 0 and rf.level_stat_bonus(30) == 10, "level 1 = +0, level 30 = +10 every stat")
check(g.upgraded(g.cards[T]) is g.cards[T], "an untouched card is drawn as it is")
# ---- open the card, UPGRADE tab
g.card_detail = g.cards[T]; g.card_tab = 0
back, tabs, panel = g.card_view_layout()
check(len(tabs) == 5 and g.CV_TABS[4] == "UPGRADE", "the player screen has a fifth tab, UPGRADE")
r.click(tabs[4].center)
check(g.card_tab == 4, "UPGRADE opens")
r.shot("prog_tab_fresh", half=False)
L = g.upgrade_layout(g.CV_PANEL)
tp0 = g.save["training_coins"]
r.click(L["one"].center)
check(g.card_lvl(g.cards[T])[0] == 2 and tp0 - g.save["training_coins"] == g.tp_for(g.cards[T], 1) + 24,
      "+1 LEVEL: level 2 for %d training points" % (tp0 - g.save["training_coins"]))
r.click(L["max"].center)
lvl = g.card_lvl(g.cards[T])[0]
check(lvl > 2 and g.tp_for(g.cards[T], lvl + 1) > g.save["training_coins"],
      "AS FAR AS I CAN: level %d, %d points left (not enough for %d)" % (lvl, g.save["training_coins"], lvl + 1))
v = g.upgraded(g.cards[T])
check(v["rating"] == base["rating"], "levels never touch the overall (%d)" % v["rating"])
check(all(v["stats"][k] == min(rf.STAT_CEIL, base["stats"][k] + rf.level_stat_bonus(lvl)) for k in rf.STAT_KEYS),
      "every stat +%d at level %d" % (rf.level_stat_bonus(lvl), lvl))
check(g.cards[T]["stats"] == base["stats"] and g.cards[T]["rating"] == base["rating"],
      "the table's card is untouched (a CPU Isco plays as he comes out of the pack)")
# ---- feed
fl = [c["id"] for c, n in g.feed_list(g.cards[T])]
check("LB_yamal" not in fl and T not in fl, "squad players and the card itself can't be fed")
check("LB_weghorst" in fl and "LB_tadic" in fl, "spares and non-squad cards can")
xp0 = g.prog(T)["xp"]
r.click(L["feed"].center)
check(g.feed_ui is not None, "FEED A PLAYER opens the picker")
r.shot("prog_feed_pick", half=False)
first = g.feed_list(g.cards[T])[0][0]
r.click(L["cards"][0].center)
check(g.feed_ui["pick"]["id"] == first["id"], "picking a card asks first")
r.shot("prog_feed_confirm", half=False)
r.click(L["no"].center)
check(g.feed_ui["pick"] is None and g.save["owned"].get(first["id"]), "CANCEL keeps him")
r.click(L["cards"][0].center); r.click(L["yes"].center)
gain = g.prog(T)["xp"] - xp0
check(gain == rf.feed_xp(first), "FEED: +%d XP (%s, rated %d)" % (gain, first["name"], first["rating"]))
check(g.save["owned"].get(first["id"], 0) == (1 if first["id"] == "LB_weghorst" else 0), "...and one copy of him is gone")
r.key(pygame.K_ESCAPE)
check(g.feed_ui is None and g.card_detail is not None, "Esc closes the picker, not the player")
# ---- gem
pz0 = g.save["puzzle_points"]
for i in range(5):
    r.click(L["rank"].center)
check(g.prog(T)["rank"] == 5 and pz0 - g.save["puzzle_points"] == sum(rf.RANK_COST),
      "five upgrades grey -> gold for %d puzzle points" % sum(rf.RANK_COST))
r.click(L["rank"].center)
check(g.prog(T)["rank"] == 5, "no sixth upgrade")
v = g.upgraded(g.cards[T])
check(v["rating"] == base["rating"] + 5 and g.card_pool(v) == g.card_pool(base),
      "gold gem: overall %d -> %d, still pool %s" % (base["rating"], v["rating"], g.card_pool(v)))
check(g.skill_left(g.cards[T]) == 5, "five skill points to spend")
pas = [row for key, row, plus in L["skills"] if key == "pass"][0]
plus = [plus for key, row, plus in L["skills"] if key == "pass"][0]
for i in range(5):
    r.click(plus.center)
check(g.prog(T)["skill"]["pass"] == 4 and g.skill_left(g.cards[T]) == 1, "PASSING stops at level 4 (one point left)")
dplus = [plus for key, row, plus in L["skills"] if key == "drib"][0]
r.click(dplus.center)
v = g.upgraded(g.cards[T])
lv = g.card_lvl(g.cards[T])[0]
want = min(rf.STAT_CEIL, base["stats"]["pass"] + rf.level_stat_bonus(lv) + 5 + 20)
check(v["stats"]["pass"] == want, "PASSING %d -> %d (+%d level, +5 gem, +20 skill)" % (base["stats"]["pass"], v["stats"]["pass"], rf.level_stat_bonus(lv)))
check(g.skill_left(g.cards[T]) == 0, "all points spent")
r.shot("prog_tab_gold", half=False)
# ---- the card face shows the gem and the new overall, and the cache noticed
s = pygame.Surface((420, 560)); s.fill((14, 4, 8))
g.blit_card(s, g.cards[T], pygame.Rect(40, 40, 340, 472))
s.im.convert("RGB").save(os.path.join(OUT, "prog_card_gold.png"))
check(g.prog_sig(g.cards[T]) is not None, "card faces are cached per rank and level")
# ---- the doll in a match uses your version, the CPU's copy doesn't
g.card_detail = None
g.player.set_stats(g.upgraded(g.cards[T]))
check(g.player.stat["pass"] == v["stats"]["pass"], "your player takes the field with the upgraded stats")
g.cpu.set_stats(g.cards[T])
check(g.cpu.stat["pass"] == base["stats"]["pass"], "the CPU's Isco doesn't")
# ---- match reward
g.mode = "club"; g.score_home, g.score_away = 2, 1; g.forfeited = False
pz = g.save["puzzle_points"]
g.settle_match()
check(g.save["puzzle_points"] - pz == rf.PUZZLE_REWARD["win"], "a win pays +%d puzzle points" % rf.PUZZLE_REWARD["win"])
g.forfeited = True; pz = g.save["puzzle_points"]
g.settle_match()
check(g.save["puzzle_points"] == pz, "a forfeit pays none")
# ---- save round trip, and the last copy taking its progress with it
g.write_save()
r2 = Run(save=None, keep=True)
g2 = r2.g
check(g2.prog(T)["rank"] == 5 and g2.prog(T)["skill"]["pass"] == 4 and g2.card_lvl(g2.cards[T])[0] == lv,
      "the save keeps level %d, gold, and the skill points" % lv)
g2.exchange_card(g2.cards[T])
check(g2.prog(T) is None, "exchanging the last copy takes its progress with it")
# ---- the screen for a card you don't own
g2.card_detail = g2.cards["LB_salah"]; g2.card_tab = 4
r2.shot("prog_tab_not_owned", half=True)
print("\n%s (%d failed)" % ("ALL PASSED" if not fails else "FAILED", len(fails)))
for f in fails: print("   -", f)

sys.exit(1 if fails else 0)
