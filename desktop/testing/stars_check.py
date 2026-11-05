"""STAR SIGNINGS (1 Nov). The cards: the 41 legends wear the new GOLD CRYSTAL card (148+), the WORLD CUP flag
card (143-147) or their CLUB's Champions card (135-142), each as a posed figure. The market: every player in
the game for Star Points - sort, watchlist, SEARCH (typed through the real keyboard events), signing into
the walkout - and MY PLAYERS: select, AUTO SELECT, RELEASE.

    python3 stars_check.py      (pictures: out/stars_*.png)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Run, rf, pygame

fails = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


squad = ["ARS_saka", "CHE_caicedo", "AST_martinez", "BRE_wissa", "BOU_evanilson"]
owned = {"ARS_saka": 3, "CHE_caicedo": 2, "AST_martinez": 1, "BRE_wissa": 1, "BOU_evanilson": 1,
         "STAR_pele": 1, "STAR_gullit": 1, "STAR_pirlo": 1, "LB_yamal": 2, "WC_ARG_messi": 1, "WG_messi": 1}
r = Run(save={"coins": 0, "star_points": 1000000, "tutorial_done": True, "starter_opened": True,
              "owned": owned, "squad": list(squad)}, name="save_stars.json")
g = r.g
ids = ["STAR_" + row[0] for row in rf.STAR_SIGNINGS]
check(len(ids) == 41, "41 Star Signings")

# ================================================================== THE CARDS
looks = [rf.STAR_LOOK[c] for c in ids]
n = {k: looks.count(k) for k in ("gold", "wc", "club")}
check(n == {"gold": 9, "wc": 15, "club": 17}, "9 gold, 15 World Cup, 17 club: %s" % n)
raw = {"STAR_" + row[0]: row[3] for row in rf.STAR_SIGNINGS}
check(all((raw[c] >= 148) == (rf.STAR_LOOK[c] == "gold") for c in ids), "gold is exactly the 148+ legends")
missing = [c for c in ids if c not in g.card_figs]
check(not missing, "all 41 have a posed figure (missing: %s)" % missing)
wrong = []
for c in ids:
    k, look, card = g.star_key(g.cards[c]), rf.STAR_LOOK[c], g.cards[c]
    want = {"gold": "stargold", "wc": "flag_" + card["nation"], "club": "champ_" + card["team"]}[look]
    if k != want:
        wrong.append((c, k, want))
check(not wrong, "each wears his tier's card: %s" % (wrong or "ok"))
for club in ("RMA", "BAY", "JUV", "MIL"):
    check(rf.find_sprite("tpl_champ_%s_card" % club) and rf.find_sprite("champpen_%s" % club),
          "the new %s club card and its pennants are there" % club)
a = g.card_template("stargold", 262, 361)
b = g.card_template("stargoldframe", 262, 361)
check(a is not None and b is not None and a[0].get_size() == b[0].get_size() and a[1:3] == b[1:3],
      "the gold card and its frame line up")
errs = []
for c in ids:
    for size in ((120, 166), (262, 361), (380, 524)):
        try:
            w = pygame.Surface((size[0] + 200, size[1] + 200), pygame.SRCALPHA)
            g.blit_card(w, g.cards[c], pygame.Rect(100, 100, *size))
        except Exception as e:                            # pragma: no cover
            errs.append((c, size, repr(e)))
check(not errs, "every legend's card draws at three sizes (%s)" % (errs[:2] or "ok"))
g.card_figs.discard("STAR_kaka")
g._star_ok.pop("STAR_kaka", None)
check(g.star_key(g.cards["STAR_kaka"]) == "star", "with no figure a legend keeps the purple card")
g.card_figs.add("STAR_kaka")
g._star_ok.pop("STAR_kaka", None)

# ================================================================== THE MARKET
cat = g.ss_catalogue()
cat_ids = {c["id"] for c in cat}
want = [c for c in g.cards.values() if c["kind"] != "wg" and c["id"] not in rf.NO_EXCHANGE]
check(len(cat) == len(want) and not any(c["kind"] == "wg" for c in cat)
      and not any(cid in cat_ids for cid in rf.BOX_CARDS),
      "every player is for sale (%d) but the World's Game and the Game Box cards" % len(cat))
check(all(c["id"] in cat_ids for c in g.cards.values() if c["kind"] in ("club", "wc", "lb", "no10", "star", "rookie")),
      "...club, World Cup, Limit Breakers, No. 10, legends and rookies all in it")
check(g.sign_price(g.cards["STAR_pele"]) == 300000, "a legend costs 3x his listed price (Pele 300,000)")
loop = [c["id"] for c in cat if g.can_exchange(c) and g.sign_price(c) <= rf.star_points_for(c["rating"])]
check(not loop, "signing always costs more than releasing - no loop (%s)" % loop[:3])
check(min(g.sign_price(c) for c in cat) >= rf.SIGN_MIN, "nothing under %d SP" % rf.SIGN_MIN)
# 5 Nov: 80-119 capped (SIGN_CAP), 120+ untouched
band = [c for c in cat if 100 <= c["rating"] <= 119]
check(band and max(g.sign_price(c) for c in band) <= 40000 and
      max(g.sign_price(c) for c in band if c["rating"] == min(x["rating"] for x in band)) <= 15000 + 100 * 0,
      "100-119 cost 15,000-40,000 SP (top of the band %s)" % g.fmt(max(g.sign_price(c) for c in band)))
top = [c for c in cat if c["rating"] >= 120]
check(min(g.sign_price(c) for c in top) > 100000, "120+ keep their prices (cheapest %s)" % g.fmt(min(g.sign_price(c) for c in top)))
by = sorted((c["rating"], g.sign_price(c)) for c in cat if c["rating"] < 120 and not c.get("price"))
check(all(by[i][1] <= by[i + 1][1] for i in range(len(by) - 1) if by[i][0] < by[i + 1][0]),
      "below 120 a better card never costs less")

# the screen, through the store
g.open_store()
r.frames(5)
tiles = dict(zip([t[0] for t in g.STORE_TILES], g.store_layout()))
r.click(tiles["stars"].center)
check(g.state == rf.STARS and g.ss()["tab"] == "players", "the store's STAR SIGNINGS tile opens PLAYERS")
r.shot("stars_players", half=False)
L = g.ss_layout()
first = L["grid"][0][0]
check(first["rating"] == max(c["rating"] for c in cat), "sorted OVR high to low (%s %d first)" % (first["name"], first["rating"]))
check(len(L["grid"]) == 10, "ten players on screen")
# scroll
r0 = g.ss()["scroll"]
pygame.event.post(pygame.event.Event(pygame.MOUSEWHEEL, y=-1, x=0))
r.frames(2)
check(g.ss()["scroll"] == r0 + 1, "the wheel scrolls a row")
g.ss()["scroll"] = 0
# sort dropdown
r.click(L["sort"].center)
check(g.ss()["dropdown"], "the sort box opens")
r.click(L["sort_opts"][3].center)
L = g.ss_layout()
prices = [g.sign_price(c) for c, _r in L["grid"]]
check(g.ss()["sort"] == 3 and prices == sorted(prices) and prices[0] == min(g.sign_price(c) for c in cat),
      "PRICE LOW - HIGH: cheapest first (%s)" % prices[:3])
g.ss()["sort"] = 0
L = g.ss_layout()
# watchlist
tile_card, tile = L["grid"][1]
r.click(g.ss_star_rect(tile).center)
check(tile_card["id"] in g.save.get("watchlist", []), "the star on a player puts him on the watchlist")
r.click(L["watch"].center)
check(g.ss()["watch_only"] and [c["id"] for c in g.ss_players()] == [tile_card["id"]], "WATCHLIST shows only him")
r.shot("stars_watch", half=False)
r.click(L["watch"].center)
check(not g.ss()["watch_only"], "...and off again")

# ---- SEARCH, typed for real
def type_text(txt):
    for ch in txt:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=0, unicode=ch))
    r.frames(2)

def press(key):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key, unicode=""))
    r.frames(2)

r.click(L["search"].center)
check(g.ss()["modal"] is not None, "SEARCH opens the search box")
M = g.ss_modal_layout()
r.click(M["name"].center)
type_text("ronalx")
check(g.ss()["modal"]["draft"]["name"] == "ronalx", "typing goes into PLAYER NAME")
press(pygame.K_BACKSPACE)
type_text("d")
check(g.ss()["modal"]["draft"]["name"] == "ronald", "BACKSPACE deletes (ronald)")
r.click(M["min"].center)
type_text("12a0")                                          # letters are ignored in a number box
check(g.ss()["modal"]["draft"]["min"] == "120", "OVR MIN takes digits only (120)")
r.click(M["stars"][2].center)
check(g.ss()["modal"]["draft"]["skill"] == 3, "three skill-move stars")
r.shot("stars_search", half=False)
r.click(M["go"].center)
found = g.ss_players()
check(g.ss()["modal"] is None and found and all("ronald" in c["name"].lower() and c["rating"] >= 120
                                                  and g.card_skill(c) >= 3 for c in found),
      "SEARCH: every result fits (%s)" % [c["name"] for c in found])
check(any(c["id"] == "STAR_ronaldinho" for c in found) or not any(
      "ronald" in c["name"].lower() for c in cat if c["rating"] >= 120 and g.card_skill(c) >= 3), "...and the right ones are there")
L = g.ss_layout()
r.click(L["clear"].center)
check(g.ss_active(g.ss()["filters"]) == 0 and len(g.ss_players()) == len(cat), "CLEAR FILTERS shows everyone again")
# pickers
r.click(L["search"].center)
r.click(M["edit_team"].center)
check(g.ss()["modal"]["picker"] == "team", "the TEAM pencil opens the team list")
panel, btns = g.ss_picker_layout("team")
bar = [b for b in btns if b[0] == "BAR"][0]
r.shot("stars_picker", half=False)
r.click(bar[2].center)
r.click(M["edit_pos"].center)
panel, btns = g.ss_picker_layout("pos")
r.click([b for b in btns if b[0] == "ST"][0][2].center)
r.click(M["edit_program"].center)
panel, btns = g.ss_picker_layout("program")
r.click([b for b in btns if b[0] == "STAR SIGNING"][0][2].center)
press(pygame.K_RETURN)
found = g.ss_players()
check({c["id"] for c in found} == {"STAR_suarez"}, "TEAM Barcelona + ST + STAR SIGNING: Suarez (%s)" % [c["id"] for c in found])
r.click(g.ss_layout()["search"].center)
r.click(M["reset"].center)
check(g.ss_active(g.ss()["modal"]["draft"]) == 0, "RESET ALL empties the box")
press(pygame.K_ESCAPE)
check(g.ss()["modal"] is None and g.state == rf.STARS, "Esc closes the box (and stays on the screen)")
g.ss()["filters"] = g.ss_blank()

# ---- signing: a club player you don't have, then a legend you do
target = g.cards["MCI_haaland"] if "MCI_haaland" in g.cards else [c for c in cat if c["id"] not in owned][0]
g.ss()["filters"]["name"] = target["name"]
L = g.ss_layout()
tcard, tr = [(c, rr) for c, rr in L["grid"] if c["id"] == target["id"]][0]
sp0 = g.star_points()
r.click(tr.center)
r.frames(40)                                               # (the single click waits out a double-click)
check(g.store_confirm is not None and g.store_confirm["ok"] == "SIGN", "tapping a player asks SIGN %s?" % target["name"])
r.shot("stars_confirm", half=False)
_p, ok, _c = g.store_confirm_layout()
r.click(ok.center)
check(g.state == rf.PACK_OPEN and g.pack_reveal["card"]["id"] == target["id"], "SIGN: he walks out")
check(g.star_points() == sp0 - g.sign_price(target) and g.save["owned"].get(target["id"]) == 1,
      "...for %s SP, and he's yours" % g.fmt(g.sign_price(target)))
r.click(960, 540)
r.click(960, 540, settle=3)
r.frames(20, dt=1 / 30.0, draw=True)
r.click(960, 540, settle=0)
r.frames(40, dt=1 / 30.0, draw=True)
check(g.state == rf.STARS, "after the walkout: back to Star Signings (%s)" % g.state)
g.ss()["filters"] = g.ss_blank()
check(g.sign_star(g.cards["STAR_pele"]) and g.save["owned"]["STAR_pele"] == 2, "a legend you own: another copy")
g.state = rf.STARS
g.save["star_points"] = 10
g.store_confirm = None
g.ask_signing(g.cards["STAR_r9"])
check(g.store_confirm is None, "not enough Star Points: no sale")
check(not g.sign_star(g.cards["WG_messi"]), "the World's Game can't be signed here")
g.save["star_points"] = 1000000

# ================================================================== MY PLAYERS
L = g.ss_layout()
r.click(L["tabs"][1][1].center)
check(g.ss()["tab"] == "mine", "MY PLAYERS tab")
mine_ids = [c["id"] for c in g.ss_mine()]
check(set(mine_ids) == {c for c, n in g.save["owned"].items() if n > 0}, "every card you own is there")
L = g.ss_layout()
r.click(L["auto"].center)
sel = dict(g.ss()["sel"])
check(sel == {"ARS_saka": 2, "CHE_caicedo": 1, "LB_yamal": 1}, "AUTO SELECT: duplicates only, legends left (%s)" % sel)
n_sel, sp_sel = g.ss_release_total()
r.shot("stars_mine", half=False)
sp0 = g.star_points()
r.click(L["release"].center)
check(g.store_confirm is not None and g.store_confirm["ok"] == "RELEASE", "RELEASE asks first")
_p, ok, _c = g.store_confirm_layout()
r.click(ok.center)
check(g.star_points() == sp0 + sp_sel and g.save["owned"]["ARS_saka"] == 1 and g.save["owned"]["LB_yamal"] == 1,
      "RELEASE: +%s SP, one copy of each kept" % g.fmt(sp_sel))
check(g.ss()["sel"] == {}, "...and the selection clears")
# one tap selects a single card (all of it), an IN LINEUP card won't select
L = g.ss_layout()
tile = [rr for c, rr in L["grid"] if c["id"] == "WC_ARG_messi"][0]
r.click(tile.center)
r.frames(40)
check(g.ss()["sel"] == {"WC_ARG_messi": 1}, "tapping a player selects him")
lineup = [rr for c, rr in L["grid"] if c["id"] == "AST_martinez"][0]
r.click(lineup.center)
r.frames(40)
check("AST_martinez" not in g.ss()["sel"], "an IN LINEUP player can't be selected")
locked = [rr for c, rr in L["grid"] if c["id"] == "STAR_gullit"][0]
r.click(locked.center)
r.frames(40)
check("STAR_gullit" not in g.ss()["sel"], "a legend is LOCKED")
r.click(tile.center)
r.frames(40)
check(g.ss()["sel"] == {}, "tap again: unselected")
# filter my players
r.click(L["filter"].center)
check(g.ss()["modal"]["for"] == "mine_filters", "FILTER opens the box for my players")
g.ss()["modal"]["draft"]["program"] = "STAR SIGNING"
g.ss_apply()
check(all(c["kind"] == "star" for c in g.ss_mine()) and g.ss_mine(), "...and filters them (legends only)")
g.ss()["mine_filters"] = g.ss_blank()

# the store's other tile goes straight to MY PLAYERS; BACK goes to the store
g.open_store()
r.frames(5)
r.click(tiles["exchange"].center)
check(g.state == rf.STARS and g.ss()["tab"] == "mine", "the store's RELEASE PLAYERS tile opens MY PLAYERS")
r.click(g.BACK_RECT.center)
check(g.state == rf.STORE, "BACK: the store")

# ---- no method of the game defined twice (1 Nov: a new card_club() once silently replaced the old one)
import ast, collections
tree = ast.parse(open(rf.__file__).read())
dupes = [n for cls in tree.body if isinstance(cls, ast.ClassDef)
         for n, k in collections.Counter(f.name for f in cls.body if isinstance(f, ast.FunctionDef)).items() if k > 1]
check(not dupes, "no method is defined twice in the game (%s)" % (dupes or "ok"))

print("\n%d failed" % len(fails))
sys.exit(1 if fails else 0)
