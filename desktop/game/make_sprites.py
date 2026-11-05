"""Generate pixel-art player sprites for Ragdoll Football.

Canvas sizes match the hand-made Canva originals:
  head 160x160 (16x16 blocks of 10px, transparent background)
  torso 128x128 (16x16 blocks of 8px)
  arm / leg 48x128 (6x16 blocks of 8px)
No eyes (house style). Badges are simple shields in team colours with one star
per World Cup won (Spain has 2 after winning in 2026) - no real federation logos.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont



def shade(c, k):
    """k<1 darker, k>1 lighter."""
    if k < 1:
        return tuple(max(0, int(v * k)) for v in c)
    return tuple(min(255, int(v + (255 - v) * (k - 1))) for v in c)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Grid:
    def __init__(self, w, h, block, bg=None):
        self.w, self.h, self.block = w, h, block
        self.px = [[bg for _ in range(w)] for _ in range(h)]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h and c is not None:
            self.px[y][x] = c

    def get(self, x, y):
        return self.px[y][x] if 0 <= x < self.w and 0 <= y < self.h else None

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c)

    def image(self):
        img = Image.new("RGBA", (self.w * self.block, self.h * self.block), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        for y in range(self.h):
            for x in range(self.w):
                c = self.px[y][x]
                if c is not None:
                    d.rectangle([x * self.block, y * self.block,
                                 (x + 1) * self.block - 1, (y + 1) * self.block - 1], fill=c + (255,))
        return img


# ---------------------------------------------------------------- palettes
SKIN = {
    "pale": (244, 212, 184), "light": (232, 190, 158), "tan": (206, 160, 122),
    "olive": (188, 140, 102), "brown": (150, 102, 74), "dark": (112, 74, 56),
    "deep": (84, 55, 42),
}
HAIR = {
    "black": (30, 24, 24), "darkbrown": (58, 38, 30), "brown": (96, 64, 40),
    "lightbrown": (140, 100, 62), "blond": (196, 158, 92), "ginger": (158, 84, 44),
}
GOLD = (236, 190, 60)
WHITE = (246, 246, 246)
NAVY = (22, 32, 72)

DIGITS = {
    "0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"], "3": ["111", "001", "111", "001", "111"],
    "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"], "7": ["111", "001", "010", "010", "010"],
    "8": ["111", "101", "111", "101", "111"], "9": ["111", "101", "111", "001", "111"],
}

# ---------------------------------------------------------------- kits
# pattern: plain | stripes | checks | weave | lines | fade | dots
KITS = {
    "ARG": dict(base=(117, 180, 228), alt=WHITE, pattern="stripes", trim=NAVY, number=NAVY,
                shorts=(24, 24, 30), shorts_trim=(117, 180, 228), socks=WHITE, sock_trim=(117, 180, 228),
                badge=((117, 180, 228), WHITE), stars=3),
    "BRA": dict(base=(252, 214, 40), alt=(240, 196, 24), pattern="weave", trim=(0, 150, 72), number=(0, 110, 60),
                shorts=(28, 82, 170), shorts_trim=WHITE, socks=WHITE, sock_trim=(252, 214, 40),
                badge=((28, 82, 170), (252, 214, 40)), stars=5),
    "CRO": dict(base=(214, 32, 42), alt=WHITE, pattern="checks", trim=(26, 56, 140), number=(26, 56, 140),
                number_outline=WHITE,
                shorts=WHITE, shorts_trim=(214, 32, 42), socks=(26, 56, 140), sock_trim=(214, 32, 42),
                badge=((214, 32, 42), WHITE), stars=0),
    "ENG": dict(base=WHITE, alt=(232, 232, 236), pattern="plain", trim=NAVY, number=NAVY,
                shorts=NAVY, shorts_trim=WHITE, socks=WHITE, sock_trim=NAVY,
                badge=(WHITE, (200, 30, 45)), stars=1),
    "FRA": dict(base=(26, 46, 112), alt=(36, 58, 130), pattern="plain", trim=WHITE, placket=(212, 32, 46),
                number=WHITE, shorts=WHITE, shorts_trim=(26, 46, 112), socks=(212, 32, 46), sock_trim=WHITE,
                badge=(WHITE, GOLD), stars=2),
    "MOR": dict(base=(182, 22, 32), alt=(0, 112, 62), pattern="dots", trim=(0, 112, 62), number=WHITE,
                shorts=(0, 112, 62), shorts_trim=(182, 22, 32), socks=(182, 22, 32), sock_trim=(0, 112, 62),
                badge=((0, 112, 62), (182, 22, 32)), stars=0),
    "JPN": dict(base=(22, 42, 112), alt=(92, 124, 176), pattern="lines", trim=WHITE, number=WHITE,
                shorts=(22, 42, 112), shorts_trim=WHITE, socks=(22, 42, 112), sock_trim=WHITE,
                badge=(WHITE, (210, 30, 40)), stars=0),
    "POL": dict(base=WHITE, alt=(236, 236, 240), pattern="plain", trim=(220, 22, 60), number=(220, 22, 60),
                shorts=(220, 22, 60), shorts_trim=WHITE, socks=WHITE, sock_trim=(220, 22, 60),
                badge=((220, 22, 60), WHITE), stars=0),
    "NED": dict(base=(245, 112, 22), alt=(232, 98, 14), pattern="plain", trim=(24, 24, 24), number=(24, 24, 24),
                shorts=(245, 112, 22), shorts_trim=(24, 24, 24), socks=(245, 112, 22), sock_trim=(24, 24, 24),
                badge=((24, 24, 24), (245, 112, 22)), stars=0),
    "AUS": dict(base=(255, 198, 32), alt=(0, 122, 72), pattern="fade", trim=(0, 122, 72), number=(0, 122, 72),
                shorts=(0, 122, 72), shorts_trim=(255, 198, 32), socks=(255, 198, 32), sock_trim=(0, 122, 72),
                badge=((0, 122, 72), (255, 198, 32)), stars=0),
    "ESP": dict(base=(202, 22, 34), alt=(186, 16, 28), pattern="plain", trim=(250, 200, 24), number=(250, 200, 24),
                shorts=NAVY, shorts_trim=(202, 22, 34), socks=NAVY, sock_trim=(202, 22, 34),
                badge=((202, 22, 34), (250, 200, 24)), stars=2),         # 2010 + 2026
    "POR": dict(base=(172, 20, 36), alt=(156, 14, 30), pattern="plain", trim=(0, 102, 60), number=GOLD,
                shorts=(0, 102, 60), shorts_trim=(172, 20, 36), socks=(172, 20, 36), sock_trim=(0, 102, 60),
                badge=((0, 102, 60), (172, 20, 36)), stars=0),
}

# four more national kits, for the No. 10 pack portraits
KITS["GER"] = dict(base=WHITE, alt=(236, 236, 240), pattern="plain", trim=(20, 20, 24), number=(20, 20, 24),
                   shorts=(20, 20, 24), shorts_trim=WHITE, socks=WHITE, sock_trim=(20, 20, 24),
                   badge=((20, 20, 24), (221, 0, 0)), stars=4)
KITS["ROU"] = dict(base=(252, 209, 22), alt=(240, 196, 16), pattern="plain", trim=(0, 43, 127),
                   number=(0, 43, 127), shorts=(0, 43, 127), shorts_trim=(252, 209, 22), socks=(206, 17, 38),
                   sock_trim=(252, 209, 22), badge=((0, 43, 127), (252, 209, 22)), stars=0)
KITS["TUR"] = dict(base=(227, 10, 23), alt=(210, 8, 20), pattern="plain", trim=WHITE, number=WHITE,
                   shorts=WHITE, shorts_trim=(227, 10, 23), socks=(227, 10, 23), sock_trim=WHITE,
                   badge=((227, 10, 23), WHITE), stars=0)
KITS["DEN"] = dict(base=(198, 12, 48), alt=(186, 10, 44), pattern="plain", trim=WHITE, number=WHITE,
                   shorts=WHITE, shorts_trim=(198, 12, 48), socks=(198, 12, 48), sock_trim=WHITE,
                   badge=((198, 12, 48), WHITE), stars=0)
KITS["SWE"] = dict(base=(254, 204, 0), alt=(240, 190, 0), pattern="plain", trim=(0, 82, 147),
                   number=(0, 82, 147), shorts=(0, 82, 147), shorts_trim=(254, 204, 0), socks=(254, 204, 0),
                   sock_trim=(0, 82, 147), badge=((0, 82, 147), (254, 204, 0)), stars=0)

# ---------------------------------------------------------------- players
# (slug, display name, number, skin, hair colour, hair style, facial hair, boots, extras)
TEAMS = {
    "ARG": [("simeone", "Giuliano Simeone", 17, "light", "darkbrown", "curly", None, (30, 30, 36), ()),
            ("lautaro", "Lautaro Martinez", 22, "tan", "black", "short", "short", (240, 240, 244), ()),
            ("messi", "Messi", 10, "light", "brown", "short", "full", (255, 112, 182), ())],
    "BRA": [("igor", "Igor Thiago", 25, "deep", "black", "bald", None, (30, 30, 36), ("earring",)),
            ("bruno", "Bruno Guimaraes", 8, "olive", "darkbrown", "fade", "stubble", (240, 240, 244), ()),
            ("vinicius", "Vinicius Jr", 7, "dark", "black", "twists", None, (255, 210, 40), ())],
    "CRO": [("majer", "Lovro Majer", 7, "pale", "darkbrown", "short", "stubble", (30, 30, 36), ()),
            ("kovacic", "Mateo Kovacic", 8, "light", "darkbrown", "swept", "full", (240, 240, 244), ()),
            ("modric", "Modric", 10, "pale", "lightbrown", "long", None, (255, 112, 182), ())],
    "ENG": [("henderson", "Jordan Henderson", 14, "pale", "lightbrown", "short", "full", (30, 30, 36), ()),
            ("foden", "Phil Foden", 11, "pale", "lightbrown", "buzz", None, (240, 240, 244), ()),
            ("bellingham", "Bellingham", 10, "brown", "black", "fade", "goatee", (255, 210, 40), ())],
    "FRA": [("thuram", "Marcus Thuram", 9, "dark", "black", "fade", "short", (30, 30, 36), ()),
            ("dembele", "Ousmane Dembele", 7, "dark", "black", "buzz", None, (240, 240, 244), ()),
            ("mbappe", "Mbappe", 10, "brown", "black", "buzz", None, (255, 210, 40), ())],
    "MOR": [("elkhannouss", "Bilal El Khannouss", 23, "tan", "black", "curly", "stubble", (30, 30, 36), ()),
            ("amrabat", "Sofyan Amrabat", 4, "tan", "black", "short", "full", (240, 240, 244), ()),
            ("hakimi", "Hakimi", 2, "olive", "black", "fade", "short", (255, 210, 40), ())],
    "JPN": [("ueda", "Ayase Ueda", 18, "light", "black", "short", None, (30, 30, 36), ()),
            ("kubo", "Takefusa Kubo", 8, "light", "black", "swept", None, (240, 240, 244), ()),
            ("minamino", "Minamino", 10, "light", "black", "short", None, (255, 210, 40), ())],
    "POL": [("kaminski", "Jakub Kaminski", 13, "pale", "lightbrown", "short", None, (30, 30, 36), ()),
            ("zielinski", "Piotr Zielinski", 20, "pale", "brown", "short", "stubble", (240, 240, 244), ()),
            ("lewandowski", "Lewandowski", 9, "light", "darkbrown", "short", "stubble", (255, 210, 40), ())],
    "NED": [("weghorst", "Wout Weghorst", 9, "pale", "blond", "short", "full", (30, 30, 36), ()),
            ("gakpo", "Cody Gakpo", 11, "brown", "black", "short", "short", (240, 240, 244), ()),
            ("vandijk", "Van Dijk", 4, "brown", "black", "fade", "full", (255, 210, 40), ())],
    "AUS": [("yengi", "Kusini Yengi", 26, "deep", "black", "buzz", "stubble", (30, 30, 36), ()),
            ("irvine", "Jackson Irvine", 22, "pale", "ginger", "bun", "full", (240, 240, 244), ()),
            ("ryan", "Mathew Ryan", 1, "light", "darkbrown", "short", "stubble", (255, 210, 40), ())],
    "ESP": [("baena", "Alex Baena", 15, "light", "darkbrown", "short", "short", (30, 30, 36), ()),
            ("olmo", "Dani Olmo", 10, "light", "darkbrown", "swept", "short", (240, 240, 244), ()),
            ("yamal", "Lamine Yamal", 19, "brown", "black", "curly", None, (255, 210, 40), ())],
    "POR": [("palhinha", "Palhinha", 6, "light", "darkbrown", "short", "full", (30, 30, 36), ()),
            ("bernardo", "Bernardo Silva", 10, "light", "darkbrown", "short", "stubble", (240, 240, 244), ()),
            ("ronaldo", "Cristiano Ronaldo", 7, "tan", "darkbrown", "swept", None, (240, 240, 244), ())],
}


# ---------------------------------------------------------------- head
def make_head(skin, hair, style, facial, extras):
    g = Grid(16, 16, 10)
    s, s_dark, s_light = skin, shade(skin, 0.86), shade(skin, 1.12)
    h, h_light, h_dark = hair, shade(hair, 1.25), shade(hair, 0.75)
    top = 4 if style not in ("bald", "wedge") else 3
    # face block with a shadow side and chin shade
    g.rect(2, top, 13, 15, s)
    g.rect(12, top + 1, 13, 15, s_dark)
    g.rect(3, 15, 11, 15, s_dark)
    g.rect(2, top, 2, 15, s_light)
    # ears
    g.set(1, 9, s_dark); g.set(1, 10, s_dark)
    g.set(14, 9, s_dark); g.set(14, 10, s_dark)

    if style == "bald":
        g.set(4, 3, s_light); g.set(5, 3, s_light)          # shine
    elif style == "wedge":                                # shaved, one little wedge at the front
        g.set(4, 3, s_light)
        g.rect(6, 3, 9, 3, h); g.rect(7, 4, 8, 4, h)
    elif style == "mohawk":                               # shaved sides, strip on top
        g.rect(2, 3, 13, 4, mix(h, s, 0.55))
        g.rect(6, 0, 9, 4, h); g.set(7, 0, h_light); g.set(8, 1, h_light)
    elif style == "buzz":
        g.rect(2, 3, 13, 4, mix(h, s, 0.25))
        g.rect(2, 5, 2, 6, mix(h, s, 0.45)); g.rect(13, 5, 13, 6, mix(h, s, 0.45))
    elif style == "short":
        g.rect(2, 2, 13, 4, h)
        for x in (3, 5, 6, 9, 11):
            g.set(x, 1, h)
        g.rect(2, 5, 4, 5, h); g.set(2, 6, h); g.set(13, 5, h); g.set(13, 6, h)
        for x in (5, 9):
            g.set(x, 2, h_light)
    elif style == "fade":
        g.rect(3, 2, 12, 3, h)
        g.rect(2, 4, 13, 4, h)
        g.rect(2, 5, 2, 7, mix(h, s, 0.5)); g.rect(13, 5, 13, 7, mix(h, s, 0.5))
        g.set(6, 2, h_light); g.set(10, 3, h_light)
    elif style == "swept":
        g.rect(2, 2, 13, 4, h)
        g.rect(6, 1, 12, 1, h); g.rect(9, 0, 12, 0, h)       # quiff
        g.rect(9, 5, 13, 5, h); g.set(2, 5, h); g.set(2, 6, h)
        g.set(10, 1, h_light); g.set(11, 2, h_light)
    elif style == "curly":
        g.rect(1, 2, 14, 4, h)
        for x in range(1, 15, 2):
            g.set(x, 1, h)
        for x in (2, 6, 10):
            g.set(x, 0, h)
        g.rect(1, 5, 3, 6, h); g.rect(12, 5, 14, 6, h)
        for (x, y) in ((3, 2), (7, 1), (11, 3), (5, 4), (13, 2)):
            g.set(x, y, h_light)
    elif style == "twists":
        g.rect(2, 3, 13, 4, h)
        for x in range(2, 14):
            if x % 2 == 0:
                g.rect(x, 0, x, 2, h)
            else:
                g.rect(x, 1, x, 2, h_dark)
        for x in (4, 8, 12):
            g.set(x, 0, h_light)
        g.set(2, 5, h); g.set(13, 5, h)
    elif style == "long":
        g.rect(2, 1, 13, 4, h)
        g.rect(1, 3, 2, 13, h); g.rect(13, 3, 14, 13, h)
        g.rect(1, 12, 2, 13, h_dark); g.rect(13, 12, 14, 13, h_dark)
        g.set(4, 5, h); g.set(5, 5, h); g.set(8, 1, h_light); g.set(10, 2, h_light)
        for y in (9, 10):                                 # hair covers the ears
            g.set(1, y, h); g.set(14, y, h)
    elif style == "bigcurly":
        g.rect(0, 1, 15, 4, h)
        for x in range(1, 15):
            g.set(x, 0, h if x % 3 else h_dark)
        g.rect(0, 5, 2, 9, h); g.rect(13, 5, 15, 9, h)
        g.rect(3, 5, 4, 5, h); g.rect(11, 5, 12, 5, h)
        for (x, y) in ((2, 1), (5, 2), (8, 0), (11, 2), (13, 1), (1, 6), (14, 7), (6, 4), (10, 3)):
            g.set(x, y, h_light)
        for y in (9, 10):                                 # hair covers the ears
            g.set(1, y, h); g.set(14, y, h)
    elif style == "bun":
        g.rect(2, 2, 13, 4, h)
        g.rect(6, 0, 9, 1, h); g.set(7, 0, h_light)
        g.rect(2, 5, 2, 6, h); g.rect(13, 5, 13, 6, h)
        g.set(4, 2, h_light); g.set(11, 3, h_light)

    beard = h if facial in ("full", "short", "goatee", "tache") else mix(h, s, 0.55)
    if facial == "full":
        g.rect(2, 9, 2, 13, beard); g.rect(13, 9, 13, 13, beard)
        g.rect(2, 12, 13, 15, beard)
        g.rect(5, 11, 10, 11, beard)                       # moustache
        g.rect(6, 13, 9, 13, shade(s, 0.7))                # mouth gap
        g.rect(3, 15, 12, 15, shade(beard, 0.8))
    elif facial == "short":
        g.rect(2, 10, 2, 13, beard); g.rect(13, 10, 13, 13, beard)
        g.rect(3, 13, 12, 15, beard)
        g.rect(5, 11, 10, 11, beard)
        g.rect(6, 13, 9, 13, shade(s, 0.75))
    elif facial == "stubble":
        g.rect(3, 13, 12, 15, beard); g.rect(2, 11, 2, 13, beard); g.rect(13, 11, 13, 13, beard)
        g.rect(6, 11, 9, 11, beard)
    elif facial == "goatee":
        g.rect(5, 11, 10, 11, beard)
        g.rect(6, 13, 9, 15, beard)
    elif facial == "tache":
        g.rect(5, 11, 10, 11, beard)
    if "hband" in extras:
        g.rect(2, 4, 13, 4, (240, 240, 244))
    if "earring" in extras:
        g.set(14, 11, (224, 224, 230))
    return g.image()


# ---------------------------------------------------------------- kit pieces
def kit_colour(kit, x, y, w, h):
    base, alt, p = kit["base"], kit["alt"], kit["pattern"]
    if p == "stripes":
        return alt if (x // 2) % 2 == 1 else base
    if p == "checks":
        return alt if ((x // 2) + (y // 2)) % 2 else base
    if p == "weave":
        return alt if (x + y) % 5 == 0 else base
    if p == "lines":
        return alt if (x - y) % 6 == 0 else base
    if p == "fade":
        t = max(0.0, (y - h * 0.55) / (h * 0.45))
        return mix(base, alt, min(1.0, t) * 0.85)
    if p == "dots":
        return alt if (y in (2, 3) and x % 3 == 0) else base
    return base


def make_torso(kit, number):
    g = Grid(16, 16, 8)
    for y in range(16):
        for x in range(16):
            g.set(x, y, kit_colour(kit, x, y, 16, 16))
    # shading: light left edge, shadow right edge, darker hem
    for y in range(16):
        g.set(15, y, shade(g.get(15, y), 0.82))
        g.set(0, y, shade(g.get(0, y), 1.08) if g.get(0, y) != WHITE else g.get(0, y))
    for x in range(16):
        g.set(x, 15, shade(g.get(x, 15), 0.85))
    # collar: V-neck in trim colour with the inside of the shirt showing
    trim = kit["trim"]
    g.rect(4, 0, 11, 0, trim)
    g.rect(5, 1, 10, 1, trim)
    g.rect(6, 0, 9, 0, shade(kit["base"], 0.6))
    g.rect(7, 1, 8, 1, shade(kit["base"], 0.6))
    g.rect(7, 2, 8, 2, trim)
    if "placket" in kit:
        g.rect(7, 2, 8, 4, kit["placket"])
    if "sleeve" in kit:                  # contrasting sleeves (Arsenal, Villa, West Ham)
        g.rect(0, 0, 1, 4, kit["sleeve"]); g.rect(14, 0, 15, 4, shade(kit["sleeve"], 0.88))
        g.set(4, 0, kit["trim"]); g.set(11, 0, kit["trim"])
    # sleeve seams
    g.rect(0, 0, 0, 3, shade(g.get(0, 0), 0.9)); g.rect(15, 0, 15, 3, shade(g.get(15, 0), 0.85))
    # badge: small shield on the chest (viewer's right), stars above
    b1, b2 = kit["badge"]
    bx, by = 10, 4
    edge = shade(b1, 0.6) if b1 != WHITE else NAVY
    g.rect(bx, by, bx + 2, by + 2, b1)
    g.set(bx + 1, by + 1, b2)
    g.set(bx + 1, by + 3, b1)
    g.set(bx - 1, by, edge); g.set(bx + 3, by, edge)
    n = kit["stars"]
    for i in range(n):
        g.set(bx + 1 - (n - 1) // 2 + i, by - 1, GOLD)
    # number on the front
    s = str(number)
    width = len(s) * 3 + (len(s) - 1)
    x0 = (16 - width) // 2
    cells = set()
    for i, ch in enumerate(s):
        for dy, row in enumerate(DIGITS[ch]):
            for dx, bit in enumerate(row):
                if bit == "1":
                    cells.add((x0 + i * 4 + dx, 8 + dy))
    if kit.get("pattern") == "stripes" and "number_outline" in kit:
        # striped club shirts: solid patch behind the number
        g.rect(x0 - 1, 7, x0 + width, 13, kit["number_outline"])
    elif "number_outline" in kit:        # keeps numbers readable on busy patterns
        for (x, y) in cells:
            for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x + ox, y + oy) not in cells:
                    g.set(x + ox, y + oy, kit["number_outline"])
    for (x, y) in cells:
        g.set(x, y, kit["number"])
    return g.image().convert("RGB")


def make_arm(kit, skin):
    g = Grid(6, 16, 8)
    for y in range(0, 6):
        for x in range(6):
            g.set(x, y, kit.get("sleeve") or kit_colour(kit, x, y, 6, 16))
    g.rect(0, 6, 5, 6, kit["trim"])                        # cuff
    g.rect(0, 7, 5, 14, skin)
    g.rect(0, 15, 5, 15, shade(skin, 0.9))                 # hand
    for y in range(16):
        g.set(5, y, shade(g.get(5, y), 0.84))
        if y < 6:
            g.set(0, y, shade(g.get(0, y), 1.06))
    g.set(0, 7, shade(skin, 0.92)); g.set(5, 7, shade(skin, 0.75))
    return g.image().convert("RGB")


def make_leg(kit, skin, boots):
    g = Grid(6, 16, 8)
    g.rect(0, 0, 5, 5, kit["shorts"])
    g.rect(0, 6, 5, 6, kit["shorts_trim"])                 # hem
    g.set(1, 1, kit["shorts_trim"])                        # little logo dot
    g.rect(0, 7, 5, 9, skin)
    g.rect(0, 10, 5, 13, kit["socks"])
    g.rect(0, 11, 5, 11, kit["sock_trim"])                 # sock band
    g.rect(0, 14, 5, 15, boots)
    g.rect(0, 15, 5, 15, shade(boots, 0.6))                # sole
    g.set(4, 14, shade(boots, 1.3) if boots != (240, 240, 244) else (200, 200, 210))
    for y in range(16):
        g.set(5, y, shade(g.get(5, y), 0.84))
    return g.image().convert("RGB")


def main():
    OUT = sys.argv[1] if len(sys.argv) > 1 else "sprites"
    os.makedirs(OUT, exist_ok=True)
    for code, players in TEAMS.items():
        kit = KITS[code]
        for slug, name, num, skin, hair, style, facial, boots, extras in players:
            sk, hr = SKIN[skin], HAIR[hair]
            base = os.path.join(OUT, "%s_%s" % (code, slug))
            make_head(sk, hr, style, facial, extras).save(base + "_head.png")
            make_torso(kit, num).save(base + "_torso.png")
            make_arm(kit, sk).save(base + "_arm.png")
            make_leg(kit, sk, boots).save(base + "_leg.png")
    print("wrote", len(os.listdir(OUT)), "files to", OUT)





# ================================================================ CLUB FOOTBALL
RED = (218, 30, 32)
BLACK = (22, 22, 26)
CLARET = (122, 36, 58)
SKY = (140, 190, 232)

CLUB_KITS = {
    "ARS": dict(base=(219, 12, 24), alt=(219, 12, 24), sleeve=WHITE, pattern="plain", trim=WHITE, number=WHITE,
                shorts=WHITE, shorts_trim=(219, 12, 24), socks=WHITE, sock_trim=(219, 12, 24),
                badge=((219, 12, 24), GOLD), stars=0),
    "AST": dict(base=CLARET, alt=CLARET, sleeve=SKY, pattern="plain", trim=SKY, number=SKY,
                shorts=WHITE, shorts_trim=CLARET, socks=SKY, sock_trim=CLARET, badge=(CLARET, SKY), stars=0),
    "BOU": dict(base=(214, 34, 26), alt=BLACK, pattern="stripes", trim=BLACK, number=WHITE, number_outline=BLACK,
                shorts=BLACK, shorts_trim=(214, 34, 26), socks=BLACK, sock_trim=(214, 34, 26),
                badge=((214, 34, 26), BLACK), stars=0),
    "BRE": dict(base=(226, 12, 24), alt=WHITE, pattern="stripes", trim=BLACK, number=BLACK, number_outline=WHITE,
                shorts=BLACK, shorts_trim=(226, 12, 24), socks=(226, 12, 24), sock_trim=WHITE,
                badge=((226, 12, 24), WHITE), stars=0),
    "BRI": dict(base=(0, 88, 184), alt=WHITE, pattern="stripes", trim=(0, 88, 184), number=NAVY, number_outline=WHITE,
                shorts=(0, 88, 184), shorts_trim=WHITE, socks=(0, 88, 184), sock_trim=WHITE,
                badge=((0, 88, 184), WHITE), stars=0),
    "CHE": dict(base=(6, 72, 150), alt=(6, 72, 150), pattern="plain", trim=WHITE, number=WHITE,
                shorts=(6, 72, 150), shorts_trim=WHITE, socks=WHITE, sock_trim=(6, 72, 150),
                badge=((6, 72, 150), GOLD), stars=0),
    "CRY": dict(base=(196, 20, 48), alt=(28, 70, 146), pattern="stripes", trim=(28, 70, 146), number=WHITE,
                number_outline=NAVY, shorts=(28, 70, 146), shorts_trim=(196, 20, 48), socks=(28, 70, 146),
                sock_trim=(196, 20, 48), badge=((28, 70, 146), (196, 20, 48)), stars=0),
    "EVE": dict(base=(40, 70, 140), alt=(40, 70, 140), pattern="plain", trim=WHITE, number=WHITE,
                shorts=WHITE, shorts_trim=(40, 70, 140), socks=WHITE, sock_trim=(40, 70, 140),
                badge=((40, 70, 140), WHITE), stars=0),
    "FUL": dict(base=WHITE, alt=(234, 234, 238), pattern="plain", trim=BLACK, number=BLACK,
                shorts=BLACK, shorts_trim=WHITE, socks=WHITE, sock_trim=BLACK, badge=(WHITE, BLACK), stars=0),
    "LIV": dict(base=(200, 16, 46), alt=(200, 16, 46), pattern="plain", trim=WHITE, number=WHITE,
                shorts=(200, 16, 46), shorts_trim=WHITE, socks=(200, 16, 46), sock_trim=WHITE,
                badge=((200, 16, 46), GOLD), stars=0),
    "MCI": dict(base=(108, 172, 222), alt=(108, 172, 222), pattern="plain", trim=(28, 44, 92), number=(28, 44, 92),
                shorts=WHITE, shorts_trim=(108, 172, 222), socks=(108, 172, 222), sock_trim=(28, 44, 92),
                badge=((108, 172, 222), (28, 44, 92)), stars=0),
    "MUN": dict(base=(218, 34, 28), alt=(218, 34, 28), pattern="plain", trim=BLACK, number=WHITE,
                shorts=WHITE, shorts_trim=(218, 34, 28), socks=BLACK, sock_trim=(218, 34, 28),
                badge=((218, 34, 28), GOLD), stars=0),
    "NEW": dict(base=BLACK, alt=WHITE, pattern="stripes", trim=BLACK, number=BLACK, number_outline=WHITE,
                shorts=BLACK, shorts_trim=WHITE, socks=BLACK, sock_trim=WHITE, badge=(BLACK, WHITE), stars=0),
    "NOT": dict(base=(221, 8, 8), alt=(221, 8, 8), pattern="plain", trim=WHITE, number=WHITE,
                shorts=WHITE, shorts_trim=(221, 8, 8), socks=(221, 8, 8), sock_trim=WHITE,
                badge=((221, 8, 8), WHITE), stars=0),
    "TOT": dict(base=WHITE, alt=(234, 234, 238), pattern="plain", trim=(20, 34, 88), number=(20, 34, 88),
                shorts=(20, 34, 88), shorts_trim=WHITE, socks=WHITE, sock_trim=(20, 34, 88),
                badge=((20, 34, 88), WHITE), stars=0),
    "WES": dict(base=CLARET, alt=CLARET, sleeve=(30, 176, 230), pattern="plain", trim=(30, 176, 230), number=WHITE,
                shorts=WHITE, shorts_trim=CLARET, socks=WHITE, sock_trim=CLARET,
                badge=(CLARET, (30, 176, 230)), stars=0),
    "WOL": dict(base=(252, 184, 20), alt=(252, 184, 20), pattern="plain", trim=BLACK, number=BLACK,
                shorts=BLACK, shorts_trim=(252, 184, 20), socks=(252, 184, 20), sock_trim=BLACK,
                badge=((252, 184, 20), BLACK), stars=0),
    "SUN": dict(base=(234, 24, 44), alt=WHITE, pattern="stripes", trim=BLACK, number=BLACK, number_outline=WHITE,
                shorts=BLACK, shorts_trim=(234, 24, 44), socks=(234, 24, 44), sock_trim=WHITE,
                badge=((234, 24, 44), WHITE), stars=0),
    "INT": dict(base=(245, 180, 204), alt=(245, 180, 204), pattern="plain", trim=BLACK, number=BLACK,
                shorts=(245, 180, 204), shorts_trim=BLACK, socks=(245, 180, 204), sock_trim=BLACK,
                badge=((245, 180, 204), BLACK), stars=0),
    "ALN": dict(base=(255, 218, 0), alt=(255, 218, 0), pattern="plain", trim=(0, 56, 142), number=(0, 56, 142),
                shorts=(0, 56, 142), shorts_trim=(255, 218, 0), socks=(255, 218, 0), sock_trim=(0, 56, 142),
                badge=((255, 218, 0), (0, 56, 142)), stars=0),
    "BAR": dict(base=(0, 78, 152), alt=(166, 0, 68), pattern="stripes", trim=GOLD, number=GOLD,
                number_outline=(12, 30, 80), shorts=(12, 30, 80), shorts_trim=(166, 0, 68),
                socks=(12, 30, 80), sock_trim=(166, 0, 68), badge=((166, 0, 68), (0, 78, 152)), stars=0),
}

K, W, G = (30, 30, 36), (240, 240, 244), (255, 210, 40)      # boot colours
P = (255, 112, 182)
# 5 players per club: Bad, Bad, Alright, Alright, Good
# (slug, name, number, skin, hair, style, facial, boots, extras)
CLUB_TEAMS = {
    "ARS": [("kepa", "Kepa", 13, "light", "darkbrown", "short", "stubble", K, ()),
            ("trossard", "Trossard", 19, "light", "brown", "short", "stubble", W, ()),
            ("odegaard", "Odegaard", 8, "pale", "lightbrown", "swept", None, W, ()),
            ("saka", "Saka", 7, "dark", "black", "fade", None, G, ()),
            ("gyokeres", "Gyokeres", 14, "pale", "lightbrown", "short", "stubble", G, ())],
    "AST": [("cash", "Cash", 2, "pale", "lightbrown", "short", "stubble", K, ()),
            ("digne", "Digne", 12, "light", "darkbrown", "short", "full", K, ()),
            ("rogers", "Rogers", 27, "brown", "black", "fade", None, W, ()),
            ("watkins", "Watkins", 11, "brown", "black", "buzz", "short", W, ()),
            ("martinez", "Martinez", 23, "light", "darkbrown", "short", "stubble", G, ())],
    "BOU": [("christie", "Christie", 10, "light", "brown", "buzz", "stubble", K, ()),
            ("kerkez", "Kerkez", 3, "pale", "darkbrown", "swept", None, K, ()),
            ("evanilson", "Evanilson", 9, "brown", "black", "fade", "stubble", W, ()),
            ("kluivert", "Kluivert", 19, "brown", "black", "twists", None, G, ()),
            ("tavernier", "Tavernier", 16, "pale", "darkbrown", "short", "stubble", W, ())],
    "BRE": [("janelt", "Janelt", 27, "pale", "blond", "short", None, K, ()),
            ("potter", "Lewis Potter", 23, "pale", "lightbrown", "short", None, K, ()),
            ("schade", "Schade", 7, "light", "darkbrown", "short", "stubble", W, ()),
            ("mbeumo", "Mbeumo", 19, "dark", "black", "fade", "short", W, ()),
            ("wissa", "Wissa", 11, "dark", "black", "buzz", "goatee", G, ())],
    "BRI": [("lamptey", "Lamptey", 2, "dark", "black", "fade", None, K, ()),
            ("igor", "Igor", 3, "brown", "black", "buzz", "stubble", K, ()),
            ("rutter", "Rutter", 14, "brown", "black", "fade", None, W, ()),
            ("mitoma", "Mitoma", 22, "light", "black", "short", None, W, ()),
            ("welbeck", "Welbeck", 18, "dark", "black", "buzz", "short", W, ())],
    "CHE": [("disasi", "Disasi", 2, "dark", "black", "buzz", "stubble", K, ()),
            ("cucurella", "Cucurella", 3, "light", "darkbrown", "bigcurly", None, K, ()),
            ("enzo", "Enzo", 8, "light", "darkbrown", "buzz", "stubble", W, ()),
            ("palmer", "Palmer", 10, "pale", "lightbrown", "fade", None, W, ()),
            ("caicedo", "Caicedo", 25, "brown", "black", "short", None, G, ()),
            ("joaopedro", "Joao Pedro", 20, "brown", "black", "curly", None, G, ())],
    "CRY": [("ward", "Ward", 2, "pale", "darkbrown", "short", "stubble", K, ()),
            ("lerma", "Lerma", 8, "dark", "black", "short", "stubble", K, ()),
            ("mateta", "Mateta", 14, "dark", "black", "bald", None, W, ()),
            ("eze", "Eze", 10, "dark", "black", "buzz", "stubble", W, ()),
            ("sarr", "Sarr", 7, "dark", "black", "buzz", None, W, ())],
    "EVE": [("young", "Young", 18, "dark", "black", "bald", "goatee", K, ()),
            ("tarkowski", "Tarkowski", 6, "pale", "darkbrown", "short", "full", K, ()),
            ("pickford", "Pickford", 1, "pale", "lightbrown", "short", "stubble", W, ()),
            ("ndiaye", "Ndiaye", 10, "dark", "black", "buzz", None, W, ()),
            ("beto", "Beto", 9, "deep", "black", "curly", None, G, ())],
    "FUL": [("reed", "Reed", 6, "pale", "lightbrown", "short", "stubble", K, ()),
            ("robinson", "Robinson", 33, "brown", "black", "buzz", "short", K, ()),
            ("iwobi", "Iwobi", 17, "dark", "black", "buzz", "stubble", W, ()),
            ("pereira", "Pereira", 18, "light", "darkbrown", "short", "stubble", W, ()),
            ("jimenez", "Jimenez", 7, "tan", "black", "bun", "full", G, ())],
    "LIV": [("gomez", "Gomez", 2, "dark", "black", "buzz", "full", K, ()),
            ("tsimikas", "Tsimikas", 21, "light", "darkbrown", "short", "full", K, ()),
            ("macallister", "Mac Allister", 10, "light", "ginger", "short", "stubble", W, ()),
            ("szoboszlai", "Szoboszlai", 8, "pale", "blond", "swept", None, W, ()),
            ("salah", "Salah", 11, "brown", "black", "bigcurly", "full", G, ())],
    "MCI": [("ake", "Ake", 6, "dark", "black", "buzz", "short", K, ()),
            ("akanji", "Akanji", 25, "tan", "black", "buzz", "stubble", K, ()),
            ("foden", "Foden", 47, "pale", "lightbrown", "buzz", None, W, ()),
            ("rodri", "Rodri", 16, "light", "darkbrown", "short", "stubble", W, ()),
            ("haaland", "Haaland", 9, "pale", "blond", "bun", None, G, ()),
            # 28 Oct: Champion Draft A - Guehi and Semenyo play for City now
            ("guehi", "Guehi", 15, "dark", "black", "buzz", None, G, ()),
            ("semenyo", "Semenyo", 42, "dark", "black", "buzz", None, W, ())],
    "MUN": [("lindelof", "Lindelof", 2, "pale", "blond", "short", "stubble", K, ()),
            ("malacia", "Malacia", 12, "brown", "black", "buzz", "short", K, ()),
            ("garnacho", "Garnacho", 17, "light", "darkbrown", "curly", None, W, ()),
            ("bruno", "Bruno", 8, "light", "darkbrown", "short", "stubble", W, ()),
            ("mainoo", "Mainoo", 37, "dark", "black", "fade", None, G, ())],
    "NEW": [("burn", "Burn", 33, "pale", "lightbrown", "short", "stubble", K, ()),
            ("targett", "Targett", 13, "pale", "brown", "short", "stubble", K, ()),
            ("gordon", "Gordon", 10, "pale", "lightbrown", "short", None, W, ()),
            ("brunog", "Bruno G", 39, "olive", "darkbrown", "fade", "stubble", W, ()),
            ("isak", "Isak", 14, "brown", "black", "short", "stubble", G, ())],
    "NOT": [("yates", "Yates", 22, "pale", "brown", "short", "full", K, ()),
            ("toffolo", "Toffolo", 15, "pale", "darkbrown", "short", "stubble", K, ()),
            ("elanga", "Elanga", 21, "dark", "black", "fade", None, W, ()),
            ("gibbswhite", "Gibbs-White", 10, "pale", "lightbrown", "swept", None, W, ()),
            ("hudsonodoi", "Hudson-Odoi", 14, "brown", "black", "buzz", "stubble", G, ())],
    "TOT": [("davies", "Davies", 33, "pale", "lightbrown", "short", "full", K, ()),
            ("dragusin", "Dragusin", 6, "pale", "darkbrown", "short", "stubble", K, ()),
            ("maddison", "Maddison", 10, "pale", "darkbrown", "short", "stubble", W, ()),
            ("romero", "Romero", 17, "tan", "darkbrown", "short", "stubble", W, ()),
            ("son", "Son", 7, "light", "black", "swept", None, G, ())],
    "WES": [("coufal", "Coufal", 5, "pale", "darkbrown", "short", "stubble", K, ()),
            ("cresswell", "Cresswell", 3, "pale", "lightbrown", "short", "stubble", K, ()),
            ("bowen", "Bowen", 20, "pale", "darkbrown", "short", "stubble", W, ()),
            ("paqueta", "Paqueta", 10, "tan", "darkbrown", "curly", "stubble", W, ()),
            ("kudus", "Kudus", 14, "dark", "black", "buzz", None, G, ())],
    "WOL": [("doherty", "Doherty", 2, "pale", "lightbrown", "short", "full", K, ()),
            ("lemina", "Lemina", 5, "dark", "black", "buzz", "stubble", K, ()),
            ("cunha", "Cunha", 10, "tan", "black", "curly", None, W, ()),
            ("aitnouri", "Ait-Nouri", 3, "tan", "black", "bigcurly", None, W, ()),
            ("sarabia", "Sarabia", 21, "light", "darkbrown", "short", "stubble", G, ())],
    "SUN": [("onien", "O'Nien", 13, "pale", "brown", "short", "stubble", K, ()),
            ("ballard", "Ballard", 5, "pale", "lightbrown", "short", None, K, ()),
            ("clarke", "Clarke", 20, "pale", "lightbrown", "short", None, W, ()),
            ("lefee", "Le Fee", 28, "light", "darkbrown", "short", None, W, ()),
            ("bellingham", "Bellingham", 7, "brown", "black", "fade", None, G, ())],
    "INT": [("aviles", "Aviles", 17, "light", "darkbrown", "short", None, K, ()),
            ("redondo", "Redondo", 55, "light", "darkbrown", "swept", None, K, ()),
            ("suarez", "Suarez", 9, "light", "darkbrown", "short", "stubble", W, ()),
            ("depaul", "De Paul", 7, "light", "darkbrown", "swept", "full", W, ()),
            ("messi", "Messi", 10, "light", "brown", "short", "full", P, ())],
    "ALN": [("alghannam", "Al Ghannam", 2, "tan", "black", "short", "full", K, ()),
            ("alkhaibari", "Al Khaibari", 17, "brown", "black", "short", "full", K, ()),
            ("mane", "Mane", 10, "deep", "black", "buzz", "short", W, ()),
            ("joaofelix", "Joao Felix", 79, "light", "darkbrown", "swept", None, W, ()),
            ("ronaldo", "Ronaldo", 7, "tan", "darkbrown", "swept", None, W, ())],
    "BAR": [("ferran", "Ferran Torres", 7, "light", "darkbrown", "short", "stubble", K, ()),
            ("fermin", "Fermin Lopez", 16, "light", "darkbrown", "curly", "stubble", K, ()),
            ("pedri", "Pedri", 8, "light", "darkbrown", "swept", None, W, ()),
            ("raphinha", "Raphinha", 11, "tan", "black", "fade", "stubble", W, ()),
            ("yamal", "Lamine Yamal", 10, "brown", "black", "curly", None, G, ())],
}

# 3x5 letters for the badge codes
LETTERS = {
    "A": ["010", "101", "111", "101", "101"], "B": ["110", "101", "110", "101", "110"],
    "C": ["011", "100", "100", "100", "011"], "D": ["110", "101", "101", "101", "110"],
    "E": ["111", "100", "110", "100", "111"], "G": ["011", "100", "101", "101", "011"],
    "J": ["001", "001", "001", "101", "010"], "K": ["101", "101", "110", "101", "101"],
    "P": ["110", "101", "110", "100", "100"],
    "F": ["111", "100", "110", "100", "100"], "H": ["101", "101", "111", "101", "101"],
    "I": ["111", "010", "010", "010", "111"], "L": ["100", "100", "100", "100", "111"],
    "M": ["101", "111", "111", "101", "101"], "N": ["110", "101", "101", "101", "101"],
    "O": ["010", "101", "101", "101", "010"], "R": ["110", "101", "110", "101", "101"],
    "S": ["011", "100", "010", "001", "110"], "T": ["111", "010", "010", "010", "010"],
    "U": ["101", "101", "101", "101", "111"], "V": ["101", "101", "101", "101", "010"],
    "W": ["101", "101", "111", "111", "101"], "Y": ["101", "101", "010", "010", "010"],
}


def make_badge(code, kit):
    """Club badge: a shield in the club's colours with the 3-letter code."""
    g = Grid(20, 24, 6)
    c1, c2 = kit["badge"]
    edge = c2 if c2 != c1 else BLACK
    # shield outline + fill
    for y in range(24):
        if y < 16:
            x0, x1 = 1, 18
        else:
            k = y - 15
            x0, x1 = 1 + k, 18 - k
        if x0 > x1:
            continue
        g.rect(x0, y, x1, y, edge)
        if y > 0 and y < 23 and x1 - x0 >= 2:
            g.rect(x0 + 1, y, x1 - 1, y, c1)
    # top band in the second colour
    g.rect(2, 1, 17, 5, c2 if c2 != c1 else shade(c1, 0.7))
    g.rect(2, 5, 17, 5, edge)
    # code letters
    ink = WHITE if sum(c1) < 360 else BLACK
    if ink == c1 or ink == edge:
        ink = c2
    for i, ch in enumerate(code):
        for dy, row in enumerate(LETTERS[ch]):
            for dx, bit in enumerate(row):
                if bit == "1":
                    g.set(4 + i * 4 + dx, 9 + dy, ink)
    # little shine
    g.set(3, 7, shade(c1, 1.3)); g.set(3, 8, shade(c1, 1.2))
    return g.image()


# ================================================================ STAR SIGNINGS
# Kits for the Star Signing clubs that aren't in the league (plain colour kits, no real crests).
MADRID_NAVY = (34, 44, 110)
STAR_KITS = {
    "SAN": dict(base=WHITE, alt=WHITE, pattern="plain", trim=BLACK, number=BLACK,
                shorts=WHITE, shorts_trim=BLACK, socks=WHITE, sock_trim=BLACK, badge=(WHITE, BLACK), stars=0),
    "RMA": dict(base=WHITE, alt=(238, 238, 242), pattern="plain", trim=GOLD, number=MADRID_NAVY,
                shorts=WHITE, shorts_trim=GOLD, socks=WHITE, sock_trim=MADRID_NAVY,
                badge=(WHITE, GOLD), stars=0),
    "NAP": dict(base=(18, 142, 222), alt=(18, 142, 222), pattern="plain", trim=WHITE, number=WHITE,
                shorts=WHITE, shorts_trim=(18, 142, 222), socks=(18, 142, 222), sock_trim=WHITE,
                badge=((18, 142, 222), WHITE), stars=0),
    "MIL": dict(base=(206, 18, 36), alt=BLACK, pattern="stripes", trim=BLACK, number=WHITE, number_outline=BLACK,
                shorts=WHITE, shorts_trim=(206, 18, 36), socks=BLACK, sock_trim=(206, 18, 36),
                badge=((206, 18, 36), BLACK), stars=0),
    "BEN": dict(base=(226, 22, 38), alt=(226, 22, 38), pattern="plain", trim=WHITE, number=WHITE,
                shorts=WHITE, shorts_trim=(226, 22, 38), socks=(226, 22, 38), sock_trim=WHITE,
                badge=((226, 22, 38), GOLD), stars=0),
    "BAY": dict(base=(220, 10, 46), alt=(220, 10, 46), pattern="plain", trim=WHITE, number=WHITE,
                shorts=WHITE, shorts_trim=(220, 10, 46), socks=(220, 10, 46), sock_trim=WHITE,
                badge=((0, 92, 172), (220, 10, 46)), stars=0),
    "DYN": dict(base=(20, 62, 160), alt=(20, 62, 160), pattern="plain", trim=WHITE, number=WHITE,
                shorts=WHITE, shorts_trim=(20, 62, 160), socks=(20, 62, 160), sock_trim=WHITE,
                badge=((20, 62, 160), WHITE), stars=0),
    "JUV": dict(base=WHITE, alt=BLACK, pattern="stripes", trim=BLACK, number=BLACK, number_outline=WHITE,
                shorts=WHITE, shorts_trim=BLACK, socks=WHITE, sock_trim=BLACK, badge=(BLACK, WHITE), stars=0),
}
# goalkeepers wear keeper shirts
STAR_GK_KITS = {
    "yashin": dict(base=(26, 26, 30), alt=(26, 26, 30), pattern="plain", trim=WHITE, number=WHITE,
                   shorts=(26, 26, 30), shorts_trim=WHITE, socks=(26, 26, 30), sock_trim=WHITE,
                   badge=((20, 62, 160), WHITE), stars=0),
    "neuer": dict(base=(36, 168, 122), alt=(36, 168, 122), pattern="plain", trim=(18, 44, 40), number=(18, 44, 40),
                  shorts=(36, 168, 122), shorts_trim=(18, 44, 40), socks=(36, 168, 122), sock_trim=(18, 44, 40),
                  badge=((0, 92, 172), (220, 10, 46)), stars=0),
    "buffon": dict(base=(56, 60, 72), alt=(56, 60, 72), pattern="plain", trim=GOLD, number=GOLD,
                   shorts=(56, 60, 72), shorts_trim=GOLD, socks=(56, 60, 72), sock_trim=GOLD,
                   badge=(BLACK, WHITE), stars=0),
}
# slug: skin, hair, portrait style, beard, extras (make_art.py draws the card portrait from this)
STAR_LOOKS = {
    "neto": ("tan", "black", "short", None, ()),          # Pedro Neto (admin-only Chelsea card)
    "pele": ("deep", "black", "buzz", None, ()),
    "r9": ("tan", "black", "wedge", None, ()),
    "maradona": ("tan", "black", "curly", None, ()),
    "zidane": ("light", "darkbrown", "bald", "stubble", ()),
    "ronaldinho": ("brown", "black", "long", None, ("hband", "grin")),
    "mbappe": ("brown", "black", "buzz", None, ()),
    "neymar": ("tan", "darkbrown", "mohawk", None, ()),
    "cruyff": ("pale", "brown", "shaggy", None, ("nogrin",)),
    "gullit": ("dark", "black", "dreads", "tache", ()),
    "hazard": ("light", "darkbrown", "short", "stubble", ()),
    "iniesta": ("pale", "lightbrown", "bald", None, ()),
    "xavi": ("light", "darkbrown", "neat", "stubble", ()),
    "kaka": ("light", "darkbrown", "short", None, ()),
    "henry": ("dark", "black", "bald", None, ()),
    "vanbasten": ("pale", "lightbrown", "shaggy", None, ("nogrin",)),
    "eusebio": ("dark", "black", "short", None, ()),
    "maldini": ("olive", "darkbrown", "long", None, ()),
    "beckenbauer": ("pale", "brown", "swept", None, ()),
    "ramos": ("tan", "darkbrown", "quiff", "short", ()),
    "vandijk": ("brown", "black", "fade", "full", ()),
    "cafu": ("dark", "black", "bald", None, ("grin",)),
    "rcarlos": ("brown", "black", "bald", None, ()),
    "yashin": ("pale", "darkbrown", "neat", None, ()),
    "neuer": ("pale", "blond", "short", None, ()),
    "buffon": ("light", "darkbrown", "short", "stubble", ()),
    "modric": ("pale", "lightbrown", "long", None, ()),
    "debruyne": ("pale", "ginger", "short", None, ()),
    "salah": ("brown", "black", "afro", "full", ()),
    "vinicius": ("dark", "black", "twists", None, ()),
    "haaland": ("pale", "blond", "bun", None, ()),
    "bellingham": ("brown", "black", "buzz", None, ()),
    "rodri": ("light", "darkbrown", "neat", "stubble", ()),
    "saka": ("dark", "black", "fade", None, ()),
    "musiala": ("brown", "black", "curly", None, ()),
    "pedri": ("light", "darkbrown", "swept", None, ()),
    "wirtz": ("pale", "brown", "short", None, ()),
    "yamal": ("brown", "black", "curlytop", None, ("nohb",)),
    "kane": ("pale", "lightbrown", "short", None, ()),
    "suarez": ("light", "darkbrown", "shaggy", "stubble", ()),
    "pirlo": ("light", "darkbrown", "long", "full", ()),
}
# the No. 10 pack (playmakers) - portraits in national kits
NO10_LOOKS = {
    "bellingham": ("brown", "black", "buzz", None, ()),
    "wirtz": ("pale", "brown", "short", None, ()),
    "bruno": ("light", "darkbrown", "short", "stubble", ()),
    "olmo": ("light", "darkbrown", "swept", None, ()),
    "eze": ("dark", "black", "twists", "short", ()),
    "guler": ("light", "black", "curly", None, ()),
    "stanciu": ("light", "darkbrown", "short", "stubble", ()),
    "ihagi": ("light", "darkbrown", "short", None, ()),
    "olaru": ("light", "darkbrown", "short", "stubble", ()),
    "macallister": ("light", "darkbrown", "swept", "stubble", ()),
    "mount": ("pale", "lightbrown", "short", "stubble", ()),
    "eriksen": ("pale", "lightbrown", "short", None, ()),
    "ziyech": ("light", "black", "fade", "short", ()),
    "wardprowse": ("pale", "lightbrown", "short", None, ()),
    "oscar": ("brown", "black", "short", None, ()),
    "locelso": ("light", "darkbrown", "short", "stubble", ()),
    "forsberg": ("pale", "blond", "short", "stubble", ()),
}
# the tutorial's beginner cards
ROOKIE_LOOKS = {"palmer": ("pale", "lightbrown", "fade", None, ()),
                "bellingham": STAR_LOOKS["bellingham"],
                "vandijk": STAR_LOOKS["vandijk"]}
# portrait style -> in-match head style
HEAD_STYLE = {"bald": "bald", "buzz": "buzz", "wedge": "wedge", "curly": "curly", "curlytop": "curly",
              "long": "long", "mohawk": "mohawk", "shaggy": "long", "dreads": "long", "short": "short",
              "neat": "short", "swept": "swept", "quiff": "swept", "fade": "fade", "afro": "bigcurly",
              "twists": "twists", "bun": "bun"}
STAR_BOOTS = (K, W, G, P, (40, 120, 230), (250, 120, 30))


def star_kit(slug, club):
    return STAR_GK_KITS.get(slug) or STAR_KITS.get(club) or CLUB_KITS.get(club) or KITS.get(club)


def main_stars(out, stars, prefix="STAR", looks=None):
    """stars: [(slug, club, number)] -> <prefix>_<slug>_<piece>.png, plus the new club badges."""
    looks = looks or STAR_LOOKS
    for code, kit in STAR_KITS.items():
        make_badge(code, kit).save(os.path.join(out, "%s_badge.png" % code))
    for slug, club, num in stars:
        skin, hair, style, beard, extras = looks[slug]
        sk = SKIN[skin]
        hr = HAIR.get(hair, (196, 158, 92))
        kit = star_kit(slug, club)
        boots = STAR_BOOTS[sum(map(ord, slug)) % len(STAR_BOOTS)]
        base = os.path.join(out, "%s_%s" % (prefix, slug))
        make_head(sk, hr, HEAD_STYLE.get(style, "short"), beard,
                  extras).save(base + "_head.png")
        make_torso(kit, num).save(base + "_torso.png")
        make_arm(kit, sk).save(base + "_arm.png")
        make_leg(kit, sk, boots).save(base + "_leg.png")


# ================================================================ PRACTICE ROBOTS
ROBOT_LIGHTS = {"easy": (90, 230, 120), "medium": (255, 210, 60), "hard": (250, 70, 70), "dummy": (70, 74, 86)}
STEEL, STEEL_D, STEEL_L, JOINT = (168, 176, 190), (112, 120, 136), (214, 222, 232), (52, 56, 66)


def make_robot_head(light):
    g = Grid(16, 16, 10)
    g.rect(2, 4, 13, 15, STEEL)                              # rounded metal box
    g.rect(12, 5, 13, 15, STEEL_D)
    g.rect(2, 4, 2, 15, STEEL_L)
    g.rect(3, 3, 12, 3, STEEL)
    g.set(2, 4, None); g.set(13, 4, None)
    g.rect(3, 15, 12, 15, STEEL_D)
    g.rect(7, 0, 8, 2, JOINT)                                # antenna
    g.rect(7, 0, 8, 0, light if light != ROBOT_LIGHTS["dummy"] else STEEL_L)
    g.rect(3, 7, 12, 10, (26, 30, 38))                       # visor
    g.rect(4, 8, 6, 9, light); g.rect(9, 8, 11, 9, light)   # eyes
    g.set(4, 8, shade(light, 1.3)); g.set(9, 8, shade(light, 1.3))
    for x in range(5, 11, 2):                                # mouth grille
        g.rect(x, 12, x, 13, JOINT)
    g.rect(1, 8, 1, 10, JOINT); g.rect(14, 8, 14, 10, JOINT)  # ear bolts
    return g.image()


def make_robot_torso(light):
    g = Grid(16, 16, 8)
    g.rect(0, 0, 15, 15, STEEL)
    g.rect(14, 0, 15, 15, STEEL_D)
    g.rect(0, 0, 0, 15, STEEL_L)
    g.rect(0, 15, 15, 15, STEEL_D)
    g.rect(4, 3, 11, 10, STEEL_D)                            # chest plate
    g.rect(5, 4, 10, 9, (30, 34, 44))
    g.rect(6, 5, 9, 8, light)                                # power core
    g.rect(7, 6, 8, 7, shade(light, 1.35))
    for (x, y) in ((1, 1), (14, 1), (1, 13), (14, 13), (7, 12), (8, 12)):
        g.set(x, y, JOINT)                                   # rivets
    g.rect(2, 13, 13, 13, JOINT)                             # belt seam
    return g.image().convert("RGB")


def make_robot_arm(light):
    g = Grid(6, 16, 8)
    g.rect(0, 0, 5, 15, STEEL)
    g.rect(5, 0, 5, 15, STEEL_D)
    g.rect(0, 0, 0, 15, STEEL_L)
    g.rect(0, 5, 5, 6, JOINT)                                # elbow
    g.set(2, 5, light)
    g.rect(0, 13, 5, 15, JOINT)                              # clamp hand
    g.rect(1, 14, 4, 14, STEEL_D)
    return g.image().convert("RGB")


def make_robot_leg(light):
    g = Grid(6, 16, 8)
    g.rect(0, 0, 5, 15, STEEL)
    g.rect(5, 0, 5, 15, STEEL_D)
    g.rect(0, 0, 0, 12, STEEL_L)
    g.rect(0, 6, 5, 7, JOINT)                                # knee
    g.set(3, 6, light)
    g.rect(0, 13, 5, 15, (40, 44, 54))                       # heavy feet
    g.rect(0, 15, 5, 15, (24, 26, 32))
    return g.image().convert("RGB")


def main_robots(out):
    for tier, light in ROBOT_LIGHTS.items():
        base = os.path.join(out, "ROBOT_%s" % tier)
        make_robot_head(light).save(base + "_head.png")
        make_robot_torso(light).save(base + "_torso.png")
        make_robot_arm(light).save(base + "_arm.png")
        make_robot_leg(light).save(base + "_leg.png")


def main_clubs(out):
    for code, players in CLUB_TEAMS.items():
        kit = CLUB_KITS[code]
        make_badge(code, kit).save(os.path.join(out, "%s_badge.png" % code))
        for slug, name, num, skin, hair, style, facial, boots, extras in players:
            sk, hr = SKIN[skin], HAIR[hair]
            base = os.path.join(out, "%s_%s" % (code, slug))
            make_head(sk, hr, style, facial, extras).save(base + "_head.png")
            make_torso(kit, num).save(base + "_torso.png")
            make_arm(kit, sk).save(base + "_arm.png")
            make_leg(kit, sk, boots).save(base + "_leg.png")


if __name__ == "__main__":
    main()                                           # World Cup teams
    main_clubs(sys.argv[1] if len(sys.argv) > 1 else "sprites")   # clubs
    main_robots(sys.argv[1] if len(sys.argv) > 1 else "sprites")  # practice robots
    print("clubs done")
