"""LIMIT BREAKERS figures - the pack's 28 players on the card, posed with cardfig.

Same rules as cards17.py: LEFT and RIGHT are the CARD's, arms are written as the camera sees
them, (upper-arm direction, forearm direction, hand[, options]). Pool A and B (13) are posed
from the pictures Hubi sent; pool C (15) has no pictures, so they stand easy in their country's
shirt with a little turn and a face each. Kits are shapes and colours only - no crest, no maker,
no sponsor. cardfig.py itself is untouched: the two things this pack needs that it lacks
(vertical stripes and a pharaoh headdress) are added here by subclassing.
"""
import numpy as np

import cardfig
from cardfig import Fig, Kit, Shot, mat

cardfig.RAMPS.setdefault("pink", [(150, 62, 96), (204, 104, 140), (238, 150, 182), (250, 190, 212), (255, 224, 236)])


class StripeKit(Kit):
    """A Kit with vertical stripes: stripes=(alt material, period cm, share of the period)."""

    def __init__(self, stripes=None, **kw):
        super().__init__(**kw)
        self.stripes = stripes
        if stripes:
            self.alt = stripes[0]

    def paint(self, q, sleeve, sl_t, collar):
        m, off = super().paint(q, sleeve, sl_t, collar)
        if self.stripes:
            alt, period, share = self.stripes
            x = q[:, 0]
            on = (((x / period) + 0.5) % 1.0) < share
            body = m == mat(self.body)
            m[on & body & ~sleeve & ~collar] = mat(alt)
        return m, off


class NemesFig(Fig):
    """Salah's pharaoh headdress: the 'hair' is cloth, gold and black bands, a gold brow band."""

    def head_mats(self, P, part):
        m, off = super().head_mats(P, part)
        q = self.head_local(P)
        cloth = part == 1
        band = ((q[:, 1] + 0.18 * np.abs(q[:, 0])) % 2.6) < 1.05
        m[cloth & band] = mat("nemes_gold", "gold", 1.2)
        brow = cloth & (np.abs(q[:, 1] - (12.6 - 0.12 * q[:, 2])) < 0.75) & (q[:, 2] > 2.0)
        m[brow] = mat("nemes_band", "gold", 1.6)
        off[brow] = 1
        return m, off


# ------------------------------------------------------------------ kits
def K(**kw):
    return StripeKit(**kw)


SPAIN = dict(body="red", sleeve="navy", collar="navy", number="yellow", shorts="navy",
             raglan=True, pinstripe=3.4, badge=("yellow", "red"), piping="yellow")
EGYPT_TEE = dict(body="red", collar="red", number="white", number_txt="", shorts="black", badge=None)
PSG = dict(body="deep_navy", collar="white", cuff="white", number="white", shorts="deep_navy", badge=("red", "white"))
CITY = dict(body="sky", collar="navy", cuff="navy", number="navy", shorts="white", badge=("navy", "sky"))
LAFC = dict(body="black", collar="gold", number="gold", shorts="black", stripes=("gold", 3.2, 0.16),
            badge=("gold", "black"))
BETIS = dict(body="white", collar="green", number="black", shorts="white", stripes=("green", 6.2, 0.5),
             badge=("green", "white"))
RACING = dict(body="white", sleeve="green", collar="green", number="green", shorts="black", raglan=True,
              badge=("green", "white"))
ATHLETIC = dict(body="white", collar="black", number="black", shorts="black", stripes=("red", 6.2, 0.5),
                badge=("red", "white"))
MIAMI = dict(body="pink", collar="black", cuff="black", number="black", shorts="pink", badge=("black", "pink"))
JUVE = dict(body="white", collar="black", number="gold", shorts="white", stripes=("black", 6.0, 0.5),
            badge=("black", "white"))
CHELSEA = dict(body="blue", collar="white", cuff="white", number="white", shorts="blue", badge=("white", "blue"))
IVORY = dict(body="orange", collar="green", cuff="green", number="white", shorts="white", badge=("green", "orange"))
# pool C: national shirts
ENGLAND = dict(body="white", collar="navy", cuff="navy", number="navy", shorts="navy", badge=("navy", "red"))
SERBIA = dict(body="red", collar="white", cuff="white", number="white", shorts="blue", badge=("white", "red"))
HOLLAND = dict(body="orange", collar="navy", cuff="navy", number="navy", shorts="orange", pinstripe=2.4,
               badge=("white", "blue"))
ARGENTINA = dict(body="white", collar="navy", number="black", shorts="black", stripes=("sky", 6.4, 0.5),
                 badge=("sky", "white"))
PORTUGAL = dict(body="red", collar="green", cuff="green", number="yellow", shorts="green", badge=("yellow", "green"))
CAMEROON_GK = dict(body="green", collar="green", number="white", pattern="zig", long_sleeve=True, shorts="green",
                   badge=("yellow", "red"))
TURKEY = dict(body="red", collar="white", cuff="white", number="white", shorts="white", badge=("white", "red"))
FRANCE = dict(body="deep_navy", collar="white", collar_w=2.2, number="white", shorts="white", pinstripe=3.0,
              badge=("yellow", "deep_navy"))
MOROCCO = dict(body="red", collar="green", cuff="green", number="white", shorts="green", badge=("yellow", "green"))
GERMANY = dict(body="white", collar="black", cuff="black", number="black", shorts="black", badge=("black", "white"))
SLOVENIA = dict(body="white", collar="green", cuff="blue", number="green", shorts="white", badge=("green", "blue"))

HANG_L = ((-0.14, -0.98, 0.06), (-0.05, -0.97, 0.22), "relaxed")
HANG_R = ((0.14, -0.98, 0.06), (0.05, -0.97, 0.22), "relaxed")
CROP = dict(len=0.5, fringe=2.0, fade=True)
SHORT = dict(len=0.8, top=1.2, fade=True)
SLICK = dict(len=0.9, top=1.5, quiff=1.0, fade=True)


def kit(number, base, **more):
    d = dict(base)
    d.update(more)
    d.setdefault("number_txt", str(number))
    return K(**d)


# ================================================================== POOL A
def yamal():
    # jogging at you, elbows bent, fists loose in front, a calm half smile
    f = Fig(skin="skin_tan", hair="black", iris="iris_brown",
            hair_cfg=dict(len=1.6, top=3.0, curl=1.2, fade=True),
            kit=kit(19, SPAIN), torso=(-6, -2, 2), shrug=(1.0, 2.0), head=(-4, 2, -4),
            eye_open=0.9, brow_lift=0.05, mouth="closed", mouth_w=2.2, smile=0.35,
            left=((-0.32, -0.90, 0.30), (0.62, -0.05, 0.78), "fist"),
            right=((0.30, -0.92, 0.25), (-0.45, -0.30, 0.84), "fist"),
            order=("body", "head", "left", "right"))
    f.folds = (((-9, -18), (3, -32), 0.45, 1.5),)
    return f, Shot(top_y=36.0, centre_x=-1.0)


def salah():
    # both fists up beside his head, a huge grin, in a pharaoh's headdress and a plain red tee
    f = NemesFig(skin="skin_tan", hair="black", iris="iris_brown", beard="full", beard_ramp="black",
                 hair_cfg=dict(len=1.4, top=1.6, long=6.5, side=1.28, fringe=-0.4),
                 kit=kit("", EGYPT_TEE), torso=(4, -2, 0), shrug=(5.0, 5.0), head=(6, 4, 4),
                 eye_open=0.6, brow_lift=0.15, mouth="smile", mouth_w=2.9, mouth_h=1.05, smile=1.0, snarl=1.0,
                 left=((-0.55, 0.31, -0.77), (0.42, 0.64, 0.64), "fist"),
                 right=((0.55, 0.31, -0.77), (-0.42, 0.64, 0.64), "fist"), pecs=0.3)
    # 30 Oct: the plain tee pulled up by two raised arms read as a round bust - the creases Olmo has
    # (armpit to middle) break it into a shirt
    f.folds = (((-14, -11), (-4, -27), 0.55, 1.3), ((14, -11), (4, -27), 0.55, 1.3),
               ((-15, -24), (-7, -44), 0.5, 1.6), ((15, -24), (7, -44), 0.5, 1.6))
    return f, Shot(top_y=37.0, centre_x=0.0)


def dembele():
    # body turned to the card's right, head back round to the lens, quiet and serious
    f = Fig(light="right", skin="skin_dark", hair="black", iris="iris_brown", hair_cfg=CROP, beard="stubble",
            lip="lip_dark", kit=kit(10, PSG), torso=(34, 0, 0), head=(12, 0, 0),
            gaze=(-0.15, 0.0), brow_lift=-0.25, brow_slope=0.5, mouth="closed", mouth_w=2.1,
            left=HANG_L, right=HANG_R, order=("right", "body", "head", "left"))
    f.folds = (((-6, -14), (8, -28), 0.45, 1.5),)
    return f, Shot(top_y=35.5, centre_x=3.0)


def haaland():
    # square-ish, looking off to the card's right, hair tied back
    f = Fig(light="right", skin="skin_fair", hair="blond", hair_side="blond_dark", brow="blond_dark",
            iris="iris_blue", hair_cfg=dict(len=0.9, top=0.6, bun=True, fringe=-0.6),
            kit=kit(9, CITY), torso=(10, 0, 0), head=(26, 2, 0),
            gaze=(0.3, 0.0), brow_lift=-0.1, mouth="closed", mouth_w=2.1, jaw_w=5.8,
            left=HANG_L, right=HANG_R)
    f.folds = (((-8, -16), (4, -30), 0.4, 1.5),)
    return f, Shot(top_y=35.5, centre_x=1.0)


def son():
    # caught by surprise: brows up, mouth open, head turned a touch to the card's left
    f = Fig(skin="skin_light", hair="black", iris="iris_brown",
            hair_cfg=dict(len=1.1, top=1.4, fringe=2.6, part_x=1.0, side=1.05),
            kit=kit(7, LAFC), torso=(-6, 0, 0), head=(-12, 4, 2),
            eye_open=1.1, brow_lift=0.5, mouth="shout", mouth_w=1.6, mouth_h=0.9, jaw_drop=0.5,
            left=HANG_L, right=HANG_R)
    return f, Shot(top_y=35.5, centre_x=-1.0)


# ================================================================== POOL B
CLAP_L = ((-0.40, -0.75, 0.53), (0.85, 0.38, 0.37), "flat", dict(dir=(0.30, 0.95, 0.0), face=(0.95, 0, 0.3)))
CLAP_R = ((0.40, -0.75, 0.53), (-0.85, 0.38, 0.37), "flat", dict(dir=(-0.30, 0.95, 0.0), face=(-0.95, 0, 0.3)))


def isco():
    # applauding in front of his chest, full beard, a small smile
    f = Fig(skin="skin_light", hair="brown_dark", iris="iris_brown", beard="full", beard_ramp="brown_dark",
            hair_cfg=SLICK, kit=kit(22, BETIS), torso=(-4, 0, 0), head=(-6, -2, -3),
            mouth="closed", mouth_w=2.2, smile=0.5, left=CLAP_L, right=CLAP_R,
            order=("body", "head", "left", "right"))
    return f, Shot(top_y=35.5, centre_x=0.0)


def canales():
    # easy stance, turned a little to the card's left, swept hair
    f = Fig(skin="skin_light", hair="brown", iris="iris_brown", beard="stubble",
            hair_cfg=dict(len=1.0, top=2.0, quiff=1.4, top_x=0.6),
            kit=kit(10, RACING), torso=(-12, 0, 0), head=(-14, 0, 0),
            gaze=(-0.15, 0.0), mouth="closed", mouth_w=2.0, left=HANG_L, right=HANG_R)
    return f, Shot(top_y=35.5, centre_x=-1.5)


def yeray():
    # square to the lens, steady
    f = Fig(skin="skin_light", hair="brown_dark", iris="iris_brown", beard="stubble", hair_cfg=SHORT,
            kit=kit(5, ATHLETIC), torso=(4, 0, 0), head=(2, 0, 0), brow_lift=-0.1,
            mouth="closed", mouth_w=2.0, left=HANG_L, right=HANG_R)
    return f, Shot(top_y=35.5, centre_x=0.0)


def suarez():
    # a big grin, pointing away to the card's left
    f = Fig(skin="skin_light", hair="brown_dark", iris="iris_brown", beard="stubble", hair_cfg=SLICK,
            kit=kit(9, MIAMI), torso=(-10, 2, 0), shrug=(4.0, 0.0), head=(-16, 4, -2),
            eye_open=0.6, mouth="smile", mouth_w=3.0, mouth_h=1.0, smile=1.0, snarl=1.0,
            left=((-0.86, 0.22, 0.46), (-0.82, 0.32, 0.47), "point", dict(dir=(-0.80, 0.34, 0.50), face=(0, 0.6, 0.8))),
            right=HANG_R)
    return f, Shot(top_y=35.5, centre_x=-2.0)


def locatelli():
    # captain, hair swept back, a level look
    f = Fig(skin="skin_light", hair="brown_dark", iris="iris_brown", beard="short", beard_ramp="brown_dark",
            hair_cfg=dict(len=1.2, top=1.8, quiff=1.0, long=1.6, side=1.05),
            kit=kit(5, JUVE), armband=("right", "gold"), torso=(-4, 0, 0), head=(-2, 0, 0),
            brow_lift=-0.15, mouth="closed", mouth_w=2.1, left=HANG_L, right=HANG_R)
    return f, Shot(top_y=35.5, centre_x=0.0)


def bremer():
    # turned a little to the card's right, serious
    f = Fig(light="right", skin="skin_brown", hair="black", iris="iris_brown", beard="short", lip="lip_dark",
            hair_cfg=CROP, kit=kit(3, JUVE), torso=(14, 0, 0), head=(8, 0, 0),
            brow_lift=-0.3, brow_slope=0.6, mouth="closed", mouth_w=2.1, jaw_w=5.8, left=HANG_L, right=HANG_R)
    return f, Shot(top_y=35.5, centre_x=1.0)


def gusto():
    # mid-run, looking off to the card's right, braids
    f = Fig(light="right", skin="skin_brown", hair="black", iris="iris_brown", lip="lip_dark",
            hair_cfg=dict(len=1.4, top=2.0, curl=1.2, long=2.6, side=1.05),
            kit=kit(27, CHELSEA), torso=(16, 2, -2), head=(26, 0, 0), gaze=(0.3, 0.0),
            mouth="closed", mouth_w=2.0,
            left=((-0.30, -0.90, 0.32), (0.55, -0.05, 0.83), "fist"),
            right=((0.30, -0.90, -0.30), (0.15, -0.95, 0.27), "fist"))
    return f, Shot(top_y=35.5, centre_x=2.0)


def diomande():
    # both fists clenched up at his chest, beaming
    f = Fig(skin="skin_dark", hair="black", iris="iris_brown", lip="lip_dark",
            hair_cfg=dict(len=1.2, top=2.6, curl=1.0, fade=True),
            kit=kit(11, IVORY), torso=(-4, 2, 0), shrug=(3.0, 3.0), head=(-4, 4, 2),
            eye_open=0.7, mouth="smile", mouth_w=2.9, mouth_h=1.0, smile=1.0,
            left=((-0.22, -0.82, 0.53), (0.55, 0.62, 0.56), "fist"),
            right=((0.22, -0.82, 0.53), (-0.55, 0.62, 0.56), "fist"),
            order=("body", "head", "left", "right"))
    return f, Shot(top_y=35.5, centre_x=0.0)


# ================================================================== POOL C (no pictures: standing easy)
def easy(num, base, skin, hair, hair_cfg, yaw=0, look=0, mouth="closed", smile=0.0, beard=None,
         beard_ramp=None, light=None, lip="lip", iris="iris_brown", gloves=False, **more):
    hand = dict(glove="charcoal") if gloves else {}
    left = HANG_L + ((hand,) if gloves else ())
    right = HANG_R + ((hand,) if gloves else ())
    f = Fig(light=light or ("right" if yaw > 8 else "left"), skin=skin, hair=hair, iris=iris, beard=beard,
            beard_ramp=beard_ramp, lip=lip, hair_cfg=hair_cfg, kit=kit(num, base),
            torso=(yaw, 0, 0), head=(yaw + look, 2, 0), gaze=(0.25 if look > 0 else -0.25 if look < 0 else 0.0, 0.0),
            mouth=mouth, mouth_w=2.2 if mouth == "closed" else 2.6, mouth_h=0.9, smile=smile,
            left=left, right=right, **more)
    return f, Shot(top_y=35.5, centre_x=yaw / 8.0)


def calhanoglu():
    return easy(10, TURKEY, "skin_light", "black", SLICK, yaw=-10, beard="stubble", smile=0.3)


def muller():
    return easy(13, GERMANY, "skin_fair", "brown_mid", SHORT, yaw=6, look=-12, mouth="smile", smile=1.0)


def palhinha():
    return easy(6, PORTUGAL, "skin_light", "brown_dark", SHORT, yaw=12, beard="short", beard_ramp="brown_dark",
                brow_lift=-0.25)


def giroud():
    return easy(9, FRANCE, "skin_light", "brown_dark", dict(len=1.0, top=1.8, quiff=1.6, top_x=0.5),
                yaw=-14, beard="full", beard_ramp="brown_dark", smile=0.3)


def mitrovic():
    return easy(9, SERBIA, "skin_light", "black", CROP, yaw=4, beard="full", beard_ramp="black",
                brow_lift=-0.35, brow_slope=0.7)


def depay():
    return easy(10, HOLLAND, "skin_brown", "black", dict(len=0.6, top=0.8, bun=True), yaw=-8, look=-8,
                beard="short", lip="lip_dark")


def correa():
    return easy(15, ARGENTINA, "skin_light", "black", SHORT, yaw=10, look=6, beard="stubble")


def fofana():
    return easy(19, FRANCE, "skin_dark", "black", CROP, yaw=-6, beard="short", lip="lip_dark", smile=0.3)


def onana():
    return easy(24, CAMEROON_GK, "skin_dark", "black", CROP, yaw=16, lip="lip_dark", gloves=True,
                brow_lift=-0.2)


def tagliafico():
    return easy(3, ARGENTINA, "skin_light", "brown_dark", dict(len=1.2, top=1.6, long=1.4, side=1.05),
                yaw=-12, beard="full", beard_ramp="brown_dark")


def ziyech():
    return easy(7, MOROCCO, "skin_tan", "black", SLICK, yaw=14, look=-6, beard="short")


def maguire():
    return easy(5, ENGLAND, "skin_fair", "brown_mid", SHORT, yaw=0, beard="stubble", jaw_w=5.9)


def tadic():
    return easy(10, SERBIA, "skin_light", "brown_dark", SLICK, yaw=-10, beard="short", beard_ramp="brown_dark",
                smile=0.4)


def ilicic():
    return easy(10, SLOVENIA, "skin_fair", "brown", dict(len=0.6, top=0.6, fade=True), yaw=8, beard="stubble")


def weghorst():
    return easy(9, HOLLAND, "skin_fair", "blond_dark", SHORT, yaw=-4, beard="full", beard_ramp="blond_dark",
                brow_lift=-0.2)


FIGS = {"LB_yamal": yamal, "LB_salah": salah, "LB_dembele": dembele, "LB_haaland": haaland, "LB_son": son,
        "LB_isco": isco, "LB_canales": canales, "LB_yeray": yeray, "LB_suarez": suarez,
        "LB_locatelli": locatelli, "LB_bremer": bremer, "LB_gusto": gusto, "LB_diomande": diomande,
        "LB_calhanoglu": calhanoglu, "LB_muller": muller, "LB_palhinha": palhinha, "LB_giroud": giroud,
        "LB_mitrovic": mitrovic, "LB_depay": depay, "LB_correa": correa, "LB_fofana": fofana,
        "LB_onana": onana, "LB_tagliafico": tagliafico, "LB_ziyech": ziyech, "LB_maguire": maguire,
        "LB_tadic": tadic, "LB_ilicic": ilicic, "LB_weghorst": weghorst}
