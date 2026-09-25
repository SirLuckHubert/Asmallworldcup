#!/usr/bin/env python3
"""Stamp a new build string everywhere, so browsers can't serve half of an old upload.

    python3 bump_build.py            # today's date + a letter
    python3 bump_build.py 2026-10-01b

It rewrites the ?v= query on the stylesheet and every local script, the --build marker in
style.css, the footer tag, check.html's expected build, and the ?v= on the modules that
app.js / play.js / admin.js import (ES modules are cached separately from the page).
"""
import datetime
import os
import re
import string
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = ["index.html", "admin.html", "play.html", "check.html", "style.css"]
SCRIPTS = ["app.js", "admin.js", "play.js", "net.js", "ranks.js", "words.js", "titles.js", "mail.js"]
LOCAL_MODULES = SCRIPTS + ["firebase-config.js"]
STAMPED = ["style.css"] + SCRIPTS
OLD = re.compile(r"\d{4}-\d{2}-\d{2}[a-z]")


def read(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return fh.read()


def write(name, text):
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as fh:
        fh.write(text)


def current():
    m = OLD.search(read("style.css"))
    return m.group(0) if m else ""


def next_build():
    today = datetime.date.today().isoformat()
    now, letters = current(), string.ascii_lowercase
    if now.startswith(today) and now[-1] in letters:
        step = letters.index(now[-1]) + 1
        return today + letters[min(step, len(letters) - 1)]
    return today + "a"


def main():
    build = sys.argv[1] if len(sys.argv) > 1 else next_build()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}[a-z]", build):
        sys.exit("build should look like 2026-10-01b")
    was = current()
    for name in PAGES + SCRIPTS:
        text = read(name)
        fixed = text
        for target in STAMPED:                      # <script src="app.js?v=...">
            fixed = re.sub(re.escape(target) + r"\?v=" + OLD.pattern, target + "?v=" + build, fixed)
        for target in LOCAL_MODULES:                # import ... from "./ranks.js?v=..."
            fixed = re.sub(r'(\./' + re.escape(target) + r')(\?v=' + OLD.pattern + r')?(")',
                           r'\g<1>?v=' + build + r'\g<3>', fixed)
        fixed = fixed.replace('--build: "%s"' % was, '--build: "%s"' % build)
        fixed = fixed.replace('EXPECTED_BUILD = "%s"' % was, 'EXPECTED_BUILD = "%s"' % build)
        fixed = fixed.replace("build %s" % was, "build %s" % build)
        if fixed != text:
            write(name, fixed)
            print("stamped", name)
    print("build is now", build, "(was %s)" % (was or "unset"))


if __name__ == "__main__":
    main()
