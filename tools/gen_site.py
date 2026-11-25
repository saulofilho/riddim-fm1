#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 RIDDIM (after COQUÍ's tools/gen_hub.py, the same author)
"""RIDDIM's site (site/): its sounds and data, made from the firmware itself, in host mode.

  site/audio/kit-NN.mp3   each factory DRUM kit (PRESETS 31 .. 39) playing its own GROOVE style by itself (PLAY), four
                          bars at its tempo, the fourth with the fill: the firmware's drummer, nothing scripted
  site/audio/keys.mp3     the 27 keys of the ONE DROP KIT one after another (site/riddim-data.js: where each starts)
  site/audio/demo.mp3     eight bars of the ONE DROP KIT's GROOVE (the live view's DEMO)
  site/riddim-data.js     the kits, their styles' lanes (groove.c) as grids, the keys' names, the version

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

# the kits (PRESETS 31 .. 39) as they come: each plays its own GROOVE style (store.c) when PLAY is pressed; the tempo
# each is recorded at
KITS = [("ONE DROP KIT", 76), ("ROCKERS KIT", 80), ("STEPPERS KIT", 76), ("DUB KIT", 70), ("RUB-A-DUB KIT", 88),
        ("ROCKSTEADY KIT", 96), ("DEEP ROOTS KIT", 72), ("TIGHT KIT", 82), ("BOOMY KIT", 74)]


def styles():
    """GROOVE's styles as firmware/src/groove.c has them: name, feel, lanes, fills (keys by DK_ name); its braces counted"""
    g = (ROOT / "firmware" / "src" / "groove.c").read_text()
    body = g[g.index("static const gr_style_t GR_STYLE[] = {"):g.index("#define NSTYLE")]
    body = body[body.index("{", body.index("=")) + 1:]
    groups, depth, start = [], 0, 0
    for i, c in enumerate(body):                # (each style: a top-level brace group)
        if c == "{":
            if depth == 0: start = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0: groups.append(body[start + 1:i])
            if depth < 0: break
    out = []
    lane = lambda t: re.findall(r'\{DK_(\w+), "([.goxX]+)"\}', t)
    for st in groups:
        m = re.match(r'\s*"([^"]+)", (\d+),', st)
        parts, d, s0 = [], 0, 0
        for i, c in enumerate(st):              # (its three groups: the lanes, fill A, fill B)
            if c == "{":
                if d == 0: s0 = i
                d += 1
            elif c == "}":
                d -= 1
                if d == 0: parts.append(st[s0 + 1:i])
        out.append({"name": m.group(1), "feel": int(m.group(2)), "lanes": lane(parts[0]), "fa": lane(parts[1]),
                    "fb": lane(parts[2]) if len(parts) > 2 else []})
    return out


def kit_styles():
    """each factory kit's GROOVE style number (store.c: FSNDD(n, kit, tu, de, hu, style, fill))"""
    st = (ROOT / "firmware" / "src" / "store.c").read_text()
    return [int(m.group(1)) for m in re.finditer(r"FSNDD\(\d, \d, \d+, \d+, \d+, (\d+), \d\)", st)]




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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="0.1")
    ap.add_argument("--no-audio", action="store_true", help="the data only")
    a = ap.parse_args()
    names = key_names()
    assert len(names) == 27, len(names)
    out = ROOT / "build" / "site-audio"
    out.mkdir(parents=True, exist_ok=True)
    (SITE / "audio").mkdir(parents=True, exist_ok=True)
    data = {"version": a.version, "keys": names, "kits": [], "keyStarts": [], "steps": 32}
    if not a.no_audio and not BIN.exists():
        sys.exit("gen_site: no build/host/riddim (run tests/run_host.sh first)")
    ff = None if a.no_audio else ffmpeg()
    sty, ks = styles(), kit_styles()
    assert len(sty) == 8 and len(ks) == 9, (len(sty), len(ks))
    dk = {n.replace(" ", ""): i for i, n in enumerate(names)}   # (groove.c's DK_ names: drum.c's names, no spaces)
    alias = {"PEDAL": "PEDALHAT", "OHAT": "OPENHAT", "RIM": "RIMSHOT", "TOML": "TOMLO", "SHAKE": "SHAKER", "TOMM": "TOMMID",
             "COWB": "COWBELL", "TOMH": "TOMHI", "SKICK": "STEPKICK", "SYN": "SYNDRUM", "SYNHI": "SYNHI", "SYNLO": "SYNLO",
             "FLOOR": "FLOORTOM", "CROSSHI": "CROSSHI", "TIMB": "TIMBALE", "DKICK": "DUBKICK", "SNAREHI": "SNAREHI",
             "SPRINGHI": "SPRINGHI"}
    keyname = lambda k: names[dk[alias.get(k, k)]]
    for i, (name, bpm) in enumerate(KITS):
        S = sty[ks[i] - 1]
        bar_ms = 4 * 60000 / bpm
        data["kits"].append({"name": name, "style": S["name"], "bpm": bpm, "feel": S["feel"], "preset": 31 + i,
                             "lanes": [{"key": keyname(k), "steps": v} for k, v in S["lanes"]],
                             "fill": [{"key": keyname(k), "steps": v} for k, v in S["fa"]]})
        if a.no_audio:
            continue
        t0 = BOOT_MS + 1000                     # (the kit loaded, its tempo set, then PLAY: its GROOVE plays by itself)
        ev = [(BOOT_MS, f"enc 6 {31 + i}"), (BOOT_MS + 200, f"enc 0 {bpm - 120}"), (t0, "btn 12")]
        end = int(t0 + 4 * bar_ms + 1500)
        ch, raw = host(f"kit{i + 1:02d}", ev, end, out)
        mp3(ff, cut(raw, ch, t0, int(t0 + 4 * bar_ms + 1200)), ch, SITE / "audio" / f"kit-{i + 1:02d}.mp3")
        print(f"kit {i + 1} {name:<15} {S['name']:<11} {bpm} BPM -> site/audio/kit-{i + 1:02d}.mp3")
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
        bpm = KITS[0][1]
        bar_ms = 4 * 60000 / bpm
        t0 = BOOT_MS + 1000
        ev = [(BOOT_MS, "enc 6 31"), (BOOT_MS + 200, f"enc 0 {bpm - 120}"), (t0, "btn 12")]
        ch, raw = host("demo", ev, int(t0 + 8 * bar_ms + 2000), out)
        mp3(ff, cut(raw, ch, t0, int(t0 + 8 * bar_ms + 1500)), ch, SITE / "audio" / "demo.mp3", fade_ms=1200)
        print("demo -> site/audio/demo.mp3")
    (SITE / "riddim-data.js").write_text("/* GENERATED by tools/gen_site.py from firmware/src/drum.c and its beats: do not edit */\n"
                                         "window.RIDDIM = " + json.dumps(data, ensure_ascii=False) + ";\n")
    print("data -> site/riddim-data.js")


if __name__ == "__main__":
    main()
