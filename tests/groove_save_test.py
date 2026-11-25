#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 RIDDIM (after COQUÍ's tests/perc/groove_save_test.py, the same author)
# RIDDIM: a DRUM track's GROOVE is saved and comes back (host mode). ONE DROP KIT loaded (its GROOVE: ONE DROP, ALL,
# FILL /4, FEEL 0), then on the GROOVE page STYLE +2 (STEPPERS), FILL +1 (/8), FEEL -10; the autosave; a new start from
# those saves: all as left.
#   python3 tests/groove_save_test.py build/host/riddim
import os
import re
import subprocess
import sys
from pathlib import Path

BIN = sys.argv[1] if len(sys.argv) > 1 else "build/host/riddim"
OUT = Path("build/host/groove_save")
OUT.mkdir(parents=True, exist_ok=True)


def run(name, events, end, env=None):
    script = OUT / f"{name}.txt"
    script.write_text("".join(f"{t} {e}\n" for t, e in events) + f"{end} end\n")
    r = subprocess.run([BIN, str(OUT / name), str(script)], capture_output=True, text=True, env=env or os.environ)
    return re.findall(r"eng (\d+).*? grv (-?\d+),(-?\d+),(-?\d+),(-?\d+)", r.stdout)


bad = 0


def check(what, ok, got):
    global bad
    bad += not ok
    print(f"  {'ok  ' if ok else 'FAIL'}  groove save: {what}" + ("" if ok else f" ({got})"))


saves = OUT / "saves.bin"
p = run("set", [(6000, "enc 6 31"), (6200, "probe"), (6400, "btn 6"), (6500, "btn 6"), (6600, "enc 2 2"), (6700, "enc 4 1"),
                (6800, "enc 5 -10"), (6900, "probe")], 30000, dict(os.environ, GRIMM_SAVE_OUT=str(saves)))
check("ONE DROP KIT brings its GROOVE (ONE DROP, ALL, FILL /4, FEEL 0)", p[:1] == [("3", "1", "0", "2", "0")], p)
check("the GROOVE page's knobs move it (STEPPERS, FILL /8, FEEL -10)", p[1:2] == [("3", "3", "0", "3", "-10")], p)
q = run("load", [(6500, "probe")], 6600, dict(os.environ, GRIMM_SAVE_IN=str(saves)))
check("after a new start: DRUM, STEPPERS, FILL /8, FEEL -10, as left", q == [("3", "3", "0", "3", "-10")], q)
print("groove save test: passed" if not bad else "groove save test: FAILED")
sys.exit(1 if bad else 0)
