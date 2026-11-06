"""Every PlayStyle fires in its moment - and only then."""
import sys, collections, random
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Run, pygame, rf
V = rf.Vector2
class SFX:
    def play(self, *a, **k): pass
class PT:
    def burst(self, *a, **k): pass
sfx, pt = SFX(), PT()
fails = []
def check(name, ok, info=""):
    print(("PASS " if ok else "FAIL ") + name + ("   " + info if info else ""))
    if not ok: fails.append(name)

def doll(keys=(), gk=False, x=900.0, facing=1, level=1):
    d = rf.Player(x, facing, None)
    styles = [(rf.PS_BY_KEY[k], level) for k in keys]
    d.set_stats({"rating": 110, "stats": {k: 105 for k in rf.STAT_KEYS}, "pos": "GK" if gk else "ST",
                 "ps": styles})
    d.ctx = {}
    d.pos = V(x, rf.GROUND_Y - rf.FOOT_OFFSET); d.vel = V(0, 0); d.angle = 0.0; d.av = 0.0
    for l in d.limbs: l.reset(0.0)
    d.grounded = True
    return d

def ball_at(p, v=(0, 0)):
    b = rf.Ball(); b.frozen = False; b.pos = V(*p); b.vel = V(*v); return b

def hit(d, b):
    """Move the player into the ball (and the ball along) until they touch - like in play."""
    if (b.pos - d.pos).length() < 200:
        off = b.pos - d.pos
        if d.vel.length() > 1:
            b.pos = d.pos + off - d.vel.normalize() * 0 + (d.vel.normalize() * 70)
    for _ in range(240):
        h = 1 / 480.0
        d.pos += d.vel * h
        b.pos += b.vel * h
        v0 = rf.Vector2(b.vel)
        if rf.ball_vs_player(b, d, sfx, pt, lambda *a, **k: None) and (b.vel - v0).length() > 1.0:
            return True
    return False

# 1 header: ball on the head while flying in
d = doll(["header"]); d.pos = V(1400, 600); d.grounded = False; d.vel = V(900, -200)
h = d.to_world(d.HEAD_LOCAL)
b = ball_at((h.x + rf.HEAD_R + b_r - 6 if (b_r := rf.BALL_RADIUS) else 0, h.y), (0, 0))
hit(d, b); check("header fires on a head hit", "header" in d.ps_flash, str(d.ps_flash))
d2 = doll(["header"]); d2.vel = V(900, 0); b2 = ball_at((d2.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, d2.pos.y + 20))
hit(d2, b2); check("header does not fire on a body hit", "header" not in d2.ps_flash)

# 2 penalty: a still ball
d = doll(["penalty"]); d.vel = V(700, 0); b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, d.pos.y + 10))
hit(d, b); check("penalty fires on a dead ball", "penalty" in d.ps_flash)
d = doll(["penalty"]); d.vel = V(700, 0); b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, d.pos.y + 10), (-300, 0))
hit(d, b); check("penalty does not fire on a moving ball", "penalty" not in d.ps_flash)

# 3 power: full run-up vs slow
for spd, want in ((1800, True), (700, False)):
    d = doll(["power"]); d.vel = V(spd, 0); b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, d.pos.y + 10))
    hit(d, b); check("power %s at %d" % ("fires" if want else "quiet", spd), ("power" in d.ps_flash) == want)

# 4 power changes the result: same hit with/without
outs = []
for keys in ((), ("power",)):
    d = doll(keys); d.vel = V(1800, 0); b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, d.pos.y + 10))
    hit(d, b); outs.append(b.vel.length())
check("power hits harder", outs[1] > outs[0] * 1.05, "%.0f -> %.0f" % tuple(outs))

# 5 clinical near goal only
for x, want in ((rf.WIDTH - 700, True), (600, False)):
    d = doll(["clinical"], x=x); d.vel = V(1000, 0); b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, d.pos.y + 10))
    hit(d, b); check("clinical %s at x=%d" % ("fires" if want else "quiet", x), ("clinical" in d.ps_flash) == want)

# 6 accelerator: throw with the ball far / near
for gap, want in ((900, True), (150, False)):
    d = doll(["accelerator"]); d.ball_ref = ball_at((d.pos.x + gap, d.pos.y)); d.ctx = {}
    d.throw(V(1, 0.0), 1500); check("accelerator %s, ball %dpx away" % ("fires" if want else "quiet", gap), ("accelerator" in d.ps_flash) == want)


# ---------------------------------------------------------------------------------------------
# 6 Nov: what each one DOES, and that you can see it - the ball's path, the players
# ---------------------------------------------------------------------------------------------
GAME = Run(save={}).g
SEGS = GAME.segments


def fly(b, secs=2.0, stop_in_goal=True):
    """Step the ball through the world (crossbars and all); returns the points it passed."""
    pts = [V(b.pos)]
    for _ in range(int(secs * 480)):
        b.step(1 / 480.0, SEGS, sfx, pt)
        pts.append(V(b.pos))
        if stop_in_goal and (b.pos.x > rf.WIDTH - rf.GOAL_DEPTH + b.radius or b.pos.x < rf.GOAL_DEPTH - b.radius):
            break
    return pts


def in_goal(b, facing=1):
    past = b.pos.x > rf.WIDTH - rf.GOAL_DEPTH + b.radius if facing > 0 else b.pos.x < rf.GOAL_DEPTH - b.radius
    return past and b.pos.y >= rf.GROUND_Y - rf.GOAL_HEIGHT + rf.CROSSBAR_THICK * 0.5


def bend(pts):
    """How far the flight strays from the straight line between its ends (px)."""
    a, c = pts[0], pts[-1]
    d = c - a
    if d.length() < 1:
        return 0.0
    nrm = V(-d.y, d.x).normalize()
    return max(abs((p - a).dot(nrm)) for p in pts)


def strike(key, x, y=None, vel=(1800, 0), dy=10, ctx=None, level=2, **kw):
    d = doll([key], x=x, level=level, **kw)
    if y is not None:
        d.pos = V(d.pos.x, y); d.grounded = False
    d.ctx = dict(ctx or {})
    d.vel = V(*vel)
    dv = d.vel.normalize()
    b = ball_at((d.pos.x + dv.x * (rf.BODY_R + rf.BALL_RADIUS - 6), d.pos.y + dy + dv.y * (rf.BODY_R + rf.BALL_RADIUS - 6)))
    hit(d, b)
    return d, b

# FINESSE: it really curls - out low, and up into the top corner
best = None
for dy in range(-80, 81, 8):
    d = doll(["finesse"], x=rf.WIDTH - 1300, level=2); d.pos = V(d.pos.x, rf.GROUND_Y - 300); d.grounded = False
    d.vel = V(1500, 0)
    b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 4, d.pos.y + dy)); hit(d, b)
    if b.move is not None and b.move["k"] == "finesse":
        best = (d, b); break
check("finesse fires on a spun hit and puts the ball on its curl", best is not None)
if best:
    d, b = best
    pts = fly(b)
    top = rf.GROUND_Y - rf.GOAL_HEIGHT * 0.5
    check("...it curls: %.0f px off the straight line" % bend(pts), bend(pts) > 60)
    check("...and goes in, in the top half of the goal", in_goal(b) and pts[-1].y < top, "ends (%.0f, %.0f)" % tuple(pts[-1]))

# POWER SHOT: a fireball - dead straight, and straight THROUGH a man in the way
d, b = strike("power", rf.WIDTH - 900, vel=(1800, 0))
check("power shot is a fireball path", b.move is not None and b.move["k"] == "power")
wall = doll([], x=rf.WIDTH - 600, facing=-1); wall.pos = V(rf.WIDTH - 600, (b.pos.y + b.move["p2"][1]) * 0.5 if b.move else 700)
pts = [V(b.pos)]
for _ in range(960):
    b.step(1 / 480.0, SEGS, sfx, pt); pts.append(V(b.pos))
    rf.ball_vs_player(b, wall, sfx, pt, lambda *a, **k: None)
    if in_goal(b):
        break
check("...it goes through him and in", in_goal(b), "ends (%.0f, %.0f)" % tuple(b.pos))
check("...and he's blasted back, dazed", wall.vel.x > 500 and wall.daze_t > 0, "his vx %.0f" % wall.vel.x)
check("...on a straight line", bend(pts) < 30, "%.0f px off" % bend(pts))

# CLINICAL: locks on to the corner furthest from him - you see the crosshair
for opp_y, want in ((rf.GROUND_Y - 60, "top"), (rf.GROUND_Y - rf.GOAL_HEIGHT + 40, "low")):
    rf.PS_FX.clear()
    opp = doll([], x=rf.WIDTH - 260, facing=-1); opp.pos = V(rf.WIDTH - 260, opp_y)
    d = doll(["clinical"], x=rf.WIDTH - 700); d.opp_ref = opp; d.vel = V(1000, 0)
    b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, d.pos.y + 10)); hit(d, b)
    ok = b.move is not None and b.move["k"] == "clinical"
    goes = b.move["p2"][1] < rf.GROUND_Y - rf.GOAL_HEIGHT * 0.5 if ok else None
    check("clinical: keeper %s -> it goes %s" % ("low" if want == "top" else "high", want),
          ok and goes == (want == "top") and any(f["kind"] == "cross" for f in rf.PS_FX))

# CHIP SHOT: up into the sky, drops in under the bar
d = doll(["chip"], x=rf.WIDTH - 800); d.ctx = {"opp_off_line": True}; d.vel = V(600, -1100)
dv = d.vel.normalize(); b = ball_at((d.pos.x + dv.x * 260, d.pos.y + dv.y * 260)); hit(d, b)
check("chip shot is a lob path", b.move is not None and b.move["k"] == "chip")
if b.move:
    y0 = b.pos.y
    pts = fly(b, 3.0)
    check("...it goes way up (%.0f px above where it was hit)" % (y0 - min(p.y for p in pts)), y0 - min(p.y for p in pts) > 250)
    check("...and drops in under the bar", in_goal(b), "ends (%.0f, %.0f)" % tuple(b.pos))

# PENALTY EXPERT: the knuckleball - it wobbles side to side on its way in
d, b = strike("penalty", rf.WIDTH - 1000, vel=(700, 0))
check("penalty is a knuckleball path", b.move is not None and b.move["k"] == "penalty" and b.move["wob"] > 0)
if b.move:
    m = dict(b.move)
    a, c = rf.Vector2(m["p0"]), rf.Vector2(m["p2"]); nrm = rf.Vector2(-(c - a).y, (c - a).x).normalize()
    pts = fly(b)
    side = [(p - a).dot(nrm) for p in pts]
    flips = sum(1 for i in range(1, len(side)) if (side[i] > 4) != (side[i - 1] > 4))
    check("...it wobbles (%d swings)" % flips, flips >= 3)
    check("...and goes in", in_goal(b), "ends (%.0f, %.0f)" % tuple(b.pos))

# WHIPPED CROSS: the dipper - up, then down into the goal mouth
d = doll(["whipped"], x=420); d.vel = V(700, -1100)
dv = d.vel.normalize(); b = ball_at((d.pos.x + dv.x * 260, d.pos.y + dv.y * 260)); hit(d, b)
check("whipped cross is a dipper path", b.move is not None and b.move["k"] == "whipped")
if b.move:
    y0 = b.pos.y
    pts = fly(b, 3.0)
    check("...it rises then dives in, well under the bar", min(p.y for p in pts) < y0 - 150 and in_goal(b) and b.pos.y > rf.GROUND_Y - rf.GOAL_HEIGHT + 120,
          "ends (%.0f, %.0f)" % tuple(b.pos))

# PRECISION HEADER: a bullet header in their half, a huge clearance in yours
d = doll(["header"]); d.pos = V(1400, 600); d.grounded = False; d.vel = V(900, -200)
hp = d.to_world(d.HEAD_LOCAL); b = ball_at((hp.x + rf.HEAD_R + rf.BALL_RADIUS - 6, hp.y)); hit(d, b)
check("header in their half: on a line into the goal", b.move is not None and b.move["k"] == "header")
if b.move:
    fly(b); check("...and in", in_goal(b), "ends (%.0f, %.0f)" % tuple(b.pos))
d = doll(["header"], x=500); d.pos = V(500, 600); d.grounded = False; d.vel = V(900, -200)
hp = d.to_world(d.HEAD_LOCAL); b = ball_at((hp.x + rf.HEAD_R + rf.BALL_RADIUS - 6, hp.y)); x0 = b.pos.x; hit(d, b)
check("header in your half: a towering clearance", b.move is not None and b.move["k"] == "clear")
if b.move:
    while b.move is not None:
        b.step(1 / 480.0, SEGS, sfx, pt)
    check("...that lands far upfield (%.0f px)" % (b.pos.x - x0), b.pos.x - x0 > 900)

# BULLET PASS: a laser - flat, not dropping
d, b = strike("bullet", 500, vel=(900, 0))
check("bullet pass is a laser path", b.move is not None and b.move["k"] == "bullet")
if b.move:
    y0, x0 = b.pos.y, b.pos.x
    pts = []
    while b.move is not None:
        b.step(1 / 480.0, SEGS, sfx, pt); pts.append(V(b.pos))
    check("...dead flat for %.0f px" % (pts[-1].x - x0), pts[-1].x - x0 > 1000 and max(abs(p.y - y0) for p in pts) < 3)

# DEFLECTOR: the parry, up and away, landing far upfield
d = doll(["deflector"], gk=True, x=300); d.ctx = {"own_half": True}
b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, d.pos.y - 10), (-1600, 0)); x0 = b.pos.x; hit(d, b)
check("deflector parries it onto an arc", "deflector" in d.ps_flash and b.move is not None and b.move["k"] == "parry")
if b.move:
    while b.move is not None:
        b.step(1 / 480.0, SEGS, sfx, pt)
    check("...that lands far upfield (%.0f px)" % (b.pos.x - x0), b.pos.x - x0 > 900)

# ---- the PASSIVE ones (6 Nov, Hubi: "playstyles are passive abilities"): each makes HIS throw,
# touch or duel a bit better in its moment, and none of them ever moves him or the ball by itself
def throw_speed(keys, setup, direction=(1, -0.2), power=1500, **kw):
    d = doll(keys, **kw)
    b = setup(d)
    x0 = d.pos.x
    d.throw(V(*direction), power)
    return d, b, x0


def carry(d):
    b = ball_at((d.pos.x + 60, d.pos.y)); b.carrier, b.carrier_t = d, 0.8; d.ball_ref = b
    return b

# RAPID: quicker on the ball
plain, _b, _x = throw_speed([], carry)
d, b, x0 = throw_speed(["rapid"], carry)
check("rapid: a quicker launch with the ball (%.0f vs %.0f)" % (d.vel.length(), plain.vel.length()),
      "rapid" in d.ps_flash and d.vel.length() > plain.vel.length() * 1.08)
check("...and the ball stays his a bit longer - but it isn't stuck to him", b.carrier_t > 0.8 and b.glue is None)

# TIKI TAKA: a cleaner first touch, the next throw sooner (not at once)
d = doll(["tikitaka"]); d.vel = V(200, 0); d.throw_timer = 0.3
b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, d.pos.y + 10), (-600, 0)); hit(d, b)
check("tiki taka: next throw comes round sooner (%.2f, was 0.30), and nothing is stuck" % d.throw_timer,
      "tikitaka" in d.ps_flash and 0.0 < d.throw_timer < 0.3 and b.glue is None)
d = doll(["tikitaka"]); d.vel = V(200, 0)
b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, d.pos.y + 10), (-100, 0)); hit(d, b)
check("tiki taka quiet on a slow ball", "tikitaka" not in d.ps_flash)

# TRICKSTER: sharper turns with the ball near him
def turn(keys):
    d = doll(keys, x=1000); d.vel = V(1200, 0); d.ctx = {"near_opp": True}
    opp = doll([], x=1150, facing=-1); d.opp_ref = opp
    carry(d); x0 = d.pos.x
    d.throw(V(-1, -0.2), 1500)
    return d, opp, x0
plain, _o, _x = turn([])
d, opp, x0 = turn(["trickster"])
check("trickster: a sharper turn - less of the old run carried over (vx %.0f vs %.0f)" % (d.vel.x, plain.vel.x),
      "trickster" in d.ps_flash and d.vel.x < plain.vel.x - 50)
check("...he stays where he is, and his man isn't frozen", d.pos.x == x0 and opp.throw_timer == 0.0
      and getattr(opp, "daze_t", 0.0) == 0.0)

# RELENTLESS: behind / late - a bit harder, a bit sooner
def clutch(keys, on=True):
    d = doll(keys); d.ball_ref = ball_at((d.pos.x + 400, d.pos.y)); d.ctx = {"clutch": on}
    d.throw(V(1, -0.2), 1500)
    return d
plain, d = clutch([]), clutch(["relentless"])
check("relentless: a bit harder (%.0f vs %.0f) and ready sooner (%.2f vs %.2f)" % (d.vel.length(), plain.vel.length(),
      d.throw_timer, plain.throw_timer), "relentless" in d.ps_flash and d.vel.length() > plain.vel.length() * 1.03
      and d.throw_timer < plain.throw_timer)
check("relentless quiet when it isn't", "relentless" not in clutch(["relentless"], on=False).ps_flash)

# GUARDIAN: stronger in duels in your own half, cleaner tackles
def duel(keys, own):
    A = doll(keys, x=900); B = doll([], x=900 + 2 * rf.BODY_R - 8, facing=-1)
    A.ctx = {"own_half": own}; B.ctx = {}
    A.vel = V(900, 0); B.vel = V(-900, 0)
    rf.player_vs_player(A, B, sfx)
    return A, B
plain, _B = duel([], True)
A, B = duel(["guardian"], True)
check("guardian: holds his ground better in his own half (vx %.0f vs %.0f)" % (A.vel.x, plain.vel.x),
      "guardian" in A.ps_flash and A.vel.x > plain.vel.x)
A2, _B = duel(["guardian"], False)
check("...but not in theirs", abs(A2.vel.x - plain.vel.x) < 1.0)
check("...and nobody is knocked flat or stunned", B.throw_timer == 0.0 and getattr(B, "daze_t", 0.0) == 0.0)

# BRUISER: stronger in hard duels, harder to knock off the ball
outs = []
for keys in ((), ("bruiser",)):
    A, B = duel(keys, False); outs.append((A.vel.x, B.vel.x))
check("bruiser: keeps more of his speed in a hard duel (%.0f vs %.0f)" % (outs[1][0], outs[0][0]), outs[1][0] > outs[0][0])
check("...without sending him flying (his vx %.0f vs %.0f)" % (outs[1][1], outs[0][1]), outs[1][1] < outs[0][1] + 400)

# ANTICIPATE: quicker off the mark in your own half, and after a touch
def own(keys, own_half=True, touched=False):
    d = doll(keys); d.ball_ref = ball_at((d.pos.x + 400, d.pos.y)); d.ctx = {"own_half": own_half}
    if touched:
        d.read_t = 1.5
    d.throw(V(1, -0.2), 1500)
    return d
plain = own([])
d = own(["anticipate"])
check("anticipate: quicker off the mark in his own half (%.0f vs %.0f)" % (d.vel.length(), plain.vel.length()),
      "anticipate" in d.ps_flash and d.vel.length() > plain.vel.length() * 1.05)
d2 = own(["anticipate"], own_half=False)
d3 = own(["anticipate"], own_half=False, touched=True)
check("...not in theirs, but quicker again just after a touch (%.0f vs %.0f)" % (d3.vel.length(), d2.vel.length()),
      abs(d2.vel.length() - plain.vel.length()) < 1.0 and d3.vel.length() > d2.vel.length() * 1.08)
t = doll(["anticipate"]); t.vel = V(600, 0)
b = ball_at((t.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, t.pos.y + 10)); hit(t, b)
check("...a touch starts that moment", getattr(t, "read_t", 0.0) > 0.0)
check("...and it never moves him by itself", not hasattr(rf, "ps_anticipate"))

# RUSH OUT: a keeper comes off his line quicker, and is ready again sooner
def rush(keys, gk=True):
    k = doll(keys, gk=gk, x=300); b = ball_at((520, k.pos.y)); k.ball_ref = b
    k.throw(V(1, -0.2), 1500)
    return k, b
plain, _b = rush([])
k, b = rush(["rushout"])
check("rush out: off his line quicker (%.0f vs %.0f) and ready sooner (%.2f vs %.2f)" % (k.vel.length(), plain.vel.length(),
      k.throw_timer, plain.throw_timer), "rushout" in k.ps_flash and k.vel.length() > plain.vel.length() * 1.1
      and k.throw_timer < plain.throw_timer)
check("...no catch: the ball is just a ball", b.glue is None)

# ACCELERATOR: a streak
d = doll(["accelerator"]); d.ball_ref = ball_at((d.pos.x + 900, d.pos.y)); d.ctx = {}
d.throw(V(1, 0.0), 1500); check("accelerator: speed lines and a bigger launch", d.streak_t > 0 and d.vel.x > 2200, "vx %.0f" % d.vel.x)

# the cooldown
def power_hit(cool=None):
    d = doll(["power"]); d.vel = V(1800, 0)
    if cool is not None:
        d.ps_cool = dict(cool)
    b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, d.pos.y + 10)); hit(d, b)
    return d
d1 = power_hit()
d2 = power_hit(d1.ps_cool)
check("power can't fire twice in a row (cooldown)", "power" in d1.ps_flash and "power" not in d2.ps_flash,
      "cooldown %.1fs" % d1.ps_cool.get("power", 0))
d3 = doll(["power"]); d3.ps_cool = dict(d1.ps_cool); d3.tick_styles(rf.PS_COOL["power"] + 0.1)
d4 = power_hit(d3.ps_cool)
check("...and fires again once it's over", "power" in d4.ps_flash)


# relentless still saves stamina
r = Run(save={}); g = r.g
card = dict(next(c for c in g.cards.values() if c.get("ps")))
card["ps"] = ((rf.PS_BY_KEY["relentless"], 1),)
check("relentless: a half costs less stamina", g.half_cost(card) < rf.STAMINA_PER_HALF)
# the badge pops
d = doll(["header"]); d.ps_fire("header"); d.tick_styles(0.3)
check("badge pops over the player", d.ps_pop is not None and d.ps_pop[0] == "header")
print("\n%d failed" % len(fails), fails)
sys.exit(1 if fails else 0)
