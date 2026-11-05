"""CHAMPION DRAFT A figures - the twelve players on the gold Champions card, posed with cardfig.

Same rules as cards17.py / cards_lb.py: LEFT and RIGHT are the CARD's, arms are written as the
camera sees them, (upper-arm direction, forearm direction, hand[, options]). Kits are shapes and
colours only - no crest, no maker, no sponsor. Guehi and Semenyo wear Man City's sky blue
(Guehi No. 15, Semenyo No. 42 - their City numbers).
"""
import cardfig
from cardfig import Fig, Shot
from cards_lb import CHELSEA, CITY, CLAP_L, CLAP_R, CROP, HANG_L, HANG_R, SHORT, SLICK, StripeKit

cardfig.RAMPS.setdefault("claret", [(40, 8, 20), (72, 16, 34), (110, 30, 54), (142, 50, 76), (176, 84, 108)])

ARSENAL = dict(body="red", sleeve="white", collar="white", cuff="red", number="white", shorts="white",
               badge=("gold", "red"))
VILLA_GK = dict(body="yellow", collar="black", cuff="black", number="black", long_sleeve=True,
                shorts="black", badge=("black", "yellow"))
BOURNEMOUTH = dict(body="red", collar="black", number="white", shorts="black", stripes=("black", 5.6, 0.5),
                   badge=("black", "red"))
BRENTFORD = dict(body="red", collar="black", number="black", shorts="black", stripes=("white", 5.6, 0.5),
                 badge=("white", "red"))

FISTS_CHEST = (((-0.22, -0.82, 0.53), (0.55, 0.62, 0.56), "fist"),
               ((0.22, -0.82, 0.53), (-0.55, 0.62, 0.56), "fist"))
FISTS_UP = (((-0.55, 0.31, -0.77), (0.42, 0.64, 0.64), "fist"),
            ((0.55, 0.31, -0.77), (-0.42, 0.64, 0.64), "fist"))
POINT_L = ((-0.86, 0.22, 0.46), (-0.82, 0.32, 0.47), "point", dict(dir=(-0.80, 0.34, 0.50), face=(0, 0.6, 0.8)))
POINT_R = ((0.86, 0.22, 0.46), (0.82, 0.32, 0.47), "point", dict(dir=(0.80, 0.34, 0.50), face=(0, 0.6, 0.8)))
GLOVE = dict(glove="charcoal")


def kit(number, base, **more):
    d = dict(base)
    d.update(more)
    d.setdefault("number_txt", str(number))
    return StripeKit(**d)


# ================================================================== POOL A
# 30 Oct: every pose re-done from Hubi's 13 reference pictures (the real cards' poses - pose only:
# our own figures, kits as shapes and colours, no frames or crests copied).
FISTS_TIGHT = (((-0.20, -0.86, 0.47), (0.62, 0.58, 0.53), "fist"),
               ((0.20, -0.86, 0.47), (-0.62, 0.58, 0.53), "fist"))


def guehi():
    # the power pose: chest a touch angled, both elbows bent, fists clenched at chest height,
    # an intense stare straight down the lens
    f = Fig(skin="skin_dark", hair="black", iris="iris_brown", lip="lip_dark", hair_cfg=CROP,
            kit=kit(15, CITY), torso=(-8, 0, 0), shrug=(3.0, 3.0), head=(-4, 2, 0),
            eye_open=0.75, brow_lift=-0.45, brow_slope=0.9, mouth="grit", mouth_w=2.6, mouth_h=1.0,
            snarl=1.0, jaw_w=5.9, left=FISTS_CHEST[0], right=FISTS_CHEST[1],
            order=("body", "head", "left", "right"))
    f.folds = (((-12, -12), (-3, -28), 0.5, 1.4), ((12, -12), (3, -28), 0.5, 1.4))
    return f, Shot(top_y=35.5, centre_x=-0.5)


def saka():
    # back to the camera - the 7 and the armband - looking back over his shoulder with a big
    # smile, one arm swinging out wide
    f = Fig(light="right", skin="skin_dark", hair="black", iris="iris_brown", lip="lip_dark",
            hair_cfg=dict(len=0.7, top=1.0, fade=True),
            kit=kit(7, ARSENAL, back=True, name_txt="SAKA"), armband=("left", "yellow"),
            torso=(-150, 0, 0), head=(-62, 4, 3), neck_dx=0.0, gaze=(-0.25, 0.0),
            eye_open=0.75, mouth="smile", mouth_w=2.9, mouth_h=1.0, smile=1.0, snarl=1.0,
            left=((-0.70, -0.66, -0.25), (-0.80, -0.50, 0.30), "relaxed"),
            right=((0.16, -0.98, 0.05), (0.10, -0.97, 0.20), "relaxed"),
            order=("right", "body", "left", "head"))
    return f, Shot(top_y=35.5, centre_x=1.0)


def martinez():
    # the keeper standing tall and square, headband on, head tilted, eyes off to the side,
    # lips pressed into a smug little smile
    f = Fig(skin="skin_light", hair="brown_dark", iris="iris_brown", beard="short", beard_ramp="brown_dark",
            hair_cfg=dict(len=0.8, top=1.4, fade=True, band="sky"), kit=kit(23, VILLA_GK),
            torso=(4, 0, 0), head=(8, 0, 5), gaze=(0.35, 0.05), eye_open=0.8, brow_lift=-0.1,
            mouth="closed", mouth_w=2.2, smirk=0.55,
            left=HANG_L[:3] + (GLOVE,), right=HANG_R[:3] + (GLOVE,))
    return f, Shot(top_y=35.5, centre_x=0.5)


def gyokeres():
    # full celebration: both fists clenched in front of his chest, elbows tucked, leaning in at
    # the lens with his mouth wide open
    f = Fig(skin="skin_fair", hair="brown_mid", iris="iris_blue", beard="stubble", beard_ramp="brown_mid",
            hair_cfg=dict(len=0.9, top=1.6, fade=True), kit=kit(14, ARSENAL), torso=(2, -7, 0), shrug=(4.0, 4.0),
            head=(2, 6, 0), neck_fwd=2.4, eye_open=0.6, brow_lift=-0.3, brow_slope=0.7,
            mouth="smile", mouth_w=3.0, mouth_h=1.3, smile=0.9, snarl=1.0, jaw_w=5.8,
            left=FISTS_TIGHT[0], right=FISTS_TIGHT[1], order=("body", "head", "left", "right"))
    f.folds = (((-12, -10), (12, -10), 0.4, 1.5), ((-10, -26), (8, -30), 0.45, 1.6))
    return f, Shot(top_y=36.0, centre_x=0.0)


def caicedo():
    # the calm one: nearly square, a slight turn, arms down, a straight serious face at you
    f = Fig(skin="skin_brown", hair="black", iris="iris_brown", lip="lip_dark", hair_cfg=SHORT,
            kit=kit(25, CHELSEA), torso=(-6, 0, 0), head=(-3, 0, 0), brow_lift=-0.2, brow_slope=0.3,
            mouth="closed", mouth_w=2.1, jaw_w=5.7, left=HANG_L, right=HANG_R)
    return f, Shot(top_y=35.5, centre_x=-0.5)


def joaopedro():
    # three-quarter turn, shoulders angled away, head snapped round to look off the card's right,
    # mouth just open - alert, tracking the ball
    f = Fig(light="right", skin="skin_brown", hair="black", iris="iris_brown", lip="lip_dark",
            hair_cfg=dict(len=1.4, top=2.6, curl=1.3, long=0.6, fade=True),
            kit=kit(20, CHELSEA), torso=(-18, 0, 0), head=(30, 2, 0), gaze=(0.35, 0.0),
            eye_open=1.0, brow_lift=0.15, mouth="smile", mouth_w=2.0, mouth_h=0.9, smile=0.1, snarl=1.0,
            left=HANG_L, right=((0.20, -0.96, 0.10), (0.10, -0.95, 0.30), "relaxed"),
            pecs=0.2)                 # Hubi: turned and side-lit, the chest muscles read as a bust - flattened
    f.folds = (((-10, -16), (2, -30), 0.5, 1.5), ((8, -14), (-2, -34), 0.45, 1.6))   # a shirt crease instead
    return f, Shot(top_y=35.5, centre_x=1.0)


def palmer():
    # running at the camera on an angle, leaning in, one arm pumping forward, the other driving
    # back, eyes locked ahead
    f = Fig(skin="skin_fair", hair="brown_mid", iris="iris_blue",
            hair_cfg=dict(len=0.8, top=2.0, quiff=1.3, fringe=0.4, fade=True), kit=kit(10, CHELSEA),
            torso=(-14, -6, 2), shrug=(2.0, 0.0), head=(-8, 2, 0), neck_fwd=2.0, eye_open=0.85,
            brow_lift=-0.35, brow_slope=0.6, mouth="closed", mouth_w=2.0,
            left=((-0.30, -0.85, 0.43), (0.40, 0.55, 0.73), "fist"),
            right=((0.28, -0.70, -0.66), (0.10, -0.95, -0.30), "fist"),
            order=("right", "body", "head", "left"))
    f.folds = (((-10, -14), (4, -30), 0.45, 1.5),)
    return f, Shot(top_y=35.5, centre_x=-1.0)


# ================================================================== POOL B
def enzo():
    # caught mid-run, body twisted three-quarters to the card's left, an arm bent and pumping,
    # head the same way, lips parted
    f = Fig(skin="skin_light", hair="brown_dark", iris="iris_brown", beard="stubble", beard_ramp="brown_dark",
            hair_cfg=dict(len=0.8, top=1.6, quiff=0.8, fade=True), kit=kit(8, CHELSEA),
            torso=(-26, -3, -2), head=(-34, 0, 0), gaze=(-0.3, 0.0), brow_lift=-0.2, brow_slope=0.4,
            mouth="smile", mouth_w=1.9, mouth_h=0.9, smile=0.0, snarl=1.0,
            left=((-0.30, -0.90, -0.30), (-0.15, -0.95, 0.27), "fist"),
            right=((0.30, -0.90, 0.32), (-0.55, -0.05, 0.83), "fist"),
            order=("left", "body", "head", "right"))
    return f, Shot(top_y=35.5, centre_x=-2.0)


def semenyo():
    # laughing, head tipped back, eyes squeezed nearly shut, a hand on his chest pointing at himself
    f = Fig(skin="skin_dark", hair="black", iris="iris_brown", lip="lip_dark", hair_cfg=CROP,
            kit=kit(42, CITY), torso=(-8, 3, 0), head=(-10, 16, -4), neck_fwd=0.5,
            eye_open=0.12, brow_lift=0.2, brow_slope=-0.3, mouth="smile", mouth_w=3.0, mouth_h=1.2,
            smile=1.0, snarl=1.0,
            left=((-0.22, -0.88, 0.42), (0.80, 0.52, 0.30), "point",
                  dict(dir=(0.35, 0.40, -0.85), face=(0, 0.6, 0.8))),
            right=HANG_R, order=("body", "head", "right", "left"))
    return f, Shot(top_y=36.0, centre_x=-1.0)


def odegaard():
    # the captain square to the lens, arms down, a wide toothy smile straight at you
    f = Fig(skin="skin_fair", hair="brown_mid", iris="iris_blue",
            hair_cfg=dict(len=1.2, top=1.8, quiff=1.2, side=1.05), kit=kit(8, ARSENAL),
            armband=("right", "yellow"), torso=(0, 0, 0), head=(0, 1, 0), eye_open=0.8,
            mouth="smile", mouth_w=2.9, mouth_h=1.0, smile=1.0, snarl=1.0, left=HANG_L, right=HANG_R)
    return f, Shot(top_y=35.5, centre_x=0.0)


def kluivert():
    # a head-and-shoulders portrait, a slight turn, eyes off to the side, calm, no smile
    f = Fig(light="right", skin="skin_brown", hair="black", iris="iris_brown", lip="lip_dark",
            hair_cfg=dict(len=1.3, top=2.2, curl=1.1, fade=True), kit=kit(19, BOURNEMOUTH),
            torso=(10, 0, 0), head=(14, 0, 0), gaze=(0.35, 0.0), brow_lift=-0.05,
            mouth="closed", mouth_w=2.1, left=HANG_L, right=HANG_R)
    return f, Shot(top_y=35.5, centre_x=1.0)


def evanilson():
    # hand on heart: his right hand pressed flat over the badge, a calm closed smile, eyes just off
    f = Fig(skin="skin_brown", hair="black", iris="iris_brown", beard="stubble", lip="lip_dark",
            hair_cfg=dict(len=0.7, top=1.2, fade=True), kit=kit(9, BOURNEMOUTH), torso=(-4, 0, 0),
            head=(-6, 0, -4), gaze=(-0.2, 0.05), mouth="closed", mouth_w=2.3, smile=0.7,
            left=((-0.25, -0.85, 0.46), (0.94, 0.34, 0.05), "flat", dict(dir=(0.62, 0.78, 0.08), face=(0, 0, 1))),
            right=HANG_R, order=("body", "head", "right", "left"))
    return f, Shot(top_y=35.5, centre_x=0.0)


def wissa():
    # walking out, back to the camera: the name and the 11, arms down, head facing away
    f = Fig(light="right", skin="skin_dark", hair="black", iris="iris_brown", beard="short", lip="lip_dark",
            hair_cfg=CROP, kit=kit(11, BRENTFORD, back=True, name_txt="WISSA"),
            torso=(180, 0, 0), head=(172, 0, 0), left=HANG_L, right=HANG_R,
            order=("left", "right", "body", "head"))
    return f, Shot(top_y=35.5, centre_x=0.0)


FIGS = {"CRY_guehi": guehi, "ARS_saka": saka, "AST_martinez": martinez, "ARS_gyokeres": gyokeres,
        "CHE_palmer": palmer, "CHE_caicedo": caicedo, "CHE_joaopedro": joaopedro, "CHE_enzo": enzo, "BOU_semenyo": semenyo,
        "ARS_odegaard": odegaard, "BOU_kluivert": kluivert, "BOU_evanilson": evanilson, "BRE_wissa": wissa}
