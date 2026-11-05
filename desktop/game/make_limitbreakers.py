"""LIMIT BREAKERS - card template, frame overlay and pack foil.

    python3 make_limitbreakers.py [out_dir]

Writes:
  tpl_lb_card.png        the card: crimson storm, red lightning, snapped chains, a red crystal
                         bursting through the top-right corner of a silver frame, silver laurels
  tpl_lbframe_card.png   the same with the inside cut out - laid OVER the player so the laurels,
                         the frame and the crystal's shards sit in front of him
  tpl_lbc_card.png       pool C: the same card without the crystal (+ tpl_lbcframe_card.png)
  pack_5.png             the foil a Limit Breaker comes out of (pack index 5 in the game)
  lb_badge.png           the pack's crest (the pack reveal's "club" beat)
  flag_KOR|CIV|SRB|CMR|SVN.png   the five flags the pack needs that the game didn't have
  LB_<slug>_head|torso|arm|leg.png   each player in a match (needs make_sprites.py)
  LB_<slug>_figure.png   each player on his card (needs numpy, cardfig.py and cards_lb.py;
                         only figures that are missing are drawn - add --figures to redraw all)

Same 400 x 500 canvas and BODY box as every other template in make_art.py, so the game lays it
out with the routine it already has. Everything is drawn here - no card art, no logos.
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

TPL_W, TPL_H = 400, 500
BODY = (66, 34, 334, 458)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ---------------------------------------------------------------- palette
NIGHT = (22, 2, 8)
MAROON = (70, 6, 18)
BLOOD = (138, 12, 30)
CRIMSON = (200, 22, 44)
HOT = (255, 64, 78)
PINK = (255, 168, 178)
STEEL_D, STEEL, STEEL_L = (46, 42, 54), (124, 120, 138), (214, 212, 226)
SILVER_D, SILVER, SILVER_L = (96, 100, 118), (196, 200, 214), (246, 248, 255)
WHITE = (255, 255, 255)


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def layer():
    return Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))


def text_img(txt, size, fill, stroke=(0, 0, 0), sw=3):
    f = ImageFont.truetype(FONT, size)
    l, t, r, b = f.getbbox(txt, stroke_width=sw)
    im = Image.new("RGBA", (r - l + 4, b - t + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - l, 2 - t), txt, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)
    return im


def pixelate(im, k=3):
    return im.resize((max(1, im.width // k), max(1, im.height // k)), Image.NEAREST).resize(
        (im.width // k * k, im.height // k * k), Image.NEAREST)


def card_path(box, ct=20, cb=34, steps=10):
    """The silhouette: chamfered top corners, rounder cut bottom corners."""
    x0, y0, x1, y1 = box
    pts = [(x0 + ct, y0), (x1 - ct, y0), (x1, y0 + ct)]
    for i in range(steps + 1):                                  # bottom-right, a soft curve
        a = i / float(steps) * math.pi / 2
        pts.append((x1 - cb + cb * math.cos(a), y1 - cb + cb * math.sin(a)))
    for i in range(steps + 1):                                  # bottom-left
        a = math.pi / 2 + i / float(steps) * math.pi / 2
        pts.append((x0 + cb + cb * math.cos(a), y1 - cb + cb * math.sin(a)))
    pts.append((x0, y0 + ct))
    return pts


def pin_corners(im):
    """The game trims a template to what is visible before scaling it, so a pixel at alpha 1
    in two corners keeps every template (and its overlay) on the full 400 x 500 frame."""
    im.putpixel((0, 0), (0, 0, 0, 1))
    im.putpixel((im.width - 1, im.height - 1), (0, 0, 0, 1))


def mask_of(pts, size=(TPL_W, TPL_H)):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m


# ---------------------------------------------------------------- the storm behind everything
def storm(w, h, rnd, ox=0, oy=0, bright=1.0):
    """Crimson smoke: a dark gradient with big soft clouds of red and a little pink in it."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / float(h)
        d.line([(0, y), (w, y)], fill=mix(MAROON, NIGHT, abs(t - 0.38) * 1.6) + (255,))
    clouds = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(clouds)
    for _ in range(int(w * h / 1400)):
        x, y = rnd.uniform(-0.1, 1.1) * w, rnd.uniform(-0.1, 1.05) * h
        r = rnd.uniform(18, 70)
        col = rnd.choice([BLOOD, BLOOD, CRIMSON, (160, 30, 54), (96, 8, 22), (230, 90, 110)])
        a = rnd.randint(30, 90) if col != (230, 90, 110) else rnd.randint(16, 40)
        a = min(255, int(a * bright))
        cd.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=col + (a,))
    clouds = clouds.filter(ImageFilter.GaussianBlur(14))
    im.alpha_composite(clouds)
    wisps = Image.new("RGBA", (w, h), (0, 0, 0, 0))             # thin bright smoke threads
    wd = ImageDraw.Draw(wisps)
    for _ in range(int(w / 22)):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        pts = []
        a = rnd.uniform(-0.6, 0.6)
        for k in range(14):
            pts.append((x, y))
            a += rnd.uniform(-0.45, 0.45)
            x += math.cos(a) * 9
            y += math.sin(a) * 9
        wd.line(pts, fill=(255, 140, 150, rnd.randint(30, 70)), width=rnd.choice([2, 3]), joint="curve")
    im.alpha_composite(wisps.filter(ImageFilter.GaussianBlur(1.6)))
    return im


def bolt_points(p0, p1, rnd, disp, depth):
    if depth == 0:
        return [p0, p1]
    mx, my = (p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dx, dy) or 1.0
    off = rnd.uniform(-disp, disp)
    mid = (mx - dy / ln * off, my + dx / ln * off)
    return bolt_points(p0, mid, rnd, disp / 2.0, depth - 1)[:-1] + bolt_points(mid, p1, rnd, disp / 2.0, depth - 1)


def lightning(size, bolts, rnd, width=2.0):
    """Red lightning: a wide blurred glow under a thin hot core, with branches off each bolt."""
    w, h = size
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    core = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd, cd = ImageDraw.Draw(glow), ImageDraw.Draw(core)
    for p0, p1, disp in bolts:
        pts = bolt_points(p0, p1, rnd, disp, 6)
        gd.line(pts, fill=HOT + (200,), width=int(7 * width))
        cd.line(pts, fill=PINK + (255,), width=max(1, int(width + 0.5)))
        cd.line(pts, fill=WHITE + (255,), width=max(1, int(width * 0.5)))
        for _ in range(rnd.randint(2, 4)):                      # branches
            i = rnd.randrange(4, len(pts) - 4)
            a = math.atan2(p1[1] - p0[1], p1[0] - p0[0]) + rnd.choice([-1, 1]) * rnd.uniform(0.4, 1.0)
            ln = rnd.uniform(0.18, 0.4) * math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            q = (pts[i][0] + math.cos(a) * ln, pts[i][1] + math.sin(a) * ln)
            br = bolt_points(pts[i], q, rnd, disp * 0.4, 4)
            gd.line(br, fill=HOT + (140,), width=int(4 * width))
            cd.line(br, fill=PINK + (230,), width=max(1, int(width * 0.6)))
    out = glow.filter(ImageFilter.GaussianBlur(5 * width))
    out.alpha_composite(glow.filter(ImageFilter.GaussianBlur(1.5 * width)))
    out.alpha_composite(core)
    return out


# ---------------------------------------------------------------- chains
def _ellipse_pts(cx, cy, rx, ry, ang, n=28):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + rx * math.cos(t) * ca - ry * math.sin(t) * sa, cy + rx * math.cos(t) * sa + ry * math.sin(t) * ca)
            for t in (2 * math.pi * k / n for k in range(n))]


def chain_link(im, cx, cy, ang, s, face, open_gap=False):
    """One link: face-on it is a ring, side-on a short bar. Dark steel with a lit upper edge."""
    lk = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lk)
    if face:
        d.polygon(_ellipse_pts(cx, cy, 11 * s, 6.6 * s, ang), fill=STEEL_D)
        d.polygon(_ellipse_pts(cx, cy - 0.6 * s, 10 * s, 5.6 * s, ang), fill=STEEL)
        d.polygon(_ellipse_pts(cx + 0.5 * s, cy + 0.6 * s, 9.4 * s, 4.9 * s, ang), fill=STEEL_D)
        d.polygon(_ellipse_pts(cx, cy, 6.4 * s, 2.4 * s, ang), fill=(0, 0, 0, 0))
        hl = _ellipse_pts(cx, cy - 1.2 * s, 8.6 * s, 4.6 * s, ang, 28)[15:22]
        d.line(hl, fill=STEEL_L, width=max(1, int(1.6 * s)))
        if open_gap:                                             # a snapped link, prised open
            ca, sa = math.cos(ang), math.sin(ang)
            gx, gy = cx + 9 * s * ca, cy + 9 * s * sa
            d.ellipse([gx - 4 * s, gy - 4 * s, gx + 4 * s, gy + 4 * s], fill=(0, 0, 0, 0))
    else:
        ca, sa = math.cos(ang), math.sin(ang)
        a = (cx - ca * 10 * s, cy - sa * 10 * s)
        b = (cx + ca * 10 * s, cy + sa * 10 * s)
        d.line([a, b], fill=STEEL_D, width=int(5.4 * s))
        d.line([(a[0], a[1] - 0.8 * s), (b[0], b[1] - 0.8 * s)], fill=STEEL, width=int(3 * s))
        d.line([(a[0] + ca * 2 * s, a[1] - 1.4 * s), (b[0] - ca * 2 * s, b[1] - 1.4 * s)], fill=STEEL_L,
               width=max(1, int(1.1 * s)))
    im.alpha_composite(lk)


def chain(im, a, b, s, rnd, broken_at=None):
    """Links from a to b. broken_at (0..1): the chain stops there, the last link prised open."""
    ln = math.hypot(b[0] - a[0], b[1] - a[1])
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    step = 15.5 * s
    n = int(ln / step)
    stop = n if broken_at is None else int(n * broken_at)
    for k in range(stop + 1):
        x = a[0] + math.cos(ang) * step * k + math.sin(k * 0.9) * 1.2 * s
        y = a[1] + math.sin(ang) * step * k + math.cos(k * 0.7) * 1.2 * s
        chain_link(im, x, y, ang + rnd.uniform(-0.08, 0.08), s, k % 2 == 0, open_gap=(k == stop and broken_at))
    return (a[0] + math.cos(ang) * step * stop, a[1] + math.sin(ang) * step * stop), ang


def glow_behind(lay, col=HOT, blur=3, k=0.9):
    """A soft coloured halo the shape of `lay`, so dark steel reads against dark red."""
    g = Image.new("RGBA", lay.size, col + (0,))
    g.putalpha(lay.split()[3].filter(ImageFilter.GaussianBlur(blur)).point(lambda v: min(255, int(v * k * 1.6))))
    g.alpha_composite(lay)
    return g


# ---------------------------------------------------------------- the crystal
def crystal(size, cx, cy, R, rnd, shards=22, burst=1.0):
    """A faceted red crystal cracking open: two rings of facets lit from the top-left, glowing
    cracks running out from the core, shards flying off with streaks behind them."""
    w, h = size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bloom = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(bloom).ellipse([cx - R * 1.2, cy - R * 1.2, cx + R * 1.2, cy + R * 1.2], fill=HOT + (150,))
    out.alpha_composite(bloom.filter(ImageFilter.GaussianBlur(R * 0.3)))
    d = ImageDraw.Draw(out)
    N = 11
    outer, mid = [], []
    for k in range(N):
        a = 2 * math.pi * k / N + rnd.uniform(-0.12, 0.12)
        r = R * rnd.uniform(0.86, 1.05)
        outer.append((cx + math.cos(a) * r, cy + math.sin(a) * r * 1.06))
        a2 = a + math.pi / N
        r2 = R * rnd.uniform(0.48, 0.62)
        mid.append((cx + math.cos(a2) * r2, cy + math.sin(a2) * r2))
    core = (cx - R * 0.10, cy - R * 0.12)
    L = (-0.62, -0.78)                                          # light from the top-left

    def tone(tri, bias=0.0):
        mx = sum(p[0] for p in tri) / 3.0 - cx
        my = sum(p[1] for p in tri) / 3.0 - cy
        ln = math.hypot(mx, my) or 1.0
        k = (mx / ln) * L[0] + (my / ln) * L[1]
        k = 0.5 + 0.5 * k + bias + rnd.uniform(-0.16, 0.16)
        if k < 0.25:
            return (74, 2, 14)
        if k < 0.45:
            return (138, 8, 26)
        if k < 0.62:
            return (198, 18, 38)
        if k < 0.80:
            return (240, 54, 66)
        if k < 0.92:
            return (255, 120, 128)
        return (255, 210, 214)

    facets = []
    for k in range(N):
        o0, o1 = outer[k], outer[(k + 1) % N]
        m0, mp = mid[k], mid[(k - 1) % N]
        facets.append(((o0, o1, m0), 0.0))
        facets.append(((o0, m0, mp), 0.05))
    for k in range(N):                                          # the inner fan
        facets.append(((mid[k], mid[(k + 1) % N], core), 0.14))
    for tri, bias in facets:
        d.polygon(tri, fill=tone(tri, bias))
    for k in range(N):                                          # facet edges catch the light
        d.line([outer[k], mid[k]], fill=(255, 150, 156), width=1)
        d.line([mid[k], core], fill=(255, 196, 200), width=1)
    d.line(outer + [outer[0]], fill=(60, 0, 10), width=3)
    glint = (cx - R * 0.42, cy - R * 0.48)                      # one hard white glint
    d.polygon([(glint[0], glint[1] - 9), (glint[0] + 3, glint[1] - 2), (glint[0] + 11, glint[1]),
               (glint[0] + 3, glint[1] + 2), (glint[0], glint[1] + 9), (glint[0] - 3, glint[1] + 2),
               (glint[0] - 11, glint[1]), (glint[0] - 3, glint[1] - 2)], fill=WHITE)
    cracks = Image.new("RGBA", (w, h), (0, 0, 0, 0))            # glowing cracks out of the core
    kd = ImageDraw.Draw(cracks)
    for k in range(7):
        a = rnd.uniform(0, 2 * math.pi)
        end = (core[0] + math.cos(a) * R * rnd.uniform(0.8, 1.15), core[1] + math.sin(a) * R * rnd.uniform(0.8, 1.15))
        pts = bolt_points(core, end, rnd, R * 0.16, 4)
        kd.line(pts, fill=(255, 236, 200, 255), width=2)
    out.alpha_composite(cracks.filter(ImageFilter.GaussianBlur(2.2)))
    out.alpha_composite(cracks)
    sd = ImageDraw.Draw(out)                                    # shards flying out
    for _ in range(shards):
        a = rnd.uniform(0, 2 * math.pi)
        r = R * rnd.uniform(1.08, 1.9) * burst
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        if not (14 < x < w - 14 and 14 < y < h - 14):
            continue
        s = rnd.uniform(3, 9) * (1.25 - (r / (R * 1.9)) * 0.5)
        rot = rnd.uniform(0, 2 * math.pi)
        tri = [(x + math.cos(rot + j * 2.2) * s * (1.5 if j == 0 else 0.8),
                y + math.sin(rot + j * 2.2) * s * (1.5 if j == 0 else 0.8)) for j in range(3)]
        tail = (x - math.cos(a) * s * 3.2, y - math.sin(a) * s * 3.2)
        sd.line([tail, (x, y)], fill=(255, 90, 100, 110), width=max(1, int(s * 0.5)))
        sd.polygon(tri, fill=rnd.choice([(240, 54, 66), (198, 18, 38), (255, 140, 146)]), outline=(255, 210, 214))
    return out


# ---------------------------------------------------------------- frame pieces
def silver_band(size, steps=200):
    """Chrome: a diagonal sweep of bright and dark silver with a red reflection running through."""
    w, h = size
    band = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(band)
    stops = [SILVER_L, SILVER, SILVER_D, (220, 160, 170), SILVER_L, SILVER, (120, 124, 140), SILVER_L]
    span = w + h
    for i in range(steps):
        t = i / float(steps - 1)
        k = t * (len(stops) - 1)
        col = mix(stops[int(k)], stops[min(len(stops) - 1, int(k) + 1)], k - int(k))
        x = -h + span * t
        d.line([(x, 0), (x + h, h)], fill=col, width=int(span / steps) + 3)
    return band


def laurel(d, side, rnd, cx=TPL_W / 2.0, bottom=TPL_H - 22, top=150, spread=148):
    """A silver laurel branch up one side of the card, leaves pointing up and out."""
    prev = None
    n = 16
    for k in range(n):
        t = k / float(n - 1)
        x = cx + side * (34 + spread * math.sin(min(1.0, t * 1.55) * math.pi / 2))
        y = bottom - t * (bottom - top)
        if prev:
            d.line([prev, (x, y)], fill=SILVER_D, width=5)
            d.line([prev, (x, y)], fill=SILVER, width=2)
        prev = (x, y)
        up = -math.pi / 2 + side * (0.35 + 0.25 * (1 - t))
        for leaf, lean in ((0, -0.95), (1, 0.75)):
            la = up + side * lean
            ln, wd = 30 - t * 7, 9.0 - t * 2.0
            ca, sa = math.cos(la), math.sin(la)
            pts = []
            for u, v in ((0.0, 0.0), (0.3, 0.95), (0.7, 0.8), (1.0, 0.0), (0.7, -0.8), (0.3, -0.95)):
                pts.append((x + ca * ln * u - sa * wd * v, y + sa * ln * u + ca * wd * v))
            d.polygon(pts, fill=(222, 224, 236) if leaf else (160, 164, 182), outline=(44, 40, 52))
            mid_a = (x + ca * ln * 0.15, y + sa * ln * 0.15)
            mid_b = (x + ca * ln * 0.85, y + sa * ln * 0.85)
            d.line([mid_a, mid_b], fill=SILVER_D if leaf else (130, 134, 150), width=1)
            if k % 3 == 1 and leaf:                              # a red tip now and then
                tip = (x + ca * ln * 0.92, y + sa * ln * 0.92)
                d.ellipse([tip[0] - 2.5, tip[1] - 2.5, tip[0] + 2.5, tip[1] + 2.5], fill=HOT)


# ---------------------------------------------------------------- the card
FRONT = {}                       # pieces of the frame layer that live inside the card (kept in the overlay)
CRYSTAL_AT = (BODY[2] - 34, BODY[1] + 52)
CRYSTAL_R = 58


def make_lb_template(seed=7, crystal_on=True, layers=False):
    """crystal_on=False is the pool C card: the same storm, chains, frame and laurels, no crystal.
    layers=True also returns the card cut in two round its lightning, for the game to animate:
    BACK (aura, laurels, the storm and the chains) and TOP (the crystal's light, the dark plate,
    the frame) - the game draws its own bolts between them, a new shape every strike."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = BODY
    path = card_path(BODY)
    im = layer()
    # ---- a red aura outside the card, strongest at the top-right where it is breaking
    aura = layer()
    ad = ImageDraw.Draw(aura)
    ad.polygon(card_path((x0 - 16, y0 - 16, x1 + 16, y1 + 16)), fill=(200, 16, 40, 170))
    if crystal_on:
        ad.ellipse([CRYSTAL_AT[0] - 70, CRYSTAL_AT[1] - 60, CRYSTAL_AT[0] + 50, CRYSTAL_AT[1] + 70],
                   fill=(255, 50, 64, 200))
    im.alpha_composite(aura.filter(ImageFilter.GaussianBlur(16)))
    # ---- laurels (behind the card body: they wrap round its sides)
    lau = layer()
    ld = ImageDraw.Draw(lau)
    for side in (-1, 1):
        laurel(ld, side, rnd)
    glow = Image.new("RGBA", lau.size, HOT + (0,))
    glow.putalpha(lau.split()[3].filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * 0.7)))
    im.alpha_composite(glow)
    im.alpha_composite(lau)
    # ---- the card body
    body = layer()
    body.alpha_composite(storm(x1 - x0, y1 - y0, rnd, bright=1.7), (x0, y0))
    chains = layer()
    end1, a1 = chain(chains, (x0 - 20, y0 + 120), (x1 + 20, y0 + 300), 0.95, rnd, broken_at=0.42)
    chain(chains, (x1 + 24, y0 + 360), (x0 - 10, y0 + 200), 0.85, rnd)
    end2, a2 = chain(chains, (x0 + 10, y1 + 10), (x0 + 200, y0 + 150), 0.8, rnd, broken_at=0.55)
    cd = ImageDraw.Draw(chains)
    for (ex, ey), aa in ((end1, a1), (end2, a2)):               # the far half, snapped and falling
        far = (ex + math.cos(aa) * 30, ey + math.sin(aa) * 30 + 10)
        chain_link(chains, far[0], far[1], aa + 0.9, 0.9, True, open_gap=True)
        for j in range(4):                                       # bits of link in the air
            fx, fy = ex + math.cos(aa) * (14 + j * 7) + rnd.uniform(-6, 6), ey + math.sin(aa) * (14 + j * 7) - 8 + rnd.uniform(-6, 6)
            cd.rectangle([fx, fy, fx + 2, fy + 2], fill=STEEL_L)
        spark = (ex + math.cos(aa) * 12, ey + math.sin(aa) * 12)
        for j in range(8):
            a = rnd.uniform(0, 2 * math.pi)
            cd.line([spark, (spark[0] + math.cos(a) * rnd.uniform(6, 14), spark[1] + math.sin(a) * rnd.uniform(6, 14))],
                    fill=(255, 220, 180), width=1)
    shade = Image.new("RGBA", chains.size, (40, 0, 8, 0))        # chains sit back in the smoke
    shade.putalpha(chains.split()[3].point(lambda v: int(v * 0.25)))
    body.alpha_composite(chains)
    body.alpha_composite(shade)
    back = im.copy()                                            # the still part under the bolts
    under = body.copy()
    under.putalpha(ImageChops.multiply(under.split()[3], mask_of(path)))
    back.alpha_composite(under)
    over = layer()                                              # ... and the part over them
    body.alpha_composite(lightning(body.size, [
        ((x0 + 40, y0 - 10), (x0 + 14, y0 + 300), 46),
        ((x1 - 14, y0 + 110), (x1 - 34, y0 + 330), 40),
        ((x0 + 150, y0 - 6), (x0 + 96, y0 + 110), 26),
        ((x0 + 210, y0 - 6), (x0 + 250, y0 + 120), 24),
        ((x0 + 6, y0 + 230), (x0 + 60, y0 + 320), 24),
    ], rnd, 1.7))
    # the crystal's light spilling into the card
    spill = layer()
    if crystal_on:
        ImageDraw.Draw(spill).ellipse([CRYSTAL_AT[0] - 150, CRYSTAL_AT[1] - 130, CRYSTAL_AT[0] + 110, CRYSTAL_AT[1] + 150],
                                  fill=(255, 60, 70, 70))
    body.alpha_composite(spill.filter(ImageFilter.GaussianBlur(30)))
    over.alpha_composite(spill.filter(ImageFilter.GaussianBlur(30)))
    # name plate + a dark pool behind the rating
    plate = layer()
    pd = ImageDraw.Draw(plate)
    for y in range(314, y1 + 1):
        a = int(240 * min(1.0, ((y - 314) / 44.0) ** 1.4))
        pd.line([(x0, y), (x1, y)], fill=(18, 0, 6, a))
    body.alpha_composite(plate)
    over.alpha_composite(plate)
    pool = layer()
    pl = ImageDraw.Draw(pool)
    for k in range(24):
        pl.ellipse([x0 - 140 + k * 6, y0 - 130 + k * 6, x0 + 220 - k * 6, y0 + 210 - k * 6], fill=(14, 0, 6, 18))
    body.alpha_composite(pool)
    over.alpha_composite(pool)
    body.putalpha(ImageChops.multiply(body.split()[3], mask_of(path)))
    over.putalpha(ImageChops.multiply(over.split()[3], mask_of(path)))
    im.alpha_composite(body)
    front = frame_layer(rnd, crystal_on)
    im.alpha_composite(front)
    pin_corners(im)
    if not layers:
        return im
    over.alpha_composite(front)
    pin_corners(back)
    pin_corners(over)
    return im, back, over


def frame_layer(rnd, crystal_on=True):
    """Everything that sits IN FRONT of the player: the silver frame (broken open at the
    top-right), the red spikes and gem at the foot, and the crystal bursting through."""
    x0, y0, x1, y1 = BODY
    path = card_path(BODY)
    out = layer()
    d = ImageDraw.Draw(out)
    d.line(path + [path[0]], fill=(30, 4, 10), width=19, joint="curve")
    ring = Image.new("L", out.size, 0)
    ImageDraw.Draw(ring).line(path + [path[0]], fill=255, width=12, joint="curve")
    out.paste(silver_band(out.size), (0, 0), ring)
    d.line(path + [path[0]], fill=WHITE, width=1, joint="curve")
    inner = card_path((x0 + 9, y0 + 9, x1 - 9, y1 - 9), 15, 27)
    d.line(inner + [inner[0]], fill=HOT, width=2, joint="curve")
    # ---- horns on the top corners and red spikes off the bottom ones
    for side in (-1, 1):
        cx = x0 if side < 0 else x1
        d.polygon([(cx - side * 4, y0 + 30), (cx + side * 22, y0 - 26), (cx + side * 8, y0 + 44)],
                  fill=SILVER, outline=(40, 36, 48))
        d.line([(cx + side * 2, y0 + 30), (cx + side * 18, y0 - 18)], fill=SILVER_L, width=2)
        by = y1 - 26
        for j, (ln, ang) in enumerate(((38, 0.55), (28, 0.95), (22, 0.25))):
            a = ang if side > 0 else math.pi - ang
            tip = (cx + math.cos(a) * ln, by + math.sin(a) * ln)
            base_a = (cx - side * 6, by - 8 + j * 6)
            base_b = (cx - side * 14, by + 4 + j * 6)
            d.polygon([base_a, tip, base_b], fill=(214, 24, 44), outline=(70, 0, 12))
    # ---- the break: frame torn open round the crystal, cracks running off it
    cx, cy = CRYSTAL_AT
    hole = Image.new("L", out.size, 255)
    if crystal_on:
        ImageDraw.Draw(hole).ellipse([cx - CRYSTAL_R * 0.95, cy - CRYSTAL_R * 0.95, cx + CRYSTAL_R * 0.95,
                                      cy + CRYSTAL_R * 0.95], fill=0)
    out.putalpha(ImageChops.multiply(out.split()[3], hole))
    cracks = layer()
    kd = ImageDraw.Draw(cracks)
    for a0, ln in ((math.pi * 1.02, 90), (math.pi * 0.62, 80), (math.pi * 1.32, 60), (math.pi * 0.2, 50)):
        p0 = (cx + math.cos(a0) * CRYSTAL_R * 0.9, cy + math.sin(a0) * CRYSTAL_R * 0.9)
        p1 = (p0[0] + math.cos(a0) * ln, p0[1] + math.sin(a0) * ln)
        kd.line(bolt_points(p0, p1, rnd, 14, 4), fill=(255, 90, 100, 255), width=2)
    if crystal_on:
        out.alpha_composite(cracks.filter(ImageFilter.GaussianBlur(2)))
        out.alpha_composite(cracks)
        out.alpha_composite(crystal(out.size, cx, cy, CRYSTAL_R, rnd))
    # ---- a snapped chain hanging in off the left edge, in front of him
    hang = layer()
    end, ang = chain(hang, (x0 - 14, y0 + 196), (x0 + 120, y0 + 262), 0.9, rnd, broken_at=0.42)
    hd = ImageDraw.Draw(hang)
    spark = (end[0] + math.cos(ang) * 11, end[1] + math.sin(ang) * 11)
    for j in range(10):
        a = rnd.uniform(-1.3, 1.3) + ang
        hd.line([spark, (spark[0] + math.cos(a) * rnd.uniform(6, 16), spark[1] + math.sin(a) * rnd.uniform(6, 16))],
                fill=(255, 226, 190), width=2)
    for j in range(3):
        fx, fy = spark[0] + math.cos(ang) * (10 + j * 8) + rnd.uniform(-4, 4), spark[1] + math.sin(ang) * (10 + j * 8) + rnd.uniform(-5, 5)
        hd.rectangle([fx, fy, fx + 3, fy + 3], fill=STEEL_L)
    hang = glow_behind(hang, (255, 70, 84), 2.5)
    out.alpha_composite(hang)
    FRONT["hang"] = hang
    # ---- the gem at the foot: gunmetal hexagon, red core
    gx, gy = (x0 + x1) // 2, y1 - 1
    hexa = [(gx + math.cos(math.pi / 6 + j * math.pi / 3) * 24, gy + math.sin(math.pi / 6 + j * math.pi / 3) * 24)
            for j in range(6)]
    d = ImageDraw.Draw(out)
    d.polygon(hexa, fill=(58, 58, 70), outline=SILVER_L)
    inner_h = [(gx + (x - gx) * 0.62, gy + (y - gy) * 0.62) for x, y in hexa]
    d.polygon(inner_h, fill=(150, 8, 28))
    d.polygon([inner_h[3], inner_h[4], (gx, gy)], fill=(255, 90, 100))
    d.polygon([inner_h[0], inner_h[1], (gx, gy)], fill=(84, 2, 16))
    return out


def lb_frame(tpl_seed=7, crystal_on=True):
    """tpl_lbframe: the frame alone, with the card's inside cut out (laid over the player)."""
    rnd = random.Random(tpl_seed)
    # replay the template's random stream up to the frame so the cracks and shards match
    make = make_lb_template(tpl_seed, crystal_on)
    x0, y0, x1, y1 = BODY
    hole = Image.new("L", make.size, 255)
    ImageDraw.Draw(hole).polygon(card_path((x0 + 6, y0 + 6, x1 - 6, y1 - 6), 16, 29), fill=0)
    gx, gy = (x0 + x1) // 2, y1 - 1                              # the gem stays BEHIND the player
    ImageDraw.Draw(hole).polygon([(gx + math.cos(math.pi / 6 + j * math.pi / 3) * 27,
                                   gy + math.sin(math.pi / 6 + j * math.pi / 3) * 27) for j in range(6)], fill=0)
    cx, cy = CRYSTAL_AT                                          # but keep the crystal in front
    if crystal_on:
        ImageDraw.Draw(hole).ellipse([cx - CRYSTAL_R * 1.05, cy - CRYSTAL_R * 1.05, cx + CRYSTAL_R * 1.05,
                                      cy + CRYSTAL_R * 1.05], fill=255)
    out = make.copy()
    out.putalpha(ImageChops.multiply(make.split()[3], hole))
    out.alpha_composite(FRONT["hang"])
    pin_corners(out)
    return make, out


# ---------------------------------------------------------------- the pack
def make_pack_lb(W=300, H=420, seed=11, letter=None):
    """The Limit Breakers foil. (31 Oct: two drafts now - `letter` stamps A or B in a silver badge.)"""
    rnd = random.Random(seed)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    body = storm(W, H, rnd)
    chains = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    end, ang = chain(chains, (-10, 262), (W + 10, 150), 1.5, rnd, broken_at=0.42)
    far = (end[0] + math.cos(ang) * 56, end[1] + math.sin(ang) * 56 + 10)
    chain(chains, far, (W + 20, 156), 1.5, rnd)
    sd = ImageDraw.Draw(chains)
    spark = (end[0] + math.cos(ang) * 22, end[1] + math.sin(ang) * 22)
    for j in range(14):
        a = rnd.uniform(0, 2 * math.pi)
        sd.line([spark, (spark[0] + math.cos(a) * rnd.uniform(8, 22), spark[1] + math.sin(a) * rnd.uniform(8, 22))],
                fill=(255, 226, 190), width=2)
    body.alpha_composite(glow_behind(chains, (255, 70, 84), 3))
    body.alpha_composite(lightning((W, H), [((40, 0), (10, 260), 50), ((W - 30, 20), (W - 60, 300), 50),
                                            ((90, 30), (200, 170), 30)], rnd, 1.8))
    body.alpha_composite(crystal((W, H), W // 2, 150, 62, rnd, shards=26))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([10, 24, W - 10, H - 24], 18, fill=255)
    body.putalpha(mask)
    im.alpha_composite(body)
    foil = silver_band((W, H))
    trim = Image.new("L", (W, H), 0)
    td = ImageDraw.Draw(trim)
    for x in range(10, W - 10, 12):                              # crimped foil ends
        td.polygon([(x, 26), (x + 6, 8), (x + 12, 26)], fill=255)
        td.polygon([(x, H - 26), (x + 6, H - 8), (x + 12, H - 26)], fill=255)
    td.rectangle([10, 24, W - 10, 40], fill=255)
    td.rectangle([10, H - 40, W - 10, H - 24], fill=255)
    td.rounded_rectangle([10, 24, W - 10, H - 24], 18, outline=255, width=6)
    im.paste(foil, (0, 0), trim)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([16, 46, W - 16, H - 46], 14, outline=HOT, width=2)
    # name plate
    plate = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    pd.polygon([(22, 274), (W - 22, 260), (W - 22, 366), (22, 378)], fill=(24, 0, 8, 235))
    im.alpha_composite(plate)
    edge = Image.new("L", (W, H), 0)
    ed = ImageDraw.Draw(edge)
    ed.line([(22, 274), (W - 22, 260)], fill=255, width=7)
    ed.line([(22, 378), (W - 22, 366)], fill=255, width=7)
    im.paste(Image.new("RGBA", (W, H), SILVER + (255,)), (0, 0), edge)
    t = text_img("LIMIT", 46, WHITE, (110, 0, 20), 4).rotate(2.7, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(t, ((W - t.width) // 2, 299 - t.height // 2))
    t2 = text_img("BREAKERS", 34, (255, 110, 120), (60, 0, 12), 4).rotate(2.7, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(t2, ((W - t2.width) // 2, 343 - t2.height // 2))
    if letter:                                                    # the draft's letter, top right
        d = ImageDraw.Draw(im)
        cx, cy, r = W - 56, 82, 30
        d.ellipse([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4], fill=SILVER + (255,))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(30, 0, 8, 255), outline=HOT, width=3)
        t3 = text_img(letter, 40, WHITE, (110, 0, 20), 3)
        im.alpha_composite(t3, (cx - t3.width // 2, cy - t3.height // 2))
    return pixelate(im, 3)


# ---------------------------------------------------------------- the pack's crest and flags
def make_lb_badge(W=240, H=280, seed=5):
    """A dark shield with a silver edge and the red crystal cracking open on it."""
    rnd = random.Random(seed)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(20, 16), (W - 20, 16), (W - 20, H - 90), (W // 2, H - 14), (20, H - 90)]
    d.polygon(pts, fill=SILVER_D)
    inner = [(30, 26), (W - 30, 26), (W - 30, H - 96), (W // 2, H - 30), (30, H - 96)]
    d.polygon(inner, fill=(30, 2, 10))
    end, ang = chain(im, (34, 196), (W - 34, 120), 1.2, rnd, broken_at=0.45)
    im.alpha_composite(crystal((W, H), W // 2, 120, 58, rnd, shards=14, burst=0.8))
    d = ImageDraw.Draw(im)
    d.line(pts + [pts[0]], fill=SILVER_L, width=5)
    return pixelate(im, 3)


def _flag_canvas(W=240, H=160, bg=WHITE):
    im = Image.new("RGBA", (W, H), bg + (255,))
    return im, ImageDraw.Draw(im)


def _star(cx, cy, ro, ri, n=5, rot=-math.pi / 2):
    return [(cx + math.cos(rot + k * math.pi / n) * (ro if k % 2 == 0 else ri),
             cy + math.sin(rot + k * math.pi / n) * (ro if k % 2 == 0 else ri)) for k in range(2 * n)]


def make_flags():
    """Simplified flags, drawn the way make_art.py draws its extra ones (240 x 160, pixelated)."""
    out = {}
    im, d = _flag_canvas()                                       # South Korea: taegeuk + four trigrams
    cx, cy, r = 120, 80, 40
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=(205, 46, 58))
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 0, 180, fill=(0, 71, 160))
    d.ellipse([cx - r, cy - r / 2, cx, cy + r / 2], fill=(205, 46, 58))
    d.ellipse([cx, cy - r / 2, cx + r, cy + r / 2], fill=(0, 71, 160))
    for (tx, ty, ang) in ((52, 34, 33), (188, 126, 33), (188, 34, -33), (52, 126, -33)):
        bars = Image.new("RGBA", (40, 34), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bars)
        for k in range(3):
            bd.rectangle([0, k * 12, 39, k * 12 + 7], fill=(20, 20, 24))
        bars = bars.rotate(ang, expand=True, resample=Image.NEAREST)
        im.alpha_composite(bars, (int(tx - bars.width / 2), int(ty - bars.height / 2)))
    out["KOR"] = im
    im, d = _flag_canvas()                                       # Ivory Coast
    for k, c in enumerate(((247, 127, 0), WHITE, (0, 158, 96))):
        d.rectangle([k * 80, 0, k * 80 + 80, 160], fill=c)
    out["CIV"] = im
    im, d = _flag_canvas()                                       # Serbia: red-blue-white + a simple crest
    for k, c in enumerate(((198, 54, 60), (12, 64, 118), WHITE)):
        d.rectangle([0, k * 160 / 3, 240, (k + 1) * 160 / 3], fill=c)
    d.polygon([(52, 40), (92, 40), (92, 100), (72, 116), (52, 100)], fill=(198, 54, 60), outline=(230, 190, 80))
    d.rectangle([68, 48, 76, 104], fill=WHITE)
    d.rectangle([58, 64, 86, 72], fill=WHITE)
    out["SRB"] = im
    im, d = _flag_canvas()                                       # Cameroon
    for k, c in enumerate(((0, 122, 94), (206, 17, 38), (252, 209, 22))):
        d.rectangle([k * 80, 0, k * 80 + 80, 160], fill=c)
    d.polygon(_star(120, 80, 26, 11), fill=(252, 209, 22))
    out["CMR"] = im
    im, d = _flag_canvas()                                       # Slovenia: white-blue-red + a small shield
    for k, c in enumerate((WHITE, (0, 92, 168), (237, 28, 36))):
        d.rectangle([0, k * 160 / 3, 240, (k + 1) * 160 / 3], fill=c)
    d.polygon([(50, 26), (96, 26), (96, 70), (73, 86), (50, 70)], fill=(0, 92, 168), outline=(237, 28, 36))
    d.polygon([(54, 66), (64, 50), (73, 60), (82, 46), (92, 66)], fill=WHITE)
    out["SVN"] = im
    return {code: pixelate(f, 3) for code, f in out.items()}


# ---------------------------------------------------------------- the players in a match
# make_sprites.py kits (base, alt, pattern, trim, number, shorts, shorts_trim, socks, sock_trim,
# badge, stars) - colours only, no crests. Pool A/B wear the shirts in Hubi's pictures, pool C
# their country's.
def _kit(base, trim, number, shorts, socks, alt=None, pattern="plain", **more):
    k = dict(base=base, alt=alt or base, pattern=pattern, trim=trim, number=number, shorts=shorts,
             shorts_trim=trim, socks=socks, sock_trim=trim, badge=(trim, base), stars=0)
    k.update(more)
    return k


_R, _NV, _W, _B = (202, 22, 34), (22, 32, 72), (246, 246, 246), (22, 22, 26)
_GR, _GO = (0, 140, 72), (236, 190, 60)
LB_KITS = {
    "spain": _kit(_R, (250, 200, 24), (250, 200, 24), _NV, _NV, sleeve=_NV),
    "egypt": _kit((206, 22, 36), (206, 22, 36), _W, _B, _B),
    "psg": _kit((24, 30, 74), _W, _W, (24, 30, 74), (24, 30, 74)),
    "city": _kit((108, 172, 222), (28, 44, 92), (28, 44, 92), _W, (108, 172, 222)),
    "lafc": _kit(_B, _GO, _GO, _B, _B, alt=(60, 52, 30), pattern="lines"),
    "betis": _kit(_W, _GR, _B, _W, _GR, alt=_GR, pattern="stripes", number_outline=_W),
    "racing": _kit(_W, _GR, _GR, _B, _W, sleeve=_GR),
    "athletic": _kit(_W, _B, _B, _B, _B, alt=(214, 24, 40), pattern="stripes", number_outline=_W),
    "miami": _kit((245, 180, 204), _B, _B, (245, 180, 204), (245, 180, 204)),
    "juve": _kit(_W, _B, _B, _W, _W, alt=_B, pattern="stripes", number_outline=_W),
    "chelsea": _kit((6, 72, 150), _W, _W, (6, 72, 150), _W),
    "ivory": _kit((247, 127, 0), _GR, _W, _W, (247, 127, 0)),
    "england": _kit(_W, _NV, _NV, _NV, _W),
    "serbia": _kit((198, 30, 42), _W, _W, (12, 64, 118), _W),
    "holland": _kit((245, 112, 22), _B, _B, (245, 112, 22), (245, 112, 22)),
    "argentina": _kit(_W, _NV, _NV, _B, _W, alt=(117, 180, 228), pattern="stripes", number_outline=_W),
    "portugal": _kit((172, 20, 36), (0, 102, 60), _GO, (0, 102, 60), (172, 20, 36)),
    "cameroon_gk": _kit((0, 122, 94), (252, 209, 22), _W, (0, 122, 94), (0, 122, 94)),
    "turkey": _kit((227, 10, 23), _W, _W, _W, (227, 10, 23)),
    "france": _kit((26, 46, 112), _W, _W, _W, (212, 32, 46), placket=(212, 32, 46)),
    "morocco": _kit((182, 22, 32), (0, 112, 62), _W, (0, 112, 62), (182, 22, 32)),
    "germany": _kit(_W, _B, _B, _B, _W),
    "slovenia": _kit(_W, (0, 140, 72), (0, 140, 72), _W, _W),
    # Draft B (31 Oct): national shirts
    "brazil": _kit((250, 214, 30), _GR, _GR, (22, 60, 160), _W),
    "belgium": _kit((200, 16, 34), _GO, _GO, (200, 16, 34), (200, 16, 34)),
    "belgium_gk": _kit((0, 120, 70), _B, _W, (0, 120, 70), (0, 120, 70)),
    "poland": _kit(_W, (214, 20, 40), (214, 20, 40), (214, 20, 40), _W),
    "ecuador": _kit((252, 210, 20), (22, 50, 150), (22, 50, 150), (22, 50, 150), (252, 210, 20)),
    "italy": _kit((22, 84, 180), _W, _W, _W, (22, 84, 180)),
    "croatia": _kit((214, 32, 42), (26, 56, 140), (26, 56, 140), _W, (26, 56, 140), alt=_W, pattern="checks"),
    "uruguay": _kit((110, 176, 230), _W, _B, _B, _B),
    "denmark_gk": _kit(_B, (250, 210, 30), (250, 210, 30), _B, _B),
}
# slug: (skin, hair, head style, facial hair, extras, kit, shirt number)
LB_LOOKS = {
    "yamal": ("brown", "black", "curly", None, (), "spain", 19),
    "salah": ("tan", "black", "long", "full", (), "egypt", 10),
    "dembele": ("dark", "black", "buzz", "stubble", (), "psg", 10),
    "haaland": ("pale", "blond", "bun", None, (), "city", 9),
    "son": ("light", "black", "swept", None, (), "lafc", 7),
    "isco": ("light", "darkbrown", "short", "full", (), "betis", 22),
    "canales": ("light", "brown", "swept", "stubble", (), "racing", 10),
    "yeray": ("light", "darkbrown", "short", "stubble", (), "athletic", 5),
    "suarez": ("light", "darkbrown", "short", "stubble", (), "miami", 9),
    "locatelli": ("light", "darkbrown", "long", "short", (), "juve", 5),
    "bremer": ("brown", "black", "buzz", "short", (), "juve", 3),
    "gusto": ("brown", "black", "twists", None, (), "chelsea", 27),
    "diomande": ("dark", "black", "twists", None, (), "ivory", 11),
    "calhanoglu": ("light", "black", "short", "stubble", (), "turkey", 10),
    "muller": ("pale", "lightbrown", "short", None, (), "germany", 13),
    "palhinha": ("light", "darkbrown", "short", "short", (), "portugal", 6),
    "giroud": ("light", "darkbrown", "swept", "full", (), "france", 9),
    "mitrovic": ("light", "black", "buzz", "full", (), "serbia", 9),
    "depay": ("brown", "black", "bun", "short", (), "holland", 10),
    "correa": ("light", "black", "short", "stubble", (), "argentina", 15),
    "fofana": ("dark", "black", "buzz", "short", (), "france", 19),
    "onana": ("dark", "black", "buzz", None, (), "cameroon_gk", 24),
    "tagliafico": ("light", "darkbrown", "long", "full", (), "argentina", 3),
    "ziyech": ("tan", "black", "fade", "short", (), "morocco", 7),
    "maguire": ("pale", "lightbrown", "short", "stubble", (), "england", 5),
    "tadic": ("light", "darkbrown", "swept", "short", (), "serbia", 10),
    "ilicic": ("pale", "brown", "buzz", "stubble", (), "slovenia", 10),
    "weghorst": ("pale", "blond", "short", "full", (), "holland", 9),
    # Draft B (31 Oct)
    "vannistelrooy": ("pale", "darkbrown", "short", "stubble", (), "holland", 9),
    "raphinha": ("tan", "black", "bun", "stubble", (), "brazil", 11),
    "debruyne": ("pale", "ginger", "swept", None, (), "belgium", 7),
    "lewandowski": ("pale", "darkbrown", "short", None, (), "poland", 9),
    "saliba": ("dark", "black", "curly", None, (), "france", 17),
    "valencia": ("dark", "black", "buzz", "short", (), "ecuador", 16),
    "florenzi": ("light", "darkbrown", "short", "short", (), "italy", 24),
    "gabriel": ("tan", "black", "buzz", "full", (), "brazil", 4),
    "fermin": ("light", "black", "wedge", None, (), "spain", 16),
    "martinelli": ("light", "darkbrown", "curly", None, (), "brazil", 11),
    "sane": ("dark", "black", "buzz", "short", (), "germany", 19),
    "casteels": ("pale", "blond", "short", "stubble", (), "belgium_gk", 1),
    "ansufati": ("brown", "black", "curly", None, (), "spain", 10),
    "modric": ("pale", "brown", "long", None, (), "croatia", 10),
    "griezmann": ("pale", "blond", "swept", "stubble", (), "france", 7),
    "dimaria": ("light", "black", "short", None, (), "argentina", 11),
    "busquets": ("light", "darkbrown", "short", "short", (), "spain", 5),
    "thiagosilva": ("tan", "black", "buzz", "short", (), "brazil", 3),
    "hummels": ("pale", "darkbrown", "swept", "stubble", (), "germany", 5),
    "cavani": ("light", "black", "long", "full", (), "uruguay", 21),
    "reus": ("pale", "blond", "swept", None, (), "germany", 11),
    "casemiro": ("tan", "black", "buzz", "short", (), "brazil", 5),
    "immobile": ("light", "darkbrown", "short", "full", (), "italy", 17),
    "vardy": ("pale", "lightbrown", "swept", None, (), "england", 9),
    "aspas": ("light", "darkbrown", "short", "short", (), "spain", 10),
    "mertens": ("pale", "blond", "short", "stubble", (), "belgium", 14),
    "jordialba": ("light", "darkbrown", "swept", "stubble", (), "spain", 18),
    "schmeichel": ("pale", "blond", "short", "short", (), "denmark_gk", 1),
}


def make_lb_players(out):
    import make_sprites as MS
    for slug, (skin, hair, style, beard, extras, kit_name, num) in LB_LOOKS.items():
        kit = LB_KITS[kit_name]
        sk, hr = MS.SKIN[skin], MS.HAIR[hair]
        boots = MS.STAR_BOOTS[sum(map(ord, slug)) % len(MS.STAR_BOOTS)]
        base = os.path.join(out, "LB_%s" % slug)
        MS.make_head(sk, hr, style, beard, extras).save(base + "_head.png")
        MS.make_torso(kit, num).save(base + "_torso.png")
        MS.make_arm(kit, sk).save(base + "_arm.png")
        MS.make_leg(kit, sk, boots).save(base + "_leg.png")
    return len(LB_LOOKS)


def make_lb_figures(out, force=False, quality=6, only=None):
    """The player on each card. Several minutes for all 28; only missing ones unless force."""
    try:
        import cardfig
        import cards_lb
        import cards_lb2
    except ImportError as exc:
        print("   figures skipped (%s)" % exc)
        return 0
    n = 0
    figs = dict(cards_lb.FIGS)
    figs.update(cards_lb2.FIGS)                                   # Draft B (31 Oct)
    for cid, pose in figs.items():
        path = os.path.join(out, "%s_figure.png" % cid)
        if (only and cid not in only) or (os.path.exists(path) and not force):
            continue
        fig, shot = pose()
        cardfig.flatten(cardfig.render(fig, shot, S=quality)).save(path)
        n += 1
    return n


def main():
    out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "sprites"
    os.makedirs(out, exist_ok=True)
    tpl, frame = lb_frame()
    tpl.save(os.path.join(out, "tpl_lb_card.png"))
    frame.save(os.path.join(out, "tpl_lbframe_card.png"))
    tpl, frame = lb_frame(crystal_on=False)                     # pool C: no crystal
    tpl.save(os.path.join(out, "tpl_lbc_card.png"))
    frame.save(os.path.join(out, "tpl_lbcframe_card.png"))
    for crystal_on, name in ((True, "lb"), (False, "lbc")):     # the two halves the game animates
        _full, back, top = make_lb_template(crystal_on=crystal_on, layers=True)
        back.save(os.path.join(out, "tpl_%sback_card.png" % name))
        top.save(os.path.join(out, "tpl_%stop_card.png" % name))
    make_pack_lb(letter="A").save(os.path.join(out, "pack_5.png"))
    make_pack_lb(seed=23, letter="B").save(os.path.join(out, "pack_6.png"))     # Draft B (31 Oct)
    make_lb_badge().save(os.path.join(out, "lb_badge.png"))
    for code, im in make_flags().items():
        im.save(os.path.join(out, "flag_%s.png" % code))
    try:
        print("match sprites:", make_lb_players(out))
    except ImportError as exc:
        print("   match sprites skipped (%s)" % exc)
    print("card figures:", make_lb_figures(out, force="--figures" in sys.argv))
    print("limit breakers art written to", out)


if __name__ == "__main__":
    main()
