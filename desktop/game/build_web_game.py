"""Pack the browser build of the game (game/aswc.apk + game/aswc.tar.gz) without pygbag.

    python3 build_web_game.py <old game folder with your .ogg files> <out folder>

What pygbag's build does for this game is just this: everything the game reads goes in an
archive under assets/ (main.py = ragdoll_football.py, sprites/, the flag PNGs, the .ogg music).
The loader page (index.html) and bridge.js stay as they are.

5 Nov optimising pass: the browser shows the game at 640 x 360, a third of the size it's drawn
at, so pictures that are only ever scaled to a size on loading (card templates, full-screen
backgrounds, stadiums) go in at half size. load_pixel() trims every picture to its visible part
and scales it to the size asked for, so each one is cropped to its visible part first and its
corners pinned - the game ends up with exactly the same shapes, for a quarter of the memory.
"""
import os
import sys
import tarfile
import zipfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))


def shrink_ok(name):
    return (name.startswith("tpl_") and name.endswith("_card.png")) or name.endswith("_bg.png") \
        or name.startswith("event_bg") or name.startswith("stadium_") or name.startswith("slide_")


def shrink(src, dst):
    im = Image.open(src).convert("RGBA")
    box = im.getchannel("A").getbbox()
    if box:
        im = im.crop(box)
    w, h = im.size
    small = im.resize((max(1, w // 2), max(1, h // 2)), Image.BOX)
    a = small.getchannel("A")
    for xy in ((0, 0), (small.width - 1, small.height - 1)):   # keep the visible box exactly the same
        if a.getpixel(xy) == 0:
            small.putpixel(xy, small.getpixel(xy)[:3] + (1,))
    small.save(dst, optimize=True)


def main():
    oggs = sys.argv[1] if len(sys.argv) > 1 else HERE
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "web_build")
    stage = os.path.join(out, "stage", "assets")
    os.makedirs(os.path.join(stage, "sprites"), exist_ok=True)
    with open(os.path.join(HERE, "ragdoll_football.py"), "rb") as fh, open(os.path.join(stage, "main.py"), "wb") as o:
        o.write(fh.read())
    small = 0
    for f in sorted(os.listdir(os.path.join(HERE, "sprites"))):
        if not f.endswith(".png"):
            continue
        src, dst = os.path.join(HERE, "sprites", f), os.path.join(stage, "sprites", f)
        if shrink_ok(f):
            shrink(src, dst)
            small += 1
        else:
            with open(src, "rb") as a, open(dst, "wb") as b:
                b.write(a.read())
    for f in sorted(os.listdir(HERE)):
        if f.endswith(".png"):
            with open(os.path.join(HERE, f), "rb") as a, open(os.path.join(stage, f), "wb") as b:
                b.write(a.read())
    for f in sorted(os.listdir(oggs)):
        if f.endswith(".ogg"):
            with open(os.path.join(oggs, f), "rb") as a, open(os.path.join(stage, f), "wb") as b:
                b.write(a.read())
    files = []
    root = os.path.dirname(stage)
    for d, ds, fs in os.walk(stage):
        ds.sort()
        for f in sorted(fs):
            files.append(os.path.relpath(os.path.join(d, f), root))
    with zipfile.ZipFile(os.path.join(out, "aswc.apk"), "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(os.path.join(root, f), f)
    with tarfile.open(os.path.join(out, "aswc.tar.gz"), "w:gz") as t:
        for f in files:
            t.add(os.path.join(root, f), arcname=f, recursive=False)
    print("%d files (%d pictures at half size) -> %s" % (len(files), small, out))


if __name__ == "__main__":
    main()
