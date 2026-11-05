"""PlayStyle icons, third go (31 Oct) - our own, not EA's.

    python3 make_playstyle_icons.py [out_dir]

Hubi: "rework the playstyles icons". The second set was navy ink on a flat gold hexagon: at
badge size half of them were blobs (a header was a lump, a penalty a box, finesse and whipped
cross the same curve). This set:

  * a cut GEM, not a coin - a hexagon with six bevelled facets on the rim, each lit
    differently, around a DARK face. A bright symbol on a dark face reads at any size.
  * every symbol re-thought to be one idea you get at a glance, drawn big and bold on a 256
    canvas, shrunk to the 32 x 32 grid and snapped to hard pixels, with a one-pixel dark
    outline so it never melts into the face.
  * level 2 is GOLD (gold rim, gold symbol, a glint at the top), level 1 is SILVER.

Writes ps_<key>_p.png (level 3, purple), ps_<key>.png (level 2), ps_<key>_s.png (level 1), ps_<key>_x4.png and playstyles_sheet.png.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

N = 32                     # the pixel grid
S = 256                    # the drawing canvas (8x)
C = S / 2.0

GOLD = dict(rim=[(255, 248, 210), (250, 214, 110), (226, 172, 56), (176, 120, 26), (120, 76, 14)],
            sym=(255, 222, 120), sym_hi=(255, 248, 214), sym_lo=(214, 152, 40),
            face=[(46, 34, 70), (28, 22, 50), (16, 12, 30)], glint=(255, 255, 240))
SILVER = dict(rim=[(255, 255, 255), (222, 230, 244), (178, 190, 214), (124, 136, 166), (72, 82, 110)],
              sym=(226, 236, 252), sym_hi=(255, 255, 255), sym_lo=(150, 166, 200),
              face=[(30, 40, 68), (18, 26, 48), (10, 14, 30)], glint=None)
# 1 Nov: level 3 - only an evolved World's Game card reaches it. Purple, with the gold's glint.
PURPLE = dict(rim=[(250, 226, 255), (214, 150, 255), (170, 88, 240), (118, 44, 190), (70, 18, 120)],
              sym=(226, 170, 255), sym_hi=(252, 236, 255), sym_lo=(150, 70, 220),
              face=[(52, 20, 80), (32, 12, 54), (18, 6, 34)], glint=(255, 244, 255))
OUTLINE = (10, 8, 18)

PLAYSTYLES = [
    ("accelerator", "Accelerator"), ("header", "Precision Header"), ("bullet", "Bullet Pass"),
    ("chip", "Chip Shot"), ("guardian", "Guardian"), ("bruiser", "Bruiser"),
    ("penalty", "Penalty Expert"), ("finesse", "Finesse Expert"), ("relentless", "Relentless"),
    ("rapid", "Rapid"), ("anticipate", "Anticipate"), ("rushout", "Rush Out"),
    ("clinical", "Clinical Finisher"), ("deflector", "Deflector"), ("power", "Power Shot"),
    ("whipped", "Whipped Cross"), ("tikitaka", "Tiki Taka"), ("trickster", "Trickster"),
]


# ---------------------------------------------------------------- drawing helpers (256 canvas)
def hexagon(cx, cy, r, rot=-90):
    return [(cx + r * math.cos(math.radians(rot + 60 * i)), cy + r * math.sin(math.radians(rot + 60 * i)))
            for i in range(6)]


def arc_pts(cx, cy, rx, ry, a0, a1, n=48):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def thick(d, pts, w, fill=255):
    d.line(pts, fill=fill, width=int(w), joint="curve")
    r = w / 2.0
    for x, y in (pts[0], pts[-1]):
        d.ellipse([x - r, y - r, x + r, y + r], fill=fill)


def arrowhead(d, tip, ang, size, fill=255):
    a = math.radians(ang)
    bx, by = tip[0] - math.cos(a) * size, tip[1] - math.sin(a) * size
    px, py = -math.sin(a) * size * 0.62, math.cos(a) * size * 0.62
    d.polygon([tip, (bx + px, by + py), (bx - px, by - py)], fill=fill)


def ball(d, x, y, r, fill=255, cut=0):
    """A football: a disc with the pentagon patch cut out of it (cut = the face colour)."""
    d.ellipse([x - r, y - r, x + r, y + r], fill=fill)
    d.polygon([(x + r * 0.40 * math.cos(math.radians(-90 + 72 * i)),
               y + r * 0.40 * math.sin(math.radians(-90 + 72 * i))) for i in range(5)], fill=cut)


def star(cx, cy, r1, r2, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        a = math.radians(rot + 180.0 / n * i)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


SYM = {}


def sym(key):
    def deco(fn):
        SYM[key] = fn
        return fn
    return deco


# ---------------------------------------------------------------- the eighteen symbols
@sym("accelerator")                      # >> : two big chevrons and speed lines - sprint
def _(d):
    for x in (96, 156):
        thick(d, [(x - 34, 70), (x + 14, 128), (x - 34, 186)], 30)
    for y, x0 in ((88, 20), (128, 8), (168, 20)):
        thick(d, [(x0, y), (x0 + 38, y)], 16)


@sym("header")                           # the ball landing on his head, a flash either side
def _(d):
    d.ellipse([70, 130, 186, 246], fill=255)                    # the head
    d.ellipse([92, 176, 112, 196], fill=0)                      # eyes
    d.ellipse([144, 176, 164, 196], fill=0)
    ball(d, 128, 58, 50)
    for sx in (-1, 1):                                          # impact lines
        thick(d, [(128 + sx * 62, 112), (128 + sx * 104, 86)], 14)
        thick(d, [(128 + sx * 70, 138), (128 + sx * 116, 132)], 12)


@sym("bullet")                           # a ball and a long dead-straight trail
def _(d):
    ball(d, 184, 128, 46)
    for y, x0, w in ((96, 30, 18), (128, 10, 22), (160, 30, 18)):
        thick(d, [(x0, y), (128, y)], w)


@sym("chip")                             # one big lob over a defender, dropping in
def _(d):
    d.rectangle([44, 150, 82, 240], fill=255)                  # the defender
    d.ellipse([40, 104, 86, 150], fill=255)
    pts = arc_pts(150, 236, 128, 196, 196, 336, 40)
    thick(d, pts, 26)
    arrowhead(d, pts[-1], 70, 50)
    ball(d, 30, 226, 26)

@sym("guardian")                         # a shield with a ball held safe inside it
def _(d):
    d.polygon([(128, 20), (222, 52), (210, 150), (128, 236), (46, 150), (34, 52)], fill=255)
    d.polygon([(128, 50), (194, 72), (186, 144), (128, 206), (70, 144), (62, 72)], fill=0)
    ball(d, 128, 124, 42)


@sym("bruiser")                          # a fist, knuckles forward, with impact bursts
def _(d):
    d.rounded_rectangle([60, 70, 176, 176], 22, fill=255)                  # the fist
    d.rounded_rectangle([86, 166, 156, 224], 12, fill=255)                 # wrist
    for y in (100, 130):                                                    # finger creases
        d.line([(66, y), (150, y)], fill=0, width=8)
    d.rounded_rectangle([132, 120, 186, 166], 14, fill=255)                # thumb
    for a in (-40, 0, 40):
        x, y = 196 + 22 * math.cos(math.radians(a)), 120 + 40 * math.sin(math.radians(a))
        thick(d, [(x, y), (x + 34 * math.cos(math.radians(a)), y + 34 * math.sin(math.radians(a)))], 14)


@sym("penalty")                          # the goal, and the ball on the spot below it
def _(d):
    thick(d, [(36, 150), (36, 50), (220, 50), (220, 150)], 18)
    for x in (82, 128, 174):                                                # the net
        d.line([(x, 56), (x, 146)], fill=255, width=6)
    d.line([(42, 100), (214, 100)], fill=255, width=6)
    ball(d, 128, 200, 36)
    thick(d, [(76, 240), (180, 240)], 10)                                   # the spot / line


@sym("finesse")                          # a curling arrow bending into the top corner
def _(d):
    thick(d, [(150, 44), (232, 44), (232, 130)], 14)                       # top corner of a goal
    pts = arc_pts(196, 210, 160, 150, 192, 266, 40)
    thick(d, pts, 26)
    arrowhead(d, (206, 66), -18, 52)
    ball(d, 46, 206, 28)


@sym("relentless")                       # a flame - he never stops
def _(d):
    d.polygon([(128, 18), (178, 92), (206, 154), (190, 210), (128, 240), (66, 210), (50, 154),
               (86, 118), (96, 152), (112, 80)], fill=255)
    d.polygon([(128, 116), (156, 166), (152, 206), (128, 222), (104, 206), (102, 172)], fill=0)


@sym("rapid")                            # a lightning bolt with the ball at its foot
def _(d):
    d.polygon([(150, 14), (70, 132), (124, 132), (96, 236), (190, 104), (134, 104), (176, 14)], fill=255)
    ball(d, 196, 206, 32)


@sym("anticipate")                       # an eye - he reads it before it happens
def _(d):
    r, h = 132.0, 72.0                                          # a lens: two circles, centres above and below
    xs = range(14, 243, 4)
    top = [(x, 128 + h - math.sqrt(max(0.0, r * r - (x - 128) ** 2))) for x in xs]
    bot = [(x, 128 - h + math.sqrt(max(0.0, r * r - (x - 128) ** 2))) for x in xs][::-1]
    d.polygon(top + bot, fill=255)
    d.ellipse([80, 80, 176, 176], fill=0)
    d.ellipse([96, 96, 160, 160], fill=255)
    d.ellipse([114, 114, 142, 142], fill=0)


@sym("rushout")                          # a keeper's glove flying forward, motion lines behind
def _(d):
    d.rounded_rectangle([104, 70, 210, 196], 30, fill=255)                 # palm
    for i, x in enumerate((110, 136, 162, 188)):                           # fingers
        d.rounded_rectangle([x, 26 + (6 if i in (0, 3) else 0), x + 22, 100], 11, fill=255)
    d.rounded_rectangle([70, 112, 124, 152], 18, fill=255)                 # thumb
    d.rectangle([120, 196, 196, 230], fill=255)                            # cuff
    for y, x0 in ((90, 14), (132, 4), (174, 14)):
        thick(d, [(x0, y), (x0 + 48, y)], 14)


@sym("clinical")                         # cross-hairs with the ball dead centre
def _(d):
    d.ellipse([28, 28, 228, 228], fill=255)
    d.ellipse([52, 52, 204, 204], fill=0)
    for a, b in (((128, 6), (128, 70)), ((128, 186), (128, 250)), ((6, 128), (70, 128)), ((186, 128), (250, 128))):
        thick(d, [a, b], 18)
    ball(d, 128, 128, 40)


@sym("deflector")                        # a palm, and the ball glancing off it up and away
def _(d):
    d.rounded_rectangle([30, 110, 120, 220], 26, fill=255)
    for i, x in enumerate((34, 56, 78, 100)):
        d.rounded_rectangle([x, 62 + (8 if i in (0, 3) else 0), x + 18, 130], 9, fill=255)
    pts = arc_pts(150, 180, 70, 120, 200, 300, 30)
    thick(d, pts, 18)
    arrowhead(d, pts[-1], -70, 40)
    ball(d, 204, 192, 28)


@sym("power")                            # a ball exploding out of a burst
def _(d):
    d.polygon(star(128, 128, 122, 70, 8, -90), fill=255)
    d.ellipse([70, 70, 186, 186], fill=0)
    ball(d, 128, 128, 48)


@sym("whipped")                          # the cross: whipped from the wing, curling down into the box
def _(d):
    pts = arc_pts(30, 214, 196, 176, -84, -4, 40)
    thick(d, pts, 36)
    arrowhead(d, (228, 236), 96, 64)
    ball(d, 44, 46, 40)

@sym("tikitaka")                         # three men, passes round the triangle
def _(d):
    pts = [(128, 44), (218, 204), (38, 204)]
    for i in range(3):
        a, b = pts[i], pts[(i + 1) % 3]
        thick(d, [a, b], 14)
    for x, y in pts:
        d.ellipse([x - 32, y - 32, x + 32, y + 32], fill=255)
        d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=0)


@sym("trickster")                        # a spin move: an arrow all the way round the ball
def _(d):
    pts = arc_pts(128, 128, 96, 96, -60, 230, 60)
    thick(d, pts, 24)
    arrowhead(d, pts[-1], 230 + 90, 56)
    ball(d, 128, 128, 44)


# ---------------------------------------------------------------- the gem
def to_grid(mask, cut=0.45):
    small = mask.resize((N, N), Image.BOX)
    return small.point(lambda v: 255 if v >= cut * 255 else 0)


def mask_of(poly):
    big = Image.new("L", (S, S), 0)
    ImageDraw.Draw(big).polygon(poly, fill=255)
    return to_grid(big, 0.5)


def icon(key, pal):
    outer = mask_of(hexagon(C - 0.5, C - 0.5, S * 0.49)).load()
    face = mask_of(hexagon(C - 0.5, C - 0.5, S * 0.36)).load()
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    px = im.load()
    cx = cy = (N - 1) / 2.0
    for y in range(N):
        for x in range(N):
            if not outer[x, y]:
                continue
            edge = any(not (0 <= x + dx < N and 0 <= y + dy < N and outer[x + dx, y + dy])
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if edge:
                px[x, y] = OUTLINE + (255,)
            elif face[x, y]:                                      # the dark face, a little light at the top
                t = (y + 0.6 * x) / (1.6 * N)
                px[x, y] = pal["face"][0 if t < 0.30 else 1 if t < 0.62 else 2] + (255,)
            else:                                                 # the rim: six facets, lit from the top left
                a = (math.degrees(math.atan2(y - cy, x - cx)) + 360 + 30) % 360
                facet = int(a // 60)                              # 0 = right ... going clockwise
                shade = {4: 0, 3: 1, 5: 1, 2: 2, 0: 3, 1: 4}[facet]
                px[x, y] = pal["rim"][shade] + (255,)
    # a dark seam where the facets meet the face
    for y in range(N):
        for x in range(N):
            if face[x, y] and any(not face[x + dx, y + dy] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                                  if 0 <= x + dx < N and 0 <= y + dy < N):
                px[x, y] = OUTLINE + (255,)
    # the symbol: drawn big, shrunk into the face, outlined, lit top-left
    big = Image.new("L", (S, S), 0)
    SYM[key](ImageDraw.Draw(big))
    big = big.resize((int(S * 0.58), int(S * 0.58)), Image.LANCZOS)
    canvas = Image.new("L", (S, S), 0)
    canvas.paste(big, ((S - big.width) // 2, (S - big.height) // 2))
    m = to_grid(canvas).load()
    for y in range(N):
        for x in range(N):
            if m[x, y] or not face[x, y]:
                continue
            if any(0 <= x + dx < N and 0 <= y + dy < N and m[x + dx, y + dy]
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = OUTLINE + (255,)                     # the symbol's outline
    for y in range(N):
        for x in range(N):
            if not m[x, y] or not outer[x, y]:
                continue
            up = y > 0 and not m[x, y - 1]
            left = x > 0 and not m[x - 1, y]
            down = y < N - 1 and not m[x, y + 1]
            col = pal["sym_hi"] if (up or left) else pal["sym_lo"] if down else pal["sym"]
            px[x, y] = col + (255,)
    if pal["glint"]:                                             # level 2: a glint on the top-left facet
        for gx, gy in ((9, 6), (10, 5), (8, 7), (10, 7)):
            if 0 <= gx < N and outer[gx, gy] and not face[gx, gy]:
                px[gx, gy] = pal["glint"] + (255,)
    return im


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "playstyle_icons"
    os.makedirs(out, exist_ok=True)
    icons = {}
    for key, _name in PLAYSTYLES:
        gold, silver = icon(key, GOLD), icon(key, SILVER)
        icons[key] = (gold, silver)
        gold.save(os.path.join(out, "ps_%s.png" % key))                     # level 2
        icon(key, PURPLE).save(os.path.join(out, "ps_%s_p.png" % key))       # level 3 (1 Nov)
        silver.save(os.path.join(out, "ps_%s_s.png" % key))                 # level 1
        gold.resize((N * 4, N * 4), Image.NEAREST).save(os.path.join(out, "ps_%s_x4.png" % key))
    cols, cw, ch, z = 6, 300, 250, 5
    rows = (len(PLAYSTYLES) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw + 40, rows * ch + 120), (14, 16, 28))
    sd = ImageDraw.Draw(sheet)
    try:
        f_t = ImageFont.truetype("DejaVuSans-Bold.ttf", 42)
        f_n = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
    except OSError:
        f_t = f_n = ImageFont.load_default()
    sd.text((40, 30), "PLAYSTYLES  -  gold = level 2, silver = level 1", fill=(240, 232, 210), font=f_t)
    for i, (key, name) in enumerate(PLAYSTYLES):
        x, y = 20 + (i % cols) * cw, 110 + (i // cols) * ch
        for j, im in enumerate(icons[key]):
            big = im.resize((N * z, N * z), Image.NEAREST) if j == 0 else im.resize((N * 3, N * 3), Image.NEAREST)
            sheet.paste(big, (x + 10 + j * 170, y + (0 if j == 0 else 30)), big)
        tw = sd.textlength(name, font=f_n)
        sd.text((x + (cw - tw) / 2, y + N * z + 12), name, fill=(232, 228, 214), font=f_n)
    sheet.save(os.path.join(out, "playstyles_sheet.png"))
    print("wrote %d icons (gold + silver) + sheet to %s" % (len(icons), out))


if __name__ == "__main__":
    main()
