"""Classic physics (29 Oct): the numbers measured off the original A Small World Cup.

    python3 classic_check.py

On screen, per real second, in pitch lengths (goal line to goal line):
ball and players fall at ~0.65 /s^2, nothing slows sideways in the air, the ball comes off the
floor at ~0.84, and the slower world still moves every frame (no stutter)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from harness import Run, rf

U = rf.WIDTH - 2 * rf.GOAL_DEPTH
fails = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


r = Run(save={"coins": 0}); g = r.g
g.mode = "wc"; g.state = rf.SELECT
for f in range(3600):
    if g.state == rf.LINEUP:
        g.pick_player([c for c in g.lineup_cards() if g.available(c)][0])
    if g.state == rf.SELECT and g.roulette is None:
        if g.team is None:
            g.new_tournament(0)
        g.start_draw()
    r.frames(1)
    if g.state == rf.PLAY:
        break
    if f % 120 == 0 and g.state not in (rf.PLAY, rf.GOAL, rf.KICKOFF):
        r.click(rf.WIDTH // 2, rf.HEIGHT // 2, settle=1)
check(g.state == rf.PLAY, "a match is under way")
p, b, cpu = g.player, g.ball, g.cpu
fps = 60.0


def park():
    cpu.pos.update(rf.WIDTH - 120, rf.GROUND_Y - 90); cpu.vel.update(0, 0)
    p.pos.update(200, rf.GROUND_Y - 90); p.vel.update(0, 0)


# 1. the ball: dropped with a sideways push, high in the middle of the pitch
r.frames(20)
park()
b.pos.update(rf.WIDTH * 0.5, rf.GROUND_Y - 600); b.vel.update(300, 0); b.spin = 0.0
xs, ys = [], []
for k in range(40):
    park(); r.frames(1)
    xs.append(b.pos.x); ys.append(b.pos.y)
t = np.arange(len(ys)) / fps
gy = 2 * np.polyfit(t, ys, 2)[0] / U
ax = 2 * np.polyfit(t, xs, 2)[0] / U
# 30 Oct: Hubi asked for the whole game 30% slower (WORLD_TIME 0.6 -> 0.42): gravity on screen goes
# with the square of the clock, so the target is the original's 0.65 x (WORLD_TIME / 0.6)^2
G_WANT = 0.65 * (rf.WORLD_TIME / 0.6) ** 2
check(G_WANT * 0.9 < gy < G_WANT * 1.1, "ball gravity on screen %.3f pitch lengths/s^2 (want %.3f: the original 0.65 on the match clock)" % (gy, G_WANT))
check(abs(ax) < 0.02, "the ball keeps its sideways speed in the air (%.3f)" % ax)
check(min(abs(np.diff(xs))) > 0.5, "the ball moves every frame (no stutter): smallest step %.2f px" % min(abs(np.diff(xs))))
# 2. the bounce off the floor
vin = vout = None
prev = b.vel.y
for k in range(240):
    park(); r.frames(1)
    if prev > 0 and b.vel.y < 0:
        vin, vout = prev, b.vel.y
        break
    prev = b.vel.y
e = -vout / vin if vin else 0.0
check(0.74 < e < 0.9, "the ball comes off the floor at %.2f (original ~0.84)" % e)
# 3. a player thrown high: gravity and no sideways drag
r.frames(30)
cpu.pos.update(rf.WIDTH - 120, rf.GROUND_Y - 90)
p.pos.update(400, rf.GROUND_Y - 300); p.vel.update(0, 0); p.av = 0.0; p.angle = 0.0
p.throw_timer = 0.0
p.throw(rf.Vector2(0.5, -1.0), p.max_power() * 0.7)
xs, ys = [], []
for k in range(36):
    cpu.pos.update(rf.WIDTH - 120, rf.GROUND_Y - 90); cpu.vel.update(0, 0)
    r.frames(1)
    xs.append(p.pos.x); ys.append(p.pos.y)
t = np.arange(len(ys)) / fps
gp = 2 * np.polyfit(t, ys, 2)[0] / U
axp = 2 * np.polyfit(t, xs, 2)[0] / U
check(G_WANT * 0.82 < gp < G_WANT * 1.1, "player gravity on screen %.3f pitch lengths/s^2 (want %.3f)" % (gp, G_WANT))
check(abs(axp) < 0.05, "the player keeps his sideways speed in the air (%.3f)" % axp)
check(abs(gp - gy) < 0.12, "ball and players fall alike (%.2f v %.2f)" % (gy, gp))
# 4. zip (BULLET PASS / TIKI TAKA / POWER SHOT): the ball falls slower while it lasts
def fall(zip_t):
    r.frames(10); park()
    b.pos.update(rf.WIDTH * 0.5, rf.GROUND_Y - 600); b.vel.update(0, 0); b.zip_t = zip_t
    ys = []
    for k in range(30):
        park(); r.frames(1); ys.append(b.pos.y)
    return 2 * np.polyfit(np.arange(len(ys)) / fps, ys, 2)[0]
gz, g0 = fall(5.0), fall(0.0)
check(0.6 < gz / g0 < 0.8, "a zipping ball falls at %.0f%% (BULLET PASS stays on a line)" % (100 * gz / g0))
# 5. GLIDE: skids on further after landing (air drag is gone, so it works on the floor now)
def skid(glide):
    """From a flat dive into the floor: how far he skids on after touching down, glide on or off
    (averaged: a tumbling body lands a little differently every time)."""
    keep = p.a
    p.a = (lambda k, _keep=keep: glide if k == "glide" else _keep(k))
    out = []
    for trial in range(12):
        b.frozen = True; b.pos.update(rf.WIDTH - 300, 120); b.vel.update(0, 0)
        r.frames(90)
        cpu.pos.update(rf.WIDTH - 120, rf.GROUND_Y - 90); cpu.vel.update(0, 0)
        p.pos.update(260 + trial * 12, rf.GROUND_Y - 240); p.vel.update(1300, 500); p.av = 0.0; p.angle = 0.0
        x0 = None
        for k in range(200):
            cpu.pos.update(rf.WIDTH - 120, rf.GROUND_Y - 90); cpu.vel.update(0, 0)
            b.pos.update(rf.WIDTH - 300, 120); b.vel.update(0, 0)
            r.frames(1)
            if x0 is None and p.grounded:
                x0 = p.pos.x
        out.append(p.pos.x - (x0 if x0 is not None else p.pos.x))
    p.a = keep
    b.frozen = False
    return float(np.median(out))
d0, d1 = skid(0.0), skid(0.14)
check(d1 > d0 * 1.15, "GLIDE skids further after landing: %.0f px v %.0f px" % (d1, d0))

# ---- 1 Nov: 30% faster play, a ball that's always round, spins and dips -----------------------
check(abs(rf.WORLD_TIME - 0.42 * 1.3) < 1e-9, "the match plays 30%% faster than 30 Oct (WORLD_TIME %.3f)" % rf.WORLD_TIME)


class _Nop:
    def play(self, *a, **k): pass
    def burst(self, *a, **k): pass


def flight(spin):
    bb = rf.Ball(); bb.reset(200, rf.GROUND_Y - bb.radius - 4, frozen=False)
    bb.vel = rf.Vector2(2300, -1000); bb.spin = spin
    for k in range(2000):
        bb.step(rf.FIXED_DT * rf.WORLD_TIME, [], _Nop(), _Nop())
        if k > 10 and bb.pos.y >= rf.GROUND_Y - bb.radius - 0.5:
            break
    return bb.pos.x, bb.angle
x_flat, _a = flight(0.0)
x_top, ang = flight(rf.math.degrees(2300 / 30.0) * rf.BALL_TOPSPIN)
check(x_top < x_flat - 120, "topspin dips a driven ball: lands at %.0f px, %.0f px short of no spin" % (x_top, x_flat - x_top))
check(abs(ang) > 360.0, "...and it visibly turns in the air (%.1f turns)" % (abs(ang) / 360.0))
x_back, _a = flight(-rf.math.degrees(2300 / 30.0) * rf.BALL_TOPSPIN)
check(abs(x_back - x_flat) < 1.0, "backspin never floats it up (lands %.0f v %.0f)" % (x_back, x_flat))
# a real hit puts topspin on: player flies into a still ball
b.frozen = False
b.pos.update(900, rf.GROUND_Y - b.radius); b.vel.update(0, 0); b.spin = 0.0
p.pos.update(900 - 160, rf.GROUND_Y - 120); p.vel.update(1500, 0); p.av = 0.0; p.angle = 0.0
cpu.pos.update(rf.WIDTH - 120, rf.GROUND_Y - 90); cpu.vel.update(0, 0)
for k in range(30):
    r.frames(1)
    if abs(b.vel.x) > 300.0:
        break
check(b.vel.x > 300.0 and b.spin > rf.math.degrees(b.vel.x / b.radius) * rf.BALL_TOPSPIN * 0.8,
      "a hit puts topspin on the way it's struck (%.0f px/s, spin %.0f deg/s)" % (b.vel.x, b.spin))
# always a circle
b.impact(rf.Vector2(0, -1), 5000.0)
surf = rf.pygame.Surface((400, 400), rf.pygame.SRCALPHA)
b.pos.update(200, 200); b.angle = 0.0
b.draw(surf)
check(not hasattr(b, "squash") or b.squash == 0.0, "the hardest impact never squashes the ball")
check(b.art.get_width() == b.art.get_height(), "the ball is drawn from a square (round) picture, only ever turned")
print("%d failed %s" % (len(fails), fails))
sys.exit(1 if fails else 0)
