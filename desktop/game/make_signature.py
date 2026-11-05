"""Neymar Jr's autograph for his Signature card.

    python3 make_signature.py [out_dir] [ink]        ink: gold (default), silver, black

Drawn, not typed: every stroke is a path through hand-placed points (Catmull-Rom; a point followed
by CUSP is a sharp turn of the pen), slanted like fast handwriting and climbing a little, then
inked with a broad nib held at an angle - down-strokes thick, up-strokes hairline - tapering in
and out like a marker touching down and lifting off.

28 Oct, second go - Hubi: "the signature looks buns". The first one was a fat gold outline on
every letter, a shape you'd see on a sign, not a shirt. Now: a thin marker line, a big N, and the
J's tail sweeps back under the whole name as the underline - one fast motion, the way people
actually sign. No outline, just a one-pixel shadow so it stands off the shirt.

  sig_neymar.png      smooth, for very big cards
  sig_neymar_px.png   pixel art at every small width (rows, see px_sheet) - the game keeps one
                      pixel in three, so smooth hairlines fall apart on normal-size cards
"""
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

CUSP = "cusp"
# signature space: about 520 x 230, baseline y = 150, small letters 112..150
STROKES = [
    # N - in from below, a tall left stem, the diagonal, a taller right stem, the tip flicks over
    {"pts": [(10, 178), (24, 152), (38, 98), (52, 26), CUSP, (74, 90), (98, 152), CUSP, (110, 92),
             (126, 10), CUSP, (140, 14), (150, 28)], "tail": 0.10},
    # e y m a r, one stroke
    {"pts": [(124, 146), (151, 129), (161, 115), (155, 102), (140, 105), (130, 124), (134, 145), (150, 152),
             (168, 139), CUSP, (176, 108), CUSP, (176, 138), (186, 150), (198, 139), CUSP, (204, 108), CUSP,
             (202, 142), (195, 182), (183, 207), (169, 211), (164, 199), (177, 180), (200, 161), (218, 142),
             CUSP, (222, 110), CUSP, (222, 150), CUSP, (227, 122), (238, 107), (246, 118), CUSP, (248, 150), CUSP,
             (253, 122), (264, 107), (272, 118), (274, 146), (283, 151), (292, 140),
             CUSP, (318, 110), (302, 106), (290, 121), (292, 144), (304, 150), (316, 137), CUSP, (322, 108), CUSP,
             (320, 140), (328, 150), (338, 142), CUSP, (343, 111), CUSP, (349, 121), (358, 108), (370, 110),
             (382, 124)], "tail": 0.08},
    # J - its tail comes round and runs back under the whole name: the underline, in one go
    {"pts": [(426, 50), (440, 36), (456, 40), CUSP, (449, 96), (441, 146), (431, 184), (416, 208),
             (394, 222), (362, 226), (318, 218), (240, 207), (150, 204), (70, 208), (8, 218)], "tail": 0.34},
    # r
    {"pts": [(456, 150), (463, 116), CUSP, (470, 127), (480, 113), (494, 117)], "tail": 0.2},
]
SPARKLES = ((52, 26, 12), (456, 40, 9))
SLANT = 0.26                      # tops lean right, like fast handwriting
TILT = math.radians(-7.0)         # and the whole name climbs a little
NIB = math.radians(38)
SS = 4                            # supersampling
PEN = 7.5                         # the nib's width, in signature units
NIB_MIN = 0.22                    # how thin it goes when drawn along the nib

INKS = {
    # (light, deep) ink colours, shadow colour, the top-edge glint
    "silver": ((252, 253, 255), (176, 186, 204), (12, 16, 34, 200), (255, 255, 255)),
    "black": ((44, 44, 50), (8, 8, 12), None, (110, 112, 122)),
    "gold": ((255, 236, 160), (206, 142, 34), (40, 22, 4, 200), (255, 250, 220)),
}
INK = "gold"


def corners(stroke):
    pts, sharp = [], set()
    for p in stroke:
        if p == CUSP:
            sharp.add(len(pts) - 1)
        else:
            pts.append(p)
    return pts, sharp


def catmull(pts, n=24):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / float(n)
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(pts[-1])
    return out


def place_all(line):
    """Slant and tilt: where signature space lands on the picture."""
    ca, sa = math.cos(TILT), math.sin(TILT)
    out = []
    for x, y in line:
        x, y = x + (150 - y) * SLANT - 260, y - 120
        out.append((x * ca - y * sa + 260, x * sa + y * ca + 150))
    return out


def place(x, y):
    return place_all([(x, y)])[0]


def path(stroke):
    pts, sharp = corners(stroke)
    runs, cur = [], [pts[0]]
    for i in range(1, len(pts)):
        cur.append(pts[i])
        if i in sharp:
            runs.append(cur)
            cur = [pts[i]]
    if len(cur) > 1:
        runs.append(cur)
    line = []
    for r in runs:
        seg = catmull(r)
        line.extend(seg if not line else seg[1:])
    return place_all(line)


def resample(line, step):
    out = [line[0]]
    acc = 0.0
    for a, b in zip(line, line[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        if d == 0:
            continue
        t = step - acc
        while t <= d:
            out.append((a[0] + (b[0] - a[0]) * t / d, a[1] + (b[1] - a[1]) * t / d))
            t += step
        acc = d - (t - step)
    return out


def _bounds():
    xs, ys = [], []
    for st in STROKES:
        for x, y in path(st["pts"]):
            xs.append(x)
            ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


_B = None


def origin():
    """Signature space -> canvas: a margin round the strokes' real extent."""
    global _B
    if _B is None:
        _B = _bounds()
    return 18 - _B[0], 18 - _B[1]


def canvas_size(scale):
    if _B is None:
        origin()
    return int((_B[2] - _B[0] + 36) * scale) + 4, int((_B[3] - _B[1] + 36) * scale) + 4


def ink(size, scale, width, min_r=0.5):
    """The strokes as a mask: broad nib + taper. scale = pixels per signature unit."""
    W, H = size
    m = Image.new("L", (W * SS, H * SS), 0)
    d = ImageDraw.Draw(m)
    k = scale * SS
    OX, OY = origin()
    for st in STROKES:
        line = resample([((x + OX) * k, (y + OY) * k) for x, y in path(st["pts"])],
                        max(0.4, 0.6 * SS * min(1.0, scale * 2)))
        n = len(line)
        for i, (x, y) in enumerate(line):
            a = line[max(0, i - 2)]
            b = line[min(n - 1, i + 2)]
            ang = math.atan2(b[1] - a[1], b[0] - a[0])
            nib = NIB_MIN + (1.0 - NIB_MIN) * abs(math.sin(ang - NIB))         # thick across the nib, thin along it
            u = i / float(max(1, n - 1))
            taper = min(1.0, u / 0.05, (1.0 - u) / st["tail"]) ** 0.8
            r = max(min_r * SS, width * k * nib * taper * 0.5)
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    return m.resize((W, H), Image.LANCZOS)


def colour_by_height(mask, light, deep):
    W, H = mask.size
    grad = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        t = y / float(max(1, H - 1))
        gd.line([(0, y), (W, y)], fill=tuple(int(light[j] + (deep[j] - light[j]) * t) for j in range(3)) + (255,))
    grad.putalpha(mask)
    return grad


def render(px_w=720, name=None):
    """The smooth autograph, px_w pixels across the signature space."""
    light, deep, shadow, glint = INKS[name or INK]
    scale = px_w / 560.0
    W, H = canvas_size(scale)
    core = ink((W, H), scale, PEN)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if shadow is not None:
        sh = Image.new("RGBA", (W, H), shadow[:3] + (0,))
        sh.putalpha(core.point(lambda v: v * shadow[3] // 255))
        out.alpha_composite(ImageChops.offset(sh, max(1, int(2 * scale)), max(1, int(2.5 * scale))))
    out.alpha_composite(colour_by_height(core, light, deep))
    lit = ImageChops.subtract(core, ImageChops.offset(core, max(1, int(1.5 * scale)), max(1, int(1.5 * scale))))
    g = Image.new("RGBA", (W, H), glint + (0,))
    g.putalpha(lit.point(lambda v: int(v * 0.7)))
    out.alpha_composite(g)
    d = ImageDraw.Draw(out)
    if name != "black" and (name or INK) != "black":
        for x, y, r in SPARKLES:
            x, y = place(x, y)
            OX, OY = origin()
            x, y, r = (x + OX) * scale, (y + OY) * scale, r * scale
            w = r * 0.22
            d.polygon([(x, y - r), (x + w, y - w), (x + r, y), (x + w, y + w), (x, y + r), (x - w, y + w),
                       (x - r, y), (x - w, y - w)], fill=(255, 255, 250, 235))
    return out.crop(out.getbbox())


# ---- pixel art, for the game's 3 px grid --------------------------------------------------
PX_MIN, PX_MAX, PX_STEP, PX_SLOT = 36, 160, 2, 80


def render_px(art_w, name=None):
    light, deep, shadow, glint = INKS[name or INK]
    scale = art_w / 560.0
    W, H = canvas_size(scale)
    m = ink((W, H), scale, PEN, min_r=0.55).point(lambda v: 255 if v >= 96 else 0)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if shadow is not None:                                   # one pixel down-right, under the ink
        out.paste(shadow[:3] + (shadow[3],), (0, 0), ImageChops.offset(m, 1, 1))
    two = Image.new("RGBA", (W, H))
    td = ImageDraw.Draw(two)
    for y in range(H):                                       # two tones: light above, deep below
        td.line([(0, y), (W, y)], fill=(light if y < H * 0.58 else deep) + (255,))
    out.paste(two, (0, 0), m)
    lit = ImageChops.subtract(m, ImageChops.offset(m, 1, 1))  # the upper-left edge catches the light
    out.paste(glint + (255,), (0, 0), lit)
    if (name or INK) != "black":
        d = ImageDraw.Draw(out)
        for x, y, r in SPARKLES:
            x, y = place(x, y)
            OX, OY = origin()
            x, y = int((x + OX) * scale), int((y + OY) * scale)
            r = max(1, int(r * scale * 0.9))
            d.line([(x - r, y), (x + r, y)], fill=(255, 255, 250, 255))
            d.line([(x, y - r), (x, y + r)], fill=(255, 255, 250, 255))
    return out.crop(out.getbbox())


def px_sheet(name=None):
    """Every pixel version, one per PX_SLOT-tall row: row i is PX_MIN + i * PX_STEP wide."""
    widths = list(range(PX_MIN, PX_MAX + 1, PX_STEP))
    sheet = Image.new("RGBA", (PX_MAX + 8, PX_SLOT * len(widths)), (0, 0, 0, 0))
    for i, w in enumerate(widths):
        im = render_px(w, name)
        assert im.height <= PX_SLOT, (w, im.size)
        sheet.alpha_composite(im, (0, i * PX_SLOT))
    return sheet


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "sprites"
    name = sys.argv[2] if len(sys.argv) > 2 else INK
    os.makedirs(out, exist_ok=True)
    render(name=name).save(os.path.join(out, "sig_neymar.png"))
    px_sheet(name).save(os.path.join(out, "sig_neymar_px.png"))
    print("signature (%s) written to %s" % (name, out))


if __name__ == "__main__":
    main()
