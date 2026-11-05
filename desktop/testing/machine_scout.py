"""THE MACHINE's scouting report, take two: what each card's stats physically DO, in each twist.

    python3 machine_scout.py          (prints the table; --write puts the top three in the game)

Why not win rates: machine_sim.py played CPU v CPU matches and it came out a coin flip whatever
the card or the CPU level (Saka v Bruno 42-54%, an EASY CPU no worse than IMPOSSIBLE) - brain
against brain, goals come from the chaos, not the stats, so a win rate there can't rank cards.
What CAN be measured exactly is what the stats do to the physics, in that twist's world:

  SHOT   how fast the ball leaves him off a full-speed run-up (the twist's ball: GIANT is bigger)
  REACH  how far one full-power throw carries him, flight + skid (the twist's gravity and grip)
  RATE   throws a second: 1 / the wait after a full throw

Each is turned into a z-score across the candidates, and a card's score is the plain average of
the three (no weighting: shooting, getting there first and acting often all count the same). No
dice anywhere, so the same game always gives the same table."""
import json, math, os, re, sys
T = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, T)
from harness import Run, rf
from pygame import Vector2 as V

CANDIDATES = 24
r = Run(save={"coins": 0}, name="save_scout.json")
g = r.g
H = rf.FIXED_DT * rf.WORLD_TIME


class Q:
    def play(self, *a, **k): pass
    def burst(self, *a, **k): pass
    def __getattr__(self, name): return lambda *a, **k: None


q = Q()


def world(twist):
    g.mode = "gauntlet"
    g.match_twist = twist
    g.half = 1
    g.apply_twist()


def fresh(card, x):
    d = rf.Player(x, 1, None)
    d.set_stats(g.upgraded(card) if hasattr(g, "upgraded") else card)
    d.ps_on = {}
    d.ctx = {}
    d.pos = V(x, rf.GROUND_Y - rf.FOOT_OFFSET)
    d.vel = V(0, 0)
    d.angle = 0.0
    d.av = 0.0
    for l in d.limbs:
        l.reset(0.0)
    d.grounded = True
    return d


def reach(card):
    d = fresh(card, 200.0)
    for _ in range(30):
        d.step(H, g.segments, q, q)
    d.throw_timer = 0.0
    x0 = d.pos.x
    d.throw(V(1, -1).normalize(), d.max_power())
    wait = d.throw_timer
    for k in range(int(8.0 / H)):
        d.step(H, g.segments, q, q)
        if k > 30 and d.on_ground and d.vel.length() < 15.0:
            break
    return d.pos.x - x0, wait


def shot(card, run=1300.0):
    d = fresh(card, 700.0)
    d.vel = V(run, 0)
    b = rf.Ball()
    b.radius = g.ball.radius
    b.frozen = False
    b.vel = V(0, 0)
    b.pos = d.pos + V(70 + b.radius, 10)
    for _ in range(400):
        d.pos += d.vel * (1 / 480.0)
        v0 = V(b.vel)
        if rf.ball_vs_player(b, d, q, q, lambda *a, **k: None) and (b.vel - v0).length() > 1.0:
            break
    return b.vel.length()


def z(xs):
    m = sum(xs) / len(xs)
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs)) or 1.0
    return [(x - m) / sd for x in xs]


if __name__ == "__main__":
    pool = sorted((c for c in g.cards.values() if c["kind"] != "rookie"), key=lambda c: -c["rating"])[:CANDIDATES]
    twists = ["normal"] + list(rf.GT_PLAYABLE_TWISTS)
    best = {}
    for tw in twists:
        world(tw)
        rows = []
        for c in pool:
            rch, wait = reach(c)
            rows.append({"id": c["id"], "rating": c["rating"], "shot": shot(c), "reach": rch,
                         "rate": 1.0 / max(0.05, wait)})
        g.clear_twist()
        zs = {k: z([x[k] for x in rows]) for k in ("shot", "reach", "rate")}
        for i, x in enumerate(rows):
            x["score"] = (zs["shot"][i] + zs["reach"][i] + zs["rate"][i]) / 3.0
        rows.sort(key=lambda x: (-x["score"], -x["rating"]))
        print("\n%s" % rf.TWIST_NAME[tw])
        for x in rows[:6]:
            print("  %-18s %3d   score %+.2f   shot %5.0f px/s   reach %5.0f px   %.2f throws/s"
                  % (x["id"], x["rating"], x["score"], x["shot"], x["reach"], x["rate"]))
        best[tw] = {"ids": [x["id"] for x in rows[:3]], "score": [round(x["score"], 2) for x in rows[:3]],
                    "shot": [int(x["shot"]) for x in rows[:3]], "reach": [int(x["reach"]) for x in rows[:3]],
                    "rate": [round(x["rate"], 2) for x in rows[:3]]}
    if "--write" in sys.argv:
        path = os.path.join(os.path.dirname(T), "game", "ragdoll_football.py")
        src = open(path).read()
        line = "MACHINE = " + json.dumps(best, separators=(", ", ": ")) + "\n"
        src, n = re.subn(r"^MACHINE = .*\n", lambda m: line, src, count=1, flags=re.M)
        assert n == 1
        open(path, "w").write(src)
        print("\nwritten to", path)
