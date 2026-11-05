"""MARIO KEMPES (1 Nov) - the second Game Box's Signature card: everything he needs that isn't the card
figure (cards_sig.py draws that, through make_card_figures.py).

    python3 make_kempes.py [sprites_dir]

  sig_kempes.png, sig_kempes_px.png   his autograph, drawn with make_signature.py's pen (smooth + pixel)
  box_kempes.png                      his Game Box: Argentina's sky blue and white, a gold sun, a 10
  SIG_kempes_<head|torso|arm|leg>.png  him in a match (make_sprites.py's legends, in the 1978 stripes)
  event_bg_kempes.png                 his Game Box's backdrop: Argentina's flag, dimmed

The autograph is hand-placed pen paths like Neymar Jr's, in the shape of his own signature (2 Nov): the long
K stem, the name climbing up his chest, the 10, the two rising strokes underneath. Drawn with this game's pen
in a fat gold marker, not traced.
"""
import math
import os
import sys

import numpy as np
from PIL import Image

import make_signature as ms
import make_sprites

CUSP = ms.CUSP
# 2 Nov, second go (Hubi: "it doesn't look like Kempes's signature"). His signature, in its shape, drawn with
# this game's own pen - not traced: a K whose stem drops straight down past everything, its arm coming in from
# the top right and looping round the left; "empes" in upright letters on a baseline that climbs up his chest,
# the s finishing in a tall loop; a 10 under the end; two long strokes underneath, rising to the right.
# Written in place (TILT and SLANT off): the letters are written flat, then climb() stretches them out and
# steps each one up the slope, so the loops stay upright instead of leaning over.
CLIMB = math.tan(math.radians(24))
def climb(pts, x0=180, y0=240, sx=1.6, sy=1.3, lean=0.0):
    """letters written flat (baseline 250) -> stretched out and stepped up the slope, loops kept upright"""
    out = []
    for p in pts:
        if p == CUSP: out.append(p); continue
        x = x0 + (p[0] - 180) * sx + (250 - p[1]) * lean
        out.append((x, (p[1] - 250) * sy + y0 - (x - x0) * CLIMB))
    return out
WORD = [(184, 240), (198, 232), (204, 222), (198, 214), (188, 216), (182, 232), (188, 248), (204, 252), (216, 242),
        # m
        (222, 216), CUSP, (222, 250), CUSP, (227, 226), (237, 214), (245, 224), (247, 250), CUSP,
        (251, 226), (261, 214), (269, 224), (271, 246), (278, 250),
        # p: down through a long tail, back up into its bowl
        (286, 216), CUSP, (284, 260), (280, 300), CUSP, (284, 240), (292, 220), (304, 213), (314, 222), (311, 242),
        (298, 251), (287, 246), CUSP, (304, 250), (320, 244),
        # e
        (332, 232), (336, 220), (328, 213), (317, 224), (319, 244), (333, 252), (348, 242),
        # s, finishing in a tall loop
        (360, 222), (368, 196), (372, 170), (363, 162), (354, 178), (358, 210), (370, 238), (364, 256), (346, 256)]
STROKES = [
    # K: the long stem, from the top down past everything
    {"pts": [(150, 70), (147, 150), (146, 250), (148, 310), (152, 352)], "tail": 0.30},
    # K: the arm in from the top right, a loop round the left, the leg kicking out into the name
    {"pts": [(204, 112), (172, 150), (130, 184), (96, 198), (82, 212), (96, 220), (128, 210), (150, 198), CUSP,
             (166, 222), (180, 238)] + climb(WORD)[1:], "tail": 0.10},
    {"pts": [(444, 180), (442, 230), (438, 280), (432, 330)], "tail": 0.35},
    {"pts": [(482, 222), (466, 224), (460, 242), (472, 256), (492, 252), (498, 234), (486, 222), (472, 226)], "tail": 0.2},
    {"pts": [(218, 296), (266, 278), (314, 258)], "tail": 0.35},
    {"pts": [(152, 352), (240, 316), (340, 280), (400, 262)], "tail": 0.3},
    {"pts": [(418, 262), (480, 240), (552, 218)], "tail": 0.4},
]
SPARKLES = ((150, 70, 10),)


def autograph(out):
    ms.STROKES, ms.SPARKLES, ms._B, ms.TILT, ms.SLANT = STROKES, SPARKLES, None, 0.0, 0.0
    ms.PEN, ms.NIB_MIN = 11.0, 0.42       # a fat glossy marker, like his card's
    ms.PX_SLOT = 128                      # it climbs, so it is taller than Neymar Jr's: taller rows
    ms.render(px_w=900, name="gold").save(os.path.join(out, "sig_kempes.png"))
    ms.px_sheet("gold").save(os.path.join(out, "sig_kempes_px.png"))


def box(out, src):
    """Neymar Jr's box re-coloured: green -> Argentina's sky blue, the yellow ribbon -> white with
    gold edges, the 10 badge kept navy."""
    a = np.asarray(Image.open(src).convert("RGBA")).astype(np.float32)
    rgb = a[..., :3]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    green = (g > r + 30) & (g > b + 10)
    yellow = (r > 200) & (g > 170) & (b < 90)
    lum = (0.299 * r + 0.587 * g + 0.114 * b)[..., None] / 255.0
    sky = np.array([117, 180, 228], np.float32)
    rgb = np.where(green[..., None], sky * (0.55 + 0.9 * lum), rgb)
    rgb = np.where(yellow[..., None], np.array([250, 250, 252], np.float32) * (0.75 + 0.3 * lum), rgb)
    im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a[..., 3:]]).astype(np.uint8), "RGBA")
    # a gold sun on the lid, Argentina's
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    w, h = im.size
    cx, cy = w // 2, int(h * 0.36)
    for k in range(16):
        import math
        ang = k * math.pi / 8
        d.line([(cx, cy), (cx + math.cos(ang) * 26, cy + math.sin(ang) * 26)], fill=(236, 186, 40, 255), width=4)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(250, 206, 60, 255), outline=(180, 120, 20, 255), width=2)
    im.save(os.path.join(out, "box_kempes.png"))


def event_bg(out):
    """His Game Box's backdrop: Argentina's flag, dimmed like Neymar Jr's Brazil one (event_bg.png)."""
    import math
    from PIL import ImageDraw
    W, H = 1920, 1080
    im = Image.new("RGBA", (W, H), (66, 104, 132, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, H // 3, W, 2 * H // 3], fill=(138, 142, 150, 255))
    cx, cy = W // 2, H // 2
    for k in range(32):
        ang = k * math.pi / 16
        r0, r1 = 92, 150 if k % 2 == 0 else 128
        d.line([(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0), (cx + math.cos(ang) * r1, cy + math.sin(ang) * r1)],
               fill=(150, 118, 34, 255), width=10)
    d.ellipse([cx - 90, cy - 90, cx + 90, cy + 90], fill=(156, 124, 36, 255), outline=(110, 82, 20, 255), width=6)
    im.save(os.path.join(out, "event_bg_kempes.png"))


def ragdoll(out):
    looks = {"kempes": ("light", "black", "long", None, ())}
    make_sprites.main_stars(out, [("kempes", "ARG", 10)], prefix="SIG", looks=looks)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites")
    os.makedirs(out, exist_ok=True)
    autograph(out)
    box(out, os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites", "box_neymar.png"))
    ragdoll(out)
    event_bg(out)
    print("Mario Kempes written to", out)


if __name__ == "__main__":
    main()
