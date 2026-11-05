"""cardfig.py - copied verbatim from the project (render only)."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

f32 = np.float32
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def V(*a):
    return np.array(a, dtype=f32)


def unit(v):
    v = np.asarray(v, dtype=f32)
    return v / np.linalg.norm(v)


def R_euler(yaw=0.0, pitch=0.0, roll=0.0):
    y, p, r = [math.radians(a) for a in (yaw, pitch, roll)]
    Ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(p), math.sin(p)], [0, -math.sin(p), math.cos(p)]])
    Rz = np.array([[math.cos(r), math.sin(r), 0], [-math.sin(r), math.cos(r), 0], [0, 0, 1]])
    return (Ry @ Rx @ Rz).astype(f32)


def ell(p, c, r):
    c = np.asarray(c, f32)
    r = np.asarray(r, f32)
    q = (p - c) / r
    k0 = np.sqrt((q * q).sum(1))
    q2 = q / r
    k1 = np.sqrt((q2 * q2).sum(1))
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)


def sph(p, c, r):
    d = p - np.asarray(c, f32)
    return np.sqrt((d * d).sum(1)) - r


def cap(p, a, b, ra, rb=None):
    a = np.asarray(a, f32)
    b = np.asarray(b, f32)
    rb = ra if rb is None else rb
    pa = p - a
    ba = b - a
    h = np.clip((pa @ ba) / float(ba @ ba), 0.0, 1.0)
    d = pa - h[:, None] * ba
    return np.sqrt((d * d).sum(1)) - (ra + (rb - ra) * h)


def rbox(q, half, r):
    d = np.abs(q) - (np.asarray(half, f32) - r)
    out = np.sqrt((np.maximum(d, 0) ** 2).sum(1))
    return out + np.minimum(d.max(1), 0) - r


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b + (a - b) * h - k * h * (1.0 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def mirror(q):
    m = q.copy()
    m[:, 0] = np.abs(m[:, 0])
    return m


def seg_dist2d(x, y, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    h = np.clip(((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy), 0, 1)
    return np.hypot(x - ax - h * dx, y - ay - h * dy), h


RAMPS = {
    "skin_fair":  [(138, 72, 74), (190, 114, 100), (226, 156, 130), (244, 190, 160), (255, 222, 196)],
    "skin_light": [(110, 58, 54), (160, 96, 78), (204, 140, 108), (230, 176, 140), (250, 212, 178)],
    "skin_tan":   [(86, 46, 40), (130, 76, 56), (174, 112, 80), (206, 146, 108), (232, 182, 142)],
    "skin_brown": [(58, 32, 30), (92, 54, 42), (128, 80, 58), (162, 108, 78), (194, 140, 104)],
    "skin_dark":  [(40, 24, 26), (66, 40, 36), (94, 60, 48), (124, 84, 64), (156, 112, 86)],
    "blond":      [(116, 84, 52), (168, 130, 74), (210, 174, 106), (236, 206, 140), (252, 232, 178)],
    "blond_dark": [(74, 54, 40), (106, 80, 54), (140, 110, 74), (172, 142, 98), (200, 172, 124)],
    "brown":      [(24, 16, 16), (40, 27, 24), (58, 39, 31), (78, 53, 40), (102, 72, 54)],
    "black":      [(8, 8, 12), (17, 15, 20), (28, 25, 31), (41, 37, 45), (60, 55, 66)],
    "red":        [(84, 10, 40), (134, 16, 42), (182, 24, 40), (214, 40, 44), (238, 78, 64)],
    "navy":       [(8, 12, 40), (16, 24, 68), (28, 42, 104), (48, 68, 142), (84, 108, 184)],
    "yellow":     [(142, 86, 12), (198, 138, 14), (244, 194, 30), (255, 224, 84), (255, 244, 160)],
    "white":      [(104, 112, 150), (160, 168, 198), (210, 214, 230), (238, 240, 248), (255, 255, 255)],
    "teeth":      [(150, 140, 150), (196, 190, 196), (232, 228, 226), (250, 248, 244), (255, 255, 255)],
    "eyewhite":   [(150, 140, 150), (190, 184, 190), (224, 220, 222), (240, 238, 238), (252, 252, 252)],
    "iris_blue":  [(22, 30, 48)] * 2 + [(34, 48, 76)] * 3,
    "iris_brown": [(26, 14, 12)] * 2 + [(44, 24, 18)] * 3,
    "lash":       [(40, 22, 24)] * 5,
    "mouth":      [(52, 12, 22)] * 3 + [(76, 20, 30)] * 2,
    "lip":        [(120, 50, 58), (160, 76, 78), (196, 108, 102), (216, 134, 122), (232, 160, 146)],
    "lip_dark":   [(64, 28, 34), (92, 44, 46), (124, 62, 60), (150, 82, 76), (176, 104, 94)],
    "orange":     [(118, 40, 18), (174, 66, 14), (226, 98, 16), (248, 130, 32), (255, 172, 84)],
    "green":      [(4, 42, 36), (8, 70, 48), (14, 102, 62), (36, 136, 82), (86, 176, 118)],
    "blue":       [(10, 18, 66), (18, 34, 108), (28, 56, 152), (48, 88, 192), (94, 132, 226)],
    "charcoal":   [(8, 12, 14), (18, 26, 26), (30, 42, 40), (48, 64, 60), (76, 96, 90)],
    "brown_mid":  [(50, 30, 24), (80, 52, 38), (114, 78, 54), (148, 108, 76), (184, 144, 106)],
    "deep_navy":  [(6, 9, 30), (11, 18, 52), (18, 30, 80), (28, 46, 108), (46, 70, 142)],
    "sky":        [(44, 78, 138), (72, 118, 184), (112, 164, 220), (156, 200, 240), (206, 232, 252)],
    "gold":       [(120, 76, 20), (170, 116, 30), (214, 164, 54), (240, 200, 96), (255, 232, 160)],
    "brown_dark": [(16, 11, 12), (28, 19, 18), (42, 29, 24), (58, 40, 32), (78, 56, 44)],
}
MATS = {}


def mat(name, ramp=None, weight=1.0):
    if name not in MATS:
        MATS[name] = (len(MATS), ramp or name, weight)
    return MATS[name][0]


def mat_tables():
    n = len(MATS)
    rgb = np.zeros((n, 5, 3), np.uint8)
    w = np.ones(n, f32)
    for name, (i, ramp, weight) in MATS.items():
        rgb[i] = RAMPS[ramp]
        w[i] = weight
    return rgb, w


class Kit:
    def __init__(self, body="red", sleeve=None, collar=None, number="yellow", shorts="navy",
                 number_txt="10", number_y=-16.8, raglan=False, pinstripe=0.0,
                 badge=("yellow", "red"), badge_x=7.6, badge_y=-8.6,
                 piping=None, cuff=None, pattern=None, alt=None, long_sleeve=False,
                 collar_w=1.25, sash=None, band=None, flash=None, number_x=0.0, back=False, name_txt=None):
        sleeve = sleeve or body
        collar = collar or body
        self.__dict__.update(locals())

    def print_on(self):
        names = [self.body] + [n for n in (self.alt, self.sash, self.band and self.band[0]) if n]
        return {MATS[n][0] for n in names if n in MATS}

    def paint(self, q, sleeve, sl_t, collar):
        x, y, z = q[:, 0], q[:, 1], q[:, 2]
        m = np.full(len(q), mat(self.body), np.int32)
        off = np.zeros(len(q), np.int32)
        front = z > 0.0
        if self.pinstripe:
            u = np.abs(((x / self.pinstripe) + 0.5) % 1.0 - 0.5) * self.pinstripe
            off[(u < 0.26) & ~sleeve] = -1
        if self.pattern == "checks":
            s = 6.0
            on = ((np.floor((x + 0.5 * s) / s) + np.floor((y + 3.0) / s)) % 2) == 0
            m[on] = mat(self.alt)
        elif self.pattern == "swirl":
            w = np.sin(x * 0.46 + 1.9 * np.sin(y * 0.30 + 0.6)) * np.sin(y * 0.42 + 0.35 * x + 1.0)
            m[w > 0.50] = mat(self.alt)
            off[(w > 0.24) & (w <= 0.50)] = 1
        elif self.pattern == "zig":
            tri = np.abs(((x / 2.4) % 2.0) - 1.0) * 2.2
            off[((y + tri) % 3.4) < 0.9] = 1
        elif self.pattern == "hoop":
            m[(y < -8.0) & (y > -15.5)] = mat(self.alt)
        yoke = np.zeros(len(q), bool)
        if self.raglan:
            yoke = (np.abs(x) - 6.2 - 0.74 * np.maximum(-y, 0.0) > 0) & (y > -14.5)
        if self.raglan or self.sleeve != self.body:
            other = sleeve | yoke
            m[other] = mat(self.sleeve)
            off[other] = 0
        if self.sash:
            d = (y + 4.0) + 0.62 * (x - 2.0)
            on = front & (np.abs(d) < 2.3) & (x > -13.0) & (x < 13.0) & ~sleeve
            m[on] = mat(self.sash)
        if self.band:
            colour, bx0, bx1 = self.band
            on = (x > bx0) & (x < bx1) & ~sleeve
            m[on] = mat(colour)
            off[on] = 0
            edge = ((np.abs(x - bx0) < 0.45) | (np.abs(x - bx1) < 0.45)) & ~sleeve & front
            off[edge & on] = -1
        if self.flash:
            ax = np.abs(x)
            curve = ax - 5.4 - 0.050 * (y + 2.0) ** 2
            on = front & ~sleeve & (np.abs(curve) < 1.15) & (y < 0.5) & (y > -15.5)
            m[on] = mat("flash", self.flash, 1.4)
            off[on] = 0
        if self.piping and self.raglan:
            seam = np.abs(np.abs(x) - 6.2 - 0.74 * np.maximum(-y, 0.0)) < 0.30
            pipe = seam & (y > -14.5) & (y < 1.0) & front & ~sleeve
            m[pipe] = mat("piping", self.piping, 1.6)
        if self.cuff and not self.long_sleeve:
            m[sleeve & (sl_t > 0.86)] = mat("cuff", self.cuff, 1.3)
        m[collar] = mat(self.collar)
        off[collar] = 0
        return m, off

    def stamps(self):
        if self.back:
            # 30 Oct: shot from behind - the number (and the name above it) on the back of the shirt.
            # Rows are mirrored here because the torso's x axis points away from us when he's turned round.
            out = [([r[::-1] for r in number_rows(self.number_txt)], {"#": mat("number", self.number, 1.0)},
                    (-self.number_x, self.number_y + 1.0, -11.4), 1)]
            if self.name_txt:
                out.append(([r[::-1] for r in name_rows(self.name_txt)], {"#": mat("number", self.number, 1.0)},
                            (0.0, self.number_y + 10.5, -11.0), 1))
            return out
        out = [(number_rows(self.number_txt), {"#": mat("number", self.number, 1.0)},
                (self.number_x, self.number_y, 11.6), 1)]
        if self.badge:
            out.append((PIX_BADGE, {"#": mat("badge", self.badge[0], 1.0), "o": mat("badge2", self.badge[1], 1.0)},
                        (self.badge_x, self.badge_y, 10.6), 1))
        return out


PIX_DIGITS = {
    "0": [".####.", "######", "##..##", "##..##", "##..##", "##..##", "##..##", "##..##", "##..##", "######", ".####."],
    "1": ["..##", ".###", "####", "..##", "..##", "..##", "..##", "..##", "..##", "..##", "..##"],
    "2": [".####.", "######", "##..##", "....##", "...###", "..###.", ".###..", "###...", "##....", "######", "######"],
    "3": [".####.", "######", "##..##", "....##", "..####", "..####", "....##", "....##", "##..##", "######", ".####."],
    "4": ["...###", "..####", ".##.##", ".##.##", "##..##", "##..##", "######", "######", "....##", "....##", "....##"],
    "5": ["######", "######", "##....", "##....", "#####.", "######", "....##", "....##", "##..##", "######", ".####."],
    "6": [".####.", "######", "##....", "##....", "#####.", "######", "##..##", "##..##", "##..##", "######", ".####."],
    "7": ["######", "######", "....##", "...##.", "...##.", "..##..", "..##..", ".##...", ".##...", ".##...", ".##..."],
    "8": [".####.", "######", "##..##", "##..##", ".####.", ".####.", "##..##", "##..##", "##..##", "######", ".####."],
    "9": [".####.", "######", "##..##", "##..##", "######", ".#####", "....##", "....##", "##..##", "######", ".####."],
}
PIX_BADGE = ["#####", "#ooo#", "#o#o#", "#ooo#", ".###.", "..#.."]


PIX_LETTERS = {
    "A": [".#.", "#.#", "###", "#.#", "#.#"], "B": ["##.", "#.#", "##.", "#.#", "##."],
    "E": ["###", "#..", "##.", "#..", "###"], "I": ["#", "#", "#", "#", "#"],
    "K": ["#.#", "##.", "#..", "##.", "#.#"], "L": ["#..", "#..", "#..", "#..", "###"],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#"], "N": ["#..#", "##.#", "#.##", "#..#", "#..#"],
    "O": ["###", "#.#", "#.#", "#.#", "###"], "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "S": ["###", "#..", "###", "..#", "###"], "W": ["#...#", "#...#", "#.#.#", "##.##", "#...#"],
    "Y": ["#.#", "#.#", ".#.", ".#.", ".#."],
}


def name_rows(txt):
    rows = [""] * 5
    for i, c in enumerate(txt.upper()):
        g = PIX_LETTERS.get(c)
        if g is None:
            continue
        for r in range(5):
            rows[r] += ("." if rows[r] else "") + g[r]
    return rows


def number_rows(txt, gap=2):
    rows = [""] * 11
    for i, c in enumerate(txt):
        for r in range(11):
            rows[r] += ("." * gap if i else "") + PIX_DIGITS[c][r]
    return rows


def stamp(best, rows, inks, centre, basis, allowed, lift=0):
    h, w = len(rows), len(rows[0])
    A = np.array(basis, float)
    if abs(A[0][0] - 1) < 0.08 and abs(A[1][1] - 1) < 0.08 and abs(A[0][1]) < 0.06 and abs(A[1][0]) < 0.06:
        A = np.eye(2)
    if abs(np.linalg.det(A)) < 0.15:
        return
    Ai = np.linalg.inv(A)
    cx = round(centre[0]) + (0.5 if w % 2 else 0.0)
    cy = round(centre[1]) + (0.5 if h % 2 else 0.0)
    R = int(max(w, h) * 0.9) + 2
    H, W = best.shape
    for py in range(max(0, int(cy) - R), min(H, int(cy) + R + 1)):
        for px in range(max(0, int(cx) - R), min(W, int(cx) + R + 1)):
            u, v = Ai @ np.array([px + 0.5 - cx, py + 0.5 - cy])
            ti, tj = int(math.floor(u + w / 2.0)), int(math.floor(v + h / 2.0))
            if 0 <= ti < w and 0 <= tj < h and rows[tj][ti] != "." and best[py, px] >= 0 \
                    and best[py, px] // 8 in allowed:
                band = min(4, max(0, best[py, px] % 8 + lift))
                best[py, px] = inks[rows[tj][ti]] * 8 + band


HAIR = dict(len=1.0, top=0.0, top_x=0.0, top_z=2.6, quiff=0.0, fringe=0.0, part_x=0.0, side=1.0,
            fade=False, long=0.0, curl=0.0, bun=False, band=None, sideburn=0.0)


class Fig:
    def __init__(self, **kw):
        d = dict(
            skin="skin_fair", hair="blond", hair_side=None, brow=None, iris="iris_brown", kit=None,
            hair_cfg=None, beard=None, beard_ramp=None, lip="lip",
            jaw_w=5.4, face_w=6.4,
            torso=(0.0, 0.0, 0.0),
            torso_x=0.0, shrug=(0.0, 0.0),
            armband=None,
            head=(0.0, 0.0, 0.0), neck_fwd=1.0, neck_dx=0.0,
            eye_open=1.0, gaze=(0.0, 0.0), brow_lift=0.0, brow_slope=0.0,
            mouth="closed", mouth_w=2.5, mouth_h=0.9, smile=0.0, smirk=0.0, snarl=0.0, jaw_drop=0.0,
            left=((-0.14, -0.98, 0.06), (-0.05, -0.97, 0.22), "relaxed"),
            right=((0.14, -0.98, 0.06), (0.05, -0.97, 0.22), "relaxed"),
            order=("body", "head", "left", "right"),
            spin=0.0, head_follow=0.5,
            pecs=1.0,                 # 30 Oct: the chest muscles' depth (0 = a flat chest)
            light="left",
        )
        d.update(kw)
        self.__dict__.update(d)
        self.kit = self.kit or Kit()
        self.hair_side = self.hair_side or self.hair
        self.brow = self.brow or self.hair
        self.beard_ramp = self.beard_ramp or self.hair
        h = dict(HAIR)
        h.update(self.hair_cfg or {})
        self.H = h
        self.build()

    L_UP, L_FORE = 29.0, 26.0

    def build(self):
        Rs = R_euler(self.spin)
        self.TR = Rs @ R_euler(*self.torso)
        self.Tt = V(self.torso_x, 0, 0)
        self.HR = R_euler(self.spin * self.head_follow) @ R_euler(*self.head)
        self.Ht = self.Tt + self.TR @ V(self.neck_dx, 11.1, self.neck_fwd)
        self.arm = {}
        for side, sgn, spec, sh in (("left", -1, self.left, self.shrug[0]),
                                    ("right", 1, self.right, self.shrug[1])):
            u, f, hand = spec[:3]
            o = dict(spec[3]) if len(spec) > 3 else {}
            u, f = unit(u), unit(f)
            S = self.Tt + self.TR @ V(sgn * (17.2 - 0.25 * sh), -4.0 + sh, -0.5 + 0.4 * sh)
            E = S + self.L_UP * u
            W = E + self.L_FORE * f
            hd = unit(o.get("dir", f))
            face = unit(o.get("face", (0, 0, 1)))
            cam = face - hd * float(face @ hd)
            if np.linalg.norm(cam) < 0.2:
                cam = V(0, 1, 0) - hd * float(V(0, 1, 0) @ hd)
            hz = unit(cam)
            hx = unit(np.cross(hd, hz))
            reach = {"fist": 5.0, "flat": 4.6, "open": 4.4}.get(hand, 5.0)
            self.arm[side] = dict(S=S, E=E, W=W, u=u, f=f, hand=hand, sgn=sgn, o=o, hd=hd,
                                  HRm=np.stack([hx, hd, hz], 1).astype(f32), C=W + reach * hd)

    def head_local(self, P):
        return (P - self.Ht) @ self.HR

    def head_parts(self, P):
        q = self.head_local(P)
        qm = mirror(q)
        jd = self.jaw_drop
        d = ell(q, (0, 10.2, 0), (7.7, 9.3, 9.6))
        d = smin(d, ell(q, (0, 5.0 - 0.2 * jd, 3.0), (self.face_w, 8.6 + 0.3 * jd, 6.9)), 2.0)
        d = smin(d, ell(q, (0, 1.4 - 0.6 * jd, 2.6), (self.jaw_w, 5.0, 6.2)), 1.5)
        d = smin(d, ell(q, (0, -1.3 - jd, 6.6 - 0.25 * jd), (2.6, 2.3, 2.4)), 1.5)
        d = smin(d, ell(qm, (4.6, 5.6, 6.2), (2.4, 1.8, 2.2)), 1.5)
        d = smin(d, cap(q, (-4.2, 9.75, 8.15), (4.2, 9.75, 8.15), 1.5), 1.2)
        d = smax(d, -ell(qm, (3.2, 8.0, 9.9), (2.3, 1.3, 1.6)), 0.8)
        d = smin(d, cap(q, (0, 8.8, 8.9), (0, 4.4, 11.2), 0.9, 1.35), 0.9)
        d = smin(d, ell(qm, (1.2, 4.0, 10.0), (1.0, 0.85, 1.05)), 0.5)
        d = smin(d, ell(q, (0, 1.3 - 0.45 * jd, 8.9), (3.0, 1.7 + 0.35 * jd, 1.3)), 0.8)
        d = np.minimum(d, ell(qm, (7.9, 6.6, -0.6), (0.9, 3.0, 1.9)))
        return [d, self.hair_sd(q)]

    def hair_sd(self, q):
        H = self.H
        k = H["len"]
        x, y, z = q[:, 0], q[:, 1], q[:, 2]
        shell = ell(q, (0, 10.4, -0.3), (7.7 + 0.75 * k * H["side"], 9.3 + 0.8 * k, 9.6 + 0.8 * k))
        if H["top"]:
            shell = smin(shell, ell(q, (H["top_x"], 17.6, H["top_z"]), (6.1, H["top"], 6.6)), 1.6)
        if H["quiff"]:
            shell = smin(shell, ell(q, (H["top_x"] + 0.8, 18.6, 5.6), (4.6, H["quiff"], 3.6)), 1.4)
        if H["long"]:
            L = H["long"]
            qm = mirror(q)
            shell = smin(shell, ell(qm, (7.3, 7.0 - L * 0.5, -1.6), (2.3, 4.0 + L * 0.5, 4.6)), 1.5)
            shell = smin(shell, ell(q, (0, 5.0 - L * 0.5, -6.2), (7.2, 5.0 + L * 0.5, 4.2)), 2.0)
        if H["bun"]:
            shell = smin(shell, sph(q, (0, 16.0, -9.6), 3.3), 1.0)
        if H["curl"]:
            shell = shell - H["curl"] * 0.6 * (np.sin(x * 1.7 + 0.8) * np.sin(y * 1.9 + 0.3) * np.sin(z * 1.6 + 1.1))
        face = ell(q, (H["part_x"], 4.5 - H["fringe"], 10.5), (8.0, 10.6, 9.5))
        low = (5.2 - H["sideburn"] - H["long"] - y) - np.maximum(0.0, -z - 2.0) * 0.9
        return np.maximum(np.maximum(shell, -face), low)

    def head_mats(self, P, part):
        q = self.head_local(P)
        x, y, z = q[:, 0], q[:, 1], q[:, 2]
        n = len(q)
        H = self.H
        m = np.full(n, mat("skin", self.skin), np.int32)
        off = np.zeros(n, np.int32)
        hair = part == 1
        m[hair] = mat("hair", self.hair)
        if H["fade"]:
            side = hair & (y < 13.2 - 0.25 * np.maximum(z, 0)) & (np.abs(x) > 4.6)
            m[side] = mat("hair_side", self.hair_side)
        if H["curl"]:
            strand = np.sin(x * 2.9 + 1.4 * np.sin(y * 2.3)) * np.sin(y * 2.6 + z * 1.3) * 1.3
        else:
            strand = np.sin((x * 1.0 + y * 0.45 - z * 0.35) * 2.3) + 0.6 * np.sin((x * 0.7 - z) * 4.1 + 1.3)
        self._strand = np.where(hair, strand * 0.11, 0.0)
        if H["band"]:
            ring = (np.abs(y - (13.4 - 0.16 * z)) < 0.62) & (z > -7.0)
            m[ring & (hair | (y > 11.5))] = mat("hairband", H["band"], 1.5)
            hair = hair & ~ring
        front = (z > 4.0) & ~(part == 1)
        ax = np.abs(x)
        sg = np.sign(x)
        jd = self.jaw_drop
        if self.beard:
            top = 3.3 if self.beard == "full" else 1.5
            line = top + (0.42 if self.beard == "full" else 0.62) * np.maximum(ax - 3.0, 0.0)
            reg = (z > -1.5) & ~(part == 1) & (y < line) & ((ax > 2.9) | (y < 0.3 - 0.45 * jd))
            tash = front & (ax < 3.2) & (y > 2.15 - 0.2 * jd) & (y < 3.25)
            reg = reg | tash
            if self.beard == "stubble":
                off[reg] -= 1
            else:
                m[reg] = mat("beard", self.beard_ramp, 1.0)
                if self.beard == "short":
                    off[reg] += 1
        by = 10.05 + self.brow_lift + self.brow_slope * (ax - 3.2) * 0.22
        thick = 0.50 - 0.07 * (ax - 1.2)
        brow = front & (ax > 1.15) & (ax < 5.35) & (np.abs(y - by) < thick)
        m[brow] = mat("brow", self.brow, 1.7)
        ex, ey = 3.15, 8.05
        dx, dy = ax - ex, y - ey
        if self.eye_open < 0.2:
            lid = front & (np.abs(dx) < 1.6) & (np.abs(dy + 0.25 * (1 - (dx / 1.6) ** 2) - 0.1) < 0.24)
            m[lid] = mat("lash", "lash", 2.0)
        else:
            h = 0.66 * self.eye_open
            opening = front & ((dx / 1.55) ** 2 + (dy / h) ** 2 < 1.0)
            lash = front & ((dx / 1.74) ** 2 + ((dy - 0.12) / (h + 0.20)) ** 2 < 1.0) & ~opening & (dy > 0.0)
            m[lash] = mat("lash", "lash", 1.8)
            m[opening] = mat("eyewhite", "eyewhite", 1.3)
            gx, gy = self.gaze
            ir = opening & ((x - sg * ex - gx) ** 2 + (dy - gy) ** 2 < 0.70 ** 2)
            m[ir] = mat("iris", self.iris, 2.4)
        if self.snarl:
            dd, hh = seg_dist2d(ax, y, (1.9, 4.4), (3.3, 1.2 + 0.3 * self.smile - 0.45 * jd))
            off[front & (dd < 0.30)] -= 1
        mw, mh = self.mouth_w, self.mouth_h
        my = 1.25 - 0.45 * jd + self.smile * 0.25 * (ax / max(mw, 0.1)) ** 2 * mw + self.smirk * 0.3 * (x / max(mw, 0.1))
        ddy = y - my
        lipm = mat("lip", self.lip, 1.0)
        if self.mouth == "closed":
            line = front & (ax < mw) & (np.abs(ddy) < 0.20)
            m[line] = mat("mouthline", "mouth", 2.0)
            lip = front & (ax < mw * 0.8) & (ddy < -0.2) & (ddy > -0.95) & ~line
            m[lip] = lipm
        elif self.mouth == "purse":
            ring = front & ((ax / 1.45) ** 2 + (ddy / 0.85) ** 2 < 1.0)
            m[ring] = lipm
            m[ring & (ax < 1.0) & (np.abs(ddy) < 0.14)] = mat("mouthline", "mouth", 1.2)
        else:
            p = 3.0
            inside = front & ((ax / mw) ** p + (np.abs(ddy) / mh) ** p < 1.0)
            ring = front & ((ax / (mw + 0.42)) ** p + (np.abs(ddy) / (mh + 0.42)) ** p < 1.0) & ~inside
            m[ring] = lipm
            m[inside] = mat("mouth", "mouth", 1.6)
            if self.mouth == "grit":
                teeth = inside & (ax < mw - 0.42)
                m[teeth] = mat("teeth", "teeth", 1.5)
                off[teeth & (ddy < 0)] -= 1
                gap = teeth & (np.abs(ddy) < 0.10)
                m[gap] = mat("toothgap", "mouth", 0.9)
            elif self.mouth == "smile":
                teeth = inside & (ddy > -mh * 0.25) & (ax < mw - 0.35)
                m[teeth] = mat("teeth", "teeth", 1.5)
            else:
                teeth = inside & (ddy > mh * 0.42) & (ax < mw - 0.5)
                m[teeth] = mat("teeth", "teeth", 1.5)
                tongue = inside & (ddy < -mh * 0.35) & (ax < mw * 0.6)
                m[tongue] = lipm
        return m, off

    def torso_local(self, P):
        return (P - self.Tt) @ self.TR

    # 30 Oct (Hubi: "the shading looks like they have boobs"): the chest egg was deeper than the
    # waist egg, the shirt's belly stuck out past the chest, and the banded light ringed each egg.
    # TORSO_V2 makes a shallower chest that blends into the waist and gives the shirt a flat front.
    TORSO_V2 = dict(chest_z=9.4, blend=10.0, belly_z=9.6, belly_dz=-0.4, front=7.6, front_soft=3.5)
    TORSO_V1 = dict(chest_z=10.5, blend=6.0, belly_z=10.9, belly_dz=0.9, front=None, front_soft=0.0)
    torso_style = TORSO_V2

    def torso_sd(self, q):
        qm = mirror(q)
        T = self.torso_style
        d = ell(q, (0, -16, 0), (16.0, 19.0, T["chest_z"]))
        d = smin(d, cap(q, (-14.2, -4.6, -0.5), (14.2, -4.6, -0.5), 5.7), 5.0)
        d = smin(d, cap(qm, (0, 2.6, -2.6), (13.0, -2.6, -1.5), 5.0, 4.5), 4.0)
        k = getattr(self, "pecs", 1.0)          # sunk into the chest as k drops: no bulge at 0
        d = smin(d, ell(qm, (7.5, -12.0, 6.4 - 4.0 * (1.0 - k)), (7.6, 6.0 - 1.5 * (1.0 - k), 4.6)), 3.0)
        d = smin(d, ell(q, (0, -34, 0.3), (14.6, 18.0, 9.6)), T["blend"])
        d = smin(d, ell(q, (0, -49, 0), (15.6, 12.0, 10.2)), 6.0)
        if T["front"] is not None:                    # the body stays inside the shirt's flat front
            d = smax(d, q[:, 2] - (T["front"] - 1.6), T["front_soft"])
        return d

    folds = ()
    SLEEVE = 0.56

    def sleeve_len(self):
        return 0.36 if self.kit.long_sleeve else self.SLEEVE

    def sleeve_sd(self, P, side):
        a = self.arm[side]
        end = a["S"] + self.sleeve_len() * self.L_UP * a["u"]
        if self.kit.long_sleeve:
            s = cap(P, a["S"], end, 5.9, 5.6)
            s = smin(s, sph(P, a["S"], 6.6), 2.0)
        else:
            s = cap(P, a["S"], end, 6.5, 6.1)
            s = smin(s, sph(P, a["S"], 7.0), 2.0)
        return np.maximum(s, (P - end) @ a["u"])

    def body_parts(self, P):
        q = self.torso_local(P)
        x, y, z = q[:, 0], q[:, 1], q[:, 2]
        base = self.torso_sd(q)
        neck_top = self.Ht + self.HR @ V(0, 4.0, -1.2)
        skin = smin(base, cap(P, self.Tt + self.TR @ V(0, -2.0, -2.6), neck_top, 5.7, 5.3), 3.0)
        loose = 1.0 + 1.5 * sstep(-14.0, -34.0, y)
        shirt = base - loose
        T = self.torso_style
        shirt = smin(shirt, ell(q, (0, -37, T["belly_dz"]), (15.9, 25.0, T["belly_z"])), 4.0)
        if T["front"] is not None:                    # a flat shirt front: no rounded chest or belly
            shirt = smax(shirt, z - T["front"], T["front_soft"])
        if self.folds:
            ridge = 0.0
            for a, b, amp, wid in self.folds:
                dd, hh = seg_dist2d(x, y, a, b)
                ridge = ridge + amp * np.exp(-(dd / wid) ** 2) * np.sin(np.pi * np.clip(hh, 0.02, 0.98)) ** 0.6
            shirt = shirt - ridge * sstep(-3.0, 3.0, z)
        sl = np.minimum(self.sleeve_sd(P, "left"), self.sleeve_sd(P, "right"))
        self._sleeve = sl
        self._shirt_only = shirt
        shirt = smin(shirt, sl, 3.0)
        neckhole = ell(q, (0, 3.0, 2.0), (6.6, 5.6, 9.0))
        self._neckhole = neckhole
        shirt = np.maximum(shirt, -neckhole)
        shirt = np.maximum(shirt, -(y + 54.0))
        shorts = np.maximum(base - 1.5, y + 50.0)
        return [skin, shirt, shorts]

    def body_mats(self, P, part):
        q = self.torso_local(P)
        n = len(q)
        m = np.full(n, mat("skin", self.skin), np.int32)
        off = np.zeros(n, np.int32)
        self.body_parts(P)
        sleeve = self._sleeve < self._shirt_only
        sl_t = np.zeros(n, f32)
        sl_side = np.zeros(n, np.int32)
        for i, side in enumerate(("left", "right")):
            a = self.arm[side]
            t = ((P - a["S"]) @ a["u"]) / (self.sleeve_len() * self.L_UP)
            near = cap(P, a["S"], a["S"] + self.sleeve_len() * self.L_UP * a["u"], 6.5, 6.1) < 1.5
            sl_t = np.where(near, t, sl_t)
            sl_side = np.where(near, i + 1, sl_side)
        collar = self._neckhole < self.kit.collar_w
        km, koff = self.kit.paint(q, sleeve, sl_t, collar)
        if self.armband and not self.kit.long_sleeve:
            i = 1 if self.armband[0] == "left" else 2
            band = sleeve & (sl_side == i) & (sl_t > 0.50) & (sl_t < 0.84)
            km[band] = mat("armband", self.armband[1], 1.4)
            koff[band] = 0
        sh = part == 1
        m[sh] = km[sh]
        off[sh] = koff[sh]
        m[part == 2] = mat(self.kit.shorts)
        self._strand = -0.17 * sstep(-20.0, -46.0, q[:, 1])
        return m, off

    def arm_parts(self, P, side):
        a = self.arm[side]
        S, E, W, f = a["S"], a["E"], a["W"], a["f"]
        fat = 0.55 if self.kit.long_sleeve else 0.0
        d = cap(P, S, E, 5.0 + fat, 4.25 + fat)
        d = smin(d, sph(P, E, 4.0 + fat), 2.5)
        d = smin(d, cap(P, E, W, 4.2 + fat, 2.9 + fat), 2.5)
        d = smin(d, sph(P, E + 0.28 * self.L_FORE * f, 4.3 + fat), 3.5)
        qh = (P - a["C"]) @ a["HRm"]
        sg = a["sgn"]
        kind = a["hand"]
        if kind == "fist":
            h = rbox(qh, (4.4, 4.7, 3.6), 2.0)
            th = cap(qh, (-sg * 4.2, -3.2, 2.0), (sg * 1.4, -1.0, 4.0), 1.55, 1.45)
            h = smin(h, th, 0.6)
        elif kind == "point":
            h = rbox(qh, (4.4, 4.7, 3.6), 2.0)
            th = cap(qh, (-sg * 4.2, -3.2, 2.0), (sg * 1.4, -1.0, 4.0), 1.55, 1.45)
            h = smin(h, th, 0.6)
            h = smin(h, cap(qh, (-sg * 2.6, 3.0, 0.8), (-sg * 2.6, 13.0, 0.8), 1.5, 1.2), 0.7)
        elif kind == "flat":
            h = rbox(qh - V(0, 2.4, 0), (3.9, 7.2, 1.6), 1.5)
            th = cap(qh, (-sg * 3.4, -3.2, 0.3), (-sg * 5.4, 1.6, 0.9), 1.3, 1.05)
            h = smin(h, th, 0.9)
        elif kind == "open":
            h = rbox(qh - V(0, -0.4, 0), (4.0, 4.5, 1.6), 1.4)
            for bx, tx, ty in ((-3.0, -5.6, 10.2), (-1.0, -1.9, 12.0), (1.0, 1.9, 11.6), (3.0, 5.6, 9.6)):
                h = smin(h, cap(qh, (bx * -sg, 3.2, 0), (tx * -sg, ty, 0.3), 1.1, 0.95), 0.5)
            h = smin(h, cap(qh, (-sg * 3.4, -2.6, 0.2), (-sg * 7.4, 2.8, 0.8), 1.3, 1.05), 0.8)
        else:
            h = rbox(qh - V(0, 1.5, 0), (4.1, 6.2, 1.9), 1.7)
            th = cap(qh, (-sg * 3.6, -2.0, 0.6), (-sg * 6.2, 2.4, 1.6), 1.4, 1.1)
            h = smin(h, th, 1.0)
        return [d, smin(h, cap(P, W - 2.0 * f, W + 1.2 * a["hd"], 3.0), 1.2)]

    def arm_mats(self, P, part, side):
        a = self.arm[side]
        o = a["o"]
        n = len(P)
        m = np.full(n, mat("skin", self.skin), np.int32)
        off = np.zeros(n, np.int32)
        qh = (P - a["C"]) @ a["HRm"]
        hand = part == 1
        tf = ((P - a["E"]) @ a["f"]) / self.L_FORE
        if self.kit.long_sleeve:
            m[~hand] = mat(self.kit.sleeve)
            if self.kit.cuff:
                m[~hand & (tf > 0.90)] = mat("cuff", self.kit.cuff, 1.3)
            if self.armband and self.armband[0] == side:
                tu = ((P - a["S"]) @ a["u"]) / self.L_UP
                m[~hand & (tu > 0.40) & (tu < 0.60) & (tf < 0.0)] = mat("armband", self.armband[1], 1.4)
        if o.get("tape"):
            m[~hand & (tf > 0.80) & (tf < 0.99)] = mat("tape", o["tape"], 1.3)
        if o.get("glove"):
            m[hand] = mat("glove", o["glove"])
        kind = a["hand"]
        if kind in ("fist", "point"):
            g = np.abs(((qh[:, 0] / 2.2) + 0.5) % 1.0 - 0.5) * 2.2
            groove = hand & (g < 0.27) & (qh[:, 2] > 0.8) & (qh[:, 1] > -0.6) & (np.abs(qh[:, 0]) < 3.6)
            if kind == "point":
                groove &= qh[:, 1] < 4.4
            off[groove] -= 1
        elif kind in ("flat", "relaxed"):
            g = np.abs(((qh[:, 0] / 2.0) + 0.5) % 1.0 - 0.5) * 2.0
            groove = hand & (g < 0.24) & (qh[:, 1] > 3.0) & (np.abs(qh[:, 0]) < 3.4)
            off[groove] -= 1
        return m, off

    def groups(self):
        g = {
            "body": (self.body_parts, self.body_mats),
            "head": (self.head_parts, self.head_mats),
        }
        for side in ("left", "right"):
            g[side] = ((lambda P, s=side: self.arm_parts(P, s)),
                       (lambda P, part, s=side: self.arm_mats(P, part, s)))
        return g


LIGHT = unit((-0.40, 0.58, 0.71))
FILL = unit((0.62, 0.10, 0.78))
BANDS = (0.30, 0.46, 0.64, 0.84)


def march(sd, O, D, t0, t1, steps=96):
    n = len(D)
    t = np.full(n, t0, f32)
    hit = np.zeros(n, bool)
    live = np.arange(n)
    for _ in range(steps):
        if not len(live):
            break
        d = sd(O + t[live, None] * D[live])
        got = d < 0.035
        hit[live[got]] = True
        t[live] += np.maximum(d, 0.02) * 0.82
        keep = ~got & (t[live] < t1)
        live = live[keep]
    t[~hit] = np.inf
    return t


def normals(sd, P, h=0.09):
    e = np.array([[1, -1, -1], [-1, -1, 1], [-1, 1, -1], [1, 1, 1]], f32)
    n = np.zeros_like(P)
    for k in e:
        n += k * sd(P + h * k)[:, None]
    return n / np.maximum(np.sqrt((n * n).sum(1))[:, None], 1e-6)


def shadow(sd, P, L, k=6.0, far=60.0, steps=40):
    res = np.ones(len(P), f32)
    t = np.full(len(P), 0.6, f32)
    live = np.arange(len(P))
    for _ in range(steps):
        if not len(live):
            break
        d = sd(P[live] + t[live, None] * L)
        res[live] = np.minimum(res[live], k * d / t[live])
        t[live] += np.clip(d, 0.35, 5.0)
        live = live[(res[live] > 0.02) & (t[live] < far)]
    return np.clip(res, 0.0, 1.0)


class Shot:
    def __init__(self, NW=160, NH=170, ppc=1.75, win=(26, 10, 107, 150), cam_d=330.0,
                 centre_x=0.0, top_y=38.0):
        self.__dict__.update(locals())

    def rays(self, S):
        W, H = self.NW * S, self.NH * S
        xs = ((np.arange(W) + 0.5) / S - (self.win[0] + self.win[2] / 2.0)) / self.ppc + self.centre_x
        ys = self.top_y - ((np.arange(H) + 0.5) / S - self.win[1]) / self.ppc
        X, Y = np.meshgrid(xs.astype(f32), ys.astype(f32))
        O = V(self.centre_x, self.top_y - 22.0, self.cam_d)
        T = np.stack([X.ravel(), Y.ravel(), np.zeros(X.size, f32)], 1)
        D = T - O
        D /= np.sqrt((D * D).sum(1))[:, None]
        return O, D.astype(f32), W, H


def project(shot, P):
    O = V(shot.centre_x, shot.top_y - 22.0, shot.cam_d)
    P = np.asarray(P, f32)
    X = O + (P - O) * (O[2] / (O[2] - P[2]))
    return ((X[0] - shot.centre_x) * shot.ppc + shot.win[0] + shot.win[2] / 2.0,
            (shot.top_y - X[1]) * shot.ppc + shot.win[1])


def render(fig, shot=None, S=4, verbose=False):
    shot = shot or Shot()
    MATS.clear()
    O, D, W, H = shot.rays(S)
    flip = V(-1, 1, 1) if getattr(fig, "light", "left") == "right" else V(1, 1, 1)
    key_l, fill_l = unit(LIGHT * flip), unit(FILL * flip)
    groups = fig.groups()
    sds = {k: (lambda P, f=v[0]: np.minimum.reduce(f(P))) for k, v in groups.items()}

    def scene(P):
        return np.minimum.reduce([sds[k](P) for k in fig.order])

    t0, t1 = shot.cam_d - 75.0, shot.cam_d + 40.0
    below = np.full(len(D), np.inf, f32)
    keys = []
    for name in fig.order:
        parts_f, mats_f = groups[name]
        t = march(sds[name], O, D, t0, t1)
        vis = np.isfinite(t) & (t < below + 0.25)
        idx = np.nonzero(vis)[0]
        key = np.full(len(D), -1, np.int32)
        if len(idx):
            P = O + t[idx, None] * D[idx]
            N = normals(sds[name], P)
            part = np.argmin(np.stack(parts_f(P)), 0)
            fig._strand = 0.0
            m, off = mats_f(P, part)
            sh = shadow(scene, P + N * 0.45, key_l)
            lam = np.clip(N @ key_l, 0, 1)
            I = 0.20 + 0.74 * lam * (0.42 + 0.58 * sh) + 0.20 * np.clip(N @ fill_l, 0, 1)
            I = I + fig._strand
            band = np.searchsorted(np.array(BANDS, f32), I).astype(np.int32)
            band = np.clip(band + off, 0, 4)
            key[idx] = m * 8 + band
        below = np.minimum(below, t)
        keys.append((name, key.reshape(H, W)))
        if verbose:
            print("  ", name, int(vis.sum()), "samples")
    rgb, wts = mat_tables()
    out = [(name, vote(key, S, wts)) for name, key in keys]
    return finish(out, fig, shot)


def vote(key, S, wts):
    H, W = key.shape
    h, w = H // S, W // S
    blocks = key.reshape(h, S, w, S).transpose(0, 2, 1, 3).reshape(h, w, S * S)
    best = np.full((h, w), -1, np.int32)
    score = np.zeros((h, w), f32)
    filled = (blocks >= 0).sum(2)
    for k in np.unique(key):
        if k < 0:
            continue
        s = (blocks == k).sum(2) * wts[k // 8]
        win = s > score
        best[win] = k
        score[win] = s[win]
    best[filled < (S * S) * 0.5] = -1
    return best


KEEP = ("iris", "eyewhite", "lash", "teeth", "badge2", "brow", "mouthline", "hairband", "tape")
LAST = {}
RIM = True


def tidy(best):
    keep = np.array([MATS[k][0] for k in KEEP if k in MATS])
    h, w = best.shape
    pad = np.pad(best, 1, constant_values=-2)
    nb = [pad[1 + dy:1 + dy + h, 1 + dx:1 + dx + w] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dx, dy) != (0, 0)]
    lonely = (best >= 0) & np.all([n != best for n in nb], 0) & ~np.isin(best // 8, keep)
    four = [pad[0:h, 1:w + 1], pad[2:h + 2, 1:w + 1], pad[1:h + 1, 0:w], pad[1:h + 1, 2:w + 2]]
    out = best.copy()
    for y, x in zip(*np.nonzero(lonely)):
        c = [int(f[y, x]) for f in four if f[y, x] >= 0]
        if c:
            out[y, x] = max(set(c), key=c.count)
    return out


def finish(keyed, fig, shot):
    keyed = [(n, tidy(b)) for n, b in keyed]
    body = dict(keyed).get("body")
    if body is not None:
        allowed = fig.kit.print_on()
        for rows, inks, at, lift in fig.kit.stamps():
            P0 = fig.Tt + fig.TR @ V(*at)
            c = project(shot, P0)
            ex = project(shot, P0 + fig.TR @ V(1, 0, 0))
            ey = project(shot, P0 + fig.TR @ V(0, -1, 0))
            k = math.hypot(*(project(shot, P0 + V(1, 0, 0))[i] - c[i] for i in (0, 1)))
            basis = [[(ex[0] - c[0]) / k, (ey[0] - c[0]) / k], [(ex[1] - c[1]) / k, (ey[1] - c[1]) / k]]
            stamp(body, rows, inks, c, basis, allowed, lift)
    rgb, _w = mat_tables()
    if RIM:
        top = np.full(keyed[0][1].shape, -1, np.int32)
        owner = np.full(top.shape, -1, np.int32)
        for i, (n, b) in enumerate(keyed):
            on = b >= 0
            top[on] = b[on]
            owner[on] = i
        solid = top >= 0
        pad = np.pad(solid, 1, constant_values=False)
        h, w = solid.shape
        edge = solid & ~(pad[0:h, 1:w + 1] & pad[2:h + 2, 1:w + 1] & pad[1:h + 1, 0:w] & pad[1:h + 1, 2:w + 2])
        keep = np.array([MATS[k][0] for k in KEEP if k in MATS])
        for i, (n, b) in enumerate(keyed):
            sel = edge & (owner == i) & ~np.isin(b // 8, keep)
            b[sel] = (b[sel] // 8) * 8 + np.maximum(b[sel] % 8 - 1, 0)
    ramp_of = {i: ramp for _n, (i, ramp, _w) in MATS.items()}
    keep = np.array([MATS[k][0] for k in KEEP if k in MATS])
    for i in range(1, len(keyed) if getattr(fig, "overlap_edge", True) else 1):
        b = keyed[i][1]
        under = np.full(b.shape, -1, np.int32)
        for _n, lower in keyed[:i]:
            under[lower >= 0] = lower[lower >= 0]
        h, w = b.shape
        on = b >= 0
        pb = np.pad(on, 1, constant_values=False)
        pu = np.pad(under, 1, constant_values=-1)
        touch = np.zeros(b.shape, bool)
        mine = np.vectorize(lambda k: ramp_of.get(k // 8, "") if k >= 0 else "")(b)
        for dy, dx in ((0, 1), (2, 1), (1, 0), (1, 2)):
            nb_on = pb[dy:dy + h, dx:dx + w]
            nb_under = pu[dy:dy + h, dx:dx + w]
            theirs = np.vectorize(lambda k: ramp_of.get(k // 8, "") if k >= 0 else "?")(nb_under)
            touch |= on & ~nb_on & (theirs == mine)
        sel = touch & ~np.isin(b // 8, keep)
        b[sel] = (b[sel] // 8) * 8 + np.maximum(b[sel] % 8 - 1, 0)
    layers = []
    LAST["keys"] = [(n, b.copy()) for n, b in keyed]
    for n, b in keyed:
        out = np.zeros(b.shape + (4,), np.uint8)
        on = b >= 0
        out[on, :3] = rgb[b[on] // 8, b[on] % 8]
        out[on, 3] = 255
        layers.append((n, Image.fromarray(out, "RGBA")))
    return layers


def flatten(layers):
    base = None
    for name, im in layers:
        base = im.copy() if base is None else Image.alpha_composite(base, im)
    return base
