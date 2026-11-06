"""THE SEASON 1 card (6 Nov) - the exclusive card at tier 50 of the Season 1 pass.

    python3 make_s1_card.py [out_dir]

This game's own design: the gold card's chamfered shape (make_star_gold.py) in the season's colours -
deep teal fading to near black, a huge "1" standing behind the player, the centre circle and halfway
line of a pitch drawn faintly across it, light rays rising from the foot, and a pale-gold frame. A
shield crest at the top with "S1" on it, a teal gem at the foot. No real logo or competition mark.

  tpl_s1_card.png       everything round the player
  tpl_s1frame_card.png  the frame and the crest only, laid OVER the player
  s1card_preview.png    a look at it (not used by the game)
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from make_star_gold import BODY, CHAMFER, FONT, RING, TPL_H, TPL_W, mask_of, octagon, pin_corners, ramp

TEAL = [(2, 14, 18), (6, 40, 46), (12, 90, 92), (30, 160, 150), (120, 230, 210), (230, 255, 248)]
PALE_GOLD = [(50, 36, 10), (120, 92, 34), (196, 160, 80), (236, 214, 140), (252, 240, 196), (255, 252, 236)]


def background(rnd):
    x0, y0, x1, y1 = BODY
    yy, xx = np.mgrid[0:TPL_H, 0:TPL_W].astype(np.float32)
    cx = (x0 + x1) / 2
    # teal from the foot, darker at the top
    t = 0.12 + 0.48 * np.clip((yy - y0) / (y1 - y0), 0, 1) ** 1.4
    # light rays rising from the foot
    ang = np.arctan2(yy - (y1 + 30), xx - cx)
    rays = (0.5 + 0.5 * np.cos(ang * 18)) ** 6 * np.clip((yy - y0) / (y1 - y0), 0, 1)
    t = t + 0.16 * rays
    rgb = ramp(np.clip(t, 0, 1), TEAL)
    im = Image.fromarray(np.dstack([rgb, np.full(rgb.shape[:2], 255.0)]).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(im)
    # the pitch: halfway line and centre circle, faint
    line = (120, 230, 210, 70)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    my = y0 + (y1 - y0) * 0.42
    ld.line([(x0, my), (x1, my)], fill=line, width=2)
    ld.ellipse((cx - 92, my - 92, cx + 92, my + 92), outline=line, width=2)
    ld.ellipse((cx - 4, my - 4, cx + 4, my + 4), fill=line)
    im.alpha_composite(lay)
    # the big "1" behind him
    try:
        big = ImageFont.truetype(FONT, 330)
    except Exception:
        big = ImageFont.load_default()
    one = Image.new("RGBA", im.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(one)
    w = od.textlength("1", font=big)
    od.text((cx - w / 2 + 30, y0 - 10), "1", font=big, fill=(150, 240, 220, 46), stroke_width=3,
            stroke_fill=(190, 255, 236, 110))
    im.alpha_composite(one.filter(ImageFilter.GaussianBlur(0.8)))
    # glints drifting up
    for _ in range(40):
        sx, sy = rnd.uniform(x0 + 8, x1 - 8), rnd.uniform(y0 + 8, y1 - 60)
        s = rnd.choice((1, 2, 2, 3, 5))
        a = rnd.randint(120, 230)
        d.line([(sx - s, sy), (sx + s, sy)], fill=(230, 255, 248, a), width=1)
        d.line([(sx, sy - s), (sx, sy + s)], fill=(230, 255, 248, a), width=1)
    # the name plate: darkened, with a pale-gold rule
    pa = np.zeros((TPL_H, TPL_W), np.float32)
    top = y0 + int((y1 - y0) * 0.70)
    pa[top:, :] = np.clip((np.arange(TPL_H - top)[:, None] / 40.0), 0, 1) * 225
    plate = Image.new("RGBA", im.size, (2, 12, 14, 255))
    plate.putalpha(Image.fromarray(pa.astype(np.uint8)))
    im.alpha_composite(plate)
    d = ImageDraw.Draw(im)
    d.line([(x0 + 30, top + 6), (x1 - 30, top + 6)], fill=(236, 214, 140, 255), width=2)
    return im


def frame_ring():
    x0, y0, x1, y1 = BODY
    outer = octagon((x0 - 6, y0 - 6, x1 + 6, y1 + 6), CHAMFER + 3)
    inner = octagon((x0 + RING - 6, y0 + RING - 6, x1 - RING + 6, y1 - RING + 6), CHAMFER - 4)
    m = np.asarray(mask_of(outer)).astype(np.float32) / 255.0
    mi = np.asarray(mask_of(inner)).astype(np.float32) / 255.0
    ring = np.clip(m - mi, 0, 1)
    yy, xx = np.mgrid[0:TPL_H, 0:TPL_W].astype(np.float32)
    dist_out = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))) / 255.0
    bands = 0.5 + 0.5 * np.sin((xx * 0.8 - yy) / 24.0)
    t = 0.32 + 0.45 * bands + 0.28 * (1 - dist_out)
    rgb = ramp(np.clip(t, 0, 1), PALE_GOLD)
    im = Image.fromarray(np.dstack([rgb, (ring * 255)]).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(im)
    d.polygon(outer, outline=(40, 28, 8, 255))
    d.polygon(octagon((x0 - 4, y0 - 4, x1 + 4, y1 + 4), CHAMFER + 2), outline=(255, 250, 226, 255))
    d.polygon(inner, outline=(10, 50, 52, 255))
    d.polygon(octagon((x0 + RING - 4, y0 + RING - 4, x1 - RING + 4, y1 - RING + 4), CHAMFER - 3),
              outline=(120, 230, 210, 255))
    # a teal stud on each cut corner
    for cx, cy in ((x0 + 6, y0 + 6), (x1 - 6, y0 + 6), (x0 + 6, y1 - 6), (x1 - 6, y1 - 6)):
        d.polygon([(cx - 5, cy), (cx, cy - 5), (cx + 5, cy), (cx, cy + 5)], fill=(150, 255, 230, 255))
    # the crest: a shield with S1 on it
    cx, cy = (x0 + x1) / 2, y0 - 6
    sh = lambda k: [(cx - 26 * k, cy - 22 * k), (cx + 26 * k, cy - 22 * k), (cx + 26 * k, cy + 6 * k),
                    (cx, cy + 26 * k), (cx - 26 * k, cy + 6 * k)]
    d.polygon(sh(1.0), fill=(40, 28, 8, 255))
    d.polygon(sh(0.88), fill=(236, 214, 140, 255))
    d.polygon(sh(0.74), fill=(8, 70, 72, 255))
    try:
        f = ImageFont.truetype(FONT, 20)
    except Exception:
        f = ImageFont.load_default()
    tw = d.textlength("S1", font=f)
    d.text((cx - tw / 2, cy - 15), "S1", font=f, fill=(250, 240, 196, 255))
    return im


def gem(im):
    x0, y0, x1, y1 = BODY
    cx, cy = (x0 + x1) / 2, y1 + 2
    d = ImageDraw.Draw(im)
    d.polygon([(cx, cy - 20), (cx + 17, cy), (cx, cy + 20), (cx - 17, cy)], fill=(40, 28, 8, 255))
    d.polygon([(cx, cy - 17), (cx + 14, cy), (cx, cy + 17), (cx - 14, cy)], fill=(30, 170, 156, 255))
    d.polygon([(cx, cy - 17), (cx + 14, cy), (cx, cy)], fill=(200, 255, 240, 255))
    d.polygon([(cx - 14, cy), (cx, cy + 17), (cx, cy)], fill=(8, 80, 80, 255))
    return im


def label(im):
    x0, y0, x1, y1 = BODY
    try:
        font = ImageFont.truetype(FONT, 13)
    except Exception:
        font = ImageFont.load_default()
    d = ImageDraw.Draw(im)
    txt = "SEASON  1"
    w = d.textlength(txt, font=font)
    cx, y = (x0 + x1) / 2, y1 - 34
    d.text((cx - w / 2 + 1, y + 1), txt, font=font, fill=(2, 12, 14, 255))
    d.text((cx - w / 2, y), txt, font=font, fill=(236, 214, 140, 255))
    for side in (-1, 1):
        sx = cx + side * (w / 2 + 14)
        d.polygon([(sx, y + 2), (sx + 5, y + 8), (sx, y + 14), (sx - 5, y + 8)], fill=(150, 255, 230, 255))
    return im


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "sprites")
    os.makedirs(out, exist_ok=True)
    rnd = random.Random(2026)
    x0, y0, x1, y1 = BODY
    card = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    card.paste(background(rnd), (0, 0), mask_of(octagon((x0, y0, x1, y1), CHAMFER)))
    over = label(frame_ring())
    card.alpha_composite(over)
    card = gem(card)
    pin_corners(card).save(os.path.join(out, "tpl_s1_card.png"))
    pin_corners(over).save(os.path.join(out, "tpl_s1frame_card.png"))
    prev = Image.new("RGBA", (TPL_W, TPL_H), (24, 24, 30, 255))
    prev.alpha_composite(card)
    prev.save(os.path.join(here, "s1card_preview.png"))
    print("Season 1 card written to", out)


if __name__ == "__main__":
    main()
