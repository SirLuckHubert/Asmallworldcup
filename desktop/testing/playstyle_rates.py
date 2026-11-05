"""How often each PlayStyle fires in CPU v CPU play, every PlayStyle on for both players.
    python3 playstyle_rates.py [seconds]"""


import sys, os, random, time, collections
secs = float(sys.argv[1]) if len(sys.argv) > 1 else 120
T = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, T)
import harness
from harness import Run, pygame, rf
random.seed(3)
r = Run(save={"coins": 0}); g = r.g
fires = collections.Counter(); hits = [0]; throws = [0]; shots = [0]
orig_fire = rf.Player.ps_fire
def fire(self, key):
    fires[key] += 1
    return orig_fire(self, key)
rf.Player.ps_fire = fire
orig_hit = rf.ball_vs_player
def hit(ball, doll, *a, **k):
    v0 = ball.vel.length()
    ok = orig_hit(ball, doll, *a, **k)
    if ok and abs(ball.vel.length() - v0) > 1:
        hits[0] += 1
        if ball.vel.length() > 900: shots[0] += 1
    return ok
rf.ball_vs_player = hit
orig_throw = rf.Player.throw
def th(self, *a, **k):
    ok = orig_throw(self, *a, **k); throws[0] += ok; return ok
rf.Player.throw = th
ALL = [p[0] for p in rf.PLAYSTYLES]
def arm(d):
    if getattr(d, "_armed", False) and d.ps_on: return
    d.is_gk = True                                  # so the keeper ones can fire too
    d.ps_on = {k: 1.0 for k in ALL}
    d._armed = True
g.mode = "wc"; g.state = rf.SELECT
brain = None; played = 0.0; t0 = time.time()
for f in range(int(secs * 60 * 4)):
    if g.state == rf.LINEUP:
        g.pick_player([c for c in g.lineup_cards() if g.available(c)][0])
    if g.state == rf.SELECT and g.roulette is None:
        if g.team is None: g.new_tournament(0)
        g.start_draw()
    if g.state == rf.PLAY:
        if brain is None or brain.doll is not g.player:
            brain = rf.Brain(g.player, 1, skill=0.8, opponent=g.cpu)
        arm(g.player); arm(g.cpu)
        brain.update(1 / 60.0, g.ball)
        played += 1 / 60.0
    if g.state == rf.GOAL:
        globals()["gf"] = globals().get("gf", 0) + 1
        if gf > 150: globals()["gf"] = 0; g.advance_after_goal()
    r.frames(1)
    if g.state == rf.FULLTIME: g.advance_after_goal()
    if played >= secs: break
    if f % 120 == 0 and g.state not in (rf.PLAY, rf.GOAL, rf.KICKOFF):
        r.click(rf.WIDTH // 2, rf.HEIGHT // 2, settle=1)
rf.CPU_LOSING_BONUS = 0.0
print("played %.0fs  hits %d  hard hits %d  throws %d  goals %d-%d" % (played, hits[0], shots[0], throws[0], g.score_home, g.score_away))
for k in ALL:
    print("  %-12s %4d fires  %5.1f / min" % (k, fires[k], fires[k] * 60.0 / max(1, played)))
