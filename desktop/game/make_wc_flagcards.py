"""The World Cup flag card frame (25 Oct, from Hubi's FC card picture).

    python3 make_wc_flagcards.py [out_dir]

The card is a box with two corners rounded right off - top-right and bottom-left - and the other
two only just softened. Pool A gets it in gold, pool B in silver. The FLAG is not in these files:
the game waves the nation's own flag behind and inside the card while you look at it, so it moves
like cloth in the wind. These are the layers the game puts round it:

  tpl_fgold_card.png / tpl_fsilver_card.png        everything that is NOT the flag: the shadow the
                                                   card throws on the flag behind it, the dark plate
                                                   the name sits on, the pool under the rating, the
                                                   frame and the gem
  tpl_fgoldframe_card.png / tpl_fsilverframe_card.png   just the frame - laid OVER the player so his
                                                   arms end at the curve (the gem stays behind him)
  tpl_fmask_card.png                               the card's shape: the inside flag is cut to it

Same 400 x 500 canvas and BODY box as make_art.py's templates.
"""
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw

TPL_W, TPL_H = 400, 500
BODY = (66, 34, 334, 458)
WHITE = (255, 255, 255)
GOLD = [(255, 246, 206), (232, 182, 72), (160, 108, 26), (252, 224, 140), (196, 140, 40),
        (255, 240, 190), (176, 120, 30), (255, 246, 206)]
SILVER = [(250, 252, 255), (196, 202, 216), (120, 128, 146), (236, 240, 248), (160, 168, 186),
          (248, 250, 255), (140, 148, 166), (250, 252, 255)]


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def layer():
    return Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))


def pin_corners(im):
    """The game trims a template to its visible part before scaling: keep the full frame."""
    im.putpixel((0, 0), (0, 0, 0, 1))
    im.putpixel((im.width - 1, im.height - 1), (0, 0, 0, 1))


def sweep(size, stops, steps=240, repeats=1.3):
    w, h = size
    band = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(band)
    span = w + h
    for i in range(steps):
        t = (i / float(steps - 1) * repeats) % 1.0
        k = t * (len(stops) - 1)
        col = mix(stops[int(k)], stops[min(len(stops) - 1, int(k) + 1)], k - int(k))
        x = -h + span * i / float(steps - 1)
        d.line([(x, 0), (x + h, h)], fill=col, width=int(span / steps) + 3)
    return band


def fc_path(box, steps=30):
    """Top-left and bottom-right barely rounded; top-right and bottom-left rounded right off."""
    x0, y0, x1, y1 = box
    w = x1 - x0
    small, big = w * 0.035, w * 0.38
    pts = []
    for (cx, cy, r, a0) in ((x0 + small, y0 + small, small, math.pi), (x1 - big, y0 + big, big, -math.pi / 2),
                            (x1 - small, y1 - small, small, 0.0), (x0 + big, y1 - big, big, math.pi / 2)):
        for i in range(steps + 1):
            a = a0 + math.pi / 2 * i / steps
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def shape_mask(box=BODY):
    m = Image.new("L", (TPL_W, TPL_H), 0)
    ImageDraw.Draw(m).polygon(fc_path(box), fill=255)
    return m


def gem(d, cx, cy, tier):
    base, light = ((150, 158, 176), (196, 204, 220)) if tier == "A" else ((120, 130, 150), (186, 194, 210))
    d.polygon([(cx, cy - 20), (cx + 21, cy - 8), (cx + 21, cy + 12), (cx, cy + 24),
               (cx - 21, cy + 12), (cx - 21, cy - 8)], fill=base, outline=(236, 242, 252))
    d.polygon([(cx, cy - 13), (cx + 13, cy - 6), (cx + 13, cy + 7), (cx, cy + 15),
               (cx - 13, cy + 7), (cx - 13, cy - 6)], fill=light)


def frame_ring(tier):
    x0, y0, x1, y1 = BODY
    path = fc_path(BODY)
    out = layer()
    d = ImageDraw.Draw(out)
    d.line(path + [path[0]], fill=(56, 36, 6) if tier == "A" else (40, 44, 58), width=15, joint="curve")
    ring = Image.new("L", out.size, 0)
    ImageDraw.Draw(ring).line(path + [path[0]], fill=255, width=10, joint="curve")
    out.paste(sweep(out.size, GOLD if tier == "A" else SILVER), (0, 0), ring)
    d.line(path + [path[0]], fill=(255, 248, 214) if tier == "A" else WHITE, width=2, joint="curve")
    inner = fc_path((x0 + 9, y0 + 9, x1 - 9, y1 - 9))
    d.line(inner + [inner[0]], fill=(120, 80, 14, 200) if tier == "A" else (90, 98, 118, 200), width=2,
           joint="curve")
    return out


def top_layer(tier):
    """Everything round the flag: the card's shadow on the flag behind, plate, pool, frame, gem."""
    x0, y0, x1, y1 = BODY
    inside = shape_mask()
    im = layer()
    drop = layer()
    ImageDraw.Draw(drop).polygon(fc_path((x0 + 6, y0 + 10, x1 + 10, y1 + 12)), fill=(2, 4, 12, 130))
    drop.putalpha(ImageChops.multiply(drop.split()[3], ImageChops.invert(inside)))   # only outside the card
    im.alpha_composite(drop)
    card = layer()
    pd = ImageDraw.Draw(card)
    for y in range(312, y1 + 1):                                   # the name sits on this
        a = int(242 * min(1.0, ((y - 312) / 46.0) ** 1.4))
        pd.line([(x0, y), (x1, y)], fill=(6, 10, 22, a))
    pool = layer()
    pl = ImageDraw.Draw(pool)
    for k in range(26):                                             # pale flags need a pool under the rating
        pl.ellipse([x0 - 140 + k * 6, y0 - 130 + k * 6, x0 + 232 - k * 6, y0 + 218 - k * 6], fill=(3, 6, 18, 22))
    card.alpha_composite(pool)
    shine = layer()                                                 # a soft glossy streak across the card
    ImageDraw.Draw(shine).polygon([(x0 + 150, y0), (x0 + 196, y0), (x0 + 60, y1), (x0 + 14, y1)],
                                  fill=(255, 255, 255, 18))
    card.alpha_composite(shine)
    card.putalpha(ImageChops.multiply(card.split()[3], inside))
    im.alpha_composite(card)
    im.alpha_composite(frame_ring(tier))
    gem(ImageDraw.Draw(im), (x0 + x1) // 2, y1 - 2, tier)
    pin_corners(im)
    return im


def frame_overlay(tier):
    """Just the frame, with the gem's spot cut out so it stays behind the player."""
    x0, y0, x1, y1 = BODY
    out = frame_ring(tier)
    hole = Image.new("L", out.size, 255)
    cx = (x0 + x1) // 2
    ImageDraw.Draw(hole).polygon([(cx + math.cos(math.pi / 6 + k * math.pi / 3) * 27,
                                   y1 - 2 + math.sin(math.pi / 6 + k * math.pi / 3) * 27) for k in range(6)], fill=0)
    out.putalpha(ImageChops.multiply(out.split()[3], hole))
    pin_corners(out)
    return out


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "sprites"
    os.makedirs(out, exist_ok=True)
    for tier, name in (("A", "fgold"), ("B", "fsilver")):
        top_layer(tier).save(os.path.join(out, "tpl_%s_card.png" % name))
        frame_overlay(tier).save(os.path.join(out, "tpl_%sframe_card.png" % name))
    m = Image.new("RGBA", (TPL_W, TPL_H), (255, 255, 255, 0))
    m.putalpha(shape_mask())
    pin_corners(m)
    m.save(os.path.join(out, "tpl_fmask_card.png"))
    print("World Cup flag card layers written to", out)


if __name__ == "__main__":
    main()
