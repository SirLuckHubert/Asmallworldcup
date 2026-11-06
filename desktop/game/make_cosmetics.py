"""SEASON 1 cosmetics (6 Nov): profile pictures and ball skins, all this game's own pixel art.

    python3 make_cosmetics.py [out_dir]

Hubi sent fan art and photos to use as profile pictures. Those belong to other people (two signed
drawings of Sega's characters, two press photos with club crests, two branded match balls), so none
of it is used or traced. Everything here is drawn from code: plain shapes on a 32 x 32 grid, a dark
outline round every shape, scaled 4x with no smoothing so it sits with the rest of the pixel art.

  pfp_<key>.png              128 x 128, a round badge (the PFP list in ragdoll_football.py)
  pfp_owner_live.png         the animated owner picture: 12 frames of 128 x 128 side by side
  pfp_owner_live.gif         the same frames as a GIF (for the site, not used by the game)
  ball_<key>.png             240 x 240, the match ball re-coloured on its own 24 x 24 grid
  cosmetics_preview.png      everything on one sheet (not used by the game)
"""
import math
import os
import sys

from PIL import Image, ImageDraw

N = 32                    # the picture grid
UP = 4                    # 32 -> 128
INK = (16, 14, 26, 255)

# ---------------------------------------------------------------- a tiny pixel font (3 x 5 / 5 x 7)
GLYPHS = {
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "1": ["00100", "01100", "10100", "00100", "00100", "00100", "11111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
}


def text(im, s, x, y, col, k=1, gap=1):
    px = im.load()
    for ch in s:
        g = GLYPHS[ch]
        for j, row in enumerate(g):
            for i, b in enumerate(row):
                if b == "1":
                    for a in range(k):
                        for c in range(k):
                            px[x + i * k + a, y + j * k + c] = col
        x += (len(g[0]) + gap) * k


# ---------------------------------------------------------------- helpers on the 32 grid
def new():
    return Image.new("RGBA", (N, N), (0, 0, 0, 0))


def outline(im, col=INK):
    """A one-pixel dark edge round everything opaque (the look of every sprite in the game)."""
    src = im.load()
    out = im.copy()
    o = out.load()
    for y in range(N):
        for x in range(N):
            if src[x, y][3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                u, v = x + dx, y + dy
                if 0 <= u < N and 0 <= v < N and src[u, v][3] > 0:
                    o[x, y] = col
                    break
    return out


def disc(r, c0, c1, ring, cx=15.5, cy=15.5):
    """The badge: a filled circle, lighter at the top, with a metal ring."""
    im = new()
    px = im.load()
    for y in range(N):
        for x in range(N):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                t = y / float(N - 1)
                col = tuple(int(c0[i] * (1 - t) + c1[i] * t) for i in range(3)) + (255,)
                if d > r - 2:
                    col = ring + (255,)
                elif d > r - 3:
                    col = tuple(max(0, int(v * 0.55)) for v in ring) + (255,)
                px[x, y] = col
    return im


def put(base, art, dx=0, dy=0):
    base.alpha_composite(art, (dx, dy))
    return base


def finish(im):
    return im.resize((N * UP, N * UP), Image.NEAREST)


def shape(draw_fn):
    im = new()
    draw_fn(ImageDraw.Draw(im), im)
    return outline(im)


# rarity looks: inner colours top/bottom + the ring
LOOK = {
    "common": ((70, 120, 210), (24, 44, 110), (170, 200, 255)),
    "rare": ((150, 80, 230), (54, 20, 110), (220, 180, 255)),
    "epic": ((240, 170, 50), (120, 60, 10), (255, 230, 150)),
    "season": ((40, 190, 170), (8, 60, 70), (150, 255, 230)),
    "owner": ((220, 40, 60), (70, 6, 20), (255, 210, 90)),
    "pitch": ((70, 190, 90), (20, 90, 40), (200, 255, 200)),
}


def badge(kind):
    c0, c1, ring = LOOK[kind]
    return disc(15, c0, c1, ring)


# ---------------------------------------------------------------- the ball, as a 24 x 24 grid
BALL_KEYS = {(244, 246, 250): "w", (30, 30, 40): "p", (20, 20, 28): "o", (198, 206, 218): "s",
             (255, 255, 255): "h"}


def ball_grid(sprites):
    raw = Image.open(os.path.join(sprites, "ball.png")).convert("RGBA")
    g = []
    for y in range(24):
        row = ""
        for x in range(24):
            p = raw.getpixel((x * 10 + 5, y * 10 + 5))
            row += "." if p[3] == 0 else BALL_KEYS.get(p[:3], "w")
        g.append(row)
    return g


def paint_ball(grid, pal, extra=None):
    im = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    px = im.load()
    for y, row in enumerate(grid):
        for x, k in enumerate(row):
            if k != ".":
                px[x, y] = pal[k] + (255,)
    if extra:
        extra(im, grid)
    return im


BALL_SKINS = {
    # key: the five colours - white panels, patches, outline, shade, highlight
    "classic": dict(w=(244, 246, 250), p=(30, 30, 40), o=(20, 20, 28), s=(198, 206, 218), h=(255, 255, 255)),
    "ember": dict(w=(255, 160, 50), p=(150, 20, 16), o=(50, 8, 6), s=(220, 90, 30), h=(255, 236, 150)),
    "night": dict(w=(26, 30, 52), p=(40, 240, 230), o=(6, 8, 18), s=(16, 18, 36), h=(150, 255, 250)),
    "frost": dict(w=(214, 240, 255), p=(70, 150, 230), o=(20, 40, 80), s=(150, 196, 236), h=(255, 255, 255)),
    "gold": dict(w=(250, 210, 90), p=(140, 84, 14), o=(60, 34, 6), s=(206, 150, 40), h=(255, 248, 210)),
    "galaxy": dict(w=(96, 52, 176), p=(28, 14, 70), o=(8, 4, 20), s=(66, 34, 130), h=(230, 206, 255)),
    "s1": dict(w=(30, 200, 176), p=(250, 214, 110), o=(6, 40, 44), s=(16, 140, 130), h=(220, 255, 246)),
}


def galaxy_stars(im, grid):
    px = im.load()
    for x, y in ((6, 6), (16, 4), (19, 12), (4, 14), (11, 18), (17, 19), (9, 10), (14, 14)):
        if grid[y][x] in "ws":
            px[x, y] = (255, 255, 255, 255)
    for x, y in ((7, 6), (15, 4), (20, 12)):
        if grid[y][x] in "ws":
            px[x, y] = (190, 160, 255, 255)


def ember_flecks(im, grid):
    px = im.load()
    for x, y in ((5, 15), (8, 19), (15, 18), (19, 9), (12, 3)):
        if grid[y][x] in "ws":
            px[x, y] = (255, 236, 150, 255)


EXTRA = {"galaxy": galaxy_stars, "ember": ember_flecks}


# ---------------------------------------------------------------- the profile pictures
def pfp_ball(grid):
    im = badge("pitch")
    b = paint_ball(grid, BALL_SKINS["classic"])
    return put(im, b, 4, 4)


def pfp_doll():
    """The game's own little player: head on top, ARM-TORSO-ARM, legs under."""
    im = badge("common")

    def d(dr, _im):
        dr.rectangle((11, 15, 20, 23), fill=(230, 60, 60, 255))          # the shirt (torso)
        dr.rectangle((7, 16, 10, 18), fill=(230, 60, 60, 255))           # arm, left of the torso
        dr.rectangle((21, 16, 24, 18), fill=(230, 60, 60, 255))          # arm, right of the torso
        dr.rectangle((7, 19, 9, 20), fill=(240, 196, 150, 255))
        dr.rectangle((22, 19, 24, 20), fill=(240, 196, 150, 255))
        dr.rectangle((12, 24, 14, 27), fill=(250, 250, 255, 255))         # legs
        dr.rectangle((17, 24, 19, 27), fill=(250, 250, 255, 255))
        dr.ellipse((10, 4, 21, 14), fill=(240, 196, 150, 255))            # the head
        dr.rectangle((10, 4, 21, 6), fill=(70, 40, 20, 255))              # hair
        dr.point([(13, 9), (18, 9)], fill=INK)                            # eyes
        dr.line([(14, 12), (17, 12)], fill=(150, 70, 60, 255))            # a smile
        dr.rectangle((15, 17, 16, 20), fill=(255, 255, 255, 255))         # number 1
    return put(im, shape(d))


def pfp_whistle():
    im = badge("common")

    def d(dr, _im):
        dr.arc((5, 4, 17, 18), 150, 330, fill=(250, 90, 90, 255), width=2)   # the lanyard
        dr.ellipse((11, 14, 23, 25), fill=(210, 218, 232, 255))           # the body
        dr.rectangle((19, 13, 27, 17), fill=(210, 218, 232, 255))         # the mouthpiece
        dr.ellipse((14, 17, 18, 21), fill=(60, 70, 90, 255))              # the hole
        dr.point([(13, 16), (14, 15), (20, 14)], fill=(255, 255, 255, 255))
    return put(im, shape(d))


def pfp_s1(gold=False):
    im = badge("epic" if gold else "season")
    t = new()
    text(t, "S1", 6, 11, (255, 236, 160, 255) if gold else (255, 255, 255, 255), k=2, gap=0)
    t = outline(t)
    put(im, t)
    st = shape(lambda dr, _i: dr.polygon(star_pts(16, 6, 3.2, 1.4), fill=(255, 214, 90, 255)))
    return put(im, st)


def star_pts(cx, cy, ro, ri, rot=-math.pi / 2):
    pts = []
    for k in range(10):
        r = ro if k % 2 == 0 else ri
        a = rot + k * math.pi / 5
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def pfp_boot():
    im = badge("epic")

    def d(dr, _im):
        g, lit, dark = (240, 186, 60, 255), (255, 236, 150, 255), (170, 110, 20, 255)
        dr.polygon([(9, 8), (16, 8), (17, 17), (25, 19), (26, 23), (7, 23), (8, 15)], fill=g)
        dr.rectangle((7, 23, 26, 24), fill=dark)                           # the sole
        for sx in (9, 13, 18, 23):
            dr.point((sx, 25), fill=dark)                                  # studs
        dr.line([(10, 10), (10, 15)], fill=lit)
        dr.line([(12, 14), (16, 14)], fill=(255, 255, 255, 255))          # laces
        dr.line([(12, 16), (17, 16)], fill=(255, 255, 255, 255))
        dr.line([(18, 19), (23, 20)], fill=lit)
    return put(im, shape(d))


def pfp_glove():
    im = badge("common")

    def d(dr, _im):
        body, cuff, grip = (120, 230, 120, 255), (30, 60, 140, 255), (250, 250, 250, 255)
        for i, (x, top) in enumerate(((9, 9), (13, 6), (17, 6), (21, 8))):
            dr.rectangle((x, top, x + 2, 16), fill=body)                   # four fingers
        dr.polygon([(5, 14), (8, 12), (10, 17), (8, 19)], fill=body)       # the thumb
        dr.rectangle((8, 15, 23, 22), fill=body)                           # the palm
        dr.rectangle((9, 23, 22, 27), fill=cuff)                           # the strap
        dr.rectangle((12, 17, 19, 20), fill=grip)
        dr.line([(10, 24), (21, 24)], fill=(90, 130, 230, 255))
    return put(im, shape(d))


def pfp_net(grid):
    im = badge("rare")

    def d(dr, _im):
        post = (250, 250, 255, 255)
        for x in range(9, 26, 3):
            dr.line([(x, 9), (x, 25)], fill=(150, 130, 200, 255))          # the net
        for y in range(11, 26, 3):
            dr.line([(8, y), (26, y)], fill=(150, 130, 200, 255))
        dr.rectangle((6, 7, 27, 8), fill=post)                             # crossbar
        dr.rectangle((6, 7, 7, 26), fill=post)                             # posts
        dr.rectangle((26, 7, 27, 26), fill=post)
    im = put(im, shape(d))
    small = paint_ball(grid, BALL_SKINS["classic"]).resize((10, 10), Image.NEAREST)
    return put(im, small, 16, 9)                                            # top bins


def pfp_flame(grid):
    im = badge("epic")

    def d(dr, _im):
        dr.polygon([(16, 2), (21, 9), (24, 6), (27, 14), (26, 22), (6, 22), (5, 14), (8, 8), (11, 11)],
                   fill=(255, 90, 30, 255))
        dr.polygon([(16, 7), (20, 13), (23, 11), (24, 18), (8, 18), (9, 13), (12, 14)], fill=(255, 190, 60, 255))
    im = put(im, shape(d))
    b = paint_ball(grid, BALL_SKINS["ember"]).resize((16, 16), Image.NEAREST)
    return put(im, b, 8, 12)


def pfp_crown():
    im = badge("epic")

    def d(dr, _im):
        g, lit = (250, 200, 70, 255), (255, 244, 190, 255)
        dr.polygon([(6, 22), (6, 10), (11, 16), (16, 7), (21, 16), (26, 10), (26, 22)], fill=g)
        dr.rectangle((6, 21, 26, 24), fill=(200, 140, 30, 255))
        for cx, col in ((11, (230, 50, 60, 255)), (16, (60, 140, 255, 255)), (21, (230, 50, 60, 255))):
            dr.rectangle((cx - 1, 21, cx, 23), fill=col)                   # the jewels
        dr.line([(7, 12), (7, 19)], fill=lit)
        dr.point([(16, 8), (6, 10), (26, 10)], fill=(255, 255, 255, 255))
    return put(im, shape(d))


def pfp_bolt():
    im = badge("rare")

    def d(dr, _im):
        dr.polygon([(19, 3), (8, 18), (15, 18), (11, 29), (25, 12), (17, 12), (22, 3)], fill=(255, 236, 80, 255))
        dr.line([(18, 5), (11, 16)], fill=(255, 255, 220, 255))
    return put(im, shape(d))


def pfp_star():
    im = badge("rare")
    st = shape(lambda dr, _i: (dr.polygon(star_pts(16, 17, 12, 5), fill=(255, 210, 70, 255)),
                               dr.polygon(star_pts(16, 17, 6, 2.6), fill=(255, 240, 170, 255))))
    return put(im, st)


def pfp_cup():
    """A trophy of this game's own shape: a round bowl, two loop handles, a stepped base."""
    im = badge("epic")

    def d(dr, _im):
        g, lit, dark = (250, 200, 70, 255), (255, 244, 190, 255), (180, 120, 24, 255)
        dr.ellipse((5, 8, 11, 16), outline=g, width=2)                    # handles
        dr.ellipse((21, 8, 27, 16), outline=g, width=2)
        dr.pieslice((8, 0, 24, 20), 0, 180, fill=g)                         # the bowl
        dr.rectangle((8, 6, 24, 10), fill=g)
        dr.rectangle((15, 19, 17, 22), fill=dark)                           # the stem
        dr.rectangle((11, 23, 21, 24), fill=g)
        dr.rectangle((9, 25, 23, 27), fill=dark)
        dr.line([(11, 8), (11, 14)], fill=lit)
        dr.point((13, 16), fill=lit)
    return put(im, shape(d))


def pfp_owner():
    """THE OWNER (still): a red shield, a gold crown on it and a big gold H - the game is Hubi's."""
    im = badge("owner")

    def d(dr, _im):
        dr.polygon([(8, 9), (24, 9), (24, 19), (16, 27), (8, 19)], fill=(150, 14, 30, 255))   # the shield
        dr.polygon([(9, 10), (23, 10), (23, 18), (16, 25), (9, 18)], outline=(255, 210, 90, 255))
        g = (255, 214, 90, 255)
        dr.polygon([(9, 8), (9, 3), (12, 6), (16, 1), (20, 6), (23, 3), (23, 8)], fill=g)    # the crown
        dr.point([(16, 2), (9, 3), (23, 3)], fill=(255, 255, 255, 255))
    im = put(im, shape(d))
    t = new()
    text(t, "H", 14, 12, (255, 220, 110, 255), k=1)
    for y in range(12, 19):                                                  # make the H bold
        for x in range(14, 19):
            if t.getpixel((x, y))[3]:
                t.putpixel((x - 1, y), (255, 220, 110, 255))
    return put(im, outline(t, (90, 6, 16, 255)))


def pfp_owner_live(grid, frames=12):
    """THE OWNER (live): the owner's crown over a ball that spins in a ring of gold light, sparks
    running round it and the badge's red pulsing. 12 frames, looping."""
    out = []
    ball = paint_ball(grid, BALL_SKINS["gold"]).resize((16, 16), Image.NEAREST)
    for f in range(frames):
        t = f / float(frames)
        pulse = 0.5 + 0.5 * math.sin(t * math.tau)
        c0 = (int(200 + 50 * pulse), int(30 + 30 * pulse), int(50 + 20 * pulse))
        im = disc(15, c0, (70, 6, 20), (255, int(190 + 50 * pulse), 90))
        # the ring of light: an ellipse, its bright part running round
        ring = new()
        rp = ring.load()
        for k in range(48):
            a = k / 48.0 * math.tau
            x, y = 16 + math.cos(a) * 11.5, 19 + math.sin(a) * 4.5
            run = (math.cos(a - t * math.tau) + 1) / 2
            col = (255, int(200 + 55 * run), int(80 + 150 * run), int(120 + 135 * run))
            xi, yi = int(round(x)), int(round(y))
            for yy in (yi, yi + 1):
                if 0 <= xi < N and 0 <= yy < N:
                    rp[xi, yy] = col
        # the back half of the ring goes behind the ball
        back, front = new(), new()
        for y in range(N):
            for x in range(N):
                p = rp[x, y]
                if p[3]:
                    (back if y < 19 else front).putpixel((x, y), p)
        im.alpha_composite(back)
        shiny = ball.copy()                                # a band of light sweeping across it
        bp = shiny.load()
        sweep = -6 + 28 * t
        for y in range(16):
            for x in range(16):
                p = bp[x, y]
                if p[3] and abs((x + y * 0.6) - sweep) < 1.6:
                    bp[x, y] = (255, 252, 230, 255)
        im.alpha_composite(outline_small(shiny), (7, 10))
        im.alpha_composite(front)
        # the crown, bobbing
        crown = new()
        dr = ImageDraw.Draw(crown)
        bob = int(round(math.sin(t * math.tau) * 1.0))
        g = (255, 214, 90, 255)
        dr.polygon([(10, 9 + bob), (10, 4 + bob), (13, 7 + bob), (16, 2 + bob), (19, 7 + bob), (22, 4 + bob),
                    (22, 9 + bob)], fill=g)
        dr.point([(16, 3 + bob)], fill=(255, 255, 255, 255))
        im.alpha_composite(outline(crown))
        # sparks: four, going round the outside
        sp = im.load()
        for s in range(4):
            a = t * math.tau + s * math.pi / 2
            x, y = int(round(16 + math.cos(a) * 13)), int(round(16 + math.sin(a) * 13))
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                u, v = x + dx, y + dy
                if 0 <= u < N and 0 <= v < N:
                    sp[u, v] = (255, 255, 230, 255) if (dx, dy) == (0, 0) else (255, 214, 90, 255)
        out.append(finish(im))
    return out


def outline_small(im):
    """outline() for a picture smaller than the grid."""
    big = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    big.alpha_composite(im, (2, 2))
    big = outline(big)
    return big.crop((1, 1, im.width + 3, im.height + 3))


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "sprites")
    sprites = out if os.path.exists(os.path.join(out, "ball.png")) else os.path.join(here, "sprites")
    os.makedirs(out, exist_ok=True)
    grid = ball_grid(sprites)
    pfps = {
        "ball": pfp_ball(grid), "doll": pfp_doll(), "whistle": pfp_whistle(), "s1": pfp_s1(),
        "boot": pfp_boot(), "glove": pfp_glove(), "net": pfp_net(grid), "flame": pfp_flame(grid),
        "crown": pfp_crown(), "bolt": pfp_bolt(), "star": pfp_star(), "cup": pfp_cup(),
        "s1gold": pfp_s1(gold=True), "owner": pfp_owner(),
    }
    for k, im in pfps.items():
        finish(im).save(os.path.join(out, "pfp_%s.png" % k))
    live = pfp_owner_live(grid)
    sheet = Image.new("RGBA", (128 * len(live), 128), (0, 0, 0, 0))
    for i, fr in enumerate(live):
        sheet.paste(fr, (i * 128, 0))
    sheet.save(os.path.join(out, "pfp_owner_live.png"))
    gif = [fr.resize((256, 256), Image.NEAREST) for fr in live]
    gif[0].save(os.path.join(here, "pfp_owner_live.gif"), save_all=True, append_images=gif[1:], duration=90,
                loop=0, disposal=2)
    balls = {}
    for k, pal in BALL_SKINS.items():
        if k == "classic":
            continue
        b = paint_ball(grid, pal, EXTRA.get(k)).resize((240, 240), Image.NEAREST)
        b.save(os.path.join(out, "ball_%s.png" % k))
        balls[k] = b
    # the preview sheet
    items = [finish(v) for v in pfps.values()] + [live[0], live[4]] + [b.resize((128, 128), Image.NEAREST)
                                                                        for b in balls.values()]
    cols = 8
    rows = (len(items) + cols - 1) // cols
    prev = Image.new("RGBA", (cols * 144 + 16, rows * 144 + 16), (20, 24, 40, 255))
    for i, it in enumerate(items):
        prev.alpha_composite(it, (16 + (i % cols) * 144, 16 + (i // cols) * 144))
    prev.save(os.path.join(here, "cosmetics_preview.png"))
    print("%d pictures, 1 animated (%d frames), %d ball skins -> %s" % (len(pfps), len(live), len(balls), out))


if __name__ == "__main__":
    main()
