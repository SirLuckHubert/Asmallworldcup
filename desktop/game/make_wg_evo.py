"""THE WORLD'S GAME evolutions - the four stages of the card (1 Nov).

    python3 make_wg_evo.py [sprites dir]

Hubi: "first it starts off mostly grey with a little purple shards and the flag animated, the grey
one, and upgrading it just makes it better, add some crazy shine". The card is the World Cup flag
card's shape (its flag waves behind it and inside it - the game draws that, in grey at stage 1 and
gaining colour each stage). This writes the frame for each stage, re-coloured from the flag card's
gold frame, with purple crystal shards that grow in number and size:

  tpl_wgevo<N>_card.png       the card's top layer (frame, glass, name plate) - stage N = 0..3
  tpl_wgevo<N>frame_card.png  just the frame, laid over the player
  wgevo_stages.png            the four side by side (to look at)

  0 GREY       dull grey steel, three small dim shards
  1 AWAKENED   bright steel, six shards
  2 RADIANT    silver turning lilac, ten shards and a crystal crown
  3 LIMITLESS  chrome purple, sixteen shards, a big crown - the game adds the crazy shine
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites")
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites")

# the frame's colour ramp at each stage (dark -> light), and how the dark plate / glass is tinted
RAMPS = (((30, 30, 34), (70, 70, 76), (120, 120, 126), (168, 168, 174)),
         ((40, 42, 52), (96, 100, 116), (170, 176, 192), (232, 236, 246)),
         ((44, 30, 70), (110, 88, 150), (196, 176, 232), (246, 238, 255)),
         ((56, 14, 104), (140, 60, 220), (214, 150, 255), (255, 246, 255)))
PLATE = ((0.0, (16, 16, 20)), (0.25, (20, 18, 34)), (0.45, (28, 14, 52)), (0.7, (38, 8, 70)))
# (shard count, size range, shard colours: dark, mid, light)
SHARDS = ((3, (9, 13), ((54, 30, 80), (96, 60, 140), (140, 100, 180))),
          (6, (11, 18), ((64, 24, 112), (130, 70, 210), (190, 140, 250))),
          (10, (13, 24), ((72, 20, 132), (160, 86, 250), (222, 180, 255))),
          (16, (15, 30), ((80, 14, 150), (186, 100, 255), (246, 214, 255))))
CROWN = (None, None, (200, 40, 22), (200, 30, 40))       # (x, y, size) of the crystal crown, stages 2+
# places on the frame shards grow from: (x, y, outward angle in degrees), in the 400 x 500 template
SITES = [(70, 44, 225), (330, 456, 45), (334, 250, 0), (66, 300, 180), (300, 52, 300), (100, 456, 135),
         (66, 150, 190), (334, 380, 10), (200, 36, 270), (334, 120, 340), (150, 458, 100), (66, 400, 170),
         (250, 40, 280), (300, 458, 70), (334, 200, 355), (66, 230, 185)]


def ramp(lum, stops):
    t = np.clip(lum, 0, 1) * (len(stops) - 1)
    i = np.clip(t.astype(int), 0, len(stops) - 2)
    f = (t - i)[..., None]
    s = np.array(stops, np.float32)
    return s[i] * (1 - f) + s[i + 1] * f


def recolour(im, stage):
    """Gold -> this stage's metal; the dark plate and the glass streak tinted to match."""
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    rgb, al = a[..., :3], a[..., 3:]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    gold = (r > b + 30) & (r >= g)                          # the warm metal
    metal = ramp(lum ** 0.9, RAMPS[stage])
    tint_k, tint = PLATE[stage]
    grey = np.repeat(lum[..., None] * 255.0, 3, -1)
    plate = grey * (1 - tint_k) + (grey * 0.4 + np.array(tint, np.float32)) * tint_k
    out = np.where(gold[..., None], metal, plate)
    return Image.fromarray(np.dstack([np.clip(out, 0, 255), al]).astype(np.uint8), "RGBA")


def shard(d, x, y, ang, size, cols, rnd):
    """A purple crystal growing out from the frame: a long facet, lit on one side."""
    dark, mid, light = cols
    a = math.radians(ang + rnd.uniform(-18, 18))
    L = size * rnd.uniform(1.0, 1.45)
    wd = size * rnd.uniform(0.50, 0.72)
    tip = (x + math.cos(a) * L, y + math.sin(a) * L)
    px, py = -math.sin(a), math.cos(a)
    b1 = (x + px * wd, y + py * wd)
    b2 = (x - px * wd, y - py * wd)
    mid_pt = (x + math.cos(a) * L * 0.45, y + math.sin(a) * L * 0.45)
    d.polygon([b1, tip, b2], fill=dark + (255,))
    d.polygon([b1, tip, mid_pt], fill=mid + (255,))              # the lit face
    d.polygon([(b1[0] * 0.6 + tip[0] * 0.4, b1[1] * 0.6 + tip[1] * 0.4), tip, mid_pt], fill=light + (255,))
    d.line([b1, tip, b2], fill=(20, 6, 36, 255), width=2)
    d.line([mid_pt, tip], fill=(255, 246, 255, 200), width=1)


def crown(d, cx, cy, size, cols):
    """The crystal crown on top of the card (stages 2 and 3)."""
    dark, mid, light = cols
    for k, (dx, h) in enumerate(((-1.6, 0.8), (-0.8, 1.15), (0.0, 1.6), (0.8, 1.15), (1.6, 0.8))):
        x = cx + dx * size * 0.55
        pts = [(x - size * 0.32, cy), (x, cy - size * h), (x + size * 0.32, cy)]
        d.polygon(pts, fill=(mid if k % 2 else light) + (255,))
        d.polygon([pts[0], pts[1], (x, cy)], fill=dark + (255,))
        d.line(pts, fill=(20, 6, 36, 255), width=2)


def add_shards(im, stage, seed=4):
    rnd = random.Random(seed + stage * 17)
    d = ImageDraw.Draw(im)
    n, (s0, s1), cols = SHARDS[stage]
    for x, y, ang in SITES[:n]:
        shard(d, x, y, ang, rnd.uniform(s0, s1), cols, rnd)
        if stage >= 1:                                            # a cluster: smaller ones beside it
            for _ in range(1 if stage < 3 else 2):
                shard(d, x + rnd.uniform(-9, 9), y + rnd.uniform(-9, 9), ang + rnd.choice((-38, 38)),
                      rnd.uniform(s0, s1) * 0.65, cols, rnd)
    if CROWN[stage]:
        cx, cy, size = CROWN[stage]
        crown(d, cx, cy, size, cols)
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    top = Image.open(os.path.join(SRC, "tpl_fgold_card.png")).convert("RGBA")
    frame = Image.open(os.path.join(SRC, "tpl_fgoldframe_card.png")).convert("RGBA")
    sheet = Image.new("RGBA", (400 * 4, 500), (40, 60, 44, 255))
    for st in range(4):
        t = add_shards(recolour(top, st), st)
        f = add_shards(recolour(frame, st), st)
        t.save(os.path.join(OUT, "tpl_wgevo%d_card.png" % st))
        f.save(os.path.join(OUT, "tpl_wgevo%dframe_card.png" % st))
        sheet.alpha_composite(t, (st * 400, 0))
    sheet.save(os.path.join(OUT, "wgevo_stages.png"))
    print("World's Game evolution frames written to", OUT)


if __name__ == "__main__":
    main()
