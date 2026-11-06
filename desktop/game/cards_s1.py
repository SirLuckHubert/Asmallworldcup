"""SEASON 1 card figure (6 Nov): Lionel Messi, the exclusive card at the top of the Season 1 pass.

His Barcelona years - the long hair - running off after a goal, one fist pumped high, a big open smile.
Kit is shapes and colours only: claret and blue stripes, the yellow 10, no crest, no maker (same rules
as cards_lb.py: LEFT and RIGHT are the CARD's).
"""
from cardfig import Fig, Shot
from cards_club import BARCA, mirror
from cards_lb import HANG_L, kit

# the fist punched up and out over his shoulder
FIST_HIGH_R = ((0.55, 0.31, -0.77), (-0.30, 0.80, 0.52), "fist")


def messi():
    f = Fig(skin="skin_light", hair="brown", iris="iris_brown",
            hair_cfg=dict(len=1.35, top=1.4, fringe=1.8, part_x=0.7, long=3.6, side=1.15),
            kit=kit(10, BARCA, badge=None), torso=(-6, 4, 0), shrug=(1.0, 4.0), head=(-8, 10, 2), neck_fwd=0.6,
            gaze=(0.0, 0.10), eye_open=0.7, brow_lift=0.25, brow_slope=-0.1,
            mouth="smile", mouth_w=2.5, mouth_h=1.05, smile=0.9,
            left=((-0.36, -0.88, 0.30), (0.50, -0.20, 0.84), "fist"), right=FIST_HIGH_R,
            order=("body", "head", "left", "right"))
    f.folds = (((-12, -10), (-2, -24), 0.5, 1.4), ((10, -12), (2, -30), 0.4, 1.4))
    return f, Shot(top_y=36.0, centre_x=0.0)


FIGS = {"S1_ARG_messi": messi}
