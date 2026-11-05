"""The card gap: per card, a full throw, the wait between throws, and the shot off the same run-up.
    python3 card_gap.py"""
import sys, os
T = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, T)
import harness
from harness import Run, rf, pygame
from pygame import Vector2 as V
class Q:
    def play(self, *a, **k): pass
    def burst(self, *a, **k): pass
q = Q()
r = Run(save={"coins": 0}); g = r.g
def doll(card, x=900.0):
    d = rf.Player(x, 1, None); d.set_stats(card); d.ps_on = {}; d.ctx = {}
    d.pos = V(x, rf.GROUND_Y - rf.FOOT_OFFSET); d.vel = V(0, 0); d.angle = 0.0; d.av = 0.0
    for l in d.limbs: l.reset(0.0)
    d.grounded = True
    return d
def hit(card, run):
    d = doll(card); d.vel = V(run, 0)
    b = rf.Ball(); b.frozen = False; b.vel = V(0, 0); b.pos = d.pos + V(90, 10)
    for _ in range(400):
        h = 1 / 480.0
        d.pos += d.vel * h
        v0 = V(b.vel)
        if rf.ball_vs_player(b, d, q, q, lambda *a, **k: None) and (b.vel - v0).length() > 1.0:
            break
    return b.vel.length() * rf.BALL_TIME          # what you SEE: px/s on screen
for cid in ("WC_ENG_henderson", "SUN_lefee", "BOU_evanilson", "INT_messi"):
    c = g.cards[cid]
    d = doll(c); d.throw_timer = 0.0
    d.throw(V(1, -0.2), d.max_power())
    print("%-17s %3d  launch %5.0f  wait %.2fs  shot@800 %5.0f px/s  shot@1600 %5.0f px/s"
          % (c["name"], c["rating"], d.vel.length(), d.throw_timer, hit(c, 800), hit(c, 1600)))
