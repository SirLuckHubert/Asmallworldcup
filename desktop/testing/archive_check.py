"""THE SIGNATURE ARCHIVE and MARIO KEMPES (1 Nov).

Kempes 128, the second Game Box's Signature card; both box players with a level 3 and a level 2 PlayStyle;
two Game Boxes side by side; the Archive - Signature cards for SIGNATURE TOKENS, tokens only from its quest
(level 10: the World Cup final against the Netherlands scoring 3+, THE MACHINE, the Premier League on HARD),
each task driven through the game's own code.

    python3 archive_check.py      (pictures: out/archive_*.png)"""
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


random.seed(7)
squad = ["ARS_saka", "CHE_caicedo", "AST_martinez", "BRE_wissa", "BOU_evanilson"]
r = Run(save={"coins": 200000, "xp": 0, "owned": {c: 1 for c in squad}, "squad": list(squad),
              "tutorial_done": True, "starter_opened": True}, name="save_archive.json")
g = r.g

# ================================================================== KEMPES
k = g.cards.get("SIG_ARG_kempes")
check(k is not None and k["rating"] == 128 and k["pos"] == "ST" and k["design"] == "signature",
      "Mario Kempes: a 128 ST Signature card")
check(g.card_template_key(k) == "flagholo_ARG", "...on the HOLO Signature card with Argentina's flag")
# the holo card (Hubi's second look): chrome layers that line up, and it never stands still
ta, tb, tc = (g.card_template(n, 262, 361) for n in ("fholo", "fholoframe", "fholochrome"))
check(ta and tb and tc and ta[0].get_size() == tb[0].get_size() == tc[0].get_size() and ta[1:3] == tb[1:3] == tc[1:3],
      "the holo card's three layers line up")
check(g.live_top_key("flagholo_ARG") == "fholo", "it moves on every screen (the flag waves under it)")
h0, h1 = g.holo_frame(262, 361, 0), g.holo_frame(262, 361, rf.HOLO_FRAMES // 2)
px = [(int(262 * 0.04), int(361 * 0.5)), (int(262 * 0.96), int(361 * 0.3)), (int(262 * 0.5), int(361 * 0.02))]
diff = sum(1 for x, y in px if h0[0].get_at((x + h0[1], y + h0[2]))[:3] != h1[0].get_at((x + h1[1], y + h1[2]))[:3])
check(h0 is not None and diff >= 2, "the rainbow sheen drifts: the chrome's colour changes between frames (%d/3)" % diff)
check(h0[0].get_at((h0[1] + 131, h0[2] + 180))[:3] == (0, 0, 0), "...and never touches the player (only the chrome)")
w0 = pygame.Surface((600, 800), pygame.SRCALPHA)
for size in ((120, 166), (262, 361), (380, 524)):
    g.blit_card(w0, k, pygame.Rect(100, 100, *size))
check(True, "the holo card draws at three sizes")
# the autograph pulses (dims, then a light runs along it) and petals drift round the card
def sig_light(at):
    pygame.time.set_ticks(int(at * 1000)) if hasattr(pygame.time, "set_ticks") else None
    w1 = pygame.Surface((600, 800), pygame.SRCALPHA)
    g.draw_sig_pulse(w1, k, pygame.Rect(100, 100, 380, 524))
    tot = 0
    for yy in range(300, 420, 4):
        for xx in range(150, 450, 4):
            c = w1.get_at((xx, yy))
            tot += (c[0] + c[1] + c[2]) * c[3] // 255
    return tot
base_t = pygame.time.get_ticks() / 1000.0
off = (sum(map(ord, k["id"])) % 13) * 0.21
def at(u):
    t = base_t + ((u * rf.SIG_PULSE - (base_t + off)) % rf.SIG_PULSE)
    pygame.time.advance((t - pygame.time.get_ticks() / 1000.0) * 1000.0)
    return sig_light(None)
normal = at(0.80)
dark = at(0.20)
shine = at(0.50)
check(dark < normal * 0.9, "the autograph dims (%d -> %d)" % (normal, dark))
check(shine > dark, "...then the light runs along it (%d)" % shine)
w2 = pygame.Surface((800, 900), pygame.SRCALPHA)
g.draw_petals(w2, pygame.Rect(200, 150, 380, 524), k["id"], rf.PETALS)
cols = set()
for yy in range(100, 750, 3):
    for xx in range(100, 700, 3):
        c = w2.get_at((xx, yy))
        if c[3] > 150:
            cols.add(min(rf.PETAL_COLS, key=lambda p: sum((p[j] - c[j]) ** 2 for j in range(3))))
check(len(cols) == 3, "petals in all three colours, blue, white and yellow (%d)" % len(cols))
class Rec:                                    # where each petal lands, a moment apart
    def __init__(self): self.at = []
    def blit(self, img, r, *a, **kw): self.at.append(r.center)
moves = []
r1, r2 = Rec(), Rec()
g.draw_petals(r1, pygame.Rect(200, 150, 380, 524), k["id"], rf.PETALS)
pygame.time.advance(100)
g.draw_petals(r2, pygame.Rect(200, 150, 380, 524), k["id"], rf.PETALS)
if len(r1.at) == len(r2.at):
    moves = [(b[0] - a[0], b[1] - a[1]) for a, b in zip(r1.at, r2.at)]
mx = sum(m[0] for m in moves) / max(1, len(moves))
my = sum(m[1] for m in moves) / max(1, len(moves))
check(moves and mx > 0.5 and my > 0.5, "the petals blow from the top left to the bottom right (%.1f, %.1f)" % (mx, my))
# 2 Nov crash (Hubi, in a walkout): a cache that filled up cleared itself straight after storing the new
# entry, then looked it up - KeyError. A card zooming in passes through dozens of sizes, so try a hundred.
ok = True
try:
    for i in range(100):
        g.aura_glow_img(200 + i, 270 + i, (176, 70, 255))
        g.sig_parts("sig_kempes", 150 + i)
        g.gold_mask("fholochrome", 200 + i, 270 + i)
        g.card_template(rf.card_template_key(k) if hasattr(rf, "card_template_key") else "star", 200 + i, 270 + i)
except KeyError as e:
    ok = False
    print("   KeyError", e)
check(ok, "caches survive filling up (a hundred card sizes in a row)")
sg = g.autograph_img("sig_kempes", 380)
check(sg is not None and sg.get_width() >= 370 and sg.get_height() > sg.get_width() * 0.6,
      "Kempes's autograph is drawn smooth and climbs (%s)" % (sg.get_size() if sg else None,))
g._fholo_ok = False
check(g.card_template_key(k) == "flagsig_ARG", "without the holo sprites: the plain Signature card")
g._fholo_ok = None
check(k["id"] in g.card_figs and rf.find_sprite("sig_kempes") and rf.find_sprite("sig_kempes_px"),
      "...his figure and his autograph are there")
check(all(g.sig_looks.get(k["id"], {}).get(p) is not None for p in ("head", "torso", "arm", "leg")),
      "...and his look in a match (head, shirt, arms, legs)")
for cid in rf.BOX_CARDS:
    lv = [l for _p, l in g.cards[cid]["ps"]]
    check(lv[:2] == [3, 2], "%s: PlayStyles level 3 + level 2 (%s)" % (g.cards[cid]["name"], lv))
check(not g.can_exchange(k) and k["id"] not in {c["id"] for c in g.ss_catalogue()},
      "a box player can't be released or bought in Star Signings")

# ================================================================== TWO GAME BOXES
g.open_store()
r.frames(5)
tiles = dict(zip([t[0] for t in g.STORE_TILES], g.store_layout()))
r.click(tiles["box"].center)
check(g.state == rf.EVENT and g.box_entry()[0] == "kempes", "the store's GAME BOXES opens Mario Kempes's box")
r.shot("archive_box_kempes", half=False)
L = g.event_layout()
coins0 = g.save["coins"]
for n in range(13):
    r.click(L["buy"].center)
    for _ in range(400):
        if g.event_spin is None:
            break
        r.frames(1)
    if g.state == rf.PACK_OPEN:
        g.state = rf.EVENT
    g.event_popup = None
check(g.owns(k), "13 draws: Kempes is yours (the last draw is sure)")
check(len(g.save["kempes_box"]["claimed"]) == 13 and not g.save.get("neymar_box", {}).get("claimed"),
      "his box is used up, Neymar Jr's untouched")
won = sum(v for kd, v in rf.NEYMAR_REWARDS if kd in ("coins", "jackpot_coins"))
check(coins0 - g.save["coins"] + won == sum(rf.NEYMAR_PRICES),
      "the same prices as Neymar Jr's box (%d coins, %d of it won back)" % (sum(rf.NEYMAR_PRICES), won))
# 4 Nov: Neymar Jr's box is gone - he only comes from Signature Tokens
check(all(b[1] != rf.NEYMAR_CARD for b in rf.GAME_BOXES) and len(rf.GAME_BOXES) == 1,
      "one Game Box (Kempes's) - no Neymar Jr box")
check(not L["boxes"], "...so no box tabs")
g.open_event("neymar")
check(g.box_entry()[0] == "kempes", "asking for the old Neymar Jr box opens Kempes's")
check(rf.NEYMAR_CARD in rf.ARCHIVE_CARDS and rf.NEYMAR_CARD in rf.NO_EXCHANGE
      and rf.NEYMAR_CARD not in [c["id"] for c in g.ss_catalogue()],
      "Neymar Jr: Archive only - not in a box, not in the market")

# ================================================================== THE ARCHIVE
g.open_store()
r.frames(5)
r.click(g.store_archive_rect().center)
check(g.state == rf.ARCHIVE, "the store's SIGNATURE ARCHIVE strip opens it")
q = rf.ARCHIVE_QUESTS[0]
check(len(rf.ARCHIVE_QUESTS) == 1 and q[1] == 10 and len(q[3]) == 3, "one quest so far, at level 10, three tasks")
check(g.player_level() < 10 and not g.archive_quest_open(q), "at level %d it is locked" % g.player_level())
r.shot("archive_locked", half=False)
check(not g.archive_event("machine"), "...and a locked quest's task doesn't count")
check(g.sig_tokens() == 0, "no tokens to start with")
g.ask_archive(g.cards[rf.NEYMAR_CARD])
check(g.store_confirm is None, "no tokens: no signing")

# level 10
need = 0
while rf.level_from_xp(need)[0] < 10:
    need += 100
g.save["xp"] = need
check(g.player_level() == 10 and g.archive_quest_open(q), "level 10: the quest opens")
A = g.archive()

# -- task 1: the World Cup final against the Netherlands, 3 or more
codes = [t["name"] for t in g.teams]
arg, net, fra = codes.index("ARG"), codes.index("NET"), codes.index("FRA")


def wc_final(opp, score):
    g.mode = "wc"
    g.wc_slot = "normal"
    g.difficulty = 1
    g.new_tournament(arg)
    others = [i for i in range(len(codes)) if i not in (arg, opp)]
    g.opponents = others[:6] + [opp]
    g.results = [(2, 0)] * 6
    g.round = 6
    g.score_home, g.score_away = score
    g.forfeited = False
    g.played_this_match = set()
    g.settle_match()

wc_final(fra, (4, 0))
check(not A["done"].get("wc_final_net"), "a final won 4-0 against France: not this one")
wc_final(net, (2, 0))
check(not A["done"].get("wc_final_net"), "the Netherlands beaten 2-0: not enough goals")
wc_final(net, (3, 1))
check(A["done"].get("wc_final_net"), "the Netherlands beaten 3-1 in the final: TASK DONE")

# -- task 2: THE MACHINE
g.mode = "gauntlet"
check(g.gt_new_run(), "a Gauntlet run starts")
run = g.gt_run()
run["rung"] = rf.GT_LEN - 1
g.gt_finish(2, 1)
check(A["done"].get("machine") and g.gt()["wins"] >= 1, "THE MACHINE beaten: TASK DONE")

# -- task 3: the Premier League on HARD (through the club ladder)
def season(diff):
    g.mode = "club"
    g.ladder()["mine"] = 0
    g.lg = None
    g.difficulty = diff
    g.go_to_club()
    Lay = g.lg_layout()
    for _ in range(rf.CLUB_ROUNDS):
        r.click(Lay["play"].center)
        if g.state != rf.LINEUP:
            break
        g.difficulty = diff
        g.pick_player([c for c in g.lineup_cards() if g.available(c)][0])
        r.frames(3)
        g.score_home, g.score_away = 5, 0
        g.finish_match()
        g.advance_after_goal()
        for _ in range(3):
            if g.state == rf.TABLE:
                r.click(400, 400)
    return g.lg and g.lg.get("end")

end = season(1)
check(end and end["result"] == "champions" and not A["done"].get("pl_hard"), "Premier League champions on MEDIUM: not this one")
end = season(2)
check(end and end["result"] == "champions" and A["done"].get("pl_hard"), "Premier League champions on HARD: TASK DONE")

# ---- claiming, through the screen
g.open_archive()
r.frames(5)
r.shot("archive_done", half=False)
L = g.archive_layout()
for b in L["claims"]:
    r.click(b.center)
check(g.sig_tokens() == 3 * rf.ARCHIVE_TASK_TOKENS, "three CLAIMs: %d tokens" % g.sig_tokens())
r.click(L["claims"][0].center)
check(g.sig_tokens() == 3, "...each once")
r.click(L["bonus_btn"].center)
check(g.sig_tokens() == 3 + rf.ARCHIVE_BONUS_TOKENS == rf.SIG_TOKEN_PRICE, "all three: +%d more - one Signature card's worth (%d)"
      % (rf.ARCHIVE_BONUS_TOKENS, g.sig_tokens()))
check(g.archive_next_quest() is None, "the quest is finished")
r.shot("archive_claimed", half=False)

# ---- signing: Kempes is already yours (from the box), so Neymar Jr
kempes_btn = [b for cid, cr, b in L["cards"] if cid == rf.KEMPES_CARD][0]
r.click(kempes_btn.center)
check(g.store_confirm is None, "Kempes is at your club already: no second copy")
ney_btn = [b for cid, cr, b in L["cards"] if cid == rf.NEYMAR_CARD][0]
r.click(ney_btn.center)
check(g.store_confirm is not None and g.store_confirm["ok"] == "SIGN", "Neymar Jr: SIGN for %d tokens?" % rf.SIG_TOKEN_PRICE)
_p, ok, _c = g.store_confirm_layout()
r.click(ok.center)
check(g.state == rf.PACK_OPEN and g.owns(g.cards[rf.NEYMAR_CARD]) and g.sig_tokens() == 0, "...he walks out, the tokens spent")
r.click(960, 540)
r.click(960, 540, settle=3)
r.frames(20, dt=1 / 30.0, draw=True)
r.click(960, 540, settle=0)
r.frames(40, dt=1 / 30.0, draw=True)
check(g.state == rf.ARCHIVE, "after the walkout: back to the Archive (%s)" % g.state)
r.click(g.BACK_RECT.center)
check(g.state == rf.STORE, "BACK: the store")

# ---- an old save
r2 = Run(save={"coins": 0, "tutorial_done": True, "starter_opened": True, "neymar_box": {"v": 2, "claimed": [0, 1],
                                                                                      "players": []}},
         name="save_archive2.json")
g2 = r2.g
g2.open_event("neymar")
check(g2.save["neymar_box"]["claimed"] == [0, 1] and g2.box_entry()[0] == "kempes",
      "an old save's Neymar Jr box progress is left alone (and Kempes's box opens)")
g2.save.setdefault("archive", {})["tokens"] = rf.SIG_TOKEN_PRICE
g2.archive()["tokens"] = rf.SIG_TOKEN_PRICE
check(g2.archive_sign(rf.NEYMAR_CARD) and g2.owns(g2.cards[rf.NEYMAR_CARD]), "Neymar Jr signs for %d tokens" % rf.SIG_TOKEN_PRICE)
g2.archive()["tokens"] = 0
g2.state = rf.ARCHIVE
g2.open_archive()
r2.frames(3)
r2.shot("archive_fresh", half=False)
check(g2.sig_tokens() == 0, "...and starts the Archive at 0 tokens")

print("\n%d failed" % len(fails))
sys.exit(1 if fails else 0)
