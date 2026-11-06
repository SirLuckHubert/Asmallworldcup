"""PlayStyle icons, fourth go (6 Nov) - medallions. Our own design, not EA's.

    python3 make_playstyle_icons.py [out_dir]

Hubi: "make the playstyles icon look better" - and he picked a round medallion: a coin with a
thick metal rim (silver / gold / purple for the level) and ONE big symbol filling the face.

  * 64 x 64 hard pixels (the old set was 32): drawn on a 256 canvas, shrunk, snapped to the
    grid, with a one-pixel ink outline round every shape so nothing melts at badge size.
  * the rim is a real coin edge: lit from the top left, shadowed bottom right, with milled ticks.
  * the face is dark enamel, so a bright symbol reads at any size.
  * each symbol is the thing you SEE on the pitch when that PlayStyle fires (6 Nov rework), in
    the same colour as its trail: Finesse's blue curl into the top corner, Power Shot's fireball,
    Clinical's red crosshair, Chip's lob over the bar... the badge and the effect are one idea.
  * gold gets a glint on the rim, purple a glint and two sparkles.

Writes ps_<key>.png (level 2, gold), ps_<key>_s.png (level 1, silver), ps_<key>_p.png (level 3,
purple), ps_<key>_x4.png and playstyles_sheet.png.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

N = 64                    # the pixel grid
S = 256                   # the drawing canvas (4x)
C = S / 2.0
INK = (10, 8, 18, 255)

METALS = {
    "silver": dict(rim=[(255, 255, 255), (226, 233, 246), (184, 196, 220), (132, 144, 174), (78, 88, 118)],
                   face=((34, 44, 74), (16, 22, 42)), glint=False, sparkle=False),
    "gold": dict(rim=[(255, 250, 214), (252, 218, 112), (230, 176, 58), (180, 122, 26), (118, 74, 14)],
                 face=((50, 34, 30), (24, 16, 18)), glint=True, sparkle=False),
    "purple": dict(rim=[(252, 232, 255), (218, 156, 255), (174, 92, 242), (120, 46, 192), (70, 18, 122)],
                   face=((52, 22, 84), (24, 8, 42)), glint=True, sparkle=True),
}

# (key, accent colour) - the accent is the colour of its trail / mark on the pitch (PS_LOOK)
PLAYSTYLES = [
    ("accelerator", (255, 222, 80)), ("header", (245, 245, 255)), ("bullet", (80, 240, 255)),
    ("chip", (255, 236, 170)), ("guardian", (120, 180, 255)), ("bruiser", (255, 170, 70)),
    ("penalty", (190, 255, 110)), ("finesse", (140, 210, 255)), ("relentless", (255, 130, 40)),
    ("rapid", (255, 222, 70)), ("anticipate", (120, 220, 255)), ("rushout", (255, 255, 255)),
    ("clinical", (255, 76, 86)), ("deflector", (220, 235, 255)), ("power", (255, 130, 30)),
    ("whipped", (255, 164, 60)), ("tikitaka", (110, 255, 150)), ("trickster", (210, 130, 255)),
]
WHITE = (250, 250, 255)
CREAM = (255, 240, 214)


# ---- drawing helpers on the 256 canvas ---------------------------------------------------------
def layer():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


def ball(d, x, y, r, col=WHITE):
    d.ellipse((x - r, y - r, x + r, y + r), fill=col + (255,))
    p = r * 0.42                                  # a pentagon patch, so it reads as a football
    pts = [(x + math.cos(a) * p, y + math.sin(a) * p) for a in [i * math.tau / 5 - math.pi / 2 for i in range(5)]]
    d.polygon(pts, fill=(30, 30, 44, 255))


def thick_curve(d, pts, w, col):
    for a, b in zip(pts, pts[1:]):
        d.line((a, b), fill=col + (255,), width=int(w))
    for p in (pts[0], pts[-1]):
        d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=col + (255,))


def bez(p0, c, p2, n=40):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p2[1]) for t in [i / n for i in range(n + 1)]]


def arrow_head(d, tip, ang, size, col):
    a, b = ang + math.pi * 0.82, ang - math.pi * 0.82
    d.polygon([tip, (tip[0] + math.cos(a) * size, tip[1] + math.sin(a) * size),
               (tip[0] + math.cos(b) * size, tip[1] + math.sin(b) * size)], fill=col + (255,))


def goal_frame(d, x0, y0, x1, y1, w, col=WHITE):
    d.line(((x0, y1), (x0, y0), (x1, y0)), fill=col + (255,), width=w)   # post + bar (side view)


# ---- the eighteen symbols (each draws on the face, roughly within 64..192) -------------------------
def sym(key, acc):
    im = layer()
    d = ImageDraw.Draw(im)
    if key == "accelerator":                      # chevrons streaking right, speed lines behind
        for i, x in enumerate((96, 128, 160)):
            d.polygon([(x - 18, 84), (x + 10, 128), (x - 18, 172), (x - 2, 172), (x + 26, 128), (x - 2, 84)],
                      fill=(acc if i == 2 else WHITE) + (255,))
        for y in (100, 128, 156):
            d.line(((52, y), (70, y)), fill=acc + (255,), width=10)
    elif key == "header":                         # a head (with hair) meets it - and it flies off on a laser
        d.ellipse((52, 112, 124, 184), fill=CREAM + (255,))
        d.pieslice((52, 106, 124, 178), 180, 360, fill=(70, 46, 30, 255))      # hair
        d.ellipse((96, 140, 106, 150), fill=(30, 30, 44, 255))                # an eye
        for k, (a, b) in enumerate((((130, 120), (150, 104)), ((138, 136), (160, 128)), ((126, 104), (138, 84)))):
            d.line((a, b), fill=(255, 236, 140, 255), width=9)                 # the impact
        d.line(((150, 96), (168, 84)), fill=acc + (255,), width=16)
        ball(d, 180, 78, 26)
    elif key == "bullet":                         # a flat laser bar, the ball at its head
        d.rectangle((52, 112, 150, 144), fill=acc + (255,))
        d.rectangle((70, 122, 150, 134), fill=WHITE + (255,))
        ball(d, 168, 128, 28)
    elif key == "chip":                           # up over the bar, dropping into the goal
        goal_frame(d, 150, 110, 196, 196, 10)
        pts = bez((60, 188), (140, -10), (176, 150))
        for p in pts[::4]:
            d.ellipse((p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7), fill=acc + (255,))
        ball(d, 176, 154, 20)
    elif key == "guardian":                       # a shield, a ball won in it
        d.polygon([(128, 56), (192, 80), (186, 140), (128, 200), (70, 140), (64, 80)], fill=acc + (255,))
        d.polygon([(128, 74), (176, 92), (171, 138), (128, 182), (85, 138), (80, 92)], fill=(30, 60, 120, 255))
        ball(d, 128, 126, 26)
    elif key == "bruiser":                        # a fist, and the shockwave off it
        d.rounded_rectangle((70, 92, 140, 168), 16, fill=CREAM + (255,))
        for x in (84, 102, 120):
            d.line(((x, 96), (x, 128)), fill=(150, 110, 90, 255), width=4)
        d.rounded_rectangle((60, 120, 84, 160), 8, fill=CREAM + (255,))   # thumb
        for r in (32, 56):
            d.arc((140 - r, 128 - r, 140 + r, 128 + r), -55, 55, fill=acc + (255,), width=12)
    elif key == "penalty":                        # the knuckleball: a ball on a zig-zag trail
        pts = [(52, 150), (74, 118), (96, 156), (118, 112), (140, 150)]
        thick_curve(d, pts, 13, acc)
        ball(d, 166, 120, 30)
    elif key == "finesse":                        # out low, and CURLING up into the top corner
        goal_frame(d, 166, 70, 200, 190, 10)
        pts = bez((56, 176), (150, 220), (178, 96))
        thick_curve(d, pts, 18, acc)
        thick_curve(d, pts[8:], 7, WHITE)
        ball(d, 182, 92, 20)
    elif key == "relentless":                     # a flame
        d.polygon([(128, 50), (176, 120), (172, 170), (128, 204), (84, 170), (80, 120), (108, 96)], fill=acc + (255,))
        d.polygon([(130, 104), (156, 150), (150, 182), (128, 194), (106, 182), (102, 150), (118, 134)],
                  fill=(255, 226, 110, 255))
    elif key == "rapid":                          # a bolt, the ball at its foot
        d.polygon([(122, 48), (82, 132), (118, 132), (96, 208), (170, 108), (132, 108), (152, 48)], fill=acc + (255,))
        ball(d, 176, 176, 22)
    elif key == "anticipate":                     # an eye that reads it
        d.ellipse((50, 92, 206, 164), fill=WHITE + (255,))
        d.ellipse((98, 98, 158, 158), fill=acc + (255,))
        d.ellipse((114, 114, 142, 142), fill=(16, 16, 30, 255))
        d.ellipse((132, 108, 144, 120), fill=WHITE + (255,))
    elif key == "rushout":                        # a glove flying out, motion lines behind
        d.rounded_rectangle((104, 78, 176, 176), 26, fill=WHITE + (255,))
        d.rounded_rectangle((84, 112, 112, 164), 12, fill=WHITE + (255,))         # thumb
        for x in (124, 142, 160):
            d.line(((x, 84), (x, 118)), fill=(150, 160, 190, 255), width=5)
        d.rectangle((110, 176, 172, 196), fill=(80, 200, 120, 255))                # cuff
        for y in (98, 130, 162):
            d.line(((48, y), (76, y)), fill=(200, 220, 255, 255), width=9)
    elif key == "clinical":                       # the crosshair, locked on, the ball in it
        d.ellipse((60, 60, 196, 196), outline=acc + (255,), width=14)
        for a, b in (((128, 44), (128, 92)), ((128, 164), (128, 212)), ((44, 128), (92, 128)), ((164, 128), (212, 128))):
            d.line((a, b), fill=acc + (255,), width=14)
        ball(d, 128, 128, 22)
    elif key == "deflector":                      # a parry: the ball sent up and away off a wall
        d.rounded_rectangle((60, 70, 84, 196), 10, fill=acc + (255,))
        pts = bez((92, 170), (130, 40), (190, 92))
        for p in pts[::5]:
            d.ellipse((p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6), fill=WHITE + (255,))
        ball(d, 186, 96, 22)
    elif key == "power":                          # the fireball
        d.polygon([(40, 128), (100, 82), (90, 112), (150, 96), (150, 160), (90, 144), (100, 174)], fill=acc + (255,))
        d.polygon([(76, 128), (116, 104), (112, 120), (150, 112), (150, 144), (112, 136), (116, 152)],
                  fill=(255, 226, 110, 255))
        ball(d, 164, 128, 32)
    elif key == "whipped":                        # the dipper: up, then diving down
        pts = bez((52, 190), (128, -30), (186, 182))
        thick_curve(d, pts, 16, acc)
        thick_curve(d, pts[10:30], 6, WHITE)
        arrow_head(d, (192, 196), math.atan2(182 - 70, 186 - 160), 34, acc)
        ball(d, 128, 84, 20)
    elif key == "tikitaka":                       # the passing triangle
        tri = [(128, 70), (184, 170), (72, 170)]
        d.polygon(tri, outline=acc + (255,), width=14)
        for (x, y) in tri:
            ball(d, x, y, 20)
    elif key == "trickster":                      # a sharp turn with the ball: in, and hard back out
        thick_curve(d, [(56, 92), (150, 92)], 16, acc)
        pts = bez((150, 92), (206, 128), (150, 164))
        thick_curve(d, pts, 16, acc)
        thick_curve(d, [(150, 164), (84, 164)], 16, acc)
        arrow_head(d, (60, 164), math.pi, 34, acc)
        ball(d, 176, 128, 22)
    return im


# ---- the coin ----------------------------------------------------------------------------------
def snap(im, n=N):
    """256 -> 64: average down, then make every pixel either solid or clear."""
    small = im.resize((n, n), Image.BOX)
    px = small.load()
    for y in range(n):
        for x in range(n):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255) if a >= 110 else (0, 0, 0, 0)
    return small


def outlined(im):
    """Its own one-pixel ink outline, on the 64 grid."""
    a = im.getchannel("A").filter(ImageFilter.MaxFilter(3))
    out = Image.new("RGBA", im.size, INK)
    out.putalpha(a)
    out.alpha_composite(im)
    return out


def medallion(key, acc, metal):
    M = METALS[metal]
    base = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    px = base.load()
    c = (N - 1) / 2.0
    R, RIM_IN = 31.0, 23.5
    rim = M["rim"]
    for y in range(N):
        for x in range(N):
            dx, dy = x - c, y - c
            dd = math.hypot(dx, dy)
            if dd > R:
                continue
            if dd > R - 1.2:
                px[x, y] = INK
                continue
            if dd > RIM_IN:                       # the rim, lit from the top left
                lit = (-dx - dy) / (dd * 1.4142 + 1e-6)               # 1 top-left .. -1 bottom-right
                band = (dd - RIM_IN) / (R - RIM_IN)                   # 0 inner .. 1 outer
                k = 0.5 - 0.5 * lit
                k += 0.18 * (0.5 - band) * (1 if lit > 0 else -1)     # a rounded edge
                i = max(0, min(4, int(round(k * 4))))
                col = rim[i]
                ang = math.atan2(dy, dx)
                if band > 0.55 and int((ang + math.pi) / math.tau * 32) % 2 == 0:
                    col = rim[min(4, i + 1)]                            # the milled ticks
                px[x, y] = col + (255,)
            elif dd > RIM_IN - 1.2:
                px[x, y] = INK                    # the step down into the face
            else:                                 # the enamel face, a touch lighter top left
                t = max(0.0, min(1.0, 0.5 + (dx + dy) / (RIM_IN * 2.6)))
                f0, f1 = M["face"]
                px[x, y] = tuple(int(f0[j] + (f1[j] - f0[j]) * t) for j in range(3)) + (255,)
                if abs(dd - (RIM_IN - 2.2)) < 0.6 and dx + dy < -4:
                    px[x, y] = tuple(min(255, v + 40) for v in px[x, y][:3]) + (255,)   # inner bevel light
    # the symbol: drawn big, shrunk onto the face, outlined
    s = sym(key, acc)
    s = s.resize((int(S * 1.06), int(S * 1.06)), Image.LANCZOS)   # (big: it should fill the face)
    canvas = layer()
    off = (S - s.width) // 2
    canvas.paste(s, (off, off), s)
    small = outlined(snap(canvas))
    base.alpha_composite(small)
    pxb = base.load()
    if M["glint"]:                                # a glint on the rim, top left
        for (x, y, col) in ((13, 8, (255, 255, 255)), (12, 9, (255, 255, 255)), (14, 9, (255, 255, 255)),
                            (13, 10, (255, 255, 255)), (13, 7, (255, 255, 230)), (13, 11, (255, 255, 230)),
                            (11, 9, (255, 255, 230)), (15, 9, (255, 255, 230))):
            pxb[x, y] = col + (255,)
    if M["sparkle"]:
        for (cx, cy) in ((52, 12), (54, 50)):
            for (dx, dy) in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                pxb[cx + dx, cy + dy] = (255, 236, 255, 255)
    return base


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites")
    os.makedirs(out, exist_ok=True)
    sheet = Image.new("RGBA", (len(PLAYSTYLES) * 72 + 8, 3 * 72 + 8), (20, 22, 34, 255))
    for i, (key, acc) in enumerate(PLAYSTYLES):
        for j, (metal, suffix) in enumerate((("silver", "_s"), ("gold", ""), ("purple", "_p"))):
            im = medallion(key, acc, metal)
            im.save(os.path.join(out, "ps_%s%s.png" % (key, suffix)))
            if metal == "gold":
                im.resize((N * 4, N * 4), Image.NEAREST).save(os.path.join(out, "ps_%s_x4.png" % key))
            sheet.alpha_composite(im, (8 + i * 72, 8 + j * 72))
    sheet.save(os.path.join(out, "playstyles_sheet.png"))
    print("%d PlayStyles x 3 metals -> %s" % (len(PLAYSTYLES), out))


if __name__ == "__main__":
    main()
