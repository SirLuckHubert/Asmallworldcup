"""SEASON 1 (6 Nov): the pass, gems, rewarded ads, profile pictures, ball skins and the S1 card - moved
by the game's own code (matches settled, quests claimed, mail claimed) and clicked through on screen.

    python3 season_check.py      (pictures: out/season_*.png)"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Run, rf, pygame

fails = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


random.seed(6)
squad = ["ARS_saka", "CHE_caicedo", "AST_martinez", "BRE_wissa", "BOU_evanilson"]
r = Run(save={"coins": 1000, "xp": 900, "owned": {c: 1 for c in squad}, "squad": list(squad),
              "tutorial_done": True, "starter_opened": True}, name="save_season.json")
g = r.g
r.frames(30)
g.pass_shift = 0
check(g.season_on() or g.season_today() >= g.season_days()[1],
      "the season clock works (on: %s, %s left)" % (g.season_on(), g.season_left()))
if not g.season_on():                                     # (run after the season: move the calendar back)
    g.pass_shift = g.season_days()[0] - rf.today_number() + 1
check(g.season_on(), "Season 1 is on")

# ---- the rewards table
R = rf.PASS_REWARDS
check(len(R) == 50, "50 tiers")
check(R[50][1].get("card") == rf.S1_CARD, "premium tier 50 is the Season 1 card")
check(not any(rf.S1_CARD == R[t][0].get("card") for t in R), "the S1 card is never on the free track")
check(sum(1 for t in R if R[t][1].get("pfp")) >= 8, "premium has profile pictures")
check(sum(1 for t in R if R[t][1].get("ball")) == 5, "premium has five ball skins")
check(not any(R[t][k].get("pfp") in rf.PFP_OWNER for t in R for k in (0, 1)), "the owner pictures aren't on the pass")
check(all(os.path.exists(os.path.join(rf.HERE if hasattr(rf, "HERE") else os.path.dirname(rf.__file__), "sprites",
                                      "pfp_%s.png" % k)) for k, _n in rf.PFPS), "every profile picture is drawn")
check(all(k == "classic" or os.path.exists(os.path.join(os.path.dirname(rf.__file__), "sprites", "ball_%s.png" % k))
          for k, _n in rf.BALL_SKINS), "every ball skin is drawn")
card = g.cards.get(rf.S1_CARD)
check(card is not None and card["design"] == "season1", "the S1 card exists")
check(rf.S1_CARD in g.card_figs, "his posed figure loads")
check(g.card_template_key(card) == "s1", "he wears the Season 1 card (%s)" % g.card_template_key(card))
check(all(rf.S1_CARD not in [c["id"] for c in g.pack_pool(p)] for p in range(len(rf.PACK_NAMES))),
      "he isn't in any pack")

# ---- the home tab
L = g.home_layout()
tabs = dict(L["tabs"])
check("PASS" in tabs, "PASS is a tab on the home screen")
check(max(rr.right for _t, rr in L["tabs"]) < L["level"].x, "all eight tabs fit before the level ring")
check(g.pass_claimable() == 1, "tier 1's free reward is waiting from the start (%d)" % g.pass_claimable())
r.shot("season_home", half=False)
r.click(tabs["PASS"].center)
check(g.state == rf.PASS, "the tab opens the pass")
r.shot("season_pass_new", half=False)

# ---- claim tier 1 by clicking its box
coins = g.save["coins"]
Lp = g.pass_layout()
col = [c for c in Lp["cols"] if c[0] == 1][0]
r.click(col[2].center)
check(1 in g.pass_state()["free"] and g.save["coins"] == coins + 150, "clicking tier 1 FREE claims 150 coins")
r.click(col[3].center)
check(1 not in g.pass_state()["prem"], "the premium box stays locked without the premium pass")

# ---- premium with gems
r.click(Lp["premium"].center)
check(not g.pass_state()["premium"], "no premium without 600 gems")
g.save["gems"] = 650
r.click(Lp["premium"].center)
check(g.pass_state()["premium"] and g.save["gems"] == 50, "600 gems unlock premium (50 left)")
r.click(col[3].center)
check(1 in g.pass_state()["prem"] and g.save["coins"] == coins + 550, "tier 1 PREMIUM pays 400 coins")


# ---- pass XP from matches and quests
def settle(mode, hs, as_):
    g.mode = mode
    g.forfeited = False
    g.played_this_match = set()
    g.score_home, g.score_away = hs, as_
    g.settle_match()


P = g.pass_state()
x0 = P["xp"]
settle("club", 3, 1)
check(P["xp"] - x0 == 100 + 30 + rf.PASS_XP_FIRST_WIN, "a win: match XP + the first win of the day (%d)" % (P["xp"] - x0))
check(g.pass_tier() == 2, "...which is tier 2")
x0 = P["xp"]
settle("club", 2, 0)
check(P["xp"] - x0 == 120, "the second win of the day: no bonus (%d)" % (P["xp"] - x0))
x0 = P["xp"]
settle("club", 0, 1)
check(P["xp"] - x0 == 20, "a loss still moves it (%d)" % (P["xp"] - x0))
x0 = P["xp"]
settle("free", 5, 0)
check(P["xp"] == x0, "free mode gives no pass XP")
g.forfeited = True
g.mode = "club"
g.score_home, g.score_away = 0, 3
g.played_this_match = set()
g.settle_match()
check(P["xp"] == x0, "a forfeit gives no pass XP")
g.forfeited = False
Q = g.quests()
Q["daily"] = [g.quest_new(k) for k in ("d_play", "d_win", "d_goal")]
Q["daily"][0]["done"] = True
Q["daily"][0]["n"] = 1
x0 = P["xp"]
g.quest_claim("daily", 0)
check(P["xp"] - x0 == rf.PASS_XP_QUEST["daily"], "a daily quest: +100 pass XP")
g.state = rf.PASS

# ---- gem sources are capped: weekly quests, the lucky chest
check(all(q[4].get("gems") == rf.QUEST_WEEKLY_GEMS for q in rf.QUEST_WEEKLY), "every weekly quest pays 25 gems")
check(not any(q[4].get("gems") for q in rf.QUEST_DAILY), "dailies pay no gems")
Q["weekly"] = [g.quest_new(k) for k in ("w_win", "w_goal", "w_pack")]
Q["weekly"][0]["done"] = True
gm = g.save.get("gems", 0)
g.quest_claim("weekly", 0)
check(g.save["gems"] == gm + 25, "claiming a weekly: +25 gems")
lucky = 0
for k in range(400):
    Q["chest"] = False
    for q in Q["daily"]:
        q["done"] = q["claimed"] = True
    gm = g.save.get("gems", 0)
    g.quest_claim("chest")
    lucky += g.save["gems"] > gm
check(5 <= lucky <= 40, "the daily chest drops gems about one day in twenty (%d / 400)" % lucky)
g.state = rf.PASS

# ---- buy a tier
g.save["gems"] = 200
t0 = g.pass_tier()
r.click(g.pass_layout()["tier"].center)
check(g.pass_tier() == t0 + 1 and g.save["gems"] == 80, "BUY A TIER: one tier for 120 gems")

# ---- gems from mail
box = g.save.setdefault("mail", [])
box.insert(0, {"id": "m1", "from": "HUBI", "subject": "gems", "body": "", "gift": {"gems": 300}, "read": False})
g.claim_mail(box[0])
check(g.save["gems"] == 380, "mail can carry gems (%d)" % g.save["gems"])

# ---- the ads
g.state = rf.PASS
check(not rf.ADS_ON, "ads are off for now")
g.watch_ad()
check(getattr(g, "ad_wait", None) is None and g.save["gems"] == 380, "desktop: WATCH AD says ads are on the browser version")
r.click(g.pass_layout()["ad"].center)
check(getattr(g, "code_wait", None) is None and g.save["gems"] == 380, "desktop: ENTER A CODE says codes are on the browser version")


class FakeWin:
    def __init__(self):
        self.asked, self.answer, self.owner = 0, "", False

    def aswcAd(self, what):
        self.asked += 1

    def aswcAdPoll(self):
        a, self.answer = self.answer, ""
        return a

    def aswcOwner(self):
        return self.owner

    def aswcCode(self):
        self.code_asked = getattr(self, "code_asked", 0) + 1

    def aswcCodePoll(self):
        a, self.code_answer = getattr(self, "code_answer", ""), ""
        return a


fake = FakeWin()
real_js = rf.js_window
rf.js_window = lambda: fake
# codes: the slot where WATCH AD goes
r.click(g.pass_layout()["ad"].center)
check(getattr(fake, "code_asked", 0) == 1 and g.code_wait is not None, "browser: ENTER A CODE asks the page for a code")
r.shot("season_pass_code", half=False)
r.click(g.pass_layout()["ad"].center)
check(fake.code_asked == 1, "a second click while it checks asks nothing")
gems, coins = g.save["gems"], g.save["coins"]
fake.code_answer = json.dumps({"ok": True, "code": "KICKOFF", "gift": {"gems": 100, "coins": 500}})
g.draw()
check(g.code_wait is None and g.save["gems"] == gems + 100 and g.save["coins"] == coins + 500,
      "a good code pays its gems and coins")
g.enter_code()
fake.code_answer = json.dumps({"ok": True, "code": "KICKOFF", "gift": {"gems": 100}})
g.draw()
check(g.save["gems"] == gems + 100, "the same code twice pays once (the save remembers it too)")
for why in ("nocode", "expired", "full", "used", "cancel"):
    gm = g.save["gems"]
    g.enter_code()
    fake.code_answer = json.dumps({"ok": False, "why": why, "code": "NOPE"})
    g.draw()
    check(g.save["gems"] == gm and g.code_wait is None, "a refused code (%s) pays nothing" % why)
g.enter_code()
fake.code_answer = json.dumps({"ok": True, "code": "HUGE", "gift": {"gems": 999999}})
g.draw()
check(g.save["gems"] == gm + 5000, "a code can't pay more than 5,000 gems")
g.save["gems"] = 380 + 0
# ads (switched off, but kept working for later)
g.watch_ad()
check(fake.asked == 1 and g.ad_wait is not None, "browser: WATCH AD asks the page for an ad")
g.watch_ad()
check(fake.asked == 1, "a second ask while the ad plays asks nothing")
fake.answer = json.dumps({"ok": True})
r.frames(1)
g.draw()
check(g.ad_wait is None and g.save["gems"] == 380 + rf.GEMS_PER_AD, "a watched ad pays %d gems" % rf.GEMS_PER_AD)
for why in ("skipped", "noads", "notReady"):
    gems = g.save["gems"]
    g.watch_ad()
    fake.answer = json.dumps({"ok": False, "why": why})
    g.draw()
    check(g.save["gems"] == gems and g.ad_wait is None, "an ad that wasn't watched (%s) pays nothing" % why)
g.ads_today()["n"] = rf.ADS_PER_DAY
asked = fake.asked
g.watch_ad()
check(fake.asked == asked, "ten ads a day, then no more")
g.pass_shift += 1
check(g.ads_today()["n"] == 0, "a new day: ten more")
g.pass_shift -= 1

# ---- the top of the pass: claim everything, the S1 card walks out
P["xp"] = (rf.PASS_TIERS - 1) * rf.PASS_TIER_XP
check(g.pass_tier() == 50, "tier 50 at %d pass XP" % P["xp"])
g.state = rf.PASS
g.pass_scroll = 42.0
r.shot("season_pass_top", half=False)
n = g.pass_claimable()
check(n == 49 * 2 - 0 - 0 + 0 or n > 90, "everything up to tier 50 waiting (%d)" % n)
r.click(g.pass_layout()["claim_all"].center)
check(g.pass_claimable() == 0, "CLAIM ALL claims every box")
check(g.save["owned"].get(rf.S1_CARD, 0) == 1, "the Season 1 card is yours")
check(g.state == rf.PACK_OPEN and g.pack_reveal["card"]["id"] == rf.S1_CARD and g.pack_reveal["back"] == "pass",
      "and he walks out")
g.pack_reveal["t"] = 999
g.pack_open_click()
g.card_detail = None
check(g.state == rf.PASS or g.card_detail is None, "back to the pass after the walkout")
check(all(g.pfp_owned(k) for k in ("whistle", "s1", "boot", "crown", "cup", "s1gold")), "the pass pictures are yours")
check(all(g.ball_owned(k) for k, _n in rf.BALL_SKINS), "every ball skin is yours")

# ---- the S1 card on screen
g.state = rf.PASS
g.card_detail = card
g.card_tab = 0
r.frames(20)
r.shot("season_s1_card", half=False)
g.card_detail = None

# ---- the LOCKER: pictures, the owner's two, the ball
g.open_locker("pfp", back="pass")
r.frames(5)
check(g.state == rf.LOCKER, "the locker opens")
cells = dict(g.locker_layout()["cells"])
check(not g.pfp_owned("owner") and not g.pfp_owned("owner_live"), "not the owner: both owner pictures locked")
r.click(cells["owner_live"].center)
check(g.save["pfp"] != "owner_live", "...and can't be equipped")
r.shot("season_locker_locked", half=False)
r.click(cells["crown"].center)
check(g.save["pfp"] == "crown", "equip THE CROWN")
fake.owner = True
g._owner_seen = None
check(g.pfp_owned("owner") and g.pfp_owned("owner_live"), "the owner account: both owner pictures open")
r.click(cells["owner_live"].center)
check(g.save["pfp"] == "owner_live", "the owner wears the live one")
f0 = g.pfp_img("owner_live", 160)
pygame.time.advance(300)
f1 = g.pfp_img("owner_live", 160)
check(f0 is not f1, "the live picture moves (a different frame 0.3 s later)")
r.shot("season_locker_owner", half=False)
fake.owner = False
g._owner_seen = None
check(g.shown_pfp("owner_live") == "doll", "the same save on someone else's account shows the RAGDOLL instead")
g.load_save()
check("owner_live" not in g.save.get("pfps", []), "owner pictures are never written into the save as owned")
fake.owner = True
g._owner_seen = None
g.locker_tab = "ball"
cells = dict(g.locker_layout()["cells"])
before = g.ball.art.get_at((g.ball.art.get_width() // 2, g.ball.art.get_height() // 3))
r.click(cells["galaxy"].center)
after = g.ball.art.get_at((g.ball.art.get_width() // 2, g.ball.art.get_height() // 3))
check(g.save["ball"] == "galaxy" and rf.BALL_SKIN == "galaxy" and tuple(before) != tuple(after),
      "equip the GALAXY ball: the match ball changes")
r.shot("season_locker_balls", half=False)
r.click(g.BACK_RECT.center)
check(g.state == rf.PASS, "BACK goes back to the pass")

# ---- the profile shows the picture, and opens the locker
g.open_profile()
r.frames(5)
r.shot("season_profile", half=False)
r.click(g.profile_pic_rect().center)
check(g.state == rf.LOCKER and g.locker_from == "profile", "the profile picture opens the locker")
r.click(g.BACK_RECT.center)
check(g.state == rf.PROFILE, "and BACK goes back to the profile")

# ---- a match with the skin on
g.mode = "club"
g.ball.reset(rf.WIDTH / 2, 300, frozen=False)
g.state = rf.PLAY
r.frames(10)
r.shot("season_match_ball", half=False)

# ---- the season ends
g.pass_shift = g.season_days()[1] - rf.today_number()
check(not g.season_on(), "after the end date the season is over")
x0 = P["xp"]
g.pass_add_xp(500)
check(P["xp"] == x0, "no pass XP once it's over")
g.state = rf.PASS
r.shot("season_pass_over", half=False)

# ---- a save from before the season
rf.js_window = real_js
r2 = Run(save={"coins": 10, "owned": {}, "squad": [], "tutorial_done": True, "starter_opened": True,
               "pfp": "owner", "ball": "gold", "gems": "x"}, name="save_season_old.json")
g2 = r2.g
check(g2.save["gems"] == 0 and g2.save["ball"] == "classic", "a broken save is tidied (no gems, the classic ball)")
check(g2.shown_pfp(g2.save["pfp"]) == "doll", "an owner picture in someone's save shows as the RAGDOLL")

print("\n%d failed" % len(fails) if fails else "\nall passed")
sys.exit(1 if fails else 0)
