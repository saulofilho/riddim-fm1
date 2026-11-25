#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 RIDDIM
"""The manual's screens (docs/screens/*.png), drawn by the firmware itself in host mode: each page reached as a player
would (the buttons, the knobs), its last frame saved at 480 x 480. Needs a host build (build/host/riddim:
tests/run_host.sh makes it) and Pillow; the host build is Linux: on a Mac, in a container:
  docker run --rm -v "$PWD":/work -w /work python:3.12-bookworm sh -c "pip install -q Pillow; python3 tools/gen_screens.py"
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "build" / "host" / "riddim"
OUT = ROOT / "build" / "screens"
SCREENS = ROOT / "docs" / "screens"
B = 6000                                        # (after the boot screen)
FX, SEL, ENV, LFO, EDIT, GLO, HOME, SAVE, ARP, SEQ, PLAY = 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
ONE_DROP, FROZEN_HALL = 31, 9                   # (PRESETS: the first DRUM kit; an FM pad)


def btn(t, b):
    return [(t, f"btn {b}")]


def beat(t0):                                   # a few hits on a DRUM track (HOME's cones, the kit's picture)
    ev = []
    for i, k in enumerate((0, 1, 2, 1, 0, 5)):
        ev += [(t0 + 120 * i, f"keys {1 << k:#x}"), (t0 + 120 * i + 30, "keys 0")]
    return ev


SHOTS = {
    "boot": ([], 3600),
    "home": ([(B, f"enc 6 {ONE_DROP}"), (B + 100, "enc 1 1"), (B + 200, f"enc 6 {FROZEN_HALL}"), (B + 300, "enc 1 -1"),
              (B + 400, "down 7"), (B + 420, "keys 0x10"), (B + 440, "keys 0"), (B + 460, "up 7")] + beat(B + 800), B + 1460),
    "mixer1": (btn(B, HOME), B + 600),
    "va": (btn(B, EDIT), B + 600),
    "drum": ([(B, f"enc 6 {ONE_DROP}")] + btn(B + 200, EDIT) + beat(B + 500), B + 1210),
    "groove": ([(B, f"enc 6 {ONE_DROP}")] + btn(B + 200, EDIT) + btn(B + 300, EDIT) + btn(B + 400, PLAY), B + 2650),
    "arp-line": ([(B, "enc 6 21"), (B + 300, "keys 0x890")] + btn(B + 400, ARP), B + 1700),   # (SKANK PIANO, A minor held)
    "fm-algo": ([(B, f"enc 6 {FROZEN_HALL}")] + btn(B + 200, EDIT) + btn(B + 300, EDIT), B + 900),
    "fm-op": ([(B, f"enc 6 {FROZEN_HALL}")] + btn(B + 200, EDIT) + btn(B + 300, EDIT) + btn(B + 400, EDIT), B + 1000),
    "env": (btn(B, ENV), B + 600),
    "lfo": (btn(B, LFO), B + 600),
    "scale": (btn(B, SEL), B + 600),
    "chord": (btn(B, SEL) + btn(B + 200, SEL), B + 800),
    "arp": (btn(B, ARP), B + 600),
    "seq": ([(B, f"enc 6 {ONE_DROP}")] + btn(B + 200, SEQ), B + 800),
    "save": (btn(B, SAVE), B + 600),
    "song": (btn(B, GLO), B + 600),
    "tape": (btn(B, FX), B + 600),
    "perform": ([(B, f"down {FX}")], B + 1500),
    "system": ([(B, f"down {HOME}"), (B + 800, f"up {HOME}")], B + 1300),
    "system2": ([(B, f"down {HOME}"), (B + 800, f"up {HOME}")] + btn(B + 1000, HOME), B + 1500),
    "system3": ([(B, f"down {HOME}"), (B + 800, f"up {HOME}")] + btn(B + 1000, HOME) + btn(B + 1200, HOME), B + 1700),
}


def main():
    if not BIN.exists():
        sys.exit("gen_screens: no build/host/riddim (run tests/run_host.sh first)")
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (ev, end) in SHOTS.items():
        for old in OUT.glob(f"{name}-*.ppm"):
            old.unlink()
        script = OUT / f"{name}.txt"
        script.write_text("".join(f"{t} {e}\n" for t, e in sorted(ev, key=lambda x: x[0])) + f"{end} end\n")
        subprocess.run([str(BIN), str(OUT / name), str(script), "4"], check=True, capture_output=True)
        frames = sorted(OUT.glob(f"{name}-*.ppm"))
        if not frames:
            sys.exit(f"gen_screens: {name}: no frame")
        Image.open(frames[-1]).resize((480, 480), Image.NEAREST).save(SCREENS / f"{name}.png", optimize=True)
        print(f"{name:<8} -> docs/screens/{name}.png ({frames[-1].name})")


if __name__ == "__main__":
    main()
