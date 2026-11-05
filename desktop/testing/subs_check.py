"""The team sheet before kick-off, and the half-time IN / OUT sub: 20 s + SKIP vs the CPU, 10 s online,
and the CPU's choice by difficulty.

    python3 subs_check.py"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Run, pygame, rf
fails = []
def check(name, ok, info=""):
    print(("PASS " if ok else "FAIL ") + name + ("   " + info if info else ""))
    if not ok: fails.append(name)

def to_half_time(r, g, mode="wc", difficulty=1):
    g.difficulty = difficulty
    g.mode = mode; g.state = rf.SELECT
    for f in range(60 * 60 * 4):
        if g.state == rf.LINEUP and g.sub is None:
            g.pick_player([c for c in g.lineup_cards() if g.available(c)][0])
        if g.state == rf.SELECT and g.roulette is None:
            if g.team is None: g.new_tournament(0)
            g.start_draw()
        if g.state == rf.PLAY and g.half == 1 and g.match_time < rf.HALF_SECONDS - 1.0:
            g.match_time = rf.HALF_SECONDS - 0.05      # straight to the half-time whistle
        if g.state == rf.GOAL:
            g.advance_after_goal()
        r.frames(1)
        if g.state == rf.LINEUP and g.sub is not None:
            return True
        if f % 120 == 0 and g.state not in (rf.PLAY, rf.GOAL, rf.KICKOFF, rf.LINEUP):
            r.click(rf.WIDTH // 2, rf.HEIGHT // 2, settle=1)
    return False

# ---- offline: the clock, SKIP, the reveal, the second half
r = Run(save={"coins": 0}); g = r.g
ok = to_half_time(r, g)
check("half time opens the sub screen", ok and g.sub["phase"] == "pick")
check("vs the CPU you get 20 seconds", ok and g.sub["limit"] == 20.0, str(g.sub and g.sub["limit"]))
out = g.sub["out"]
stam = g.stamina_of(g.cards[out])
r.frames(60 * 21)                                      # let the clock run out
check("the clock running out keeps your pick and shows the reveal", g.sub is not None and g.sub["phase"] == "reveal")
check("...he stays on and plays (stamina spent)", g.my_card["id"] == out and g.stamina_of(g.cards[out]) < stam)
r.frames(int(60 * (rf.SUB_REVEAL + 0.3)))
check("then the second half kicks off", g.sub is None and g.half == 2 and g.state in (rf.KICKOFF, rf.PLAY))

r = Run(save={"coins": 0}, name="s2.json"); g = r.g
to_half_time(r, g)
r.frames(60)                                           # (menus ignore clicks for a moment after opening)
L = g.sub_layout()
other = [c for c in L["cards"] if c["id"] != g.sub["out"] and g.available(c)]
i = L["cards"].index(other[0]); rr = L["bench"][i]
r.click(rr.centerx, rr.centery, settle=1); r.frames(30)
check("tapping a bench card picks him", g.sub["pick"] == other[0]["id"])
t_before = g.sub["t"]
r.click(L["skip"].centerx, L["skip"].centery, settle=1)
check("SKIP ends the 20 seconds early", g.sub["phase"] == "reveal" and t_before < 5.0, "at %.1fs" % t_before)
check("...and he comes on", g.my_card["id"] == other[0]["id"])
r.click(rf.WIDTH // 2, rf.HEIGHT // 2, settle=0)
check("a click skips the reveal offline", g.sub is None and g.half == 2)

# ---- the CPU's pick by difficulty
r = Run(save={"coins": 0}, name="s3.json"); g = r.g
to_half_time(r, g)
pool = g.cpu_pool()
prof = {c["id"]: g.sub_profile(c) for c in pool}
check("the CPU has a choice to make", len(pool) >= 2, "%d cards" % len(pool))
# MEDIUM, CPU two goals behind: the most attacking of its good players
g.difficulty = 1; g.score_home, g.score_away = 2, 0
g.cpu_sub()
best = max(pool, key=lambda c: g.sub_score(c, g.my_card, "situation", 2))
check("MEDIUM picks the best card for the situation (chasing the game)", g.cpu_card["id"] == best["id"]
      and "CHASING" in g.sub["why"], "%s - %s" % (g.cpu_card["name"], g.sub["why"]))
# HARD: a counter to what you sent on
g.difficulty = 2; g.score_home, g.score_away = 1, 1
g.cpu_sub()
check("HARD picks the counter to your player", "COUNTERS" in g.sub["why"], "%s - %s" % (g.cpu_card["name"], g.sub["why"]))
# against a pure attacker, the counter weighs stopping him; against a wall, beating him
att = {"rating": 100, "stats": {"speed": 140, "shot": 150, "pass": 90, "drib": 150, "def": 60, "phys": 70}}
wall = {"rating": 100, "stats": {"speed": 80, "shot": 60, "pass": 90, "drib": 60, "def": 150, "phys": 150}}
D = max(pool, key=lambda c: prof[c["id"]]["wall"] - prof[c["id"]]["att"])     # its most defensive
X = max(pool, key=lambda c: prof[c["id"]]["att"] - prof[c["id"]]["wall"])     # its most attacking
lean_att = g.sub_score(D, att, "counter", 0) - g.sub_score(X, att, "counter", 0)
lean_wall = g.sub_score(D, wall, "counter", 0) - g.sub_score(X, wall, "counter", 0)
check("the counter leans to a defender vs an attacker, to an attacker vs a wall", lean_att > lean_wall,
      "%s over %s: %+.0f vs your attacker, %+.0f vs your wall" % (D["name"], X["name"], lean_att, lean_wall))
# EASY still just picks anyone from its squad
g.difficulty = 0
picks = set()
for _ in range(30):
    g.cpu_sub(); picks.add(g.cpu_card["id"])
check("EASY still picks at random", len(picks) >= 2, "%d different" % len(picks))

# ---- online: two games linked together
class Link:
    def __init__(self): self.on = True; self.inbox = []; self.peer = None; self.log = []; self.mute = ()
    def poll(self): out, self.inbox = self.inbox, []; return out
    def send(self, m):
        self.log.append(m.get("t"))
        if self.peer and m.get("t") not in self.mute: self.peer.inbox.append(json.loads(json.dumps(m)))
    def chat(self, t): pass
    def result(self, h, a): pass
    def connected_hint(self): return True

def online(mute=()):
    ra = Run(save={"coins": 0}, name="h.json"); A = ra.g
    rb = Run(save={"coins": 0}, name="g.json"); B = rb.g
    la, lb = Link(), Link(); la.peer, lb.peer = lb, la; A.net, B.net = la, lb
    lb.mute = mute
    a0, b0 = A.owned_cards()[0], B.owned_cards()[0]
    A.start_pvp({"role": "host", "card": a0["id"], "oppCard": b0["id"], "name": "HOST", "oppName": "GUEST"})
    B.start_pvp({"role": "guest", "card": b0["id"], "oppCard": a0["id"], "name": "GUEST", "oppName": "HOST"})
    def step(n=1):
        for _ in range(n):
            pygame.time.advance(1000 / 60.0)
            for gg in (A, B):
                gg.handle_events(); gg.update(1 / 60.0)
    for _ in range(600):
        for gg in (A, B):
            if gg.state == rf.VERSUS: gg.versus["t"] = 99
        step()
        if A.state == rf.PLAY: break
    A.match_time = rf.HALF_SECONDS - 0.05
    step(5)
    return A, B, step

A, B, step = online()
check("online: both sides get the sub screen at half time", A.sub is not None and B.sub is not None)
check("online: 10 seconds, no skip", A.sub["limit"] == 10.0 and B.sub["limit"] == 10.0)
newb = [c for c in B.lineup_cards() if c["id"] != B.sub["out"]][0]
B.sub["pick"] = newb["id"]
step(int(60 * 10.5))
check("online: both see the reveal", A.sub is not None and A.sub["phase"] == "reveal" and B.sub["phase"] == "reveal")
check("online: the host plays the guest's pick", A.cpu_card["id"] == newb["id"] and B.my_card["id"] == newb["id"])
step(int(60 * 4))
check("online: back to football, second half", A.sub is None and B.sub is None and A.half == 2
      and A.state in (rf.KICKOFF, rf.PLAY) and B.state in (rf.KICKOFF, rf.PLAY))

A, B, step = online(mute=("sub",))                     # the guest's pick never arrives
old = A.cpu_card["id"]
step(int(60 * (10 + rf.SUB_GRACE + 0.5)))
check("online: no word from the rival - he keeps his player, the match goes on",
      A.sub is not None and A.sub["phase"] == "reveal" and A.cpu_card["id"] == old)

# ---- 28 Oct: the team sheet before kick-off
r = Run(save={"coins": 0}, name="ts1.json"); g = r.g
g.go_to_club(); g.new_season(g.user_idx); g.start_club_draw()
g.club_opps.append(g.club_roulette["cur"]); g.club_roulette = None; g.start_club_match()
g.pick_player(g.lineup_cards()[1])
mine, ms, theirs, cs = g.team_sheet()
check("club: the team sheet shows 5 v 5", g.state == rf.VERSUS and len(mine) == 5 and len(theirs) == 5,
      "%d v %d" % (len(mine), len(theirs)))
check("club: both starters are on it", ms == g.my_card["id"] and any(c["id"] == cs["id"] for c in theirs))
for tt in (1.0, 3.5, 5.0, 7.0):
    g.versus["t"] = tt; g.draw()
check("club: the sheet draws through the whole intro", True)
r = Run(save={"coins": 0}, name="ts2.json"); g = r.g
g.mode = "wc"; g.new_tournament(0); g.start_draw()
g.roulette["landed"] = True; g.opponents.append(g.roulette["cur"]); g.roulette = None
g.round = 0; g.start_round(); g.pick_player(g.lineup_cards()[0])
mine, ms, theirs, cs = g.team_sheet()
check("World Cup: the team sheet shows 3 v 3", len(mine) == 3 and len(theirs) == 3, "%d v %d" % (len(mine), len(theirs)))
g.versus["t"] = 5.0; g.draw()
r.click(rf.WIDTH // 2, rf.HEIGHT // 2, settle=0); r.frames(2)
check("a click goes straight to kick-off", g.state in (rf.KICKOFF, rf.PLAY))
A2, B2, _step = online()
check("online: each side gets the other's squad for the sheet", len(A2.opp_squad) >= 2 and len(B2.opp_squad) >= 2,
      "%d / %d" % (len(A2.opp_squad), len(B2.opp_squad)))

print("\n%d failed" % len(fails), fails)
sys.exit(1 if fails else 0)
