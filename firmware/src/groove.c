/* SPDX-License-Identifier: GPL-3.0-only
 * Copyright (C) 2026 RIDDIM (after COQUÍ's groove.c, the same author) */
/* RIDDIM's GROOVE: a DRUM track's own drummer, a roots reggae style played on the sequencer's clock while PLAY runs,
 * beside the track's own steps.
 *   a style: lanes, each a drum (a key of drum.c's map) and its strokes over two bars (32 sixteenths), and two one-bar
 *   FILLs (A, B: one phrase each in turn) whose drums take the place of the same drums' lanes in a phrase's last bar
 *   strokes: '.' none, 'g' a ghost, 'o' soft, 'x' played, 'X' accented
 *   PARTS: which of the drums play: ALL, DRUMS (kicks, snares, cross-stick, rim, toms), HATS (hats, shaker, ride),
 *   EXTRAS (syndrum, spring, wood, cowbell, sticks, timbale, crash), or two of them: split a style over two DRUM tracks
 *   FILL: OFF, or a fill in the last bar of every 2, 4 or 8 bars (counted from PLAY)
 *   FEEL: the swing of the off sixteenths, -64 .. +63: 0 the style's own; less straighter, more looser
 *   The drummer, never a machine (tests/drum_test.c measures it): each stroke a little late by its drum (the cross-stick
 *   and the snare laid back ~5 ms, the kick on it, the hats loosest), its force off by up to +-12 %, a ghost played 7
 *   times in 10 and a soft stroke 9 in 10, now and then a ghost on the hats between their strokes; and drum.c makes no
 *   two hits alike. Rhythms as roots reggae plays them (the one drop, rockers, steppers, the flying cymbal, rocksteady,
 *   early reggae, rub-a-dub, dub), written for RIDDIM as two-bar loops: none transcribed from a record.
 * Audio ISR only (groove_tick from seq_tick); the main loop sets the track's grv_* (32-bit volatiles). */

enum { DK_KICK, DK_HAT, DK_CROSS, DK_PEDAL, DK_SNARE, DK_OHAT, DK_RIM, DK_TOML, DK_SHAKE, DK_TOMM, DK_COWB, DK_TOMH, DK_SKICK, DK_WOOD, DK_SYN, DK_SYNHI, DK_SYNLO, DK_STICKS, DK_SPRING, DK_FLOOR, DK_CROSSHI, DK_TIMB, DK_RIDE, DK_CRASH, DK_DKICK, DK_SNAREHI, DK_SPRINGHI };   /* (drum.c's keys, F3 .. G5) */
_Static_assert(DK_SPRINGHI + 1 == DK_N, "a key a drum");

#define GR_LANES 8u                             /* a style's lanes at most */
#define GR_FLANES 5u                            /* a fill's */
#define GR_STEPS 32u                            /* two bars of sixteenths */
#define GR_TP 24u                               /* ticks a step (96 a quarter note) */
typedef struct { uint8_t k; const char *s; } gr_lane_t;
typedef struct {
    const char *name;
    uint8_t feel;                               /* its own swing, 0..127 (FEEL 0) */
    gr_lane_t l[GR_LANES];                      /* (s 0: no lane) */
    gr_lane_t fa[GR_FLANES], fb[GR_FLANES];     /* the fills: one bar (16 steps) each */
} gr_style_t;

/*                                              |1 . . . 2 . . . 3 . . . 4 . . . |1 . . . 2 . . . 3 . . . 4 . . . | */
static const gr_style_t GR_STYLE[] = {   /* (each lane 32 steps, each fill 16: tests/drum_test.c checks) */
    {"ONE DROP", 28,
     {{DK_HAT, "x.o.x.o.x.o.x.o.x.o.x.o.x.o.x.og"},
      {DK_KICK, "........X...............X......."},
      {DK_CROSS, "........X...............X......."},
      {DK_SHAKE, "..g...g...g...g...g...g...g...g."}},
     {{DK_SNARE, "........g.o.x.x."}, {DK_TOMH, "............x..."}, {DK_TOMM, "..............x."}, {DK_TOML, "...............X"}},
     {{DK_CROSS, "........X.....x."}, {DK_SYN, "..............X."}}},
    {"ROCKERS", 18,
     {{DK_HAT, "xgxgxgxgxgxgxgxgxgxgxgxgxgxgxg.."},
      {DK_OHAT, "..............x...............x."},
      {DK_KICK, "X.......X.......X.......X......."},
      {DK_RIM, "........X...............X......."}},
     {{DK_SNARE, "........x.x.xxXX"}, {DK_HAT, "xgxgxgxg........"}},
     {{DK_TOMH, "........x.x....."}, {DK_TOMM, "............x.x."}, {DK_HAT, "xgxgxgxg........"}}},
    {"STEPPERS", 14,
     {{DK_SKICK, "X...X...X...X...X...X...X...X..."},
      {DK_HAT, "..x...x...x...x...x...x...x...x."},
      {DK_PEDAL, "o...o...o...o...o...o...o...o..."},
      {DK_RIM, "........X...............X......."},
      {DK_SHAKE, ".g.g.g.g.g.g.g.g.g.g.g.g.g.g.g.g"}},
     {{DK_SNARE, "....g.o.x.x.xxXX"}},
     {{DK_TOML, "........x...x.x."}, {DK_RIM, "........X...X..."}}},
    {"FLYERS", 24,
     {{DK_HAT, "x...x...x...x...x...x...x...x..."},
      {DK_OHAT, "..x...x...x...x...x...x...x...x."},
      {DK_KICK, "........X...............X......."},
      {DK_CROSS, "........X...............X......."}},
     {{DK_SNARE, "........o.x.xxXX"}, {DK_OHAT, "..x...x........."}},
     {{DK_TOMH, "..........x.x..."}, {DK_TOML, "..............xX"}, {DK_OHAT, "..x...x........."}}},
    {"ROCKSTEADY", 56,
     {{DK_KICK, "X.......X.......X.......X......."},
      {DK_CROSS, "....X.......X.......X.......X..."},
      {DK_HAT, "x.ox.ox.x.ox.ox.x.ox.ox.x.ox.ox."},
      {DK_RIDE, "o...o...o...o...o...o...o...o..."}},
     {{DK_SNARE, "............xxxX"}},
     {{DK_SNARE, "........x...x.xX"}}},
    {"EARLY", 34,
     {{DK_KICK, "X.......X.......X.......X......."},
      {DK_SNARE, "....X.......X.......X.......X..."},
      {DK_HAT, "x.x.x.x.x.x.x.x.x.x.x.x.x.x.x.x."},
      {DK_SHAKE, "o.ogo.ogo.ogo.ogo.ogo.ogo.ogo.og"}},
     {{DK_SNARE, "........x.x.xxxX"}},
     {{DK_TOMH, "........x.x....."}, {DK_TOML, "............x.xX"}}},
    {"RUB-A-DUB", 10,
     {{DK_KICK, "X.......X.......X.......X......."},
      {DK_SNAREHI, "....X.......X.......X.......X..."},
      {DK_HAT, "x.x.x.x.x.x.x.x.x.x.x.x.x.x.xxx."},
      {DK_SYN, "..............x...........x...x."}},
     {{DK_SYNHI, "........x.x....."}, {DK_SYN, "............x.x."}, {DK_SYNLO, "...............X"}},
     {{DK_SYN, "....x...x...x.x."}, {DK_SNAREHI, "....X.......X.X."}}},
    {"DUB", 30,
     {{DK_HAT, "x.......o...x...x...o.......x.o."},
      {DK_KICK, "........X...............X......."},
      {DK_CROSS, "........X...............X......."}},
     {{DK_SPRING, "........X......."}, {DK_SYNLO, "..............x."}},
     {{DK_CROSS, "........X.x....."}, {DK_SPRING, "............X..."}}},
};
#define NSTYLE (sizeof GR_STYLE / sizeof GR_STYLE[0])
static const char *const GR_SHORT[] = {"ONEDRP", "ROCKRS", "STEPRS", "FLYERS", "RKSTDY", "EARLY", "RUBDUB", "DUB"};   /* (the knob's slab: 6 letters) */
_Static_assert(sizeof GR_SHORT / sizeof GR_SHORT[0] == NSTYLE, "a short name a style");

enum { GP_ALL, GP_DRUMS, GP_HATS, GP_EXTRAS, GP_DH, GP_HE, GP_DE, GP_N };
static const char *const GP_NAME[GP_N] = {"ALL", "DRUMS", "HATS", "EXTRAS", "DRM+HAT", "HAT+EXT", "DRM+EXT"};
static const uint8_t GP_MASK[GP_N] = {7, 1, 2, 4, 3, 6, 5};   /* bit 0 DRUMS, 1 HATS, 2 EXTRAS */
static const uint8_t GR_FILLN[4] = {0, 2, 4, 8};   /* FILL: OFF, every 2, 4, 8 bars */
static uint32_t gr_sect(uint32_t k)             /* a key's part: 1 DRUMS, 2 HATS, 4 EXTRAS */
{
    switch (k) {
    case DK_HAT: case DK_PEDAL: case DK_OHAT: case DK_SHAKE: case DK_RIDE: return 2u;
    case DK_COWB: case DK_WOOD: case DK_SYN: case DK_SYNHI: case DK_SYNLO: case DK_STICKS: case DK_SPRING: case DK_TIMB:
    case DK_CRASH: case DK_SPRINGHI: return 4u;
    default: return 1u;
    }
}
static uint32_t gr_vel(char c)                  /* a stroke's force, Q8 for drum_hit (0: none): under a key's, so a busy
                                                 * style's drums together stay under full scale (tests/drum_test.c) */
{
    return c == 'X' ? 200u : c == 'x' ? 150u : c == 'o' ? 100u : c == 'g' ? 58u : 0u;
}
static uint32_t gr_late(uint32_t k)             /* a drum's place behind the beat (frames, 44.1 kHz): the cross-stick and the
                                                 * snare laid back, the kick on it, the rest between */
{
    switch (k) {
    case DK_CROSS: case DK_CROSSHI: case DK_SNARE: case DK_SNAREHI: case DK_RIM: return 220u;
    case DK_KICK: case DK_SKICK: case DK_DKICK: return 40u;
    case DK_HAT: case DK_PEDAL: case DK_OHAT: case DK_SHAKE: case DK_RIDE: return 90u;
    default: return 120u;
    }
}

static uint32_t grv_lit[NT];                    /* audio: the step a track's groove played last + 1 (the GROOVE page) */
static uint32_t grv_seed = 0x2F6E2B1u;           /* the drummer's dice */
static uint32_t grv_rnd(void) { grv_seed ^= grv_seed << 13, grv_seed ^= grv_seed >> 17, grv_seed ^= grv_seed << 5; return grv_seed; }
static void groove_hit(uint32_t t, uint32_t k, uint32_t v)   /* a stroke, as a drummer plays it */
{
    uint32_t r = grv_rnd(), jit = k == DK_HAT || k == DK_SHAKE ? 140u : 90u;
    if (trk_quiet >> t & 1u) return;            /* (muted, or another soloed) */
    if (v <= 58u && (r & 1023u) >= 717u) return;   /* (a ghost: 7 in 10) */
    if (v <= 100u && v > 58u && (r & 1023u) >= 942u) return;   /* (a soft stroke: 9 in 10) */
    v = v * (226u + (r >> 10) % 61u) / 256u;    /* (its force: -12 .. +12 %) */
    drum_hit_at(t, DK_LO + k, v ? v : 1u, gr_late(k) + (r >> 20) % jit);
    if (mo_seq) ec_put(0x90, t, (DK_LO + k) | EC_SEQ), ec_put(0x80, t, (DK_LO + k) | EC_SEQ);   /* (SEQ MIDI OUT) */
}
/* audio: a tick of the sequencer (tk: ticks since PLAY, 96 a quarter note) for track t */
static void groove_tick(uint32_t t, uint32_t tk)
{
    const gr_style_t *G;
    const gr_lane_t *F;
    uint32_t st = (uint32_t)clamp(trk[t].grv_style, 0, (int32_t)NSTYLE), sw, loc, s, i, j, mask, fn, fill;
    if (!st || trk[t].eng != ENG_DRUM) return;
    G = &GR_STYLE[st - 1u];
    {                                           /* FEEL: the style's swing, moved (0: as it is) */
        int32_t f = (int32_t)G->feel + clamp(trk[t].grv_feel, -64, 63) * 2;
        sw = (uint32_t)clamp(f, 0, 127) * (GR_TP / 2u) / 127u;   /* (up to half a step late) */
    }
    loc = tk % (2u * GR_TP);
    if (loc == 0u) s = tk / GR_TP;
    else if (loc == GR_TP + sw && sw) s = tk / GR_TP;
    else if (loc == GR_TP && !sw) s = tk / GR_TP;
    else return;
    s %= GR_STEPS;
    fn = GR_FILLN[clamp(trk[t].grv_fill, 0, 3)];
    fill = fn && (tk / SEQ_BAR) % fn == fn - 1u;   /* (the phrase's last bar) */
    F = fill && ((tk / SEQ_BAR) / fn & 1u) && G->fb[0].s ? G->fb : G->fa;   /* (A, B: a phrase each) */
    mask = GP_MASK[clamp(trk[t].grv_parts, 0, GP_N - 1)];
    grv_lit[t] = s + 1u;
    for (i = 0; i < GR_LANES && G->l[i].s; i++) {
        const gr_lane_t *L = &G->l[i];
        uint32_t v;
        if (!(gr_sect(L->k) & mask)) continue;
        if (fill) {                             /* (a drum the fill plays: the fill's, not the lane's) */
            for (j = 0; j < GR_FLANES && F[j].s && F[j].k != L->k; j++)
                ;
            if (j < GR_FLANES && F[j].s) continue;
        }
        if ((v = gr_vel(L->s[s])) != 0u) groove_hit(t, L->k, v);
        else if (L->k == DK_HAT && (s & 1u) && (grv_rnd() & 255u) < 16u) groove_hit(t, L->k, 58u);   /* (now and then a
                                                 * ghost between the hats' strokes) */
    }
    if (fill)
        for (j = 0; j < GR_FLANES && F[j].s; j++)
            if (gr_sect(F[j].k) & mask) {
                uint32_t v = gr_vel(F[j].s[s % 16u]);
                if (v) groove_hit(t, F[j].k, v);
            }
}
static void groove_text(uint32_t k, int32_t v, char *s)   /* the GROOVE page's knob k at v */
{
    switch (k) {
    case 0: put_s(s, v <= 0 ? "OFF" : GR_STYLE[clamp(v, 1, (int32_t)NSTYLE) - 1].name); return;
    case 1: put_s(s, GP_NAME[clamp(v, 0, GP_N - 1)]); return;
    case 2: if (v <= 0) put_s(s, "OFF"); else put_u(put_s(s, "/"), GR_FILLN[clamp(v, 0, 3)]); return;
    default: {
        int32_t d = clamp(v, -64, 63);
        if (d < 0) put_u(put_s(s, "-"), (uint32_t)-d);
        else put_u(put_s(s, d ? "+" : ""), (uint32_t)d);
        return;
    }
    }
}
