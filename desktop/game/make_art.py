"""Pixel art for Ragdoll Football menus and cards.

Writes into the sprites folder:
  icon_<player>.png       detailed 48x48-block portraits for the icon cards (192x192)
  pack_0..3.png           illustrated packs (World Cup, Champion Drafts A-C)
  card_back.png           face-down card for the pack opening
  banner_1..3.png         main-menu panels (champions / World Cup pack / coming soon)
  tpl_wg_card.png         THE WORLD'S GAME card: purple flag, rainbow-silver border
  tpl_wgframe_card.png    the same with the inside cut out - laid over the player
  pack_wg.png             the foil a World's Game player comes out of
  essence_bg.png          the Essence shop's backdrop
No real photos or logos - everything is drawn here.
"""
import os
import sys
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont

import make_sprites as MS

OUT = sys.argv[1] if len(sys.argv) > 1 else "sprites"
os.makedirs(OUT, exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
shade, mix, Grid = MS.shade, MS.mix, MS.Grid
GOLD = (236, 190, 60)
DGOLD = (170, 120, 30)
WHITE = (248, 248, 248)
INK = (18, 18, 26)


# ======================================================================= portraits
SKIN = {"pale": (240, 206, 178), "light": (228, 184, 150), "tan": (204, 156, 116),
        "olive": (186, 138, 100), "brown": (150, 100, 70), "dark": (108, 70, 52), "deep": (82, 54, 40)}
HAIR = {"black": (26, 22, 22), "darkbrown": (54, 36, 28), "brown": (92, 62, 40),
        "lightbrown": (150, 110, 70), "blond": (240, 216, 128), "ginger": (170, 90, 46),
        "pink": (246, 142, 194)}

# name: skin, hair, style, beard, shirt (base, trim)
ICONS = {
    "messi": ("light", "brown", "swept", "full", ((117, 180, 228), WHITE)),
    "neymar": ("tan", "blond", "bleach", "stubble", ((252, 214, 40), (0, 150, 72))),
    "aoyagi": ("light", "pink", "pinkcrop", None, ((22, 22, 30), (60, 230, 240))),
    "ronaldo": ("tan", "darkbrown", "quiff", None, ((172, 20, 36), (0, 102, 60))),
    "mbappe": ("brown", "black", "buzz", None, ((26, 46, 112), WHITE)),
    "yamal": ("brown", "black", "curlytop", None, ((202, 22, 34), (250, 200, 24))),
    "salah": ("brown", "black", "afro", "full", ((200, 16, 46), WHITE)),
    "vandijk": ("brown", "black", "fade", "full", ((245, 112, 22), (24, 24, 24))),
    "lewandowski": ("light", "darkbrown", "neat", "stubble", (WHITE, (220, 22, 60))),
    "modric": ("pale", "lightbrown", "long", None, ((214, 32, 42), WHITE)),
    "suarez": ("light", "darkbrown", "shaggy", "stubble", ((245, 180, 204), INK)),
}


# ---------------------------------------------------------------- portraits (64x64 blocks)
def _disc(g, cx, cy, r, col, squash=1.0):
    for y in range(int(cy - r * squash) - 1, int(cy + r * squash) + 2):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            if ((x - cx) / r) ** 2 + ((y - cy) / (r * squash)) ** 2 <= 1.0:
                g.set(x, y, col)


def _face_half(y):
    import math as _m
    if y < 14:
        v = 1 - ((14 - y) / 7.5) ** 2
        return 16 * _m.sqrt(max(0.0, v))
    if y <= 34:
        return 16.0
    v = 1 - ((y - 34) / 14.5) ** 2
    return 16 * _m.sqrt(max(0.0, v))


def portrait(skin_name, hair_name, style, beard, shirt, extras=()):
    """Detailed 64x64 pixel portrait: jersey shoulders, shaded face, styled hair.
    shirt = (base, trim) or (base, trim, alt, pattern) for striped kits."""
    g = Grid(64, 64, 3)
    s = SKIN[skin_name] if isinstance(skin_name, str) else skin_name
    sl, sd, sdd = shade(s, 1.12), shade(s, 0.86), shade(s, 0.7)
    h = HAIR[hair_name] if isinstance(hair_name, str) else hair_name
    hl, hd = shade(h, 1.13), shade(h, 0.65)
    base, trim = shirt[0], shirt[1]
    alt, pattern = (shirt[2], shirt[3]) if len(shirt) > 3 else (base, "plain")
    lip = mix(s, (170, 66, 62), 0.5)

    # ---- jersey shoulders
    for y in range(50, 64):
        half = 12 + (y - 50) * 2.4
        g.rect(int(32 - half), y, int(31 + half), y, base)
        if pattern in ("stripes", "weave") and alt != base:
            for x in range(int(32 - half), int(32 + half)):
                if (x // 5) % 2 == 1:
                    g.set(x, y, alt)
        elif pattern == "checks" and alt != base:
            for x in range(int(32 - half), int(32 + half)):
                if ((x // 5) + (y // 5)) % 2 == 1:
                    g.set(x, y, alt)
        g.rect(int(32 - half), y, int(32 - half) + 2, y, shade(base, 0.8))
        g.rect(int(31 + half) - 2, y, int(31 + half), y, shade(base, 0.82))
    g.rect(0, 62, 63, 63, shade(base, 0.72))
    for y in range(50, 57):                               # collar
        g.rect(24 - (y - 50), y, 39 + (y - 50), y, trim)
    g.rect(26, 50, 37, 54, sd)                            # chest showing through the collar
    # ---- neck
    g.rect(25, 44, 38, 54, sd)
    g.rect(25, 44, 38, 47, sdd)                           # jaw shadow
    g.rect(28, 50, 35, 52, shade(s, 0.78))
    # ---- face
    for y in range(7, 50):
        half = _face_half(y)
        if half < 1:
            continue
        g.rect(int(32 - half), y, int(31 + half), y, s)
        g.rect(int(31 + half) - 2, y, int(31 + half), y, sd)       # shadow side
        g.set(int(32 - half), y, sl)
    for y in range(14, 40):                               # left light
        g.set(int(32 - _face_half(y)) + 1, y, sl)
    # ears
    for cx in (15, 48):
        _disc(g, cx, 30, 4.2, s, 1.35)
        _disc(g, cx, 30, 2.4, sd, 1.3)
        _disc(g, cx + (1 if cx < 32 else -1), 29, 1.2, sdd, 1.2)
    # cheekbones + chin
    _disc(g, 21, 35, 4.0, mix(s, (214, 128, 112), 0.18), 0.8)
    _disc(g, 43, 35, 4.0, mix(s, (200, 120, 104), 0.14), 0.8)
    _disc(g, 32, 45, 4.5, sl, 0.55)
    g.rect(26, 47, 37, 48, sd)
    # brows
    for x0, x1, d in ((18, 28, 1), (35, 45, -1)):
        for x in range(x0, x1 + 1):
            k = (x - x0) / max(1, (x1 - x0))
            y = 22 + int((1 - k) * 1.6 if d > 0 else k * 1.6)
            g.rect(x, y, x, y + 1, hd)
    # eyes
    iris = (58, 136, 250) if "eyes_blue" in extras else \
        ((72, 48, 32) if hair_name != "black" else (58, 40, 30))
    for ex in (20, 36):
        if "eyes_closed" in extras:                        # lids shut: a soft lash curve
            g.rect(ex, 27, ex + 8, 30, s)
            g.rect(ex + 1, 29, ex + 7, 29, sdd)
            g.set(ex, 28, sdd); g.set(ex + 8, 28, sdd)
            g.rect(ex, 31, ex + 8, 31, sd)
            continue
        # A real eye is mostly iris with a sliver of white either side. The old version was a
        # 9x5 white block with a small pupil floating in it, which at card size read as googly.
        white = mix(WHITE, s, 0.12)
        g.rect(ex + 1, 27, ex + 7, 29, white)
        g.set(ex + 1, 27, mix(white, sd, 0.5)); g.set(ex + 7, 27, mix(white, sd, 0.5))
        g.rect(ex, 26, ex + 8, 26, sdd)                    # lash line, heavier than the lid
        g.rect(ex, 25, ex + 8, 25, mix(s, sdd, 0.45))      # crease above it
        g.set(ex, 27, sd); g.set(ex + 8, 27, sd)           # inner / outer corners
        _disc(g, ex + 4, 28.4, 3.0, iris)                  # iris fills the opening
        _disc(g, ex + 4, 28.4, 1.5, (14, 10, 10) if "eyes_blue" not in extras else (12, 20, 56))
        g.set(ex + 3, 27, (252, 252, 250))                 # catchlight
        g.rect(ex + 1, 30, ex + 7, 30, mix(s, sd, 0.6))    # lower lid
        g.rect(ex, 31, ex + 8, 31, sd)                     # under-eye
    # nose
    g.rect(30, 27, 33, 36, mix(s, sd, 0.35))
    g.rect(29, 33, 34, 37, s)
    g.rect(28, 36, 35, 37, sd)
    g.set(28, 36, sdd); g.set(35, 36, sdd)
    g.rect(30, 38, 33, 38, sdd)
    g.set(31, 34, sl)
    # mouth
    g.rect(25, 40, 38, 40, sdd)
    g.rect(26, 41, 37, 42, lip)
    g.rect(27, 43, 36, 43, shade(lip, 0.75))
    g.set(25, 41, sdd); g.set(38, 41, sdd)

    # ---- hair
    if style == "bald":
        for y in range(7, 13):
            half = _face_half(y)
            g.rect(int(32 - half), y, int(31 + half), y, shade(s, 0.97))
        _disc(g, 26, 11, 4.0, sl, 0.55)
        for x in range(16, 48, 2):
            g.set(x, 15, mix(s, h, 0.22))
    elif style == "wedge":                                  # shaved head with one wedge of hair at the front
        for y in range(7, 13):
            half = _face_half(y)
            g.rect(int(32 - half), y, int(31 + half), y, shade(s, 0.97))
        _disc(g, 24, 11, 3.6, sl, 0.55)
        for y in range(7, 17):
            half = 1 + (y - 7) * 0.75
            g.rect(int(32 - half), y, int(31 + half), y, h)
        g.set(31, 9, hl); g.set(33, 12, hl)
        for x in range(16, 48, 2):
            g.set(x, 15, mix(s, h, 0.22))
    elif style == "mohawk":                                 # shaved sides, a spiky strip down the middle
        for y in range(7, 17):
            half = _face_half(y) + (1 if y > 12 else 0)
            for x in range(int(32 - half), int(32 + half)):
                if (x + y) % 3 == 0:
                    g.set(x, y, mix(h, s, 0.45))
        g.rect(25, 3, 38, 17, h)
        for x in range(25, 38, 3):
            g.rect(x, 0, x + 1, 3, h)
            g.set(x, 0, hl)
        for y in range(5, 16, 4):
            g.rect(29, y, 30, y + 1, hl)
        g.rect(14, 16, 15, 24, mix(h, s, 0.5)); g.rect(48, 16, 49, 24, mix(h, s, 0.5))
    elif style == "dreads":                                 # locs tied up top, falling past the ears
        _disc(g, 32, 14, 17, mix(h, s, 0.15), 0.58)
        for x in range(15, 49, 3):
            top = 2 + (x * 5) % 4
            g.rect(x, top, x + 1, 17, h)
            g.set(x, top, hl)
        for x in list(range(9, 18, 2)) + list(range(46, 55, 2)):
            end = 44 + (x * 7) % 9
            for y in range(14, end):
                g.set(x, y, h if (y // 3) % 2 else hd)
            g.set(x, end, hl)
    elif style == "swept":                                  # Messi
        _disc(g, 32, 13, 17.5, h, 0.62)
        g.rect(15, 13, 48, 18, h)
        for x in range(16, 48, 4):
            g.rect(x, 18, x + 1, 20, h)
        g.rect(14, 15, 17, 28, h); g.rect(46, 15, 49, 28, h)
        for x in range(20, 44, 9):
            g.rect(x, 6, x + 1, 10, hl)
        g.rect(38, 17, 47, 21, h)
    elif style == "quiff":                                  # Ronaldo
        _disc(g, 32, 15, 17.0, h, 0.6)
        for x in range(17, 48):
            k = (x - 17) / 31.0
            top = int(2 + 7 * abs(k - 0.42) * 1.6)
            g.rect(x, top, x, 16, h)
        for x in range(22, 42, 8):
            g.rect(x, 7, x + 1, 12, hl)
        g.rect(14, 16, 16, 26, mix(h, s, 0.35)); g.rect(47, 16, 49, 26, mix(h, s, 0.35))
        g.rect(16, 17, 47, 19, h)
    elif style == "curlytop":                               # Yamal
        for (dx, dy, r) in ((-14, 10, 6), (-7, 5, 7), (2, 3, 7), (11, 5, 7), (17, 11, 6),
                            (-16, 18, 5), (18, 18, 5), (-3, 9, 6), (8, 9, 6)):
            _disc(g, 32 + dx, 8 + dy, r, h, 0.95)
        for (dx, dy) in ((-12, 7), (-4, 2), (6, 1), (13, 4), (16, 11), (-16, 14)):
            _disc(g, 32 + dx, 8 + dy, 1.3, hl, 0.9)
        g.rect(15, 18, 18, 26, h); g.rect(45, 18, 48, 26, h)
        for x in range(17, 47, 4):                          # curls over the forehead
            _disc(g, x, 19, 2.6, h, 0.9)
        if "nohb" not in extras:
            g.rect(14, 17, 49, 20, (232, 232, 236))        # headband
            g.rect(14, 18, 49, 19, (206, 28, 38))
    elif style == "pinkcrop":                               # spiky textured crop, side-swept fringe, undercut
        root = shade(h, 0.62)
        _disc(g, 32, 13, 17.4, h, 0.6)
        g.rect(15, 11, 48, 16, h)
        for x in range(16, 48, 4):                          # spikes on top
            for k in range(5):
                g.rect(x + k // 2, 3 + k, x + 3 - k // 2, 3 + k, h)
            g.set(x + 1, 3, hl)
        for k in range(12):                                 # fringe swept across to one side
            g.rect(19 + k * 2, 16 + k // 3, 22 + k * 2, 17 + k // 3, h)
        g.rect(40, 18, 46, 21, h)
        g.rect(14, 16, 16, 27, mix(root, s, 0.35)); g.rect(47, 16, 49, 27, mix(root, s, 0.35))
        for x in range(20, 46, 7):
            g.rect(x, 7, x + 1, 12, hl)
    elif style == "curly":                                  # tight curls, no band
        for (dx, dy, r) in ((-14, 11, 5), (-7, 6, 6), (2, 4, 6), (11, 6, 6), (16, 11, 5), (-3, 9, 5), (8, 9, 5)):
            _disc(g, 32 + dx, 8 + dy, r, h, 0.95)
        for (dx, dy) in ((-11, 7), (-2, 3), (7, 3), (14, 8)):
            _disc(g, 32 + dx, 8 + dy, 1.2, mix(h, hl, 0.45), 0.9)   # sheen, not sparkles
        g.rect(15, 16, 17, 25, h); g.rect(46, 16, 48, 25, h)
        for x in range(17, 47, 5):
            _disc(g, x, 18, 2.4, h, 0.9)
    elif style == "buzz":                                   # a short fade - solid on top,
        _disc(g, 32, 14, 17.4, h, 0.62)                     # thinning down to the temples
        g.rect(15, 13, 48, 18, h)
        for y in range(7, 20):                              # the fade itself: hair gives way
            half = _face_half(y) + (1 if y > 12 else 0)     # to skin as it comes down
            if half < 1:
                continue
            k = max(0.0, (y - 15) / 5.0)
            for x in range(int(32 - half), int(32 + half)):
                if k <= 0:
                    continue
                if (x + y) % 2 == 0 and k > 0.35:
                    g.set(x, y, mix(h, s, min(0.75, k)))
        g.rect(14, 15, 16, 24, mix(h, s, 0.3)); g.rect(47, 15, 49, 24, mix(h, s, 0.3))
        for x in range(20, 45, 7):                          # a little sheen on the crown
            g.set(x, 9, mix(h, hl, 0.5))
    elif style == "short":                                  # neat short crop with a small fringe
        _disc(g, 32, 13, 17.2, h, 0.6)
        g.rect(15, 12, 48, 17, h)
        for x in range(18, 46, 4):
            g.rect(x, 17, x + 2, 19, h)
        g.rect(14, 15, 16, 25, h); g.rect(47, 15, 49, 25, h)
        for x in range(20, 44, 8):
            g.rect(x, 6, x + 1, 10, hl)
    elif style == "bun":                                    # hair tied back into a bun
        _disc(g, 32, 13, 17, h, 0.58)
        g.rect(16, 12, 47, 16, h)
        _disc(g, 32, 3, 7, h, 0.8)
        _disc(g, 30, 1, 2, hl, 0.9)
        for x in range(18, 46, 5):
            g.set(x, 9, hl)
        g.rect(14, 15, 16, 22, h); g.rect(47, 15, 49, 22, h)
    elif style == "twists":                                 # short twists / locs on top
        _disc(g, 32, 14, 17, mix(h, s, 0.2), 0.58)
        for x in range(15, 49, 3):
            top = 2 + (x * 7) % 5
            g.rect(x, top, x + 1, 17, h)
            g.set(x, top, hl)
        g.rect(14, 16, 16, 26, mix(h, s, 0.4)); g.rect(47, 16, 49, 26, mix(h, s, 0.4))
    elif style == "afro":                                   # Salah
        _disc(g, 32, 14, 21, h, 0.85)
        for (dx, dy, r) in ((-18, 6, 7), (-9, 0, 7), (2, -2, 7), (12, 0, 7), (20, 7, 7),
                            (-22, 16, 6), (24, 16, 6)):
            _disc(g, 32 + dx, 8 + dy, r, h, 0.95)
        for (dx, dy) in ((-14, 1), (-4, -3), (8, -4), (16, 1), (20, 11), (-20, 11)):
            _disc(g, 32 + dx, 8 + dy, 1.4, hl, 0.9)
        g.rect(14, 18, 17, 30, h); g.rect(46, 18, 49, 30, h)
        g.rect(17, 19, 46, 21, h)
    elif style == "bleach":                                 # Neymar: bleached top, dark sides
        root = HAIR["darkbrown"]
        _disc(g, 32, 13, 17, h, 0.6)
        g.rect(16, 12, 47, 17, h)
        for x in range(18, 46, 3):                          # spiky textured top
            g.rect(x, 3 + (x % 2), x + 1, 6, h)
        for x in range(19, 45, 6):
            g.rect(x, 7, x + 1, 12, hl)
        g.rect(14, 16, 16, 27, mix(root, s, 0.45)); g.rect(47, 16, 49, 27, mix(root, s, 0.45))
        g.rect(17, 17, 46, 19, shade(h, 0.85))
    elif style == "fade":                                   # Van Dijk
        _disc(g, 32, 14, 17, h, 0.6)
        g.rect(16, 14, 47, 18, h)
        g.rect(14, 19, 16, 28, mix(h, s, 0.5)); g.rect(47, 19, 49, 28, mix(h, s, 0.5))
        for x in range(19, 45, 6):
            g.set(x, 7, hl)
        g.rect(17, 19, 46, 20, mix(h, s, 0.25))
    elif style == "neat":                                   # Lewandowski
        _disc(g, 32, 13, 17.5, h, 0.62)
        g.rect(15, 13, 48, 19, h)
        g.rect(15, 16, 18, 27, h); g.rect(45, 16, 48, 27, h)
        for x in range(20, 44, 9):
            g.rect(x, 6, x + 1, 10, hl)
        g.rect(20, 19, 44, 20, hd)
    elif style == "shaggy":                                 # Suarez
        _disc(g, 32, 13, 18.5, h, 0.68)
        g.rect(13, 13, 50, 20, h)
        g.rect(13, 14, 17, 32, h); g.rect(46, 14, 50, 32, h)
        for x in range(17, 47, 3):
            g.rect(x, 20, x + 1, 22 + (x % 3), h)
        for x in range(20, 44, 9):
            g.rect(x, 6, x + 1, 10, hl)
        if "nogrin" not in extras:
            g.rect(26, 39, 37, 39, sdd)                     # big grin
            g.rect(27, 40, 36, 41, (238, 238, 232))
            g.rect(28, 42, 35, 42, shade(lip, 0.8))
            g.set(26, 40, sdd); g.set(37, 40, sdd)
    elif style == "long":                                   # Modric
        _disc(g, 32, 13, 18, h, 0.62)
        g.rect(14, 13, 49, 18, h)
        g.rect(10, 16, 16, 52, h); g.rect(47, 16, 53, 52, h)
        g.rect(10, 48, 15, 54, hd); g.rect(48, 48, 53, 54, hd)
        g.rect(30, 3, 33, 16, hd)                           # centre parting
        for y in range(20, 48, 3):
            g.set(11, y, hl); g.set(52, y + 1, hl)
        g.rect(16, 17, 24, 20, h); g.rect(39, 17, 47, 20, h)

    # ---- beards
    if beard == "full":
        for y in range(34, 50):
            half = _face_half(y)
            if half < 1:
                continue
            g.rect(int(32 - half), y, int(31 + half), y, h)
        g.rect(24, 37, 39, 39, h)                           # moustache
        g.rect(25, 40, 38, 40, (32, 20, 18))
        g.rect(26, 41, 37, 42, lip)                         # mouth shows through
        g.rect(27, 43, 36, 43, shade(lip, 0.72))
        g.rect(25, 44, 38, 44, hd)
        g.rect(29, 33, 34, 37, s)                           # nose on top
        g.rect(28, 36, 35, 37, sd)
        g.rect(14, 26, 16, 36, h); g.rect(47, 26, 49, 36, h)
        for x in range(20, 44, 5):
            g.set(x, 46, hl)
    elif beard == "short":                                  # trimmed short beard
        bc = mix(h, s, 0.25)
        for y in range(36, 50):
            half = _face_half(y) - 1
            if half < 1:
                continue
            g.rect(int(32 - half), y, int(31 + half), y, bc)
        g.rect(25, 38, 38, 39, bc)
        g.rect(26, 40, 37, 40, sdd)
        g.rect(26, 41, 37, 42, lip)
        g.rect(28, 36, 35, 37, sd)
    elif beard == "goatee":
        bc = mix(h, s, 0.15)
        g.rect(26, 38, 37, 39, bc)
        g.rect(28, 44, 35, 49, bc)
        g.rect(29, 49, 34, 50, bc)
    elif beard == "tache":                                  # moustache only
        g.rect(25, 37, 38, 39, h)
        g.rect(24, 39, 25, 40, h); g.rect(38, 39, 39, 40, h)
    elif beard == "stubble":
        # A flat-ish wash over the jaw with a fine checker on top. Scattering single pixels at
        # full strength, which is what this used to do, reads as cuts rather than stubble.
        st = mix(s, h, 0.22)
        dark = mix(s, h, 0.32)
        for y in range(37, 50):
            half = _face_half(y) - 1
            if half < 1:
                continue
            for x in range(int(32 - half), int(32 + half)):
                if 25 <= x <= 38 and 39 <= y <= 43:         # not over the mouth
                    continue
                g.set(x, y, dark if (x + y) % 2 == 0 else st)
        g.rect(27, 44, 36, 47, mix(s, h, 0.30))
    if "grin" in extras:                                    # big toothy smile
        g.rect(25, 39, 38, 39, sdd)
        g.rect(26, 40, 37, 42, (240, 240, 234))
        g.rect(27, 43, 36, 43, shade(lip, 0.8))
        g.set(25, 40, sdd); g.set(38, 40, sdd)
        for x in range(28, 37, 3):
            g.set(x, 41, (214, 214, 206))
    if "hband" in extras:                                   # headband across the forehead
        g.rect(13, 17, 50, 20, (240, 240, 244))
        g.rect(13, 20, 50, 20, (200, 200, 210))
    for glow, col in (("glow_cyan", (70, 240, 255)), ("glow_green", (90, 255, 140))):
        if glow in extras and "eyes_closed" not in extras:
            for ex in (20, 36):
                g.rect(ex, 26, ex + 8, 30, mix(col, WHITE, 0.55))
                _disc(g, ex + 4, 28.5, 2.6, col)
                _disc(g, ex + 4, 28.5, 1.1, WHITE)
                side = -1 if ex == 20 else 1
                for k in range(1, 7):                       # light streaking off the eye
                    x = ex + (8 + k if side > 0 else -k)
                    g.set(x, 28 - k // 3, mix(col, s, k / 8.0))
    return g.image()


# ======================================================================= packs
def text_img(txt, size, fill, stroke=INK, sw=3):
    f = ImageFont.truetype(FONT, size)
    l, t, r, b = f.getbbox(txt, stroke_width=sw)
    im = Image.new("RGBA", (r - l + 4, b - t + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - l, 2 - t), txt, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)
    return im


def pixelate(im, k=3):
    return im.resize((max(1, im.width // k), max(1, im.height // k)), Image.NEAREST).resize(
        (im.width // k * k, im.height // k * k), Image.NEAREST)


def make_ball(N=24, k=10):
    """The match ball: a chunky pixel football (white with dark patches)."""
    import math as _m
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    px = im.load()
    c = (N - 1) / 2.0
    R = N / 2.0 - 0.5
    base, lit, dim = (244, 246, 250), (255, 255, 255), (198, 206, 218)
    edge, patch = (20, 20, 28), (30, 30, 40)
    spots = [(c, c, R * 0.27)]
    for i in range(5):
        a = _m.radians(i * 72 - 90)
        spots.append((c + _m.cos(a) * R * 0.66, c + _m.sin(a) * R * 0.66, R * 0.19))
    hx, hy = c - R * 0.44, c - R * 0.44
    for y in range(N):
        for x in range(N):
            dx, dy = x - c, y - c
            d = _m.hypot(dx, dy)
            if d > R:
                continue
            if d > R - 1.15:
                px[x, y] = edge + (255,)
                continue
            col = base
            if d > R * 0.5 and (dx + dy) / R > 0.8:        # shaded underside
                col = dim
            elif _m.hypot(x - hx, y - hy) < R * 0.2:       # highlight
                col = lit
            for sx, sy, sr in spots:
                if _m.hypot(x - sx, y - sy) <= sr:
                    col = patch
                    break
            px[x, y] = col + (255,)
    return im.resize((N * k, N * k), Image.NEAREST)


def trophy(d, cx, top, s, col=GOLD):
    """Chunky pixel World Cup-style trophy (generic, not the real design)."""
    dk = shade(col, 0.7)
    d.ellipse([cx - 10 * s, top, cx + 10 * s, top + 16 * s], fill=col)
    d.rectangle([cx - 5 * s, top + 12 * s, cx + 5 * s, top + 30 * s], fill=col)
    d.rectangle([cx - 2 * s, top + 14 * s, cx - 1 * s, top + 28 * s], fill=shade(col, 1.3))
    d.rectangle([cx - 9 * s, top + 30 * s, cx + 9 * s, top + 36 * s], fill=(30, 110, 60))
    d.rectangle([cx - 11 * s, top + 36 * s, cx + 11 * s, top + 40 * s], fill=dk)
    d.ellipse([cx - 6 * s, top + 3 * s, cx + 2 * s, top + 9 * s], fill=shade(col, 1.35))


def make_pack(i):
    W, H = 300, 420
    styles = [((20, 34, 80), (236, 190, 60), "WORLD CUP"), ((150, 20, 40), (250, 220, 120), "CLUB PACK 1"),
              ((20, 70, 170), (140, 210, 255), "CLUB PACK 2"), ((90, 30, 130), (240, 150, 255), "CLUB PACK 3")]
    body, accent, name = styles[i]
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # foil body with crimped top/bottom edges
    d.rounded_rectangle([10, 24, W - 10, H - 24], 18, fill=body)
    for x in range(10, W - 10, 12):
        d.polygon([(x, 26), (x + 6, 8), (x + 12, 26)], fill=shade(body, 1.2))
        d.polygon([(x, H - 26), (x + 6, H - 8), (x + 12, H - 26)], fill=shade(body, 1.2))
    d.rectangle([10, 24, W - 10, 40], fill=shade(body, 1.35))
    d.rectangle([10, H - 40, W - 10, H - 24], fill=shade(body, 1.35))
    # diagonal foil light
    for k in range(-H, W, 46):
        d.polygon([(k, H), (k + 18, H), (k + 18 + H * 0.6, 0), (k + H * 0.6, 0)], fill=shade(body, 1.12) + (255,))
    d.rounded_rectangle([10, 24, W - 10, H - 24], 18, outline=accent, width=6)
    # emblem
    if i == 0:
        trophy(d, W // 2, 100, 4, GOLD)
    else:
        codes = [c for c in ("ARS", "AST", "BOU", "BRE", "BRI", "CHE", "CRY", "EVE", "FUL", "LIV", "MCI",
                             "MUN", "NEW", "NOT", "TOT", "WES", "WOL", "SUN", "INT", "ALN", "BAR")]
        mine = codes[(i - 1) * 7:(i - 1) * 7 + 7]
        if "BAR" in mine:
            mine = ["BAR"] + [c for c in mine if c != "BAR"]
        for j, code in enumerate(mine[:6]):
            p = os.path.join(OUT, "%s_badge.png" % code)
            if os.path.exists(p):
                b = Image.open(p).convert("RGBA").resize((60, 72), Image.NEAREST)
                x = 50 + (j % 3) * 70
                y = 90 + (j // 3) * 88
                im.alpha_composite(b, (x, y))
    # stars + name plate
    for sx in (60, 150, 240):
        d.polygon([(sx, 58), (sx + 6, 70), (sx + 18, 70), (sx + 8, 78), (sx + 12, 90), (sx, 82), (sx - 12, 90),
                   (sx - 8, 78), (sx - 18, 70), (sx - 6, 70)], fill=accent)
    d.rectangle([22, 290, W - 22, 350], fill=shade(body, 0.6))
    t = text_img(name, 34, accent)
    im.alpha_composite(t, ((W - t.width) // 2, 320 - t.height // 2))
    return pixelate(im, 3)


def make_card_back():
    W, H = 360, 500
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, W - 1, H - 1], 26, fill=(16, 20, 40))
    d.rounded_rectangle([10, 10, W - 11, H - 11], 20, outline=GOLD, width=6)
    for k in range(-H, W, 30):
        d.line([(k, H), (k + H * 0.7, 0)], fill=(26, 32, 62), width=8)
    d.ellipse([W // 2 - 90, H // 2 - 90, W // 2 + 90, H // 2 + 90], outline=GOLD, width=8)
    t = text_img("RF", 110, GOLD)
    im.alpha_composite(t, ((W - t.width) // 2, (H - t.height) // 2))
    return pixelate(im, 3)


# ======================================================================= banners
def ragdoll(code, slug, arms_up=True, scale=2):
    """A standing player built from the game sprites (for banner art)."""
    base = os.path.join(OUT, "%s_%s_" % (code, slug))
    parts = {}
    for p, size in (("head", (52, 52)), ("torso", (51, 67)), ("arm", (17, 53)), ("leg", (20, 51))):
        im = Image.open(base + p + ".png").convert("RGBA")
        bb = im.getbbox()
        im = im.crop(bb)
        if p == "head":
            k = min(size[0] / im.width, size[1] / im.height)
            size = (int(im.width * k), int(im.height * k))
        parts[p] = im.resize(size, Image.NEAREST)
    W, H = 150, 220
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ox, cy = W // 2, 110
    for sx in (-12, 12):
        c.alpha_composite(parts["leg"], (ox + sx - 10, cy + 30))
    for sx, rot in ((-1, 150), (1, -150)) if arms_up else ((-1, 0), (1, 0)):
        arm = parts["arm"].rotate(rot, expand=True, resample=Image.NEAREST) if arms_up else parts["arm"]
        ax = ox + sx * 34 - arm.width // 2
        ay = cy - 34 - (arm.height - 20 if arms_up else 0)
        c.alpha_composite(arm, (ax, ay + (20 if arms_up else 30)))
    c.alpha_composite(parts["torso"], (ox - 25, cy - 33))
    c.alpha_composite(parts["head"], (ox - parts["head"].width // 2, cy - 33 - parts["head"].height - 2))
    return c.resize((W * scale, H * scale), Image.NEAREST)


def champion(im, faces, cx, ground, scale=1.0):
    """A player holding the World Cup above his head (banner hero)."""
    d = ImageDraw.Draw(im)
    S = lambda v: int(v * scale)
    red, dred, yel = (198, 22, 36), (150, 12, 26), (250, 200, 24)
    navy, skin = (24, 30, 70), SKIN["brown"]
    # legs
    for sx in (-S(26), S(10)):
        d.rectangle([cx + sx, ground - S(74), cx + sx + S(28), ground - S(30)], fill=navy)
        d.rectangle([cx + sx + S(2), ground - S(32), cx + sx + S(26), ground - S(8)], fill=red)
        d.rectangle([cx + sx, ground - S(10), cx + sx + S(30), ground], fill=(240, 240, 240))
    # torso
    d.rectangle([cx - S(44), ground - S(150), cx + S(44), ground - S(66)], fill=red)
    d.rectangle([cx - S(44), ground - S(150), cx - S(30), ground - S(66)], fill=dred)
    d.rectangle([cx - S(44), ground - S(76), cx + S(44), ground - S(66)], fill=yel)
    d.rectangle([cx - S(10), ground - S(140), cx + S(6), ground - S(90)], fill=(250, 230, 120))  # crest strip
    # arms raised
    for sx in (-1, 1):
        x0 = cx + sx * S(44)
        d.polygon([(x0, ground - S(148)), (x0 + sx * S(24), ground - S(150)),
                   (x0 + sx * S(40), ground - S(236)), (x0 + sx * S(18), ground - S(238))], fill=skin)
        d.rectangle([x0 - S(6), ground - S(150), x0 + S(6), ground - S(132)], fill=red)
        d.ellipse([x0 + sx * S(16) - S(12), ground - S(252), x0 + sx * S(16) + S(12), ground - S(228)], fill=skin)
    # head (pixel portrait, cropped to the face)
    face = faces["yamal"].resize((S(120), S(120)), Image.NEAREST)
    im.alpha_composite(face, (cx - S(60), ground - S(262)))
    # medal
    d.line([(cx - S(22), ground - S(146)), (cx, ground - S(112))], fill=(40, 60, 160), width=S(7))
    d.line([(cx + S(22), ground - S(146)), (cx, ground - S(112))], fill=(40, 60, 160), width=S(7))
    d.ellipse([cx - S(11), ground - S(118), cx + S(11), ground - S(96)], fill=GOLD)
    # the trophy, held overhead
    ts = max(2, int(4 * scale))
    trophy(d, cx, max(2, ground - S(258) - 40 * ts), ts, GOLD)


def make_banner_champions(faces):
    W, H = 840, 270
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for y in range(H):                                   # night sky -> Spain red glow
        t = y / H
        d.line([(0, y), (W, y)], fill=mix((16, 10, 34), (150, 26, 30), t * 0.95))
    import random, math
    rnd = random.Random(7)
    for _ in range(90):                                  # blurred crowd + camera flashes
        x, y = rnd.randrange(W), rnd.randrange(40, 180)
        c = rnd.choice([(70, 40, 60), (90, 50, 60), (60, 34, 54)])
        d.ellipse([x, y, x + rnd.randrange(8, 18), y + rnd.randrange(8, 16)], fill=c)
    for _ in range(26):
        x, y = rnd.randrange(W), rnd.randrange(30, 170)
        d.ellipse([x, y, x + 7, y + 7], fill=(255, 250, 220))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))       # soft stadium light beams
    gd = ImageDraw.Draw(glow)
    for k in (40, 300, 560, 760):
        gd.polygon([(k, 0), (k + 44, 0), (k + 200, H), (k + 120, H)], fill=(255, 240, 200, 30))
    im.alpha_composite(glow)
    d.rectangle([0, 244, W, H], fill=(38, 112, 48))
    champion(im, faces, 210, 250, 0.62)
    for _ in range(190):                                 # confetti in Spain colours
        x, y = rnd.randrange(W), rnd.randrange(240)
        d.rectangle([x, y, x + 6, y + 4], fill=rnd.choice([(202, 22, 34), (250, 200, 24), WHITE, GOLD]))
    def fit(txt, size, col, box, y, sw=4):
        t = text_img(txt, size, col, INK, sw)
        if t.width > box:
            t = t.resize((box, max(1, int(t.height * box / t.width))), Image.LANCZOS)
        im.alpha_composite(t, (400 + (420 - t.width) // 2, y))
        return t.height
    y = 42
    y += fit("GAME RELEASED!!", 58, (255, 214, 60), 410, y, 5) + 10
    y += fit("SPAIN - 2026", 34, WHITE, 380, y) + 2
    y += fit("WORLD CHAMPIONS", 34, WHITE, 380, y) + 10
    fit("PLAY THE WORLD CUP NOW", 22, (255, 220, 140), 340, y, 3)
    return pixelate(im, 3)


def make_banner_wcpack(pack_img, icon_imgs):
    W, H = 840, 270
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=mix((14, 22, 60), (40, 70, 150), y / H))
    for k in range(12):                                  # rays behind the pack
        import math
        a = k * math.tau / 12
        d.polygon([(150, 135), (150 + math.cos(a) * 400, 135 + math.sin(a) * 400),
                   (150 + math.cos(a + 0.18) * 400, 135 + math.sin(a + 0.18) * 400)], fill=(60, 90, 170))
    p = pack_img.resize((150, 210), Image.NEAREST)
    im.alpha_composite(p, (75, 30))
    for j, face in enumerate(icon_imgs):                 # fanned icon portraits
        f = face.resize((110, 110), Image.NEAREST)
        x, y = 470 + j * 110, 110
        d.rounded_rectangle([x - 6, y - 6, x + 116, y + 150], 12, fill=(226, 186, 72))
        d.rounded_rectangle([x, y, x + 110, y + 144], 10, fill=(250, 246, 234))
        im.alpha_composite(f, (x, y + 4))
    t = text_img("WORLD CUP PACK", 54, GOLD, INK, 5)
    im.alpha_composite(t, (260, 16))
    s = text_img("ICONS INSIDE  -  CLICK TO OPEN", 26, WHITE, INK, 3)
    im.alpha_composite(s, (270, 80))
    return pixelate(im, 3)


def make_banner_soon():
    W, H = 840, 270
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=mix((28, 30, 36), (50, 54, 64), y / H))
    for k in range(-H, W, 40):
        d.line([(k, H), (k + H, 0)], fill=(44, 46, 54), width=14)
    # padlock
    d.rounded_rectangle([380, 110, 460, 190], 10, fill=(150, 150, 160))
    d.arc([390, 60, 450, 140], 180, 360, fill=(150, 150, 160), width=14)
    d.rectangle([414, 138, 426, 162], fill=(60, 60, 70))
    t = text_img("COMING SOON", 56, (200, 200, 210), INK, 5)
    im.alpha_composite(t, ((W - t.width) // 2, 16))
    return pixelate(im, 3)


# ======================================================================= stadiums
def _crowd(d, x0, y0, x1, y1, rnd, cols, dark=0.0, flash=0):
    """A block of packed pixel fans - chunky enough to read after pixelating."""
    step = 12
    for y in range(y0, y1, step):
        row = (y - y0) // step
        for x in range(x0 + (row % 2) * 6, x1, step):
            c = rnd.choice(cols)
            k = 0.6 + 0.4 * ((y - y0) / max(1, y1 - y0))
            d.rectangle([x, y + 4, x + 7, y + 10], fill=shade(c, k * (1 - dark)))       # body
            d.rectangle([x + 2, y, x + 6, y + 4], fill=shade(rnd.choice(SKIN_TONES), k * (1 - dark)))
    for _ in range(flash):
        fx, fy = rnd.randrange(x0, max(x0 + 1, x1)), rnd.randrange(y0, max(y0 + 1, y1))
        d.rectangle([fx - 3, fy - 3, fx + 4, fy + 4], fill=(255, 252, 226))


SKIN_TONES = [(238, 200, 170), (212, 166, 126), (166, 116, 84), (120, 80, 58), (86, 58, 44)]


def _floodlight(d, cx, top, h, on=True):
    pole = (96, 100, 112)
    d.rectangle([cx - 9, top, cx + 9, top + h], fill=pole)
    for y in range(top + 20, top + h, 30):                     # lattice
        d.line([(cx - 9, y), (cx + 9, y + 18)], fill=(70, 74, 86), width=4)
    d.rectangle([cx - 46, top - 70, cx + 46, top + 6], fill=(62, 66, 78))
    for r in range(4):
        for c in range(6):
            col = (255, 248, 210) if on else (126, 130, 142)
            d.rectangle([cx - 40 + c * 14, top - 62 + r * 17, cx - 30 + c * 14, top - 50 + r * 17], fill=col)


def make_stadium(i, W=1920, H=930):
    """Side-on stadium behind the pitch: packed tiers, roof, floodlights, screen."""
    import random as _r
    rnd = _r.Random(20 + i)
    kind = ("day", "sunset", "night", "rain")[i]
    sky = {"day": ((88, 164, 232), (186, 222, 248)),
           "sunset": ((84, 54, 126), (244, 152, 98)),
           "night": ((8, 12, 30), (26, 36, 72)),
           "rain": ((54, 62, 78), (126, 136, 152))}[kind]
    dark = {"day": 0.0, "sunset": 0.2, "night": 0.45, "rain": 0.3}[kind]
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=mix(sky[0], sky[1], min(1.0, y / 420)))
    if kind == "day":
        for cx, cy, s in ((330, 120, 1.0), (1220, 80, 1.3), (1700, 170, 0.8)):
            for dx, dy, r in ((0, 0, 44), (50, 10, 32), (-46, 12, 28), (20, -20, 28)):
                d.ellipse([cx + dx * s - r * s, cy + dy * s - r * s,
                           cx + dx * s + r * s, cy + dy * s + r * s], fill=(248, 250, 255))
    if kind == "sunset":
        d.ellipse([1380, 150, 1560, 330], fill=(255, 216, 130))
    if kind == "night":
        for _ in range(130):
            x, y = rnd.randrange(W), rnd.randrange(250)
            d.rectangle([x, y, x + 3, y + 3], fill=(220, 228, 255))

    kit = [(196, 42, 52), (232, 232, 236), (34, 62, 150), (240, 196, 44),
           (26, 130, 68), (26, 28, 36), (236, 130, 40), (120, 40, 150)]
    rnd.shuffle(kit)
    cols = kit[:4] + [(232, 232, 236), (28, 30, 40)]

    # floodlight towers first (they stand behind the roof)
    for fx in (150, W - 150):
        _floodlight(d, fx, 150, 190, on=kind != "day")
    # roof over the stand
    d.polygon([(0, 250), (W, 250), (W, 330), (0, 330)], fill=shade((26, 30, 40), 1 - dark))
    for x in range(0, W, 150):
        d.rectangle([x, 250, x + 10, 340], fill=shade((44, 50, 64), 1 - dark))
    d.rectangle([0, 330, W, 348], fill=shade((54, 60, 76), 1 - dark))
    # upper tier
    _crowd(d, 0, 352, W, 520, rnd, cols, dark, flash=34 if kind == "night" else 6)
    d.rectangle([0, 520, W, 556], fill=shade((48, 52, 66), 1 - dark))              # walkway + front wall
    for bx in range(80, W - 260, 420):                                             # banners
        c = rnd.choice(kit)
        d.rectangle([bx, 524, bx + 260, 552], fill=c)
        d.rectangle([bx + 6, 530, bx + 254, 546], fill=(244, 244, 246))
    # lower tier
    _crowd(d, 0, 560, W, 800, rnd, cols, dark, flash=44 if kind == "night" else 8)
    d.rectangle([0, 800, W, 828], fill=shade((42, 46, 58), 1 - dark))
    # big screen on the roof
    sx, sy = 1300, 120
    d.rectangle([sx - 12, sy - 12, sx + 332, sy + 192], fill=(22, 24, 32))
    d.rectangle([sx, sy, sx + 320, sy + 180], fill=(12, 34, 20))
    t = text_img("RAGDOLL", 40, GOLD, INK, 3)
    im.alpha_composite(t, (sx + 160 - t.width // 2, sy + 32))
    t2 = text_img("FOOTBALL", 32, WHITE, INK, 3)
    im.alpha_composite(t2, (sx + 160 - t2.width // 2, sy + 98))
    d.rectangle([sx + 130, sy + 192, sx + 190, sy + 250], fill=(60, 64, 76))
    if kind != "day":
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        for fx in (150, W - 150):
            gd.polygon([(fx - 46, 90), (fx + 46, 90), (fx + 560, H), (fx - 560, H)], fill=(255, 244, 200, 24))
        im.alpha_composite(glow)
    # advertising boards along the touchline
    for j, bx in enumerate(range(0, W, 240)):
        base = [(18, 32, 92), (180, 26, 40), (20, 20, 26), (236, 190, 60)][j % 4]
        d.rectangle([bx, 836, bx + 236, 916], fill=shade(base, 1 - dark))
        d.rectangle([bx + 8, 846, bx + 228, 906], fill=shade(mix(base, WHITE, 0.82), 1 - dark))
        ad = text_img(["RAGDOLL FC", "SMALL WORLD", "PIXEL CUP", "KICK IT"][j % 4], 26, shade(base, 0.75), None, 0)
        if ad.width > 206:
            ad = ad.resize((206, int(ad.height * 206 / ad.width)), Image.LANCZOS)
        im.alpha_composite(ad, (bx + 118 - ad.width // 2, 864))
    d.rectangle([0, 916, W, H], fill=shade((30, 78, 38), 1 - dark))
    if kind == "rain":
        rain = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        rd = ImageDraw.Draw(rain)
        for _ in range(420):
            x, y = rnd.randrange(-40, W), rnd.randrange(H)
            rd.line([(x, y), (x + 12, y + 30)], fill=(200, 216, 240, 110), width=2)
        im.alpha_composite(rain)
    return pixelate(im, 3)


def make_shop_bg(W=1920, H=1080):
    """Dark store backdrop: light rays, foil sheen, a shelf glow."""
    import math as _m
    import random as _r
    rnd = _r.Random(9)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=mix((10, 16, 40), (28, 44, 96), y / H))
    cx, cy = W // 2, int(H * 0.42)
    for k in range(24):                                     # slow rays from the middle
        a = k * _m.tau / 24
        d.polygon([(cx, cy), (cx + _m.cos(a) * 2200, cy + _m.sin(a) * 2200),
                   (cx + _m.cos(a + 0.09) * 2200, cy + _m.sin(a + 0.09) * 2200)],
                  fill=(20, 34, 78) if k % 2 else (14, 24, 58))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r in range(9):
        rr = 860 - r * 90
        gd.ellipse([cx - rr, cy - rr // 2, cx + rr, cy + rr // 2], fill=(90, 140, 255, 8))
    im.alpha_composite(glow)
    for k in range(-H, W, 130):                             # foil sheen
        d.polygon([(k, H), (k + 40, H), (k + 40 + H * 0.5, 0), (k + H * 0.5, 0)], fill=(24, 40, 92))
    for _ in range(90):                                     # floating gold sparks
        x, y = rnd.randrange(W), rnd.randrange(H)
        s = rnd.choice([3, 4, 6])
        d.rectangle([x, y, x + s, y + s], fill=rnd.choice([(236, 200, 90), (150, 190, 255), (255, 255, 255)]))
    vign = Image.new("RGBA", (W, H), (0, 0, 0, 0))          # soft vignette
    vd = ImageDraw.Draw(vign)
    for k in range(10):
        vd.rectangle([0, 0, W, 26 * k], fill=(4, 8, 24, 10))
        vd.rectangle([0, H - 26 * k, W, H], fill=(4, 8, 24, 10))
    im.alpha_composite(vign)
    return pixelate(im, 3)


# ======================================================================= badges + extra flags
def make_wc_badge(W=240, H=280):
    """World Cup crest for World Cup cards (generic trophy on a shield)."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(W // 2, H - 6), (8, H - 90), (8, 20), (W // 2, 4), (W - 8, 20), (W - 8, H - 90)]
    d.polygon(pts, fill=GOLD)
    inner = [(W // 2, H - 26), (26, H - 100), (26, 34), (W // 2, 20), (W - 26, 34), (W - 26, H - 100)]
    d.polygon(inner, fill=(20, 32, 84))
    for k in range(3):
        d.polygon([(26, 150 + k * 16), (W - 26, 110 + k * 16), (W - 26, 118 + k * 16), (26, 158 + k * 16)],
                  fill=[(200, 30, 44), (240, 240, 240), (30, 110, 60)][k])
    trophy(d, W // 2, 44, 3, GOLD)
    t = text_img("WORLD CUP", 26, GOLD, INK, 3)
    im.alpha_composite(t, ((W - t.width) // 2, H - 108))
    return pixelate(im, 3)


def make_flag_usa(W=240, H=160):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(13):
        d.rectangle([0, k * H / 13, W, (k + 1) * H / 13], fill=(178, 34, 52) if k % 2 == 0 else WHITE)
    d.rectangle([0, 0, W * 0.42, H * 7 / 13], fill=(40, 52, 120))
    for r in range(5):
        for c in range(6):
            x, y = 10 + c * 16 + (r % 2) * 8, 8 + r * 16
            d.rectangle([x, y, x + 4, y + 4], fill=WHITE)
    return pixelate(im, 3)


def make_flag_ksa(W=240, H=160):
    """Green field with a white sword (script left out)."""
    im = Image.new("RGBA", (W, H), (0, 108, 53, 255))
    d = ImageDraw.Draw(im)
    for x in range(50, 190, 18):                         # stylised band where the script sits
        d.rectangle([x, 50, x + 10, 64], fill=WHITE)
    d.rectangle([50, 108, 184, 114], fill=WHITE)         # sword blade
    d.polygon([(184, 104), (198, 111), (184, 118)], fill=WHITE)
    d.rectangle([56, 102, 62, 120], fill=WHITE)          # hilt
    return pixelate(im, 3)



# ======================================================================= Neymar Jr signature event
def make_neymar_sprites():
    """In-match pieces for the Neymar Jr signature card (Brazil kit, 10)."""
    kit = MS.KITS["BRA"]
    sk, hr = MS.SKIN["tan"], (244, 222, 132)            # bleached, lighter than his skin
    base = os.path.join(OUT, "SIG_neymar")
    MS.make_head(sk, hr, "short", "stubble", ()).save(base + "_head.png")
    MS.make_torso(kit, 10).save(base + "_torso.png")
    MS.make_arm(kit, sk).save(base + "_arm.png")
    MS.make_leg(kit, sk, (255, 112, 182)).save(base + "_leg.png")


def brazil_flag(d, x0, y0, W, H, band=True):
    d.rectangle([x0, y0, x0 + W, y0 + H], fill=(0, 146, 64))
    d.polygon([(x0 + W * 0.08, y0 + H / 2), (x0 + W / 2, y0 + H * 0.08), (x0 + W * 0.92, y0 + H / 2),
               (x0 + W / 2, y0 + H * 0.92)], fill=(254, 214, 0))
    r = H * 0.26
    d.ellipse([x0 + W / 2 - r, y0 + H / 2 - r, x0 + W / 2 + r, y0 + H / 2 + r], fill=(22, 44, 128))
    if band:
        d.arc([x0 + W / 2 - r * 1.6, y0 + H / 2 - r * 0.6, x0 + W / 2 + r * 1.2, y0 + H / 2 + r * 2.2],
              215, 330, fill=WHITE, width=max(2, int(H * 0.03)))


def scrawl(d, x, y, s, col=GOLD, width=5):
    """A made-up signature squiggle (not a real autograph)."""
    import math as _m
    pts = []
    for i in range(60):
        t = i / 59.0
        pts.append((x + t * 180 * s, y + _m.sin(t * 13.0) * 22 * s * (1 - t * 0.5) - t * 30 * s))
    d.line(pts, fill=col, width=width)
    d.line([(x + 20 * s, y + 30 * s), (x + 200 * s, y - 10 * s)], fill=col, width=width)


def make_banner_neymar(face):
    W, H = 840, 270
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    brazil_flag(d, -60, -40, W + 120, H + 80)
    veil = Image.new("RGBA", (W, H), (0, 40, 20, 90))
    im.alpha_composite(veil)
    f = face.resize((250, 250), Image.NEAREST)
    im.alpha_composite(f, (10, 20))
    d = ImageDraw.Draw(im)
    scrawl(d, 270, 250, 0.9, (255, 236, 150), 5)
    # the prize card on the right
    cx0 = 640
    d.rounded_rectangle([cx0, 18, cx0 + 170, 252], 14, fill=(236, 198, 96))
    d.rounded_rectangle([cx0 + 8, 26, cx0 + 162, 244], 10, fill=(0, 120, 56))
    im.alpha_composite(face.resize((140, 140), Image.NEAREST), (cx0 + 15, 70))
    t = text_img("120", 30, WHITE, INK, 3)
    im.alpha_composite(t, (cx0 + 16, 34))
    t = text_img("NEYMAR JR", 20, (255, 226, 120), INK, 3)
    im.alpha_composite(t, (cx0 + 85 - t.width // 2, 212))
    def put(txt, size, col, y, sw=4):
        t = text_img(txt, size, col, INK, sw)
        if t.width > 350:
            t = t.resize((350, int(t.height * 350 / t.width)), Image.LANCZOS)
        im.alpha_composite(t, (450 - t.width // 2, y))
    put("THE WORLD'S", 40, (255, 226, 60), 22, 5)
    put("GAME BOX", 40, (255, 226, 60), 72, 5)
    put("NEYMAR JR SIGNATURE", 26, WHITE, 136)
    put("FIRST DRAW FREE!", 28, (140, 255, 160), 186)
    return pixelate(im, 3)



def make_event_bg(W=1920, H=1080):
    """Big Brazil flag, softened, for the Game Box screen."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    brazil_flag(d, -200, -120, W + 400, H + 240)
    veil = Image.new("RGBA", (W, H), (0, 30, 16, 120))
    im.alpha_composite(veil)
    return pixelate(im, 3)


def make_box_neymar(W=300, H=420):
    """The Game Box itself (used when a reward flies out)."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 150, W - 20, H - 20], 16, fill=(0, 120, 56))
    d.rounded_rectangle([10, 100, W - 10, 170], 12, fill=(0, 150, 70))
    d.rectangle([W // 2 - 24, 100, W // 2 + 24, H - 20], fill=(254, 214, 0))
    d.rectangle([10, 120, W - 10, 146], fill=(254, 214, 0))
    d.ellipse([W // 2 - 90, 40, W // 2 - 4, 110], outline=(254, 214, 0), width=18)
    d.ellipse([W // 2 + 4, 40, W // 2 + 90, 110], outline=(254, 214, 0), width=18)
    d.ellipse([W // 2 - 70, 250, W // 2 + 70, 390], fill=(24, 46, 130))
    t = text_img("10", 70, WHITE, INK, 4)
    im.alpha_composite(t, ((W - t.width) // 2, 285))
    return pixelate(im, 3)



# ======================================================================= per-card faces (pool A + B)
def load_card_db(path=None):
    """Read CARD_DB straight out of ragdoll_football.py (no pygame needed)."""
    import ast
    path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "ragdoll_football.py")
    tree = ast.parse(open(path, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CARD_DB":
            rows = ast.literal_eval(node.value)
            keys = ("id", "name", "kind", "team", "slot", "tier", "rating", "pos", "number", "pack",
                    "sho", "str", "design", "desc")
            cards = [dict(zip(keys, r)) for r in rows]
            return cards + load_star_cards(tree)
    return []


def load_star_cards(tree=None):
    """The Star Signing Elite cards, read out of STAR_SIGNINGS in ragdoll_football.py."""
    import ast
    if tree is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ragdoll_football.py")
        tree = ast.parse(open(path, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "STAR_SIGNINGS":
            out = []
            for slug, name, pos, ovr, price, nation, club, num, desc in ast.literal_eval(node.value):
                out.append({"id": "STAR_" + slug, "slug": slug, "name": name, "kind": "star", "team": club,
                            "slot": 0, "tier": "good", "rating": ovr, "pos": pos, "number": num, "pack": None,
                            "design": "starsign", "nation": nation, "price": price, "desc": desc})
            return out + load_rookie_cards(tree) + load_no10_cards(tree) + load_wg_cards(tree)
    return []


def load_wg_cards(tree):
    """THE WORLD'S GAME: the players the Essence shop's slot turns through."""
    import ast
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "WORLDS_GAME":
            return [{"id": "WG_" + slug, "slug": slug, "name": name, "kind": "wg", "team": nation, "slot": 0,
                     "tier": "good", "rating": ovr, "pos": pos, "number": num, "pack": None,
                     "design": "worldsgame", "nation": nation, "desc": desc}
                    for slug, name, pos, ovr, nation, num, desc in ast.literal_eval(node.value)]
    return []


def load_no10_cards(tree):
    """The No. 10 pack's playmakers (pool A / B / C)."""
    import ast
    out = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") in ("NO10_POOL_A", "NO10_POOL_B",
                                                                                  "NO10_POOL_C"):
            for slug, name, pos, ovr, nation, num, desc in ast.literal_eval(node.value):
                out.append({"id": "NO10_" + slug, "slug": slug, "name": name, "kind": "no10", "team": nation,
                            "slot": 0, "tier": "good", "rating": ovr, "pos": pos, "number": num, "pack": 4,
                            "design": "no10", "nation": nation, "desc": desc})
    return out


def load_rookie_cards(tree):
    import ast
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ROOKIE_CARDS":
            return [{"id": "ROOKIE_" + slug, "slug": slug, "name": name, "kind": "rookie", "team": club, "slot": 0,
                     "tier": "alright", "rating": ovr, "pos": pos, "number": num, "pack": None, "design": "beginner",
                     "nation": nation, "desc": desc}
                    for slug, name, pos, ovr, nation, club, num, desc in ast.literal_eval(node.value)]
    return []


def card_pool(c):
    if c["design"] in ("icon", "signature") or c["rating"] >= 120:
        return "A"
    return "B" if c["rating"] >= 100 else "C"


MS_CODE = {"NET": "NED", "SPA": "ESP"}


REN_KIT = dict(base=(22, 22, 30), alt=(22, 22, 30), pattern="plain", trim=(60, 230, 240), number=(240, 244, 250),
               shorts=(22, 22, 30), shorts_trim=(60, 230, 240), socks=(22, 22, 30), sock_trim=(246, 142, 194),
               badge=((60, 230, 240), (246, 142, 194)), stars=0)
BLUE_KIT = dict(base=(40, 90, 210), alt=(40, 90, 210), pattern="plain", trim=WHITE, number=WHITE,
                shorts=WHITE, shorts_trim=(40, 90, 210), socks=(40, 90, 210), sock_trim=WHITE,
                badge=(WHITE, (40, 90, 210)), stars=0)


# THE WORLD'S GAME: each player in the kit and the hair of the picture his card was drawn from.
# slug: (skin, hair, portrait style, beard, extras)
WG_LOOKS = {"messi": ("light", "darkbrown", "long", None, ("nohb",)),
            "ronaldo": ("tan", "darkbrown", "short", None, ("nohb",)),
            "lewandowski": ("light", "darkbrown", "neat", None, ("nohb",))}
_SKY, _DNAVY = (124, 178, 232), (18, 26, 66)
WG_KITS = {
    "messi": dict(base=_DNAVY, alt=_DNAVY, pattern="plain", trim=_SKY, number=WHITE, shorts=_DNAVY,
                  shorts_trim=_SKY, socks=_DNAVY, sock_trim=_SKY, badge=(WHITE, _SKY), stars=0),
    "ronaldo": dict(base=(182, 22, 38), alt=(182, 22, 38), pattern="plain", trim=(0, 102, 60), number=GOLD,
                    shorts=(0, 102, 60), shorts_trim=(182, 22, 38), socks=(182, 22, 38), sock_trim=(0, 102, 60),
                    badge=(GOLD, (0, 102, 60)), stars=0),
    "lewandowski": dict(base=WHITE, alt=(236, 236, 240), pattern="plain", trim=(220, 22, 60), number=(220, 22, 60),
                        shorts=(220, 22, 60), shorts_trim=WHITE, socks=WHITE, sock_trim=(220, 22, 60),
                        badge=((220, 22, 60), WHITE), stars=0),
}


def card_kit(c):
    if c["design"] == "prodigy":
        return REN_KIT
    if c["kind"] == "wg":
        return WG_KITS.get(c["id"][3:]) or MS.KITS.get(MS_CODE.get(c["team"], c["team"]))
    if c["kind"] == "no10":
        return MS.KITS.get(MS_CODE.get(c["team"], c["team"]))
    if c["kind"] in ("star", "rookie"):
        return MS.star_kit(c["id"].split("_", 1)[1], c["team"])
    if c["kind"] == "club":
        return MS.CLUB_KITS.get(c["team"])
    return MS.KITS.get(MS_CODE.get(c["team"], c["team"]))


ICON_EXTRAS = {"aoyagi": ("eyes_blue", "nohb")}


def card_look(c):
    """(skin, hair, style, beard, extras) for a card's player."""
    slug = c["id"].split("_")[-1]
    if c["kind"] == "star":
        return MS.STAR_LOOKS[c["id"][5:]]
    if c["kind"] == "rookie":
        return MS.ROOKIE_LOOKS[c["id"][7:]]
    if c["kind"] == "no10":
        return MS.NO10_LOOKS[c["id"][5:]]
    if c["kind"] == "wg":
        return WG_LOOKS.get(c["id"][3:], ("tan", "black", "short", None, ("nohb",)))
    if c["design"] in ("icon", "signature", "prodigy") and slug in ICONS:
        sk, hr, st, bd, _shirt = ICONS[slug]
        return sk, hr, st, bd, ICON_EXTRAS.get(slug, ())
    table = MS.CLUB_TEAMS if c["kind"] == "club" else MS.TEAMS
    code = c["team"] if c["kind"] == "club" else MS_CODE.get(c["team"], c["team"])
    for row in table.get(code, []):
        if row[0] == slug:
            _slug, _name, _num, skin, hair, style, facial, _boots, extras = row
            style = {"bigcurly": "afro", "long": "long", "swept": "swept"}.get(style, style)
            return skin, hair, style, facial, ("nohb",) + tuple(extras)
    return "tan", "black", "short", None, ("nohb",)


def make_card_faces(cards):
    made = 0
    for c in cards:
        if card_pool(c) == "C" and c["kind"] not in ("rookie", "no10"):
            continue
        kit = card_kit(c) or {"base": (40, 60, 140), "trim": WHITE, "alt": (40, 60, 140), "pattern": "plain"}
        skin, hair, style, beard, extras = card_look(c)
        shirt = (kit["base"], kit.get("trim", WHITE), kit.get("alt", kit["base"]), kit.get("pattern", "plain"))
        portrait(skin, hair, style, beard, shirt, extras).save(os.path.join(OUT, "%s_portrait.png" % c["id"]))
        made += 1
    return made



# ======================================================================= card templates (pool A / B)
TPL_W, TPL_H = 400, 500
BODY = (66, 34, 334, 458)            # the card itself inside the template (x0, y0, x1, y1)


def _grad(d, box, top, bot):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        d.line([(x0, y), (x1, y)], fill=mix(top, bot, (y - y0) / max(1, y1 - y0)))


def _body_mask(radius=18):
    m = Image.new("L", (TPL_W, TPL_H), 0)
    ImageDraw.Draw(m).rounded_rectangle(BODY, radius, fill=255)
    return m


def _gold_frame(d, box, w=10, notch=False):
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0 - w, y0 - w, x1 + w, y1 + w], 22, outline=(146, 104, 28), width=w)
    d.rounded_rectangle([x0 - w + 3, y0 - w + 3, x1 + w - 3, y1 + w - 3], 20, outline=(242, 206, 110), width=w - 5)
    d.rounded_rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], 18, outline=(255, 238, 170), width=2)
    if notch:                                            # little crown on top
        cx = (x0 + x1) // 2
        d.polygon([(cx - 34, y0 - w), (cx - 22, y0 - w - 18), (cx - 10, y0 - w - 6), (cx, y0 - w - 22),
                   (cx + 10, y0 - w - 6), (cx + 22, y0 - w - 18), (cx + 34, y0 - w)], fill=(236, 196, 90),
                  outline=(146, 104, 28))


def make_icon_template():
    """Blue crystal card with gold wings and a hexagon gem (icons)."""
    import random as _r
    import math as _m
    rnd = _r.Random(3)
    im = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # the card body
    body = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    _grad(bd, BODY, (20, 36, 130), (10, 18, 70))
    for _ in range(55):                                   # crystals, mostly top + right
        x = rnd.uniform(BODY[0], BODY[2]); y = rnd.uniform(BODY[1], BODY[1] + 300)
        if rnd.random() < 0.4:
            x = rnd.uniform(BODY[0] + 150, BODY[2])
        sz = rnd.uniform(10, 38); a = rnd.uniform(0, _m.tau)
        pts = [(x + _m.cos(a + j * 1.7) * sz * (0.6 + 0.5 * (j % 2)), y + _m.sin(a + j * 1.7) * sz * 1.4)
               for j in range(4)]
        col = rnd.choice([(40, 80, 220), (60, 110, 250), (30, 60, 180), (110, 150, 255), (22, 40, 150)])
        bd.polygon(pts, fill=col)
        bd.line([pts[0], pts[2]], fill=(200, 220, 255), width=2)
    # gold swirl band across the middle
    bd.polygon([(BODY[0], 250), (BODY[2], 150), (BODY[2], 190), (BODY[0], 300)], fill=(226, 180, 70))
    bd.polygon([(BODY[0], 262), (BODY[2], 162), (BODY[2], 170), (BODY[0], 272)], fill=(255, 232, 150))
    # gold plate for the name
    _grad(bd, (BODY[0], 330, BODY[2], BODY[3]), (236, 198, 100), (176, 130, 40))
    for x in range(BODY[0], BODY[2], 14):                 # scale texture
        for y in range(338, BODY[3], 12):
            bd.arc([x, y, x + 14, y + 12], 0, 180, fill=(206, 164, 64), width=2)
    body.putalpha(Image.composite(body.split()[3], Image.new("L", body.size, 0), _body_mask()))
    im.alpha_composite(body)
    _gold_frame(d, BODY, 11)
    # big gold wings over the lower corners, fanning outwards
    for side in (-1, 1):
        root = (TPL_W // 2 + side * 138, 372)
        for k in range(9):
            ang = _m.radians(250 - k * 17) if side < 0 else _m.radians(-70 + k * 17)
            ln = 58 + (k % 3) * 12 - abs(k - 4) * 3
            tip = (root[0] + _m.cos(ang) * ln, root[1] - _m.sin(ang) * ln * 1.5)
            a2 = ang + 0.32 * (1 if side > 0 else -1)
            base2 = (root[0] + _m.cos(a2) * 26, root[1] - _m.sin(a2) * 36)
            d.polygon([root, tip, base2], fill=(236, 196, 90) if k % 2 else (206, 158, 58), outline=(130, 90, 20))
        for k in range(4):                                # lower blades
            y = 400 + k * 18
            d.polygon([(TPL_W // 2 + side * 120, y), (TPL_W // 2 + side * (176 - k * 6), y + 24),
                       (TPL_W // 2 + side * 128, y + 30)], fill=(236, 196, 90), outline=(130, 90, 20))
        for k in range(3):                                # top spikes
            d.polygon([(TPL_W // 2 + side * 110, 44 + k * 16), (TPL_W // 2 + side * (170 - k * 10), 6 + k * 20),
                       (TPL_W // 2 + side * 128, 70 + k * 16)], fill=(236, 196, 90), outline=(130, 90, 20))
    # hexagon gem
    cx, cy, r = TPL_W // 2, BODY[3] + 6, 26
    hexa = [(cx + _m.cos(_m.pi / 6 + j * _m.pi / 3) * r, cy + _m.sin(_m.pi / 6 + j * _m.pi / 3) * r) for j in range(6)]
    d.polygon([(x, y) for x, y in hexa], fill=(236, 196, 90), outline=(130, 90, 20))
    inner = [(cx + (x - cx) * 0.68, cy + (y - cy) * 0.68) for x, y in hexa]
    d.polygon(inner, fill=(40, 90, 230))
    d.polygon([inner[0], inner[1], (cx, cy)], fill=(120, 170, 255))
    d.polygon([inner[3], inner[4], (cx, cy)], fill=(20, 50, 160))
    return im


def make_poolb_template():
    """White marble card, gold laurel wreath, navy band (pool B)."""
    import random as _r
    import math as _m
    rnd = _r.Random(5)
    im = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    _grad(bd, BODY, (246, 246, 248), (226, 228, 232))
    for _ in range(9):                                     # marble veins
        x, y = rnd.uniform(BODY[0], BODY[2]), rnd.uniform(BODY[1], BODY[3] - 120)
        pts = [(x, y)]
        for _j in range(6):
            x += rnd.uniform(-10, 30); y += rnd.uniform(8, 30)
            pts.append((x, y))
        bd.line(pts, fill=(196, 198, 206), width=2)
    # navy scalloped block on the right + gold diagonal band
    bd.polygon([(BODY[2] - 80, 260), (BODY[2], 150), (BODY[2], 330), (BODY[2] - 60, 330)], fill=(24, 34, 84))
    for x in range(BODY[2] - 76, BODY[2], 16):
        for y in range(210, 330, 16):
            bd.ellipse([x, y, x + 14, y + 12], fill=(40, 54, 120))
    bd.polygon([(BODY[0] + 40, BODY[1]), (BODY[0] + 80, BODY[1]), (BODY[2] - 60, 330), (BODY[2] - 100, 330)],
               fill=(230, 190, 84))
    bd.line([(BODY[0] + 60, BODY[1]), (BODY[2] - 80, 330)], fill=(255, 236, 160), width=3)
    for k in range(9):                                     # little gold stars in an arc
        a = _m.pi * (0.9 + k * 0.07)
        sx, sy = BODY[0] + 150 + _m.cos(a) * 110, BODY[1] + 150 + _m.sin(a) * 110
        bd.line([(sx - 5, sy), (sx + 5, sy)], fill=(214, 170, 60), width=2)
        bd.line([(sx, sy - 5), (sx, sy + 5)], fill=(214, 170, 60), width=2)
    # navy wave band at the bottom (name area)
    pts = [(BODY[0], 340)]
    for x in range(BODY[0], BODY[2] + 1, 8):
        pts.append((x, 336 + _m.sin((x - BODY[0]) / 30.0) * 8))
    pts += [(BODY[2], BODY[3]), (BODY[0], BODY[3])]
    bd.polygon(pts, fill=(18, 28, 76))
    bd.line(pts[1:-2], fill=(236, 196, 90), width=4)
    body.putalpha(Image.composite(body.split()[3], Image.new("L", body.size, 0), _body_mask()))
    im.alpha_composite(body)
    _gold_frame(d, BODY, 10)
    # laurel wreath hugging both sides, from the bottom up
    for side in (-1, 1):
        prev = None
        for k in range(15):
            t = k / 14.0
            x = TPL_W / 2 + side * (40 + 132 * _m.sin(min(1.0, t * 1.6) * _m.pi / 2))
            y = TPL_H - 20 - t * 390
            if prev:
                d.line([prev, (x, y)], fill=(170, 124, 36), width=5)
            prev = (x, y)
            ang = _m.atan2(-390 / 14, side * 20) + (0.9 if side > 0 else -0.9)
            for leaf in (-1, 1):
                la = ang + leaf * 0.9
                lx, ly = x + _m.cos(la) * 16, y + _m.sin(la) * 16
                nx, ny = -_m.sin(la) * 7, _m.cos(la) * 7
                d.polygon([(x, y), (lx + nx, ly + ny), (x + _m.cos(la) * 30, y + _m.sin(la) * 30), (lx - nx, ly - ny)],
                          fill=(236, 196, 90) if leaf > 0 else (214, 170, 66), outline=(150, 108, 30))
    d.polygon([(TPL_W / 2 - 30, TPL_H - 22), (TPL_W / 2 + 30, TPL_H - 22), (TPL_W / 2, TPL_H - 4)],
              fill=(214, 170, 66))
    # gold ball emblem at the bottom
    cx, cy = TPL_W // 2, BODY[3] + 4
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=(236, 196, 90), outline=(146, 104, 28), width=3)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(200, 156, 56))
    d.polygon([(cx, cy - 8), (cx + 8, cy - 2), (cx + 5, cy + 8), (cx - 5, cy + 8), (cx - 8, cy - 2)], fill=(120, 84, 20))
    return im


def make_team_template(c1, c2, code):
    """Club / nation pool A card: team colours, side scarves, gold frame with a crown."""
    import math as _m
    im = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    dark = shade(c1, 0.45)
    # scarves hanging down both sides
    for side in (-1, 1):
        x = TPL_W // 2 + side * 156
        pts = [(x - 16, 60), (x + 16, 56), (x + 20 + side * 6, 420), (x - 12 + side * 6, 424)]
        d.polygon(pts, fill=c1)
        for k in range(8):                                 # stripes
            y = 90 + k * 42
            d.polygon([(x - 15 + side * k * 0.7, y), (x + 17 + side * k * 0.7, y - 3),
                       (x + 17 + side * k * 0.7, y + 12), (x - 15 + side * k * 0.7, y + 15)], fill=c2)
        for f in range(6):                                 # fringe
            fx = x - 10 + f * 5 + side * 6
            d.line([(fx, 424), (fx, 446)], fill=c2, width=3)
    body = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    _grad(bd, BODY, shade(c1, 0.95), dark)
    for k in range(6):                                     # light streaks
        x = BODY[0] + 20 + k * 52
        bd.polygon([(x, BODY[1]), (x + 22, BODY[1]), (x - 60, BODY[3]), (x - 82, BODY[3])],
                   fill=shade(c1, 1.12 if k % 2 else 1.04))
    bd.polygon([(BODY[0], 300), (BODY[2], 250), (BODY[2], 262), (BODY[0], 312)], fill=mix(c2, WHITE, 0.3))
    _grad(bd, (BODY[0], 336, BODY[2], BODY[3]), shade(dark, 0.9), shade(dark, 0.55))
    bd.line([(BODY[0], 336), (BODY[2], 336)], fill=(236, 196, 90), width=3)
    body.putalpha(Image.composite(body.split()[3], Image.new("L", body.size, 0), _body_mask()))
    im.alpha_composite(body)
    _gold_frame(d, BODY, 11, notch=True)
    # gold number plate at the bottom
    cx, cy = TPL_W // 2, BODY[3] + 6
    d.ellipse([cx - 30, cy - 22, cx + 30, cy + 22], fill=(236, 196, 90), outline=(146, 104, 28), width=3)
    d.ellipse([cx - 24, cy - 16, cx + 24, cy + 16], fill=(250, 226, 150))
    return im


def make_sig_template():
    """The signature card: the holo family's silhouette, cast in gold.

    A Brazil flag flies behind it, darkened and warmed so the frame reads against it; inside,
    a dark green stage lit from above with the number 10 ghosted behind the player, and a
    laurel around the gem at the foot. Everything else on the card is drawn by the game."""
    import math as _m
    flag = None
    for cand in ("BRA.png", os.path.join(OUT, "BRA.png")):
        if os.path.exists(cand):
            flag = Image.open(cand)
            break
    x0, y0, x1, y1 = BODY
    cx = (x0 + x1) // 2
    im = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    # ---- the flag flying behind, spilling past the card on both sides
    if flag is not None:
        back = wave_flag(flag, TPL_W + 170, int((y1 - y0) * 1.0), 0.6, amp=0.085, folds=2.3)
        back = ImageEnhance.Brightness(back).enhance(0.44)
        back = ImageEnhance.Color(back).enhance(0.52)
        im.alpha_composite(back, (-85, y0 + 24))
    # ---- the card: a dark green stage, lit from the top
    card = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    _grad(cd, (x0 - 6, y0 - 6, x1 + 6, y1 + 6), (8, 54, 32), (2, 9, 7))
    beam = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    for k in range(26):                                    # a soft cone of gold light
        w = 26 + k * 10
        bd.polygon([(cx - 24, y0 - 10), (cx + 24, y0 - 10), (cx + w, y1), (cx - w, y1)],
                   fill=(255, 212, 108, 7))
    card.alpha_composite(beam)
    # ---- the shirt number ghosted behind the player
    f = ImageFont.truetype(FONT, 430)
    num = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(num)
    nd.text((cx, y0 + 190), "10", font=f, fill=(255, 226, 150, 34), anchor="mm",
            stroke_width=6, stroke_fill=(255, 240, 190, 76))
    card.alpha_composite(num)
    # ---- the plate the name sits on
    _grad(cd, (x0, 334, x1, y1), (6, 30, 20), (2, 6, 5))
    plate = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    for k in range(26):                                    # fades in rather than cutting a line
        pd.rectangle([x0, 334 + k, x1, 335 + k], fill=(4, 18, 12, 255 - k * 9))
    card.alpha_composite(plate)
    cd.line([(x0 + 26, 336), (x1 - 26, 336)], fill=(236, 198, 104), width=3)
    shadow = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))   # under the rating, top left
    sd = ImageDraw.Draw(shadow)
    for k in range(24):
        sd.ellipse([x0 - 130 + k * 6, y0 - 120 + k * 6, x0 + 200 - k * 6, y0 + 196 - k * 6],
                   fill=(2, 10, 8, 12))
    card.alpha_composite(shadow)
    shape = Image.new("L", (TPL_W, TPL_H), 0)
    ImageDraw.Draw(shape).polygon(_holo_card_path(BODY), fill=255)
    card.putalpha(Image.composite(card.split()[3], Image.new("L", card.size, 0), shape))
    im.alpha_composite(card)
    # ---- the frame: dark edge, gold sweep, white hairline
    d = ImageDraw.Draw(im)
    path = _holo_card_path(BODY)
    d.line(path + [path[0]], fill=(34, 24, 6), width=19, joint="curve")
    ring = Image.new("L", (TPL_W, TPL_H), 0)
    ImageDraw.Draw(ring).line(path + [path[0]], fill=255, width=13, joint="curve")
    im.paste(_holo_band((TPL_W, TPL_H), "SIG"), (0, 0), ring)
    d.line(path + [path[0]], fill=(255, 244, 198), width=2, joint="curve")
    inner_path = _holo_card_path((x0 + 12, y0 + 12, x1 - 12, y1 - 12))
    d.line(inner_path + [inner_path[0]], fill=(255, 232, 160, 130), width=2, joint="curve")
    # ---- laurel and gem at the foot
    gy = y1 + 5                                            # the game prints the shirt number here
    for side in (-1, 1):
        def stem(t):                                       # a sprig curving out from the gem and up
            return (cx + side * (24 + t * 70), gy + 16 - t * t * 40)
        d.line([stem(k / 18.0) for k in range(19)], fill=(168, 126, 40), width=4, joint="curve")
        for k in range(5):
            t = 0.16 + k * 0.19
            bx, by = stem(t)
            ax, ay = side * 70, -2.0 * t * 40
            base = _m.atan2(ay, ax)
            for lean in (0.85, -0.85):                     # one leaf each side of the stem
                ang = base + lean * side
                ln, wd = 21 - t * 6, 7.4 - t * 2.0
                ca, sa = _m.cos(ang), _m.sin(ang)
                leaf = []
                for u, v in ((0.0, 0.0), (0.34, 0.92), (0.72, 0.8), (1.0, 0.0),
                             (0.72, -0.8), (0.34, -0.92)):
                    leaf.append((bx + ca * ln * u - sa * wd * v, by + sa * ln * u + ca * wd * v))
                d.polygon(leaf, fill=(230, 190, 92), outline=(150, 108, 30))
    d.polygon([(cx, gy - 22), (cx + 23, gy - 9), (cx + 23, gy + 13), (cx, gy + 26),
               (cx - 23, gy + 13), (cx - 23, gy - 9)], fill=(206, 160, 56),
              outline=(255, 238, 180))
    d.polygon([(cx, gy - 14), (cx + 14, gy - 6), (cx + 14, gy + 8), (cx, gy + 16),
               (cx - 14, gy + 8), (cx - 14, gy - 6)], fill=(250, 220, 136))
    return im



# ======================================================================= Ren Aoyagi (original prodigy)
def make_ren_art():
    """Ren's in-match pieces, cutscene close-ups and the blue default opponent."""
    skin = SKIN["light"]
    pink = HAIR["pink"]
    base = os.path.join(OUT, "SIG_aoyagi")
    MS.make_head(skin, pink, "fade", None, ()).save(base + "_head.png")
    MS.make_torso(REN_KIT, 7).save(base + "_torso.png")
    MS.make_arm(REN_KIT, skin).save(base + "_arm.png")
    MS.make_leg(REN_KIT, skin, (240, 244, 250)).save(base + "_leg.png")
    b = os.path.join(OUT, "BLUEGUY")
    MS.make_head(MS.SKIN["tan"], MS.HAIR["darkbrown"], "short", None, ()).save(b + "_head.png")
    MS.make_torso(BLUE_KIT, 4).save(b + "_torso.png")
    MS.make_arm(BLUE_KIT, MS.SKIN["tan"]).save(b + "_arm.png")
    MS.make_leg(BLUE_KIT, MS.SKIN["tan"], (30, 30, 36)).save(b + "_leg.png")
    shirt = ((22, 22, 30), (60, 230, 240))
    for name, extras in (("open", ("eyes_blue", "nohb")), ("closed", ("eyes_closed", "nohb")),
                         ("glow", ("eyes_blue", "glow_cyan", "nohb")),
                         ("glowgreen", ("eyes_blue", "glow_green", "nohb"))):
        portrait("light", "pink", "pinkcrop", None, shirt, extras).save(os.path.join(OUT, "cut_ren_%s.png" % name))
    portrait("tan", "darkbrown", "short", None, ((40, 90, 210), WHITE), ("nohb",)).save(
        os.path.join(OUT, "cut_blue.png"))


def make_prodigy_template():
    """Ren's card: night-black with cyan circuitry, pink streak, silver frame with a star."""
    import random as _r
    import math as _m
    rnd = _r.Random(187)
    im = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for side in (-1, 1):                                  # angular silver blades
        for k in range(5):
            y = 90 + k * 70
            x = TPL_W // 2 + side * 134
            d.polygon([(x, y), (x + side * (46 - k * 4), y + 22), (x + side * 6, y + 50)],
                      fill=(214, 222, 236) if k % 2 else (150, 160, 180), outline=(70, 80, 100))
    body = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    _grad(bd, BODY, (10, 12, 30), (4, 6, 14))
    for _ in range(90):                                   # stars
        x, y = rnd.uniform(BODY[0], BODY[2]), rnd.uniform(BODY[1], BODY[3] - 120)
        bd.rectangle([x, y, x + 2, y + 2], fill=rnd.choice([(200, 230, 255), (120, 240, 255), (255, 200, 230)]))
    for _ in range(14):                                   # cyan circuit lines
        x, y = rnd.uniform(BODY[0], BODY[2]), rnd.uniform(BODY[1], BODY[3] - 140)
        pts = [(x, y)]
        for _j in range(4):
            if rnd.random() < 0.5:
                x += rnd.choice([-1, 1]) * rnd.uniform(14, 40)
            else:
                y += rnd.uniform(14, 40)
            pts.append((x, y))
        bd.line(pts, fill=(40, 200, 230), width=2)
        bd.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(120, 250, 255))
    bd.polygon([(BODY[0], 290), (BODY[2], 120), (BODY[2], 150), (BODY[0], 320)], fill=(246, 142, 194))
    bd.polygon([(BODY[0], 300), (BODY[2], 130), (BODY[2], 136), (BODY[0], 306)], fill=(255, 220, 240))
    _grad(bd, (BODY[0], 336, BODY[2], BODY[3]), (18, 22, 44), (6, 8, 18))
    bd.line([(BODY[0], 336), (BODY[2], 336)], fill=(60, 230, 240), width=3)
    body.putalpha(Image.composite(body.split()[3], Image.new("L", body.size, 0), _body_mask()))
    im.alpha_composite(body)
    x0, y0, x1, y1 = BODY
    d.rounded_rectangle([x0 - 11, y0 - 11, x1 + 11, y1 + 11], 22, outline=(90, 100, 120), width=11)
    d.rounded_rectangle([x0 - 8, y0 - 8, x1 + 8, y1 + 8], 20, outline=(222, 228, 240), width=6)
    d.rounded_rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], 18, outline=(60, 230, 240), width=2)
    cx = TPL_W // 2                                       # star on top, cyan gem at the bottom
    pts = []
    for k in range(10):
        a = -_m.pi / 2 + k * _m.pi / 5
        r = 30 if k % 2 == 0 else 13
        pts.append((cx + _m.cos(a) * r, y0 - 6 + _m.sin(a) * r))
    d.polygon(pts, fill=(236, 240, 250), outline=(90, 100, 120))
    d.polygon([(cx, y1 - 14), (cx + 20, y1 + 6), (cx, y1 + 26), (cx - 20, y1 + 6)], fill=(60, 230, 240),
              outline=(222, 228, 240))
    return im



def make_samba_template():
    """Joao Pedro's one-off card: Chelsea blue with a Brazilian streak cut across it.

    Blue field, a green-and-gold sash from bottom-left to top-right, confetti in the dark,
    and a silver-over-gold frame so it reads as a club card that somebody special got."""
    import random as _r
    rnd = _r.Random(20)
    blue, deep = (10, 74, 168), (5, 26, 74)
    green, gold = (0, 150, 70), (250, 210, 40)
    im = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    body = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    x0, y0, x1, y1 = BODY
    _grad(bd, BODY, blue, deep)
    for _ in range(70):                                   # confetti
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1 - 120)
        c = rnd.choice([green, gold, (150, 210, 255), (255, 255, 255)])
        bd.rectangle([x, y, x + rnd.choice([2, 3]), y + rnd.choice([2, 3])], fill=c)
    # the sash: three stripes running up to the right, low enough to show either side of him
    for off, col in ((0, green), (22, gold), (40, (255, 255, 255))):
        bd.polygon([(x0 - 10, 306 + off), (x0 - 10, 326 + off),
                    (x1 + 10, 214 + off), (x1 + 10, 194 + off)], fill=col)
    # a low arc of stars, the way a Brazil shirt carries them
    for k in range(7):
        sx = x0 + 34 + k * ((x1 - x0 - 68) / 6.0)
        sy = y0 + 46 + (abs(k - 3) ** 2) * 3
        bd.polygon([(sx, sy - 7), (sx + 2, sy - 2), (sx + 7, sy - 2), (sx + 3, sy + 2),
                    (sx + 5, sy + 7), (sx, sy + 4), (sx - 5, sy + 7), (sx - 3, sy + 2),
                    (sx - 7, sy - 2), (sx - 2, sy - 2)], fill=(255, 244, 200))
    _grad(bd, (x0, 336, x1, y1), (8, 46, 118), (4, 18, 52))
    bd.line([(x0, 336), (x1, 336)], fill=gold, width=3)
    bd.line([(x0, 341), (x1, 341)], fill=green, width=2)
    body.putalpha(Image.composite(body.split()[3], Image.new("L", body.size, 0), _body_mask()))
    im.alpha_composite(body)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x0 - 11, y0 - 11, x1 + 11, y1 + 11], 22, outline=(120, 132, 156), width=11)
    d.rounded_rectangle([x0 - 8, y0 - 8, x1 + 8, y1 + 8], 20, outline=(228, 234, 246), width=5)
    d.rounded_rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], 18, outline=gold, width=2)
    cx = TPL_W // 2                                       # a ball at the top, a green gem below
    d.ellipse([cx - 24, y0 - 30, cx + 24, y0 + 18], fill=(244, 248, 255), outline=(120, 132, 156), width=3)
    d.polygon([(cx, y0 - 16), (cx + 13, y0 - 7), (cx + 8, y0 + 8), (cx - 8, y0 + 8), (cx - 13, y0 - 7)],
              fill=(18, 24, 40))
    d.polygon([(cx, y1 - 14), (cx + 20, y1 + 6), (cx, y1 + 26), (cx - 20, y1 + 6)], fill=green,
              outline=gold)
    return im


def wave_flag(flag, w, h, phase=0.0, amp=0.055, folds=2.6):
    """A flag image redrawn as cloth: columns shifted on a sine, lit on the crests.

    This is the whole trick behind the card looking alive - the flag is not a flat
    rectangle behind the player, it hangs and ripples like the real thing."""
    import math as _m
    src = flag.convert("RGBA").resize((w, h), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = src.load()
    cols = []
    for x in range(w):
        t = x / float(max(1, w - 1))
        shift = _m.sin(t * folds * _m.tau + phase) * h * amp
        light = 0.80 + 0.30 * (0.5 + 0.5 * _m.cos(t * folds * _m.tau + phase))
        cols.append((int(round(shift)), light))
    for x, (shift, light) in enumerate(cols):
        strip = src.crop((x, 0, x + 1, h))
        if light != 1.0:
            strip = ImageEnhance.Brightness(strip).enhance(light)
        out.paste(strip, (x, shift))
        if shift > 0:                                     # fill the gap the shift opened
            out.paste(strip.crop((0, 0, 1, shift)), (x, 0))
        elif shift < 0:
            out.paste(strip.crop((0, h + shift, 1, h)), (x, h + shift))
    return out


def _arch_path(box, steps=90):
    """The card's silhouette: a straight left edge and a big bulge on the right - a D."""
    import math as _m
    x0, y0, x1, y1 = box
    cy = (y0 + y1) * 0.5
    ry = (y1 - y0) * 0.5
    rx = (x1 - x0) * 0.47                                 # how far the right side bulges
    lx = x1 - rx
    pts = []
    for i in range(steps + 1):                            # the right half-ellipse, top to bottom
        a = -_m.pi / 2 + _m.pi * i / steps
        pts.append((lx + rx * _m.cos(a), cy + ry * _m.sin(a)))
    r = (x1 - x0) * 0.16                                  # softly rounded left corners
    pts.append((x0 + r, y1))
    for i in range(1, 9):
        a = _m.pi / 2 + _m.pi / 2 * i / 9
        pts.append((x0 + r + r * _m.cos(a), y1 - r + r * _m.sin(a)))
    pts.append((x0, y0 + r))
    for i in range(1, 9):
        a = _m.pi + _m.pi / 2 * i / 9
        pts.append((x0 + r + r * _m.cos(a), y0 + r + r * _m.sin(a)))
    return pts


def make_arch_template(code, tier="A", phase=0.0):
    """A World Cup card: the nation's flag flying behind a gold arch.

    tier "A" gets the gold frame, tier "B" the silver one. The shape is the point - it is
    not a rectangle. It is a D, the flag is bright inside it and faded outside, and the
    player stands out of the top of it."""
    flag = None
    for name in (code, "flag_" + code):
        for cand in (name + ".png", os.path.join(OUT, name + ".png")):
            if os.path.exists(cand):
                flag = Image.open(cand)
                break
        if flag is not None:
            break
    x0, y0, x1, y1 = BODY
    arch = _arch_path((x0 + 8, y0 + 6, x1 - 8, y1 - 6))
    # ---- the flag, flying, wider than the card so it spills past the arch
    cloth = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    if flag is not None:
        flown = wave_flag(flag, (x1 - x0) + 80, (y1 - y0) + 10, phase)
        cloth.alpha_composite(flown, (x0 - 40, y0 - 5))
    else:
        ImageDraw.Draw(cloth).rectangle(BODY, fill=(40, 58, 120))
    inside = Image.new("L", (TPL_W, TPL_H), 0)
    ImageDraw.Draw(inside).polygon(arch, fill=255)
    im = ImageEnhance.Brightness(cloth).enhance(0.58)      # the spill, pushed back
    im.paste(cloth, (0, 0), inside)                        # bright inside the arch
    # ---- the plate the name sits on, only inside the arch
    plate = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    _grad(pd, (x0, 336, x1, y1), (10, 16, 38), (4, 7, 18))
    pd.line([(x0, 336), (x1, 336)], fill=GOLD if tier == "A" else (214, 222, 236), width=3)
    plate.putalpha(Image.composite(plate.split()[3], Image.new("L", plate.size, 0), inside))
    im.alpha_composite(plate)
    shade_tl = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade_tl)
    for k in range(26):                                    # a corner that fades out
        a = int(104 * (1.0 - k / 26.0))
        sd.ellipse([x0 - 120 + k * 5, y0 - 110 + k * 5, x0 + 196 - k * 5, y0 + 188 - k * 5],
                   fill=(4, 8, 22, max(0, a // 7)))
    im.alpha_composite(shade_tl)
    im.putalpha(Image.composite(im.split()[3], Image.new("L", im.size, 0), _body_mask()))
    # ---- the arch itself
    d = ImageDraw.Draw(im)
    outer, mid, edge = ((132, 92, 22), (246, 206, 106), (255, 246, 206)) if tier == "A" else \
                       ((84, 96, 118), (214, 224, 240), (255, 255, 255))
    d.line(arch + [arch[0]], fill=outer, width=18, joint="curve")
    d.line(arch + [arch[0]], fill=mid, width=10, joint="curve")
    d.line(arch + [arch[0]], fill=edge, width=3, joint="curve")
    # ---- the gem hanging off the bottom of the arch
    cx, cy = (x0 + x1) // 2, y1 - 4
    d.polygon([(cx, cy - 15), (cx + 17, cy + 2), (cx, cy + 21), (cx - 17, cy + 2)],
              fill=(150, 160, 180) if tier == "B" else (236, 196, 90), outline=outer)
    d.polygon([(cx, cy - 9), (cx + 10, cy + 2), (cx, cy + 13), (cx - 10, cy + 2)],
              fill=(206, 214, 230) if tier == "B" else (250, 226, 150))
    return im


def _holo_band(size, tier="A", steps=240):
    """A diagonal pearl sweep - white through pink, mint and pale blue and back.

    This is what makes the frame look like it catches the light instead of being a flat
    gold line. Tier B gets the same sweep with the colour taken most of the way out."""
    w, h = size
    band = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(band)
    stops = [(255, 255, 255), (255, 206, 232), (214, 255, 236), (206, 232, 255),
             (255, 246, 214), (255, 255, 255)]
    if tier == "SIG":                                      # the signature card: gold, not pearl
        stops = [(255, 246, 206), (236, 186, 70), (255, 232, 158), (182, 132, 32),
                 (255, 250, 228), (255, 246, 206)]
    elif tier != "A":                                      # silver: keep a hint of the shimmer
        stops = [mix(c, (226, 232, 242), 0.72) for c in stops]
    span = w + h
    for i in range(steps):
        t = i / float(steps - 1)
        k = t * (len(stops) - 1)
        a = stops[int(k)]
        b = stops[min(len(stops) - 1, int(k) + 1)]
        col = mix(a, b, k - int(k))
        x = -h + span * t
        d.line([(x, 0), (x + h, h)], fill=col, width=int(span / steps) + 3)
    return band


def _holo_card_path(box, steps=40):
    """The card outline: a tall rounded rectangle, rounder at the bottom than the top."""
    import math as _m
    x0, y0, x1, y1 = box
    rt, rb = (x1 - x0) * 0.13, (x1 - x0) * 0.30
    pts = []
    for i in range(steps + 1):                             # top-left
        a = _m.pi + _m.pi / 2 * i / steps
        pts.append((x0 + rt + rt * _m.cos(a), y0 + rt + rt * _m.sin(a)))
    for i in range(steps + 1):                             # top-right
        a = -_m.pi / 2 + _m.pi / 2 * i / steps
        pts.append((x1 - rt + rt * _m.cos(a), y0 + rt + rt * _m.sin(a)))
    for i in range(steps + 1):                             # bottom-right
        a = 0 + _m.pi / 2 * i / steps
        pts.append((x1 - rb + rb * _m.cos(a), y1 - rb + rb * _m.sin(a)))
    for i in range(steps + 1):                             # bottom-left
        a = _m.pi / 2 + _m.pi / 2 * i / steps
        pts.append((x0 + rb + rb * _m.cos(a), y1 - rb + rb * _m.sin(a)))
    return pts


def make_holo_template(code, tier="A", phase=0.0):
    """A World Cup card: the nation's flag flying behind it, a shimmering frame around it.

    tier "A" gets the full pearl shimmer, tier "B" a plainer silver. The flag is drawn
    twice - once huge and flying behind the card, once calmer inside it - which is what
    gives the card something to sit in front of."""
    flag = None
    for name in (code, "flag_" + code):
        for cand in (name + ".png", os.path.join(OUT, name + ".png")):
            if os.path.exists(cand):
                flag = Image.open(cand)
                break
        if flag is not None:
            break
    x0, y0, x1, y1 = BODY
    im = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    # ---- the big flag flying behind, spilling well past the card on both sides
    if flag is not None:
        back = wave_flag(flag, TPL_W + 170, int((y1 - y0) * 1.04), phase, amp=0.085, folds=3.1)
        back = ImageEnhance.Color(ImageEnhance.Brightness(back).enhance(0.52)).enhance(0.72)
        im.alpha_composite(back, (-85, y0 - 8))
    drop = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))          # the card sits in front
    ImageDraw.Draw(drop).polygon(_holo_card_path((x0 + 6, y0 + 10, x1 + 10, y1 + 12)),
                                 fill=(2, 4, 12, 120))
    im.alpha_composite(drop)
    # ---- the card itself
    card = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    if flag is not None:
        inner = wave_flag(flag, (x1 - x0) + 30, (y1 - y0) + 10, phase + 1.4, amp=0.05, folds=2.2)
        inner = ImageEnhance.Brightness(inner).enhance(1.06)
        card.alpha_composite(inner, (x0 - 15, y0 - 5))
    else:
        ImageDraw.Draw(card).rectangle(BODY, fill=(34, 52, 110))
    cd = ImageDraw.Draw(card)
    plate = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))         # the name sits on this
    pdd = ImageDraw.Draw(plate)
    for y in range(314, y1 + 1):                                    # fades in, never a hard edge
        a = int(242 * min(1.0, ((y - 314) / 44.0) ** 1.4))          # full before the name lands
        pdd.line([(x0, y), (x1, y)], fill=(6, 10, 26, a))
    card.alpha_composite(plate)
    shadow = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))        # top-left, for the rating
    sd = ImageDraw.Draw(shadow)
    for k in range(26):                                             # pale flags need a real pool
        sd.ellipse([x0 - 140 + k * 6, y0 - 130 + k * 6, x0 + 232 - k * 6, y0 + 218 - k * 6],
                   fill=(3, 6, 20, 22))
    card.alpha_composite(shadow)
    shape = Image.new("L", (TPL_W, TPL_H), 0)
    ImageDraw.Draw(shape).polygon(_holo_card_path(BODY), fill=255)
    card.putalpha(Image.composite(card.split()[3], Image.new("L", card.size, 0), shape))
    im.alpha_composite(card)
    # ---- the frame: a dark edge, the pearl band, a white hairline
    d = ImageDraw.Draw(im)
    path = _holo_card_path(BODY)
    d.line(path + [path[0]], fill=(26, 30, 44), width=14, joint="curve")
    ring = Image.new("L", (TPL_W, TPL_H), 0)
    ImageDraw.Draw(ring).line(path + [path[0]], fill=255, width=9, joint="curve")
    im.paste(_holo_band((TPL_W, TPL_H), tier), (0, 0), ring)
    d.line(path + [path[0]], fill=(255, 255, 255), width=2, joint="curve")
    inner_path = _holo_card_path((x0 + 11, y0 + 11, x1 - 11, y1 - 11))
    d.line(inner_path + [inner_path[0]], fill=(255, 255, 255, 120), width=2, joint="curve")
    # ---- the gem at the bottom, sitting over the frame
    cx, cy = (x0 + x1) // 2, y1 - 2
    base = (120, 130, 150) if tier == "B" else (150, 158, 176)
    d.polygon([(cx, cy - 20), (cx + 21, cy - 8), (cx + 21, cy + 12), (cx, cy + 24),
               (cx - 21, cy + 12), (cx - 21, cy - 8)], fill=base, outline=(236, 242, 252))
    d.polygon([(cx, cy - 13), (cx + 13, cy - 6), (cx + 13, cy + 7), (cx, cy + 15),
               (cx - 13, cy + 7), (cx - 13, cy - 6)], fill=(196, 204, 220))
    return im


def make_card_templates(cards):
    make_icon_template().save(os.path.join(OUT, "tpl_icon_card.png"))
    make_poolb_template().save(os.path.join(OUT, "tpl_b_card.png"))
    make_sig_template().save(os.path.join(OUT, "tpl_sig_card.png"))
    make_prodigy_template().save(os.path.join(OUT, "tpl_prodigy_card.png"))
    make_samba_template().save(os.path.join(OUT, "tpl_samba_card.png"))
    make_star_template().save(os.path.join(OUT, "tpl_star_card.png"))
    make_star_template(ROOKIE_PAL, "BEGINNER").save(os.path.join(OUT, "tpl_rookie_card.png"))
    make_eclipse_template().save(os.path.join(OUT, "tpl_eclipse_card.png"))
    make_neon_template().save(os.path.join(OUT, "tpl_neon_card.png"))
    make_street_template().save(os.path.join(OUT, "tpl_street_card.png"))
    # World Cup pool A and B: the arch card, one per nation per tier
    arches = set()
    nations = []
    for c in cards:                                        # every World Cup nation, in order
        if c["kind"] == "wc" and c["team"] not in nations:
            nations.append(c["team"])
    for code in nations:                                   # both tiers for all of them, so a
        for pool in ("A", "B"):                            # card can never find its art missing
            arches.add((code, pool))
            name = ("tpl_holo_%s_card.png" if pool == "A" else "tpl_holob_%s_card.png") % code
            make_holo_template(code, pool).save(os.path.join(OUT, name))
    done = set()
    for c in cards:
        if card_pool(c) != "A" or c["design"] in ("icon", "signature", "prodigy", "starsign",
                                                  "beginner", "no10", "samba", "worldsgame"):
            continue
        if c["kind"] == "wc":
            continue                                       # these have the arch card now
        key = ("club_" if c["kind"] == "club" else "nat_") + c["team"]
        if key in done:
            continue
        kit = card_kit(c) or {"base": (40, 60, 140), "trim": WHITE}
        c1 = kit["base"]
        c2 = kit.get("alt") if kit.get("alt") and kit.get("alt") != c1 else kit.get("trim", WHITE)
        make_team_template(c1, c2, c["team"]).save(os.path.join(OUT, "tpl_%s_card.png" % key))
        done.add(key)
    return len(done) + len(arches) + 2



# ======================================================================= posed card figures
# The player on a World Cup / signature card is his own piece of pixel art now, not the match
# ragdoll re-posed. cardfig.py builds him: a small 3D mannequin, posed, lit and seen through
# a long lens, then reduced to the card's own pixel grid with five colours per material. The
# seventeen poses are in cards17.py, each taken from Hubi's reference picture for that card.
#
# Drawing all seventeen takes several minutes and needs numpy, so this script only draws a
# figure that is MISSING from the sprites folder. To redraw them all:
#     python3 make_card_figures.py

def make_card_figures(cards, force=False, quality=6):
    """A posed figure for every card that has a pose in cards17.py. Returns how many it drew."""
    try:
        import cardfig
        import cards17
        import cards_wg
    except ImportError as exc:
        print("   card figures skipped (%s) - the ones already in %s are kept" % (exc, OUT))
        return 0
    poses = dict(cards17.FIGS)
    poses.update(cards_wg.FIGS)
    n = 0
    for c in cards:
        pose = poses.get(c["id"])
        path = os.path.join(OUT, "%s_figure.png" % c["id"])
        if pose is None or (os.path.exists(path) and not force):
            continue
        fig, shot = pose()
        cardfig.flatten(cardfig.render(fig, shot, S=quality)).save(path)
        n += 1
    return n



# ======================================================================= menu carousel slides (portrait)
SLIDE_W, SLIDE_H = 560, 680


def _slide_base(top, bottom):
    im = Image.new("RGBA", (SLIDE_W, SLIDE_H), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for y in range(SLIDE_H):
        d.line([(0, y), (SLIDE_W, y)], fill=mix(top, bottom, y / SLIDE_H))
    return im, d


def _caption(im, title, sub, col=(255, 214, 60)):
    d = ImageDraw.Draw(im)
    band = Image.new("RGBA", (SLIDE_W, 150), (6, 10, 20, 200))
    im.alpha_composite(band, (0, SLIDE_H - 150))
    t = text_img(title, 46, col, INK, 5)
    if t.width > SLIDE_W - 40:
        t = t.resize((SLIDE_W - 40, int(t.height * (SLIDE_W - 40) / t.width)), Image.LANCZOS)
    im.alpha_composite(t, ((SLIDE_W - t.width) // 2, SLIDE_H - 136))
    s2 = text_img(sub, 24, WHITE, INK, 3)
    if s2.width > SLIDE_W - 40:
        s2 = s2.resize((SLIDE_W - 40, int(s2.height * (SLIDE_W - 40) / s2.width)), Image.LANCZOS)
    im.alpha_composite(s2, ((SLIDE_W - s2.width) // 2, SLIDE_H - 62))


def make_slide_playnow():
    """A player seen from behind, setting the ball down in the rain."""
    import random as _r
    rnd = _r.Random(11)
    im, d = _slide_base((24, 40, 70), (70, 76, 70))
    for _ in range(14):                                    # blurry stadium lights
        x, y = rnd.randrange(SLIDE_W), rnd.randrange(40, 260)
        r = rnd.randrange(18, 46)
        glow = Image.new("RGBA", (r * 2, r * 2), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([0, 0, r * 2, r * 2], fill=rnd.choice([(255, 250, 230, 60), (220, 90, 70, 50),
                                                                              (120, 170, 255, 50)]))
        im.alpha_composite(glow, (x - r, y - r))
    d.rectangle([0, 470, SLIDE_W, SLIDE_H], fill=(58, 92, 50))            # pitch
    for x in range(0, SLIDE_W, 70):
        d.rectangle([x, 470, x + 35, SLIDE_H], fill=(62, 98, 54))
    cx = SLIDE_W // 2
    blue, red, skin = (28, 58, 150), (150, 28, 52), (206, 158, 120)
    # legs + socks + boots (bent over, seen from behind)
    for sx in (-44, 18):
        d.polygon([(cx + sx, 360), (cx + sx + 28, 360), (cx + sx + 34, 500), (cx + sx + 6, 500)], fill=blue)
        d.rectangle([cx + sx + 6, 470, cx + sx + 34, 506], fill=red)
        d.rectangle([cx + sx + 4, 506, cx + sx + 40, 522], fill=(230, 40, 40))
    # shorts
    d.rounded_rectangle([cx - 56, 320, cx + 56, 390], 14, fill=(20, 40, 110))
    # torso leaning towards us: big back with stripes
    d.rounded_rectangle([cx - 92, 150, cx + 92, 340], 40, fill=blue)
    for k in range(-2, 3):
        d.rectangle([cx + k * 36 - 9, 158, cx + k * 36 + 9, 334], fill=red)
    t = text_img("10", 70, (250, 204, 40), INK, 3)
    im.alpha_composite(t, (cx - t.width // 2, 205))
    # arms reaching down to the ball
    for sx in (-1, 1):
        d.polygon([(cx + sx * 80, 180), (cx + sx * 104, 200), (cx + sx * 40, 470), (cx + sx * 20, 460)], fill=blue)
        d.ellipse([cx + sx * 36 - 14, 450, cx + sx * 36 + 14, 478], fill=skin)
    # head, bowed (back of the head)
    d.rectangle([cx - 18, 150, cx + 18, 176], fill=shade(skin, 0.8))      # neck
    d.ellipse([cx - 42, 96, cx + 42, 168], fill=(34, 26, 24))             # back of the bowed head
    d.ellipse([cx - 22, 104, cx + 6, 122], fill=(64, 50, 44))             # shine on the hair
    d.ellipse([cx - 50, 126, cx - 38, 146], fill=skin); d.ellipse([cx + 38, 126, cx + 50, 146], fill=skin)
    # the ball
    d.ellipse([cx - 44, 452, cx + 44, 540], fill=(246, 222, 120))
    d.arc([cx - 44, 452, cx + 44, 540], 200, 340, fill=(40, 90, 140), width=8)
    d.polygon([(cx - 8, 480), (cx + 14, 486), (cx + 10, 510), (cx - 14, 508)], fill=(40, 90, 140))
    rain = Image.new("RGBA", (SLIDE_W, SLIDE_H), (0, 0, 0, 0))            # rain / snow sparkles
    rd = ImageDraw.Draw(rain)
    for _ in range(260):
        x, y = rnd.randrange(SLIDE_W), rnd.randrange(SLIDE_H)
        rd.rectangle([x, y, x + 3, y + 3], fill=(255, 255, 255, rnd.randrange(80, 200)))
    im.alpha_composite(rain)
    _caption(im, "PLAY NOW", "WORLD CUP  -  CLUB FOOTBALL")
    return pixelate(im, 3)


def make_slide_champions(faces):
    im, d = _slide_base((16, 10, 34), (150, 26, 30))
    import random as _r
    rnd = _r.Random(4)
    for _ in range(220):
        x, y = rnd.randrange(SLIDE_W), rnd.randrange(SLIDE_H - 150)
        d.rectangle([x, y, x + 7, y + 5], fill=rnd.choice([(202, 22, 34), (250, 200, 24), WHITE, GOLD]))
    d.rectangle([0, 470, SLIDE_W, SLIDE_H], fill=(38, 112, 48))
    champion(im, faces, SLIDE_W // 2, 500, 1.2)
    _caption(im, "GAME RELEASED!!", "SPAIN - 2026 WORLD CHAMPIONS")
    return pixelate(im, 3)


def make_slide_pack(pack_img, faces):
    import math as _m
    im, d = _slide_base((14, 22, 60), (40, 70, 150))
    for k in range(16):
        a = k * _m.tau / 16
        d.polygon([(SLIDE_W / 2, 280), (SLIDE_W / 2 + _m.cos(a) * 700, 280 + _m.sin(a) * 700),
                   (SLIDE_W / 2 + _m.cos(a + 0.14) * 700, 280 + _m.sin(a + 0.14) * 700)], fill=(56, 86, 170))
    p = pack_img.resize((230, 322), Image.NEAREST)
    im.alpha_composite(p, (SLIDE_W // 2 - 115, 60))
    for j, f in enumerate(faces):
        x = 40 + j * 170
        d.rounded_rectangle([x, 380, x + 140, 520], 12, fill=(236, 196, 90))
        im.alpha_composite(f.resize((130, 130), Image.NEAREST), (x + 5, 385))
    _caption(im, "WORLD CUP PACK", "ICONS INSIDE  -  CLICK TO OPEN")
    return pixelate(im, 3)


def make_slide_neymar(face):
    im, d = _slide_base((0, 0, 0), (0, 0, 0))
    brazil_flag(d, -200, -40, SLIDE_W + 400, SLIDE_H + 80)
    im.alpha_composite(Image.new("RGBA", (SLIDE_W, SLIDE_H), (0, 40, 20, 90)))
    im.alpha_composite(face.resize((400, 400), Image.NEAREST), (80, 60))
    d = ImageDraw.Draw(im)
    scrawl(d, 120, 450, 1.2, (255, 236, 150), 7)
    _caption(im, "THE WORLD'S GAME BOX", "NEYMAR JR 150 SIGNATURE - FIRST DRAW FREE", (140, 255, 160))
    return pixelate(im, 3)



# ======================================================================= Star Signing Elite
PURPLE = (132, 58, 226)
LILAC = (214, 182, 255)
SILVER = (206, 210, 224)


def _chamfer(box, c):
    a0, b0, a1, b1 = box
    return [(a0 + c, b0), (a1 - c, b0), (a1, b0 + c), (a1, b1 - c), (a1 - c, b1), (a0 + c, b1),
            (a0, b1 - c), (a0, b0 + c)]


def _star_pts(cx, cy, r_out, r_in, n=5, rot=-1.5707963):
    import math as _m
    pts = []
    for k in range(n * 2):
        a = rot + k * _m.pi / n
        r = r_out if k % 2 == 0 else r_in
        pts.append((cx + _m.cos(a) * r, cy + _m.sin(a) * r))
    return pts


def _sparkle(d, x, y, s, col):
    d.polygon([(x, y - s), (x + s * 0.28, y - s * 0.28), (x + s, y), (x + s * 0.28, y + s * 0.28),
               (x, y + s), (x - s * 0.28, y + s * 0.28), (x - s, y), (x - s * 0.28, y - s * 0.28)], fill=col)


def _low_poly(d, box, top, bottom, rnd, cols=7, rows=10, jitter=0.35, light=None, tone=None):
    """Geometric facets: a jittered grid split into triangles. `tone` replaces shade() for
    palettes too dark to be lightened toward white without going grey."""
    x0, y0, x1, y1 = box
    cw, ch = (x1 - x0) / cols, (y1 - y0) / rows
    pts = {}
    for j in range(rows + 1):
        for i in range(cols + 1):
            jx = 0 if i in (0, cols) else rnd.uniform(-jitter, jitter) * cw
            jy = 0 if j in (0, rows) else rnd.uniform(-jitter, jitter) * ch
            pts[i, j] = (x0 + i * cw + jx, y0 + j * ch + jy)
    for j in range(rows):
        for i in range(cols):
            a, b, c, e = pts[i, j], pts[i + 1, j], pts[i + 1, j + 1], pts[i, j + 1]
            for tri in ((a, b, c), (a, c, e)) if (i + j) % 2 else ((a, b, e), (b, c, e)):
                cy = sum(p[1] for p in tri) / 3
                cx = sum(p[0] for p in tri) / 3
                base = mix(top, bottom, (cy - y0) / max(1, y1 - y0))
                k = rnd.uniform(0.82, 1.22)
                if light and ((cx - light[0]) ** 2 + (cy - light[1]) ** 2) ** 0.5 < light[2]:
                    k += 0.25
                d.polygon(tri, fill=(tone or shade)(base, k))


STAR_PAL = {"glow": (186, 96, 255), "frame": (132, 58, 226), "top": (116, 46, 214), "bottom": (38, 10, 86),
            "star": (236, 214, 255), "panel": ((44, 12, 94), (18, 4, 42)), "facet": (52, 18, 104),
            "line": (160, 100, 240), "band": ((168, 92, 255), (96, 34, 186)), "tail": (84, 30, 150),
            "ink": (54, 12, 104), "gem": (214, 182, 255)}
ROOKIE_PAL = {"glow": (90, 240, 160), "frame": (36, 168, 104), "top": (58, 188, 124), "bottom": (10, 70, 48),
              "star": (210, 255, 230), "panel": ((16, 74, 48), (6, 34, 22)), "facet": (22, 92, 60),
              "line": (110, 230, 160), "band": ((96, 226, 150), (30, 132, 84)), "tail": (20, 100, 62),
              "ink": (8, 60, 36), "gem": (186, 255, 214)}


def make_star_template(pal=None, label="STAR SIGNING"):
    """Star Signing Elite card: purple frame with white + silver trim, purple geometric
    background, STAR SIGNING band across the lower section and a purple glow outside.
    The same shape in green with a BEGINNER band makes the tutorial's beginner cards."""
    import random as _r
    from PIL import ImageFilter
    P = pal or STAR_PAL
    rnd = _r.Random(2026)
    x0, y0, x1, y1 = BODY
    H = y1 - y0
    im = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    # purple glow around the outside
    glow = Image.new("L", (TPL_W, TPL_H), 0)
    ImageDraw.Draw(glow).polygon(_chamfer((x0 - 20, y0 - 20, x1 + 20, y1 + 20), 34), fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(13))
    layer = Image.new("RGBA", (TPL_W, TPL_H), P["glow"] + (0,))
    layer.putalpha(glow.point(lambda v: int(v * 0.9)))
    im.alpha_composite(layer)
    d = ImageDraw.Draw(im)
    # frame: silver edge, purple band, white inner trim
    d.polygon(_chamfer((x0 - 15, y0 - 15, x1 + 15, y1 + 15), 30), fill=(150, 156, 176))
    d.polygon(_chamfer((x0 - 12, y0 - 12, x1 + 12, y1 + 12), 28), fill=SILVER)
    d.polygon(_chamfer((x0 - 9, y0 - 9, x1 + 9, y1 + 9), 26), fill=P["frame"])
    d.polygon(_chamfer((x0 - 4, y0 - 4, x1 + 4, y1 + 4), 23), fill=(250, 250, 255))
    # the card body
    body = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    _low_poly(bd, BODY, P["top"], P["bottom"], rnd, 7, 10, 0.38, (x1 - 40, y0 + 60, 120))
    over = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    for k in range(3):                                    # diagonal light beams
        bx = x0 + 40 + k * 90
        od.polygon([(bx, y0), (bx + 26 - k * 6, y0), (bx - 150, y0 + 330), (bx - 176 + k * 6, y0 + 330)],
                   fill=(255, 255, 255, 26))
    od.polygon(_star_pts((x0 + x1) / 2 + 18, y0 + 150, 150, 60), outline=P["star"] + (110,), width=4)
    od.polygon(_star_pts((x0 + x1) / 2 + 18, y0 + 150, 126, 50), outline=P["star"] + (50,), width=2)
    for _ in range(26):                                   # little sparkles in the sky
        _sparkle(od, rnd.uniform(x0 + 10, x1 - 10), rnd.uniform(y0 + 10, y0 + 280), rnd.choice([3, 4, 6]),
                 (255, 255, 255, rnd.choice([120, 180, 230])))
    body.alpha_composite(over)
    # lower panel (name, band, flag + badge)
    py = int(y0 + 0.70 * H)
    _grad(bd, (x0, py, x1, y1), P["panel"][0], P["panel"][1])
    for k in range(0, x1 - x0, 22):                       # faint facets in the panel too
        bd.line([(x0 + k, y1), (x0 + k + 40, py)], fill=P["facet"], width=2)
    bd.line([(x0, py), (x1, py)], fill=SILVER, width=3)
    bd.line([(x0, py + 4), (x1, py + 4)], fill=P["line"], width=1)
    mask = Image.new("L", (TPL_W, TPL_H), 0)
    ImageDraw.Draw(mask).polygon(_chamfer(BODY, 20), fill=255)
    body.putalpha(Image.composite(body.split()[3], Image.new("L", body.size, 0), mask))
    im.alpha_composite(body)
    d = ImageDraw.Draw(im)
    # STAR SIGNING band across the lower section - wraps past the frame
    ry0, ry1 = int(y0 + 0.788 * H), int(y0 + 0.866 * H)
    mid = (ry0 + ry1) / 2
    for side in (-1, 1):                                  # swallow-tail ends behind the band
        ex = x0 - 20 if side < 0 else x1 + 20
        ix = x0 + 6 if side < 0 else x1 - 6
        d.polygon([(ix, ry0 + 5), (ex, ry0 + 5), (ex + side * -12, mid + 2), (ex, ry1 + 5), (ix, ry1 + 5)],
                  fill=P["tail"], outline=SILVER)
    d.rectangle([x0 - 8, ry0, x1 + 8, ry1], fill=SILVER)
    band = Image.new("RGBA", (x1 - x0 + 12, ry1 - ry0 - 6), (0, 0, 0, 0))
    bdd = ImageDraw.Draw(band)
    for y in range(band.height):
        bdd.line([(0, y), (band.width, y)], fill=mix(P["band"][0], P["band"][1], y / max(1, band.height)))
    im.alpha_composite(band, (x0 - 6, ry0 + 3))
    t = text_img(label, 23, WHITE, P["ink"], 3)
    im.alpha_composite(t, (int((x0 + x1 - t.width) / 2), int(mid - t.height / 2)))
    for sx in (x0 + 14, x1 - 14):
        d.polygon(_star_pts(sx, mid, 9, 4), fill=WHITE)
    # silver star crest on top, purple gem at the bottom
    cx = TPL_W // 2
    d.polygon(_star_pts(cx, y0 - 8, 32, 14), fill=SILVER, outline=(120, 126, 150))
    d.polygon(_star_pts(cx, y0 - 8, 20, 9), fill=P["frame"])
    d.polygon(_star_pts(cx, y0 - 10, 8, 4), fill=P["star"])
    d.polygon([(cx, y1 - 10), (cx + 18, y1 + 6), (cx, y1 + 22), (cx - 18, y1 + 6)], fill=P["frame"], outline=SILVER)
    d.polygon([(cx, y1 - 4), (cx + 8, y1 + 6), (cx, y1 + 6)], fill=P["gem"])
    # corner sparkles on the frame
    for (sx, sy) in ((x0 - 8, y0 + 40), (x1 + 8, y0 + 40), (x0 - 8, y1 - 60), (x1 + 8, y1 - 60)):
        _sparkle(d, sx, sy, 8, WHITE)
    return im


def star_card_preview(c, width):
    """A finished Star Signing card as one PIL image (for the menu slide + pack)."""
    tpl = make_star_template()
    x0, y0, x1, y1 = BODY
    card = tpl.copy()
    W, H = x1 - x0, y1 - y0
    face_p = os.path.join(OUT, "%s_portrait.png" % c["id"])
    if os.path.exists(face_p):
        face = Image.open(face_p).convert("RGBA").resize((int(W * 0.84),) * 2, Image.NEAREST)
        card.alpha_composite(face, (x0 + W // 2 + int(W * 0.08) - face.width // 2, y0 + int(H * 0.705) - face.height))
    num = text_img(str(c["rating"]), 58, WHITE, (44, 8, 92), 4)
    card.alpha_composite(num, (x0 + int(W * 0.06), y0 + int(H * 0.03)))
    pos = text_img(c["pos"], 26, LILAC, (44, 8, 92), 3)
    card.alpha_composite(pos, (x0 + int(W * 0.09), y0 + int(H * 0.03) + num.height))
    nm = text_img(c["name"].upper(), 28, WHITE, (30, 6, 60), 3)
    if nm.width > W * 0.86:
        nm = nm.resize((int(W * 0.86), int(nm.height * W * 0.86 / nm.width)), Image.LANCZOS)
    card.alpha_composite(nm, (x0 + (W - nm.width) // 2, y0 + int(H * 0.743) - nm.height // 2))
    k = width / TPL_W
    return card.resize((width, int(TPL_H * k)), Image.LANCZOS)


def make_star_bg(W=1920, H=1080):
    """Star Signing backdrop: purple facets, light rays, big faint stars, sparkles."""
    import math as _m
    import random as _r
    rnd = _r.Random(77)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    _low_poly(d, (0, 0, W, H), (70, 22, 140), (16, 4, 40), rnd, 16, 9, 0.4, (W * 0.62, H * 0.35, 520))
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    cx, cy = int(W * 0.62), int(H * 0.36)
    for k in range(18):                                    # rays
        a = k * _m.tau / 18
        od.polygon([(cx, cy), (cx + _m.cos(a) * 2400, cy + _m.sin(a) * 2400),
                    (cx + _m.cos(a + 0.08) * 2400, cy + _m.sin(a + 0.08) * 2400)], fill=(200, 150, 255, 18))
    for (sx, sy, r) in ((cx, cy, 380), (240, 860, 200), (1760, 900, 160)):
        od.polygon(_star_pts(sx, sy, r, r * 0.4), outline=(220, 190, 255, 60), width=6)
    for _ in range(140):
        _sparkle(od, rnd.randrange(W), rnd.randrange(H), rnd.choice([3, 5, 7, 10]),
                 (255, 255, 255, rnd.choice([70, 120, 200])))
    for k in range(10):                                    # vignette
        od.rectangle([0, 0, W, 24 * k], fill=(10, 0, 24, 12))
        od.rectangle([0, H - 24 * k, W, H], fill=(10, 0, 24, 12))
    im.alpha_composite(over)
    return pixelate(im, 3)


def make_pack_star(W=300, H=420):
    """Purple foil Star Signing pack."""
    import random as _r
    rnd = _r.Random(5)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    _low_poly(bd, (10, 24, W - 10, H - 24), (126, 52, 226), (40, 10, 90), rnd, 5, 8, 0.4, (W * 0.7, 90, 90))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([10, 24, W - 10, H - 24], 18, fill=255)
    body.putalpha(mask)
    im.alpha_composite(body)
    for x in range(10, W - 10, 12):                        # crimped foil ends
        d.polygon([(x, 26), (x + 6, 8), (x + 12, 26)], fill=SILVER)
        d.polygon([(x, H - 26), (x + 6, H - 8), (x + 12, H - 26)], fill=SILVER)
    d.rectangle([10, 24, W - 10, 40], fill=SILVER)
    d.rectangle([10, H - 40, W - 10, H - 24], fill=SILVER)
    d.rounded_rectangle([10, 24, W - 10, H - 24], 18, outline=(250, 250, 255), width=5)
    d.polygon(_star_pts(W // 2, 160, 88, 36), fill=WHITE, outline=SILVER)
    d.polygon(_star_pts(W // 2, 160, 62, 25), fill=PURPLE)
    d.polygon(_star_pts(W // 2, 156, 22, 10), fill=LILAC)
    for (sx, sy) in ((60, 70), (245, 92), (54, 250), (250, 262)):
        _sparkle(d, sx, sy, 10, WHITE)
    d.rectangle([22, 280, W - 22, 372], fill=(40, 10, 86))
    d.line([(22, 280), (W - 22, 280)], fill=SILVER, width=3)
    t = text_img("STAR SIGNING", 32, WHITE, (54, 12, 104), 3)
    im.alpha_composite(t, ((W - t.width) // 2, 304 - t.height // 2))
    t2 = text_img("ELITE", 34, LILAC, (54, 12, 104), 4)
    im.alpha_composite(t2, ((W - t2.width) // 2, 346 - t2.height // 2))
    return pixelate(im, 3)


def make_slide_stars(cards):
    """Menu slide: three Star Signing Elite cards fanned out."""
    im, d = _slide_base((70, 22, 140), (18, 4, 40))
    rnd = __import__("random").Random(4)
    _low_poly(d, (0, 0, SLIDE_W, SLIDE_H), (80, 26, 156), (18, 4, 44), rnd, 5, 7, 0.4, (280, 250, 220))
    over = Image.new("RGBA", (SLIDE_W, SLIDE_H), (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    od.polygon(_star_pts(280, 260, 250, 100), outline=(230, 200, 255, 80), width=6)
    for _ in range(40):
        _sparkle(od, rnd.randrange(SLIDE_W), rnd.randrange(SLIDE_H - 150), rnd.choice([3, 5, 7]),
                 (255, 255, 255, 170))
    im.alpha_composite(over)
    by_id = {c["id"]: c for c in cards}
    for cid, x, y, ang, width in (("STAR_r9", 30, 130, 9, 250), ("STAR_maradona", 280, 130, -9, 250),
                                  ("STAR_pele", 130, 60, 0, 300)):
        if cid not in by_id:
            continue
        cimg = star_card_preview(by_id[cid], width).rotate(ang, resample=Image.BICUBIC, expand=True)
        im.alpha_composite(cimg, (x + (width - cimg.width) // 2 + 0, y))
    _caption(im, "STAR SIGNING", "40 ELITE LEGENDS - EXCHANGE PLAYERS FOR STAR POINTS", LILAC)
    return pixelate(im, 3)


# ---- extra flags for Star Signing nations
def _flag(W, H):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    return im, ImageDraw.Draw(im)


def make_flag_stripes(cols, vertical, W=240, H=160):
    im, d = _flag(W, H)
    n = len(cols)
    for k, c in enumerate(cols):
        if vertical:
            d.rectangle([k * W / n, 0, (k + 1) * W / n, H], fill=c)
        else:
            d.rectangle([0, k * H / n, W, (k + 1) * H / n], fill=c)
    return im, d


def make_extra_flags():
    out = {}
    out["BEL"], _ = make_flag_stripes([(20, 20, 22), (253, 218, 36), (239, 51, 64)], True)
    out["ITA"], _ = make_flag_stripes([(0, 146, 70), (246, 246, 246), (206, 43, 55)], True)
    out["GER"], _ = make_flag_stripes([(20, 20, 22), (221, 0, 0), (255, 206, 0)], False)
    out["RUS"], _ = make_flag_stripes([(246, 246, 246), (0, 57, 166), (213, 43, 30)], False)
    im, d = make_flag_stripes([(206, 17, 38), (246, 246, 246), (20, 20, 22)], False)
    cx, cy = 120, 80                                        # simplified gold eagle
    d.polygon([(cx, cy - 20), (cx + 8, cy - 8), (cx + 26, cy - 14), (cx + 16, cy + 6), (cx + 8, cy + 18),
               (cx - 8, cy + 18), (cx - 16, cy + 6), (cx - 26, cy - 14), (cx - 8, cy - 8)], fill=(192, 147, 44))
    d.rectangle([cx - 5, cy - 4, cx + 5, cy + 10], fill=(246, 246, 246))
    out["EGY"] = im
    im, d = _flag(240, 160)                                 # red with a white-edged blue cross
    d.rectangle([0, 0, 240, 160], fill=(186, 12, 47))
    d.rectangle([66, 0, 106, 160], fill=WHITE)
    d.rectangle([0, 60, 240, 100], fill=WHITE)
    d.rectangle([76, 0, 96, 160], fill=(0, 32, 91))
    d.rectangle([0, 70, 240, 90], fill=(0, 32, 91))
    out["NOR"] = im
    im, d = _flag(240, 160)                                 # 9 stripes + the sun
    for k in range(9):
        d.rectangle([0, k * 160 / 9, 240, (k + 1) * 160 / 9], fill=WHITE if k % 2 == 0 else (0, 56, 168))
    d.rectangle([0, 0, 96, 160 * 5 / 9], fill=WHITE)
    sx, sy = 48, 44
    d.polygon(_star_pts(sx, sy, 34, 18, 8, 0), fill=(252, 209, 22))
    d.ellipse([sx - 16, sy - 16, sx + 16, sy + 16], fill=(252, 209, 22), outline=(140, 90, 20), width=2)
    out["URU"] = im
    for code, im in out.items():
        pixelate(im, 3).save(os.path.join(OUT, "flag_%s.png" % code))
    return len(out)


def make_star_art(cards):
    stars = [c for c in cards if c["kind"] == "star"]
    MS.main_stars(OUT, [(c["id"][5:], c["team"], c["number"]) for c in stars])
    MS.main_robots(OUT)                                   # practice-mode robots
    print("no.10 pack:", make_no10_art(cards))
    rookies = [c for c in cards if c["kind"] == "rookie"]
    MS.main_stars(OUT, [(c["id"][7:], c["team"], c["number"]) for c in rookies], "ROOKIE", MS.ROOKIE_LOOKS)
    make_extra_flags()
    make_star_bg().save(os.path.join(OUT, "star_bg.png"))
    make_pack_star().save(os.path.join(OUT, "pack_star.png"))
    return len(stars)


# ======================================================================= pool card designs (A/B/C)
def _noise(d, box, rnd, cols, n=900, size=(2, 5)):
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        s = rnd.randint(*size)
        d.rectangle([x, y, x + s, y + s], fill=rnd.choice(cols))


def _plate(bd, y_top, top, bottom, line, width=3):
    x0, y0, x1, y1 = BODY
    _grad(bd, (x0, y_top, x1, y1), top, bottom)
    bd.line([(x0, y_top), (x1, y_top)], fill=line, width=width)


def make_eclipse_template():
    """Pool A - ECLIPSE: black to deep purple, a huge glow behind the player,
    thin metallic border, drifting particles. The giant number is drawn in-game."""
    import math as _m
    import random as _r
    from PIL import ImageFilter
    rnd = _r.Random(10)
    x0, y0, x1, y1 = BODY
    im = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    glow = Image.new("L", (TPL_W, TPL_H), 0)
    ImageDraw.Draw(glow).rounded_rectangle([x0 - 14, y0 - 14, x1 + 14, y1 + 14], 20, fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(12))
    layer = Image.new("RGBA", (TPL_W, TPL_H), (150, 60, 230, 0))
    layer.putalpha(glow.point(lambda v: int(v * 0.8)))
    im.alpha_composite(layer)
    body = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    _grad(bd, BODY, (10, 4, 22), (62, 16, 118))            # black -> deep purple
    halo = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    for r in range(16, 0, -1):                             # the eclipse corona behind the player
        rr = 40 + r * 11
        hd.ellipse([200 - rr, 210 - rr, 200 + rr, 210 + rr], fill=(150, 60, 240, 9))
    hd.ellipse([200 - 108, 210 - 108, 200 + 108, 210 + 108], fill=(16, 6, 30, 255))
    hd.ellipse([200 - 112, 210 - 112, 200 + 112, 210 + 112], outline=(196, 130, 255, 160), width=3)
    body.alpha_composite(halo)
    for _ in range(90):                                    # drifting particles
        px, py = rnd.uniform(x0, x1), rnd.uniform(y0, y1 - 60)
        sz = rnd.choice([2, 2, 3, 4])
        bd.rectangle([px, py, px + sz, py + sz],
                     fill=rnd.choice([(214, 170, 255), (150, 80, 240), (255, 255, 255), (120, 40, 200)]))
    for k in range(3):                                     # thin light rays
        a = _m.radians(-58 + k * 12)
        bd.line([(x0, y0 + 120 + k * 60), (x0 + _m.cos(a) * 600, y0 + 120 + k * 60 + _m.sin(a) * 600)],
                fill=(90, 40, 160), width=2)
    _plate(bd, 340, (36, 10, 72), (12, 4, 26), (200, 150, 255))
    body.putalpha(Image.composite(body.split()[3], Image.new("L", body.size, 0), _body_mask(16)))
    im.alpha_composite(body)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x0 - 6, y0 - 6, x1 + 6, y1 + 6], 20, outline=(88, 92, 112), width=6)   # metal
    d.rounded_rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], 18, outline=(226, 200, 255), width=2)
    d.rounded_rectangle([x0 + 4, y0 + 4, x1 - 4, y1 - 4], 14, outline=(120, 60, 200), width=2)
    for sx in (x0 - 6, x1 + 6):                            # tiny corner sparks
        for sy in (y0 + 30, y1 - 30):
            _sparkle(d, sx, sy, 7, (236, 214, 255))
    return im


def make_neon_template():
    """Pool B - NEON PLAYMAKER: navy, cyan neon lines, stadium lights, a diagonal streak."""
    import random as _r
    rnd = _r.Random(21)
    x0, y0, x1, y1 = BODY
    im = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    body = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    _grad(bd, BODY, (12, 26, 64), (6, 12, 32))
    for k in range(6):                                     # stadium lights along the top
        lx = x0 + 24 + k * 48
        for r in range(9, 0, -1):
            bd.ellipse([lx - r * 3, y0 + 18 - r * 3, lx + r * 3, y0 + 18 + r * 3], fill=(60, 150, 220, 10))
        bd.ellipse([lx - 5, y0 + 13, lx + 5, y0 + 23], fill=(190, 230, 255))
    for k in range(-6, 12):                                # neon grid
        bd.line([(x0 + k * 28, y1), (x0 + k * 28 + 160, y0)], fill=(26, 70, 130), width=2)
    for y in range(y0 + 40, y1, 46):
        bd.line([(x0, y), (x1, y)], fill=(22, 58, 112), width=1)
    bd.polygon([(x0, 300), (x1, 170), (x1, 214), (x0, 344)], fill=(30, 200, 240))        # diagonal streak
    bd.polygon([(x0, 312), (x1, 182), (x1, 190), (x0, 320)], fill=(190, 250, 255))
    for k in range(4):                                     # neon frame lines inside
        bd.line([(x0 + 10, y0 + 10 + k), (x1 - 10, y0 + 10 + k)], fill=(40, 210, 255))
    _plate(bd, 340, (10, 34, 78), (6, 14, 36), (40, 210, 255))
    body.putalpha(Image.composite(body.split()[3], Image.new("L", body.size, 0), _body_mask(16)))
    im.alpha_composite(body)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x0 - 7, y0 - 7, x1 + 7, y1 + 7], 20, outline=(150, 166, 196), width=7)  # silver
    d.rounded_rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], 18, outline=(60, 220, 255), width=3)
    for sx in (x0 - 7, x1 + 7):
        d.line([(sx, y0 + 40), (sx, y1 - 40)], fill=(90, 230, 255), width=3)
    return im


def make_street_template():
    """Pool C - STREET CARD: concrete, scratches, a cheap silver border."""
    import random as _r
    rnd = _r.Random(33)
    x0, y0, x1, y1 = BODY
    im = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    body = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    _grad(bd, BODY, (96, 104, 92), (54, 64, 56))
    _noise(bd, BODY, rnd, [(108, 116, 104), (86, 94, 84), (120, 128, 114), (70, 78, 70)], 1400, (2, 6))
    for _ in range(26):                                    # scratches
        sx, sy = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        bd.line([(sx, sy), (sx + rnd.uniform(-40, 40), sy + rnd.uniform(-16, 16))],
                fill=rnd.choice([(134, 142, 128), (64, 72, 64)]), width=1)
    bd.rectangle([x0, y0, x1, y0 + 4], fill=(120, 128, 114))
    _plate(bd, 340, (52, 62, 54), (34, 42, 36), (150, 158, 146), 2)
    body.putalpha(Image.composite(body.split()[3], Image.new("L", body.size, 0), _body_mask(12)))
    im.alpha_composite(body)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x0 - 6, y0 - 6, x1 + 6, y1 + 6], 14, outline=(126, 132, 122), width=6)
    d.rounded_rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], 12, outline=(178, 184, 172), width=2)
    return im


def make_no10_badge(W=240, H=280):
    """The pack's crest: a glowing 10 on a dark shield."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(20, 16), (W - 20, 16), (W - 20, H - 80), (W // 2, H - 16), (20, H - 80)]
    d.polygon(pts, fill=(18, 6, 34), outline=(190, 140, 255))
    d.polygon([(p[0] + 8, p[1] + 8) if i < 2 else (p[0] - 8, p[1] - 8) for i, p in enumerate(pts)],
              outline=(120, 60, 200))
    t = text_img("10", 120, (236, 214, 255), (90, 30, 160), 6)
    im.alpha_composite(t, ((W - t.width) // 2, (H - t.height) // 2 - 14))
    return pixelate(im, 3)


def make_pack_no10(W=300, H=420):
    """The No. 10 pack: black-purple foil with a giant 10."""
    import random as _r
    rnd = _r.Random(7)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    _grad(bd, (10, 24, W - 10, H - 24), (8, 2, 18), (78, 20, 150))
    for _ in range(70):
        px, py = rnd.uniform(10, W - 10), rnd.uniform(24, H - 24)
        s = rnd.choice([2, 3, 4])
        bd.rectangle([px, py, px + s, py + s], fill=rnd.choice([(214, 170, 255), (255, 255, 255), (140, 60, 230)]))
    big = text_img("10", 210, (150, 70, 240), (20, 6, 40), 8)
    body.alpha_composite(big, ((W - big.width) // 2, 92))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([10, 24, W - 10, H - 24], 18, fill=255)
    body.putalpha(mask)
    im.alpha_composite(body)
    for x in range(10, W - 10, 12):
        d.polygon([(x, 26), (x + 6, 8), (x + 12, 26)], fill=(150, 80, 230))
        d.polygon([(x, H - 26), (x + 6, H - 8), (x + 12, H - 26)], fill=(150, 80, 230))
    d.rectangle([10, 24, W - 10, 40], fill=(120, 50, 200))
    d.rectangle([10, H - 40, W - 10, H - 24], fill=(120, 50, 200))
    d.rounded_rectangle([10, 24, W - 10, H - 24], 18, outline=(226, 200, 255), width=5)
    d.rectangle([22, 286, W - 22, 360], fill=(14, 4, 28))
    d.line([(22, 286), (W - 22, 286)], fill=(190, 140, 255), width=3)
    t = text_img("NO. 10", 36, WHITE, (60, 16, 110), 3)
    im.alpha_composite(t, ((W - t.width) // 2, 296))
    t2 = text_img("PLAYMAKERS", 22, (214, 170, 255), (60, 16, 110), 3)
    im.alpha_composite(t2, ((W - t2.width) // 2, 336))
    return pixelate(im, 3)


def make_more_flags():
    """Romania, Turkey, Denmark, Sweden."""
    out = {}
    out["ROU"], _ = make_flag_stripes([(0, 43, 127), (252, 209, 22), (206, 17, 38)], True)
    im, d = _flag(240, 160)                                 # red with a white crescent + star
    d.rectangle([0, 0, 240, 160], fill=(227, 10, 23))
    d.ellipse([70, 45, 140, 115], fill=WHITE)
    d.ellipse([88, 50, 148, 110], fill=(227, 10, 23))
    d.polygon(_star_pts(160, 80, 26, 11), fill=WHITE)
    out["TUR"] = im
    im, d = _flag(240, 160)
    d.rectangle([0, 0, 240, 160], fill=(198, 12, 48))
    d.rectangle([64, 0, 96, 160], fill=WHITE)
    d.rectangle([0, 64, 240, 96], fill=WHITE)
    out["DEN"] = im
    im, d = _flag(240, 160)
    d.rectangle([0, 0, 240, 160], fill=(0, 82, 147))
    d.rectangle([64, 0, 96, 160], fill=(254, 204, 0))
    d.rectangle([0, 64, 240, 96], fill=(254, 204, 0))
    out["SWE"] = im
    for code, im in out.items():
        pixelate(im, 3).save(os.path.join(OUT, "flag_%s.png" % code))
    return len(out)


def make_no10_art(cards):
    ten = [c for c in cards if c["kind"] == "no10"]
    MS.main_stars(OUT, [(c["id"][5:], MS_CODE.get(c["team"], c["team"]), c["number"]) for c in ten],
                  "NO10", MS.NO10_LOOKS)
    make_more_flags()
    make_no10_badge().save(os.path.join(OUT, "no10_badge.png"))
    make_pack_no10().save(os.path.join(OUT, "pack_4.png"))
    return len(ten)


# ======================================================================= The World's Game + Essence
# The card category only Essence can sign, the foil it comes in and the shop's backdrop.
# The card is what Hubi described from his pictures: a purple flag behind it, a silver border
# that runs through the rainbow, and stars (which the game animates). The Essence shop keeps
# its own ember red, so the purple card is the one bright thing in it.
EMBER = (255, 92, 64)
EMBER_HOT = (255, 206, 132)
WG_GOLD = (240, 200, 104)            # only the faint globe in the shop's backdrop still uses it
WG_PLATE = (20, 8, 44)               # the dark the name sits on (the game's scrim matches it)


def _hot(c, k):
    """Brighter or darker without drifting to grey: a dark red stays red."""
    return tuple(max(0, min(255, int(v * k))) for v in c)


def _globe(d, cx, cy, r, col, width=2, meridians=4, parallels=3):
    """A wire globe: the outline, a few meridians (ellipses) and parallels (chords)."""
    import math as _m
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=width + 1)
    for k in range(1, meridians + 1):
        rx = r * k / (meridians + 0.6)
        d.ellipse([cx - rx, cy - r, cx + rx, cy + r], outline=col, width=width)
    d.line([(cx, cy - r), (cx, cy + r)], fill=col, width=width)
    for k in range(-parallels, parallels + 1):
        y = cy + r * k / (parallels + 0.9)
        half = _m.sqrt(max(0.0, r * r - (y - cy) ** 2))
        d.line([(cx - half, y), (cx + half, y)], fill=col, width=width)


def _embers(d, box, rnd, n, hot=EMBER_HOT, alpha=(90, 220), size=(2, 4, 6)):
    x0, y0, x1, y1 = box
    for _ in range(n):
        s = rnd.choice(size)
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        col = mix(EMBER, hot, rnd.random())
        d.rectangle([x, y, x + s, y + s], fill=col + (rnd.randint(*alpha),))


def _rainbow_silver(size, steps=320, repeats=2.0):
    """Silver that goes through the rainbow as it crosses the card: the World's Game border."""
    w, h = size
    band = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(band)
    stops = [(238, 242, 250), (255, 186, 224), (255, 232, 176), (186, 250, 220), (178, 222, 255),
             (222, 192, 255), (238, 242, 250)]
    span = w + h
    for i in range(steps):
        t = (i / float(steps - 1) * repeats) % 1.0
        k = t * (len(stops) - 1)
        col = mix(stops[int(k)], stops[min(len(stops) - 1, int(k) + 1)], k - int(k))
        x = -h + span * i / float(steps - 1)
        d.line([(x, 0), (x + h, h)], fill=col, width=int(span / steps) + 3)
    return band


def _purple_flag(w, h, seed=7):
    """A purple flag with paler swirls across it - cloth, before it is made to ripple."""
    import math as _m
    import random as _r
    rnd = _r.Random(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=mix((128, 56, 226), (70, 22, 160), y / float(h)))
    over = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    for k in range(7):                                     # broad swirls, each a slice of a big ring
        cx, cy = rnd.uniform(-0.1, 1.1) * w, rnd.uniform(-0.3, 1.3) * h
        r = rnd.uniform(0.35, 0.8) * w
        col = rnd.choice([(176, 120, 255), (150, 84, 240), (206, 150, 255), (98, 40, 196)])
        od.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], outline=col + (rnd.choice([70, 96, 120]),),
                   width=int(rnd.uniform(14, 40)))
    for k in range(5):                                     # a few thin bright threads
        cx, cy = rnd.uniform(0, 1) * w, rnd.uniform(-0.2, 1.2) * h
        r = rnd.uniform(0.3, 0.7) * w
        od.ellipse([cx - r, cy - r * 0.7, cx + r, cy + r * 0.7], outline=(232, 206, 255, 90), width=3)
    im.alpha_composite(over)
    return im


def make_worldsgame_template(phase=0.6):
    """THE WORLD'S GAME card: a purple flag flying behind it, a silver border that runs
    through the rainbow, and a second fine line inside that. Built the way the World Cup
    holo card is (make_holo_template) so the game lays both out with one routine. The silver
    stars round it are not in this picture: the game draws them itself, because they move."""
    flag = _purple_flag(640, 460)
    x0, y0, x1, y1 = BODY
    im = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    import math as _m
    bw, bh = TPL_W + 170, int((y1 - y0) * 1.04)
    back = wave_flag(flag, bw, bh, phase, amp=0.085, folds=3.1)
    back = ImageEnhance.Brightness(back).enhance(0.74)
    # cut it to the shape of cloth: the top and bottom edges ride the same wave the folds do,
    # and the two ends hang in a shallow curve instead of standing as straight walls
    cloth = Image.new("L", (bw, bh), 0)
    top, bot = [], []
    for x in range(0, bw + 1, 4):
        t = x / float(bw)
        wave = _m.sin(t * 3.1 * _m.tau + phase) * bh * 0.085
        end = 26.0 * (abs(t - 0.5) * 2.0) ** 3                 # the ends droop
        top.append((x, 30 + wave * 0.55 + end))
        bot.append((x, bh - 30 + wave * 0.55 - end * 0.6))
    ImageDraw.Draw(cloth).polygon(top + bot[::-1], fill=255)
    back.putalpha(cloth)
    im.alpha_composite(back, (-85, y0 - 8))
    drop = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    ImageDraw.Draw(drop).polygon(_holo_card_path((x0 + 6, y0 + 10, x1 + 10, y1 + 12)), fill=(12, 2, 30, 130))
    im.alpha_composite(drop)
    card = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))
    inner = wave_flag(_purple_flag(640, 460, seed=11), (x1 - x0) + 30, (y1 - y0) + 10, phase + 1.4,
                      amp=0.05, folds=2.2)
    inner = ImageEnhance.Brightness(inner).enhance(1.08)
    card.alpha_composite(inner, (x0 - 15, y0 - 5))
    ring = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))          # the big pale ring behind the player
    rd = ImageDraw.Draw(ring)
    gx, gy = (x0 + x1) / 2 + 26, y0 + 168
    rd.ellipse([gx - 150, gy - 150, gx + 150, gy + 150], outline=(226, 200, 255, 110), width=16)
    rd.ellipse([gx - 112, gy - 112, gx + 112, gy + 112], outline=(240, 224, 255, 64), width=5)
    card.alpha_composite(ring)
    plate = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))         # the name sits on this
    pdd = ImageDraw.Draw(plate)
    for y in range(314, y1 + 1):
        a = int(242 * min(1.0, ((y - 314) / 44.0) ** 1.4))
        pdd.line([(x0, y), (x1, y)], fill=WG_PLATE + (a,))
    card.alpha_composite(plate)
    shadow = Image.new("RGBA", (TPL_W, TPL_H), (0, 0, 0, 0))        # top-left, for the rating
    sd = ImageDraw.Draw(shadow)
    for k in range(26):
        sd.ellipse([x0 - 140 + k * 6, y0 - 130 + k * 6, x0 + 232 - k * 6, y0 + 218 - k * 6], fill=(14, 4, 34, 20))
    card.alpha_composite(shadow)
    shape = Image.new("L", (TPL_W, TPL_H), 0)
    ImageDraw.Draw(shape).polygon(_holo_card_path(BODY), fill=255)
    card.putalpha(Image.composite(card.split()[3], Image.new("L", card.size, 0), shape))
    im.alpha_composite(card)
    # ---- the border: a dark edge, the rainbow silver, a white hairline, and a second line inside
    d = ImageDraw.Draw(im)
    path = _holo_card_path(BODY)
    d.line(path + [path[0]], fill=(30, 18, 58), width=17, joint="curve")
    band = _rainbow_silver((TPL_W, TPL_H))
    ring = Image.new("L", (TPL_W, TPL_H), 0)
    ImageDraw.Draw(ring).line(path + [path[0]], fill=255, width=12, joint="curve")
    im.paste(band, (0, 0), ring)
    d.line(path + [path[0]], fill=(255, 255, 255), width=2, joint="curve")
    inner_path = _holo_card_path((x0 + 13, y0 + 13, x1 - 13, y1 - 13))
    ring2 = Image.new("L", (TPL_W, TPL_H), 0)
    ImageDraw.Draw(ring2).line(inner_path + [inner_path[0]], fill=200, width=3, joint="curve")
    im.paste(_rainbow_silver((TPL_W, TPL_H), repeats=3.0), (0, 0), ring2)
    # ---- the gem at the bottom, sitting over the border
    cx, cy = (x0 + x1) // 2, y1 - 2
    d.polygon([(cx, cy - 20), (cx + 21, cy - 8), (cx + 21, cy + 12), (cx, cy + 24),
               (cx - 21, cy + 12), (cx - 21, cy - 8)], fill=(122, 110, 168), outline=(240, 242, 252))
    d.polygon([(cx, cy - 13), (cx + 13, cy - 6), (cx + 13, cy + 7), (cx, cy + 15),
               (cx - 13, cy + 7), (cx - 13, cy - 6)], fill=(214, 204, 244))
    return im


def _silver_star(d, cx, cy, r, rot=-1.5707963, light=(240, 244, 252), dark=(140, 146, 178), edge=(44, 28, 80)):
    """A five-point star cut like a gem: every arm has a bright side and a dull side."""
    import math as _m
    d.polygon(_star_pts(cx, cy, r * 1.14, r * 0.52, rot=rot), fill=edge)
    pts = _star_pts(cx, cy, r, r * 0.44, rot=rot)
    for k in range(5):
        tip, a, b = pts[2 * k], pts[(2 * k - 1) % 10], pts[(2 * k + 1) % 10]
        d.polygon([(cx, cy), a, tip], fill=light)
        d.polygon([(cx, cy), tip, b], fill=dark)


def make_pack_wg(W=300, H=420):
    """The purple foil a World's Game player comes out of: rainbow-silver crimps, three stars."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    body = wave_flag(_purple_flag(W, H, seed=3), W, H, 0.4, amp=0.0, folds=2.0)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([10, 24, W - 10, H - 24], 18, fill=255)
    body.putalpha(mask)
    im.alpha_composite(body)
    foil = _rainbow_silver((W, H), repeats=2.0)
    trim = Image.new("L", (W, H), 0)
    td = ImageDraw.Draw(trim)
    for x in range(10, W - 10, 12):                        # crimped foil ends
        td.polygon([(x, 26), (x + 6, 8), (x + 12, 26)], fill=255)
        td.polygon([(x, H - 26), (x + 6, H - 8), (x + 12, H - 26)], fill=255)
    td.rectangle([10, 24, W - 10, 40], fill=255)
    td.rectangle([10, H - 40, W - 10, H - 24], fill=255)
    td.rounded_rectangle([10, 24, W - 10, H - 24], 18, outline=255, width=6)
    im.paste(foil, (0, 0), trim)
    d = ImageDraw.Draw(im)
    _silver_star(d, W // 2, 150, 70)
    _silver_star(d, 74, 232, 30, rot=-1.2)
    _silver_star(d, W - 70, 96, 24, rot=-1.9)
    d.rectangle([22, 280, W - 22, 372], fill=(34, 12, 78))
    im.paste(foil, (0, 0), Image.composite(Image.new("L", (W, H), 255), Image.new("L", (W, H), 0),
                                           _rule_mask(W, H, ((22, 278, W - 22, 282), (22, 370, W - 22, 374)))))
    t = text_img("THE WORLD'S", 30, WHITE, (40, 10, 90), 3)
    im.alpha_composite(t, ((W - t.width) // 2, 306 - t.height // 2))
    t2 = text_img("GAME", 36, (226, 210, 255), (40, 10, 90), 4)
    im.alpha_composite(t2, ((W - t2.width) // 2, 346 - t2.height // 2))
    return pixelate(im, 3)


def _rule_mask(W, H, boxes):
    m = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(m)
    for b in boxes:
        md.rectangle(list(b), fill=255)
    return m


def make_essence_bg(W=1920, H=1080):
    """The Essence shop: dark red facets, heat coming up from below, embers in the air."""
    import math as _m
    import random as _r
    rnd = _r.Random(41)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    _low_poly(d, (0, 0, W, H), (26, 8, 12), (82, 18, 20), rnd, 16, 9, 0.4, (W * 0.24, H * 0.62, 560), _hot)
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    cx, cy = int(W * 0.24), int(H * 1.08)
    for k in range(16):                                    # heat rising from under the slot
        a = -_m.pi + k * _m.pi / 15
        od.polygon([(cx, cy), (cx + _m.cos(a) * 2600, cy + _m.sin(a) * 2600),
                    (cx + _m.cos(a + 0.05) * 2600, cy + _m.sin(a + 0.05) * 2600)], fill=(255, 120, 70, 14))
    _globe(od, int(W * 0.24), int(H * 0.56), 470, WG_GOLD + (26,), 5, 4, 3)
    _embers(od, (0, 0, W, H), rnd, 230, alpha=(60, 200), size=(3, 6, 9))
    for k in range(10):                                    # vignette
        od.rectangle([0, 0, W, 24 * k], fill=(8, 2, 4, 14))
        od.rectangle([0, H - 14 * k, W, H], fill=(8, 2, 4, 8))
    im.alpha_composite(over)
    return pixelate(im, 3)


def worldsgame_frame(tpl):
    """The same picture with the inside of the card cut out: everything that must sit IN FRONT
    of the player - the border, and the flag outside it. The game lays it over him, so an arm
    or a shoulder ends at the border's curve instead of at a square corner."""
    x0, y0, x1, y1 = BODY
    hole = Image.new("L", tpl.size, 255)
    ImageDraw.Draw(hole).polygon(_holo_card_path((x0 + 5, y0 + 5, x1 - 5, y1 - 5)), fill=0)
    out = tpl.copy()
    out.putalpha(ImageChops.multiply(tpl.split()[3], hole))
    return out


def make_wg_players(cards):
    """The World's Game players as they appear in a match: head, torso, arm, leg."""
    made = 0
    for c in cards:
        if c["kind"] != "wg":
            continue
        slug = c["id"][3:]
        skin, hair, style, beard, extras = card_look(c)
        kit = card_kit(c)
        sk, hr = MS.SKIN[skin], MS.HAIR.get(hair, (196, 158, 92))
        base = os.path.join(OUT, "WG_" + slug)
        MS.make_head(sk, hr, MS.HEAD_STYLE.get(style, "short"), beard, extras).save(base + "_head.png")
        MS.make_torso(kit, c["number"]).save(base + "_torso.png")
        MS.make_arm(kit, sk).save(base + "_arm.png")
        MS.make_leg(kit, sk, MS.STAR_BOOTS[sum(map(ord, slug)) % len(MS.STAR_BOOTS)]).save(base + "_leg.png")
        made += 1
    return made


def make_essence_art():
    tpl = make_worldsgame_template()
    tpl.save(os.path.join(OUT, "tpl_wg_card.png"))
    worldsgame_frame(tpl).save(os.path.join(OUT, "tpl_wgframe_card.png"))
    make_pack_wg().save(os.path.join(OUT, "pack_wg.png"))
    make_essence_bg().save(os.path.join(OUT, "essence_bg.png"))
    return 3


def main():
    faces = {}
    for name, spec in ICONS.items():
        faces[name] = portrait(*spec)
        faces[name].save(os.path.join(OUT, "icon_%s.png" % name))
    packs = [make_pack(i) for i in range(4)]
    for i, p in enumerate(packs):
        if i in (1, 2, 3):             # Champion Drafts A, B and C - make_champ_cards.py draws them
            import make_champ_cards
            p = make_champ_cards.make_pack(OUT, "ABC"[i - 1])
        p.save(os.path.join(OUT, "pack_%d.png" % i))
    make_card_back().save(os.path.join(OUT, "card_back.png"))
    make_ball().save(os.path.join(OUT, "ball.png"))
    make_banner_champions(faces).save(os.path.join(OUT, "banner_1.png"))
    make_banner_wcpack(packs[0], [faces["messi"], faces["ronaldo"], faces["mbappe"]]).save(
        os.path.join(OUT, "banner_2.png"))
    make_banner_neymar(faces["neymar"]).save(os.path.join(OUT, "banner_3.png"))
    make_slide_playnow().save(os.path.join(OUT, "slide_1.png"))
    make_slide_champions(faces).save(os.path.join(OUT, "slide_2.png"))
    make_slide_pack(packs[0], [faces["messi"], faces["ronaldo"], faces["mbappe"]]).save(os.path.join(OUT, "slide_3.png"))
    make_slide_neymar(faces["neymar"]).save(os.path.join(OUT, "slide_4.png"))
    make_neymar_sprites()
    make_event_bg().save(os.path.join(OUT, "event_bg.png"))
    make_ren_art()
    cards = load_card_db()
    print("star signings:", make_star_art(cards))
    print("card faces:", make_card_faces(cards))
    print("card figures:", make_card_figures(cards))
    print("card templates:", make_card_templates(cards))
    print("essence shop art:", make_essence_art())
    print("world's game players:", make_wg_players(cards))
    make_slide_stars(cards).save(os.path.join(OUT, "slide_5.png"))
    make_box_neymar().save(os.path.join(OUT, "box_neymar.png"))
    for i in range(4):
        make_stadium(i).save(os.path.join(OUT, "stadium_%d.png" % i))
    make_shop_bg().save(os.path.join(OUT, "shop_bg.png"))
    make_wc_badge().save(os.path.join(OUT, "wc_badge.png"))
    make_flag_usa().save(os.path.join(OUT, "flag_USA.png"))
    make_flag_ksa().save(os.path.join(OUT, "flag_KSA.png"))
    print("art written to", OUT)


if __name__ == "__main__":
    main()


