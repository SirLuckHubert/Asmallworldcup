"""CLUB PACK 2 and CLUB PACK 3 figures (31 Oct) - pools A and B, 28 players, posed like the World
Cup pack: the whole player, head to waist, in a pose that is HIS (the celebration or the look
people know him by), rendered with cardfig.

Hubi: "use the things you already have, describe the best pose of every player and add it to the
game, make it like World Cup packs". Same rules as cards17.py / cards_champ.py: LEFT and RIGHT are
the CARD's, arms are written as the camera sees them, (upper-arm direction, forearm direction,
hand[, options]). Kits are shapes and colours only - no crest, no maker, no sponsor.
"""
import cardfig
from cardfig import Fig, Shot
from cards_lb import CITY, CROP, HANG_L, HANG_R, MIAMI, SHORT, SLICK, StripeKit, CLAP_L, CLAP_R

cardfig.RAMPS.setdefault("claret", [(40, 8, 20), (72, 16, 34), (110, 30, 54), (142, 50, 76), (176, 84, 108)])
cardfig.RAMPS.setdefault("pink", [(120, 50, 80), (176, 86, 120), (226, 130, 160), (246, 172, 196), (255, 214, 228)])
cardfig.RAMPS.setdefault("amber", [(96, 56, 4), (156, 98, 10), (214, 146, 24), (244, 186, 56), (255, 222, 120)])

# ------------------------------------------------------------------ kits (no crests, makers or sponsors)
LIVERPOOL = dict(body="red", collar="white", cuff="white", number="white", shorts="red", badge=("white", "red"))
NEWCASTLE = dict(body="white", collar="black", number="black", shorts="black", stripes=("black", 6.2, 0.5),
                 badge=("black", "white"))
FOREST = dict(body="red", collar="white", cuff="white", number="white", shorts="white", badge=("white", "red"))
UNITED = dict(body="red", collar="black", cuff="black", number="white", shorts="white", badge=("yellow", "red"))
EVERTON = dict(body="blue", collar="white", cuff="white", number="white", shorts="white", badge=("white", "blue"))
FULHAM = dict(body="white", collar="black", cuff="black", number="black", shorts="black", badge=("black", "white"))
ALNASSR = dict(body="yellow", collar="blue", cuff="blue", number="blue", shorts="blue", badge=("blue", "yellow"))
BARCA = dict(body="claret", collar="deep_navy", number="yellow", shorts="deep_navy", stripes=("blue", 6.4, 0.5),
             badge=("yellow", "claret"))
SUNDERLAND = dict(body="white", collar="black", number="black", shorts="black", stripes=("red", 6.2, 0.5),
                  badge=("black", "red"))
SPURS = dict(body="white", collar="navy", cuff="navy", number="navy", shorts="navy", badge=("navy", "white"))
WESTHAM = dict(body="claret", sleeve="sky", collar="sky", number="white", shorts="white", badge=("sky", "claret"))
WOLVES = dict(body="amber", collar="black", cuff="black", number="black", shorts="black", badge=("black", "amber"))


def kit(number, base, **more):
    d = dict(base)
    d.update(more)
    d.setdefault("number_txt", str(number))
    return StripeKit(**d)


# ------------------------------------------------------------------ arms used more than once
def mirror(spec):
    """The same arm on the other side of the card (x flipped everywhere)."""
    u, f, hand = spec[:3]
    o = dict(spec[3]) if len(spec) > 3 else {}
    fl = lambda v: (-v[0], v[1], v[2])
    for k in ("dir", "face"):
        if k in o:
            o[k] = fl(o[k])
    return (fl(u), fl(f), hand, o) if o else (fl(u), fl(f), hand)


POINT_LENS_R = ((0.12, -0.48, 0.87), (-0.22, 0.30, 0.93), "point", dict(dir=(-0.68, 0.40, 0.61), face=(0.3, 0.4, 0.86)))
POINT_LENS_L = mirror(POINT_LENS_R)
# a finger up beside his head (elbow out and forward, so the hand stays on the card)
POINT_UP_R = ((0.62, 0.0, 0.78), (-0.25, 0.80, 0.55), "point", dict(dir=(0.0, 1.0, 0.05), face=(0, 0, 1)))
POINT_UP_L = mirror(POINT_UP_R)
POINT_AWAY_L = ((-0.86, 0.22, 0.46), (-0.82, 0.32, 0.47), "point", dict(dir=(-0.80, 0.34, 0.50), face=(0, 0.6, 0.8)))
HIP_L = ((-0.55, -0.80, -0.10), (0.60, -0.70, 0.40), "relaxed")             # hands on hips
HIP_R = mirror(HIP_L)
FIST_CHEST_L = ((-0.22, -0.82, 0.53), (0.55, 0.62, 0.56), "fist")
FIST_CHEST_R = mirror(FIST_CHEST_L)
FIST_LOW_L = ((-0.40, -0.90, 0.12), (-0.30, -0.80, 0.52), "fist")           # roaring, fists down
FIST_LOW_R = mirror(FIST_LOW_L)
FLEX_L = ((-0.72, -0.05, 0.69), (0.15, 0.85, 0.50), "fist")                # biceps up
FLEX_R = mirror(FLEX_L)
WIDE_UP_L = ((-0.90, 0.40, 0.15), (-0.82, 0.55, 0.15), "open")             # arms flung wide and up
WIDE_UP_R = mirror(WIDE_UP_L)
RUN_FWD_L = ((-0.30, -0.85, 0.43), (0.40, 0.55, 0.73), "fist")             # sprinting: this one forward...
RUN_BACK_R = ((0.28, -0.70, -0.66), (0.10, -0.95, -0.30), "fist")          # ...this one driving back
EAR_L = ((-0.78, 0.33, 0.46), (0.91, 0.268, -0.311), "flat", dict(dir=(0.55, 0.8, -0.2), face=(0.3, 0, 0.95)))
EAR_R = mirror(EAR_L)


# ================================================================== CLUB PACK 2 - pool A
def salah():
    # arms flung wide to the crowd, the big grin
    f = Fig(skin="skin_tan", hair="black", iris="iris_brown", beard="full", beard_ramp="black", lip="lip_dark",
            hair_cfg=dict(len=1.6, top=2.6, curl=1.4, side=1.2, fade=False), kit=kit(11, LIVERPOOL),
            torso=(0, 6, 0), shrug=(3.0, 3.0), head=(-2, 10, 4), eye_open=0.6,
            mouth="smile", mouth_w=3.0, mouth_h=1.1, smile=1.0, snarl=1.0, left=WIDE_UP_L, right=WIDE_UP_R)
    f.folds = (((-14, -11), (-4, -27), 0.5, 1.3), ((14, -11), (4, -27), 0.5, 1.3))
    return f, Shot(top_y=36.0, centre_x=0.0)


def haaland():
    # the meditation: eyes shut, hands out at his waist, palms up, perfectly calm
    f = Fig(skin="skin_fair", hair="blond", hair_side="blond_dark", brow="blond_dark", iris="iris_blue",
            hair_cfg=dict(len=1.2, top=1.4, long=1.0, bun=True, side=1.05), kit=kit(9, CITY),
            torso=(0, 0, 0), head=(0, 4, 0), eye_open=0.0, brow_lift=0.1, mouth="closed", mouth_w=2.2,
            smile=0.25, jaw_w=5.9,
            left=((-0.62, -0.75, 0.22), (-0.30, 0.10, 0.95), "open", dict(dir=(-0.25, 0.15, 0.95), face=(0, 1, 0))),
            right=((0.62, -0.75, 0.22), (0.30, 0.10, 0.95), "open", dict(dir=(0.25, 0.15, 0.95), face=(0, 1, 0))))
    return f, Shot(top_y=35.5, centre_x=0.0)


def rodri():
    # arms folded, the professor: a small knowing smile
    f = Fig(skin="skin_light", hair="brown_dark", iris="iris_brown", beard="stubble", beard_ramp="brown_dark",
            hair_cfg=dict(len=0.8, top=1.4, quiff=0.6, fade=True), kit=kit(16, CITY),
            torso=(-6, 0, 0), shrug=(2.0, 2.0), head=(-8, 2, 0), mouth="closed", mouth_w=2.1, smirk=0.4,
            left=((-0.25, -0.90, 0.36), (0.95, 0.18, 0.25), "relaxed"),
            right=((0.25, -0.88, 0.40), (-0.95, 0.08, 0.30), "relaxed"),
            order=("body", "head", "right", "left"))
    return f, Shot(top_y=35.5, centre_x=-0.5)


def isak():
    # pointing both fingers at you, a cool half smile
    f = Fig(skin="skin_brown", hair="black", iris="iris_brown", lip="lip_dark", hair_cfg=dict(len=0.9, top=1.6, fade=True),
            kit=kit(14, NEWCASTLE), torso=(4, 0, 0), head=(2, 4, 0), eye_open=0.85, mouth="closed", mouth_w=2.2,
            smirk=0.4, smile=0.4, left=POINT_LENS_L, right=POINT_LENS_R, order=("body", "head", "left", "right"))
    return f, Shot(top_y=35.5, centre_x=0.0)


# ================================================================== CLUB PACK 2 - pool B
def hudsonodoi():
    # one finger to the sky, smiling
    f = Fig(skin="skin_dark", hair="black", iris="iris_brown", lip="lip_dark", hair_cfg=CROP, kit=kit(14, FOREST),
            torso=(-6, 2, 0), shrug=(0.0, 4.0), head=(-4, 10, 0), mouth="smile", mouth_w=2.8, mouth_h=1.0,
            smile=1.0, snarl=1.0, eye_open=0.8, left=HANG_L, right=POINT_UP_R)
    return f, Shot(top_y=36.0, centre_x=-0.5)


def mainoo():
    # a hand up to the crowd, calm and young
    f = Fig(skin="skin_dark", hair="black", iris="iris_brown", lip="lip_dark", hair_cfg=dict(len=0.8, top=1.4, fade=True),
            kit=kit(37, UNITED), torso=(8, 0, 0), shrug=(0.0, 4.0), head=(4, 4, 0), mouth="closed", mouth_w=2.2,
            smile=0.6, left=HANG_L,
            right=((0.62, 0.0, 0.78), (-0.20, 0.82, 0.54), "open", dict(dir=(0.0, 1.0, 0.1), face=(0, 0, 1))))
    return f, Shot(top_y=36.0, centre_x=0.5)


def beto():
    # roaring, fists clenched down by his sides
    f = Fig(skin="skin_dark", hair="black", iris="iris_brown", beard="short", lip="lip_dark",
            hair_cfg=dict(len=0.3, top=0.2, fade=True), kit=kit(9, EVERTON), torso=(0, 6, 0), shrug=(4.0, 4.0),
            head=(0, 14, 0), eye_open=0.55, brow_lift=-0.4, brow_slope=0.9, mouth="smile", mouth_w=3.0, mouth_h=1.3,
            smile=0.6, snarl=1.0, left=FIST_LOW_L, right=FIST_LOW_R)
    return f, Shot(top_y=36.0, centre_x=0.0)


def jimenez():
    # the head guard, hair tied back, both hands up framing his face
    f = Fig(skin="skin_tan", hair="black", iris="iris_brown", beard="full", beard_ramp="black",
            hair_cfg=dict(len=1.0, top=1.6, long=1.4, bun=True, band="charcoal"), kit=kit(7, FULHAM),
            torso=(-8, 0, 0), head=(-10, 4, 0), eye_open=0.8, mouth="closed", mouth_w=2.3, smile=0.5,
            left=((-0.20, -0.65, 0.73), (0.35, 0.936, 0.02), "flat", dict(dir=(0.15, 0.97, -0.1), face=(0.2, 0, 0.98))),
            right=((0.20, -0.65, 0.73), (-0.35, 0.936, 0.02), "flat", dict(dir=(-0.15, 0.97, -0.1), face=(-0.2, 0, 0.98))),
            order=("body", "head", "left", "right"))
    return f, Shot(top_y=35.5, centre_x=-0.5)


def elanga():
    # flat out: sprinting at you, arms pumping
    f = Fig(skin="skin_dark", hair="black", iris="iris_brown", lip="lip_dark", hair_cfg=CROP, kit=kit(21, FOREST),
            torso=(-14, -6, 2), shrug=(2.0, 0.0), head=(-8, 2, 0), neck_fwd=2.0, eye_open=0.85, brow_lift=-0.35,
            brow_slope=0.6, mouth="closed", mouth_w=2.0, left=RUN_FWD_L, right=RUN_BACK_R,
            order=("right", "body", "head", "left"))
    return f, Shot(top_y=35.5, centre_x=-1.0)


def szoboszlai():
    # hands on hips, hair slicked back, a hard stare
    f = Fig(skin="skin_fair", hair="blond_dark", iris="iris_blue", hair_cfg=dict(len=0.7, top=2.2, quiff=1.6, fade=True),
            kit=kit(8, LIVERPOOL), torso=(-8, 0, 0), head=(-6, 2, 0), brow_lift=-0.35, brow_slope=0.6,
            mouth="closed", mouth_w=2.0, left=HIP_L, right=HIP_R)
    return f, Shot(top_y=35.5, centre_x=-0.5)


def gibbswhite():
    # the captain, pointing out to the stand and shouting
    f = Fig(skin="skin_fair", hair="brown_mid", iris="iris_blue", beard="stubble", beard_ramp="brown_mid",
            hair_cfg=dict(len=0.8, top=1.4, fade=True), kit=kit(10, FOREST), armband=("right", "yellow"),
            torso=(-10, 2, 0), shrug=(4.0, 0.0), head=(-16, 6, -2), eye_open=0.7, brow_lift=-0.2,
            mouth="smile", mouth_w=2.9, mouth_h=1.2, smile=0.7, snarl=1.0, left=POINT_AWAY_L, right=HANG_R)
    return f, Shot(top_y=35.5, centre_x=-2.0)


def garnacho():
    # chest out, arms swept down and back, chin up - the jump-and-land celebration
    f = Fig(skin="skin_light", hair="brown_dark", iris="iris_brown",
            hair_cfg=dict(len=1.1, top=2.0, curl=0.6, fade=True), kit=kit(17, UNITED),
            torso=(0, 8, 0), shrug=(-1.0, -1.0), head=(0, 16, 0), eye_open=0.8, brow_lift=-0.2,
            mouth="closed", mouth_w=2.2,
            left=((-0.50, -0.80, -0.32), (-0.45, -0.78, -0.43), "open"),
            right=((0.50, -0.80, -0.32), (0.45, -0.78, -0.43), "open"),
            order=("left", "right", "body", "head"))
    return f, Shot(top_y=36.0, centre_x=0.0)


def foden():
    # a finger to his lips: shh
    f = Fig(skin="skin_fair", hair="brown_mid", iris="iris_blue", hair_cfg=dict(len=0.6, top=1.0, fade=True),
            kit=kit(47, CITY), torso=(6, 0, 0), head=(4, 2, 0), eye_open=0.8, brow_lift=0.1, mouth="closed",
            mouth_w=1.8, left=HANG_L,
            right=((-0.05, -0.55, 0.83), (-0.45, 0.82, -0.35), "point", dict(dir=(0.0, 1.0, 0.05), face=(0, 0, 1))),
            order=("body", "head", "left", "right"))
    return f, Shot(top_y=35.5, centre_x=0.5)


# ================================================================== CLUB PACK 3 - pool A
def messi():
    # both fingers to the sky, eyes up: for his gran
    f = Fig(skin="skin_light", hair="brown", iris="iris_brown", beard="full", beard_ramp="brown",
            hair_cfg=dict(len=1.2, top=1.6, side=1.1), kit=kit(10, MIAMI),
            torso=(0, 4, 0), shrug=(4.0, 4.0), head=(0, 20, 0), gaze=(0.0, 0.25), eye_open=0.85,
            mouth="closed", mouth_w=2.2, smile=0.5, left=POINT_UP_L, right=POINT_UP_R)
    f.folds = (((-14, -11), (-4, -27), 0.5, 1.3), ((14, -11), (4, -27), 0.5, 1.3))
    return f, Shot(top_y=37.0, centre_x=0.0)


def ronaldo():
    # the landing: chest out, arms out and down, palms back, chin up
    f = Fig(skin="skin_light", hair="black", iris="iris_brown", hair_cfg=dict(len=0.6, top=2.0, quiff=1.6, fade=True),
            kit=kit(7, ALNASSR), torso=(0, 6, 0), shrug=(-1.0, -1.0), head=(0, 12, 0), eye_open=0.75,
            brow_lift=-0.3, brow_slope=0.5, mouth="closed", mouth_w=2.2, jaw_w=5.8,
            left=((-0.72, -0.68, -0.10), (-0.70, -0.68, 0.05), "open"),
            right=((0.72, -0.68, -0.10), (0.70, -0.68, 0.05), "open"))
    return f, Shot(top_y=35.5, centre_x=0.0)


def yamal():
    # the hand sign at his chest, a calm look
    f = Fig(skin="skin_brown", hair="black", iris="iris_brown", lip="lip_dark",
            hair_cfg=dict(len=1.1, top=2.0, curl=0.9, fade=True), kit=kit(19, BARCA),
            torso=(-6, 2, 0), shrug=(2.0, 2.0), head=(-6, 6, 0), eye_open=0.85, mouth="closed", mouth_w=2.0,
            smirk=0.3,
            left=((-0.25, -0.80, 0.55), (0.75, 0.50, 0.43), "point", dict(dir=(0.35, 0.25, 0.90), face=(0, 1, 0))),
            right=((0.25, -0.80, 0.55), (-0.75, 0.50, 0.43), "point", dict(dir=(-0.35, 0.25, 0.90), face=(0, 1, 0))),
            order=("body", "head", "left", "right"))
    return f, Shot(top_y=35.5, centre_x=-0.5)


def suarez():
    # kissing his wrist
    f = Fig(skin="skin_light", hair="black", iris="iris_brown", beard="stubble", beard_ramp="black",
            hair_cfg=dict(len=1.1, top=1.8, side=1.1), kit=kit(9, MIAMI), torso=(10, 0, 0), head=(14, -4, 0),
            eye_open=0.3, mouth="purse", mouth_w=1.6, left=HANG_L,
            right=((0.20, -0.75, 0.63), (-0.62, 0.78, 0.08), "fist"),
            order=("body", "head", "left", "right"))
    return f, Shot(top_y=35.5, centre_x=0.5)


def bellingham():
    # arms flung wide and up, roaring at the stand
    f = Fig(skin="skin_tan", hair="black", iris="iris_brown", hair_cfg=dict(len=0.8, top=1.6, fade=True),
            kit=kit(7, SUNDERLAND), torso=(0, 8, 0), shrug=(4.0, 4.0), head=(0, 16, 0), eye_open=0.6,
            brow_lift=-0.2, mouth="smile", mouth_w=3.0, mouth_h=1.3, smile=0.8, snarl=1.0,
            left=WIDE_UP_L, right=WIDE_UP_R)
    f.folds = (((-14, -11), (-4, -27), 0.5, 1.3), ((14, -11), (4, -27), 0.5, 1.3))
    return f, Shot(top_y=36.0, centre_x=0.0)


def son():
    # the camera: both hands framing a photo in front of his face, a wide smile behind it
    f = Fig(skin="skin_light", hair="black", iris="iris_brown", hair_cfg=dict(len=0.9, top=1.6, fringe=1.4),
            kit=kit(7, SPURS), torso=(-4, 2, 0), head=(-4, 4, 0), eye_open=0.6, mouth="smile", mouth_w=2.9,
            mouth_h=1.0, smile=1.0, snarl=1.0,
            # two corners of a frame: the left finger up beside his eye, the right one pointing across under it
            left=((-0.25, -0.25, 0.94), (0.35, 0.93, 0.10), "point", dict(dir=(0.05, 1.0, 0.1), face=(0, 0, 1))),
            right=((0.25, -0.35, 0.90), (-0.40, 0.85, 0.20), "point", dict(dir=(-1.0, 0.0, 0.1), face=(0, 1, 0))),
            order=("body", "head", "left", "right"))
    return f, Shot(top_y=35.5, centre_x=-0.5)


# ================================================================== CLUB PACK 3 - pool B
def kudus():
    # hands on hips, chest out, eyebrows up: cool as you like
    f = Fig(skin="skin_dark", hair="black", iris="iris_brown", beard="short", lip="lip_dark", hair_cfg=CROP,
            kit=kit(14, WESTHAM), torso=(6, 4, 0), head=(4, 8, 4), brow_lift=0.35, mouth="closed", mouth_w=2.2,
            smirk=0.6, left=HIP_L, right=HIP_R)
    return f, Shot(top_y=35.5, centre_x=0.5)


def sarabia():
    # blowing a kiss to the crowd
    f = Fig(skin="skin_light", hair="brown_dark", iris="iris_brown", beard="short", beard_ramp="brown_dark",
            hair_cfg=dict(len=0.8, top=1.4, fade=True), kit=kit(21, WOLVES), torso=(-8, 0, 0), head=(-12, 4, 0),
            eye_open=0.6, mouth="purse", mouth_w=1.6, left=HANG_L,
            right=((0.22, -0.72, 0.66), (-0.42, 0.88, 0.20), "flat", dict(dir=(-0.1, 0.98, 0.2), face=(-0.2, 0, 0.98))),
            order=("body", "head", "left", "right"))
    return f, Shot(top_y=35.5, centre_x=-0.5)


def paqueta():
    # dancing: one arm up, the other swinging low, head tilted, a big smile
    f = Fig(skin="skin_tan", hair="black", iris="iris_brown", beard="stubble", beard_ramp="black",
            hair_cfg=dict(len=0.8, top=1.4, fade=True), kit=kit(10, WESTHAM), torso=(10, 4, 4), shrug=(0.0, 5.0),
            head=(8, 6, 10), eye_open=0.6, mouth="smile", mouth_w=2.9, mouth_h=1.0, smile=1.0, snarl=1.0,
            left=((-0.62, -0.75, 0.22), (-0.55, -0.45, 0.70), "open"),
            right=((0.58, 0.15, 0.80), (0.0, 0.85, 0.52), "open"))
    return f, Shot(top_y=36.0, centre_x=0.5)


def aitnouri():
    # flexing both arms, grinning
    f = Fig(skin="skin_tan", hair="black", iris="iris_brown", hair_cfg=dict(len=1.3, top=2.4, curl=1.2, fade=True),
            kit=kit(3, WOLVES), torso=(0, 4, 0), shrug=(5.0, 5.0), head=(0, 6, 0), eye_open=0.7,
            mouth="smile", mouth_w=2.9, mouth_h=1.0, smile=1.0, snarl=1.0, left=FLEX_L, right=FLEX_R)
    f.folds = (((-14, -11), (-4, -27), 0.5, 1.3), ((14, -11), (4, -27), 0.5, 1.3))
    return f, Shot(top_y=36.0, centre_x=0.0)


def romero():
    # the warrior: roaring, fists down, chest out
    f = Fig(skin="skin_light", hair="black", iris="iris_brown", beard="stubble", beard_ramp="black",
            hair_cfg=dict(len=0.8, top=1.6, fade=True), kit=kit(17, SPURS), torso=(4, 8, 0), shrug=(4.0, 4.0),
            head=(4, 14, 0), eye_open=0.5, brow_lift=-0.45, brow_slope=1.0, mouth="grit", mouth_w=2.7, mouth_h=1.05,
            snarl=1.0, left=FIST_LOW_L, right=FIST_LOW_R)
    return f, Shot(top_y=36.0, centre_x=0.0)


def pedri():
    # applauding, a shy smile
    f = Fig(skin="skin_light", hair="black", iris="iris_brown", hair_cfg=dict(len=1.0, top=1.8, side=1.05),
            kit=kit(8, BARCA), torso=(8, 0, 0), head=(10, 0, -2), mouth="closed", mouth_w=2.1, smile=0.6,
            left=CLAP_L, right=CLAP_R, order=("body", "head", "left", "right"))
    return f, Shot(top_y=35.5, centre_x=0.5)


def raphinha():
    # both hands cupped behind his ears: I can't hear you
    f = Fig(skin="skin_tan", hair="black", iris="iris_brown", hair_cfg=dict(len=0.7, top=1.4, fade=True),
            kit=kit(11, BARCA), torso=(0, 4, 0), shrug=(4.0, 4.0), head=(0, 8, 0), eye_open=0.7,
            mouth="smile", mouth_w=2.8, mouth_h=1.0, smile=0.9, snarl=1.0, left=EAR_L, right=EAR_R,
            order=("body", "head", "left", "right"))
    return f, Shot(top_y=36.0, centre_x=0.0)


def depaul():
    # thumping his chest with a fist, shouting
    f = Fig(skin="skin_light", hair="brown_dark", iris="iris_brown", beard="short", beard_ramp="brown_dark",
            hair_cfg=dict(len=0.7, top=1.8, quiff=1.2, fade=True), kit=kit(7, MIAMI), torso=(-6, 4, 0),
            head=(-8, 10, 0), eye_open=0.6, brow_lift=-0.3, mouth="smile", mouth_w=3.0, mouth_h=1.2, smile=0.7,
            snarl=1.0, left=((-0.25, -0.85, 0.46), (0.92, 0.36, 0.15), "fist"), right=HANG_R,
            order=("body", "head", "right", "left"))
    return f, Shot(top_y=35.5, centre_x=-0.5)


def bowen():
    # pointing at you, a fist clenched low
    f = Fig(skin="skin_fair", hair="brown_mid", iris="iris_blue", beard="stubble", beard_ramp="brown_mid",
            hair_cfg=dict(len=0.6, top=1.2, fade=True), kit=kit(20, WESTHAM), torso=(-6, 0, 0), head=(-4, 4, 0),
            eye_open=0.75, mouth="smile", mouth_w=2.8, mouth_h=1.0, smile=1.0, snarl=1.0,
            left=FIST_LOW_L, right=POINT_LENS_R, order=("body", "head", "left", "right"))
    return f, Shot(top_y=35.5, centre_x=-0.5)


FIGS = {
    # Club Pack 2
    "LIV_salah": salah, "MCI_haaland": haaland, "MCI_rodri": rodri, "NEW_isak": isak,
    "NOT_hudsonodoi": hudsonodoi, "MUN_mainoo": mainoo, "EVE_beto": beto, "FUL_jimenez": jimenez,
    "NOT_elanga": elanga, "LIV_szoboszlai": szoboszlai, "NOT_gibbswhite": gibbswhite, "MUN_garnacho": garnacho,
    "MCI_foden": foden,
    # Club Pack 3
    "INT_messi": messi, "ALN_ronaldo": ronaldo, "BAR_yamal": yamal, "INT_suarez": suarez,
    "SUN_bellingham": bellingham, "TOT_son": son, "WES_kudus": kudus, "WOL_sarabia": sarabia,
    "WES_paqueta": paqueta, "WOL_aitnouri": aitnouri, "TOT_romero": romero, "BAR_pedri": pedri,
    "BAR_raphinha": raphinha, "INT_depaul": depaul, "WES_bowen": bowen,
}
