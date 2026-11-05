"""Preview renderer: draws the 17 World Cup draft cards the way draw_pool_card does in the
game, with PIL instead of pygame, then runs the frame through the same 1/3 nearest-neighbour
pixelation the game applies to everything it shows.

    python3 render_cards.py sprites out.png [card_width] [--raw]

It mirrors ragdoll_football.py: template stretched so its body is W x H, the figure placed
by FIG_WIN / FIG_PX (three screen pixels per art pixel on a full-size card, smoothed down on
a small one), clipped to the card, then the scrim, the rating lozenge, rating, position,
name and flag. Card height defaults to the game's reveal card shape (340 x 472).
"""
import os
import re
import sys
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TPL_SIZE = (400, 500)
TPL_BODY = (66, 34, 334, 458)
PIXEL = 3
HERE = os.path.dirname(os.path.abspath(__file__))


def game_consts():
    """The figure-placement numbers, read out of the game so the preview cannot drift from it."""
    src = open(os.path.join(HERE, "ragdoll_football.py"), encoding="utf-8").read()
    out = {}
    for k in ("FIG_WIN", "FIG_SNAP"):
        a, b = re.search(r"^\s+%s = \(([0-9.]+), ([0-9.]+)\)" % k, src, re.M).groups()
        out[k] = (float(a), float(b))
    out["FIG_PX"] = float(re.search(r"^\s+FIG_PX = ([0-9.]+)", src, re.M).group(1))
    return out


def load_art(sprites="sprites"):
    src = open(os.path.join(HERE, "make_art.py"), encoding="utf-8").read()
    src = src.replace('if __name__ == "__main__":\n    main()', "")
    ns = {"__name__": "make_art_preview", "__file__": os.path.join(HERE, "make_art.py")}
    argv = sys.argv
    sys.argv = ["make_art.py", sprites]
    exec(compile(src, "make_art.py", "exec"), ns)
    sys.argv = argv
    return ns


def ovr(raw):
    shown = 55 + (raw - 70) * (125 - 55) / float(150 - 70)
    return int(round(min(shown, 130)))


def text_fit(txt, colour, max_w, max_h, outline=None):
    f = ImageFont.truetype(FONT, 120)
    sw = 6 if outline else 0
    l, t, r, b = f.getbbox(txt, stroke_width=sw)
    im = Image.new("RGBA", (r - l + 4, b - t + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - l, 2 - t), txt, font=f, fill=colour, stroke_width=sw,
                            stroke_fill=outline)
    k = min(max_w / im.width, max_h / im.height)
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)


def template(sprites, key, w, h):
    p = os.path.join(sprites, "tpl_%s_card.png" % key)
    src = Image.open(p).convert("RGBA")
    bb = src.getbbox()
    src = src.crop(bb).resize(TPL_SIZE, Image.NEAREST)          # load_pixel trims, then fills
    bx0, by0, bx1, by1 = TPL_BODY
    kx, ky = w / (bx1 - bx0), h / (by1 - by0)
    img = src.resize((int(TPL_SIZE[0] * kx), int(TPL_SIZE[1] * ky)), Image.LANCZOS)
    return img, int(bx0 * kx), int(by0 * ky)


def scrim(w, h):
    s = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    y0, y1 = int(h * 0.60), int(h * 0.76)
    for y in range(y0, h):
        a = int(242 * min(1.0, (y - y0) / float(max(1, y1 - y0))) ** 1.5)
        d.line([(0, y), (w, y)], fill=(6, 10, 26, a))
    return s


def draw_card(sprites, card, pool, W, consts, flags_dir, H=None, fig=None):
    """fig: a figure to show instead of the one in the sprites folder (same 160 x 170 frame)."""
    H = int(H or round(W * 472 / 340.0))
    if card["design"] == "signature":
        key = "sig"
    else:
        key = ("holo_" if pool == "A" else "holob_") + card["team"]
    tpl, ox, oy = template(sprites, key, W, H)
    rx, ry = ox + 12, oy + 27
    rx, ry = rx - rx % PIXEL, ry - ry % PIXEL
    canvas = Image.new("RGBA", (tpl.width + 24, tpl.height + 42), (22, 26, 40, 255))
    canvas.alpha_composite(tpl, (rx - ox, ry - oy))
    # ---- the figure, exactly as draw_pool_card places it
    if fig is None:
        fig = Image.open(os.path.join(sprites, "%s_figure.png" % card["id"]))
    fig = fig.convert("RGBA")
    dw, dh = int(W * 0.055), int(H * 0.045)                     # rect.inflate(-dw, -dh)
    inset = (rx + dw // 2, ry + dh // 2, rx + dw // 2 + W - dw, ry + dh // 2 + H - dh)
    s = (inset[2] - inset[0]) / consts["FIG_PX"]                # screen pixels per art pixel
    if consts["FIG_SNAP"][0] <= s <= consts["FIG_SNAP"][1]:
        s = float(PIXEL)
    size = (max(1, int(round(fig.width * s))), max(1, int(round(fig.height * s))))
    fig = fig.resize(size, Image.NEAREST if s >= PIXEL else Image.BOX)
    px = (inset[0] + inset[2]) // 2 - int(round((consts["FIG_WIN"][0] + consts["FIG_PX"] / 2.0) * s))
    py = inset[1] - int(round(consts["FIG_WIN"][1] * s))
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    big = Image.new("RGBA", (canvas.width + 2 * fig.width, canvas.height + 2 * fig.height), (0, 0, 0, 0))
    big.alpha_composite(fig, (px + fig.width, py + fig.height))
    layer.alpha_composite(big.crop((fig.width, fig.height, fig.width + canvas.width, fig.height + canvas.height)))
    clip = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(clip).rectangle([inset[0], inset[1], inset[2] - 1, inset[3] - 1], fill=255)
    layer.putalpha(Image.composite(layer.split()[3], Image.new("L", canvas.size, 0), clip))
    canvas.alpha_composite(layer)
    canvas.alpha_composite(scrim(inset[2] - inset[0], inset[3] - inset[1]), (inset[0], inset[1]))
    # ---- rating + position over a soft dark lozenge
    num = text_fit(str(ovr(card["rating"])), (255, 255, 255), W * 0.38, H * 0.11, (10, 14, 30))
    pos = text_fit(card["pos"], (246, 206, 100), W * 0.3, H * 0.065)
    nx, ny = rx + int(W * 0.06), ry + int(H * 0.03)
    pw = max(num.width, pos.width) + int(W * 0.10)
    ph = num.height + pos.height + int(H * 0.028)
    sh = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i, a in enumerate((32, 40, 50)):
        lay = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        ImageDraw.Draw(lay).rounded_rectangle([i * 4, i * 4, pw - 1 - i * 4, ph - 1 - i * 4],
                                              max(4, int(ph * 0.3)), fill=(3, 7, 20, a))
        sh.alpha_composite(lay)
    canvas.alpha_composite(sh, (nx - int(W * 0.035), ny - int(H * 0.016)))
    canvas.alpha_composite(num, (nx, ny))
    canvas.alpha_composite(pos, (rx + int(W * 0.075), ry + int(H * 0.035) + num.height))
    d = ImageDraw.Draw(canvas)
    if key == "sig":
        rw, rh = int(W * 0.52), int(H * 0.058)
        x0, y0 = rx + W // 2 - rw // 2, ry - int(H * 0.032)
        d.rounded_rectangle([x0 - 3, y0 - 3, x0 + rw + 3, y0 + rh + 3], int(H * 0.03), fill=(28, 20, 6))
        d.rounded_rectangle([x0, y0, x0 + rw, y0 + rh], int(H * 0.028), fill=(236, 196, 90))
        lab = text_fit("SIGNATURE", (56, 36, 6), rw * 0.8, rh * 0.78)
        canvas.alpha_composite(lab, (x0 + (rw - lab.width) // 2, y0 + (rh - lab.height) // 2))
        for side in (-1, 1):
            d.line([(rx + W // 2 + side * int(W * 0.14), ry + int(H * 0.825)),
                    (rx + W // 2 + side * int(W * 0.40), ry + int(H * 0.825))],
                   fill=(236, 200, 108), width=max(1, int(W / 150)))
    name = card["name"].upper()
    if len(name) > 13 and " " in name:
        name = name.split()[-1]
    nm = text_fit(name, (255, 255, 255), W * 0.86, H * 0.075)
    canvas.alpha_composite(nm, (rx + W // 2 - nm.width // 2, ry + int(H * 0.775) - nm.height // 2))
    fp = os.path.join(flags_dir, card["team"] + ".png")
    if os.path.exists(fp):
        fl = Image.open(fp).convert("RGBA")
        k = min(W * 0.17 / fl.width, H * 0.07 / fl.height)
        fl = fl.resize((max(1, int(fl.width * k)), max(1, int(fl.height * k))), Image.NEAREST)
        canvas.alpha_composite(fl, (rx + W // 2 - fl.width // 2, ry + int(H * 0.87) - fl.height // 2))
    if key == "sig":
        nb = text_fit(str(card["number"]), (90, 60, 10), W * 0.14, H * 0.05)
        canvas.alpha_composite(nb, (rx + W // 2 - nb.width // 2, ry + int(H * 1.014) - nb.height // 2))
    return canvas


ORDER = ["WC_SPA_olmo", "WC_FRA_dembele", "WC_POR_bernardo", "WC_NET_gakpo", "WC_AUS_ryan",
         "WC_JPN_minamino", "WC_MOR_hakimi", "WC_ENG_bellingham", "WC_BRA_vinicius", "WC_SPA_yamal",
         "WC_POR_ronaldo", "WC_CRO_modric", "WC_POL_lewandowski", "WC_NET_vandijk", "WC_FRA_mbappe",
         "SIG_BRA_neymar", "WC_ARG_messi"]


def pixelate(im):
    small = im.resize((max(1, im.width // PIXEL), max(1, im.height // PIXEL)), Image.NEAREST)
    return small.resize((small.width * PIXEL, small.height * PIXEL), Image.NEAREST)


def sheet(sprites, out, W=340, raw=False, only=None, cols=6, title=None, H=None, zoom=1):
    ns = load_art(sprites)
    consts = game_consts()
    cards = {c["id"]: c for c in ns["load_card_db"]()}
    ids = [i for i in ORDER if (only is None or i in only)]
    tiles = []
    for n, cid in enumerate(ids):
        c = cards[cid]
        im = draw_card(sprites, c, ns["card_pool"](c), W, consts, HERE, H=H)
        if not raw:
            im = pixelate(im)
        if zoom != 1:
            im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
        tiles.append((ORDER.index(cid) + 1, c, im))
    tw, th = tiles[0][2].size
    lab_h = 34
    rows = (len(tiles) + cols - 1) // cols
    head = 60 if title else 0
    sh = Image.new("RGB", (cols * tw, head + rows * (th + lab_h)), (22, 26, 40))
    d = ImageDraw.Draw(sh)
    if title:
        d.text((16, 14), title, font=ImageFont.truetype(FONT, 28), fill=(236, 240, 250))
    f = ImageFont.truetype(FONT, 20)
    for i, (n, c, im) in enumerate(tiles):
        x, y = (i % cols) * tw, head + (i // cols) * (th + lab_h)
        sh.paste(im.convert("RGB"), (x, y))
        d.text((x + 14, y + th + 4), "%d  %s" % (n, c["name"]), font=f, fill=(236, 240, 250))
    sh.save(out)
    return sh.size


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sprites = args[0] if args else "sprites"
    out = args[1] if len(args) > 1 else "cards.png"
    W = int(args[2]) if len(args) > 2 else 340
    print(sheet(sprites, out, W, raw="--raw" in sys.argv))
