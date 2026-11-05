import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Run, rf, OUT, pygame
r = Run(save={"coins": 100000, "xp": 5000})
g = r.g
ids = g.lb_ids
fails = []
def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok: fails.append(msg)
want = {"LB_yamal": (121, "A"), "LB_salah": (120, "A"), "LB_dembele": (120, "A"), "LB_haaland": (119, "A"),
        "LB_son": (119, "A"), "LB_isco": (117, "B"), "LB_diomande": (109, "B"), "LB_calhanoglu": (104, "C"),
        "LB_weghorst": (90, "C")}
for cid, (rt, pool) in want.items():
    c = g.cards[cid]
    check(c["rating"] == rt and g.card_pool(c) == pool, "%s shows %d, pool %s (got %d %s)" % (cid, rt, pool, c["rating"], g.card_pool(c)))
check(len(ids) == len(set(ids)) == 56, "56 Limit Breakers cards, Drafts A and B, no id twice")
# ---- Draft B (31 Oct)
want_b = {"LB_vannistelrooy": (122, "A"), "LB_saliba": (119, "A"), "LB_valencia": (116, "B"),
          "LB_ansufati": (109, "B"), "LB_modric": (104, "C"), "LB_schmeichel": (90, "C")}
for cid, (rt, pool) in want_b.items():
    c = g.cards[cid]
    check(c["rating"] == rt and g.card_pool(c) == pool and c["pack"] == rf.LB2_PACK,
          "Draft B: %s shows %d, pool %s" % (cid, rt, pool))
check([len(g.pack_pool(rf.LB2_PACK, p)) for p in "ABC"] == [5, 8, 15], "Draft B: pools 5/8/15 in pack 6")
avg = lambda pk, pl: sum(c["rating"] for c in g.pack_pool(pk, pl)) / float(len(g.pack_pool(pk, pl)))
check(all(abs(avg(rf.LB_PACK, pl) - avg(rf.LB2_PACK, pl)) <= 1.5 for pl in "ABC"),
      "Drafts A and B balanced: pool averages A %.1f/%.1f, B %.1f/%.1f, C %.1f/%.1f"
      % tuple(v for pl in "ABC" for v in (avg(rf.LB_PACK, pl), avg(rf.LB2_PACK, pl))))
check([rf.draft_title(5), rf.draft_title(6)] == ["LIMIT BREAKERS DRAFT A", "LIMIT BREAKERS DRAFT B"],
      "titles: LIMIT BREAKERS DRAFT A / B")
check(g.pack_art[rf.LB2_PACK] is not None, "pack art pack_6 loads")
ps = [p[0]["key"] for p in g.cards["LB_vannistelrooy"]["ps"]]
check(ps == ["clinical", "power"], "Van Nistelrooy's signature PlayStyles: %s" % ps)
check(all(not g.cards[c]["ps"] for c in ids if g.card_pool(g.cards[c]) == "C"), "Draft B pool C: no PlayStyles either")
check([len(g.pack_pool(rf.LB_PACK, p)) for p in "ABC"] == [5, 8, 15], "pools 5/8/15 in pack 5")
check(all(c["pack"] != rf.LB_PACK for c in g.cards.values() if not c["id"].startswith("LB_")), "no other card leaks into pack 5")
check(all(cid in g.card_figs for cid in ids), "every LB card has its figure")
check(all(all(g.sig_looks[cid].get(p) is not None for p in ("head", "torso", "arm", "leg")) for cid in ids), "every LB card has match sprites")
check(all(g.card_flag(g.cards[cid]) is not None for cid in ids), "every LB card has a flag")
check(g.card_template_key(g.cards["LB_yamal"]) == "lb" and g.card_template_key(g.cards["LB_isco"]) == "lb"
      and g.card_template_key(g.cards["LB_maguire"]) == "lbc", "template keys lb / lb / lbc")
for k in ("lb", "lbframe", "lbc", "lbcframe"):
    t = g.card_template(k, 340, 472)
    check(t is not None, "template %s loads" % k)
check(g.pack_art[rf.LB_PACK] is not None, "pack art pack_5 loads")
check(g.lb_badge is not None, "lb badge loads")
check(rf.lb_raw(121) and rf.ovr(rf.lb_raw(121)) == 121, "lb_raw inverts ovr")
# pool A/B PlayStyles, pool C none
check(all(not g.cards[c]["ps"] for c in ids if g.card_pool(g.cards[c]) == "C"), "pool C has no PlayStyles")
check(len(g.cards["LB_yamal"]["ps"]) == 2, "pool A has two PlayStyles")
# layout: six pack rows above the Game Box button
rows = g.packs_layout(); box = g.packs_ui()["box"]
check(len(rows) == len(g.store_packs()) == 3 and rows[-1].bottom < box.y,
      "the store's three rows (Champion Drafts share one, Limit Breakers A and B another, No. 10 retired) fit")
# ---- 1 Nov: Limit Breakers A and B rotate too - one in the store, ten minutes each
import time as _time
hour = (int(_time.time() // 3600) + 1) * 3600
seq = []
for k in range(3):
    g.draft_offset = hour + k * rf.DRAFT_ROTATE + 5 - _time.time()
    seq.append(g.shown_pack(rf.LB_PACK))
check(seq == [rf.LB_PACK, rf.LB2_PACK, rf.LB_PACK], "Limit Breakers: A, then B, then A again: %s" % seq)
g.draft_offset = hour + rf.DRAFT_ROTATE + 5 - _time.time()     # Draft B's turn
coins0 = g.save["coins"]
check(not g.buy_pack(rf.LB_PACK) and g.save["coins"] == coins0 and g.view_pack == rf.LB2_PACK,
      "while B is in, A can't be bought - the store goes to B")
check(g.shown_pack(len(rf.PACK_NAMES) - 1) == rf.LB2_PACK, "the home screen's NEW tile shows the one that's in")
g.draft_offset = hour + 5 - _time.time()                         # back to A for the rest of the checks
check(g.shown_pack(rf.LB2_PACK) == rf.LB_PACK, "and A is back")
# draw every card big, into a sheet
W, H = 340, 472
sheet = pygame.Surface((7 * (W + 40), 4 * (H + 80)))
sheet.fill((14, 4, 8))
for i, cid in enumerate(ids):
    rect = pygame.Rect(30 + (i % 7) * (W + 40), 40 + (i // 7) * (H + 80), W, H)
    g.draw_card(sheet, g.cards[cid], rect)
sheet.im.convert("RGB").save(os.path.join(OUT, "lb_cards.png"))
# small sizes too (collection grid / pack banner)
small = pygame.Surface((7 * 170, 4 * 230)); small.fill((14, 4, 8))
for i, cid in enumerate(ids):
    g.draw_card(small, g.cards[cid], pygame.Rect(10 + (i % 7) * 170, 10 + (i // 7) * 230, 150, 208))
small.im.convert("RGB").save(os.path.join(OUT, "lb_small.png"))
# the pack store on pack 5
g.state = rf.PACKS if hasattr(rf, "PACKS") else g.state
g.view_pack = rf.LB_PACK
r.shot("lb_store", half=False)
# open packs until we see A, B and C
import random
random.seed(3)
seen = {}
for n in range(400):
    g.save["coins"] = 100000
    g.buy_pack(rf.LB_PACK)
    pr = g.pack_reveal
    seen.setdefault(pr["tier"], pr["card"]["id"])
    if len(seen) == 3:
        break
check(set(seen) == {"A", "B", "C"}, "packs give A, B and C: %s" % seen)
for tier in "ABC":
    g.pack_reveal = {"card": g.cards[seen[tier]], "t": 0.0, "count": 1, "pack": rf.LB_PACK, "tier": tier, "opened": True}
    g.state = rf.PACK_OPEN
    for k in range(60 * 9):
        pygame.time.advance(1000 / 60.0)
        g.pack_reveal["t"] += 1 / 60.0
        if k % 30 == 0:
            g.draw()
    r.shot("lb_reveal_%s" % tier, half=False)
print("FAILS:", len(fails))

sys.exit(1 if fails else 0)
