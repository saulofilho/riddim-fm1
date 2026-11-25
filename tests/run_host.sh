#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-only
# GR!MM changes (file names): Copyright (C) 2026 GR!MM
# Run firmware/src/riddim.c on this computer (firmware/src/host.c): build/host/riddim.wav and the screens as PNG.
set -e
cd "$(dirname "$0")/.."
mkdir -p build/host
cc -O2 -Wall -Wno-unused-function -DDINGHY_HOST -DAPP_VER="\"${APP_VER:-0.1}\"" -Ifirmware/src -Ifirmware/gen -o build/host/riddim firmware/src/riddim.c
GRIMM_MASTER=1022 GRIMM_RAW_OUT=build/host/riddim.raw build/host/riddim build/host/riddim   # (V2: MASTER as web/test_web.mjs turns it: 1022, Q12 4080)
python3 - <<'PY'
from pathlib import Path
from PIL import Image
for p in sorted(Path("build/host").glob("riddim-*.ppm")):
    Image.open(p).resize((480, 480), Image.NEAREST).save(p.with_suffix(".png"))
    p.unlink()
    print("screen ->", p.with_suffix(".png"))
PY
# (RIDDIM: its saves have their own magics, store.c and platform.c: GR!MM's are not read.) The project GR!MM 1.0
# saved (tests/data/v1.0-saves.bin) leaves the unit as a fresh one: the same state as with no saves at all (up to
# "sounds", the user-sound sector's raw bytes, where GR!MM's records stay unread: RIDDIM takes only its own "R" ones)
mkdir -p build/compat
GRIMM_SAVE_IN=tests/data/v1.0-saves.bin GRIMM_STATE_OUT=build/compat/v1.0-state.txt build/host/riddim build/compat/run \
    tests/data/compat.txt > /dev/null
GRIMM_STATE_OUT=build/compat/fresh-state.txt build/host/riddim build/compat/fresh tests/data/compat.txt > /dev/null
sed -i.bak '/^sounds /,$d' build/compat/fresh-state.txt build/compat/v1.0-state.txt
if cmp -s build/compat/fresh-state.txt build/compat/v1.0-state.txt; then
    echo "saves  GR!MM 1.0's project is not read: a fresh unit"
else
    echo "saves  FAILED: GR!MM 1.0's project changed the state (diff build/compat/fresh-state.txt build/compat/v1.0-state.txt)"
    exit 1
fi
# GR!MM V2: MIDI. The TRS jack's parser (tests/midi_uart_test.c); the clock in and out, MIDI CHANNEL's CH n > SEL
# (tests/clock_test.py: host mode's "clock", "trs" and "probe")
cc -O2 -Wall -Wno-unused-function -Ifirmware/hal -o build/host/midi_uart_test tests/midi_uart_test.c
build/host/midi_uart_test
python3 tests/clock_test.py build/host/riddim
# GR!MM V2: the effects (tests/fx_test.py): the track filter's TYPE and POS, MASTER, DRIVE, their saves
python3 tests/fx_test.py build/host/riddim
# GR!MM V2: the quick wins (tests/quick_test.py)
python3 tests/quick_test.py build/host/riddim
# LATCH: every factory sound, SYSTEM 3 both ways, EDIT, SEL + OCT+, slots, the project, PHYS (tests/latch_test.py)
python3 tests/latch_test.py build/host/riddim
# GR!MM V2: GENERATE (FX held + the black keys): in the SCALE, the pattern unheard and unchanged (tests/gen_test.py)
python3 tests/gen_test.py build/host/riddim
# GR!MM V2: VELOCITY, PHASE's LINE 2 and envelopes, GLIDE (tests/play_test.py)
python3 tests/play_test.py build/host/riddim
# GR!MM V2: the gain staging: no clip at any MASTER, SPACE and DELAY under their knee (tests/level_test.py)
python3 tests/level_test.py build/host/riddim
# GR!MM V2: TAPE off is TAPE off: TAPE's knobs and every TAPE tile at 0, the output to the bit as the reference
# (tests/tapeoff_test.py, tests/data/tapeoff.sha256: a pad, a choir, a SAMPLE track, VOICE, GENERATE, the FX)
python3 tests/tapeoff_test.py build/host/riddim
# GR!MM V2 (rc9): PRESETS through every sound on T1 and T2 while it plays, FX off and on: every one sounds, no
# track's mix moved but by its knob, the sends still work (tests/presets_test.py; the rc8 no-sound report)
python3 tests/presets_test.py build/host/riddim
# GR!MM V2 rc9's fixes (build/bugs/AUDIT-rc8.md): NEW, HOME's CUT / DRY, the LFO on VOLUME, a sound past its
# ranges, the overload guard, the saves under a tail that never ends (tests/rc9_test.py)
python3 tests/rc9_test.py build/host/riddim
# GR!MM V2 rc9: the USB audio ring (firmware/src/uac_ring.h) in time: no dropout at any CPU load
cc -O2 -Wall -Ifirmware/src -o build/host/uac_ring_test tests/uac_ring_test.c
build/host/uac_ring_test
# GR!MM V2.0 rc11: chord mode is per track: a track's chord on / off, CHORD TYPE and VOICING apply to that track only,
# through every way a note plays (tests/chord_test.py)
python3 tests/chord_test.py build/host/riddim
# GR!MM V2.0 rc11: no flash step (autosave, the settings' save) while a computer reads the USB audio: it stopped the key scan,
# the LEDs and the stream ~50 ms (tests/rc11_test.py)
python3 tests/rc11_test.py build/host/riddim
# GR!MM V2.0.2: the sample slots after another firmware or a cut upload: any slot that does not play gets its factory
# sample once the boot checks are done, one that plays is never touched, the header says which (tests/samplefix_test.py)
python3 tests/samplefix_test.py build/host/riddim
# RIDDIM: DRUM on its own (tests/drum_test.c): every key on every KIT under full scale, heard, ending; the hats one
# group; its cost. build/host/drum_keys.wav: every key one after another (KIT STUDIO), to listen
cc -O2 -Wall -Wno-unused-function -Ifirmware/src -Ifirmware/gen -o build/host/drum_test tests/drum_test.c -lm
build/host/drum_test build/host/drum_keys.wav | tail -2
# RIDDIM: a DRUM track's GROOVE saved with the project and loaded again (tests/groove_save_test.py)
python3 tests/groove_save_test.py build/host/riddim
# RIDDIM: the band's lines (SKANK, BUBBLE, BASS, STEP BASS, HORNS) over a chord: their tones, steps, register, a musician's
# timing and lengths; a sound without a line switches it off (tests/band_test.py)
python3 tests/band_test.py build/host/riddim
