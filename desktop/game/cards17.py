"""The 17 draft-card figures, one function each, posed from Hubi's reference pictures.

LEFT and RIGHT are the CARD's, as you look at it. Arms are written as the camera sees them:
(upper-arm direction, forearm direction, hand[, options]); x right, y up, z toward us.
Each player stands at the angle of his own picture. Where the picture shows a club shirt,
he wears his country's - these are World Cup cards.

25 Oct: Messi and Ronaldo re-posed from Hubi's two new pictures (Messi grinning and pointing
at you, Ronaldo smiling in the white away shirt with the armband) for their new cards.
"""
from cardfig import Fig, Kit, Shot

try:                                   # vertical stripes live in cards_lb.py (Limit Breakers)
    from cards_lb import StripeKit
except ImportError:                    # without it Argentina falls back to plain sky blue
    StripeKit = None

# ------------------------------------------------------------------ kits (no real crests or makers)
SPAIN = dict(body="red", sleeve="navy", collar="navy", number="yellow", shorts="navy",
             raglan=True, pinstripe=3.4, badge=("yellow", "red"), piping="yellow")
FRANCE = dict(body="deep_navy", collar="white", collar_w=2.2, number="white", shorts="white",
              pinstripe=3.0, badge=("yellow", "deep_navy"))
PORTUGAL = dict(body="red", collar="green", cuff="green", number="yellow", shorts="green",
                badge=("yellow", "green"))
# white with light-blue brush strokes, a dark collar: the away shirt in Hubi's picture
PORTUGAL_AWAY = dict(body="white", alt="sky", pattern="swirl", collar="deep_navy", cuff="deep_navy",
                     number="deep_navy", shorts="white", badge=("red", "green"))
HOLLAND = dict(body="orange", collar="navy", cuff="navy", number="navy", shorts="orange",
               pinstripe=2.4, badge=("white", "blue"))
HOLLAND_AWAY = dict(body="white", collar="orange", number="navy", sash="orange", cuff="orange",
                    long_sleeve=True, shorts="white", badge=("orange", "white"))
KEEPER = dict(body="charcoal", collar="charcoal", number="white", pattern="zig", long_sleeve=True,
              shorts="charcoal", badge=("yellow", "green"))
JAPAN = dict(body="blue", collar="white", cuff="white", number="white", shorts="blue",
             pinstripe=3.2, badge=("white", "red"))
MOROCCO = dict(body="red", collar="green", cuff="green", number="white", shorts="green",
               badge=("yellow", "green"))
ENGLAND = dict(body="white", collar="navy", cuff="navy", number="red", shorts="navy",
               badge=("navy", "red"))
BRAZIL = dict(body="yellow", collar="green", cuff="green", number="green", shorts="blue",
              badge=("green", "yellow"))
CROATIA = dict(body="red", alt="white", pattern="checks", collar="white", number="navy",
               shorts="white", badge=("navy", "white"))
POLAND = dict(body="white", collar="red", cuff="red", number="red", shorts="red",
              long_sleeve=True, badge=("red", "white"))
ARGENTINA_AWAY = dict(body="deep_navy", alt="blue", pattern="swirl", collar="deep_navy", number="white",
                      shorts="navy", badge=("white", "blue"))
# sky-blue and white stripes, black number: the home shirt
ARGENTINA_HOME = dict(body="white", collar="deep_navy", cuff="sky", number="black", shorts="black",
                      stripes=("sky", 6.4, 0.5), badge=("sky", "white"))

# ------------------------------------------------------------------ hair
SWEPT = dict(top=3.4, top_x=0.8, quiff=2.6, fade=True)
CROP = dict(len=0.5, fringe=2.0, fade=True)                                  # clipped close all over
SHORT = dict(len=0.8, top=1.2, fade=True)                         # short back and sides
CURLS = dict(len=1.3, top=2.4, curl=1.0, fade=True)               # a tall top of curls

HANG_L = ((-0.14, -0.98, 0.06), (-0.05, -0.97, 0.22), "relaxed")
HANG_R = ((0.14, -0.98, 0.06), (0.05, -0.97, 0.22), "relaxed")


def olmo():
    f = Fig(
        skin="skin_fair", hair="blond", hair_side="blond_dark", brow="blond_dark", iris="iris_blue",
        hair_cfg=SWEPT,
        kit=Kit(number_txt="10", **SPAIN),
        torso=(-3, -6, -2), shrug=(3.0, 3.0),
        head=(2, -3, -3), neck_fwd=2.5,
        eye_open=0.62, brow_lift=-0.45, brow_slope=1.0,
        mouth="grit", mouth_w=2.7, mouth_h=1.05, snarl=1.0,
        left=((-0.50, -0.30, 0.81), (0.10, 0.84, 0.54), "fist"),
        right=((0.45, -0.34, 0.83), (-0.26, 0.81, 0.54), "fist"),
        order=("body", "head", "left", "right"),
    )
    # the shirt pulled up and in by two raised arms: creases run from each armpit to the middle
    f.folds = (((-14, -11), (-4, -27), 0.55, 1.3), ((14, -11), (4, -27), 0.55, 1.3),
               ((-15, -24), (-7, -44), 0.5, 1.6), ((15, -24), (7, -44), 0.5, 1.6))
    f.overlap_edge = False            # the approved card, kept pixel for pixel
    return f, Shot(top_y=35.5)


def dembele():
    # head thrown back, eyes shut, shouting; both gloved hands flat on his chest
    f = Fig(
        skin="skin_dark", hair="black", iris="iris_brown", hair_cfg=CROP, beard="stubble", lip="lip_dark",
        kit=Kit(number_txt="7", long_sleeve=True, **FRANCE),
        torso=(-6, 8, 4), head=(-4, 26, -8), neck_fwd=0.0,
        eye_open=0.0, brow_lift=0.15, brow_slope=-0.6,
        mouth="shout", mouth_w=2.7, mouth_h=1.9, jaw_drop=1.8, snarl=1.0,
        left=((-0.25, -0.85, 0.45), (0.85, 0.45, 0.05), "flat", dict(dir=(0.72, 0.68, 0.1), glove="black")),
        right=((0.30, -0.85, 0.40), (-0.85, 0.20, 0.06), "flat", dict(dir=(-0.85, 0.5, 0.1), glove="black")),
        order=("body", "head", "right", "left"),
    )
    f.folds = (((-12, -24), (10, -30), 0.5, 1.5), ((-10, -34), (12, -38), 0.45, 1.6))
    return f, Shot(top_y=35.0, centre_x=-1.0)


def bernardo():
    # turned to the card's right, calm, hands up beside his face mid-clap
    f = Fig(
        light="right",
        skin="skin_light", hair="brown", iris="iris_brown", beard="full",
        hair_cfg=dict(len=1.3, top=2.0, quiff=1.2, long=1.4, side=1.1),
        kit=Kit(number_txt="10", long_sleeve=True, **PORTUGAL),
        torso=(28, 2, 0), head=(36, 2, 2),
        gaze=(0.3, 0.0), mouth="closed", mouth_w=2.3, smile=0.6,
        left=((0.55, -0.45, 0.70), (0.49, 0.75, -0.45), "flat", dict(dir=(0.2, 0.98, 0.0), face=(0.55, 0, 0.83))),
        right=((0.45, -0.55, 0.70), (-0.28, 0.96, 0.0), "flat", dict(dir=(-0.12, 0.99, 0.0), face=(-0.3, 0, 0.95))),
        order=("body", "head", "right", "left"),
    )
    f.folds = (((-6, -14), (8, -24), 0.5, 1.4), ((-10, -26), (6, -36), 0.45, 1.6))
    return f, Shot(top_y=35.5, centre_x=3.0)


def gakpo():
    # standing easy, hands on his hips, looking off to the card's left
    f = Fig(
        skin="skin_tan", hair="black", iris="iris_brown", beard="short",
        hair_cfg=dict(len=0.7, top=0.9, fade=True),
        kit=Kit(number_txt="11", **HOLLAND),
        torso=(-10, 0, 0), head=(-22, 2, 0),
        gaze=(-0.3, 0.0), brow_lift=-0.1, mouth="closed", mouth_w=2.2,
        left=((-0.55, -0.80, -0.10), (0.60, -0.70, 0.40), "relaxed"),
        right=((0.55, -0.80, -0.10), (-0.60, -0.70, 0.40), "relaxed"),
    )
    f.folds = (((-9, -20), (2, -34), 0.45, 1.5), ((10, -18), (-1, -40), 0.45, 1.6))
    return f, Shot(top_y=35.5, centre_x=-2.0)


def ryan():
    # the keeper, side-on to the card's right, one arm thrown out along the line he is looking
    f = Fig(
        light="right",
        skin="skin_light", hair="brown", iris="iris_brown", beard="short",
        hair_cfg=dict(len=0.9, top=1.5, quiff=0.8, fade=True),
        kit=Kit(number_txt="1", **KEEPER), armband=("right", "yellow"),
        torso=(46, -2, 0), head=(50, -6, 0),
        gaze=(0.3, -0.1), brow_lift=-0.4, brow_slope=0.8, mouth="closed", mouth_w=2.1,
        left=((-0.80, -0.52, 0.10), (-0.84, -0.46, 0.22), "relaxed"),
        right=((0.92, -0.06, 0.38), (0.95, -0.02, 0.30), "open"),
        order=("right", "body", "head", "left"),
    )
    return f, Shot(top_y=35.5, centre_x=3.0)


def minamino():
    # turned to the card's left, chin up, a wide open smile
    f = Fig(
        skin="skin_fair", hair="black", iris="iris_brown",
        hair_cfg=dict(len=1.4, top=1.8, fringe=3.0, part_x=1.6, long=1.4, side=1.05),
        kit=Kit(number_txt="10", **JAPAN),
        torso=(-26, 2, 0), head=(-34, 7, 4),
        gaze=(-0.25, 0.15), brow_lift=0.2,
        mouth="smile", mouth_w=2.5, mouth_h=0.85, smile=0.9,
        left=HANG_L, right=HANG_R,
    )
    f.folds = (((-8, -16), (4, -30), 0.45, 1.5),)
    return f, Shot(top_y=35.5, centre_x=-3.0)


def hakimi():
    # grinning, one hand up on his head, the other reaching out at the lens
    f = Fig(
        skin="skin_tan", hair="black", iris="iris_brown", beard="stubble", hair_cfg=SHORT,
        kit=Kit(number_txt="2", **MOROCCO),
        torso=(-10, -4, -6), shrug=(5.0, 0.0), head=(4, 2, 12),
        eye_open=0.7, brow_lift=0.1,
        mouth="smile", mouth_w=2.9, mouth_h=1.0, smile=1.0,
        left=((-0.62, 0.62, 0.45), (0.93, 0.34, -0.17), "flat", dict(dir=(0.9, 0.35, -0.25), face=(0, 0.6, 0.8))),
        right=((0.05, -0.45, 0.89), (-0.25, -0.02, 0.97), "open", dict(dir=(-0.45, -0.10, 0.89), face=(0, 1, 0.3))),
        order=("body", "head", "left", "right"),
    )
    return f, Shot(top_y=36.0, centre_x=-3.0)


def bellingham():
    # one arm straight up on the card's left, chin lifted, lips pushed out, looking right
    f = Fig(
        light="right",
        skin="skin_tan", hair="black", iris="iris_brown",
        hair_cfg=dict(len=1.0, top=1.2, curl=0.7, fade=True),
        kit=Kit(number_txt="10", **ENGLAND),
        torso=(10, 4, 3), shrug=(5.0, 0.0), head=(30, 12, 0),
        gaze=(0.25, 0.15), brow_lift=-0.25, brow_slope=0.6, mouth="purse",
        left=((-0.20, 0.97, 0.12), (-0.04, 0.99, 0.10), "fist"),
        right=HANG_R,
    )
    f.folds = (((-12, -8), (-2, -24), 0.55, 1.4), ((-13, -20), (-4, -40), 0.5, 1.6))
    return f, Shot(top_y=35.5, centre_x=-4.0)


def vinicius():
    # arms flung wide and off both edges of the card, head back, laughing
    f = Fig(
        skin="skin_dark", hair="black", iris="iris_brown", lip="lip_dark",
        hair_cfg=dict(len=1.3, top=2.6, curl=1.0, fade=True),
        kit=Kit(number_txt="7", **BRAZIL),
        torso=(0, 8, 0), shrug=(2.0, 2.0), head=(-4, 10, 9),
        eye_open=0.3, brow_lift=0.2,
        mouth="smile", mouth_w=3.2, mouth_h=1.5, smile=1.0, jaw_drop=0.9, snarl=1.0,
        left=((-0.97, 0.14, -0.05), (-0.98, 0.16, 0.02), "open"),
        right=((0.97, 0.14, -0.05), (0.98, 0.16, 0.02), "open"),
    )
    f.folds = (((-12, -10), (12, -10), 0.4, 1.5), ((-8, -22), (8, -24), 0.35, 1.6))
    return f, Shot(top_y=37.5, centre_x=-2.0)


def yamal():
    # turned a little right, head back, eyes screwed up, shouting; arms hanging off his sides
    f = Fig(
        light="right",
        skin="skin_tan", hair="black", iris="iris_brown",
        hair_cfg=dict(len=1.6, top=3.0, curl=1.2, fade=True, band="white"),
        kit=Kit(number_txt="19", **SPAIN),
        torso=(12, 6, 0), head=(24, 18, 4),
        eye_open=0.0, brow_lift=0.1,
        mouth="shout", mouth_w=2.5, mouth_h=1.5, jaw_drop=1.3, smile=0.5,
        left=((-0.30, -0.94, 0.05), (-0.15, -0.95, 0.25), "relaxed"),
        right=((0.30, -0.94, 0.05), (0.15, -0.95, 0.25), "relaxed"),
    )
    f.folds = (((-8, -18), (4, -32), 0.45, 1.5),)
    return f, Shot(top_y=37.0, centre_x=-3.0)


def ronaldo():
    # 25 Oct, from Hubi's picture: a relaxed smile, turned a touch to the card's left, arms down,
    # the white away shirt with light-blue strokes, the armband on the card's right
    f = Fig(
        skin="skin_light", hair="brown_dark", iris="iris_brown",
        hair_cfg=dict(len=0.8, top=1.5, quiff=1.3, top_x=0.4, fade=True),
        kit=Kit(number_txt="7", **PORTUGAL_AWAY), armband=("right", "deep_navy"),
        torso=(-14, 0, 0), shrug=(1.0, 1.0), head=(-8, 3, 2),
        gaze=(0.1, 0.0), brow_lift=0.1,
        mouth="smile", mouth_w=2.6, mouth_h=0.85, smile=0.9,
        left=((-0.22, -0.96, 0.10), (-0.08, -0.96, 0.26), "relaxed"),
        right=((0.24, -0.96, 0.08), (0.10, -0.96, 0.24), "relaxed"),
    )
    f.folds = (((-10, -14), (6, -28), 0.45, 1.4), ((-12, -26), (4, -40), 0.4, 1.6))
    return f, Shot(top_y=35.5, centre_x=-2.0)


def modric():
    # turned to the card's left, soft smile, applauding with both hands in front of his chest
    f = Fig(
        skin="skin_fair", hair="brown_mid", iris="iris_brown", beard="stubble",
        hair_cfg=dict(len=1.2, top=1.2, long=8.0, side=1.1),
        kit=Kit(number_txt="10", **CROATIA), armband=("right", "navy"),
        torso=(-30, 0, 0), head=(-34, 0, -4),
        gaze=(-0.25, 0.0), mouth="closed", mouth_w=2.4, smile=0.7,
        left=((-0.35, -0.82, 0.45), (0.35, 0.83, 0.43), "flat", dict(dir=(0.1, 0.99, 0.0), face=(0.2, 0, 0.98))),
        right=((-0.45, -0.70, 0.55), (-0.54, 0.82, -0.20), "flat", dict(dir=(-0.2, 0.95, 0.1), face=(-0.6, 0, 0.8))),
        order=("body", "head", "left", "right"),
    )
    return f, Shot(top_y=35.5, centre_x=-5.0)


def vandijk():
    # turned to the card's right, shouting, clapping his hands up by his face
    f = Fig(
        light="right",
        skin="skin_tan", hair="black", iris="iris_brown", beard="stubble",
        hair_cfg=dict(len=0.5, fringe=-0.5, bun=True),
        kit=Kit(number_txt="4", **HOLLAND_AWAY), armband=("right", "yellow"),
        torso=(30, 2, 0), head=(16, 6, 0),
        eye_open=0.8, brow_lift=-0.3, brow_slope=0.8,
        mouth="shout", mouth_w=2.4, mouth_h=1.5, jaw_drop=1.2,
        left=((0.55, -0.40, 0.73), (0.50, 0.72, -0.48), "flat", dict(dir=(0.25, 0.95, 0.0), face=(0.5, 0, 0.87))),
        right=((0.50, -0.45, 0.74), (-0.28, 0.96, 0.04), "flat", dict(dir=(-0.1, 0.99, 0.0), face=(-0.3, 0, 0.95))),
        order=("body", "head", "right", "left"),
    )
    return f, Shot(top_y=35.5, centre_x=4.0)


def lewandowski():
    # turned to the card's left, both hands up at his mouth
    f = Fig(
        skin="skin_fair", hair="brown_mid", iris="iris_blue",
        hair_cfg=dict(len=0.9, top=1.4, quiff=0.8, fade=True),
        kit=Kit(number_txt="9", **POLAND), armband=("right", "red"),
        torso=(-30, 0, 0), head=(-38, 4, 0),
        gaze=(-0.25, 0.0), brow_lift=-0.3, brow_slope=0.7, mouth="closed", mouth_w=1.8,
        left=((-0.20, -0.65, 0.73), (0.35, 0.936, 0.02), "flat", dict(dir=(0.15, 0.97, -0.1), face=(0.2, 0, 0.98))),
        right=((-0.30, -0.50, 0.81), (-0.352, 0.777, -0.519), "flat", dict(dir=(-0.35, 0.9, -0.2), face=(-0.5, 0, 0.87))),
        order=("body", "head", "left", "right"),
    )
    return f, Shot(top_y=35.5, centre_x=-4.0)


def mbappe():
    # head back and roaring, one fist clenched up at his shoulder on the card's right
    f = Fig(
        skin="skin_brown", hair="black", iris="iris_brown", lip="lip_dark",
        hair_cfg=dict(len=0.6, top=0.7, fringe=0.6, fade=True),
        kit=Kit(number_txt="10", **FRANCE),
        torso=(8, 6, 0), shrug=(0.0, 2.0), head=(-12, 16, -4),
        eye_open=0.5, brow_lift=-0.3, brow_slope=0.9,
        mouth="shout", mouth_w=2.8, mouth_h=1.8, jaw_drop=1.6, smile=0.3, snarl=1.0,
        left=HANG_L,
        right=((0.25, -0.80, 0.55), (-0.02, 0.90, 0.43), "fist", dict(tape="white")),
    )
    f.folds = (((10, -12), (0, -26), 0.5, 1.4), ((12, -24), (2, -40), 0.45, 1.6))
    return f, Shot(top_y=35.5, centre_x=-2.0)


def neymar():
    # chin up, a hand cupped behind his ear on the card's left, half a smile
    f = Fig(
        skin="skin_light", hair="blond", hair_side="brown", brow="brown", iris="iris_brown",
        beard="stubble", beard_ramp="brown",
        hair_cfg=dict(len=1.2, top=2.6, quiff=1.2, curl=0.8, fade=True),
        kit=Kit(number_txt="10", **BRAZIL),
        torso=(12, 4, 0), shrug=(4.0, 0.0), head=(4, 14, 6),
        eye_open=0.6, gaze=(0.0, -0.2), mouth="closed", mouth_w=2.4, smirk=0.8,
        left=((-0.78, 0.33, 0.46), (0.91, 0.268, -0.311), "flat", dict(dir=(0.55, 0.8, -0.2), face=(0.3, 0, 0.95))),
        right=((0.25, -0.95, 0.10), (0.10, -0.97, 0.20), "relaxed"),
        order=("body", "left", "head", "right"),
    )
    return f, Shot(top_y=36.5, centre_x=-2.0)


def messi():
    # 25 Oct, from Hubi's picture: a big grin straight at the lens, pointing at you with the hand
    # on the card's right, the other arm loose at his side. Argentina's sky-and-white stripes.
    kit = (StripeKit(number_txt="10", **ARGENTINA_HOME) if StripeKit is not None else
           Kit(number_txt="10", **{k: v for k, v in ARGENTINA_HOME.items() if k != "stripes"}))
    f = Fig(
        skin="skin_light", hair="brown", iris="iris_brown", beard="full", beard_ramp="brown_mid",
        hair_cfg=dict(len=1.15, top=1.6, quiff=0.9, fringe=0.4, side=1.05),
        kit=kit,
        torso=(-8, -2, 0), shrug=(0.0, 2.5), head=(-6, 3, 5),
        eye_open=0.62, brow_lift=0.15,
        mouth="smile", mouth_w=2.9, mouth_h=1.0, smile=1.0, snarl=1.0,
        left=((-0.22, -0.95, 0.20), (0.15, -0.55, 0.82), "relaxed"),
        right=((0.12, -0.48, 0.87), (-0.22, 0.30, 0.93), "point", dict(dir=(-0.68, 0.40, 0.61), face=(0.3, 0.4, 0.86))),
        order=("body", "head", "left", "right"),
    )
    f.folds = (((12, -10), (2, -24), 0.5, 1.4), ((10, -24), (-2, -38), 0.45, 1.6))
    return f, Shot(top_y=36.0, centre_x=0.0)


FIGS = {"WC_SPA_olmo": olmo, "WC_FRA_dembele": dembele, "WC_POR_bernardo": bernardo,
        "WC_NET_gakpo": gakpo, "WC_AUS_ryan": ryan, "WC_JPN_minamino": minamino,
        "WC_MOR_hakimi": hakimi, "WC_ENG_bellingham": bellingham, "WC_BRA_vinicius": vinicius,
        "WC_SPA_yamal": yamal, "WC_POR_ronaldo": ronaldo, "WC_CRO_modric": modric,
        "WC_POL_lewandowski": lewandowski, "WC_NET_vandijk": vandijk, "WC_FRA_mbappe": mbappe,
        "SIG_BRA_neymar": neymar, "WC_ARG_messi": messi}
