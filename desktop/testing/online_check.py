"""ONLINE 1v1 (5 Nov): two real games in one process, joined by a pretend internet.

    python3 online_check.py

Hubi: "either one player has good ping, the other doesn't have any lag". The host ran the match;
the guest's own throws went to the host and came back. This plays the same match through the
old protocol (1) and the new one (2) over the same connection - 60 ms each way, a little jitter,
3% of fast packets lost - with a CPU brain driving each player's own doll, and measures what
each player feels:
  * own doll pulled about by the network (px per second): the rubber band you feel on your throws
  * the ball yanked away right after YOU touched it (px per touch): your kick being undone
  * how far apart the two screens are (px): the same doll / ball, host's screen vs guest's
and that both screens agree on the score."""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Run, rf, pygame
Vector2 = rf.Vector2

fails = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


class Wire:
    """One direction of the connection: messages arrive one_way ms later (+ jitter); the fast
    kinds can be lost, the reliable ones can't (WebRTC's two channels)."""
    FAST = {"snap", "me", "ping", "pong"}

    def __init__(self, one_way, jitter, loss, rnd):
        self.q, self.one_way, self.jitter, self.loss, self.rnd = [], one_way, jitter, loss, rnd
        self.sent = 0

    def put(self, msg, now):
        if msg.get("t") in self.FAST and self.rnd.random() < self.loss:
            return
        self.sent += 1
        at = now + self.one_way + self.rnd.uniform(-self.jitter, self.jitter)
        if msg.get("t") not in self.FAST and self.q:
            at = max(at, self.q[-1][0])          # reliable + ordered
        self.q.append((at, rf.json.loads(rf.json.dumps(msg))))
        self.q.sort(key=lambda x: x[0])

    def take(self, now):
        out = [m for at, m in self.q if at <= now]
        self.q = [(at, m) for at, m in self.q if at > now]
        return out


class FakeLink:
    def __init__(self, out_wire, in_wire):
        self.on, self.out, self.inn = True, out_wire, in_wire

    def poll(self):
        return self.inn.take(pygame.time.get_ticks())

    def send(self, msg):
        self.out.put(msg, pygame.time.get_ticks())

    def chat(self, text): pass
    def result(self, home, away): pass
    def connected_hint(self): return True


def play(proto, seconds=150, one_way=60, jitter=12, loss=0.03, seed=5):
    rf.NET_PROTO = proto
    rnd = random.Random(seed)
    random.seed(seed)
    owned = {"WC_FRA_mbappe": 1, "INT_messi": 1}
    save = {"coins": 1000, "tutorial_done": True, "starter_opened": True, "owned": owned,
            "squad": list(owned)}
    H = Run(save=save, name="save_host.json", headless=True).g
    G = Run(save=save, name="save_guest.json", headless=True).g
    a, b = Wire(one_way, jitter, loss, rnd), Wire(one_way, jitter, loss, rnd)
    H.net, G.net = FakeLink(a, b), FakeLink(b, a)
    H.start_pvp({"role": "host", "card": "WC_FRA_mbappe", "oppCard": "INT_messi", "name": "HOST", "oppName": "GUEST"})
    G.start_pvp({"role": "guest", "card": "INT_messi", "oppCard": "WC_FRA_mbappe", "name": "GUEST", "oppName": "HOST"})
    for g in (H, G):
        g.input_lock = 0.0
        g.tut = None
    brains = {}
    stats = {"own_pull": {"host": 0.0, "guest": 0.0}, "kick_undo": {"host": [], "guest": []},
             "gap_guest_doll": [], "gap_host_doll": [], "gap_ball": [], "guest_touches": 0,
             "goals": 0, "errors": 0}
    flip = lambda v: Vector2(rf.WIDTH - v.x, v.y)

    # the network's pulls on each player's OWN doll, and on the ball just after their own touch
    def watch(g, who):
        own = g.player
        last_touch = {"t": -9.0}
        real_touched = g.pvp_touched

        def touched():
            last_touch["t"] = g.net_now()
            if who == "guest":
                stats["guest_touches"] += 1
            return real_touched()
        g.pvp_touched = touched
        for name in ("apply_snapshot", "apply_remote_doll", "take_guest_kick", "apply_remote_throw"):
            real = getattr(g, name)

            def wrap(*args, _real=real, **kw):
                p0, b0, st0 = Vector2(own.pos), Vector2(g.ball.pos), g.state
                out = _real(*args, **kw)
                if st0 == rf.PLAY and g.state == rf.PLAY:          # (a kick-off reset isn't a pull)
                    stats["own_pull"][who] += (own.pos - p0).length()
                if g.net_now() - last_touch["t"] < 0.35:
                    stats["kick_undo"][who].append((g.ball.pos - b0).length())
                return out
            setattr(g, name, wrap)
        # the brain throws: as a click would (an older guest sends the release point)
        real_throw = own.throw

        def throw(d, power, *rest, **kw):
            ok = real_throw(d, power, *rest, **kw)
            if ok and who == "guest":
                if g.pvp_v2():
                    g.send_me()
                else:
                    span = (power - rf.THROW_MIN) / max(1.0, own.max_power() - rf.THROW_MIN)
                    tgt = own.pos + Vector2(d).normalize() * max(2.0, span * own.drag_range())
                    g.net.send({"t": "input", "x": round(rf.WIDTH - tgt.x, 1), "y": round(tgt.y, 1)})
            return ok
        own.throw = throw
        # check_goal on the guest's own screen: is it ahead of the host? (old protocol only)
    watch(H, "host")
    watch(G, "guest")
    # a touch on the old protocol never called pvp_touched: note it from the contact itself
    for g, who in ((H, "host"), (G, "guest")):
        real_step = g.physics_step

        def step(h, _g=g, _who=who, _real=real_step):
            lt = _g.last_touch
            _real(h)
            if not _g.pvp_v2() and _g.last_touch == "home" and lt != "home" and _g.mode == "pvp":
                _g.pvp_touched()
        g.physics_step = step

    dt = 1 / 60.0
    frames = int(seconds / dt)
    for f in range(frames):
        pygame.time.advance(dt * 1000.0)
        for g in (H, G):
            if g.state == rf.VERSUS:
                g.versus["t"] = 99.0
            if g.state == rf.PLAY:
                br = brains.get(id(g))
                if br is None or br.doll is not g.player:
                    br = brains[id(g)] = rf.Brain(g.player, 1, skill=0.85, opponent=g.cpu)
                br.update(dt * g.slowmo * rf.WORLD_TIME, g.ball)
            if g.state == rf.GOAL and g is H and f % 60 == 0:
                pass                                          # the host's banner moves on by itself (v2) ...
            try:
                g.handle_events()
                g.update(dt)
            except Exception as exc:
                stats["errors"] += 1
                if stats["errors"] < 3:
                    import traceback; traceback.print_exc()
        if proto == 1 and H.state == rf.GOAL and H.state_timer < -1.0:
            H.advance_after_goal()                            # (v1: someone clicks)
        if proto == 1 and H.state == rf.GOAL:
            H.state_timer -= dt
        if H.state == rf.PLAY and G.state == rf.PLAY:
            stats["gap_guest_doll"].append((H.cpu.pos - flip(G.player.pos)).length())
            stats["gap_host_doll"].append((H.player.pos - flip(G.cpu.pos)).length())
            stats["gap_ball"].append((H.ball.pos - flip(G.ball.pos)).length())
        if H.state == rf.FULLTIME:
            break
    for _ in range(30):                                       # let the last messages land
        pygame.time.advance(dt * 1000.0)
        for g in (H, G):
            g.update(dt)
    stats["ended"] = (H.state == rf.FULLTIME, G.state == rf.FULLTIME, H.half, G.half)
    stats["score_host"] = (H.score_home, H.score_away)
    stats["score_guest"] = (G.score_away, G.score_home)       # the guest sees it mirrored
    stats["secs"] = f * dt
    stats["accepted"] = H.pvp.get("kick_seen", 0) if H.pvp else 0
    stats["kicks"] = G.pvp.get("kick_id", 0) if G.pvp else 0
    return stats


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def show(name, s):
    print("%s  (%.0f s of match)" % (name, s["secs"]))
    for who in ("host", "guest"):
        print("   %-5s own doll pulled by the network %6.0f px/s   ball yanked after own touch %5.1f px/frame"
              % (who, s["own_pull"][who] / max(1, s["secs"]), mean(s["kick_undo"][who])))
    print("   screens apart: guest doll %.0f px, host doll %.0f px, ball %.0f px   score host %s guest %s"
          % (mean(s["gap_guest_doll"]), mean(s["gap_host_doll"]), mean(s["gap_ball"]), s["score_host"], s["score_guest"]))


old = play(1)
show("OLD (host runs it, guest sends clicks)", old)
new = play(2)
show("NEW (own doll is yours, your kick is yours)", new)
print("   guest kicks: %d, the host took %d of them" % (new["kicks"], new["accepted"]))

check(new["errors"] == 0 and old["errors"] == 0, "no crashes on either side")
check(new["own_pull"]["guest"] == 0.0, "the guest's own doll is never pulled about by the network")
check(new["own_pull"]["host"] == 0.0, "nor the host's")
check(old["own_pull"]["guest"] > 50 * old["secs"], "(the old protocol did pull the guest's doll: %.0f px/s)"
      % (old["own_pull"]["guest"] / max(1, old["secs"])))
check(mean(new["kick_undo"]["guest"]) < 0.5 * mean(old["kick_undo"]["guest"]) or mean(new["kick_undo"]["guest"]) < 4.0,
      "the guest's touches stick: the ball is yanked %.1f px/frame after them (was %.1f)"
      % (mean(new["kick_undo"]["guest"]), mean(old["kick_undo"]["guest"])))
check(mean(new["gap_ball"]) < mean(old["gap_ball"]) * 1.25 + 5,
      "the two screens' balls stay as close as before or closer (%.0f px vs %.0f)" % (mean(new["gap_ball"]), mean(old["gap_ball"])))
check(new["ended"][:2] == (True, True), "the match gets to full time on both screens, second half and all %s" % (new["ended"],))
check(new["score_host"] == new["score_guest"], "both screens show the same score %s" % (new["score_host"],))
check(new["kicks"] > 0 and new["accepted"] >= 0.8 * new["kicks"],
      "the host takes the guest's kicks (%d of %d)" % (new["accepted"], new["kicks"]))
print("ALL PASS" if not fails else "%d FAILED" % len(fails))
sys.exit(1 if fails else 0)
