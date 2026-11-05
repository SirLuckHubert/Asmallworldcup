"""The Signature card, in the World Cup card's shape (28 Oct).

    python3 make_sig_card.py [out_dir]

Hubi: "rework the signature card to be like the new World Cup designs". So it is the same card -
square top-left and bottom-right, rounded right off top-right and bottom-left, the nation's flag
waving behind and inside it (the game waves it) - with what makes it a Signature:
  * the gold frame carries an emerald enamel band (Brazil green) between two gold rims
  * gold laurels climb the two big curves (28 Oct, from Hubi's FC Cafu card): one up the bottom-left
    curve and the left side, one up the right side and over the top-right curve
  * a gold plate at the foot the game prints the shirt number on
  * the game pins the SIGNATURE tab to the top edge and writes his autograph across the shirt
    (make_signature.py)

  tpl_fsig_card.png        everything that is not the flag (shadow, plate, frame, laurels)
  tpl_fsigframe_card.png   just the frame, laid over the player (laurels and plate stay behind)
Uses make_wc_flagcards.py's shape, so tpl_fmask_card.png cuts the inside flag for this one too.
"""
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import make_wc_flagcards as wc

BODY = wc.BODY
EMERALD = [(0, 120, 64), (40, 190, 110), (0, 92, 48), (24, 160, 88), (0, 104, 56), (60, 210, 130),
           (0, 96, 50), (0, 120, 64)]


def ring_path(inset):
    x0, y0, x1, y1 = BODY
    p = wc.fc_path((x0 + inset, y0 + inset, x1 - inset, y1 - inset))
    return p + [p[0]]


def sig_ring():
    """Gold rim, emerald band, gold rim: drawn as nested strokes of the card's own outline."""
    out = wc.layer()
    d = ImageDraw.Draw(out)
    d.line(ring_path(0), fill=(40, 26, 4), width=21, joint="curve")       # dark outline round it all
    for inset, width, stops in ((-3, 6, wc.GOLD), (3, 7, EMERALD), (8, 4, wc.GOLD)):
        m = Image.new("L", out.size, 0)
        ImageDraw.Draw(m).line(ring_path(inset), fill=255, width=width, joint="curve")
        out.paste(wc.sweep(out.size, stops), (0, 0), m)
    d.line(ring_path(-5), fill=(255, 248, 214), width=1, joint="curve")    # bright outer lip
    d.line(ring_path(0), fill=(255, 236, 170, 170), width=1, joint="curve")
    d.line(ring_path(11), fill=(110, 72, 10, 210), width=2, joint="curve")  # inner shadow line
    return out


LEAF_HI, LEAF_MID, LEAF_LO, LEAF_EDGE = (255, 244, 196), (236, 190, 84), (170, 112, 24), (74, 44, 4)


def leaf(d, cx, cy, ang, L, Wd, lit_side=1):
    """A pointed gold leaf centred on (cx, cy) along angle ang: a lit half, a shaded half, a
    midrib - so it reads as metal, like FC's laurels."""
    ca, sa = math.cos(ang), math.sin(ang)

    def at(x, y):
        return (cx + x * ca - y * sa, cy + x * sa + y * ca)
    top, bot = [], []
    for i in range(15):
        t = i / 14.0
        x = (t - 0.5) * L
        y = (math.sin(math.pi * t) ** 0.85) * Wd * 0.5 * (1.0 - 0.25 * t)   # fuller near the stem
        top.append(at(x, -y))
        bot.append(at(x, y))
    d.polygon(top + bot[::-1], fill=LEAF_LO if lit_side > 0 else LEAF_MID, outline=LEAF_EDGE)
    mid = [at((i / 14.0 - 0.5) * L, 0) for i in range(15)]
    d.polygon(top + mid[::-1], fill=LEAF_MID if lit_side > 0 else LEAF_HI)
    d.line(mid[2:-1], fill=LEAF_EDGE, width=1)
    hi = [at((t - 0.5) * L * 0.7, -Wd * 0.22) for t in (0.15, 0.5, 0.85)]
    d.line(hi, fill=LEAF_HI, width=1)


def dense(path, step=1.0):
    out = []
    for a, b in zip(path, path[1:] + path[:1]):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        out.extend((a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n))
    return out


def sprig(d, pts, centre, L0=40.0, L1=21.0, step=17):
    """A laurel branch along pts (the way it grows): leaves in pairs, one out, one in, shrinking to
    a single leaf at the tip. centre is the card's middle, to tell outward from inward."""
    stations = []
    for k in range(6, len(pts) - 8, step):
        p, q = pts[k], pts[min(len(pts) - 1, k + 4)]
        tx, ty = q[0] - p[0], q[1] - p[1]
        tl = math.hypot(tx, ty) or 1.0
        tx, ty = tx / tl, ty / tl
        nx, ny = ty, -tx
        if (p[0] + nx - centre[0]) ** 2 + (p[1] + ny - centre[1]) ** 2 < (p[0] - centre[0]) ** 2 + (p[1] - centre[1]) ** 2:
            nx, ny = -nx, -ny                                   # (nx, ny) points away from the card
        stations.append((p, (tx, ty), (nx, ny), k / float(len(pts))))
    d.line([s_[0] for s_ in stations], fill=LEAF_EDGE, width=4)
    d.line([s_[0] for s_ in stations], fill=(196, 140, 40), width=2)
    for i, (p, t, n, u) in enumerate(stations):
        L = L0 + (L1 - L0) * u
        Wd = L * 0.40
        for side, spread in ((1, 0.62), (-1, 0.50)):            # outer leaf, inner leaf
            vx, vy = t[0] + n[0] * spread * side, t[1] + n[1] * spread * side
            ang = math.atan2(vy, vx)
            off = L * 0.48
            leaf(d, p[0] + math.cos(ang) * off, p[1] + math.sin(ang) * off, ang, L, Wd, side)
    p, t, n, u = stations[-1]
    ang = math.atan2(t[1], t[0])
    leaf(d, p[0] + t[0] * L1 * 0.9, p[1] + t[1] * L1 * 0.9, ang, L1 * 1.1, L1 * 0.42)


def laurels(im):
    """FC's laurels: two long sprigs following the card's two big curves from outside - one
    climbs from the bottom up the bottom-left curve and the left side, the other climbs the
    right side and over the top-right curve. Turned round each other, like FC's."""
    x0, y0, x1, y1 = BODY
    centre = ((x0 + x1) / 2.0, (y0 + y1) / 2.0)
    o = 17                                                     # the stem runs this far outside the frame
    ring = dense(wc.fc_path((x0 - o, y0 - o, x1 + o, y1 + o)))
    n = len(ring)

    def nearest(x, y):
        return min(range(n), key=lambda i: (ring[i][0] - x) ** 2 + (ring[i][1] - y) ** 2)
    d = ImageDraw.Draw(im)
    w = x1 - x0
    # left: from the bottom of the bottom-left curve, forward along the outline (round, then up)
    i0 = nearest(x0 + w * 0.42, y1 + o)
    i1 = nearest(x0 - o, y0 + (y1 - y0) * 0.36)
    pts = [ring[i % n] for i in range(i0, i1 if i1 > i0 else i1 + n)]
    sprig(d, pts, centre)
    # right: from part-way down the right side, backward along the outline (up, then round the top)
    j0 = nearest(x1 + o, y0 + (y1 - y0) * 0.64)
    j1 = nearest(x1 - w * 0.30, y0 - o)
    pts = [ring[i % n] for i in range(j0, j1 - 1 if j1 < j0 else j1 - n - 1, -1)]
    sprig(d, pts, centre)


def plate(im):
    """The gold hexagon at the foot the game prints the shirt number on."""
    x0, y0, x1, y1 = BODY
    cx, cy = (x0 + x1) // 2, y1 - 2
    d = ImageDraw.Draw(im)
    def hexa(r):
        return [(cx + math.cos(math.pi / 6 + j * math.pi / 3) * r, cy + math.sin(math.pi / 6 + j * math.pi / 3) * r)
                for j in range(6)]
    d.polygon(hexa(27), fill=(56, 36, 6))
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).polygon(hexa(24), fill=255)
    im.paste(wc.sweep(im.size, wc.GOLD, repeats=2.6), (0, 0), m)
    d.polygon(hexa(18), outline=(140, 96, 20))
    d.polygon(hexa(24), outline=(255, 246, 206))


def top_layer():
    x0, y0, x1, y1 = BODY
    inside = wc.shape_mask()
    im = wc.layer()
    drop = wc.layer()
    ImageDraw.Draw(drop).polygon(wc.fc_path((x0 + 6, y0 + 10, x1 + 10, y1 + 12)), fill=(2, 4, 12, 130))
    drop.putalpha(ImageChops.multiply(drop.split()[3], ImageChops.invert(inside)))
    im.alpha_composite(drop)
    card = wc.layer()
    pd = ImageDraw.Draw(card)
    for y in range(312, y1 + 1):                                      # the plate the name sits on
        a = int(242 * min(1.0, ((y - 312) / 46.0) ** 1.4))
        pd.line([(x0, y), (x1, y)], fill=(4, 18, 12, a))              # a touch of green in the dark
    pool = wc.layer()
    pl = ImageDraw.Draw(pool)
    for k in range(26):
        pl.ellipse([x0 - 140 + k * 6, y0 - 130 + k * 6, x0 + 232 - k * 6, y0 + 218 - k * 6], fill=(3, 10, 8, 22))
    card.alpha_composite(pool)
    shine = wc.layer()
    ImageDraw.Draw(shine).polygon([(x0 + 150, y0), (x0 + 196, y0), (x0 + 60, y1), (x0 + 14, y1)],
                                  fill=(255, 255, 255, 18))
    card.alpha_composite(shine)
    card.putalpha(ImageChops.multiply(card.split()[3], inside))
    im.alpha_composite(card)
    leaves = wc.layer()
    laurels(leaves)
    leaves.putalpha(ImageChops.multiply(leaves.split()[3], ImageChops.invert(inside)))   # outside only
    im.alpha_composite(leaves)
    im.alpha_composite(sig_ring())
    plate(im)
    wc.pin_corners(im)
    return im


def frame_overlay():
    x0, y0, x1, y1 = BODY
    out = sig_ring()
    hole = Image.new("L", out.size, 255)
    cx = (x0 + x1) // 2
    ImageDraw.Draw(hole).polygon([(cx + math.cos(math.pi / 6 + k * math.pi / 3) * 28,
                                   y1 - 2 + math.sin(math.pi / 6 + k * math.pi / 3) * 28) for k in range(6)], fill=0)
    out.putalpha(ImageChops.multiply(out.split()[3], hole))
    wc.pin_corners(out)
    return out


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "sprites"
    os.makedirs(out, exist_ok=True)
    top_layer().save(os.path.join(out, "tpl_fsig_card.png"))
    frame_overlay().save(os.path.join(out, "tpl_fsigframe_card.png"))
    print("signature card layers written to", out)


if __name__ == "__main__":
    main()
