#!/bin/sh
# Render layout/map.html to entry.png (1024x1024) with headless Chrome.
# If the PNG is over 1 MiB, re-encode as a high-quality JPEG but keep the name entry.png.
# Optional: PREVIEW_DIR=<dir> also writes a 300 px preview there.
set -eu
cd "$(dirname "$0")"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT="$PWD/entry.png"
TMP="$PWD/.render-tmp.png"

"$CHROME" --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size=1024,1024 --virtual-time-budget=3000 \
  --screenshot="$TMP" "file://$PWD/layout/map.html" >/dev/null 2>&1

SIZE=$(stat -f %z "$TMP")
if [ "$SIZE" -gt 1048576 ]; then
  sips -s format jpeg -s formatOptions 92 "$TMP" --out "$PWD/.render-tmp.jpg" >/dev/null
  mv "$PWD/.render-tmp.jpg" "$OUT"
  rm -f "$TMP"
else
  mv "$TMP" "$OUT"
fi

echo "entry.png: $(stat -f %z "$OUT") bytes, $(sips -g pixelWidth -g pixelHeight "$OUT" | awk '/pixel/ {printf "%s ", $2}')"

if [ -n "${PREVIEW_DIR:-}" ]; then
  sips -Z 300 "$OUT" --out "$PREVIEW_DIR/preview300.png" >/dev/null
  echo "preview: $PREVIEW_DIR/preview300.png"
fi
