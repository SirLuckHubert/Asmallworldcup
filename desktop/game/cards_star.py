"""STAR SIGNING figures (1 Nov) - all 41, posed with cardfig.

Hubi: "rework the design for star signing players to be either club design or World Cup design or a
new design" - all three, by tier (STAR_LOOK in the game):
  148+      the new GOLD CRYSTAL card     - in their country's shirt
  143-147   the WORLD CUP flag card       - in their country's shirt
  135-142   the CLUB (Champions) card     - in their club's shirt
Each one is posed the way people know him: his celebration or his look. Kits are shapes and colours
only - no crest, no maker, no sponsor. Same rules as cards_lb.py: LEFT and RIGHT are the CARD's, arms
are (upper-arm direction, forearm direction, hand[, options]) as the camera sees them.
"""
import cardfig
from cardfig import Fig, Shot
from cards_lb import ARGENTINA, CITY, FRANCE, GERMANY, HANG_L, HANG_R, HOLLAND, PORTUGAL, SHORT, SLICK, SPAIN, kit
from cards_club import (BARCA, EAR_R, FIST_CHEST_L, FIST_CHEST_R, FIST_LOW_L, FIST_LOW_R, FLEX_L, FLEX_R, HIP_L,
                        HIP_R, LIVERPOOL, POINT_AWAY_L, POINT_LENS_L, POINT_LENS_R, POINT_UP_L, POINT_UP_R,
                        WIDE_UP_L, WIDE_UP_R, mirror)
from cards_lb2 import BELGIUM, BRAZIL, HEART_L, HEART_R, ITALY, PALMS_L, PALMS_R, PLANE_L, PLANE_R
from cards_champ import ARSENAL

cardfig.RAMPS.setdefault("ginger", [(70, 26, 8), (122, 50, 16), (170, 78, 30), (206, 110, 52), (232, 150, 90)])

# ------------------------------------------------------------------ kits (colours only)
REAL = dict(body="white", collar="navy", cuff="gold", number="navy", shorts="white", badge=("gold", "navy"))
BAYERN = dict(body="red", collar="white", cuff="white", number="white", shorts="red", badge=("white", "red"))
MILAN = dict(body="red", collar="black", number="white", shorts="white", stripes=("black", 6.2, 0.5),
             badge=("white", "red"))
USSR_GK = dict(body="black", collar="black", number="white", number_txt="", long_sleeve=True, shorts="black",
               badge=None)
BAYERN_GK = dict(body="green", collar="black", cuff="black", number="white", long_sleeve=True, shorts="green",
                 badge=("white", "green"))
JUVE_GK = dict(body="charcoal", collar="white", number="white", long_sleeve=True, shorts="charcoal",
               badge=("white", "charcoal"))
GLOVE = dict(glove="charcoal")
# crossed arms across the chest (the right one in front)
CROSS_L = ((-0.28, -0.88, 0.38), (0.92, 0.22, 0.32), "fist")
CROSS_R = ((0.30, -0.86, 0.42), (-0.90, 0.26, 0.36), "fist")
BALD = dict(len=0.05, fade=True)


def g(arm):
    """The same arm in goalkeeper's gloves."""
    return tuple(arm[:3]) + ((dict(arm[3], **GLOVE) if len(arm) > 3 else GLOVE),)


def fig(num, base, shot_x=0.0, top_y=35.5, folds=None, **kw):
    f = Fig(kit=kit(num, base), **kw)
    if folds:
        f.folds = folds
    return f, Shot(top_y=top_y, centre_x=shot_x)


# ================================================================== GOLD CRYSTAL (148+)
def neto():
    # flying in from the wing, arms flung back and wide, mouth open
    return fig(7, PORTUGAL, skin="skin_tan", hair="black", beard="stubble", beard_ramp="black",
               hair_cfg=dict(len=0.8, top=1.6, quiff=0.8, fade=True), torso=(-6, 4, 0), head=(-4, 10, 0),
               mouth="shout", mouth_w=2.6, mouth_h=1.6, jaw_drop=1.4, eye_open=0.7,
               left=WIDE_UP_L, right=WIDE_UP_R, shot_x=-0.5)


def pele():
    # the leap and the punch at the sky, the famous grin
    return fig(10, BRAZIL, skin="skin_dark", hair="black", lip="lip_dark", hair_cfg=dict(len=0.4, top=0.6, fade=True),
               torso=(-4, 6, 0), head=(-2, 12, 0), mouth="smile", mouth_w=3.0, mouth_h=1.4, smile=1.0,
               eye_open=0.6, left=FIST_LOW_L, right=FLEX_R)


def r9():
    # the wedge of hair at the front, the gap-toothed grin, a finger wagging at the crowd
    return fig(9, BRAZIL, skin="skin_tan", hair="black", hair_cfg=dict(len=0.12, fringe=2.4, top=0.5, top_z=6.0, fade=True),
               torso=(6, 2, 0), head=(8, 6, 2), mouth="smile", mouth_w=3.0, mouth_h=1.3, smile=1.0,
               left=HANG_L, right=POINT_UP_R, shot_x=0.5)


def maradona():
    # the curls, the fist clenched to his chest, a roar
    return fig(10, ARGENTINA, skin="skin_tan", hair="black", hair_cfg=dict(len=1.5, top=2.0, curl=1.2, long=1.2),
               torso=(-6, 6, 0), shrug=(3.0, 2.0), head=(-4, 12, 0), mouth="shout", mouth_w=2.8, mouth_h=1.8,
               jaw_drop=1.8, snarl=0.6, eye_open=0.55, brow_lift=-0.4, brow_slope=0.9,
               left=FLEX_L, right=FIST_CHEST_R)


def zidane():
    # calm as anything: shaved head, the look straight through you, hands easy
    return fig(10, FRANCE, skin="skin_light", hair="brown_dark", brow="brown_dark", hair_cfg=BALD,
               beard="stubble", beard_ramp="brown_dark", torso=(4, 0, 0), head=(6, 2, 0), mouth="closed",
               mouth_w=2.2, smile=0.2, brow_lift=-0.2, left=HANG_L, right=HANG_R, shot_x=0.5)


def ronaldinho():
    # the long hair under a band and the biggest smile in football, both hands up to the crowd
    return fig(10, BRAZIL, skin="skin_brown", hair="black", lip="lip_dark",
               hair_cfg=dict(len=1.4, top=1.8, long=2.4, curl=0.8, band="white"),
               torso=(0, 4, 0), head=(2, 8, 2), mouth="smile", mouth_w=3.4, mouth_h=1.6, smile=1.0, eye_open=0.6,
               left=PALMS_L, right=PALMS_R)


def mbappe():
    # arms crossed, chin up, not a flicker on his face
    return fig(9, FRANCE, skin="skin_brown", hair="black", lip="lip_dark", hair_cfg=dict(len=0.2, fade=True),
               torso=(0, 2, 0), head=(0, 10, 0), mouth="closed", mouth_w=2.4, smirk=0.3, brow_lift=-0.25,
               left=CROSS_L, right=CROSS_R, order=("body", "head", "left", "right"))


def neymar():
    # bleached top, dark sides, both hands making a heart
    return fig(11, BRAZIL, skin="skin_tan", hair="blond", hair_side="black", brow="black",
               hair_cfg=dict(len=0.6, top=2.0, quiff=1.6, fade=True), beard="stubble", beard_ramp="black",
               torso=(4, 2, 0), head=(6, 6, 2), mouth="smile", mouth_w=2.8, smile=0.8,
               left=HEART_L, right=HEART_R, order=("body", "head", "left", "right"))


def cruyff():
    # the long hair, pointing out where the pass must go
    return fig(14, HOLLAND, skin="skin_fair", hair="brown", hair_cfg=dict(len=1.2, fringe=1.6, long=1.6, part_x=1.0),
               torso=(-8, 2, 0), head=(-12, 4, 0), mouth="shout", mouth_w=2.4, mouth_h=1.2, jaw_drop=0.9,
               left=POINT_AWAY_L, right=HANG_R, shot_x=-0.8)


# ================================================================== WORLD CUP (143-147)
def gullit():
    # the dreadlocks and the moustache, arms out wide
    return fig(10, HOLLAND, skin="skin_brown", hair="black", lip="lip_dark", beard="short", beard_ramp="black",
               hair_cfg=dict(len=1.6, top=1.6, long=2.8, curl=1.6), torso=(0, 4, 0), head=(0, 8, 0),
               mouth="smile", mouth_w=3.0, smile=0.9, left=WIDE_UP_L, right=WIDE_UP_R)


def hazard():
    # hands on hips, the easy grin
    return fig(10, BELGIUM, skin="skin_light", hair="brown_dark", beard="short", beard_ramp="brown_dark",
               hair_cfg=SHORT, torso=(4, 0, 0), head=(6, 2, 2), mouth="smile", mouth_w=2.6, smile=0.8,
               left=HIP_L, right=HIP_R)


def iniesta():
    # a finger to the sky: the goal for a friend
    return fig(8, SPAIN, skin="skin_fair", hair="brown", hair_cfg=dict(len=0.35, fade=True), torso=(-2, 4, 0),
               head=(0, 16, 0), gaze=(0.0, 0.4), mouth="closed", mouth_w=2.2, smile=0.3,
               left=HANG_L, right=POINT_UP_R)


def xavi():
    # the metronome, pointing where the ball goes next
    return fig(6, SPAIN, skin="skin_light", hair="black", beard="stubble", beard_ramp="black", hair_cfg=SHORT,
               torso=(-8, 2, 0), head=(-10, 4, 0), mouth="closed", mouth_w=2.2, brow_lift=-0.15,
               left=POINT_AWAY_L, right=HANG_R, shot_x=-0.8)


def kaka():
    # both fingers to the sky, eyes up
    return fig(22, BRAZIL, skin="skin_light", hair="brown_dark", hair_cfg=dict(len=0.7, top=1.2, fade=True),
               torso=(0, 4, 0), head=(0, 18, 0), gaze=(0.0, 0.5), mouth="smile", mouth_w=2.6, smile=0.7,
               left=POINT_UP_L, right=POINT_UP_R)


def henry():
    # leaning on nothing, shaved head, ice cold
    return fig(14, FRANCE, skin="skin_dark", hair="black", lip="lip_dark", hair_cfg=BALD, torso=(8, 0, 0),
               head=(10, 2, 0), mouth="closed", mouth_w=2.4, smirk=0.5, brow_lift=-0.2,
               left=HANG_L, right=HIP_R, shot_x=0.8)


def vanbasten():
    # blond, a fist up beside his head
    return fig(9, HOLLAND, skin="skin_fair", hair="blond_dark", hair_cfg=dict(len=1.0, top=1.2, long=1.0),
               torso=(-4, 4, 0), head=(-2, 8, 0), mouth="smile", mouth_w=2.6, smile=0.7, left=HANG_L, right=FLEX_R)


def eusebio():
    # the Panther: fists clenched, a big smile
    return fig(10, PORTUGAL, skin="skin_dark", hair="black", lip="lip_dark", hair_cfg=dict(len=0.5, top=1.0, fade=True),
               torso=(-4, 2, 0), head=(-4, 6, 0), mouth="smile", mouth_w=2.8, smile=0.9,
               left=FIST_LOW_L, right=FLEX_R)


def maldini():
    # the long hair, the armband, standing tall
    f, s = fig(3, ITALY, skin="skin_light", hair="brown", hair_cfg=dict(len=1.3, fringe=0.8, long=1.8, part_x=1.2),
               armband=("left", "white"), torso=(4, 0, 0), head=(6, 4, 0), mouth="closed", mouth_w=2.2,
               smile=0.2, left=HANG_L, right=HANG_R)
    return f, s


def beckenbauer():
    # Der Kaiser: the side parting, hands behind his back, untroubled
    return fig(5, GERMANY, skin="skin_fair", hair="brown", hair_cfg=dict(len=1.0, fringe=1.2, part_x=-1.6, side=1.1),
               armband=("left", "black"), torso=(-4, 0, 0), head=(-6, 4, 0), mouth="closed", mouth_w=2.2,
               smile=0.4, left=HIP_L, right=HIP_R)


def ramos():
    # slicked back, the full beard, the armband, roaring
    return fig(4, SPAIN, skin="skin_tan", hair="brown_dark", beard="full", beard_ramp="brown_dark", hair_cfg=SLICK,
               armband=("left", "yellow"), torso=(-4, 6, 0), shrug=(3.5, 3.0), head=(-2, 12, 0),
               mouth="shout", mouth_w=2.9, mouth_h=2.0, jaw_drop=2.0, snarl=1.0, eye_open=0.5, brow_lift=-0.5,
               left=FLEX_L, right=FIST_LOW_R)


def vandijk():
    # hands on hips, the beard, a calm look down at you
    return fig(4, HOLLAND, skin="skin_brown", hair="black", lip="lip_dark", beard="short", beard_ramp="black",
               hair_cfg=dict(len=0.8, top=2.0, curl=0.8, fade=True), torso=(2, -2, 0), head=(2, -2, 0),
               mouth="closed", mouth_w=2.4, smile=0.3, jaw_w=5.9, left=HIP_L, right=HIP_R)


def cafu():
    # the armband and both arms up: the captain lifting it
    return fig(2, BRAZIL, skin="skin_dark", hair="black", lip="lip_dark", hair_cfg=BALD, armband=("left", "blue"),
               torso=(0, 6, 0), head=(0, 14, 0), mouth="smile", mouth_w=3.2, mouth_h=1.5, smile=1.0,
               left=WIDE_UP_L, right=WIDE_UP_R)


def rcarlos():
    # shaved head, flexing both arms
    return fig(6, BRAZIL, skin="skin_brown", hair="black", lip="lip_dark", hair_cfg=BALD, torso=(0, 4, 0),
               shrug=(3.0, 3.0), head=(0, 6, 0), mouth="smile", mouth_w=3.0, smile=0.9, left=FLEX_L, right=FLEX_R)


def yashin():
    # the Black Spider: all in black, gloves on, arms folded
    return fig(1, USSR_GK, skin="skin_fair", hair="brown", hair_cfg=dict(len=0.8, fringe=1.0, fade=True),
               torso=(0, 0, 0), head=(2, 4, 0), mouth="closed", mouth_w=2.2, smile=0.2,
               left=g(CROSS_L), right=g(CROSS_R), order=("body", "head", "left", "right"))


# ================================================================== CLUB (135-142)
def neuer():
    # gloves on, arms spread to cover the goal
    return fig(1, BAYERN_GK, skin="skin_fair", hair="blond", hair_cfg=SHORT, torso=(0, 0, 0), head=(0, 4, 0),
               mouth="closed", mouth_w=2.2, smile=0.3, left=g(PLANE_L), right=g(PLANE_R))


def buffon():
    # the roar, both gloves clenched
    return fig(1, JUVE_GK, skin="skin_light", hair="brown", beard="stubble", beard_ramp="brown",
               hair_cfg=dict(len=1.0, top=1.4, quiff=0.6), torso=(-4, 6, 0), shrug=(3.0, 3.0), head=(-2, 12, 0),
               mouth="shout", mouth_w=2.8, mouth_h=2.0, jaw_drop=2.0, snarl=0.8, eye_open=0.5,
               left=g(FIST_LOW_L), right=g(FLEX_R))


def modric():
    # the long fringe, the armband, calm
    return fig(10, REAL, skin="skin_fair", hair="blond_dark", hair_cfg=dict(len=1.2, fringe=2.0, long=1.6),
               armband=("left", "gold"), torso=(4, 0, 0), head=(6, 4, 0), mouth="closed", mouth_w=2.2, smile=0.4,
               left=HANG_L, right=HANG_R)


def debruyne():
    # pointing straight at you, ginger hair, half a smile
    return fig(17, CITY, skin="skin_fair", hair="ginger", brow="ginger", iris="iris_blue",
               hair_cfg=dict(len=0.9, top=1.6, quiff=0.8, top_x=0.6, fade=True), torso=(2, 2, 0), head=(2, 4, 0),
               mouth="closed", mouth_w=2.2, smile=0.5, left=HANG_L, right=POINT_LENS_R)


def salah():
    # both fingers up to the sky, the curls and the beard
    return fig(11, LIVERPOOL, skin="skin_tan", hair="black", beard="full", beard_ramp="black", lip="lip_dark",
               hair_cfg=dict(len=1.3, top=2.6, curl=1.2), torso=(0, 4, 0), head=(0, 14, 0), gaze=(0.0, 0.4),
               mouth="smile", mouth_w=2.8, smile=0.8, left=POINT_UP_L, right=POINT_UP_R)


def vinicius():
    # dancing: one arm out, one on the hip
    return fig(7, REAL, skin="skin_brown", hair="black", lip="lip_dark", hair_cfg=dict(len=0.9, top=2.0, curl=1.0, fade=True),
               torso=(8, 2, 0), head=(10, 6, 4), mouth="smile", mouth_w=3.0, smile=1.0,
               left=WIDE_UP_L, right=HIP_R, shot_x=0.8)


def haaland():
    # the meditation: eyes shut, hands open, hair tied back
    return fig(9, CITY, skin="skin_fair", hair="blond", iris="iris_blue",
               hair_cfg=dict(len=1.0, top=1.2, long=1.0, bun=True), torso=(0, 0, 0), head=(0, 4, 0),
               eye_open=0.0, mouth="closed", mouth_w=2.2, smile=0.1, left=PALMS_L, right=PALMS_R)


def bellingham():
    # arms out wide, chin up: soaking it in
    return fig(5, REAL, skin="skin_brown", hair="black", lip="lip_dark", hair_cfg=dict(len=0.4, top=0.8, fade=True),
               torso=(0, 2, 0), head=(0, 12, 0), mouth="closed", mouth_w=2.4, smile=0.4,
               left=PLANE_L, right=PLANE_R)


def rodri():
    # the quiet one: hands easy, a nod
    return fig(16, CITY, skin="skin_light", hair="brown_dark", beard="stubble", beard_ramp="brown_dark",
               hair_cfg=dict(len=0.8, top=1.2, fringe=0.6, fade=True), torso=(-4, 0, 0), head=(-4, -2, 0),
               mouth="closed", mouth_w=2.2, smile=0.3, left=HANG_L, right=HANG_R)


def saka():
    # the grin, a finger up for the crowd
    return fig(7, ARSENAL, skin="skin_dark", hair="black", lip="lip_dark", hair_cfg=dict(len=0.4, top=0.8, fade=True),
               torso=(4, 2, 0), head=(4, 6, 0), mouth="smile", mouth_w=3.0, smile=1.0, left=HANG_L, right=POINT_UP_R)


def musiala():
    # the curls, pointing at you with a big smile
    return fig(10, BAYERN, skin="skin_brown", hair="black", lip="lip_dark", hair_cfg=dict(len=1.0, top=2.2, curl=1.1),
               torso=(-4, 2, 0), head=(-4, 6, 0), mouth="smile", mouth_w=3.0, smile=1.0,
               left=POINT_LENS_L, right=HANG_R)


def pedri():
    # the fringe, hands easy, a shy smile
    return fig(8, BARCA, skin="skin_light", hair="black", hair_cfg=dict(len=1.0, fringe=2.2, top=0.8),
               torso=(4, 0, 0), head=(6, 2, 0), mouth="closed", mouth_w=2.2, smile=0.5, left=HANG_L, right=HANG_R)


def wirtz():
    # a fist to the chest
    return fig(7, LIVERPOOL, skin="skin_fair", hair="brown", iris="iris_blue", hair_cfg=SHORT, torso=(2, 4, 0),
               head=(2, 8, 0), mouth="smile", mouth_w=2.6, smile=0.7, left=HANG_L, right=FIST_CHEST_R)


def yamal():
    # a hand cupped to his ear
    return fig(10, BARCA, skin="skin_tan", hair="black", hair_cfg=dict(len=0.7, top=1.4, curl=0.6, fade=True),
               torso=(6, 2, 0), head=(10, 6, 4), mouth="smile", mouth_w=2.6, smile=0.6, left=HANG_L, right=EAR_R)


def kane():
    # both arms up and wide, roaring
    return fig(9, BAYERN, skin="skin_fair", hair="brown", iris="iris_blue", hair_cfg=SHORT, torso=(0, 6, 0),
               head=(0, 12, 0), mouth="shout", mouth_w=2.8, mouth_h=1.8, jaw_drop=1.6, eye_open=0.6,
               left=WIDE_UP_L, right=WIDE_UP_R)


def suarez():
    # a big toothy grin and a fist pumped
    return fig(9, BARCA, skin="skin_tan", hair="black", beard="stubble", beard_ramp="black",
               hair_cfg=dict(len=0.9, top=1.4, quiff=0.8, fade=True), torso=(-4, 4, 0), head=(-2, 8, 0),
               mouth="smile", mouth_w=3.0, mouth_h=1.4, smile=1.0, left=FLEX_L, right=HANG_R)


def pirlo():
    # long hair, the full beard, not a care in the world
    return fig(21, MILAN, skin="skin_light", hair="brown_dark", beard="full", beard_ramp="brown_dark",
               hair_cfg=dict(len=1.3, fringe=0.6, long=1.8, part_x=1.0), torso=(-4, 0, 0), head=(-6, 2, 0),
               eye_open=0.55, mouth="closed", mouth_w=2.2, smirk=0.3, left=HANG_L, right=HANG_R)


FIGS = {"STAR_" + f.__name__: f for f in (
    neto, pele, r9, maradona, zidane, ronaldinho, mbappe, neymar, cruyff,
    gullit, hazard, iniesta, xavi, kaka, henry, vanbasten, eusebio, maldini, beckenbauer, ramos, vandijk, cafu,
    rcarlos, yashin,
    neuer, buffon, modric, debruyne, salah, vinicius, haaland, bellingham, rodri, saka, musiala, pedri, wirtz,
    yamal, kane, suarez, pirlo)}
