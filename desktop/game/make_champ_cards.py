"""The CHAMPION DRAFT A card (28 Oct, from Hubi's FC Mobile "Champions" picture).

    python3 make_champ_cards.py [out_dir]

A gold shield: the top corners stepped in, a small crown point at the top centre, the bottom
corners cut. Inside, the player's club: its colours from top to bottom, light falling from the
crown, the club's own pixel badge from this game huge and faded behind him, and a striped banner
hanging off each side in the club's two colours. A grey hex gem at the foot. No real crest, logo
or competition mark - the badge is this game's own (make_sprites.py).

  tpl_champ_<CLUB>_card.png   everything round the player for that club
  tpl_champframe_card.png     just the gold frame + crown, laid OVER the player (gem cut out)
  tpl_champmask_card.png      the card's shape
  flag_ECU|GHA|COD.png        the three nations in the draft the game had no flag for
  pack_1.png                  the pack itself: gold foil, a crown, the six clubs' badges

Same 400 x 500 canvas and BODY box as the other templates.

31 Oct (v2, from Hubi's three FC Mobile club "Champions" backs): the inside is now the club's SHIRT -
close-up knit fabric in its colour with soft diagonal creases - the club's badge (this game's own)
big and solid on it like a sewn-on patch, a white satin sheet sweeping across the lower half with a
thread of the club's colours in its folds, gold laurel branches up both lower sides of the frame,
and the two pennants hung from rods at the top corners, running the card's full height.
Style only: no real crest, logo or competition mark.
"""
import math
import os
import sys

import numpy as np

from PIL import Image, ImageChops, ImageDraw, ImageFilter

TPL_W, TPL_H = 400, 500
BODY = (66, 34, 334, 458)
GOLD = [(255, 246, 206), (232, 182, 72), (160, 108, 26), (252, 224, 140), (196, 140, 40),
        (255, 240, 190), (176, 120, 30), (255, 246, 206)]
NOTCH, CUT = 13, 18                       # top corner step, bottom corner cut (art pixels)

# club: (top colour, bottom colour, banner stripe A, banner stripe B, glow)
CLUBS = {
    "ARS": ((214, 22, 34), (78, 4, 14), (219, 12, 24), (250, 250, 252), (255, 214, 150)),
    "AST": ((140, 44, 70), (48, 12, 28), (122, 36, 58), (140, 190, 232), (210, 230, 255)),
    "BOU": ((206, 36, 30), (34, 10, 12), (214, 34, 26), (22, 22, 26), (255, 196, 150)),
    "BRE": ((222, 22, 34), (70, 6, 14), (226, 12, 24), (250, 250, 252), (255, 220, 200)),
    "CHE": ((22, 92, 178), (6, 20, 66), (6, 72, 150), (250, 250, 252), (200, 226, 255)),
    "MCI": ((96, 160, 214), (16, 30, 72), (108, 172, 222), (28, 44, 92), (226, 244, 255)),
    # 31 Oct: Club Packs 2 and 3 (pools A and B) wear this card too
    "LIV": ((200, 18, 44), (60, 4, 14), (200, 16, 46), (250, 250, 252), (255, 214, 180)),
    "NEW": ((74, 74, 82), (10, 10, 14), (24, 24, 28), (250, 250, 252), (232, 232, 244)),
    "NOT": ((210, 22, 40), (62, 6, 12), (214, 20, 38), (250, 250, 252), (255, 214, 190)),
    "MUN": ((218, 32, 40), (66, 6, 12), (218, 30, 40), (24, 24, 28), (255, 214, 130)),
    "EVE": ((24, 66, 172), (6, 14, 60), (20, 60, 170), (250, 250, 252), (206, 224, 255)),
    "FUL": ((196, 198, 208), (36, 36, 44), (240, 240, 244), (24, 24, 28), (240, 240, 250)),
    "INT": ((236, 140, 176), (72, 20, 44), (244, 160, 192), (24, 24, 28), (255, 222, 236)),
    "ALN": ((236, 196, 40), (72, 50, 6), (240, 200, 40), (20, 60, 160), (255, 240, 180)),
    "BAR": ((150, 30, 70), (14, 20, 70), (150, 30, 70), (24, 70, 170), (255, 214, 150)),
    "SUN": ((212, 30, 40), (62, 6, 12), (214, 28, 40), (250, 250, 252), (255, 214, 190)),
    "TOT": ((200, 206, 224), (14, 20, 50), (24, 34, 86), (250, 250, 252), (226, 232, 255)),
    "WES": ((128, 34, 58), (40, 8, 18), (124, 34, 56), (130, 190, 232), (255, 214, 220)),
    "WOL": ((236, 166, 30), (70, 40, 6), (240, 170, 30), (24, 24, 28), (255, 230, 170)),
    # 1 Nov: the Star Signings rated 135-142 wear this card in their club's colours
    "RMA": ((236, 236, 244), (40, 44, 84), (250, 250, 252), (214, 170, 60), (255, 244, 214)),
    "BAY": ((214, 20, 46), (64, 4, 16), (220, 18, 44), (250, 250, 252), (255, 214, 190)),
    "JUV": ((96, 96, 104), (10, 10, 14), (24, 24, 28), (250, 250, 252), (236, 236, 244)),
    "MIL": ((206, 24, 36), (16, 6, 8), (214, 24, 36), (22, 22, 26), (255, 206, 170)),
}


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def layer():
    return Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))


def pin_corners(im):
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


def shield(box, n=NOTCH, c=CUT, crown=True):
    """The outline, clockwise from the left side's top."""
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2.0
    pts = [(x0, y0 + n), (x0 + n, y0 + n), (x0 + n, y0)]
    if crown:
        pts += [(cx - 30, y0), (cx - 16, y0 - 9), (cx, y0 - 19), (cx + 16, y0 - 9), (cx + 30, y0)]
    pts += [(x1 - n, y0), (x1 - n, y0 + n), (x1, y0 + n), (x1, y1 - c), (x1 - c, y1),
            (x0 + c, y1), (x0, y1 - c)]
    return pts


def shape_mask(box=BODY):
    m = Image.new("L", (TPL_W, TPL_H), 0)
    ImageDraw.Draw(m).polygon(shield(box), fill=255)
    return m


def gem(d, cx, cy):
    d.polygon([(cx, cy - 20), (cx + 21, cy - 8), (cx + 21, cy + 12), (cx, cy + 24),
               (cx - 21, cy + 12), (cx - 21, cy - 8)], fill=(132, 140, 156), outline=(236, 242, 252))
    d.polygon([(cx, cy - 13), (cx + 13, cy - 6), (cx + 13, cy + 7), (cx, cy + 15),
               (cx - 13, cy + 7), (cx - 13, cy - 6)], fill=(186, 194, 210))
    d.polygon([(cx - 13, cy - 6), (cx, cy - 13), (cx, cy + 1)], fill=(222, 228, 240))


def frame_ring():
    x0, y0, x1, y1 = BODY
    path = shield(BODY)
    loop = path + [path[0]]
    out = layer()
    d = ImageDraw.Draw(out)
    d.line(loop, fill=(56, 36, 6), width=15, joint="curve")
    ring = Image.new("L", out.size, 0)
    ImageDraw.Draw(ring).line(loop, fill=255, width=10, joint="curve")
    cx = (x0 + x1) // 2
    ImageDraw.Draw(ring).polygon([(cx - 30, y0 + 2), (cx - 16, y0 - 9), (cx, y0 - 19), (cx + 16, y0 - 9),
                                  (cx + 30, y0 + 2)], fill=255)          # the crown point, solid gold
    out.paste(sweep(out.size, GOLD), (0, 0), ring)
    d.line(loop, fill=(255, 248, 214), width=2, joint="curve")
    d.polygon([(cx, y0 - 12), (cx + 6, y0 - 5), (cx, y0 + 2), (cx - 6, y0 - 5)], fill=(150, 20, 30),
              outline=(255, 236, 170))                                      # a red stone in the crown
    inner = shield((x0 + 9, y0 + 9, x1 - 9, y1 - 9), NOTCH, CUT - 3, crown=False)
    d.line(inner + [inner[0]], fill=(120, 80, 14, 210), width=2, joint="curve")
    for sx in (x0 + NOTCH, x1 - NOTCH):                                     # studs on the stepped corners
        d.ellipse([sx - 4, y0 + NOTCH - 4, sx + 4, y0 + NOTCH + 4], fill=(255, 236, 160), outline=(90, 60, 10))
    out.alpha_composite(laurels())                                          # v2: gold laurels up the lower sides
    return out


PEN_PAD = 8                     # the strip the game waves: one pennant + its rod, cropped this much out


def pen_box(side):
    """(left, top, right, bottom) of one pennant's strip on the template canvas."""
    x0, y0, x1, y1 = BODY
    bx0 = x0 - 40 if side < 0 else x1 + 4
    return (bx0 - PEN_PAD, y0 + 16 - PEN_PAD, bx0 + 36 + PEN_PAD, y1 - 40 + 2)


def pennant_strip(club):
    """One pennant, flat (no folds - the game waves it and shades the folds as they move)."""
    full = banner(club, sides=(-1,), shade=False)
    return full.crop(pen_box(-1))


def banner(club, sides=(-1, 1), shade=True):
    """A striped pennant hanging off each side, behind the card, swallow-tailed at the foot."""
    _top, _bot, a, b, _g = CLUBS[club]
    x0, y0, x1, y1 = BODY
    im = layer()
    for side in sides:
        edge = x0 if side < 0 else x1
        bx0 = edge - 40 if side < 0 else edge + 4
        bx1 = bx0 + 36
        top, bot = y0 + 16, y1 - 40                                         # v2: from the top corners
        strip = layer()
        sd = ImageDraw.Draw(strip)
        for i in range(3):                                                  # vertical stripes
            sx = bx0 + i * (bx1 - bx0) / 3.0
            sd.rectangle([sx, top, sx + (bx1 - bx0) / 3.0 + 1, bot], fill=a if i % 2 == 0 else b)
        m = Image.new("L", im.size, 0)
        mid = (bx0 + bx1) / 2.0
        ImageDraw.Draw(m).polygon([(bx0, top), (bx1, top), (bx1, bot), (mid, bot - 24), (bx0, bot)], fill=255)
        strip.putalpha(m)
        shade_l = layer()                                                   # folds in the cloth
        shd = ImageDraw.Draw(shade_l)
        for y in range(top, bot):
            k = 0.5 + 0.5 * math.sin((y - top) * 0.05)
            shd.line([(bx0, y), (bx1, y)], fill=(0, 0, 0, int(70 * k)))
            if k > 0.86:                                                    # satin sheen on the folds
                shd.line([(bx0 + 4, y), (bx1 - 4, y)], fill=(255, 255, 255, int(120 * (k - 0.86) / 0.14)))
        shade_l.putalpha(ImageChops.multiply(shade_l.split()[3], m))
        im.alpha_composite(strip)
        if shade:
            im.alpha_composite(shade_l)
        d = ImageDraw.Draw(im)
        d.line([(bx0, top), (bx1, top), (bx1, bot), (mid, bot - 24), (bx0, bot), (bx0, top)],
               fill=(40, 26, 6), width=3)
        d.rectangle([bx0 - 4, top - 6, bx1 + 4, top + 2], fill=(214, 164, 54), outline=(80, 52, 8))   # the rod
        for k in (bx0 - 4, bx1 + 4):
            d.ellipse([k - 4, top - 6, k + 4, top + 2], fill=(255, 232, 160), outline=(80, 52, 8))
    return im


def ghost_badge(club, sprites):
    path = os.path.join(sprites, "%s_badge.png" % club)
    if not os.path.exists(path):
        return None
    b = Image.open(path).convert("RGBA")
    k = 3
    b = b.resize((b.width * k, b.height * k), Image.NEAREST)
    a = b.split()[3].point(lambda v: int(v * 0.12))
    b.putalpha(a)
    return b


def _ramp(t, stops):
    t = np.clip(t, 0.0, 1.0) * (len(stops) - 1)
    i = np.minimum(t.astype(int), len(stops) - 2)
    f = (t - i)[..., None]
    S = np.array(stops, float)
    return S[i] * (1 - f) + S[i + 1] * f


def fabric(club):
    """The club's shirt up close: soft diagonal creases in a few flat bands, and the knit's dots."""
    top, bot, a, _b, _g = CLUBS[club]
    yy, xx = np.mgrid[0:TPL_H, 0:TPL_W].astype(float)
    u = (xx * 0.80 + yy * 0.60)                                             # across the creases
    v = (-xx * 0.60 + yy * 0.80)
    fold = (0.55 * np.sin(u / 34.0 + 0.6 * np.sin(v / 70.0)) + 0.30 * np.sin(u / 13.0 + 1.3)
            + 0.15 * np.sin(v / 21.0))
    fold = fold * 0.5 + 0.5 - 0.35 * (yy - BODY[1]) / float(BODY[3] - BODY[1])   # darker going down
    fold = np.round(np.clip(fold, 0, 1) * 5) / 5.0                         # pixel-art bands
    light = mix(top, (255, 255, 255), 0.22)
    stops = [mix(bot, (0, 0, 0), 0.25), bot, mix(top, bot, 0.45), top, light]
    rgb = _ramp(fold, stops)
    knit = (((xx.astype(int) // 3) + (yy.astype(int) // 3)) % 2 == 0) & ((yy.astype(int) % 3) == 0)
    rgb[knit] *= 0.90                                                       # the mesh
    sparkle = ((xx.astype(int) * 7 + yy.astype(int) * 13) % 97 == 0) & (fold > 0.55)
    rgb[sparkle] = rgb[sparkle] * 0.4 + 255 * 0.6                           # a few glints in the weave
    out = np.dstack([np.clip(rgb, 0, 255), np.full((TPL_H, TPL_W), 255.0)]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def patch_badge(club, sprites, k=1.5):
    """The club's badge woven into the shirt, tone on tone: its light parts in the fabric's light
    colour, its dark parts in the dark, with a raised edge - it sits behind the player's head, so it
    has to read as part of the cloth, not as a second picture."""
    path = os.path.join(sprites, "%s_badge.png" % club)
    if not os.path.exists(path):
        return None
    top, bot, _a, _b, _g = CLUBS[club]
    b = Image.open(path).convert("RGBA")
    b = b.resize((int(b.width * k), int(b.height * k)), Image.NEAREST)
    arr = np.asarray(b).astype(float)
    lum = (0.3 * arr[..., 0] + 0.59 * arr[..., 1] + 0.11 * arr[..., 2]) / 255.0
    lum = np.round(lum * 3) / 3.0
    rgb = _ramp(lum, [mix(bot, (0, 0, 0), 0.2), mix(top, bot, 0.5), top, mix(top, (255, 255, 255), 0.35)])
    a = arr[..., 3] * 0.62
    face = Image.fromarray(np.dstack([rgb, a]).astype(np.uint8), "RGBA")
    out = Image.new("RGBA", (b.width + 8, b.height + 8), (0, 0, 0, 0))
    rim = Image.new("RGBA", b.size, mix(top, (255, 255, 255), 0.5) + (0,))
    rim.putalpha(b.split()[3].point(lambda v: int(v * 0.35)))
    shade = Image.new("RGBA", b.size, (0, 0, 0, 0))
    shade.putalpha(b.split()[3].point(lambda v: int(v * 0.35)))
    out.alpha_composite(rim, (3, 3))                                        # raised: lit above-left...
    out.alpha_composite(shade, (6, 6))                                      # ...shadowed below-right
    out.alpha_composite(face, (4, 4))
    return out


def satin(club):
    """A white silk sheet thrown across the lower half: it rises toward the card's right, its folds
    run along it in long sweeps, and a thread of the club's colours catches in one of them."""
    _top, bot, a, b, _g = CLUBS[club]
    yy, xx = np.mgrid[0:TPL_H, 0:TPL_W].astype(float)
    x0 = BODY[0]
    edge = 318 - 0.42 * (xx - x0) + 10 * np.sin(xx / 30.0 + 0.5)            # top edge: rising to the right
    inside = yy > edge
    d = yy - edge                                                           # depth into the cloth
    flow = d + 0.22 * (xx - x0)                                             # bands run along the sheet
    fold = 0.5 + 0.5 * np.sin(flow / 11.0 + 1.6 * np.sin(xx / 55.0))
    fold = np.clip(0.8 * fold + 0.35 * np.clip(1 - d / 40.0, 0, 1) - 0.25 * np.clip((d - 90) / 60.0, 0, 1), 0, 1)
    fold = np.round(fold * 4) / 4.0
    rgb = _ramp(fold, [(140, 146, 168), (190, 196, 214), (224, 228, 238), (244, 246, 251), (255, 255, 255)])
    alpha = np.where(inside, 255.0, 0.0)
    phase = flow / 11.0 + 1.6 * np.sin(xx / 55.0)
    other = b if b != (250, 250, 252) else bot
    for centre, width, col in ((5.5 * math.pi, 0.16, a), (5.5 * math.pi + 0.42, 0.10, other)):
        m = inside & (np.abs(phase - centre) < width) & (d > 6)
        rgb[m] = col                                                        # the club thread in a fold
    out = np.dstack([np.clip(rgb, 0, 255), alpha]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def laurels():
    """Gold laurel branches climbing both lower sides of the frame."""
    x0, y0, x1, y1 = BODY
    im = layer()
    d = ImageDraw.Draw(im)
    for side in (-1, 1):
        ex = x0 + 6 if side < 0 else x1 - 6
        stem = []
        for i in range(15):                                                 # an arc from the foot up the side
            t = i / 14.0
            ang = math.radians(-60 + 120 * t)
            sx = ex - side * (34 * math.cos(ang) - 34 * math.cos(math.radians(-60)))
            sy = y1 - 6 - 190 * t
            stem.append((sx, sy))
        d.line(stem, fill=(96, 62, 10), width=5)
        d.line(stem, fill=(214, 160, 48), width=2)
        for i in range(1, 14):
            px, py = stem[i]
            nx, ny = stem[i - 1]
            dx, dy = px - nx, py - ny
            n = math.hypot(dx, dy) or 1.0
            dx, dy = dx / n, dy / n
            for leaf in (-1, 1):                                            # a pair of leaves at each node
                ox, oy = -dy * leaf, dx * leaf
                lx = px + ox * 9 + dx * 6
                ly = py + oy * 9 + dy * 6
                L, W = 15 - i * 0.45, 5.5 - i * 0.12
                pts = []
                for k in range(12):
                    a = k / 11.0 * math.pi * 2
                    u, w = math.cos(a) * L / 2, math.sin(a) * W / 2
                    ax, ay = ox * 0.75 + dx * 0.65, oy * 0.75 + dy * 0.65
                    an = math.hypot(ax, ay) or 1.0
                    ax, ay = ax / an, ay / an
                    pts.append((lx + ax * u - ay * w, ly + ay * u + ax * w))
                bright = GOLD[3] if leaf * side < 0 else GOLD[1]
                d.polygon(pts, fill=bright, outline=(88, 56, 8))
                d.line([pts[0], pts[6]], fill=GOLD[0], width=1)
    return im


def top_layer(club, sprites, banners=True):
    return top_layer_v2(club, sprites, banners)


def top_layer_v2(club, sprites, banners=True):
    top, bot, _a, _b, glow = CLUBS[club]
    x0, y0, x1, y1 = BODY
    cx = (x0 + x1) // 2
    inside = shape_mask()
    im = layer()
    drop = layer()
    ImageDraw.Draw(drop).polygon(shield((x0 + 6, y0 + 10, x1 + 10, y1 + 12)), fill=(2, 4, 12, 130))
    drop.putalpha(ImageChops.multiply(drop.split()[3], ImageChops.invert(inside)))
    if banners:
        im.alpha_composite(banner(club))
    im.alpha_composite(drop)
    card = fabric(club)
    pb = patch_badge(club, sprites)
    if pb is not None:                                                      # the badge, sewn on, up top
        card.alpha_composite(pb, (cx - pb.width // 2, y0 + 14))
    halo = layer()
    hd = ImageDraw.Draw(halo)
    for k in range(18):                                                     # light from the crown
        r = 170 - k * 8
        hd.ellipse([cx - r, y0 - 40 - r * 0.6, cx + r, y0 - 40 + r * 0.9], fill=glow + (6,))
    card.alpha_composite(halo)
    card.alpha_composite(satin(club))
    plate = layer()                                                         # the name sits on this
    pd = ImageDraw.Draw(plate)
    for y in range(338, y1 + 1):
        a = int(240 * min(1.0, ((y - 338) / 44.0) ** 1.3))
        pd.line([(x0, y), (x1, y)], fill=mix(bot, (4, 6, 14), 0.72) + (a,))
    card.alpha_composite(plate)
    pool = layer()
    pl = ImageDraw.Draw(pool)
    for k in range(26):                                                     # dark pool under the rating
        pl.ellipse([x0 - 140 + k * 6, y0 - 130 + k * 6, x0 + 232 - k * 6, y0 + 218 - k * 6], fill=(3, 6, 18, 14))
    card.alpha_composite(pool)
    card.putalpha(ImageChops.multiply(card.split()[3], inside))
    im.alpha_composite(card)
    im.alpha_composite(frame_ring())
    gem(ImageDraw.Draw(im), cx, y1 - 2)
    pin_corners(im)
    return im


def top_layer_v1(club, sprites):
    top, bot, _a, _b, glow = CLUBS[club]
    x0, y0, x1, y1 = BODY
    cx = (x0 + x1) // 2
    inside = shape_mask()
    im = layer()
    drop = layer()                                                          # shadow it throws
    ImageDraw.Draw(drop).polygon(shield((x0 + 6, y0 + 10, x1 + 10, y1 + 12)), fill=(2, 4, 12, 130))
    drop.putalpha(ImageChops.multiply(drop.split()[3], ImageChops.invert(inside)))
    im.alpha_composite(banner(club))
    im.alpha_composite(drop)
    card = layer()
    cd = ImageDraw.Draw(card)
    for y in range(y0 - 20, y1 + 1):                                        # club colours, top to bottom
        t = max(0.0, (y - y0) / float(y1 - y0))
        cd.line([(x0, y), (x1, y)], fill=mix(top, bot, t ** 0.9) + (255,))
    rays = layer()                                                          # light falling from the crown
    rd = ImageDraw.Draw(rays)
    for k in range(-5, 6):
        ang = math.pi / 2 + k * 0.17
        ex, ey = cx + math.cos(ang) * 520, y0 + math.sin(ang) * 520
        w = 0.035
        rd.polygon([(cx, y0 - 10), (cx + math.cos(ang - w) * 520, y0 + math.sin(ang - w) * 520),
                    (cx + math.cos(ang + w) * 520, y0 + math.sin(ang + w) * 520)],
                   fill=glow + (22 if k % 2 else 14,))
    card.alpha_composite(rays)
    halo = layer()
    hd = ImageDraw.Draw(halo)
    for k in range(22):                                                     # a soft glow behind his head
        r = 150 - k * 6
        hd.ellipse([cx - r, y0 + 120 - r * 0.8, cx + r, y0 + 120 + r * 0.8], fill=glow + (7,))
    card.alpha_composite(halo)
    gb = ghost_badge(club, sprites)
    if gb is not None:                                                      # the club's badge, huge and faded
        card.alpha_composite(gb, (cx - gb.width // 2, y0 - 20))
    hatch = layer()                                                         # fine diagonal weave
    hh = ImageDraw.Draw(hatch)
    for k in range(-TPL_H, TPL_W, 8):
        hh.line([(k, 0), (k + TPL_H, TPL_H)], fill=(255, 255, 255, 9), width=1)
    card.alpha_composite(hatch)
    plate = layer()                                                         # the name sits on this
    pd = ImageDraw.Draw(plate)
    for y in range(300, y1 + 1):
        a = int(236 * min(1.0, ((y - 300) / 60.0) ** 1.4))
        pd.line([(x0, y), (x1, y)], fill=mix(bot, (4, 6, 14), 0.7) + (a,))
    card.alpha_composite(plate)
    pool = layer()
    pl = ImageDraw.Draw(pool)
    for k in range(26):                                                     # dark pool under the rating
        pl.ellipse([x0 - 140 + k * 6, y0 - 130 + k * 6, x0 + 232 - k * 6, y0 + 218 - k * 6], fill=(3, 6, 18, 16))
    card.alpha_composite(pool)
    card.putalpha(ImageChops.multiply(card.split()[3], inside))
    im.alpha_composite(card)
    im.alpha_composite(frame_ring())
    gem(ImageDraw.Draw(im), cx, y1 - 2)
    pin_corners(im)
    return im


def frame_overlay():
    x0, y0, x1, y1 = BODY
    out = frame_ring()
    hole = Image.new("L", out.size, 255)
    cx = (x0 + x1) // 2
    ImageDraw.Draw(hole).polygon([(cx + math.cos(math.pi / 6 + k * math.pi / 3) * 27,
                                   y1 - 2 + math.sin(math.pi / 6 + k * math.pi / 3) * 27) for k in range(6)], fill=0)
    out.putalpha(ImageChops.multiply(out.split()[3], hole))
    pin_corners(out)
    return out


def make_flags():
    """Simplified flags, the way make_limitbreakers.py draws its extra ones (240 x 160, pixelated)."""
    from make_limitbreakers import _flag_canvas, _star, pixelate
    out = {}
    im, d = _flag_canvas()                                       # Ecuador: yellow over blue over red
    d.rectangle([0, 0, 240, 80], fill=(255, 209, 0))
    d.rectangle([0, 80, 240, 120], fill=(3, 78, 162))
    d.rectangle([0, 120, 240, 160], fill=(237, 28, 36))
    d.ellipse([100, 54, 140, 104], fill=(120, 170, 220), outline=(150, 100, 30), width=4)   # a plain oval
    out["ECU"] = im
    im, d = _flag_canvas()                                       # Ghana: red, gold, green, black star
    for k, c in enumerate(((206, 17, 38), (252, 209, 22), (0, 107, 63))):
        d.rectangle([0, k * 160 / 3, 240, (k + 1) * 160 / 3], fill=c)
    d.polygon(_star(120, 82, 26, 11), fill=(20, 20, 24))
    out["GHA"] = im
    im, d = _flag_canvas(bg=(0, 127, 255))                       # DR Congo: sky blue, red band, star
    d.polygon([(0, 160), (0, 128), (200, 0), (240, 0), (240, 32), (40, 160)], fill=(247, 216, 23))
    d.polygon([(0, 160), (0, 140), (214, 0), (240, 0), (240, 20), (26, 160)], fill=(206, 16, 33))
    d.polygon(_star(46, 40, 26, 11), fill=(247, 216, 23))
    out["COD"] = im
    # 31 Oct, for Club Packs 2 + 3 (the players' own countries)
    im, d = _flag_canvas(bg=(255, 255, 255))                     # Mexico: green, white, red, an emblem
    d.rectangle([0, 0, 80, 160], fill=(0, 104, 71))
    d.rectangle([160, 0, 240, 160], fill=(206, 17, 38))
    d.ellipse([102, 58, 138, 98], fill=(140, 96, 40))
    out["MEX"] = im
    im, d = _flag_canvas()                                       # Hungary: red, white, green
    for k, c in enumerate(((206, 41, 57), (255, 255, 255), (71, 112, 80))):
        d.rectangle([0, k * 160 / 3, 240, (k + 1) * 160 / 3], fill=c)
    out["HUN"] = im
    im, d = _flag_canvas(bg=(255, 255, 255))                     # Algeria: green and white, red crescent + star
    d.rectangle([0, 0, 120, 160], fill=(0, 98, 51))
    outer = [(118 + 38 * math.cos(math.radians(t)), 80 + 38 * math.sin(math.radians(t))) for t in range(45, 316, 5)]
    inner = [(130 + 31 * math.cos(math.radians(t)), 80 + 31 * math.sin(math.radians(t))) for t in range(305, 54, -5)]
    d.polygon(outer + inner, fill=(210, 16, 52))
    d.polygon(_star(146, 80, 17, 7), fill=(210, 16, 52))
    out["ALG"] = im
    im, d = _flag_canvas()                                       # Guinea-Bissau: red bar + black star, yellow over green
    d.rectangle([0, 0, 240, 80], fill=(252, 209, 22))
    d.rectangle([0, 80, 240, 160], fill=(0, 158, 73))
    d.rectangle([0, 0, 80, 160], fill=(206, 17, 38))
    d.polygon(_star(40, 80, 24, 10), fill=(20, 20, 24))
    out["GNB"] = im
    return {code: pixelate(f, 3) for code, f in out.items()}


# 31 Oct, Hubi: "all club packs are champions packs labelled A, B and C" - Club Packs 2 and 3
# became Champion Drafts B and C: the same pack, a different tint of foil, their own six clubs.
# (31 Oct, later: Al Nassr moved to Draft B for balance - its badge leads B's pack, the
# headliners' clubs first on each.)
DRAFTS = {"A": ((22, 24, 58), ("ARS", "AST", "BOU", "BRE", "CHE", "MCI")),
          "B": ((12, 34, 74), ("ALN", "LIV", "MCI", "MUN", "NEW", "NOT")),
          "C": ((42, 18, 64), ("INT", "BAR", "TOT", "WES", "WOL", "SUN"))}


def make_pack(out, letter="A"):
    """A Champion Draft's art: dark foil with a gold rim, a crown, the six clubs in the draft."""
    from make_art import pixelate, shade, text_img
    W, H = 300, 420
    body, clubs = DRAFTS[letter]
    accent = (246, 206, 100)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([10, 24, W - 10, H - 24], 18, fill=body)
    for x in range(10, W - 10, 12):                               # crimped foil edges
        d.polygon([(x, 26), (x + 6, 8), (x + 12, 26)], fill=shade(accent, 0.8))
        d.polygon([(x, H - 26), (x + 6, H - 8), (x + 12, H - 26)], fill=shade(accent, 0.8))
    d.rectangle([10, 24, W - 10, 40], fill=shade(accent, 0.9))
    d.rectangle([10, H - 40, W - 10, H - 24], fill=shade(accent, 0.9))
    rays = layer().crop((0, 0, W, H))
    rd = ImageDraw.Draw(rays)
    for k in range(-6, 7):                                        # light from the crown
        a = math.pi / 2 + k * 0.2
        rd.polygon([(W / 2, 70), (W / 2 + math.cos(a - 0.04) * 500, 70 + math.sin(a - 0.04) * 500),
                    (W / 2 + math.cos(a + 0.04) * 500, 70 + math.sin(a + 0.04) * 500)], fill=accent + (26,))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle([16, 44, W - 16, H - 44], 14, fill=255)
    rays.putalpha(ImageChops.multiply(rays.split()[3], m))
    im.alpha_composite(rays)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([10, 24, W - 10, H - 24], 18, outline=accent, width=6)
    cx = W // 2                                                    # the crown
    d.polygon([(cx - 46, 96), (cx - 46, 58), (cx - 24, 78), (cx, 48), (cx + 24, 78), (cx + 46, 58), (cx + 46, 96)],
              fill=accent, outline=(120, 80, 14))
    d.rectangle([cx - 46, 90, cx + 46, 100], fill=shade(accent, 0.8))
    for x, y in ((cx - 46, 56), (cx, 46), (cx + 46, 56)):
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(255, 240, 190), outline=(120, 80, 14))
    d.ellipse([cx - 7, 76, cx + 7, 88], fill=(170, 24, 36))
    for j, code in enumerate(clubs):
        p = os.path.join(out, "%s_badge.png" % code)
        if os.path.exists(p):
            b = Image.open(p).convert("RGBA").resize((60, 72), Image.NEAREST)   # exactly half: letters stay whole
            im.alpha_composite(b, (51 + (j % 3) * 66, 120 - 9 * (j // 3 == 0) + (j // 3) * 76))
    d.rectangle([22, 282, W - 22, 362], fill=shade(body, 0.6))
    d.line([(22, 282), (W - 22, 282)], fill=accent, width=3)
    d.line([(22, 362), (W - 22, 362)], fill=accent, width=3)
    for line, y, size in (("CHAMPION", 306, 34), ("DRAFT " + letter, 340, 30)):
        t = text_img(line, size, accent)
        im.alpha_composite(t, ((W - t.width) // 2, y - t.height // 2))
    return pixelate(im, 3)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "sprites"
    os.makedirs(out, exist_ok=True)
    for club in CLUBS:
        top_layer(club, out).save(os.path.join(out, "tpl_champ_%s_card.png" % club))
        # 31 Oct, moving cards: the same card without its pennants (the game waves them under it)
        top_layer(club, out, banners=False).save(os.path.join(out, "tpl_champtop_%s_card.png" % club))
        pennant_strip(club).save(os.path.join(out, "champpen_%s.png" % club))
    frame_overlay().save(os.path.join(out, "tpl_champframe_card.png"))
    m = Image.new("RGBA", (TPL_W, TPL_H), (255, 255, 255, 0))
    m.putalpha(shape_mask())
    pin_corners(m)
    m.save(os.path.join(out, "tpl_champmask_card.png"))
    for i, letter in ((1, "A"), (2, "B"), (3, "C")):
        make_pack(out, letter).save(os.path.join(out, "pack_%d.png" % i))
    for code, flag in make_flags().items():
        flag.save(os.path.join(out, "flag_%s.png" % code))
    print("Champion Draft A card layers written to", out)


if __name__ == "__main__":
    main()
