/* SPDX-License-Identifier: GPL-3.0-only
 * Copyright (C) 2026 RIDDIM (after COQUÍ's tests/perc/perc_test.c, the same author)
 * RIDDIM: firmware/src/drum.c on its own (tests/run_host.sh): every key struck alone, at full velocity, on each KIT; its
 * peak, its loudness and its length; a hit never past full scale, never silent, never endless; a struck hat cutting the
 * open one; and the cost of a full pool, in operations this computer times (the FM-1's: tools/fm1_cpu.py on the
 * device). Prints a table; exits 1 on a failure. With an argument: the WAV of every key one after another (KIT STUDIO)
 * to that file. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include "dsp.c"

#define CTL 32
#define CTL_LOG2 5
#define NT 4u
#define VB 256u
#define NPARAM 4u
#define PB 7
enum { ENG_VA, ENG_FM, ENG_SAMPLE, ENG_DRUM, ENG_WHEEL, ENG_PHYS, ENG_PHASE, NENG };
typedef struct { int dummy; } voice_t;
typedef struct {
    const char *name; const char *knob[NPARAM]; int32_t max[NPARAM];
    void (*begin)(voice_t *v);
    void (*block)(voice_t *v, const volatile int32_t *p, int32_t *mono, int32_t amp0, int32_t amp1);
    void (*text)(const volatile int32_t *p, uint32_t k, char *s);
} engine_t;
static struct {
    volatile int32_t p[NENG][NPARAM], eng;
} trk[NT];
static char *put_u(char *s, uint32_t v) { return s + sprintf(s, "%u", v); }
static char *put_s(char *s, const char *a) { while (*a) *s++ = *a++; *s = 0; return s; }
static uint32_t env_k(uint32_t t_ms_q16)        /* as voices.c */
{
    uint32_t k = (uint32_t)((((uint64_t)328516u) << 16) / t_ms_q16);
    return k > 52429u ? 52429u : k ? k : 1u;
}
static uint32_t pow2_q16(int32_t d16)           /* as samples.c */
{
    uint32_t u = (uint32_t)(d16 + 192 * 16), oct = u / 192u;
    uint32_t r = pitch_inc(1600 + u % 192u) / (pitch_inc(1600) >> 16);
    return oct >= 16u ? r << (oct - 16u) : r >> (16u - oct);
}
#include "drum.c"

static int32_t tb[NT][VB];
static int16_t wav[44100 * 60];
static uint32_t wn;
static int fails;
static void check(int ok, const char *what) { if (!ok) { printf("  FAIL  %s\n", what); fails++; } }
static void render(uint32_t *used) { uint32_t c; *used = 0; for (c = 0; c < VB; c += CTL) drum_block(tb, c, VB, used); }

/* one hit of key k on track 0, rendered till it ends (at most 3 s): its peak, RMS over its first 100 ms, length (ms) */
static void one(uint32_t k, int32_t *pk, int32_t *rms, uint32_t *len, int keep)
{
    uint32_t b, i, used, frames = 0;
    int64_t ss = 0;
    *pk = 0;
    drum_hit(0, DK_LO + k, 0);
    for (b = 0; b < 3u * 44100u / VB && drum_busy(); b++) {
        render(&used);
        for (i = 0; i < VB; i++, frames++) {
            int32_t s = used & 1u ? tb[0][i] >> PB : 0;   /* (Q15) */
            if (s > *pk) *pk = s;
            if (-s > *pk) *pk = -s;
            if (frames < 4410u) ss += (int64_t)s * s;
            if (keep && wn < sizeof wav / 2) wav[wn++] = (int16_t)clamp(s, -32767, 32767);
        }
    }
    { int64_t m = ss / 4410; int32_t r = 0; while ((int64_t)(r + 1) * (r + 1) <= m) r++; *rms = r; }
    *len = frames * 1000u / 44100u;
}
static void wav_write(const char *fn)
{
    FILE *f = fopen(fn, "wb");
    uint32_t d = wn * 2u, x;
    if (!f) return;
    fwrite("RIFF", 1, 4, f); x = 36 + d; fwrite(&x, 4, 1, f); fwrite("WAVEfmt ", 1, 8, f);
    x = 16; fwrite(&x, 4, 1, f); { uint16_t h[2] = {1, 1}; fwrite(h, 2, 2, f); }
    x = 44100; fwrite(&x, 4, 1, f); x = 88200; fwrite(&x, 4, 1, f); { uint16_t h[2] = {2, 16}; fwrite(h, 2, 2, f); }
    fwrite("data", 1, 4, f); fwrite(&d, 4, 1, f); fwrite(wav, 2, wn, f); fclose(f);
}
static double db(int32_t v) { return v ? 20.0 * __builtin_log10(v / 32767.0) : -99.0; }
int main(int argc, char **argv)
{
    uint32_t kit, k;
    int32_t kick_pk = 0, loudest = 0;
    trk[0].p[ENG_DRUM][1] = 64, trk[0].p[ENG_DRUM][2] = 64, trk[0].p[ENG_DRUM][3] = 0;
    for (kit = 0; kit < NKIT; kit++) {
        trk[0].p[ENG_DRUM][0] = (int32_t)kit;
        printf("KIT %s\n", KIT_NAME[kit]);
        for (k = 0; k < DK_N; k++) {
            int32_t pk, rms; uint32_t len;
            char w[64];
            one(k, &pk, &rms, &len, argc > 1 && kit == 0);
            if (argc > 1 && kit == 0) { uint32_t z; for (z = 0; z < 4410u; z++) wav[wn++] = 0; }
            printf("  %-10s peak %6.1f dB  rms(100 ms) %6.1f dB  %5u ms\n", DKEY_NAME[k], db(pk), db(rms), len);
            if (kit == 0 && k == 0u) kick_pk = pk;
            if (kit == 0 && pk > loudest) loudest = pk;
            snprintf(w, sizeof w, "%s %s: under full scale", KIT_NAME[kit], DKEY_NAME[k]); check(pk < 32767, w);
            snprintf(w, sizeof w, "%s %s: heard", KIT_NAME[kit], DKEY_NAME[k]); check(pk > 1000, w);
            snprintf(w, sizeof w, "%s %s: ends within 2.5 s", KIT_NAME[kit], DKEY_NAME[k]); check(len < 2500u, w);   /* (3 s:
                                                 * the render's limit, a hit that never ends) */
        }
    }
    check(kick_pk * 10 >= loudest * 7, "STUDIO: the kick among the loudest (within 3 dB of the loudest hit)");
    {   /* the hats are one group: the closed hat cuts the open one sounding */
        uint32_t b, used, on = 0;
        trk[0].p[ENG_DRUM][0] = 0;
        memset(dh_, 0, sizeof dh_);
        drum_hit(0, DK_LO + 5u, 0);             /* OPEN HAT */
        for (b = 0; b < 10u; b++) render(&used);
        drum_hit(0, DK_LO + 1u, 0);             /* HAT */
        render(&used);
        for (b = 0; b < NDH; b++) on += dh_[b].on && dh_[b].inst == DI_HATO;
        check(on == 0u, "the closed hat cuts the open one (one group)");
        memset(dh_, 0, sizeof dh_);
    }
    {   /* the cost: the pool full (NDH hits, all long ones), 2000 blocks */
        uint32_t b, used; clock_t t0;
        double us;
        trk[0].p[ENG_DRUM][0] = 0, trk[0].p[ENG_DRUM][2] = 127;
        t0 = clock();
        for (b = 0; b < 2000u; b++) {
            if (b % 40u == 0u) for (k = 0; k < NDH; k++) drum_hit(k & 3u, DK_LO + (k * 7u) % DK_N, 0);
            render(&used);
        }
        us = (double)(clock() - t0) * 1e6 / CLOCKS_PER_SEC / 2000.0;
        printf("cost   %u hits sounding: %.1f us a block of 256 frames on this computer (the budget: 5805 us on the FM-1)\n", NDH, us);
    }
    if (argc > 1) wav_write(argv[1]);
    printf(fails ? "drum test: FAILED (%d)\n" : "drum test: passed\n", fails);
    return fails != 0;
}
