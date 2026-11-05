"""THE HOLO SIGNATURE card (1 Nov) - Mario Kempes's card, from Hubi's screen recording.

    python3 make_sig_holo.py [sprites_dir]

What the recording shows (FC Mobile's Kempes): a chrome frame with a rainbow sheen that never stops moving,
crystal laurel leaves glinting up both sides, the nation's flag waving behind it and inside it, a gold
autograph across the shirt and a dark gem at the foot. This is this game's own card in that spirit: the
Signature card's own shape and laurels (make_sig_card.py), re-made in chrome - the gold turned to polished
silver with a faint iridescent tint across it, the green inlay to pale ice, the gold leaves to crystal, the
glass to a deep night blue, the gem to smoked glass. The moving part (the rainbow sheen, the glints, the
light) is drawn by the game on top, through tpl_fholochrome_card.png.

  tpl_fholo_card.png         the card round the player (the flag is drawn under it, as on every flag card)
  tpl_fholoframe_card.png    the frame only, laid over the player
  tpl_fholochrome_card.png   where the chrome and the crystal are (white), for the moving sheen
"""
import colorsys
import os
import sys

import numpy as np
from PIL import Image

SILVER = [(46, 52, 66), (110, 120, 140), (176, 186, 204), (226, 232, 242), (255, 255, 255)]
ICE = [(40, 80, 100), (110, 190, 214), (180, 238, 246), (236, 252, 255)]
NIGHT = [(4, 8, 18), (10, 18, 36), (22, 34, 60)]
SMOKE = [(18, 20, 26), (58, 62, 72), (120, 126, 138), (190, 196, 206)]


def ramp(t, stops):
    t = np.clip(t, 0, 1) * (len(stops) - 1)
    i = np.clip(t.astype(int), 0, len(stops) - 2)
    f = (t - i)[..., None]
    s = np.array(stops, np.float32)
    return s[i] * (1 - f) + s[i + 1] * f


def iris(h, w, period=230.0):
    """A soft rainbow across the card, diagonal - the chrome's colour where the light catches it."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    hue = ((xx * 0.8 + yy * 0.55) / period) % 1.0
    out = np.zeros((h, w, 3), np.float32)
    for k in range(6):                                     # hsv -> rgb, in six bands
        h0 = k / 6.0
        m = (hue >= h0) & (hue < h0 + 1 / 6.0)
        r, g, b = colorsys.hsv_to_rgb(h0 + 1 / 12.0, 1.0, 1.0)
        out[m] = (r * 255, g * 255, b * 255)
    return out


def remake(top, frame):
    a = np.asarray(top.convert("RGBA")).astype(np.float32)
    fa = np.asarray(frame.convert("RGBA")).astype(np.float32)[..., 3]
    H, W = a.shape[:2]
    rgb, al = a[..., :3], a[..., 3]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    gold = (r > b + 25) & (r >= g - 10)
    green = (g > r + 20) & (g > b)
    yy, xx = np.mgrid[0:H, 0:W]
    inside = (xx > 74) & (xx < 326) & (yy > 42) & (yy < 450)
    gem = (np.abs(xx - 200) < 24) & (yy > 428) & (yy < 482) & gold
    ring = (fa > 8) & ~gem
    leaf = (al > 8) & gold & ~ring & ~gem & ~inside
    glass = (al > 8) & ~ring & ~leaf & ~gem
    rain = iris(H, W)
    out = rgb.copy()
    chrome = ramp(lum ** 0.85, SILVER)
    metal = (ring | leaf) & ~green
    k = np.where(leaf, 0.26, 0.10)[..., None]               # crystal leaves take more of the rainbow
    out = np.where(metal[..., None], chrome * (1 - k) + rain * k * (0.4 + 0.6 * lum[..., None]), out)
    ice = ramp(lum, ICE)
    out = np.where((ring & green)[..., None], ice * 0.85 + rain * 0.15, out)
    out = np.where(glass[..., None], ramp(lum * 1.6, NIGHT), out)
    out = np.where(gem[..., None], ramp(lum, SMOKE), out)
    # bright facet sparkles on the crystal leaves
    hot = leaf & (lum > 0.80) & (((xx * 7 + yy * 13) % 23) == 0)
    out[hot] = 255
    top2 = Image.fromarray(np.dstack([np.clip(out, 0, 255), al]).astype(np.uint8), "RGBA")
    # the frame layer: the same colours where the frame is
    f2 = np.dstack([np.clip(out, 0, 255), fa]).astype(np.uint8)
    frame2 = Image.fromarray(f2, "RGBA")
    m = np.zeros((H, W, 4), np.uint8)
    m[..., :3] = 255
    m[..., 3] = np.where(metal | (ring & green), np.clip(al, 0, 255), 0).astype(np.uint8)
    return top2, frame2, Image.fromarray(m, "RGBA")


def pin(im):
    im.putpixel((0, 0), (0, 0, 0, 1))
    im.putpixel((im.width - 1, im.height - 1), (0, 0, 0, 1))
    return im


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "sprites")
    src = os.path.join(here, "sprites")
    top = Image.open(os.path.join(src, "tpl_fsig_card.png"))
    frame = Image.open(os.path.join(src, "tpl_fsigframe_card.png"))
    t2, f2, m = remake(top, frame)
    pin(t2).save(os.path.join(out, "tpl_fholo_card.png"))
    pin(f2).save(os.path.join(out, "tpl_fholoframe_card.png"))
    pin(m).save(os.path.join(out, "tpl_fholochrome_card.png"))
    print("holo Signature card written to", out)


if __name__ == "__main__":
    main()
