"""The 12 World Cup flags (ARG.png ... SPA.png), drawn in pixel art.  python3 make_flags.py [out_dir]"""
import math, sys
from PIL import Image, ImageDraw
W, H = 240, 160
WH = (246, 246, 246)
def canvas(c=WH):
    im = Image.new("RGBA", (W, H), c + (255,)); return im, ImageDraw.Draw(im)
def stripes(cols, vertical):
    im, d = canvas(); n = len(cols)
    for k, c in enumerate(cols):
        d.rectangle([k*W/n, 0, (k+1)*W/n, H] if vertical else [0, k*H/n, W, (k+1)*H/n], fill=c)
    return im, d
def star(cx, cy, ro, ri, n=5, rot=-math.pi/2):
    return [(cx+math.cos(rot+k*math.pi/n)*(ro if k%2==0 else ri), cy+math.sin(rot+k*math.pi/n)*(ro if k%2==0 else ri)) for k in range(2*n)]
F = {}
im, d = stripes([(116,172,223), WH, (116,172,223)], False); d.ellipse([106,66,134,94], fill=(246,180,14), outline=(132,53,17)); F["ARG"] = im
im, d = canvas((0,148,64)); d.polygon([(22,80),(120,16),(218,80),(120,144)], fill=(254,221,0)); d.ellipse([84,44,156,116], fill=(0,39,118)); d.arc([78,58,170,120], 200, 330, fill=WH, width=5); F["BRA"] = im
im, d = stripes([(255,0,0), WH, (23,23,150)], False)
for r in range(5):
    for c in range(5):
        x, y = 100 + c*8, 46 + r*8
        d.rectangle([x, y, x+7, y+7], fill=(255,0,0) if (r+c)%2==0 else WH)
d.rectangle([99,45,140,86], outline=(23,23,150), width=2); F["CRO"] = im
im, d = canvas(); d.rectangle([104,0,136,H], fill=(206,17,36)); d.rectangle([0,64,W,96], fill=(206,17,36)); F["ENG"] = im
im, d = stripes([(0,35,149), WH, (237,41,57)], True); F["FRA"] = im
im, d = canvas((193,39,45)); d.line(star(120,82,36,14)+[star(120,82,36,14)[0]], fill=(0,98,51), width=6); F["MOR"] = im
im, d = canvas(); d.ellipse([84,44,156,116], fill=(188,0,45)); F["JPN"] = im
im, d = stripes([WH, (220,20,60)], False); F["POL"] = im
im, d = stripes([(174,28,40), WH, (33,70,139)], False); F["NET"] = im
im, d = canvas((0,40,104))
d.rectangle([0,0,120,80], fill=(0,40,104)); d.line([(0,0),(120,80)], fill=WH, width=14); d.line([(120,0),(0,80)], fill=WH, width=14)
d.line([(0,0),(120,80)], fill=(200,16,46), width=5); d.line([(120,0),(0,80)], fill=(200,16,46), width=5)
d.rectangle([48,0,72,80], fill=WH); d.rectangle([0,28,120,52], fill=WH); d.rectangle([54,0,66,80], fill=(200,16,46)); d.rectangle([0,34,120,46], fill=(200,16,46))
for (x, y, r) in ((60,120,16),(180,36,9),(204,76,9),(164,96,9),(184,128,9),(194,104,5)):
    d.polygon(star(x, y, r, r*0.45, 7), fill=WH)
F["AUS"] = im
im, d = stripes([(170,21,27),(241,191,0),(241,191,0),(170,21,27)], False); d.rectangle([48,58,78,102], fill=(170,21,27), outline=(241,191,0)); F["SPA"] = im
im, d = canvas((255,0,0)); d.rectangle([0,0,96,H], fill=(0,102,0)); d.ellipse([66,50,126,110], outline=(255,204,0), width=6)
d.line([(70,80),(122,80)], fill=(255,204,0), width=4); d.rectangle([84,62,108,98], fill=WH, outline=(255,0,0), width=4)
for (x, y) in ((96,72),(90,80),(102,80),(96,88)): d.rectangle([x-2,y-2,x+2,y+2], fill=(0,56,168))
F["POR"] = im
out = sys.argv[1]
for code, im in F.items():
    im.resize((W//3, H//3), Image.NEAREST).resize((W, H), Image.NEAREST).save("%s/%s.png" % (out, code))
print(len(F))
