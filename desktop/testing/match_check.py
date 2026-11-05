"""A real match, CPU against CPU, through the game's own loop.

    python3 match_check.py [seconds] [seed]

Passes if it plays the whole time without crashing and the ball is actually in play."""
import sys, random, time, json
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Run, pygame, rf
random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
secs = float(sys.argv[1]) if len(sys.argv) > 1 else 60
r = Run(save={"coins": 0}); g = r.g
hits = []
orig = rf.ball_vs_player
def wrapped(ball, doll, *a, **k):
    s0, v0 = ball.spin, rf.Vector2(ball.vel)
    hit = orig(ball, doll, *a, **k)
    if hit:
        hits.append({"dspin": ball.spin - s0, "out": ball.vel.length(), "in": v0.length(),
                     "bend": getattr(ball, "bend", 0.0), "who": "home" if doll is g.player else "away"})
    return hit
rf.ball_vs_player = wrapped
g.mode = "wc"; g.state = rf.SELECT
brain = None; t0 = time.time(); played = 0.0; slides = 0; throws = 0
orig_throw = rf.Player.throw
def counting_throw(self, *a, **k):
    global throws
    ok = orig_throw(self, *a, **k)
    throws += ok
    return ok
rf.Player.throw = counting_throw
crashed = None
try:
    for f in range(int(secs * 60 * 4)):
        if g.state == rf.LINEUP:
            g.pick_player([c for c in g.lineup_cards() if g.available(c)][0])
        if g.state == rf.SELECT and g.roulette is None:
            if g.team is None:
                g.new_tournament(0)
            g.start_draw()
        if g.state in (rf.SELECT,) and g.roulette is not None:
            pass
        if g.state == rf.PLAY:
            if brain is None or brain.doll is not g.player:
                brain = rf.Brain(g.player, 1, skill=0.8, opponent=g.cpu)
            brain.update(1 / 60.0, g.ball)
            played += 1 / 60.0
            if getattr(g.player, "slide_t", 0) > 0.5 or getattr(g.cpu, "slide_t", 0) > 0.5:
                slides += 1
        if g.state == rf.GOAL:
            goal_f = globals().get("goal_f", 0) + 1
            globals()["goal_f"] = goal_f
            if goal_f > 150:
                globals()["goal_f"] = 0
                g.advance_after_goal()
        r.frames(1)
        if g.state == rf.FULLTIME:
            g.advance_after_goal()
        if played >= secs:
            break
        if f % 120 == 0 and g.state not in (rf.PLAY, rf.GOAL, rf.KICKOFF):
            r.click(rf.WIDTH // 2, rf.HEIGHT // 2, settle=1)      # get past reveal/cutscene screens
except Exception as e:
    import traceback; traceback.print_exc(); crashed = repr(e)

fast = [h for h in hits if h["out"] > 300]
sp = sorted(abs(h["dspin"]) for h in fast)
q = lambda p: sp[int(p * (len(sp) - 1))] if sp else 0
print("end state", g.state, "half", getattr(g, "half", None), "clock", getattr(g, "clock_t", None))
print("played %.0fs (%.0fs wall) score %d-%d  hits %d (fast %d)  throws %d  slide frames %d  crash %s"
      % (played, time.time() - t0, g.score_home, g.score_away, len(hits), len(fast), throws, slides, crashed))
print("|dspin| on fast hits: p25 %.1f  p50 %.1f  p75 %.1f  p90 %.1f  max %.1f" % (q(.25), q(.5), q(.75), q(.9), q(1)))
print("bend set on %d of %d fast hits" % (sum(1 for h in fast if h["bend"] > 0), len(fast)))

ok = crashed is None and played >= secs * 0.95 and len(hits) > 50
print("PASS a full CPU match plays without crashing" if ok else "FAIL the CPU match broke")
sys.exit(0 if ok else 1)
