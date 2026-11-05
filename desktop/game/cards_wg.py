"""THE WORLD'S GAME figures - the players only Essence can sign - posed from Hubi's pictures.

Same rules as cards17.py: LEFT and RIGHT are the CARD's, arms are written as the camera sees
them, each player stands at the angle of his own picture. The kits are the ones in the
pictures, drawn as shapes and colours only: no crest, no maker, no sponsor.
"""
from cardfig import Fig, Kit, Shot

# navy with a light-blue flash from the neck to under each arm
ARGENTINA_2006 = dict(body="deep_navy", collar="deep_navy", cuff="sky", number="white", shorts="deep_navy",
                      flash="sky", badge=("white", "sky"))
# red, green at the neck and the cuffs, a gold number
PORTUGAL_2004 = dict(body="red", collar="green", cuff="green", number="gold", shorts="green",
                     collar_w=1.9, badge=("gold", "green"))
# white with one broad red band down the chest, the number on the white beside it
POLAND_BAND = dict(body="white", collar="white", cuff="red", number="red", shorts="red",
                   band=("red", -8.6, -2.6), number_x=3.6, badge=("red", "white"), badge_x=9.6)


def messi():
    # square to the lens, calm, pointing straight at you with the hand on the card's left
    f = Fig(
        skin="skin_light", hair="brown", iris="iris_brown",
        hair_cfg=dict(len=1.25, top=1.3, fringe=2.2, part_x=0.8, long=4.2, side=1.12),
        kit=Kit(number_txt="19", **ARGENTINA_2006),
        torso=(7, -2, 0), shrug=(2.0, 0.0), head=(-3, -2, 3), neck_fwd=1.6,
        eye_open=0.86, brow_lift=-0.15, brow_slope=0.3,
        mouth="closed", mouth_w=2.2, smirk=0.3,
        left=((-0.06, -0.44, 0.90), (0.30, 0.40, 0.87), "point", dict(dir=(0.16, 0.70, 0.70), face=(-0.6, 0, 0.8))),
        right=((0.16, -0.97, 0.10), (0.06, -0.97, 0.22), "relaxed"),
        order=("body", "head", "right", "left"),
    )
    f.folds = (((-12, -10), (-2, -24), 0.5, 1.4), ((-10, -24), (2, -38), 0.45, 1.6))
    return f, Shot(top_y=36.0, centre_x=-1.0)


def ronaldo():
    # chest out, head thrown right back and turned to the card's left, shouting at the sky
    f = Fig(
        skin="skin_light", hair="brown_dark", iris="iris_brown",
        hair_cfg=dict(len=0.9, top=1.5, quiff=1.3, fringe=0.4, fade=True),
        kit=Kit(number_txt="17", **PORTUGAL_2004),
        torso=(-24, 12, 2), shrug=(2.0, 2.0), head=(-40, 36, -8), neck_fwd=0.0,
        eye_open=0.0, brow_lift=-0.25, brow_slope=0.9,
        mouth="shout", mouth_w=2.6, mouth_h=2.1, jaw_drop=2.1, snarl=1.0,
        left=((-0.30, -0.90, -0.25), (-0.22, -0.92, 0.30), "fist"),
        right=((0.38, -0.86, -0.34), (0.26, -0.92, 0.28), "fist"),
    )
    f.folds = (((-10, -14), (6, -26), 0.5, 1.4), ((-12, -26), (4, -38), 0.45, 1.6))
    return f, Shot(top_y=35.0, centre_x=-4.0)


def lewandowski():
    # facing you, roaring, shoulders up and both fists driven down at his sides
    f = Fig(
        skin="skin_fair", hair="brown", iris="iris_blue",
        hair_cfg=dict(len=0.9, top=1.7, quiff=1.5, top_x=0.5, fade=True),
        kit=Kit(number_txt="9", **POLAND_BAND), armband=("right", "blue"),
        torso=(4, -4, -2), shrug=(4.5, 4.5), head=(2, 4, -5), neck_fwd=2.2,
        eye_open=0.42, brow_lift=-0.5, brow_slope=1.1,
        mouth="shout", mouth_w=2.9, mouth_h=2.1, jaw_drop=2.0, snarl=1.0,
        left=((-0.46, -0.88, 0.05), (-0.20, -0.86, 0.47), "fist"),
        right=((0.46, -0.88, 0.05), (0.20, -0.86, 0.47), "fist"),
    )
    f.folds = (((-13, -10), (-3, -24), 0.5, 1.4), ((13, -10), (3, -24), 0.5, 1.4),
               ((-12, -26), (0, -42), 0.45, 1.6))
    return f, Shot(top_y=35.5, centre_x=0.0)


FIGS = {"WG_messi": messi, "WG_ronaldo": ronaldo, "WG_lewandowski": lewandowski}
