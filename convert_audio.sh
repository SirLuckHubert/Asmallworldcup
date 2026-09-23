#!/usr/bin/env bash
# Turn the game's mp3s into the .ogg files the browser build needs.
# Run it once, from the folder the game lives in:   bash web/convert_audio.sh
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command -v ffmpeg >/dev/null || { echo "ffmpeg isn't installed - get it from ffmpeg.org"; exit 1; }
shopt -s nullglob
made=0
for f in "$HERE"/*.mp3; do
  out="${f%.mp3}.ogg"
  [ -e "$out" ] && { echo "skip  $(basename "$out") (already there)"; continue; }
  ffmpeg -loglevel error -i "$f" -c:a libvorbis -q:a 4 "$out"
  echo "made  $(basename "$out")"
  made=$((made + 1))
done
echo "$made file(s) converted. The game prefers .ogg now, so you can delete the mp3s if you like."
