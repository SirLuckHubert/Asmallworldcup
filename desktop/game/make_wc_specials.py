"""Two one-off World Cup cards, from the pictures Hubi sent on 25 Oct.

    python3 make_wc_specials.py [out_dir]

  tpl_gcr_card.png  / tpl_gcrframe_card.png    Messi: a heavy gold frame on a deep blue card with
                                               gold ribbons swirling behind him and blue ice
                                               crystals bursting out round the sides
  tpl_dpor_card.png / tpl_dporframe_card.png   Ronaldo: a "D" card - straight left edge, big round
                                               right side - with a thin gold edge and Portugal's
                                               flag flying behind it and filling it

Same 400 x 500 canvas and BODY box as every template in make_art.py. The *frame* files are the
same pictures with the inside cut out: the game lays them over the player so the frame and the
crystals sit in front of him (the gem at the foot stays behind him, like the Limit Breakers).
Everything is drawn here - no card art, no crests, no logos, no "TOTS" or any other EA label.
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

TPL_W, TPL_H = 400, 500
BODY = (66, 34, 334, 458)
WHITE = (255, 255, 255)


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def layer():
    return Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))


def mask_of(pts):
    m = Image.new("L", (TPL_W, TPL_H), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m


def pin_corners(im):
    """The game trims a template to its visible part before scaling: keep the full frame."""
    im.putpixel((0, 0), (0, 0, 0, 1))
    im.putpixel((im.width - 1, im.height - 1), (0, 0, 0, 1))


def sweep(size, stops, steps=240, repeats=1.0):
    """A diagonal band of colour stops - what makes metal look like it catches the light."""
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


GOLD_STOPS = [(255, 246, 206), (232, 182, 72), (160, 108, 26), (252, 224, 140), (196, 140, 40),
              (255, 240, 190), (176, 120, 30), (255, 246, 206)]


def rounded_path(box, r_tl, r_tr, r_br, r_bl, steps=24):
    x0, y0, x1, y1 = box
    pts = []
    for (cx, cy, r, a0) in ((x0 + r_tl, y0 + r_tl, r_tl, math.pi), (x1 - r_tr, y0 + r_tr, r_tr, -math.pi / 2),
                            (x1 - r_br, y1 - r_br, r_br, 0.0), (x0 + r_bl, y1 - r_bl, r_bl, math.pi / 2)):
        for i in range(steps + 1):
            a = a0 + math.pi / 2 * i / steps
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def hex_gem(d, cx, cy, r, base, light, edge):
    pts = [(cx + math.cos(math.pi / 6 + k * math.pi / 3) * r, cy + math.sin(math.pi / 6 + k * math.pi / 3) * r)
           for k in range(6)]
    d.polygon(pts, fill=base, outline=edge)
    inner = [(cx + (x - cx) * 0.62, cy + (y - cy) * 0.62) for x, y in pts]
    d.polygon(inner, fill=light)
    d.polygon([inner[3], inner[4], (cx, cy)], fill=mix(light, WHITE, 0.5))
    d.polygon([inner[0], inner[1], (cx, cy)], fill=mix(base, (0, 0, 0), 0.3))
    return pts


def wave(img, w, h, phase=0.0, amp=0.06, folds=2.6):
    """Cloth: columns shifted on a sine and lit on the crests (make_art.wave_flag's trick)."""
    src = img.convert("RGBA").resize((w, h), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for x in range(w):
        t = x / float(max(1, w - 1))
        shift = int(round(math.sin(t * folds * math.tau + phase) * h * amp))
        light = 0.80 + 0.30 * (0.5 + 0.5 * math.cos(t * folds * math.tau + phase))
        strip = ImageEnhance.Brightness(src.crop((x, 0, x + 1, h))).enhance(light)
        out.paste(strip, (x, shift))
        if shift > 0:
            out.paste(strip.crop((0, 0, 1, shift)), (x, 0))
        elif shift < 0:
            out.paste(strip.crop((0, h + shift, 1, h)), (x, h + shift))
    return out


# ============================================================== MESSI: gold and blue crystal
def gcr_path(box):
    """Rounded top, the sides running straight down, the bottom cut in to a shallow point."""
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2.0
    pts = rounded_path((x0, y0, x1, y1 - 30), 16, 16, 0, 0, 12)[:26]   # the two top corners
    pts += [(x1, y1 - 46), (x1 - 34, y1 - 10), (cx + 46, y1 - 4), (cx, y1 + 6), (cx - 46, y1 - 4),
            (x0 + 34, y1 - 10), (x0, y1 - 46)]
    return pts


def shard(d, base_pt, ang, ln, wd, rnd, tones):
    """One ice crystal: a long sliver, lit on one face, dark on the other, a white edge."""
    ca, sa = math.cos(ang), math.sin(ang)
    tip = (base_pt[0] + ca * ln, base_pt[1] + sa * ln)
    nx, ny = -sa * wd, ca * wd
    mid = (base_pt[0] + ca * ln * 0.35, base_pt[1] + sa * ln * 0.35)
    a = (mid[0] + nx, mid[1] + ny)
    b = (mid[0] - nx, mid[1] - ny)
    d.polygon([base_pt, a, tip], fill=tones[2])
    d.polygon([base_pt, b, tip], fill=tones[1])
    d.line([base_pt, tip], fill=tones[3], width=1)
    d.line([a, tip], fill=WHITE, width=1)


ICE = [(14, 40, 120), (40, 110, 220), (110, 190, 255), (220, 244, 255)]


def crystals(rnd, front):
    """Ice shards bursting out round the card's sides and lower corners."""
    lay = layer()
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = BODY
    spots = []
    for side in (-1, 1):
        ex = x0 if side < 0 else x1
        for k in range(16):                                    # a wall of ice up each side,
            y = y0 + 30 + k * 26 + rnd.uniform(-8, 8)          # bigger the lower it goes
            big = 0.7 + 0.7 * (k / 15.0)
            up = rnd.uniform(-1.0, 0.35)                       # most lean up and out
            spots.append(((ex - side * 10, y), (math.pi - up if side < 0 else up), rnd.uniform(30, 50) * big,
                          rnd.uniform(10, 16) * big))
        for k in range(8):                                     # a burst off each lower corner
            ang = (math.pi * 0.64 if side < 0 else math.pi * 0.36) + side * (-0.42 + k * 0.13)
            spots.append(((ex - side * 34, y1 - 34), ang, rnd.uniform(48, 78), rnd.uniform(11, 17)))
        for k in range(4):                                     # and off the top corners
            ang = (math.pi * 1.22 if side < 0 else -math.pi * 0.22) + rnd.uniform(-0.3, 0.3)
            spots.append(((ex - side * 6, y0 + 20 + k * 16), ang, rnd.uniform(30, 48), rnd.uniform(7, 11)))
    rnd.shuffle(spots)
    for i, (p, ang, ln, wd) in enumerate(spots):
        if front != (i % 3 == 0):                               # a third in front of the frame
            continue
        shard(d, p, ang, ln, wd, rnd, ICE)
    if not front:
        glow = Image.new("RGBA", lay.size, (80, 170, 255, 0))
        glow.putalpha(lay.split()[3].filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.8)))
        glow.alpha_composite(lay)
        lay = glow
    return lay


def gold_swirl(rnd):
    """Gold ribbons wound round behind the player: rings at an angle, lit like metal."""
    lay = layer()
    x0, y0, x1, y1 = BODY
    rings = Image.new("L", (TPL_W, TPL_H), 0)
    rd = ImageDraw.Draw(rings)
    cx, cy = x1 - 30, y0 + 160
    for k, (rx, ry, wd) in enumerate(((160, 74, 40), (124, 156, 34), (92, 200, 24), (186, 126, 18), (60, 110, 14))):
        rot = Image.new("L", (TPL_W * 2, TPL_H * 2), 0)
        ImageDraw.Draw(rot).ellipse([TPL_W - rx, TPL_H - ry, TPL_W + rx, TPL_H + ry], outline=255, width=wd)
        rot = rot.rotate(-28 + k * 22, resample=Image.BICUBIC)
        rings.paste(255, (0, 0), rot.crop((TPL_W - cx, TPL_H - cy, TPL_W - cx + TPL_W, TPL_H - cy + TPL_H)))
    metal = sweep((TPL_W, TPL_H), GOLD_STOPS, repeats=2.0)
    lay.paste(metal, (0, 0), rings)
    shade = Image.new("RGBA", lay.size, (40, 26, 4, 0))        # the far side of each ring is darker
    shade.putalpha(rings.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.25)))
    lay.alpha_composite(shade)
    d = ImageDraw.Draw(lay)
    for _ in range(70):                                         # glitter
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y0 + 300)
        s = rnd.choice([1, 2, 2, 3])
        d.rectangle([x, y, x + s, y + s], fill=rnd.choice([(255, 236, 160), (255, 255, 255), (240, 200, 90)]))
    return lay


def make_gcr(seed=19):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = BODY
    path = gcr_path(BODY)
    im = layer()
    aura = layer()                                              # cold light round the card
    ImageDraw.Draw(aura).polygon(gcr_path((x0 - 18, y0 - 18, x1 + 18, y1 + 18)), fill=(60, 150, 255, 150))
    im.alpha_composite(aura.filter(ImageFilter.GaussianBlur(16)))
    im.alpha_composite(crystals(rnd, front=False))
    # ---- the card: deep blue, gold ribbons swirling behind him
    card = layer()
    cd = ImageDraw.Draw(card)
    for y in range(y0, y1 + 12):
        t = (y - y0) / float(y1 - y0)
        cd.line([(x0, y), (x1, y)], fill=mix((22, 48, 128), (6, 14, 46), t))
    beams = layer()
    bd = ImageDraw.Draw(beams)
    for k in range(5):                                          # soft light falling from the top right
        bx = x1 - 20 - k * 46
        bd.polygon([(bx, y0), (bx + 22, y0), (bx - 170, y1), (bx - 200, y1)], fill=(140, 190, 255, 16))
    card.alpha_composite(beams)
    card.alpha_composite(gold_swirl(rnd))
    plate = layer()
    pd = ImageDraw.Draw(plate)
    for y in range(316, y1 + 12):
        a = int(236 * min(1.0, ((y - 316) / 46.0) ** 1.4))
        pd.line([(x0, y), (x1, y)], fill=(6, 12, 40, a))
    card.alpha_composite(plate)
    pool = layer()
    pl = ImageDraw.Draw(pool)
    for k in range(24):                                         # under the rating, top left
        pl.ellipse([x0 - 140 + k * 6, y0 - 130 + k * 6, x0 + 220 - k * 6, y0 + 210 - k * 6], fill=(4, 10, 36, 18))
    card.alpha_composite(pool)
    card.putalpha(ImageChops.multiply(card.split()[3], mask_of(path)))
    im.alpha_composite(card)
    im.alpha_composite(gcr_frame(rnd))
    pin_corners(im)
    return im


def gcr_frame(rnd):
    """The heavy gold frame: a dark edge, a wide band of sweeping gold, a bright inner lip, gold
    wings flaring off the top corners and a little crown at the top. Plus the front crystals."""
    x0, y0, x1, y1 = BODY
    path = gcr_path(BODY)
    out = layer()
    d = ImageDraw.Draw(out)
    d.line(path + [path[0]], fill=(70, 44, 6), width=26, joint="curve")
    ring = Image.new("L", out.size, 0)
    ImageDraw.Draw(ring).line(path + [path[0]], fill=255, width=19, joint="curve")
    metal = sweep(out.size, GOLD_STOPS, repeats=1.5)
    out.paste(metal, (0, 0), ring)
    d.line(path + [path[0]], fill=(255, 248, 214), width=2, joint="curve")
    inner = gcr_path((x0 + 11, y0 + 11, x1 - 11, y1 - 11))
    d.line(inner + [inner[0]], fill=(120, 80, 14), width=3, joint="curve")
    # wings off the top corners
    wing = Image.new("L", out.size, 0)
    wd = ImageDraw.Draw(wing)
    for side in (-1, 1):
        ex = x0 if side < 0 else x1
        for k in range(3):
            wd.polygon([(ex + side * (2 - k * 6), y0 + 40 + k * 26), (ex + side * (30 - k * 4), y0 - 22 + k * 22),
                        (ex + side * (10 - k * 4), y0 + 70 + k * 26)], fill=255)
    out.paste(metal, (0, 0), wing)
    for side in (-1, 1):
        ex = x0 if side < 0 else x1
        d.line([(ex + side * 2, y0 + 40), (ex + side * 30, y0 - 22)], fill=(255, 246, 206), width=2)
    # a small crown at the top
    cx = (x0 + x1) // 2
    crown = [(cx - 26, y0 + 4), (cx - 30, y0 - 18), (cx - 14, y0 - 6), (cx, y0 - 26), (cx + 14, y0 - 6),
             (cx + 30, y0 - 18), (cx + 26, y0 + 4)]
    cm = Image.new("L", out.size, 0)
    ImageDraw.Draw(cm).polygon(crown, fill=255)
    d.polygon([(x + (x - cx) * 0.08, y + 2) for x, y in crown], fill=(70, 44, 6))
    out.paste(metal, (0, 0), cm)
    d.line(crown, fill=(255, 248, 214), width=2)
    for px in (cx - 30, cx, cx + 30):
        py = y0 - 26 if px == cx else y0 - 18
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(120, 200, 255))
    out.alpha_composite(crystals(random.Random(rnd.random()), front=True))
    # the gem at the foot (kept behind the player by the frame overlay)
    hex_gem(ImageDraw.Draw(out), cx, y1 + 2, 24, (128, 136, 156), (196, 204, 222), (255, 246, 206))
    return out


# ============================================================== RONALDO: the D card and the flag
def d_path(box):
    """Straight left edge with small corners, a big round right side - the D."""
    x0, y0, x1, y1 = box
    w = x1 - x0
    return rounded_path(box, w * 0.07, w * 0.38, w * 0.38, w * 0.07, 30)


def portugal_flag(W=600, H=400):
    """Green and red, the armillary sphere in gold, the shield on it - simplified, drawn here."""
    im = Image.new("RGBA", (W, H), (218, 20, 32, 255))
    d = ImageDraw.Draw(im)
    split = int(W * 0.40)
    d.rectangle([0, 0, split, H], fill=(0, 110, 52))
    cx, cy, r = split, H // 2, int(H * 0.30)
    gold, dark = (255, 214, 0), (150, 100, 0)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=dark, width=12)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=gold, width=8)
    for k, (rx, ry) in enumerate(((r, int(r * 0.32)), (int(r * 0.32), r))):
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=gold, width=6)
    d.line([(cx - r, cy - int(r * 0.45)), (cx + r, cy + int(r * 0.45))], fill=gold, width=10)
    sw, sh = int(r * 0.92), int(r * 1.08)                      # the shield
    shield = [(cx - sw // 2, cy - sh // 2), (cx + sw // 2, cy - sh // 2), (cx + sw // 2, cy + sh // 6),
              (cx, cy + sh // 2), (cx - sw // 2, cy + sh // 6)]
    d.polygon(shield, fill=(218, 20, 32), outline=WHITE)
    inner = [(cx + (x - cx) * 0.66, cy + (y - cy) * 0.66) for x, y in shield]
    d.polygon(inner, fill=WHITE)
    q = int(r * 0.09)
    for (qx, qy) in ((0, -1), (-1, 0), (0, 0), (1, 0), (0, 1)):  # the five blue shields
        x, y = cx + qx * q * 2.4, cy + qy * q * 2.4 - q * 0.5
        d.rectangle([x - q, y - q, x + q, y + q * 1.2], fill=(0, 52, 160))
    for k in range(7):                                         # the castles round the border, as dots
        a = math.pi * (1.1 + k * 0.13)
        d.rectangle([cx + math.cos(a) * sw * 0.42 - 4, cy + 10 + math.sin(a) * sh * 0.40 - 4,
                     cx + math.cos(a) * sw * 0.42 + 4, cy + 10 + math.sin(a) * sh * 0.40 + 4], fill=gold)
    return im


def make_dpor(seed=7):
    x0, y0, x1, y1 = BODY
    path = d_path(BODY)
    flag = portugal_flag()
    im = layer()
    back = wave(flag, TPL_W + 170, int((y1 - y0) * 1.04), 0.4, amp=0.085, folds=3.0)
    back = ImageEnhance.Color(ImageEnhance.Brightness(back).enhance(0.55)).enhance(0.8)
    cloth = Image.new("L", back.size, 0)                        # cut to the shape of cloth, not a box
    top, bot = [], []
    bw, bh = back.size
    for x in range(0, bw + 1, 4):
        t = x / float(bw)
        wv = math.sin(t * 3.0 * math.tau + 0.4) * bh * 0.085
        end = 24.0 * (abs(t - 0.5) * 2.0) ** 3
        top.append((x, 26 + wv * 0.55 + end))
        bot.append((x, bh - 26 + wv * 0.55 - end * 0.6))
    ImageDraw.Draw(cloth).polygon(top + bot[::-1], fill=255)
    back.putalpha(cloth)
    im.alpha_composite(back, (-85, y0 - 8))
    drop = layer()
    ImageDraw.Draw(drop).polygon(d_path((x0 + 6, y0 + 10, x1 + 10, y1 + 12)), fill=(4, 6, 12, 130))
    im.alpha_composite(drop)
    # ---- inside: the flag again, bigger and calmer, the sphere just behind his shoulder
    card = layer()
    big = flag.crop((int(flag.width * 0.12), 0, int(flag.width * 0.88), flag.height))
    inner = wave(big, (x1 - x0) + 40, (y1 - y0) + 20, 1.6, amp=0.04, folds=1.6)
    inner = ImageEnhance.Brightness(inner).enhance(1.02)
    card.alpha_composite(inner, (x0 - 20, y0 - 10))
    sheen = layer()                                             # a broad soft highlight, glossy card
    ImageDraw.Draw(sheen).polygon([(x0 + 120, y0), (x0 + 190, y0), (x0 + 40, y1), (x0 - 30, y1)],
                                  fill=(255, 255, 255, 26))
    card.alpha_composite(sheen.filter(ImageFilter.GaussianBlur(6)))
    plate = layer()
    pd = ImageDraw.Draw(plate)
    for y in range(312, y1 + 1):
        a = int(240 * min(1.0, ((y - 312) / 46.0) ** 1.4))
        pd.line([(x0, y), (x1, y)], fill=(8, 14, 12, a))
    card.alpha_composite(plate)
    pool = layer()
    pl = ImageDraw.Draw(pool)
    for k in range(26):
        pl.ellipse([x0 - 140 + k * 6, y0 - 130 + k * 6, x0 + 232 - k * 6, y0 + 218 - k * 6], fill=(4, 10, 8, 22))
    card.alpha_composite(pool)
    card.putalpha(ImageChops.multiply(card.split()[3], mask_of(path)))
    im.alpha_composite(card)
    im.alpha_composite(dpor_frame())
    pin_corners(im)
    return im


def dpor_frame():
    """A thin gold edge: dark line, gold sweep, bright hairline - and the gem over the foot."""
    x0, y0, x1, y1 = BODY
    path = d_path(BODY)
    out = layer()
    d = ImageDraw.Draw(out)
    d.line(path + [path[0]], fill=(60, 38, 6), width=15, joint="curve")
    ring = Image.new("L", out.size, 0)
    ImageDraw.Draw(ring).line(path + [path[0]], fill=255, width=10, joint="curve")
    out.paste(sweep(out.size, GOLD_STOPS, repeats=1.2), (0, 0), ring)
    d.line(path + [path[0]], fill=(255, 248, 214), width=2, joint="curve")
    cx = (x0 + x1) // 2
    hex_gem(d, cx, y1 - 1, 22, (122, 130, 150), (190, 198, 216), (250, 240, 200))
    return out


def frame_of(tpl, path, keep=None):
    """The template with the card's inside cut out (laid over the player); the gem stays behind."""
    x0, y0, x1, y1 = BODY
    hole = Image.new("L", tpl.size, 255)
    hd = ImageDraw.Draw(hole)
    hd.polygon(path, fill=0)
    cx = (x0 + x1) // 2
    hd.polygon([(cx + math.cos(math.pi / 6 + k * math.pi / 3) * 28, y1 + math.sin(math.pi / 6 + k * math.pi / 3) * 28)
                for k in range(6)], fill=0)
    out = tpl.copy()
    out.putalpha(ImageChops.multiply(tpl.split()[3], hole))
    if keep is not None:                                        # parts that belong in front anyway
        out.alpha_composite(keep)
    pin_corners(out)
    return out


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "sprites"
    os.makedirs(out, exist_ok=True)
    x0, y0, x1, y1 = BODY
    g = make_gcr()
    g.save(os.path.join(out, "tpl_gcr_card.png"))
    frame_of(g, gcr_path((x0 + 7, y0 + 7, x1 - 7, y1 - 7))).save(os.path.join(out, "tpl_gcrframe_card.png"))
    p = make_dpor()
    p.save(os.path.join(out, "tpl_dpor_card.png"))
    frame_of(p, d_path((x0 + 5, y0 + 5, x1 - 5, y1 - 5))).save(os.path.join(out, "tpl_dporframe_card.png"))
    print("World Cup specials written to", out)


if __name__ == "__main__":
    main()
