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

# 7 rapid: throw while carrying
d = doll(["rapid"]); b = ball_at((d.pos.x + 60, d.pos.y)); b.carrier, b.carrier_t = d, 0.8; d.ball_ref = b
d.throw(V(1, -0.2), 1500); check("rapid fires when carrying, ball knocked on", "rapid" in d.ps_flash and b.vel.x > 200, "ball vx %.0f" % b.vel.x)

# 8 rush out: keeper only, ball in own box
d = doll(["rushout"], gk=True, x=300); b = ball_at((420, d.pos.y)); d.ball_ref = b
d.throw(V(1, -0.2), 1500); check("rush out fires for a keeper", "rushout" in d.ps_flash, "wait %.2f" % d.throw_timer)
d = doll(["rushout"], gk=False, x=300); d.ball_ref = b
d.throw(V(1, -0.2), 1500); check("rush out does nothing on an outfield player", "rushout" not in d.ps_flash)

# 9 anticipate: steal a carried ball
c = doll([], x=1000, facing=-1); t = doll(["anticipate"], x=900)
b = ball_at((t.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, t.pos.y + 10), (-200, 0)); b.carrier, b.carrier_t = c, 0.8
t.vel = V(300, 0); hit(t, b)
check("anticipate steals cleanly", "anticipate" in t.ps_flash and b.carrier is t and b.vel.x > 0, "ball vx %.0f" % b.vel.x)
check("anticipate leaves the carrier stunned", c.throw_timer >= rf.PS_STUN * 0.99, "his wait %.2f" % c.throw_timer)

# 10 guardian: barge the carrier
a = doll(["guardian"], x=900); hb = doll([], x=900 + 2 * rf.BODY_R - 8, facing=-1)
a.vel = V(1200, 0); hb.vel = V(-200, 0)
b = ball_at((hb.pos.x + 60, hb.pos.y)); b.carrier, b.carrier_t = hb, 0.8
rf.player_vs_player(a, hb, sfx, b)
check("guardian wins the ball off the carrier", "guardian" in a.ps_flash and b.carrier is a and b.vel.x < 0, "ball vx %.0f" % b.vel.x)
check("guardian leaves the carrier stunned", hb.throw_timer >= rf.PS_STUN * 0.99, "his wait %.2f" % hb.throw_timer)

# 11 bruiser in a duel
outs = []
for keys in ((), ("bruiser",)):
    A = doll(keys, x=900); B = doll([], x=900 + 2 * rf.BODY_R - 8, facing=-1)
    A.vel = V(900, 0); B.vel = V(-900, 0)
    rf.player_vs_player(A, B, sfx); outs.append(A.vel.x)
check("bruiser keeps more of his speed in a duel", outs[1] > outs[0], "%.0f -> %.0f" % tuple(outs))

# 12 deflector: keeper block goes up and wide
d = doll(["deflector"], gk=True, x=300); d.ctx = {"own_half": True}
b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, d.pos.y - 10), (-1600, 0)); hit(d, b)
check("deflector pushes a shot up and away", "deflector" in d.ps_flash and b.vel.y < 0 and b.vel.x > 0, "(%.0f, %.0f)" % (b.vel.x, b.vel.y))

# 13 bullet: flat and zipping
d = doll(["bullet"]); d.vel = V(900, 0); b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, d.pos.y + 10)); hit(d, b)
check("bullet pass stays flat", "bullet" in d.ps_flash and b.vel.y > -abs(b.vel.x) * 0.13 and b.zip_t > 0, "(%.0f, %.0f)" % (b.vel.x, b.vel.y))

# 14 tiki taka: a moving ball taken first time with a soft touch - yours, and you go again at once
d = doll(["tikitaka"]); d.vel = V(200, 0); d.throw_timer = 0.3
b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, d.pos.y + 10), (-600, 0)); hit(d, b)
check("tiki taka fires on a first-time soft touch", "tikitaka" in d.ps_flash and b.vel.x > 0 and d.throw_timer == 0.0,
      "ball vx %.0f, wait %.2f" % (b.vel.x, d.throw_timer))
d = doll(["tikitaka"]); d.vel = V(200, 0)
b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, d.pos.y + 10), (-100, 0)); hit(d, b)
check("tiki taka quiet on a slow ball", "tikitaka" not in d.ps_flash)

# 15 trickster: carrying, opponent close
d = doll(["trickster"]); d.ctx = {"near_opp": True}; d.vel = V(260, 0)
b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 6, d.pos.y + 10), (-100, 0)); b.carrier, b.carrier_t = d, 0.8; hit(d, b)
check("trickster fires carrying near an opponent", "trickster" in d.ps_flash)

# 16 chip: under the ball, their keeper off his line
d = doll(["chip"], x=rf.WIDTH - 800); d.ctx = {"opp_off_line": True}; d.vel = V(600, -1100)
dv = d.vel.normalize(); b = ball_at((d.pos.x + dv.x * 260, d.pos.y + dv.y * 260)); hit(d, b)
# the lob: follow the ball's own arc and see where it comes down at the goal line
lob_ok = False
if "chip" in d.ps_flash:
    p, v = V(b.pos), V(b.vel)
    for _ in range(2000):
        hh = 1 / 240.0
        v.y += rf.BALL_GRAVITY * hh
        v *= 1.0 - rf.BALL_AIR_DRAG * hh
        p += v * hh
        if p.x >= rf.WIDTH - rf.GOAL_DEPTH:
            lob_ok = rf.GROUND_Y - rf.GOAL_HEIGHT < p.y < rf.GROUND_Y
            break
check("chip shot lobs and drops under the bar", lob_ok, "vel (%.0f, %.0f) arrives y %.0f" % (b.vel.x, b.vel.y, p.y))

# 17 whipped: far out, rising
d = doll(["whipped"], x=420); d.vel = V(700, -1100)
dv = d.vel.normalize(); b = ball_at((d.pos.x + dv.x * 260, d.pos.y + dv.y * 260)); hit(d, b)
check("whipped cross fires from far out", "whipped" in d.ps_flash and b.bend > 0, "bend %.2f" % b.bend)

# 18 relentless: stamina
r = Run(save={}); g = r.g
card = dict(next(c for c in g.cards.values() if c.get("ps")))
card["ps"] = ((rf.PS_BY_KEY["relentless"], 1),)
check("relentless: a half costs less stamina", g.half_cost(card) < rf.STAMINA_PER_HALF, "%d vs %d" % (g.half_cost(card), rf.STAMINA_PER_HALF))

# finesse: spun hit bends earlier
ok = False
for dy in range(-80, 81, 8):
    for keys in (("finesse",),):
        d = doll(keys, x=rf.WIDTH - 1400); d.pos = V(d.pos.x, rf.GROUND_Y - 420); d.grounded = False; d.vel = V(1500, 0)
        b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 4, d.pos.y + dy)); hit(d, b)
        if "finesse" in d.ps_flash:
            ok = True
check("finesse fires on a spun hit", ok)
# ...and it is a real curler: much more bend than the same hit without it
bends = {}
for keys in ((), ("finesse",)):
    best = 0.0
    for dy in range(-80, 81, 8):
        d = doll(keys, x=rf.WIDTH - 1400); d.pos = V(d.pos.x, rf.GROUND_Y - 420); d.grounded = False; d.vel = V(1500, 0)
        b = ball_at((d.pos.x + rf.BODY_R + rf.BALL_RADIUS - 4, d.pos.y + dy)); hit(d, b)
        best = max(best, b.bend)
    bends[keys] = best
check("finesse bends far more", bends[("finesse",)] > bends[()] + 0.2 and bends[("finesse",)] >= 0.40,
      "%.2f -> %.2f rad" % (bends[()], bends[("finesse",)]))

# 28 Oct: a PlayStyle can't fire again until its cooldown is over
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

# the stuns: Guardian, Anticipate and Trickster leave the other player unable to throw for a moment
d = doll(["trickster"]); opp = doll([], x=1100, facing=-1); d.opp_ref = opp
b = ball_at((d.pos.x + 60, d.pos.y)); b.carrier, b.carrier_t = d, 0.8; d.ball_ref = b; d.ctx = {"near_opp": True}
d.throw(V(-1, -0.2), 1500)
check("trickster: a sharp turn through him, and he's frozen", "trickster" in d.ps_flash and d.trick_t > 0
      and opp.throw_timer >= rf.PS_STUN * 0.99, "his wait %.2f" % opp.throw_timer)
d = doll(["relentless"]); d.ball_ref = ball_at((d.pos.x + 400, d.pos.y)); d.ctx = {"clutch": True}
d.throw(V(1, -0.2), 1500)
check("relentless fires when behind / late", "relentless" in d.ps_flash)
d = doll(["relentless"]); d.ball_ref = ball_at((d.pos.x + 400, d.pos.y)); d.ctx = {"clutch": False}
d.throw(V(1, -0.2), 1500)
check("relentless quiet when it isn't", "relentless" not in d.ps_flash)

# the popup and the HUD don't crash
d = doll(["header"]); d.ps_fire("header"); d.tick_styles(0.3)
check("badge pops over the player", d.ps_pop is not None and d.ps_pop[0] == "header")
print("\n%d failed" % len(fails), fails)

sys.exit(1 if fails else 0)
