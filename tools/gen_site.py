#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 RIDDIM (after COQUÍ's tools/gen_hub.py, the same author)
"""RIDDIM's site (site/): its sounds and data, made from the firmware itself, in host mode.

  site/audio/kit-NN.mp3   each factory DRUM kit (PRESETS 31 .. 39) playing a beat in its style, four bars, at its tempo:
                          the beat played on the keys (MIDI notes), as a drummer would; the styles that play by
                          themselves are the next step (PLAN.md, Fase 3)
  site/audio/keys.mp3     the 27 keys of the ONE DROP KIT one after another (site/riddim-data.js: where each starts)
  site/audio/demo.mp3     a longer one-drop take (the live view's DEMO, the front page's first sound)
  site/riddim-data.js     the kits, their beats as grids, the keys' names, the version

Needs a host build (build/host/riddim: tests/run_host.sh makes it) and ffmpeg (FFMPEG, or imageio-ffmpeg). The host
build is Linux: on a Mac, in a container:
  docker run --rm -v "$PWD":/work -w /work python:3.12-bookworm sh -c "pip install -q imageio-ffmpeg; python3 tools/gen_site.py"
"""
import argparse
import array
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
BIN = ROOT / "build" / "host" / "riddim"
FS = 44100
BOOT_MS = 6000                                  # (the boot screen: inputs after it)
LO = 53                                         # (F3: the kit's first key)

# the keys (drum.c's DKEY order), by name
K = {n: i for i, n in enumerate(["KICK", "HAT", "CROSS", "PEDAL", "SNARE", "OHAT", "RIM", "TOML", "SHAKE", "TOMM", "COWB",
                                 "TOMH", "SKICK", "WOOD", "SYN", "SYNHI", "SYNLO", "STICKS", "SPRING", "FLOOR",
                                 "CROSSHI", "TIMB", "RIDE", "CRASH", "DKICK", "SNAREHI", "SPRINGHI"])}

# the beats: a bar of 16 steps a lane ('X' accented, 'x' played, 'o' soft, '.' none); the fourth bar's fill replaces
# the lanes it names; tempo (BPM) and shuffle (the off 16ths late, % of a step)
KITS = [
    ("ONE DROP KIT", "ONE DROP", 76, 18, {
        "HAT": "x.o.x.o.x.o.x.o.", "KICK": "........X.......", "CROSS": "........X......."},
     {"TOMH": "............x...", "TOMM": ".............x..", "TOML": "..............xx", "CROSS": "........X......."}),
    ("ROCKERS KIT", "ROCKERS", 80, 12, {
        "HAT": "xoxoxoxoxoxoxoxo", "KICK": "X.......X.......", "RIM": "........X.......", "OHAT": "..............x."},
     {"SNARE": "........x.x.xxxx", "HAT": "xoxoxoxo........"}),
    ("STEPPERS KIT", "STEPPERS", 76, 10, {
        "SKICK": "X...X...X...X...", "HAT": "..x...x...x...x.", "RIM": "........X.......", "PEDAL": "x...x...x...x..."},
     {"TOMH": "........x.x.....", "TOMM": "............x.x.", "SKICK": "X...X...X...X..."}),
    ("DUB KIT", "DUB", 72, 18, {
        "HAT": "x...o...x...o...", "KICK": "........X.......", "CROSS": "........X.......", "SHAKE": "..o...o...o...o."},
     {"SPRING": "........X.......", "SYNLO": "..............x."}),
    ("RUB-A-DUB KIT", "RUB-A-DUB", 88, 8, {
        "KICK": "X.......X.......", "SNAREHI": "....X.......X...", "HAT": "x.x.x.x.x.x.x.x.", "SYN": "..............x."},
     {"SYNHI": "........x.x.....", "SYN": "............x.x.", "SYNLO": "..............x."}),
    ("ROCKSTEADY KIT", "ROCKSTEADY", 96, 30, {
        "KICK": "X.......X.......", "CROSS": "....X.......X...", "HAT": "x.ox.ox.x.ox.ox.", "RIDE": "x...x...x...x..."},
     {"SNARE": "............xxxx"}),
    ("DEEP ROOTS KIT", "ONE DROP, LOW", 70, 20, {
        "HAT": "x.o.x.o.x.o.x.o.", "KICK": "........X.......", "CROSS": "........X.......", "FLOOR": "..............o."},
     {"FLOOR": "........X...x.x.", "TOML": "............x..."}),
    ("TIGHT KIT", "ROCKERS, TIGHT", 84, 6, {
        "HAT": "xxxxxxxxxxxxxxxx", "KICK": "X.......X.......", "SNARE": "........X.......", "WOOD": "......x.......x."},
     {"SNARE": "........x.xxxxxx"}),
    ("BOOMY KIT", "STEPPERS, BOOM", 74, 14, {
        "DKICK": "X...X...X...X...", "HAT": "..x...x...x...x.", "RIM": "........X.......", "CRASH": "X..............."},
     {"TOML": "........x.x.x.x.", "CRASH": "X..............."}),
]
VEL = {"X": 127, "x": 104, "o": 66}


def ffmpeg():
    ff = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if ff:
        return ff
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("gen_site: no ffmpeg (set FFMPEG, or pip install imageio-ffmpeg)")


def key_names():
    d = (ROOT / "firmware" / "src" / "drum.c").read_text()
    body = d[d.index("DKEY_NAME[DK_N] = {"):]
    return re.findall(r'"([^"]+)"', body[:body.index("};")])


# SYSTEM 3's VELOCITY on (as tests/play_test.py): a MIDI note's volume from how hard, the beats' accents and ghost notes
VEL_ON = [(500, "down 8"), (1300, "up 8"), (1400, "btn 8"), (1500, "btn 8"), (1600, "enc 3 1"), (1700, "btn 6"),
          (1800, "btn 8")]


def host(name, events, end_ms, out):
    events = VEL_ON + list(events)
    script = out / f"{name}.txt"
    script.write_text("".join(f"{t} {e}\n" for t, e in sorted(events, key=lambda x: x[0])) + f"{end_ms} end\n")
    subprocess.run([str(BIN), str(out / name), str(script)], check=True, capture_output=True,
                   env=dict(os.environ, GRIMM_MASTER="1022"))
    with wave.open(str(out / f"{name}.wav")) as w:
        return w.getnchannels(), w.readframes(w.getnframes())


def cut(raw, ch, a_ms, b_ms):
    fr = 2 * ch
    return raw[a_ms * FS // 1000 * fr:b_ms * FS // 1000 * fr]


def mp3(ff, raw, ch, dst, fade_ms=600):
    """raw 16-bit PCM -> a mono 22.05 kHz MP3, one gain for all of it: its RMS to -18 dB, its peak at most -3 dB"""
    a = array.array("h", raw)
    pk = max(1, max(abs(x) for x in a))
    rms = max(1.0, math.sqrt(sum(x * x for x in a[::7]) / max(1, len(a[::7]))))
    gain_db = min(20 * math.log10(32767 * 10 ** (-18 / 20) / rms), 20 * math.log10(32767 * 10 ** (-3 / 20) / pk))
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as t:
        with wave.open(t.name, "wb") as w:
            w.setnchannels(ch), w.setsampwidth(2), w.setframerate(FS), w.writeframes(raw)
        secs = len(raw) / (2 * ch * FS)
        af = f"volume={gain_db:.2f}dB"
        if fade_ms:
            af += f",afade=t=out:st={max(0.0, secs - fade_ms / 1000):.3f}:d={fade_ms / 1000:.3f}"
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", t.name, "-ac", "1", "-ar", "22050", "-af", af,
                        "-codec:a", "libmp3lame", "-b:a", "64k", str(dst)], check=True)
    os.unlink(t.name)


def beat_events(lanes, fill, bpm, shuffle, bars, t0):
    """the beat's MIDI notes (T1, channel 1): bars of 16 steps, the last of every four with its fill"""
    step = 60000 / bpm / 4
    ev = []
    for b in range(bars):
        bar = dict(lanes)
        if b % 4 == 3:
            bar.update(fill)
        for name, row in bar.items():
            n = LO + K[name]
            for s, c in enumerate(row):
                if c in VEL:
                    t = int(t0 + (b * 16 + s) * step + (step * shuffle / 100 if s % 2 else 0))
                    ev += [(t, f"midi 0x90 {n} {VEL[c]}"), (t + 30, f"midi 0x80 {n} 0")]
    return ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="0.1")
    ap.add_argument("--no-audio", action="store_true", help="the data only")
    a = ap.parse_args()
    names = key_names()
    assert len(names) == 27 and len(K) == 27, (len(names), len(K))
    out = ROOT / "build" / "site-audio"
    out.mkdir(parents=True, exist_ok=True)
    (SITE / "audio").mkdir(parents=True, exist_ok=True)
    data = {"version": a.version, "keys": names, "kits": [], "keyStarts": []}
    if not a.no_audio and not BIN.exists():
        sys.exit("gen_site: no build/host/riddim (run tests/run_host.sh first)")
    ff = None if a.no_audio else ffmpeg()
    for i, (name, style, bpm, shuf, lanes, fill) in enumerate(KITS):
        assert all(len(r) == 16 and set(r) <= set(".oxX") for r in list(lanes.values()) + list(fill.values())), name
        bar_ms = 4 * 60000 / bpm
        data["kits"].append({"name": name, "style": style, "bpm": bpm, "shuffle": shuf, "preset": 31 + i,
                             "lanes": [{"key": names[K[k]], "steps": r} for k, r in lanes.items()],
                             "fill": [{"key": names[K[k]], "steps": r} for k, r in fill.items()]})
        if a.no_audio:
            continue
        t0 = BOOT_MS + 1000
        ev = [(BOOT_MS, f"enc 6 {31 + i}")] + beat_events(lanes, fill, bpm, shuf, 4, t0)
        end = int(t0 + 4 * bar_ms + 1500)
        ch, raw = host(f"kit{i + 1:02d}", ev, end, out)
        mp3(ff, cut(raw, ch, t0, int(t0 + 4 * bar_ms + 1200)), ch, SITE / "audio" / f"kit-{i + 1:02d}.mp3")
        print(f"kit {i + 1} {name:<15} {style:<15} {bpm} BPM -> site/audio/kit-{i + 1:02d}.mp3")
    gap = 800                                   # (a key every 0.8 s: its tail; the spring's longer, cut by the next)
    t0 = BOOT_MS + 400
    data["keyStarts"] = [k * gap for k in range(27)]
    data["keyGap"] = gap
    if not a.no_audio:
        ev = [(BOOT_MS, "enc 6 31")]
        for k in range(27):
            ev += [(t0 + k * gap, f"midi 0x90 {LO + k} 120"), (t0 + k * gap + 40, f"midi 0x80 {LO + k} 0")]
        ch, raw = host("keys", ev, t0 + 27 * gap + 500, out)
        mp3(ff, cut(raw, ch, t0, t0 + 27 * gap), ch, SITE / "audio" / "keys.mp3", fade_ms=0)
        print("keys -> site/audio/keys.mp3")
        name, style, bpm, shuf, lanes, fill = KITS[0]
        t0 = BOOT_MS + 1000
        ev = [(BOOT_MS, "enc 6 31")] + beat_events(lanes, fill, bpm, shuf, 8, t0)
        bar_ms = 4 * 60000 / bpm
        ch, raw = host("demo", ev, int(t0 + 8 * bar_ms + 2000), out)
        mp3(ff, cut(raw, ch, t0, int(t0 + 8 * bar_ms + 1500)), ch, SITE / "audio" / "demo.mp3", fade_ms=1200)
        print("demo -> site/audio/demo.mp3")
    (SITE / "riddim-data.js").write_text("/* GENERATED by tools/gen_site.py from firmware/src/drum.c and its beats: do not edit */\n"
                                         "window.RIDDIM = " + json.dumps(data, ensure_ascii=False) + ";\n")
    print("data -> site/riddim-data.js")


if __name__ == "__main__":
    main()
