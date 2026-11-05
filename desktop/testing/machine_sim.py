"""THE EXPERIMENT THAT DIDN'T WORK (30 Oct) - kept so nobody tries it again without knowing.

    python3 machine_sim.py N1 N2 TWIST,TWIST      (writes out/machine_part_*.json)

The first plan for THE MACHINE: every strong card plays short CPU v CPU matches against a panel of
strong cards, both sides on the HARD brain, and the best goal difference wins. It ran (~30 min on
two cores) and the numbers were noise: the same check with Saka against Bruno gave 42-54% wins
whether the CPU was EASY or IMPOSSIBLE. Brain against brain, goals come from the chaos, not the
stats, so a win rate there can't rank cards. machine_scout.py measures the physics instead."""
import json, os, random, sys, time
T = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, T)
from harness import Run, rf, pygame

MATCH = float(os.environ.get("MATCH_SECONDS", 40))           # one short match, seconds of play
CANDIDATES = int(os.environ.get("CANDIDATES", 20))
PANEL = ("CHE_palmer", "WC_FRA_mbappe", "ARS_saka", "STAR_henry")   # 120-122: strong, varied
TWISTS = [t[0] for t in rf.TWISTS if t[0] != "derby"]        # derby is points, not physics

r = Run(save={"coins": 0}, name="save_machine_%d.json" % os.getpid())
g = r.g
rf.CPU_LOSING_BONUS = 0.0


def set_twist(key):
    g.mode = "gauntlet"
    g.match_twist = key
    g.half = 1
    g.apply_twist()


def duel(mine, theirs, twist, seconds):
    """Goals (mine, theirs) in `seconds` of play, both brains at HARD."""
    g.mode = "free"
    g.my_card, g.cpu_card = mine, theirs
    g.player.set_stats(mine)
    g.cpu.set_stats(theirs)
    g.brain.skill = rf.DIFFICULTY[2][1]
    g.brain.impossible = False
    g.new_match()
    set_twist(twist)
    g.mode = "free"
    g.versus = None
    g.state = rf.KICKOFF
    g.state_timer = 0.0
    me = rf.Brain(g.player, 1, skill=rf.DIFFICULTY[2][1], opponent=g.cpu)
    played = 0.0
    while played < seconds:
        if g.state == rf.PLAY:
            if me.doll is not g.player:
                me = rf.Brain(g.player, 1, skill=rf.DIFFICULTY[2][1], opponent=g.cpu)
            me.update(1 / 60.0 * rf.WORLD_TIME, g.ball)
            played += 1 / 60.0
            g.match_time = 1.0                                  # never reach half time
        r.frames(1)
        if g.state == rf.GOAL:
            g.advance_after_goal()                              # the click after the banner
        if g.state == rf.FULLTIME:
            break
    out = (g.score_home, g.score_away)
    g.clear_twist()
    return out


def score(c, tw, n, panel, rows):
    row = rows.setdefault(c["id"], {"id": c["id"], "rating": c["rating"], "n": 0, "gd": 0, "gf": 0})
    for k in range(n):
        a, b = duel(c, panel[(row["n"] + k) % len(panel)], tw, MATCH)
        row["gd"] += a - b
        row["gf"] += a
    row["n"] += n
    return row


if __name__ == "__main__":
    # python3 machine_sim.py N1 N2 TWIST,TWIST  - stage 1: every candidate N1 matches; stage 2: the
    # best 8 for that twist N2 more each (the top is what matters, so that's where the matches go)
    N1 = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    N2 = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    only = sys.argv[3].split(",") if len(sys.argv) > 3 else TWISTS
    pool = [c for c in g.cards.values() if c["kind"] != "rookie"]
    pool.sort(key=lambda c: -c["rating"])
    cands = pool[:CANDIDATES]
    panel = [g.cards[k] for k in PANEL]
    random.seed(5)
    t0 = time.time()
    part = {}
    for tw in only:
        rows = {}
        for c in cands:
            score(c, tw, N1, panel, rows)
        key = lambda x: (-x["gd"] / float(x["n"]), -x["gf"] / float(x["n"]), -x["rating"])
        for x in sorted(rows.values(), key=key)[:8]:
            score(g.cards[x["id"]], tw, N2, panel, rows)
        ranked = sorted(rows.values(), key=key)
        for x in ranked:
            x["gd"] = round(x["gd"] / float(x["n"]), 3)
            x["gf"] = round(x["gf"] / float(x["n"]), 3)
        part[tw] = ranked
        print(tw, [(x["id"], x["gd"], x["n"]) for x in ranked[:5]], "%.0fs" % (time.time() - t0), flush=True)
    name = "machine_part_%s.json" % "_".join(only)
    with open(os.path.join(T, "out", name), "w") as fh:
        json.dump(part, fh, indent=1)
    print("wrote", name)
