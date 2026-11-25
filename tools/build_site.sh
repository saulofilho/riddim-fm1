#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 RIDDIM
# RIDDIM's site, as GitHub Pages serves it (.github/workflows/pages.yml):
#   site/            the front page and its pictures
#   web/dist/        -> emu/        the web emulator and the editor (web/build_web.sh first)
#   docs/moodboard/  -> moodboard/
#   tools/build_site.sh [OUT]   (default build/site)
set -e
cd "$(dirname "$0")/.."
OUT="${1:-build/site}"
[ -f web/dist/riddim.wasm ] || { echo "build_site: no web/dist/riddim.wasm (run web/build_web.sh first)"; exit 1; }
rm -rf "$OUT"
mkdir -p "$OUT"
cp -R site/. "$OUT/"
mkdir -p "$OUT/emu" "$OUT/moodboard"
cp -R web/dist/. "$OUT/emu/"
cp -R docs/moodboard/. "$OUT/moodboard/"
touch "$OUT/.nojekyll"
echo "site: $OUT ($(find "$OUT" -type f | wc -l | tr -d ' ') files)"
