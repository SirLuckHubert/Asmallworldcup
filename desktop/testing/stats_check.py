"""The stat rework and the slide (26 Oct): each stat does what Hubi asked, measured on the real physics."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import pygame, rf
V = rf.Vector2
fails = []
def check(name, ok, info=""):
    print(("PASS " if ok else "FAIL ") + name + ("   " + info if info else ""))
    if not ok:
        fails.append(name)
class Quiet:
    def play(self, *a, **k): pass
    def burst(self, *a, **k): pass
q = Quiet()

def doll(stats=None, x=900.0):
    d = rf.Player(x, 1, None)
    d.set_stats({"rating": 110, "stats": dict({k: 105 for k in rf.STAT_KEYS}, **(stats or {})), "pos": "ST"})
    d.ctx = {}
    d.pos = V(x, rf.GROUND_Y - rf.FOOT_OFFSET); d.vel = V(0, 0); d.angle = 0.0; d.av = 0.0
    for l in d.limbs:
        l.reset(0.0)
    d.grounded = True
    return d

def ball_into(d, ball_v):
    """Move the player into the ball until they touch, like in play. Returns the ball."""
    b = rf.Ball(); b.frozen = False; b.vel = V(*ball_v)
    ahead = d.vel.normalize() if d.vel.length() > 1 else V(1, 0)
    b.pos = d.pos + ahead * 90 + V(0, 10)
    for _ in range(400):
        h = 1 / 480.0
        d.pos += d.vel * h
        b.pos += b.vel * h
        v0 = V(b.vel)
        if rf.ball_vs_player(b, d, q, q, lambda *a, **k: None) and (b.vel - v0).length() > 1.0:
            break
    return b

# ---- the slide: a dive into the floor keeps its speed, by the angle
def slide(vin):
    d = doll(); d.pos = V(900, rf.GROUND_Y - rf.FOOT_OFFSET - 60); d.grounded = False; d.vel = V(*vin)
    touch = None
    for i in range(240):
        d.step(1 / 240.0, (), q, q)
        if touch is None and d.grounded:
            touch = i
        if touch is not None and i - touch >= 60:
            break
    return abs(d.vel.x)
shallow, steep = slide((1800, 700)), slide((500, 2200))
check("shallow dive slides on (keeps > 900 px/s a quarter second after landing)", shallow > 900, "%.0f" % shallow)
check("steep dive slides less than a shallow one", steep < shallow, "%.0f vs %.0f" % (steep, shallow))

# ---- passing never cushions: standing still, a pass comes in at 500. Compared with the plain
# bounce (every passing effect switched off), top passing must not take any speed off it -
# the old passing roughly halved it - and low passing (a heavy touch) springs it off harder.
def still_touch(pass_stat):
    d = doll({"pass": pass_stat}); b = rf.Ball(); b.frozen = False
    b.pos = V(d.pos.x + 140, d.pos.y + 10); b.vel = V(-500, 0)
    for _ in range(400):
        b.pos += b.vel / 480.0
        v0 = V(b.vel)
        if rf.ball_vs_player(b, d, q, q, lambda *a, **k: None) and (b.vel - v0).length() > 1.0:
            break
    return b.vel.length()
saved = rf.TOUCH_PASS, rf.HEAVY_TOUCH, rf.CLEAN_HIT
rf.TOUCH_PASS = rf.HEAVY_TOUCH = rf.CLEAN_HIT = 0.0
plain = still_touch(160)
rf.TOUCH_PASS, rf.HEAVY_TOUCH, rf.CLEAN_HIT = saved
top, low = still_touch(160), still_touch(50)
check("top passing takes no speed off a pass (no cushioning)", top >= plain * 0.98, "%.0f vs plain bounce %.0f" % (top, plain))
check("low passing is a heavy touch: the ball springs off harder", low > plain * 1.1, "%.0f vs %.0f" % (low, plain))

# ---- soft touch on the move goes your way
d = doll({"pass": 160}); d.vel = V(260, 0); b = ball_into(d, (-150, 0))
check("a soft touch on the move goes the way you move", b.vel.x > 0, "ball vx %.0f" % b.vel.x)

# ---- hit power: strongest hits harder than weakest (~30%)
weak = doll({k: 50 for k in rf.STAT_KEYS}); weak.vel = V(1800, 0); bw = ball_into(weak, (0, 0))
strong = doll({k: 160 for k in rf.STAT_KEYS}); strong.vel = V(1800, 0); bs = ball_into(strong, (0, 0))
check("the strongest card hits harder than the weakest", bs.vel.length() > bw.vel.length() * 1.15,
      "%.0f vs %.0f" % (bs.vel.length(), bw.vel.length()))

# ---- speed: fastest launches ~55% harder than slowest (28 Oct: was ~25%)
slow, fast = doll({"speed": 50}), doll({"speed": 160})
k = fast.max_power() / slow.max_power()
check("speed gap slowest -> fastest is about 55%", 1.45 < k < 1.70, "x%.2f" % k)

# ---- 28 Oct: the worst card against the best - the same run into the ball, several times the shot
def card_doll(rating, stat):
    d = doll({k: stat for k in rf.STAT_KEYS}); d.rating = rating; return d
w = card_doll(55, 60); w.vel = V(1600, 0); bw = ball_into(w, (0, 0))
s_ = card_doll(125, 150); s_.vel = V(1600, 0); bs = ball_into(s_, (0, 0))
k = bs.vel.length() / max(1.0, bw.vel.length())
check("worst card -> best card: the same run-up hits 3x-7x as hard", 3.0 < k < 7.0, "x%.2f" % k)

# ---- dribbling: the wait between throws
waits = []
for v in (50, 160):
    d = doll({"drib": v}); d.throw(V(1, -1), 1500); waits.append(d.throw_timer)
check("better dribblers can throw again sooner", waits[1] < waits[0], "%.2f s vs %.2f s" % (waits[1], waits[0]))

# ---- duels: defending counts (30%)
A = doll({"def": 160}); Bd = doll({"def": 50}, x=900 + 2 * rf.BODY_R - 8); Bd.facing = -1
A.vel = V(1000, 0); Bd.vel = V(-1000, 0)
rf.player_vs_player(A, Bd, q)
check("the better defender wins an even duel", abs(A.vel.x) > abs(Bd.vel.x), "%.0f vs %.0f" % (A.vel.x, Bd.vel.x))

# ---- shooting: worst shooter's arrow wobbles, the best barely
w0 = max(abs(doll({"shot": 50}).aim_wobble(t * 0.05)) for t in range(60))
w1 = max(abs(doll({"shot": 160}).aim_wobble(t * 0.05)) for t in range(60))
check("the worst shooter's arrow wobbles, the best is steady", w0 > 0.1 and w1 < 0.02, "%.3f vs %.3f rad" % (w0, w1))

print("\n%d failed" % len(fails), fails if fails else "")
sys.exit(1 if fails else 0)
