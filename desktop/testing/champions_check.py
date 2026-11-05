"""Champion Draft A (28 Oct): pack 1 renamed, Hubi's thirteen players with their numbers, seven in
pool A (Palmer came later) and six in pool B, each on the gold Champions card in his own club's colours.
Writes champ_cards.png, champ_small.png, champ_store.png and champ_reveal_A/B.png to out/."""
import os
import random
import sys

import harness
import pygame

rf = harness.rf
OUT = harness.OUT
fails = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


r = harness.Run()
g = r.g
check(rf.PACK_NAMES[1] == "CHAMPION DRAFT A", "pack 1 is called CHAMPION DRAFT A")
check([rf.draft_title(i) for i in (1, 2, 3)] == ["CHAMPION DRAFT A", "CHAMPION DRAFT B", "CHAMPION DRAFT C"]
      and rf.draft_title(4) == "NO. 10 PACK DRAFT", "the club packs are Champion Drafts A, B and C (no DRAFT twice)")
check(all(rf.PACK_TAGS[i] == "CHAMPIONS" for i in (1, 2, 3)), "all three are tagged CHAMPIONS")
# 31 Oct, balance: Al Nassr moved to Draft B - every draft has two 121+ headliners in pool A
stars = {p: [c["id"] for c in g.pack_pool(p, "A") if c["rating"] >= 121] for p in (1, 2, 3)}
check(all(len(v) == 2 for v in stars.values()) and "ALN_ronaldo" in stars[2] and "INT_messi" in stars[3]
      and "BAR_yamal" in stars[3], "two headliners a draft: %s" % stars)
check(all(c["pack"] == 2 for c in g.cards.values() if c["kind"] == "club" and c["team"] == "ALN"),
      "all of Al Nassr is in Draft B (the club isn't split)")
# 31 Oct: the Champion Drafts rotate - one in the store at a time, ten minutes each, on the real clock
import time as _time
def at_clock(sec):                                   # put the draft clock at `sec` into a rotation cycle
    base = (int(_time.time() // (6 * rf.DRAFT_ROTATE)) + 1) * 6 * rf.DRAFT_ROTATE   # (an hour: every group at A)
    g.draft_offset = base + sec - _time.time()
order = []
for k in range(4):
    at_clock(k * rf.DRAFT_ROTATE + 5)
    order.append(g.active_draft())
check(order == [1, 2, 3, 1], "A, then B, then C, then A again: %s" % order)
at_clock(rf.DRAFT_ROTATE - 92.2)
check(g.draft_left_text() == "1:33" and g.next_draft() == 2, "the countdown (%s) and what's next" % g.draft_left_text())
check(len(g.store_packs()) == len(rf.PACK_NAMES) - sum(len(grp) - 1 for grp in rf.ROTATIONS) - len(rf.RETIRED_PACKS)
      and sum(p in rf.DRAFT_PACKS for p in g.store_packs()) == 1,
      "the store lists one Champion Draft: %s" % g.store_packs())
coins0 = g.save["coins"] = 5000
g.state = rf.PACKS
check(not g.buy_pack(3) and not g.buy_pack10(2) and g.save["coins"] == coins0,
      "a draft that has rotated out can't be bought")
check(g.view_pack == 1, "...and the store shows the one that's in")
g.toasts = []
g.open_packs(1)
r.frames(5)
r.shot("store_draft_rotating", half=False)
at_clock(rf.DRAFT_ROTATE + 3)                         # ten minutes later, still on the page
g.draw()
check(g.view_pack == 2 and any("DRAFT B IS IN" in str(t) for t in g.toasts),
      "it rotates while you look: the page switches to Draft B and says so")
check(g.buy_pack(2) and g.state == rf.PACK_OPEN, "Draft B can be bought now")
g.state = rf.PACKS
g.draft_offset = 0.0
# 1 Nov: the No. 10 pack is retired - not in the store, can't be bought, cards kept by their owners
no10 = [c["id"] for c in g.cards.values() if c["pack"] == rf.NO10_PACK]
check(rf.NO10_PACK in rf.RETIRED_PACKS and rf.NO10_PACK not in g.store_packs(), "the No. 10 pack is not in the store")
g.save["coins"] = 5000
check(not g.buy_pack(rf.NO10_PACK) and not g.buy_pack10(rf.NO10_PACK) and g.save["coins"] == 5000
      and g.view_pack != rf.NO10_PACK, "and can't be bought")
total0 = len(g.collection_ids())
check(total0 == len(g.cards) - len(no10), "the collection counts only cards you can still get (%d)" % total0)
g.save["owned"][no10[0]] = 1
check(len(g.collection_ids()) == total0 + 1 and no10[0] in g.cards, "a No. 10 card you own is kept and counted")
del g.save["owned"][no10[0]]
g.view_pack = rf.NO10_PACK
g.state = rf.PACKS
g.draw()
check(g.view_pack != rf.NO10_PACK, "an old save pointing at it lands on a pack that's on sale")
want = {"CRY_guehi": (124, "CB", "MCI", "ENG"), "ARS_saka": (121, "RW", "ARS", "ENG"),
        "CHE_palmer": (120, "CAM", "CHE", "ENG"),
        "AST_martinez": (120, "GK", "AST", "ARG"), "ARS_gyokeres": (119, "ST", "ARS", "SWE"),
        "CHE_caicedo": (119, "CDM", "CHE", "ECU"), "CHE_joaopedro": (119, "ST", "CHE", "BRA"),
        "CHE_enzo": (118, "CM", "CHE", "ARG"), "BOU_semenyo": (118, "LW", "MCI", "GHA"),
        "ARS_odegaard": (117, "CM", "ARS", "NOR"), "BOU_kluivert": (108, "ST", "BOU", "NET"),
        "BOU_evanilson": (103, "ST", "BOU", "BRA"), "BRE_wissa": (87, "ST", "BRE", "COD")}
A, B = g.pack_pool(1, "A"), g.pack_pool(1, "B")
check([c["id"] for c in A] == list(want)[:7], "pool A is the seven: %s" % [c["id"] for c in A])
check([c["id"] for c in B] == list(want)[7:], "pool B is the six: %s" % [c["id"] for c in B])
for cid, (ovr, pos, team, nat) in want.items():
    c = g.cards[cid]
    check((c["rating"], c["pos"], c["team"], c["nation"]) == (ovr, pos, team, nat),
          "%s %d %s %s %s" % (cid, c["rating"], c["pos"], c["team"], c["nation"]))
    check(g.card_template_key(c) == "champ_" + team, "%s wears the %s Champions card" % (cid, team))
    check(cid in g.card_figs, "%s has a posed figure" % cid)
    check(g.card_flag(c) is not None, "%s shows a flag" % cid)
check(all(c["design"] != "champions" for c in g.pack_pool(1, "C")), "pool C keeps the old card")
check(g.cards["CHE_palmer"]["pack"] == 1 and g.card_pool(g.cards["CHE_palmer"]) == "A", "Palmer is in pool A")
check(g.cards["CRY_guehi"]["number"] == 15 and g.cards["BOU_semenyo"]["number"] == 42, "City numbers 15 and 42")
# the match look: both are City players now, in sky blue
mci = [p for code, _n, _s, p in rf.CLUBS if code == "MCI"][0]
for cid in ("CRY_guehi", "BOU_semenyo"):
    c = g.cards[cid]
    slug = cid.split("_", 1)[1]
    check(mci[c["slot"]] == slug, "%s sits in City's roster at slot %d" % (cid, c["slot"]))
    look = g.card_original_look(c) if hasattr(g, "card_original_look") else None
    check(look is not None and all(v is not None for v in look.values()), "%s has City match sprites" % cid)
for cid in ("BOU_evanilson", "BOU_kluivert"):
    c = g.cards[cid]
    bou = [p for code, _n, _s, p in rf.CLUBS if code == "BOU"][0]
    check(bou[c["slot"]] == cid.split("_", 1)[1], "%s still finds his Bournemouth sprites" % cid)
# pictures
W, H = 252, 398
sheet = pygame.Surface((7 * (W + 50) + 40, 2 * (H + 90) + 40))
sheet.fill((14, 16, 24))
for i, c in enumerate(A + B):
    row, col = (0, i) if i < 7 else (1, i - 7)
    g.draw_card(sheet, c, pygame.Rect(50 + col * (W + 50), 50 + row * (H + 90), W, H))
sheet.im.convert("RGB").save(os.path.join(OUT, "champ_cards.png"))
small = pygame.Surface((7 * 170 + 20, 2 * 230 + 20))
small.fill((14, 16, 24))
for i, c in enumerate(A + B):
    row, col = (0, i) if i < 7 else (1, i - 7)
    g.draw_card(small, c, pygame.Rect(20 + col * 170, 14 + row * 230, 140, 208))
small.im.convert("RGB").save(os.path.join(OUT, "champ_small.png"))
at_clock(5)                                           # Draft A in the store (they rotate)
g.state = rf.PACKS
g.view_pack = 1
r.shot("champ_store", half=False)
random.seed(5)
seen = {}
for n in range(600):
    g.save["coins"] = 100000
    g.buy_pack(1)
    pr = g.pack_reveal
    seen.setdefault(pr["tier"], pr["card"]["id"])
    if len(seen) == 3:
        break
check(set(seen) == {"A", "B", "C"}, "packs give A, B and C: %s" % seen)
for tier in "AB":
    g.pack_reveal = {"card": g.cards[seen[tier]], "t": 0.0, "count": 1, "pack": 1, "tier": tier, "opened": True}
    g.state = rf.PACK_OPEN
    for k in range(60 * 9):
        pygame.time.advance(1000 / 60.0)
        g.pack_reveal["t"] += 1 / 60.0
        if k % 30 == 0:
            g.draw()
    r.shot("champ_reveal_%s" % tier, half=False)
print("FAILS:", len(fails))
sys.exit(1 if fails else 0)
