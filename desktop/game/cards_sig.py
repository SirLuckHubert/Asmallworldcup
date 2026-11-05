"""GAME BOX Signature figures (1 Nov): Mario Kempes, the second box's card.

Argentina's white and sky-blue stripes of 1978, the big dark curls - standing calm, a hand on his hip. Same rules as cards_lb.py: LEFT and RIGHT are the CARD's. Kit is shapes and colours
only - no crest, no maker.
"""
from cardfig import Fig, Shot
from cards_lb import ARGENTINA, kit
from cards_club import HIP_L
from cards_lb import HANG_R


def kempes():
    # 1 Nov, second go (Hubi: "the pose is ass"): calm and standing, the way his famous picture has him -
    # turned a little, one hand on his hip, the other easy at his side, looking off past the camera,
    # the big dark curls framing his face. No shouting.
    f = Fig(skin="skin_light", hair="black", iris="iris_brown", brow="black",
            hair_cfg=dict(len=1.7, top=1.9, fringe=1.0, long=2.9, curl=1.1, side=1.25, part_x=0.6),
            kit=kit(10, ARGENTINA), torso=(-10, 0, 0), shrug=(1.0, 0.5), head=(-16, 2, -2), neck_fwd=1.2,
            gaze=(-0.30, 0.04), eye_open=0.82, brow_lift=-0.15, brow_slope=0.25,
            mouth="closed", mouth_w=2.2, smile=0.0, jaw_w=5.6,
            left=HIP_L, right=HANG_R, order=("body", "head", "left", "right"))
    f.folds = (((-12, -10), (-2, -24), 0.5, 1.4), ((10, -12), (2, -30), 0.4, 1.4))
    return f, Shot(top_y=35.5, centre_x=-0.8)


FIGS = {"SIG_ARG_kempes": kempes}
