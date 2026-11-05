"""The trophy cabinet's trophies (29 Oct), from Hubi's "make some banger designs in canva".

    python3 make_trophies.py [sprites_folder]

Three trophies were generated in Canva: the World Cup, the Champions Cup and the Impossible Cup
(art_src/trophies/canva_*.png, 149 x 199). Then the free plan's image credits ran out, so the
other five are built here out of those three, in the same style:

  trophy_wc.png             the Canva World Cup, as it is
  trophy_wc_impossible.png  the Canva Impossible Cup - its ball came out as an American football,
                            so a real one goes in: the World Cup's ball, turned black and red
  trophy_cup.png            the Canva Champions Cup, as it is
  trophy_league_0.png       PREMIER LEAGUE: the cup in gold, a purple base, a gold crown for a lid
  trophy_league_1.png       CHAMPIONSHIP: the cup in steel blue-silver, a dome lid, blue ribbons
  trophy_league_2.png       LEAGUE ONE: the cup in bronze, a green base, green ribbons
  trophy_promotions.png     the World Cup's gold ball as a medal on a green and white ribbon
  trophy_perfect.png        a gold star on the World Cup's base
  trophy_gauntlet.png       THE GAUNTLET: the cup in blackened iron, a blood-red base and ribbons,
                            a crown with a red gem (30 Oct)

Every one is cut out of its black background (flood fill from the edges, so dark parts of the
trophy itself stay) and saved with transparency.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "art_src", "trophies")


def load(name):
    return np.asarray(Image.open(os.path.join(SRC, name)).convert("RGB")).astype(np.float32)


def cut_out(rgb, thresh=22):
    """RGBA: the black background (reached from the edges) becomes transparent."""
    h, w, _ = rgb.shape
    dark = rgb.max(2) < thresh
    bg = np.zeros((h, w), bool)
    stack = [(y, x) for y in range(h) for x in (0, w - 1)] + [(y, x) for x in range(w) for y in (0, h - 1)]
    while stack:
        y, x = stack.pop()
        if bg[y, x] or not dark[y, x]:
            continue
        bg[y, x] = True
        if y > 0: stack.append((y - 1, x))
        if y < h - 1: stack.append((y + 1, x))
        if x > 0: stack.append((y, x - 1))
        if x < w - 1: stack.append((y, x + 1))
    # black pockets the edges can't reach (inside a handle): any big enough patch of pure black
    from scipy import ndimage as ndi
    lab, n = ndi.label(rgb.max(2) < 14)
    if n:
        sizes = ndi.sum(np.ones_like(lab), lab, range(1, n + 1))
        for k, size in enumerate(sizes, 1):
            if size >= 40:
                bg |= lab == k
    a = np.where(bg, 0, 255).astype(np.uint8)
    # soften the very edge: near-black edge pixels go half see-through
    edge = (~bg) & (rgb.max(2) < 40)
    a[edge] = 160
    return np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), a])


def lum(rgb):
    return (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]) / 255.0


def ramp(t, stops):
    """t 0..1 through a list of colours."""
    stops = np.asarray(stops, np.float32)
    k = np.clip(t, 0, 1) * (len(stops) - 1)
    i = np.clip(np.floor(k).astype(int), 0, len(stops) - 2)
    f = (k - i)[..., None]
    return stops[i] * (1 - f) + stops[i + 1] * f


GOLD = [(30, 16, 4), (110, 64, 12), (190, 128, 30), (236, 186, 70), (255, 232, 150), (255, 252, 230)]
BRONZE = [(26, 12, 6), (92, 44, 18), (156, 88, 44), (206, 136, 80), (240, 190, 140), (255, 236, 214)]
STEEL = [(16, 20, 34), (56, 70, 100), (112, 134, 170), (170, 192, 224), (220, 234, 250), (255, 255, 255)]
PURPLE = [(18, 6, 34), (60, 20, 110), (120, 60, 200), (176, 120, 255), (230, 200, 255)]
GREEN = [(4, 24, 12), (14, 80, 40), (40, 150, 80), (110, 220, 140), (210, 255, 220)]
IRON = [(4, 3, 6), (18, 16, 24), (40, 36, 48), (72, 64, 78), (130, 104, 112), (236, 150, 140)]
BLOOD = [(20, 2, 4), (90, 8, 16), (170, 20, 32), (236, 60, 60), (255, 170, 160)]
LBLUE = [(8, 18, 44), (30, 80, 160), (80, 150, 240), (160, 210, 255), (230, 245, 255)]


def recolour(rgb, region, stops, gamma=1.0):
    out = rgb.copy()
    t = lum(rgb) ** gamma
    out[region] = ramp(t[region], stops)
    return out


def cup_parts(rgb):
    """The Champions Cup's silver body and its blue base band (by colour)."""
    h, w, _ = rgb.shape
    yy = np.arange(h)[:, None].repeat(w, 1)
    lit = rgb.max(2) > 22
    blue = (rgb[..., 2] > rgb[..., 0] + 14) & (yy > 150) & lit
    body = lit & ~blue
    return body, blue


def draw_ribbons(img, colour, dark):
    """Two little ribbon bows tied where the handles meet the bowl."""
    d = ImageDraw.Draw(img)
    for cx in (36, 113):
        y = 52
        d.polygon([(cx, y), (cx - 9, y - 6), (cx - 9, y + 6)], fill=colour, outline=dark)
        d.polygon([(cx, y), (cx + 9, y - 6), (cx + 9, y + 6)], fill=colour, outline=dark)
        d.polygon([(cx - 2, y + 2), (cx - 6, y + 18), (cx - 2, y + 15), (cx + 1, y + 19)], fill=colour, outline=dark)
        d.polygon([(cx + 2, y + 2), (cx + 7, y + 17), (cx + 3, y + 15)], fill=colour, outline=dark)
        d.rectangle([cx - 2, y - 2, cx + 2, y + 2], fill=dark)


def crown(img, cx, y, metal, gem):
    d = ImageDraw.Draw(img)
    pts = [(cx - 22, y + 14), (cx - 22, y - 2), (cx - 12, y + 6), (cx, y - 10), (cx + 12, y + 6), (cx + 22, y - 2),
           (cx + 22, y + 14)]
    d.polygon(pts, fill=metal[3], outline=metal[1])
    d.polygon([(cx - 22, y + 8), (cx + 22, y + 8), (cx + 22, y + 14), (cx - 22, y + 14)], fill=metal[2])
    d.line([(cx - 18, y + 1), (cx - 12, y + 6)], fill=metal[5], width=1)
    for x, yy in ((cx - 22, y - 3), (cx, y - 11), (cx + 22, y - 3)):
        d.ellipse([x - 3, yy - 3, x + 3, yy + 3], fill=metal[5], outline=metal[1])
    d.ellipse([cx - 4, y + 7, cx + 4, y + 13], fill=gem, outline=metal[1])


def dome(img, cx, y, metal):
    d = ImageDraw.Draw(img)
    d.pieslice([cx - 34, y - 14, cx + 34, y + 30], 180, 360, fill=metal[3], outline=metal[1])
    d.pieslice([cx - 30, y - 10, cx - 4, y + 24], 200, 260, fill=metal[4])
    d.rectangle([cx - 4, y - 24, cx + 4, y - 12], fill=metal[3], outline=metal[1])
    d.ellipse([cx - 7, y - 32, cx + 7, y - 18], fill=metal[4], outline=metal[1])


def make_league(cup, metal, base_stops, ribbon, lid=None, gem=None):
    body, blue = cup_parts(cup)
    rgb = recolour(cup, body, metal, 0.95)
    rgb = recolour(rgb, blue, base_stops, 1.0)
    img = Image.fromarray(cut_out(rgb), "RGBA")
    pal = [tuple(int(c) for c in s) for s in metal]
    if lid == "crown":
        crown(img, 74, 18, pal, gem or (150, 60, 220))
    elif lid == "dome":
        dome(img, 74, 30, pal)
    draw_ribbons(img, ribbon[0], ribbon[1])
    return img


def football(wc, colours):
    """The World Cup's ball (a circle cut from the top of the trophy), recoloured."""
    cx, cy, r = 74, 40, 33
    h, w, _ = wc.shape
    yy, xx = np.mgrid[0:h, 0:w]
    disc = (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r
    ball = recolour(wc, disc, colours, 1.1)
    return ball, disc, (cx, cy, r)


def make_impossible(imp, wc):
    ball, disc, (cx, cy, r) = football(wc, [(4, 2, 4), (24, 6, 10), (70, 12, 20), (160, 30, 40), (255, 120, 100)])
    out = imp.copy()
    # the new ball sits where the oval one was (a little up and to the left of the trophy's centre)
    tx, ty = 72, 46
    sy, sx = np.nonzero(disc)
    for y, x in zip(sy, sx):
        X, Y = x - cx + tx, y - cy + ty
        if 0 <= X < out.shape[1] and 0 <= Y < out.shape[0]:
            out[Y, X] = ball[y, x]
    # put the brightest flames back over the ball's edge so it sits inside the fire
    flames = (imp[..., 0] > 170) & (imp[..., 1] < 110) & (imp[..., 2] < 110)
    h, w, _ = imp.shape
    yy, xx = np.mgrid[0:h, 0:w]
    rim = flames & ((xx - tx) ** 2 + (yy - ty) ** 2 > (r - 6) ** 2)
    out[rim] = imp[rim]
    return Image.fromarray(cut_out(out), "RGBA")


def make_medal(wc):
    ball, disc, (cx, cy, r) = football(wc, GOLD)
    img = Image.new("RGBA", (149, 199), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # the ribbon: green and white stripes in a V
    for k, col in enumerate([(30, 150, 70), (240, 244, 250), (30, 150, 70), (240, 244, 250), (30, 150, 70)]):
        d.polygon([(40 + k * 7, 6), (47 + k * 7, 6), (78 + k * 2, 110), (71 + k * 2, 110)], fill=col)
        d.polygon([(110 - k * 7, 6), (103 - k * 7, 6), (72 - k * 2, 110), (79 - k * 2, 110)], fill=col)
    d.rectangle([60, 104, 90, 118], fill=(190, 140, 40), outline=(110, 64, 12))
    # the medal: a gold rim round the World Cup's ball
    mx, my, R = 75, 150, 40
    d.ellipse([mx - R, my - R, mx + R, my + R], fill=(150, 96, 20), outline=(90, 50, 10))
    d.ellipse([mx - R + 4, my - R + 4, mx + R - 4, my + R - 4], fill=(240, 196, 80))
    arr = np.asarray(img).copy()
    sy, sx = np.nonzero(disc)
    k = (R - 8) / float(r)
    for y in range(my - R, my + R):
        for x in range(mx - R, mx + R):
            u, v = (x - mx) / k + cx, (y - my) / k + cy
            iu, iv = int(round(u)), int(round(v))
            if (x - mx) ** 2 + (y - my) ** 2 <= (R - 8) ** 2 and 0 <= iv < 199 and 0 <= iu < 149:
                arr[y, x, :3] = np.clip(ball[iv, iu], 0, 255)
                arr[y, x, 3] = 255
    img = Image.fromarray(arr, "RGBA")
    d = ImageDraw.Draw(img)
    d.arc([mx - R + 6, my - R + 6, mx + R - 6, my + R - 6], 200, 300, fill=(255, 250, 220), width=3)
    return img


def make_star(wc):
    out = Image.new("RGBA", (149, 199), (0, 0, 0, 0))
    base = Image.fromarray(cut_out(wc), "RGBA").crop((0, 150, 149, 199))   # the World Cup's green base
    out.alpha_composite(base, (0, 150))
    d = ImageDraw.Draw(out)
    d.polygon([(66, 152), (84, 152), (80, 96), (70, 96)], fill=(190, 128, 30), outline=(110, 64, 12))
    d.polygon([(68, 150), (73, 150), (72, 98), (70, 98)], fill=(255, 232, 150))
    cx, cy = 75, 62
    outer, inner = 52, 22
    pts = [(cx + math.cos(-math.pi / 2 + k * math.pi / 5) * (outer if k % 2 == 0 else inner),
            cy + math.sin(-math.pi / 2 + k * math.pi / 5) * (outer if k % 2 == 0 else inner)) for k in range(10)]
    d.polygon(pts, fill=(110, 64, 12))
    for k in range(5):                                       # bevelled arms: a light and a dark face each
        tip, a, b = pts[2 * k], pts[(2 * k - 1) % 10], pts[(2 * k + 1) % 10]
        lit = math.cos(-math.pi / 2 + k * 2 * math.pi / 5 + 0.9)
        c1 = tuple(int(v) for v in ramp(np.array(0.72 + 0.25 * lit), GOLD))
        c2 = tuple(int(v) for v in ramp(np.array(0.42 + 0.2 * lit), GOLD))
        d.polygon([(cx, cy), a, tip], fill=c1)
        d.polygon([(cx, cy), tip, b], fill=c2)
    d.polygon(pts, outline=(90, 50, 10))
    for (x, y, s) in ((30, 28, 7), (120, 40, 5), (112, 104, 6), (36, 96, 4)):   # sparkles
        d.line([(x - s, y), (x + s, y)], fill=(255, 252, 230), width=2)
        d.line([(x, y - s), (x, y + s)], fill=(255, 252, 230), width=2)
    return out


def main(out):
    os.makedirs(out, exist_ok=True)
    wc, cup, imp = load("canva_world_cup.png"), load("canva_champions_cup.png"), load("canva_impossible.png")
    made = {
        "wc": Image.fromarray(cut_out(wc), "RGBA"),
        "cup": Image.fromarray(cut_out(cup), "RGBA"),
        "wc_impossible": make_impossible(imp, wc),
        "league_0": make_league(cup, GOLD, PURPLE, ((150, 70, 230), (60, 20, 110)), lid="crown"),
        "league_1": make_league(cup, STEEL, LBLUE, ((90, 160, 250), (20, 50, 120)), lid="dome"),
        "league_2": make_league(cup, BRONZE, GREEN, ((40, 170, 90), (10, 70, 36))),
        "promotions": make_medal(wc),
        "perfect": make_star(wc),
        "gauntlet": make_league(cup, IRON, BLOOD, ((210, 30, 40), (70, 6, 10)), lid="crown", gem=(255, 40, 40)),
    }
    for key, img in made.items():
        img.save(os.path.join(out, "trophy_%s.png" % key))
    print("%d trophies written to %s" % (len(made), out))
    return made


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "sprites"))
