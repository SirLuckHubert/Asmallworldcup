"""Redraw the posed card players into the sprites folder: the seventeen draft cards
(cards17.py), the World's Game players (cards_wg.py), Champion Draft A (cards_champ.py) and
(30 Oct) the Limit Breakers (cards_lb.py), (31 Oct) Club Packs 2 and 3, pools A and B, and
(31 Oct) Limit Breakers Draft B (cards_lb2.py), (1 Nov) the 41 Star Signings (cards_star.py)
(cards_club.py) - every figure built on cardfig's body.

    python3 make_card_figures.py [sprites_folder] [name ...]

With no names, all of them. A name is a whole card id (WG_messi) or the end of one (olmo,
vandijk); "messi" on its own draws both Messis.
Each figure is <card id>_figure.png, 160 x 170 pixels: the card shows the middle 107 columns
and the rest is bleed for arms that run off the card. Takes a few minutes; needs numpy.
"""
import os
import sys
import time
from multiprocessing import Pool

import cardfig
import cards17
import cards_champ
import cards_club
import cards_lb
import cards_lb2
import cards_sig
import cards_star
import cards_wg

QUALITY = 6          # samples per pixel side; the look was approved at 6
FIGS = dict(cards17.FIGS)
FIGS.update(cards_wg.FIGS)
FIGS.update(cards_champ.FIGS)
FIGS.update(cards_lb.FIGS)
FIGS.update(cards_club.FIGS)
FIGS.update(cards_lb2.FIGS)              # (31 Oct: Limit Breakers Draft B)
FIGS.update(cards_star.FIGS)             # (1 Nov: all 41 Star Signings)
FIGS.update(cards_sig.FIGS)              # (1 Nov: Mario Kempes, the second Game Box)


def one(args):
    cid, out = args
    fig, shot = FIGS[cid]()
    cardfig.flatten(cardfig.render(fig, shot, S=QUALITY)).save(os.path.join(out, "%s_figure.png" % cid))
    return cid


if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[0] if args and os.path.isdir(args[0]) else "sprites"
    names = [a for a in args if a != out]
    ids = [k for k in FIGS if not names or k in names or k.split("_")[-1] in names]
    t = time.time()
    with Pool(min(len(ids), os.cpu_count() or 1)) as pool:
        done = pool.map(one, [(i, out) for i in ids], chunksize=1)
    print("%d figures drawn into %s in %.0fs" % (len(done), out, time.time() - t))
