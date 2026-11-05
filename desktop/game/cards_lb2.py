"""LIMIT BREAKERS DRAFT B figures (31 Oct) - 28 players, posed with cardfig.

Hubi: "get the images, describe them and make draft B". The pictures couldn't be fetched (the image
search shows them to him but returns only titles here, and the card sites refuse a fetch), so each
pose is the one people know the player by - his celebration or his look - as was done for the club
packs. The roster follows FC Mobile's real Unbreakable Draft B (Van Nistelrooy, Valencia, Florenzi),
its pool B (Martinelli, Casteels, Sane, Ansu Fati) and the event's predicted players, at ratings
scaled to match Draft A. No pictures of the cards themselves, so everyone wears his COUNTRY's shirt
(the flag is the badge, like Draft A's pool C). Kits are shapes and colours only.

Same rules as cards_lb.py: LEFT and RIGHT are the CARD's, arms are written as the camera sees them,
(upper-arm direction, forearm direction, hand[, options]).
"""
import cardfig
from cardfig import Fig, Shot, mat
from cards_lb import (ARGENTINA, CROP, ENGLAND, FRANCE, GERMANY, HANG_L, HANG_R, HOLLAND, SHORT, SLICK, SPAIN,
                      StripeKit)
from cards_club import (EAR_R, FIST_CHEST_L, FIST_CHEST_R, FIST_LOW_L, FLEX_L, FLEX_R, HIP_L, HIP_R,
                        POINT_LENS_L, POINT_LENS_R, POINT_UP_R, mirror)

cardfig.RAMPS.setdefault("ginger", [(70, 26, 8), (122, 50, 16), (170, 78, 30), (206, 110, 52), (232, 150, 90)])


class CheckKit(StripeKit):
    """Croatia's red-and-white squares: checks=(alt material, square size cm)."""

    def __init__(self, checks=None, **kw):
        super().__init__(**kw)
        self.checks = checks
        if checks:
            self.alt = checks[0]

    def paint(self, q, sleeve, sl_t, collar):
        m, off = super().paint(q, sleeve, sl_t, collar)
        if self.checks:
            alt, size = self.checks
            on = ((q[:, 0] // size + q[:, 1] // size) % 2) == 0
            body = m == mat(self.body)
            m[on & body & ~sleeve & ~collar] = mat(alt)
        return m, off


# ------------------------------------------------------------------ national kits (colours only)
BRAZIL = dict(body="yellow", collar="green", cuff="green", number="green", shorts="blue", badge=("green", "yellow"))
BELGIUM = dict(body="red", collar="gold", cuff="gold", number="gold", shorts="red", badge=("gold", "red"))
BELGIUM_GK = dict(body="green", collar="black", number="white", long_sleeve=True, shorts="green",
                  badge=("black", "green"))
POLAND = dict(body="white", collar="red", cuff="red", number="red", shorts="red", badge=("red", "white"))
ECUADOR = dict(body="yellow", collar="blue", cuff="blue", number="blue", shorts="blue", badge=("blue", "yellow"))
ITALY = dict(body="blue", collar="white", cuff="white", number="white", shorts="white", badge=("gold", "blue"))
CROATIA = dict(body="red", collar="navy", number="navy", shorts="white", checks=("white", 3.2), badge=("navy", "red"))
URUGUAY = dict(body="sky", collar="white", cuff="white", number="black", shorts="black", badge=("gold", "sky"))
DENMARK_GK = dict(body="black", collar="yellow", number="yellow", long_sleeve=True, shorts="black",
                  badge=("yellow", "black"))


def kit(number, base, **more):
    d = dict(base)
    d.update(more)
    d.setdefault("number_txt", str(number))
    return CheckKit(**d)


def easy(num, base, skin, hair, hair_cfg, yaw=0, look=0, mouth="closed", smile=0.0, beard=None,
         beard_ramp=None, light=None, lip="lip", iris="iris_brown", gloves=False, **more):
    """Draft A's pool C stance (cards_lb.easy), in this file's kits - checks and all."""
    hand = dict(glove="charcoal") if gloves else {}
    left = HANG_L + ((hand,) if gloves else ())
    right = HANG_R + ((hand,) if gloves else ())
    f = Fig(light=light or ("right" if yaw > 8 else "left"), skin=skin, hair=hair, iris=iris, beard=beard,
            beard_ramp=beard_ramp, lip=lip, hair_cfg=hair_cfg, kit=kit(num, base),
            torso=(yaw, 0, 0), head=(yaw + look, 2, 0), gaze=(0.25 if look > 0 else -0.25 if look < 0 else 0.0, 0.0),
            mouth=mouth, mouth_w=2.2 if mouth == "closed" else 2.6, mouth_h=0.9, smile=smile,
            left=left, right=right, **more)
    return f, Shot(top_y=35.5, centre_x=yaw / 8.0)


GLOVE = dict(glove="charcoal")
SALUTE_R = ((0.62, 0.05, 0.78), (-0.62, 0.70, 0.36), "flat", dict(dir=(-0.75, 0.55, 0.2), face=(0, -0.2, 0.98)))
HEART_L = ((-0.30, -0.70, 0.65), (0.75, 0.45, 0.48), "flat", dict(dir=(0.55, 0.80, 0.1), face=(0.3, 0, 0.95)))
HEART_R = mirror(HEART_L)
MEGA_L = ((-0.22, -0.60, 0.77), (0.42, 0.88, 0.22), "flat", dict(dir=(0.35, 0.92, 0.1), face=(0.5, 0, 0.86)))
MEGA_R = mirror(MEGA_L)
PALMS_L = ((-0.55, -0.82, 0.18), (-0.60, -0.05, 0.80), "open", dict(dir=(-0.55, 0.05, 0.83), face=(0, 1, 0)))
PALMS_R = mirror(PALMS_L)
PLANE_L = ((-0.98, -0.18, 0.08), (-0.98, -0.10, 0.17), "open")            # arms out flat: the aeroplane
PLANE_R = mirror(PLANE_L)
HUG_L = ((-0.72, -0.40, 0.57), (-0.20, 0.10, 0.97), "open", dict(dir=(-0.1, 0.2, 0.97), face=(0.6, 0, 0.8)))
HUG_R = mirror(HUG_L)
CHEST_R = ((0.15, -0.80, 0.58), (-0.90, 0.40, 0.17), "flat", dict(dir=(-0.80, 0.55, 0.1), face=(0, 0, -1)))


# ================================================================== POOL A
def vannistelrooy():
    # the roar: one fist pumped up beside his head, the other clenched low, mouth wide
    f = Fig(skin="skin_fair", hair="brown_dark", iris="iris_brown", beard="stubble", beard_ramp="brown_dark",
            hair_cfg=dict(len=0.7, top=1.6, quiff=0.6, fade=True), kit=kit(9, HOLLAND), torso=(-4, 8, 0),
            shrug=(4.0, 2.0), head=(-2, 14, 0), eye_open=0.55, brow_lift=-0.4, brow_slope=0.9,
            mouth="smile", mouth_w=3.0, mouth_h=1.3, smile=0.5, snarl=1.0, jaw_w=5.9,
            left=FIST_LOW_L, right=FLEX_R)
    f.folds = (((14, -11), (4, -27), 0.5, 1.3),)
    return f, Shot(top_y=36.0, centre_x=-0.5)


def raphinha():
    # a hand on the badge over his heart, eyes to the sky, hair tied back with a band
    f = Fig(skin="skin_tan", hair="black", iris="iris_brown", beard="stubble", beard_ramp="black",
            hair_cfg=dict(len=1.2, top=1.8, long=1.4, bun=True, band="white"), kit=kit(11, BRAZIL),
            torso=(-4, 4, 0), head=(-2, 16, 0), gaze=(0.0, 0.3), eye_open=0.8, mouth="closed", mouth_w=2.3,
            smile=0.5, left=HANG_L, right=CHEST_R, order=("body", "head", "left", "right"))
    return f, Shot(top_y=36.0, centre_x=-0.5)


def debruyne():
    # palms open at his waist - "what did you expect?" - a calm half smile, ginger hair
    f = Fig(skin="skin_fair", hair="ginger", iris="iris_blue", brow="ginger",
            hair_cfg=dict(len=0.9, top=1.6, quiff=0.8, top_x=0.6, fade=True), kit=kit(7, BELGIUM),
            torso=(4, 2, 0), shrug=(3.0, 3.0), head=(4, 4, 2), brow_lift=0.25, mouth="closed", mouth_w=2.2,
            smile=0.6, left=PALMS_L, right=PALMS_R)
    return f, Shot(top_y=35.5, centre_x=0.5)


def lewandowski():
    # pointing both fingers straight at you, cool and certain
    f = Fig(skin="skin_fair", hair="brown_dark", iris="iris_blue", hair_cfg=dict(len=0.7, top=1.4, fade=True),
            kit=kit(9, POLAND), torso=(0, 2, 0), head=(0, 4, 0), brow_lift=-0.15, mouth="closed", mouth_w=2.2,
            smile=0.4, jaw_w=5.8, left=POINT_LENS_L, right=POINT_LENS_R, order=("body", "head", "left", "right"))
    return f, Shot(top_y=35.5, centre_x=0.0)


def saliba():
    # a hand cupped to his ear: can't hear you
    f = Fig(skin="skin_dark", hair="black", iris="iris_brown", lip="lip_dark",
            hair_cfg=dict(len=1.0, top=1.8, curl=1.0, fade=True), kit=kit(17, FRANCE), torso=(8, 2, 0),
            head=(12, 6, 6), eye_open=0.7, mouth="smile", mouth_w=2.6, smile=0.7, left=HANG_L, right=EAR_R)
    return f, Shot(top_y=35.5, centre_x=0.5)


# ================================================================== POOL B
def valencia():
    # one finger to the sky, serious
    f = Fig(skin="skin_dark", hair="black", iris="iris_brown", lip="lip_dark", beard="short",
            hair_cfg=dict(len=0.3, top=0.2, fade=True), kit=kit(16, ECUADOR), torso=(-6, 2, 0),
            head=(-4, 12, 0), gaze=(0.0, 0.2), brow_lift=-0.1, mouth="closed", mouth_w=2.2, jaw_w=5.9,
            left=HANG_L, right=POINT_UP_R)
    return f, Shot(top_y=36.0, centre_x=-0.5)


def florenzi():
    # arms open for the hug - he ran into the stand to his gran
    f = Fig(skin="skin_light", hair="brown_dark", iris="iris_brown", beard="short", beard_ramp="brown_dark",
            hair_cfg=dict(len=0.8, top=1.6, quiff=0.8, fade=True), kit=kit(24, ITALY), torso=(0, 4, 0),
            head=(0, 8, 2), eye_open=0.6, mouth="smile", mouth_w=3.0, mouth_h=1.0, smile=1.0, snarl=1.0,
            left=HUG_L, right=HUG_R)
    return f, Shot(top_y=35.5, centre_x=0.0)


def gabriel():
    # both arms flexed, roaring
    f = Fig(skin="skin_tan", hair="black", iris="iris_brown", beard="full", beard_ramp="black",
            hair_cfg=dict(len=0.3, top=0.2, fade=True), kit=kit(4, BRAZIL), torso=(0, 6, 0), shrug=(4.0, 4.0),
            head=(0, 12, 0), eye_open=0.55, brow_lift=-0.4, brow_slope=0.9, mouth="smile", mouth_w=3.0,
            mouth_h=1.3, smile=0.5, snarl=1.0, jaw_w=5.9, left=FLEX_L, right=FLEX_R)
    f.folds = (((-14, -11), (-4, -27), 0.5, 1.3), ((14, -11), (4, -27), 0.5, 1.3))
    return f, Shot(top_y=36.5, centre_x=0.0)


def fermin():
    # hands cupped round his mouth, shouting to the stand
    f = Fig(skin="skin_light", hair="black", iris="iris_brown", hair_cfg=dict(len=1.0, top=1.6, fringe=1.6),
            kit=kit(16, SPAIN), torso=(-4, 4, 0), head=(-2, 8, 0), eye_open=0.6, brow_lift=0.2,
            mouth="shout", mouth_w=1.8, mouth_h=1.0, jaw_drop=0.6, left=MEGA_L, right=MEGA_R,
            order=("body", "head", "left", "right"))
    return f, Shot(top_y=35.5, centre_x=-0.5)


def martinelli():
    # the salute
    f = Fig(skin="skin_light", hair="brown_dark", iris="iris_brown",
            hair_cfg=dict(len=1.2, top=2.0, curl=0.8, fade=True), kit=kit(11, BRAZIL), torso=(6, 2, 0),
            head=(4, 4, 0), brow_lift=-0.2, mouth="closed", mouth_w=2.2, smile=0.4, left=HANG_L, right=SALUTE_R)
    return f, Shot(top_y=35.5, centre_x=0.5)


def sane():
    # arms out flat: the aeroplane, a big grin
    f = Fig(skin="skin_dark", hair="black", iris="iris_brown", beard="short", lip="lip_dark",
            hair_cfg=dict(len=0.3, top=0.3, fade=True), kit=kit(19, GERMANY), torso=(0, 4, 4),
            head=(0, 6, 6), eye_open=0.6, mouth="smile", mouth_w=3.0, mouth_h=1.0, smile=1.0, snarl=1.0,
            left=PLANE_L, right=PLANE_R)
    return f, Shot(top_y=35.5, centre_x=0.0)


def casteels():
    # keeper's gloves, a fist clenched at his chest, eyes narrowed
    f = Fig(skin="skin_fair", hair="blond", hair_side="blond_dark", brow="blond_dark", iris="iris_blue",
            beard="stubble", beard_ramp="blond_dark", hair_cfg=dict(len=0.8, top=1.4, fade=True),
            kit=kit(1, BELGIUM_GK), torso=(-6, 2, 0), head=(-4, 4, 0), brow_lift=-0.35, brow_slope=0.6,
            mouth="closed", mouth_w=2.1, jaw_w=5.9, left=HANG_L + (GLOVE,), right=FIST_CHEST_R[:3] + (GLOVE,),
            order=("body", "head", "left", "right"))
    return f, Shot(top_y=35.5, centre_x=-0.5)


def ansufati():
    # a heart with his hands, in front of his chest
    f = Fig(skin="skin_brown", hair="black", iris="iris_brown", lip="lip_dark",
            hair_cfg=dict(len=1.2, top=2.0, curl=1.2, fade=True), kit=kit(10, SPAIN), torso=(-4, 2, 0),
            head=(-4, 4, 2), eye_open=0.7, mouth="smile", mouth_w=2.8, smile=1.0, left=HEART_L, right=HEART_R,
            order=("body", "head", "left", "right"))
    return f, Shot(top_y=35.5, centre_x=0.0)


# ================================================================== POOL C (standing easy, like Draft A's)
def modric():
    return easy(10, CROATIA, "skin_fair", "brown", dict(len=1.4, top=1.4, long=4.5, side=1.25, fringe=0.6),
                yaw=-8, look=-4, smile=0.3)


def griezmann():
    return easy(7, FRANCE, "skin_fair", "blond_dark", dict(len=0.9, top=1.8, quiff=1.2, fade=True), yaw=8,
                mouth="smile", smile=1.0, beard="stubble", beard_ramp="blond_dark")


def dimaria():
    return easy(11, ARGENTINA, "skin_light", "black", dict(len=0.6, top=1.0, fade=True), yaw=-12, look=-6,
                mouth="smile", smile=0.8)


def busquets():
    return easy(5, SPAIN, "skin_light", "brown_dark", dict(len=1.0, top=1.6, fade=True), yaw=6,
                beard="short", beard_ramp="brown_dark", brow_lift=-0.2)


def thiagosilva():
    return easy(3, BRAZIL, "skin_tan", "black", dict(len=0.4, top=0.4, fade=True), yaw=-6,
                beard="short", beard_ramp="black", smile=0.3)


def hummels():
    return easy(5, GERMANY, "skin_fair", "brown_dark", SLICK, yaw=10, beard="stubble", brow_lift=-0.2)


def cavani():
    return easy(21, URUGUAY, "skin_light", "black", dict(len=1.4, top=1.6, long=6.0, side=1.3, fringe=-0.4,
                                                         band="white"),
                yaw=-10, beard="full", beard_ramp="black")


def reus():
    return easy(11, GERMANY, "skin_fair", "blond_dark", dict(len=0.8, top=1.8, quiff=1.4, fade=True), yaw=-6,
                look=8, smile=0.4)


def casemiro():
    return easy(5, BRAZIL, "skin_tan", "black", dict(len=0.5, top=0.6, fade=True), yaw=8, beard="short",
                beard_ramp="black", brow_lift=-0.3, brow_slope=0.6)


def immobile():
    return easy(17, ITALY, "skin_light", "brown_dark", SHORT, yaw=-8, beard="full", beard_ramp="brown_dark",
                mouth="smile", smile=0.8)


def vardy():
    return easy(9, ENGLAND, "skin_fair", "brown_mid", dict(len=0.8, top=1.8, quiff=1.2, fade=True), yaw=12,
                look=-8, smirk=0.6)


def aspas():
    return easy(10, SPAIN, "skin_light", "brown_dark", SHORT, yaw=-4, beard="short", beard_ramp="brown_dark",
                smile=0.4)


def mertens():
    return easy(14, BELGIUM, "skin_fair", "blond_dark", dict(len=0.8, top=1.4, fade=True), yaw=6,
                beard="stubble", beard_ramp="blond_dark", mouth="smile", smile=0.9)


def jordialba():
    return easy(18, SPAIN, "skin_light", "brown_dark", dict(len=0.6, top=1.4, quiff=0.8, fade=True), yaw=-10,
                beard="stubble")


def schmeichel():
    return easy(1, DENMARK_GK, "skin_fair", "blond", dict(len=0.6, top=1.0, fade=True), yaw=10,
                beard="short", beard_ramp="blond_dark", gloves=True, brow_lift=-0.2)


FIGS = {"LB_vannistelrooy": vannistelrooy, "LB_raphinha": raphinha, "LB_debruyne": debruyne,
        "LB_lewandowski": lewandowski, "LB_saliba": saliba,
        "LB_valencia": valencia, "LB_florenzi": florenzi, "LB_gabriel": gabriel, "LB_fermin": fermin,
        "LB_martinelli": martinelli, "LB_sane": sane, "LB_casteels": casteels, "LB_ansufati": ansufati,
        "LB_modric": modric, "LB_griezmann": griezmann, "LB_dimaria": dimaria, "LB_busquets": busquets,
        "LB_thiagosilva": thiagosilva, "LB_hummels": hummels, "LB_cavani": cavani, "LB_reus": reus,
        "LB_casemiro": casemiro, "LB_immobile": immobile, "LB_vardy": vardy, "LB_aspas": aspas,
        "LB_mertens": mertens, "LB_jordialba": jordialba, "LB_schmeichel": schmeichel}
