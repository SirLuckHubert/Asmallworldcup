#!/usr/bin/env python3
"""Local test server for aSmallWorldCup.

    python3 web/serve_local.py          ->  http://localhost:8000

Why this exists instead of `python3 -m http.server`:

pygbag switches into DEV MODE whenever the page is served from localhost, and then it
fetches the Python and pygame runtime from  <your server>/cdn/...  instead of the real
CDN. A plain web server has nothing there, so you get:

    Async I/O error : file not found http://localhost:8000/cdn/cp312/pygame_ce-...whl
    ImportError: cannot import name 'Vector2' from 'pygame'

...and a grey canvas. This server answers those /cdn/ requests by redirecting them to
pygame-web.github.io, which is exactly where the live GitHub Pages site gets them from.
So what you see here is what you get once you push.
"""
import http.server
import os
import re
import socketserver
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CDN = "https://pygame-web.github.io/cdn/"
FALLBACK_VERSION = "0.9.3"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


def cdn_version():
    """Read the pygbag version out of the built page so the redirect matches it."""
    page = os.path.join(HERE, "game", "index.html")
    try:
        with open(page, "r", encoding="utf-8", errors="ignore") as fh:
            hit = re.search(r"pygame-web\.github\.io/cdn/(\d+\.\d+[\.\d]*)/", fh.read())
        if hit:
            return hit.group(1)
    except OSError:
        pass
    return FALLBACK_VERSION


VERSION = cdn_version()


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

    def _cdn_target(self):
        rest = self.path[len("/cdn/"):].split("#")[0].split("?")[0].lstrip("/")
        if not rest:
            return None
        if rest.startswith("index") or re.match(r"^\d+\.\d+", rest):
            return CDN + rest                      # already carries its own version
        return CDN + VERSION + "/" + rest

    def do_GET(self):
        if self.path.startswith("/cdn/"):
            target = self._cdn_target()
            if target:
                self.log_message("cdn -> %s", target)
                self.send_response(302)
                self.send_header("Location", target)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
        super().do_GET()

    def do_HEAD(self):
        if self.path.startswith("/cdn/"):
            return self.do_GET()
        super().do_HEAD()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")   # always test the newest build
        super().end_headers()


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    game = os.path.join(HERE, "game", "index.html")
    if not os.path.exists(game):
        print("!! web/game/ isn't built yet - run:  bash web/build_web.sh")
    print("aSmallWorldCup dev server")
    print("  serving      : %s" % HERE)
    print("  pygbag CDN   : %s%s/  (redirecting /cdn/ there for you)" % (CDN, VERSION))
    print("  open         : http://localhost:%d" % PORT)
    print("  the game only: http://localhost:%d/game/" % PORT)
    print("  stop         : Ctrl+C")
    with Server(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nbye")
