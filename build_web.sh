#!/usr/bin/env bash
# Builds the browser version of the game into web/game/ with pygbag.
#
#   cd <this repo>
#   bash web/build_web.sh
#
# Needs python 3.10+ and: pip install pygbag
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
STAGE="$ROOT/.web-build/aswc"
OUT="$HERE/game"

echo "==> staging the game in $STAGE"
rm -rf "$ROOT/.web-build"
mkdir -p "$STAGE"

# pygbag wants the entry point to be called main.py
cp "$ROOT/ragdoll_football.py" "$STAGE/main.py"

# assets: sprites, flags and the music/sfx (ogg only - browsers don't decode our mp3s reliably)
mkdir -p "$STAGE/sprites"
cp -r "$ROOT/sprites/." "$STAGE/sprites/" 2>/dev/null || true
for f in "$ROOT"/*.png; do [ -e "$f" ] && cp "$f" "$STAGE/"; done
shopt -s nullglob
oggs=("$ROOT"/*.ogg)
if [ ${#oggs[@]} -eq 0 ]; then
  echo "!! no .ogg files found next to the game - the web build will be silent."
  echo "   convert them once with:  for f in *.mp3; do ffmpeg -i \"\$f\" -c:a libvorbis -q:a 4 \"\${f%.mp3}.ogg\"; done"
else
  cp "${oggs[@]}" "$STAGE/"
fi
shopt -u nullglob

echo "==> pygbag build (this downloads the python-wasm runtime the first time)"
python3 -m pygbag --build --ume_block 0 --template default.tmpl "$STAGE"

echo "==> copying into $OUT"
rm -rf "$OUT"
mkdir -p "$OUT"
cp -r "$STAGE/build/web/." "$OUT/"
cp "$HERE/bridge.js" "$OUT/bridge.js"

# hook the save bridge into the generated page
python3 - "$OUT/index.html" <<'PY'
import sys, io
path = sys.argv[1]
html = io.open(path, encoding="utf-8").read()
tag = '<script src="bridge.js"></script>'
if tag not in html:
    html = html.replace("</head>", "  " + tag + "\n</head>", 1)
    io.open(path, "w", encoding="utf-8").write(html)
    print("bridge.js hooked into", path)
else:
    print("bridge.js already hooked in")
PY

echo
echo "Done. Test it locally with:"
echo "    python3 -m http.server -d \"$HERE\" 8000    # then open http://localhost:8000"
echo "Then commit web/ and push - GitHub Pages serves it from that folder."
