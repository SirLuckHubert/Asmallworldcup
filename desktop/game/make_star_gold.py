"""THE GOLD CRYSTAL card - the top Star Signings (1 Nov).

    python3 make_star_gold.py [out_dir]

Hubi sent FC Mobile's gold crystal card as the mood: gold, shattered crystal, a golden ball, light
raking across it. This is this game's own card in that spirit, not a copy of it: a chamfered gold frame
(all four corners cut), a five-point STAR crest at the top (they are Star Signings), a diamond gem at the
foot, and inside - a field of gold crystal facets thrown along a diagonal, a big golden ball rising out
of the top corner, and one hard streak of light across it all. No real logo or competition mark.

  tpl_stargold_card.png       everything round the player
  tpl_stargoldframe_card.png  the frame and the crest only, laid OVER the player
  stargold_preview.png        a look at it (not used by the game)

Same 400 x 500 canvas and BODY box as the other templates.
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

TPL_W, TPL_H = 400, 500
BODY = (66, 34, 334, 458)
CHAMFER = 22
RING = 13
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
GOLD_RAMP = [(54, 30, 6), (110, 66, 14), (176, 118, 30), (226, 172, 64), (250, 214, 120), (255, 244, 200)]


def ramp(t, stops=GOLD_RAMP):
    t = np.clip(t, 0, 1) * (len(stops) - 1)
    i = np.clip(t.astype(int), 0, len(stops) - 2)
    f = (t - i)[..., None]
    s = np.array(stops, np.float32)
    return s[i] * (1 - f) + s[i + 1] * f


def octagon(box, c):
    x0, y0, x1, y1 = box
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c),
            (x0, y0 + c)]


def mask_of(poly):
    m = Image.new("L", (TPL_W, TPL_H), 0)
    ImageDraw.Draw(m).polygon(poly, fill=255)
    return m


def star(cx, cy, r_out, r_in, rot=-math.pi / 2):
    pts = []
    for k in range(10):
        r = r_out if k % 2 == 0 else r_in
        a = rot + k * math.pi / 5
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def shards(im, rnd):
    """Gold crystal shards thrown along a diagonal band: each a long kite, split down its spine into a
    lit face and a shadowed face, with a dark rim and a bright edge - the big ones first, behind."""
    x0, y0, x1, y1 = BODY
    W, H = x1 - x0, y1 - y0
    d = ImageDraw.Draw(im)
    items = []
    for _ in range(150):
        t = rnd.random()
        bx = x0 - 20 + t * (W + 40)
        by = y1 + 10 - t * (H + 20) * 0.66              # (it stops short of the ball)
        spread = rnd.gauss(0, 40)
        cx, cy = bx + spread * 0.6, by + spread
        size = rnd.uniform(10, 34) * (1.6 if abs(spread) < 30 and rnd.random() < 0.3 else 1.0)
        items.append((size, cx, cy))
    for _ in range(40):                                         # a few strays off the band
        items.append((rnd.uniform(6, 14), rnd.uniform(x0, x1), rnd.uniform(y0, y1 - 80)))
    items.sort(reverse=True)
    for size, cx, cy in items:
        ang = math.radians(rnd.choice((-1, 1)) * rnd.uniform(20, 75) - 32)
        L, wd = size * rnd.uniform(1.4, 2.4), size * rnd.uniform(0.35, 0.6)
        ux, uy = math.cos(ang), math.sin(ang)
        px, py = -uy, ux
        tip = (cx + ux * L * 0.6, cy + uy * L * 0.6)
        tail = (cx - ux * L * 0.4, cy - uy * L * 0.4)
        s1 = (cx + px * wd, cy + py * wd)
        s2 = (cx - px * wd * 0.8, cy - py * wd * 0.8)
        lit = rnd.random()
        far = min(1.0, abs((cx - x0) / W + (cy - y0) / H - 1.0) * 2.2)    # dimmer off the band
        k = 1.0 - 0.55 * far
        hi = tuple(int(c) for c in ramp(np.array(0.55 + 0.45 * lit * k)))
        lo = tuple(int(c) for c in ramp(np.array((0.18 + 0.30 * lit) * k)))
        mid = tuple(int(c) for c in ramp(np.array((0.40 + 0.35 * lit) * k)))
        d.polygon([tip, s1, tail, s2], fill=(30, 16, 2, 255))           # the rim
        inset = lambda p, f=0.86: (cx + (p[0] - cx) * f, cy + (p[1] - cy) * f)
        d.polygon([inset(tip), inset(s1), inset(tail)], fill=hi + (255,))
        d.polygon([inset(tip), inset(tail), inset(s2)], fill=lo + (255,))
        d.polygon([inset(tip), inset(s1), (cx, cy)], fill=mid + (255,)) if lit > 0.6 else None
        if lit > 0.7:                                               # a bright edge catching the light
            d.line([inset(tip), inset(s1)], fill=(255, 248, 214, 255), width=1)
    return im


def golden_ball(img, cx, cy, r):
    """A big gold ball rising out of the corner: shaded sphere, panel seams, a hot highlight."""
    yy, xx = np.mgrid[0:TPL_H, 0:TPL_W].astype(np.float32)
    dx, dy = (xx - cx) / r, (yy - cy) / r
    rr = dx * dx + dy * dy
    inside = rr < 1.0
    nz = np.sqrt(np.clip(1.0 - rr, 0, 1))
    L = np.array([-0.45, -0.55, 0.70])
    L /= np.linalg.norm(L)
    shade = np.clip(dx * L[0] + dy * L[1] + nz * L[2], 0, 1)
    lum = 0.18 + 0.72 * shade ** 1.2 + 0.25 * np.clip(shade - 0.86, 0, 1) * 6
    # the panel seams: 12 pentagons (the icosahedron's corners) and 20 hexagons (the dodecahedron's)
    phi = (1 + 5 ** 0.5) / 2
    pent = []
    for s1 in (1, -1):
        for s2 in (1, -1):
            pent += [(0, s1, s2 * phi), (s1, s2 * phi, 0), (s2 * phi, 0, s1)]
    hexa = [(i, j, k) for i in (1, -1) for j in (1, -1) for k in (1, -1)]
    for s1 in (1, -1):
        for s2 in (1, -1):
            hexa += [(0, s1 / phi, s2 * phi), (s1 / phi, s2 * phi, 0), (s2 * phi, 0, s1 / phi)]
    C = np.array(pent + hexa, np.float32)
    C /= np.linalg.norm(C, axis=1, keepdims=True)
    Rm = np.array([[0.88, 0.0, 0.47], [-0.2, 0.9, 0.38], [-0.42, -0.43, 0.8]], np.float32)
    C = C @ Rm.T
    p = np.stack([dx, dy, nz], -1)
    dots = np.tensordot(p, C.T, axes=1)
    order = np.argsort(dots, -1)
    first = order[..., -1]
    top2 = np.take_along_axis(dots, order[..., -2:], -1)
    seam = (top2[..., 1] - top2[..., 0]) < 0.022
    is_pent = first < len(pent)
    lum = np.where(is_pent & inside, lum * 0.66, lum)
    lum = np.where(seam & inside, lum * 0.42, lum)
    a = np.asarray(img).astype(np.float32)
    rgb = ramp(lum)
    edge_a = np.clip((1.0 - rr) * 40, 0, 1)
    k = (inside * edge_a)[..., None] * 0.92
    a[..., :3] = a[..., :3] * (1 - k) + rgb * k
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def background(rnd):
    x0, y0, x1, y1 = BODY
    yy, xx = np.mgrid[0:TPL_H, 0:TPL_W].astype(np.float32)
    # deep bronze, warmer towards the top right where the light comes from
    t = 0.14 + 0.26 * np.clip(1.0 - (yy - y0) / (y1 - y0), 0, 1) * np.clip(0.4 + (xx - x0) / (x1 - x0), 0, 1.2)
    rgb = ramp(t)
    im = Image.fromarray(np.dstack([rgb, np.full(rgb.shape[:2], 255.0)]).astype(np.uint8), "RGBA")
    im = golden_ball(im, x1 - 40, y0 + 20, 130)
    im = shards(im, rnd)
    # the streak of light: a hard white-gold line with a wide glow, top left to bottom right
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    a0, a1 = (x0 - 20, y0 + 120), (x1 + 20, y0 + 250)
    d.line([a0, a1], fill=(255, 226, 150, 150), width=44)
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    im.alpha_composite(glow)
    d = ImageDraw.Draw(im)
    d.line([a0, a1], fill=(255, 250, 226, 255), width=3)
    d.line([(a0[0], a0[1] + 6), (a1[0], a1[1] + 6)], fill=(255, 236, 170, 140), width=1)
    # sparkles on the brightest facets
    for _ in range(26):
        sx, sy = rnd.uniform(x0 + 10, x1 - 10), rnd.uniform(y0 + 10, y1 - 100)
        s = rnd.choice((2, 3, 3, 4, 6))
        d.line([(sx - s, sy), (sx + s, sy)], fill=(255, 252, 236, 230), width=1)
        d.line([(sx, sy - s), (sx, sy + s)], fill=(255, 252, 236, 230), width=1)
    # the plate for the name and flags: darkened, with a gold rule on top
    plate = Image.new("RGBA", im.size, (0, 0, 0, 0))
    pa = np.zeros((TPL_H, TPL_W), np.float32)
    top = y0 + int((y1 - y0) * 0.70)
    pa[top:, :] = np.clip((np.arange(TPL_H - top)[:, None] / 40.0), 0, 1) * 225
    plate.putalpha(Image.fromarray(pa.astype(np.uint8)))
    plate_rgb = Image.new("RGBA", im.size, (20, 12, 4, 255))
    plate_rgb.putalpha(plate.split()[3])
    im.alpha_composite(plate_rgb)
    d = ImageDraw.Draw(im)
    d.line([(x0 + 30, top + 6), (x1 - 30, top + 6)], fill=(232, 186, 80, 255), width=2)
    return im


def frame_ring(with_crest=True):
    """The chamfered gold ring, bevelled, and the star crest."""
    x0, y0, x1, y1 = BODY
    outer = octagon((x0 - 6, y0 - 6, x1 + 6, y1 + 6), CHAMFER + 3)
    inner = octagon((x0 + RING - 6, y0 + RING - 6, x1 - RING + 6, y1 - RING + 6), CHAMFER - 4)
    m = np.asarray(mask_of(outer)).astype(np.float32) / 255.0
    mi = np.asarray(mask_of(inner)).astype(np.float32) / 255.0
    ring = np.clip(m - mi, 0, 1)
    yy, xx = np.mgrid[0:TPL_H, 0:TPL_W].astype(np.float32)
    # bevel: bright on the outer lip, dark on the inner lip, metal bands sweeping across
    dist_out = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))) / 255.0
    bands = 0.5 + 0.5 * np.sin((xx * 0.8 + yy) / 26.0)
    t = 0.30 + 0.45 * bands + 0.30 * (1 - dist_out)
    rgb = ramp(np.clip(t, 0, 1))
    alpha = (ring * 255).astype(np.float32)
    im = Image.fromarray(np.dstack([rgb, alpha]).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(im)
    d.polygon(outer, outline=(60, 34, 6, 255))
    d.polygon(octagon((x0 - 4, y0 - 4, x1 + 4, y1 + 4), CHAMFER + 2), outline=(255, 240, 190, 255))
    d.polygon(inner, outline=(70, 40, 8, 255))
    d.polygon(octagon((x0 + RING - 4, y0 + RING - 4, x1 - RING + 4, y1 - RING + 4), CHAMFER - 3),
              outline=(250, 214, 120, 255))
    # facet glints on the four cut corners
    for cx, cy in ((x0 + 6, y0 + 6), (x1 - 6, y0 + 6), (x0 + 6, y1 - 6), (x1 - 6, y1 - 6)):
        d.polygon([(cx - 5, cy), (cx, cy - 5), (cx + 5, cy), (cx, cy + 5)], fill=(255, 250, 226, 255))
    if with_crest:
        cx, cy = (x0 + x1) / 2, y0 - 4
        d.polygon(star(cx, cy, 30, 13), fill=(60, 34, 6, 255))
        d.polygon(star(cx, cy, 27, 11.5), fill=(240, 190, 76, 255))
        d.polygon(star(cx, cy - 1, 19, 8), fill=(255, 226, 140, 255))
        d.polygon([(cx, cy - 27), (cx + 6, cy - 6), (cx, cy)], fill=(255, 250, 222, 255))   # the lit point
    return im


def gem(im):
    """A gold-and-white diamond at the foot."""
    x0, y0, x1, y1 = BODY
    cx, cy = (x0 + x1) / 2, y1 + 2
    d = ImageDraw.Draw(im)
    d.polygon([(cx, cy - 20), (cx + 17, cy), (cx, cy + 20), (cx - 17, cy)], fill=(60, 34, 6, 255))
    d.polygon([(cx, cy - 17), (cx + 14, cy), (cx, cy + 17), (cx - 14, cy)], fill=(232, 186, 80, 255))
    d.polygon([(cx, cy - 17), (cx + 14, cy), (cx, cy)], fill=(255, 244, 200, 255))
    d.polygon([(cx - 14, cy), (cx, cy + 17), (cx, cy)], fill=(150, 98, 20, 255))
    return im


def label(im):
    x0, y0, x1, y1 = BODY
    try:
        font = ImageFont.truetype(FONT, 13)
    except Exception:
        font = ImageFont.load_default()
    d = ImageDraw.Draw(im)
    txt = "STAR  SIGNING"
    w = d.textlength(txt, font=font)
    cx, y = (x0 + x1) / 2, y1 - 34
    d.text((cx - w / 2 + 1, y + 1), txt, font=font, fill=(30, 16, 2, 255))
    d.text((cx - w / 2, y), txt, font=font, fill=(250, 214, 120, 255))
    for side in (-1, 1):
        sx = cx + side * (w / 2 + 14)
        d.polygon(star(sx, y + 8, 6, 2.6), fill=(250, 214, 120, 255))
    return im


def pin_corners(im):
    """A barely-there pixel in two corners: the game trims empty edges off a template before
    scaling it, and this card must keep the full 400 x 500 like the others (make_champ_cards.py)."""
    im.putpixel((0, 0), (0, 0, 0, 1))
    im.putpixel((TPL_W - 1, TPL_H - 1), (0, 0, 0, 1))
    return im


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites")
    os.makedirs(out, exist_ok=True)
    rnd = random.Random(1110)
    x0, y0, x1, y1 = BODY
    body_mask = mask_of(octagon((x0, y0, x1, y1), CHAMFER))
    card = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    bg = background(rnd)
    card.paste(bg, (0, 0), body_mask)
    over = label(frame_ring())                          # the label rides on the frame: over the player
    card.alpha_composite(over)
    card = gem(card)
    pin_corners(card).save(os.path.join(out, "tpl_stargold_card.png"))
    pin_corners(over).save(os.path.join(out, "tpl_stargoldframe_card.png"))
    prev = Image.new("RGBA", (TPL_W, TPL_H), (24, 24, 30, 255))
    prev.alpha_composite(card)
    prev.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "stargold_preview.png"))
    print("gold crystal card written to", out)


if __name__ == "__main__":
    main()
