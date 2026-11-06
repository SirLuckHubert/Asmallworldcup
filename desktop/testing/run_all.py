"""Run every check in this folder, one after another.

    cd testing
    python3 run_all.py

Each check boots the real game from ../game on a stand-in for pygame (no window, no sound), so
you can run them on any computer with Python 3 and Pillow (pip install pillow). Nothing here
touches your real save: test saves and screenshots go in testing/out/.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKS = [
    ("stats_check.py", "the six stats and the slide"),
    ("playstyles_check.py", "every PlayStyle fires in its moment"),
    ("progression_check.py", "training points, feeding, gem ranks, skill points"),
    ("limitbreakers_check.py", "the Limit Breakers pack"),
    ("match_check.py", "a full CPU v CPU match"),
    ("subs_check.py", "team sheet + half-time IN / OUT sub, on/offline"),
    ("home_check.py", "the home screen: it draws, every button works"),
    ("champions_check.py", "Champion Draft A: the thirteen, their pools, clubs and cards"),
    ("classic_check.py", "classic physics: the original's gravity, drag and bounce"),
    ("worldcup_screen_check.py", "the new World Cup screen: every state draws, every click works"),
    ("ladder_check.py", "club mode: the ladder, twists, objectives, the Champions Cup"),
    ("profile_check.py", "the profile tab: trophy cabinet, numbers, trophies counted"),
    ("gauntlet_check.py", "the Gauntlet: ten rungs, halves, twists, boosts, THE MACHINE"),
    ("walkout_check.py", "the pack walkout: every scene on the song's beat, skip, 10x"),
    ("wg_evo_check.py", "World's Game evolutions: quests, four stages, 132, purple PlayStyle"),
    ("quests_check.py", "daily + weekly quests: counted, rerolled, claimed, chest, free pack"),
    ("stars_check.py", "Star Signings: gold / World Cup / club cards by tier, 41 figures"),
    ("archive_check.py", "Signature Archive + Kempes: boxes, tokens, the level 10 quest"),
    ("online_check.py", "online 1v1: own doll is yours, kicks stick, same score both screens"),
    ("web_paths_check.py", "the browser's own paths: still pages, glass budget, light confetti"),
    ("season_check.py", "Season 1: pass, gems, ads, pictures, ball skins, the S1 card"),
]
results = []
for script, what in CHECKS:
    print("\n=== %s  (%s)" % (script, what))
    t = time.time()
    code = subprocess.call([sys.executable, os.path.join(HERE, script)], cwd=HERE)
    results.append((script, what, code == 0, time.time() - t))
print("\n" + "=" * 60)
for script, what, ok, secs in results:
    print("%s  %-24s %-48s %4.0fs" % ("PASS" if ok else "FAIL", script, what, secs))
bad = [r for r in results if not r[2]]
print("\n%s" % ("everything passed" if not bad else "%d check(s) failed - scroll up for which line" % len(bad)))
sys.exit(1 if bad else 0)
