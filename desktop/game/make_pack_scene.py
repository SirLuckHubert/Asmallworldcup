"""The walkout's pictures (31 Oct): a gold globe, the close-up over its surface, the light burst
behind it, and the stadium the card walks out into. All this game's own - the globe's continents
are a hand-made 5-degree map, the stadium and its lettering are drawn here. Nothing from EA.

    python3 make_pack_scene.py [sprites dir]

Writes:
  pk_globe.png        36 turns of the globe, 152 px each, in one row (shown x2 and up)
  pk_close.png        24 frames of the close-up over its surface, 480 x 270 each, stacked
  pk_burst_<T>.png    the light burst behind the globe, 640 x 360 (shown x3), per theme
  pk_stadium_<T>.png  the stadium, 640 x 360 (shown x3), per theme
Themes: A purple (pool A), B blue (pool B), L crimson (Limit Breakers), C slate (pool C)."""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites")
FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"

# (centre of the burst, its middle, its edge, accent)
THEMES = {"A": ((255, 196, 255), (150, 62, 255), (84, 18, 226), (60, 255, 150)),
          "B": ((206, 232, 255), (60, 120, 255), (18, 40, 176), (255, 214, 90)),
          "L": ((255, 206, 196), (222, 40, 64), (108, 6, 26), (255, 164, 44)),
          "C": ((214, 222, 240), (92, 106, 140), (34, 40, 60), (190, 204, 230))}

# ---------------------------------------------------------------- the map (5 degrees a cell)
# row r is latitude 87.5 - 5r; column c is longitude -177.5 + 5c. Land as (first, last) columns.
LAND = {
    1: [(13, 21), (26, 31)],
    2: [(10, 22), (25, 32), (39, 39), (55, 60)],
    3: [(4, 8), (9, 22), (24, 32), (39, 41), (44, 68)],
    4: [(2, 24), (25, 30), (32, 32), (37, 41), (42, 71)],
    5: [(3, 16), (20, 23), (27, 29), (37, 41), (42, 71)],
    6: [(8, 16), (20, 24), (35, 35), (37, 41), (42, 68)],
    7: [(10, 24), (35, 35), (36, 44), (44, 62), (66, 67)],
    8: [(11, 23), (35, 45), (45, 63), (64, 65)],
    9: [(11, 22), (34, 36), (38, 39), (39, 41), (43, 61), (64, 64)],
    10: [(12, 21), (34, 35), (36, 38), (41, 48), (48, 60), (61, 61), (63, 64)],
    11: [(12, 20), (33, 42), (42, 47), (47, 60)],
    12: [(13, 17), (19, 19), (32, 43), (43, 47), (47, 50), (50, 60)],
    13: [(14, 17), (19, 20), (32, 42), (43, 47), (49, 58)],
    14: [(15, 18), (32, 42), (44, 46), (50, 52), (54, 57), (60, 60)],
    15: [(17, 19), (33, 45), (51, 51), (55, 57), (60, 60)],
    16: [(19, 19), (20, 24), (33, 45), (52, 52), (56, 57), (61, 61)],
    17: [(20, 26), (35, 44), (55, 56), (58, 59)],
    18: [(20, 28), (38, 44), (56, 56), (58, 59), (60, 60), (63, 65)],
    19: [(21, 29), (38, 44), (57, 59), (63, 66)],
    20: [(21, 28), (38, 44), (45, 45), (62, 63), (65, 65)],
    21: [(22, 28), (38, 43), (45, 45), (60, 65)],
    22: [(22, 27), (38, 43), (45, 45), (59, 66)],
    23: [(22, 26), (39, 42), (59, 66)],
    24: [(22, 25), (39, 41), (59, 61), (63, 66)],
    25: [(22, 24), (64, 65), (70, 70)],
    26: [(22, 24), (65, 65), (70, 71)],
    27: [(22, 23)],
    28: [(22, 23)],
    31: [(0, 8), (12, 24), (40, 71)],
    32: [(0, 71)], 33: [(0, 71)], 34: [(0, 71)], 35: [(0, 71)],
}


def land_mask():
    """The 72 x 36 map, smoothed up to 720 x 360 and cut back to land / sea, with a little
    noise on the coasts so they aren't 5-degree blocks."""
    m = np.zeros((36, 72), np.float32)
    for r, spans in LAND.items():
        for a, b in spans:
            m[r, a:b + 1] = 1.0
    img = Image.fromarray((m * 255).astype(np.uint8)).resize((720, 360), Image.BICUBIC)
    img = img.filter(ImageFilter.GaussianBlur(3))
    a = np.asarray(img).astype(np.float32) / 255.0
    rng = np.random.default_rng(7)
    noise = Image.fromarray((rng.random((90, 180)) * 255).astype(np.uint8)).resize((720, 360), Image.BICUBIC)
    a = a + (np.asarray(noise).astype(np.float32) / 255.0 - 0.5) * 0.35
    return a > 0.5


GOLD = np.array([(34, 20, 6), (96, 60, 16), (170, 120, 40), (222, 176, 82), (250, 222, 140), (255, 248, 210)],
                np.float32)


def gold(t):
    t = np.clip(t, 0, 1) * (len(GOLD) - 1)
    i = np.clip(t.astype(int), 0, len(GOLD) - 2)
    f = (t - i)[..., None]
    return GOLD[i] * (1 - f) + GOLD[i + 1] * f


def sphere(W, H, cx, cy, R, lon0, mask, tilt=0.32, rim=(255, 170, 255), light=(-0.45, 0.58, 0.68), gloss=22):
    """Shade a gold globe into a W x H RGBA picture. Light from the top left."""
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = (xs + 0.5 - cx) / R
    ny = -(ys + 0.5 - cy) / R                      # up
    rr = nx * nx + ny * ny
    inside = rr < 1.0
    nz = np.sqrt(np.clip(1.0 - rr, 0, 1))
    # tilt the globe towards us so the north is a little visible
    wy = ny * math.cos(tilt) + nz * math.sin(tilt)
    wz = -ny * math.sin(tilt) + nz * math.cos(tilt)
    lat = np.degrees(np.arcsin(np.clip(wy, -1, 1)))
    lon = np.degrees(np.arctan2(nx, wz)) + lon0
    mi = np.clip(((90 - lat) / 180.0 * 360).astype(int), 0, 359)
    mj = (((lon + 180) % 360) / 360.0 * 720).astype(int) % 720
    land = mask[mi, mj] & inside
    # coasts: land next to sea, in picture space
    sea = inside & ~land
    # raised continents: the coast facing the light catches it, the far side is a dark crevice
    lit = land & (np.roll(sea, 1, 0) | np.roll(sea, 1, 1))           # sea above / left of it
    shadow = land & (np.roll(sea, -1, 0) | np.roll(sea, -1, 1))      # sea below / right of it
    crev = sea & (np.roll(land, 1, 0) | np.roll(land, 1, 1))         # the sea just past the far coast
    L = np.array(light, np.float64)
    L = L / np.linalg.norm(L)
    diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    # reflection of the view straight back: specular
    rz = 2 * diff * nz - L[2]
    spec = np.clip(rz, 0, 1) ** gloss
    t = 0.04 + 0.86 * diff ** 1.35
    t = np.where(land, t * 1.02 + 0.05, t * 0.90)                   # the sea a smoother, deeper gold
    rng = np.random.default_rng(3)
    t = t + np.where(land, (rng.random(t.shape) - 0.5) * 0.08, 0)    # land is brushed
    col = gold(t)
    col = col + (spec * np.where(land, 60, 170))[..., None]
    col = np.where(lit[..., None], col * 1.25 + 26, col)
    col = np.where(shadow[..., None], col * 0.50, col)
    col = np.where(crev[..., None], col * 0.62, col)
    fres = np.clip(1 - nz, 0, 1) ** 3
    col = col * (1 - fres[..., None] * 0.45) + np.array(rim, np.float32) * (fres[..., None] * 0.45)
    bounce = np.clip(-ny, 0, 1) ** 2 * np.clip(1 - nz, 0, 1) * 60
    col = col + np.stack([bounce, bounce * 0.6, bounce * 0.2], -1)
    col = np.clip(col, 0, 255)
    # anti-aliased rim
    a = np.clip((1.0 - np.sqrt(rr)) * R + 0.5, 0, 1)
    out = np.dstack([col, a * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def make_globe(mask):
    D, P, N = 148, 2, 36
    sheet = Image.new("RGBA", ((D + 2 * P) * N, D + 2 * P), (0, 0, 0, 0))
    for f in range(N):
        g = sphere(D + 2 * P, D + 2 * P, (D + 2 * P) / 2.0, (D + 2 * P) / 2.0, D / 2.0, -f * 10.0, mask)
        sheet.paste(g, (f * (D + 2 * P), 0))
    sheet.save(os.path.join(OUT, "pk_globe.png"))


def make_close(mask):
    """Skimming low over the globe: its top curve across the picture, sky above."""
    W, H, N, R = 480, 270, 24, 1150.0
    sheet = Image.new("RGBA", (W, H * N), (0, 0, 0, 0))
    for f in range(N):
        g = sphere(W, H, W * 0.5, 80 + R, R, 40.0 - f * 1.1, mask, tilt=0.95,
                   light=(-0.62, 0.70, 0.36), gloss=8)
        # so close the surface is almost flat, so light alone gives no drama: a reflected light
        # band sweeps across it and the far side falls into shade
        a = np.asarray(g).astype(np.float32)
        ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
        band = np.exp(-((xs * 0.8 + ys * 0.9 - (330 - f * 7)) / 46.0) ** 2)
        k = 0.42 + 0.38 * (1 - xs / W) * (1 - ys / (H * 1.6)) + 0.75 * band
        a[..., :3] = np.clip(a[..., :3] * k[..., None] + band[..., None] * 30, 0, 255)
        sheet.paste(Image.fromarray(a.astype(np.uint8), "RGBA"), (0, f * H))
    sheet.save(os.path.join(OUT, "pk_close.png"))


def radial(W, H, cx, cy, stops, scale):
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xs - cx) / scale) ** 2 + ((ys - cy) / (scale * 0.8)) ** 2)
    d = np.clip(d, 0, 1) * (len(stops) - 1)
    i = np.clip(d.astype(int), 0, len(stops) - 2)
    f = (d - i)[..., None]
    s = np.array(stops, np.float32)
    return s[i] * (1 - f) + s[i + 1] * f


def halftone(img, box, col, step=6, grow=(1, 0)):
    """Dots getting bigger one way, like print."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    for y in range(y0, y1, step):
        for x in range(x0, x1, step):
            k = ((x - x0) / float(x1 - x0)) if grow[0] else ((y - y0) / float(y1 - y0))
            if grow[0] < 0 or grow[1] < 0:
                k = 1 - k
            mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
            ex = 1.0 - math.hypot((x - mx) / ((x1 - x0) / 2.0), (y - my) / ((y1 - y0) / 2.0))
            r = 2.4 * k * min(1.0, max(0.0, ex) * 2.0)      # a round patch, fading out at its edge
            if r > 0.5:
                d.ellipse((x - r, y - r, x + r, y + r), fill=col)


def make_burst(code):
    c, m, e, acc = THEMES[code]
    W, H = 640, 360
    a = radial(W, H, 320, 170, [c, m, m, e], 420.0)
    img = Image.fromarray(a.astype(np.uint8), "RGB").convert("RGBA")
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    rng = np.random.default_rng(11)
    for k in range(16):                                   # wedges of light out of the middle
        ang = k * math.tau / 16 + rng.uniform(-0.12, 0.12)
        wd = rng.uniform(0.03, 0.09)
        pts = [(320, 170)]
        for s in (-wd, wd):
            pts.append((320 + math.cos(ang + s) * 900, 170 + math.sin(ang + s) * 900))
        d.polygon(pts, fill=(255, 255, 255, int(rng.uniform(14, 34))))
    for k in range(6):                                    # the chevron lines at the top
        y = 6 + k * 7
        d.line([(0, y + 40), (180, y - 10), (360, y + 40)], fill=(255, 255, 255, 26), width=2)
    img = Image.alpha_composite(img, over.filter(ImageFilter.GaussianBlur(1.2)))
    halftone(img, (10, 250, 170, 350), tuple(int(v * 0.8 + 255 * 0.2) for v in m) + (255,), grow=(1, 0))
    halftone(img, (470, 10, 630, 110), tuple(int(v * 0.8 + 255 * 0.2) for v in m) + (255,), grow=(-1, 0))
    img.convert("RGB").save(os.path.join(OUT, "pk_burst_%s.png" % code))


def letters(text, h, tilt):
    """Big silver block letters with depth, leaning towards the middle."""
    f = ImageFont.truetype(FONT, h)
    w = int(f.getlength(text)) + 30
    face = Image.new("L", (w, int(h * 1.4)), 0)
    ImageDraw.Draw(face).text((10, 0), text, font=f, fill=255)
    face = face.crop(face.getbbox())
    fw, fh = face.size
    depth = max(4, h // 7)
    out = Image.new("RGBA", (fw + depth + 4, fh + depth + 4), (0, 0, 0, 0))
    for k in range(depth, 0, -1):                         # the sides
        v = int(70 + 60 * (1 - k / float(depth)))
        layer = Image.new("RGBA", face.size, (v, v, v + 20, 255))
        out.paste(layer, (2 + k, 2 + k), face)
    grad = np.zeros((fh, fw, 4), np.uint8)
    yy = np.linspace(0, 1, fh)[:, None]
    tone = 255 - 70 * yy + 30 * np.sin(yy * 9)            # chrome bands
    grad[..., 0] = np.clip(tone, 0, 255)
    grad[..., 1] = np.clip(tone, 0, 255)
    grad[..., 2] = np.clip(tone + 12, 0, 255)
    grad[..., 3] = 255
    out.paste(Image.fromarray(grad, "RGBA"), (2, 2), face)
    d = ImageDraw.Draw(out)
    # lean: shear so the wall seems to turn in towards the middle
    W, H = out.size
    sh = tilt
    out = out.transform((W, H + int(abs(sh) * W)), Image.AFFINE,
                        (1, 0, 0, sh, 1, -max(0, sh) * W if sh > 0 else 0), Image.BICUBIC)
    return out


def make_stadium(code):
    c, m, e, acc = THEMES[code]
    W, H = 640, 360
    dark = tuple(int(v * 0.30) for v in e)
    # sky: dark at the top, the colour lit up towards the stands
    ys = np.linspace(0, 1, H)[:, None, None]
    sky = np.array(dark, np.float32) * (1 - ys) + np.array(m, np.float32) * ys
    img = Image.fromarray(np.repeat(sky, W, 1).astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(img)
    cx, cy = 320, 330
    # the bowl: roof rim, stands, a lit band, ad boards
    d.ellipse((cx - 560, cy - 330, cx + 560, cy + 330), fill=tuple(int(v * 0.55) for v in e) + (255,))
    d.ellipse((cx - 560, cy - 330, cx + 560, cy + 330), outline=(20, 16, 40, 255), width=10)
    rng = np.random.default_rng(5)
    stands = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stands)
    for k in range(9):                                    # tiers, each a little lower and nearer
        rx, ry = 540 - k * 9, 312 - k * 14
        sd.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=tuple(int(v * 0.35) for v in e) + (255,), width=2)
    for _ in range(5200):                                 # the crowd, a sea of little lights
        x = rng.uniform(0, W)
        y = rng.uniform(20, 205)
        dx, dy = (x - cx) / 548.0, (y - cy) / 318.0
        if dx * dx + dy * dy > 1.0:
            continue
        pick = rng.random()
        col = (255, 255, 255) if pick < 0.08 else (c if pick < 0.4 else (m if pick < 0.75 else acc))
        k = rng.uniform(0.25, 0.75)
        sd.point((x, y), fill=tuple(int(v * k) for v in col) + (255,))
    img = Image.alpha_composite(img, stands)
    d = ImageDraw.Draw(img)
    for k in range(46):                                   # floodlights along the roof
        a = math.pi + k * math.pi / 45
        x, y = cx + math.cos(a) * 548, cy + math.sin(a) * 318
        if y > 150:
            continue
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 255, 255, 255))
    lights = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lights)
    for k in range(46):
        a = math.pi + k * math.pi / 45
        x, y = cx + math.cos(a) * 548, cy + math.sin(a) * 318
        if y < 150:
            ld.ellipse((x - 9, y - 6, x + 9, y + 6), fill=c + (90,))
    img = Image.alpha_composite(img, lights.filter(ImageFilter.GaussianBlur(4)))
    d = ImageDraw.Draw(img)
    # the lit band round the bowl
    for k, col in enumerate((acc, c, m)):
        rx, ry = 470 - k * 2, 126 - k * 2
        d.arc((cx - rx, cy - ry - 30, cx + rx, cy + ry - 30), 180, 360, fill=col + (255,), width=3)
    # haze behind the stage
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(haze).ellipse((150, 120, 490, 300), fill=c + (120,))
    img = Image.alpha_composite(img, haze.filter(ImageFilter.GaussianBlur(30)))
    # big letters either side: this game's own name
    left_small = letters("A SMALL", 22, 0.10)
    left = letters("WORLD", 58, 0.12)
    right = letters("CUP", 66, -0.12)
    img.alpha_composite(left_small, (40, 98))
    img.alpha_composite(left, (24, 118))
    img.alpha_composite(right, (W - right.size[0] - 34, 112))
    d = ImageDraw.Draw(img)
    # ad boards
    d.rectangle((0, 228, W, 246), fill=tuple(int(v * 0.5) for v in e) + (255,))
    d.line((0, 228, W, 228), fill=c + (255,), width=1)
    f = ImageFont.truetype(FONT, 11)
    x = 4
    while x < W:
        d.text((x, 231), "A SMALL WORLD CUP", font=f, fill=acc + (255,))
        x += 130
    # the pitch, striped, running away to the middle
    for y in range(246, H):
        k = (y - 246) / float(H - 246)
        for band in range(-12, 13):
            pass
    grass = np.zeros((H - 246, W, 3), np.float32)
    yy, xx = np.mgrid[246:H, 0:W].astype(np.float32)
    vx = (xx - 320) / (yy - 150 + 1e-3)                   # stripes converge on a vanishing point
    stripe = (np.floor(vx * 3.2) % 2)
    base = np.array((52, 150, 54), np.float32)
    shade = 0.62 + 0.38 * (yy - 246) / (H - 246)
    grass = base[None, None, :] * (shade[..., None] * (0.9 + 0.12 * stripe[..., None]))
    img.paste(Image.fromarray(np.clip(grass, 0, 255).astype(np.uint8), "RGB"), (0, 246))
    d = ImageDraw.Draw(img)
    # the glossy runway up to the stage
    run = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(run)
    rd.polygon([(262, 268), (378, 268), (520, H), (120, H)], fill=(14, 12, 28, 240))
    for k in range(9):                                    # light caught on the shine
        x0 = 280 + k * 10
        col = (c, acc, (255, 255, 255))[k % 3]
        rd.line([(x0, 272), (320 + (x0 - 320) * 2.4, H)], fill=col + (30,), width=2)
    img = Image.alpha_composite(img, run)
    d = ImageDraw.Draw(img)
    # the stage: two hexagonal steps, lit edges
    for k, (rx, ry, top) in enumerate(((96, 18, 268), (74, 13, 256))):
        body = tuple(int(v * 0.5 + 40) for v in c)
        pts_top = [(320 + rx * math.cos(a), top + ry * math.sin(a)) for a in np.linspace(0, math.tau, 7)[:-1]]
        pts_bot = [(x, y + 9) for x, y in pts_top]
        d.polygon([pts_top[0], pts_top[1], pts_top[2], pts_top[3], pts_bot[3], pts_bot[2], pts_bot[1], pts_bot[0]],
                  fill=tuple(int(v * 0.55) for v in body) + (255,))
        d.polygon(pts_top, fill=body + (255,))
        d.line(pts_top + [pts_top[0]], fill=(255, 255, 255, 255), width=1)
        d.line([pts_bot[0], pts_bot[1], pts_bot[2], pts_bot[3]], fill=c + (255,), width=1)
    img.convert("RGB").save(os.path.join(OUT, "pk_stadium_%s.png" % code))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    mask = land_mask()
    make_globe(mask)
    make_close(mask)
    for code in THEMES:
        make_burst(code)
        make_stadium(code)
    print("walkout pictures written to", OUT)
