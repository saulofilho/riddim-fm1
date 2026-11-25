#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 RIDDIM
"""RIDDIM's band lines (firmware/src/arp.c: SKANK .. HORNS) in host mode: a factory sound that brings a line, an A minor
chord held (A3 C4 E4), the ARP's notes seen by the probe every 5 ms ("srcs": source 2, the arp's). Each line plays its
chord tones on its steps, in its register; and it plays like a musician, never a machine: its notes land a little
behind the grid by different amounts, their lengths differ. A factory sound without a line switches a line off.
  python3 tests/band_test.py build/host/riddim"""
import subprocess
import sys
from pathlib import Path

BIN = sys.argv[1] if len(sys.argv) > 1 else "build/host/riddim"
OUT = Path("build/host/band")
OUT.mkdir(parents=True, exist_ok=True)
SRC_ARP = 2
CHORD = 1 << 4 | 1 << 7 | 1 << 11               # A3 C4 E4 (keys from F3)
STEP = 60000 / 120 / 4                          # (the tempo as it starts: 120 BPM; a sixteenth, ms)
bad = 0


def check(what, ok, got=""):
    global bad
    bad += not ok
    print(f"  {'ok  ' if ok else 'FAIL'}  band: {what}" + ("" if ok else f" ({got})"))


def run(name, preset, hold=6200, end=10300, extra=()):
    ev = [(6000, f"enc 6 {preset}"), (hold, f"keys {CHORD:#x}")] + list(extra) + [(end - 50, "keys 0")]
    ev += [(t, "probe") for t in range(hold, end - 100, 5)]
    script = OUT / f"{name}.txt"
    script.write_text("".join(f"{t} {e}\n" for t, e in sorted(ev, key=lambda x: x[0])) + f"{end} end\n")
    out = subprocess.run([BIN, str(OUT / name), str(script)], capture_output=True, text=True, check=True).stdout
    frames = []
    for ln in out.splitlines():
        if ln.startswith("probe ") and " srcs" in ln:
            ms = int(ln.split()[1])
            on = {int(s.split(":")[2]) for s in ln.split(" srcs")[1].split(" /srcs")[0].split() if int(s.split(":")[0]) == SRC_ARP}
            frames.append((ms, on))
    return hold, frames


def onsets(frames):                             # [(ms, notes that began), ...] and each note's length
    ev, prev, start, lens = [], set(), {}, []
    for ms, on in frames:
        new = on - prev
        if new: ev.append((ms, new))
        for n in new: start[n] = ms
        for n in prev - on:
            if n in start: lens.append(ms - start.pop(n))
        prev = on
    return ev, lens


def grid(hold, ms):                             # its step (from the first note held) and how late after it (ms)
    x = (ms - hold) / STEP
    s = int(x + 0.15)
    return s, ms - hold - s * STEP


# PRESETS (1-based): BASS 1..6, PAD 7..12, LEAD 13..18, ORGAN 19..20, KEYS 21..29, FX 30, DRUMS 31..39, SECTION 40..44
SKANK_PIANO, SKANK_GUITAR, FM_GUITAR, BUBBLE, ROUND_BASS, STEPPER_BASS, DUB_BASS, HORN_LINE = 21, 24, 27, 19, 5, 2, 3, 18
UPRIGHT = 22

hold, fr = run("skank", SKANK_PIANO)
ev, lens = onsets(fr)
steps = [grid(hold, ms) for ms, _ in ev]
lates = sorted({round(l) for s, l in steps})
check("SKANK PIANO: the chop on 2 and 4 (steps 4, 12, 20, 28 ...), the whole chord (A3 C4 E4)",
      len(ev) >= 4 and all(s % 8 == 4 for s, _ in steps if not (s % 8 == 5)) and all(n == {57, 60, 64} or n <= {57, 60, 64} for _, n in ev),
      [(s, sorted(n)) for (s, _), (_, n) in zip(steps, ev)][:8])
check("SKANK PIANO: laid back, never the same twice (a chop behind the grid by several amounts)",
      len(lates) >= 2 and all(-2 <= l <= 25 for _, l in steps), lates)
check("SKANK PIANO: short chops (a third of a step and more under a sixteenth's 125 ms)", lens and max(lens) < 125, lens[:8])

hold, fr = run("skankg", SKANK_GUITAR)
ev, _ = onsets(fr)
check("SKANK GUITAR: its chop an octave up (A4 C5 E5)", ev and all(n <= {69, 72, 76} for _, n in ev), [sorted(n) for _, n in ev][:4])

hold, fr = run("bubble", BUBBLE)
ev, _ = onsets(fr)
steps = [grid(hold, ms)[0] % 4 for ms, _ in ev]
check("BUBBLE ORGAN: the off-beat eighth and the sixteenth after (steps 2, 3 of each beat), the chord",
      len(ev) >= 8 and all(s in (2, 3, 0) for s in steps) and all(n <= {57, 60, 64} for _, n in ev), steps[:12])

hold, fr = run("bass", ROUND_BASS)
ev, lens = onsets(fr)
notes = [sorted(n)[0] for _, n in ev]
check("ROUND BASS: the one drop's bass an octave under (A2 first, then the chord's tones, the octave)",
      notes and notes[0] == 45 and set(notes) <= {45, 48, 52, 57}, notes[:10])
check("ROUND BASS: its notes' lengths not all alike", len(set(round(l / 10) for l in lens)) >= 3, lens[:10])

hold, fr = run("stepbass", STEPPER_BASS)
ev, _ = onsets(fr)
notes = [sorted(n)[0] for _, n in ev]
check("STEPPER BASS: driving, on the beats, an octave under", len(ev) >= 8 and set(notes) <= {45, 48, 52, 57}, notes[:10])

hold, fr = run("dubbass", DUB_BASS)
ev, _ = onsets(fr)
check("DUB BASS (PHYS): the same bass line", ev and sorted(ev[0][1])[0] == 45, [sorted(n) for _, n in ev][:4])

hold, fr = run("horns", HORN_LINE, end=11800)
ev, _ = onsets(fr)
notes = [sorted(n)[0] for _, n in ev]
check("HORN LINE: the answer at the phrase's end, falling E4 C4 A3", notes[:3] == [64, 60, 57], notes[:6])

hold, fr = run("off", SKANK_PIANO, extra=[(7000, f"enc 6 {UPRIGHT - SKANK_PIANO}"), (7100, "keys 0"), (7200, f"keys {CHORD:#x}")])
ev, _ = onsets([f for f in fr if f[0] > 7300])
check("a factory sound without a line (UPRIGHT PIANO) switches the line off", not ev, ev[:3])

print("band test: passed" if not bad else "band test: FAILED")
sys.exit(1 if bad else 0)
