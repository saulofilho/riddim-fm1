/* SPDX-License-Identifier: GPL-3.0-only
 * Copyright (C) 2026 RIDDIM (after COQUÍ's perc.c, the same author; sine_i, noise32: Felucca's dsp.c, Leo Kuroshita,
 * Hügelton Instruments) */
/* RIDDIM's DRUM source: a roots reggae kit, synthesised (no samples, no flash, no pool).
 *   A DRUM track's notes are hits, not voices: each key a drum (drum_key: the default octave's 27 keys, F3 .. G5, hold
 *   the whole kit; notes outside fold in by two octaves), played by its own pool of NDH hits, never the six voices the
 *   other tracks share. A hit: a tone (a sine, a second partial, a pitch drop at the start) and a noise (a band- or
 *   high-pass, its own decay), each decaying on its own; a few drums have their own trick (the shaker's soft attack,
 *   the spring's rattle). A drum struck again, or another of its group (the hats: closed, pedal, open), cuts the one
 *   sounding (drum_hit).
 *   Knobs (SOUND): KIT (STUDIO, YARD, DUB, STEPPERS: the kick's, the snare's and the toms' tuning and decays), TUNE
 *   (-12 .. +12 semitones, all of it), DECAY (x 0.25 .. x 4, every decay), HUMAN (each hit a little later, softer,
 *   off-pitch, at random: 0 none .. 100 % a loose hand; a roots drummer sits behind the beat).
 *   Audio ISR only: drum_hit from note_on (riddim.c, in ctl_hook), drum_block from voices_render a control step. */

static inline int32_t sine_i(uint32_t ph)       /* sin, Q15, a full cycle over 2^32 (Felucca's dsp.c, SINE[1025]) */
{
    uint32_t i = ph >> 22;
    int32_t a = SINE[i], b = SINE[(i + 1u) & 1023u];
    return a + (((b - a) * (int32_t)((ph >> 7) & 0x7FFFu)) >> 15);
}
static inline uint32_t noise32(int32_t *st)     /* xorshift32 (Felucca's dsp.c) */
{
    uint32_t s = (uint32_t)*st;
    s ^= s << 13;
    s ^= s >> 17;
    s ^= s << 5;
    *st = (int32_t)s;
    return s;
}

enum { DI_KICK, DI_KICK2, DI_CROSS, DI_SNARE, DI_RIMSH, DI_HATC, DI_HATP, DI_HATO, DI_TOML, DI_TOMM, DI_TOMH, DI_SHAKE,
       DI_COWB, DI_WOOD, DI_SYNDR, DI_STICK, DI_SPRING, DI_TIMB, DI_RIDE, DI_CRASH, NDI };
enum { DS_NONE, DS_SOFT, DS_SPRING };           /* a drum's own trick */
enum { DC_OTHER, DC_KICK, DC_SNARE, DC_TOM };   /* what KIT changes */
typedef struct {
    uint16_t p16;                               /* the tone's pitch, 1/16 semitones (MIDI x 16; 0: no tone) */
    uint16_t r2;                                /* the second partial's ratio, Q8 (0: none) */
    uint16_t l2;                                /* .. its level, Q15 */
    uint16_t pdep;                              /* the pitch drop: the start's ratio - 1, Q8 (0: none) */
    uint16_t pdec;                              /* .. its time (ms, 60 dB) */
    uint16_t tdec;                              /* the tone's decay (ms, 60 dB) */
    uint16_t nlvl;                              /* the noise's level, Q15 */
    uint16_t ndec;                              /* .. its decay (ms) */
    uint16_t nf;                                /* .. its filter: the state-variable filter's f, Q15 (2 sin(pi fc / fs)) */
    uint8_t nt;                                 /* .. 0 high-pass, 1 band-pass */
    uint8_t sq;                                 /* the tone square (the cowbell), softened */
    uint8_t sp;                                 /* DS_ */
    uint8_t cls;                                /* DC_ */
    uint16_t gain;                              /* its level in the kit, Q8 (tests/drum_test.c: each drum's peak at full
                                                 * velocity, KIT STUDIO, to its place in the mix) */
} dinst_t;
/* the drums (pitches from Hz: (69 + 12 log2(f / 440)) x 16; filters: 2 sin(pi fc / 44100) x 32768) */
static const dinst_t DINST[NDI] = {
    { 543,   0,     0,  384,  25, 260,  6000,   4,  8381, 1, 0, 0, DC_KICK, 140},   /* KICK: 58 Hz, muffled, a soft click */
    { 512,   0,     0,  640,  30, 380,  9000,   5, 11610, 1, 0, 0, DC_KICK, 140},   /* KICK2: 52 Hz, the steppers' punch */
    {1150, 589, 14000,    0,   1,  45, 16000,  12,  8843, 1, 0, 0, DC_SNARE, 70},   /* CROSS: the cross-stick, 520 Hz wood */
    { 936, 415, 12000,   60,  12,  90, 26000, 140, 19317, 1, 0, 0, DC_SNARE, 70},   /* SNARE: 240 Hz, tuned high, tight */
    {1024, 742, 16000,    0,   1,  70, 30000, 110, 13900, 1, 0, 0, DC_SNARE, 70},   /* RIMSH: 330 Hz, the rim's crack */
    {   0,   0,     0,    0,   1,   1, 24575,  40, 31343, 0, 0, 0, DC_OTHER, 50},   /* HATC: over 7 kHz, short */
    {   0,   0,     0,    0,   1,   1, 22000,  25, 29273, 1, 0, 0, DC_OTHER, 72},   /* HATP: the pedal's chick, 6.5 kHz */
    {   0,   0,     0,    0,   1,   1, 21299, 420, 31343, 0, 0, 0, DC_OTHER, 55},   /* HATO: open, the flyers' cymbal */
    { 688, 384,  6000,   64,  40, 420,  5000,  20,  5596, 1, 0, 0, DC_TOM, 95},     /* TOML: 98 Hz */
    { 766, 384,  6000,   64,  35, 360,  5000,  18,  5596, 1, 0, 0, DC_TOM, 90},     /* TOMM: 130 Hz */
    { 849, 384,  6000,   64,  30, 300,  5000,  16,  8381, 1, 0, 0, DC_TOM, 85},     /* TOMH: 175 Hz */
    {   0,   0,     0,    0,   1,   1, 22000,  80, 25026, 0, 0, DS_SOFT, DC_OTHER, 55},   /* SHAKE: over 5.5 kHz, soft */
    {1172, 385, 29490,    0,   1, 190,  1638,   5, 13900, 1, 1, 0, DC_OTHER, 50},   /* COWB: 562 + 845 Hz squares */
    {1393, 691,  9830,    0,   1,  38,  4915,   5, 13900, 1, 0, 0, DC_OTHER, 61},   /* WOOD: a 1.25 kHz block */
    { 979,   0,     0,  640, 260, 420,  2000,   8, 13900, 1, 0, 0, DC_TOM, 80},     /* SYNDR: the syndrum, 280 Hz
                                                 * falling from ~1 kHz */
    {1550,   0,     0,    0,   1,  20,  8000,   6, 13900, 1, 0, 0, DC_OTHER, 60},   /* STICK: sticks, 2.2 kHz */
    { 744, 704, 12000,  768, 180, 600, 20000, 900,  8381, 1, 0, DS_SPRING, DC_OTHER, 70},   /* SPRING: the tank shaken: a
                                                 * falling twang and a rattle at 1.8 kHz */
    {1110, 591, 16384,   15,  10, 380, 11468,  30, 13900, 1, 0, 0, DC_TOM, 58},     /* TIMB: a timbale, 450 Hz */
    {1128, 947, 20000,    0,   1, 900,  9000, 700, 31343, 0, 0, 0, DC_OTHER, 45},   /* RIDE: 480 Hz bell, a wash */
    {   0,   0,     0,    0,   1,   1, 26000, 1300, 22853, 0, 0, 0, DC_OTHER, 50},  /* CRASH: over 5 kHz, long */
};
/* the keys, F3 .. G5 (MIDI 53 .. 79): the drum, its pitch (semitones from the drum's own), its choke group (a hit cuts
 * the one sounding in its group, on its track) */
#define DK_LO 53u
#define DK_N 27u
static const struct { uint8_t i; int8_t st; uint8_t g; } DKEY[DK_N] = {
    {DI_KICK, 0, 1},   {DI_HATC, 0, 2},    {DI_CROSS, 0, 3},  {DI_HATP, 0, 2},   {DI_SNARE, 0, 4},  {DI_HATO, 0, 2},
    {DI_RIMSH, 0, 4},  {DI_TOML, 0, 5},    {DI_SHAKE, 0, 6},  {DI_TOMM, 0, 7},   {DI_COWB, 0, 8},   {DI_TOMH, 0, 9},
    {DI_KICK2, 0, 1},  {DI_WOOD, 0, 10},   {DI_SYNDR, 0, 11}, {DI_SYNDR, 5, 12}, {DI_SYNDR, -5, 13}, {DI_STICK, 0, 14},
    {DI_SPRING, 0, 15}, {DI_TOML, -5, 16}, {DI_CROSS, 5, 3},  {DI_TIMB, 0, 17},  {DI_RIDE, 0, 18},  {DI_CRASH, 0, 19},
    {DI_KICK, -5, 1},  {DI_SNARE, 4, 4},   {DI_SPRING, 7, 15}};
static const char *const DKEY_NAME[DK_N] = {"KICK", "HAT", "CROSS", "PEDAL HAT", "SNARE", "OPEN HAT", "RIMSHOT",
                                            "TOM LO", "SHAKER", "TOM MID", "COWBELL", "TOM HI", "STEP KICK", "WOOD",
                                            "SYNDRUM", "SYN HI", "SYN LO", "STICKS", "SPRING", "FLOOR TOM", "CROSS HI",
                                            "TIMBALE", "RIDE", "CRASH", "DUB KICK", "SNARE HI", "SPRING HI"};
static uint32_t drum_key(uint32_t note)         /* a note's key: 0 .. DK_N - 1 */
{
    int32_t n = (int32_t)note;
    while (n < (int32_t)DK_LO) n += 24;
    while (n >= (int32_t)(DK_LO + DK_N)) n -= 24;
    return (uint32_t)n - DK_LO;
}

/* the kits: the kick's, the snare's (and cross-stick's) and the toms' tuning (1/16 semitones) and decay (Q8) */
#define NKIT 4u
static const char *const KIT_NAME[NKIT] = {"STUDIO", "YARD", "DUB", "STEPPERS"};
static const struct { int16_t kp, sp, tp; uint16_t kd, sd, td; } DKIT[NKIT] = {
    {0, 0, 0, 256, 256, 256},                   /* STUDIO: as the table, dry */
    {-16, -16, -16, 300, 320, 320},             /* YARD: a little lower and longer: the room */
    {0, 32, 16, 220, 170, 200},                 /* DUB: tight and high, room left for the spring and the echo */
    {-32, 16, 0, 420, 230, 256},                /* STEPPERS: a lower, longer kick on every beat */
};

#define NDH 10u                                 /* hits sounding at once (all DRUM tracks together) */
typedef struct {
    uint8_t on, inst, grp, trk, kill, sp;       /* sounding; the drum, its group, its track; out this step; its trick */
    uint16_t nf;                                /* its noise filter (DINST's, darker when struck softly) */
    uint16_t wait;                              /* frames still to wait (HUMAN) */
    uint16_t cnt;                               /* control steps since it began (the shaker) */
    uint32_t ph1, ph2, inc1;                    /* the tone's phases; its pitch's increment */
    uint32_t r2, pdep;                          /* the second partial's ratio (Q8), the drop (Q8) */
    int32_t l2;                                 /* the second partial's level (Q15) */
    int32_t ta, na, pe;                         /* the tone's, the noise's amplitude (Q24), the pitch drop left (Q16) */
    uint32_t kt, kn, kp;                        /* their decays (a control step's share) */
    int32_t npk;                                /* the noise's peak (Q24: the shaker's attack) */
    int32_t lp, bp, sl;                         /* the noise's filter, the square's smoothing */
    int32_t rs;                                 /* the noise's state */
    uint32_t rph, rinc;                         /* the spring's rattle */
    int32_t pulse;                              /* .. its knock now (Q15) */
    int32_t vel;                                /* its volume, Q14 */
} dhit_t;
static dhit_t dh_[NDH];
static uint32_t dh_seed = 0x9E3779B9u;          /* HUMAN's dice */
static volatile uint8_t drum_lit[NT];           /* the last key struck on each track + 1 (the SOUND page's picture) */

static uint32_t drum_rnd(void) { return noise32((int32_t *)&dh_seed); }
/* a decay of ms x dmul (Q16) as a control step's share (60 dB in that time: 6.9 / (t / 0.726 ms), Q16), in 32-bit
 * divisions only (the chip has no 64-bit one) */
static uint32_t dh_k(uint32_t ms, uint32_t dmul)
{
    uint32_t t = (ms * (dmul >> 6)) >> 4;       /* (ms x dmul, Q6: up to 1300 x 4 x 64) */
    uint32_t k = t ? 21025264u / t : 52429u;    /* (328516 x 65536 / 2^10 over the time / 2^10: Q16) */
    return k > 52429u ? 52429u : k ? k : 1u;
}

static int32_t dh_dec(int32_t a, uint32_t k)    /* a decay's step: at least 1 while it sounds (the longest ones, the
                                                 * crash's, would round to 0 just over the end and ring for ever) */
{
    int32_t d = mulq16(a, k);
    return d ? d : a > 0;
}

/* audio: track t's note struck, at vel (Q8, 0: full), late frames after the control step (GROOVE's drummer: the
 * cross-stick laid back). Never two hits alike, as a real drum: each a little off in pitch (+-6 cents), level (~+-0.8
 * dB) and length (+-6 %), at any HUMAN; and the force is in the sound, not only its level: a soft hit is darker (its
 * noise's filter lower), bends less (the tone's pitch drop) and is shorter */
static void drum_hit_at(uint32_t t, uint32_t note, uint32_t vel, uint32_t late)
{
    const volatile int32_t *p = trk[t].p[ENG_DRUM];
    uint32_t k = drum_key(note), i, best = 0, kit = (uint32_t)clamp(p[0], 0, NKIT - 1);
    uint32_t human = (uint32_t)clamp(p[3], 0, 127), dmul = pow2_q16(clamp(p[2], 0, 127) * 6) >> 2;
    const dinst_t *I = &DINST[DKEY[k].i];
    int32_t lv = 0x7FFFFFFF, p16;
    dhit_t *h;
    for (i = 0; i < NDH; i++)                   /* its group on its track: cut (it fades out this step) */
        if (dh_[i].on && dh_[i].trk == t && dh_[i].grp == DKEY[k].g) dh_[i].kill = 1;
    for (i = 0; i < NDH && dh_[i].on; i++)
        ;
    if (i == NDH)                               /* none free: the quietest goes at once */
        for (i = 0, best = 0; i < NDH; i++)
            if (dh_[i].ta + dh_[i].na < lv) lv = dh_[i].ta + dh_[i].na, best = i;
    h = &dh_[i < NDH ? i : best];
    h->inst = DKEY[k].i, h->grp = DKEY[k].g, h->trk = (uint8_t)t, h->kill = 0, h->sp = I->sp, h->cnt = 0;
    uint32_t f = vel ? (vel > 256u ? 256u : vel) : 256u, rr = drum_rnd();   /* (the force, Q8; the round's dice) */
    h->vel = (int32_t)(((f * 64u) * I->gain) >> 8);   /* (Q14) */
    h->vel = h->vel * (int32_t)(232u + (rr >> 8) % 48u) / 256;   /* (the level, a little off) */
    h->wait = (uint16_t)(late > 1000u ? 1000u : late);
    p16 = I->p16 + DKEY[k].st * 16 + (clamp(p[1], 0, 127) - 64) * 3 + (int32_t)(rr % 3u) - 1;   /* (a little off) */
    if (I->cls == DC_KICK) p16 += DKIT[kit].kp;
    if (I->cls == DC_SNARE) p16 += DKIT[kit].sp;
    if (I->cls == DC_TOM) p16 += DKIT[kit].tp;
    if (human) {                                /* HUMAN: later (up to ~8.6 ms), softer (up to -35 %), off-pitch (+-0.4) */
        uint32_t r = drum_rnd();
        h->wait = (uint16_t)(h->wait + (r & 0xFFFFu) % (human * 3u + 1u));
        h->vel -= (int32_t)(((uint32_t)h->vel * human * ((r >> 16) & 255u)) >> 16) * 45 / 64;
        p16 += (int32_t)(((r >> 24) & 15u) - 7u) * (int32_t)human / 127;
    }
    h->inc1 = I->p16 ? pitch_inc((uint32_t)clamp(p16, 0, 2047)) : 0u;
    h->r2 = I->r2, h->l2 = I->l2, h->pdep = I->pdep * (128u + f / 2u) / 256u;   /* (soft: half the bend) */
    h->nf = (uint16_t)((uint32_t)I->nf * (176u + f * 80u / 256u) / 256u);   /* (soft: darker, ~70 %) */
    h->ph1 = h->ph2 = 0;
    {
        uint32_t lm = (208u + f * 48u / 256u) * (240u + (rr >> 16) % 32u) / 256u, tm, nm;   /* (soft: shorter; a little
                                                 * off), Q8 */
        dmul = (dmul >> 8) * lm;
        tm = dmul, nm = dmul;
        if (I->cls == DC_KICK) tm = (tm >> 8) * DKIT[kit].kd;
        if (I->cls == DC_SNARE) tm = (tm >> 8) * DKIT[kit].sd, nm = (nm >> 8) * DKIT[kit].sd;
        if (I->cls == DC_TOM) tm = (tm >> 8) * DKIT[kit].td;
        h->kt = dh_k(I->tdec, tm);
        h->kn = dh_k(I->ndec, nm);
        h->kp = dh_k(I->pdec, 65536u);
    }
    h->ta = I->p16 ? 1 << 24 : 0;
    h->npk = (int32_t)I->nlvl << 9;             /* (Q15 -> Q24) */
    h->na = I->sp == DS_SOFT ? 0 : h->npk;
    h->pe = 65536;
    h->lp = h->bp = h->sl = 0;
    h->rs = (int32_t)(drum_rnd() | 1u);
    h->rph = 0, h->rinc = 1947831u, h->pulse = 32767;   /* (the spring: 20 knocks a second) */
    h->on = 1;
    drum_lit[t] = (uint8_t)(k + 1u);
}
static void drum_hit(uint32_t t, uint32_t note, uint32_t vel) { drum_hit_at(t, note, vel, 0u); }

/* audio: every hit's next control step (CTL frames from b) into tb[its track]; used: the tracks heard (their buffers
 * zeroed at their first sound, as voices_render does) */
static void drum_block(int32_t (*tb)[VB], uint32_t b, uint32_t n, uint32_t *used)
{
    uint32_t k, i;
    for (k = 0; k < NDH; k++) {
        dhit_t *h = &dh_[k];
        const dinst_t *I;
        int32_t ta0, ta1, na0, na1, dta, dna, *o;
        uint32_t i0 = 0, inc, inc2;
        if (!h->on) continue;
        if (h->wait >= CTL) { h->wait = (uint16_t)(h->wait - CTL); continue; }
        i0 = h->wait, h->wait = 0;
        I = &DINST[h->inst];
        ta0 = h->ta, na0 = h->na;
        if (h->kill) ta1 = na1 = 0;             /* (cut: out this step) */
        else {
            ta1 = ta0 - dh_dec(ta0, h->kt);
            if (h->sp == DS_SOFT && h->cnt < 6u)   /* a soft start: up in ~4 ms */
                na1 = h->npk / 6 * (int32_t)(h->cnt + 1u);
            else
                na1 = na0 - dh_dec(na0, h->kn);
        }
        h->cnt++;
        h->pe -= mulq16(h->pe, h->kp);
        inc = h->inc1 + (h->pdep ? (uint32_t)(((uint64_t)h->inc1 * h->pdep * (uint32_t)(h->pe >> 8)) >> 16) : 0u);
        inc2 = h->r2 ? (inc >> 8) * h->r2 : 0u;
        if (!(*used >> h->trk & 1u)) {
            *used |= 1u << h->trk;
            for (i = 0; i < n; i++) tb[h->trk][i] = 0;
        }
        o = tb[h->trk] + b;
        dta = (ta1 - ta0) >> CTL_LOG2, dna = (na1 - na0) >> CTL_LOG2;
        ta0 += dta * (int32_t)i0, na0 += dna * (int32_t)i0;
        for (i = i0; i < CTL; i++, ta0 += dta, na0 += dna) {
            int32_t s = 0, x;
            if (h->inc1) {                      /* the tone */
                if (I->sq) {
                    x = (h->ph1 & 0x80000000u ? -20000 : 20000) + (h->ph2 & 0x80000000u ? -h->l2 : h->l2) * 20000 / 32768;
                    h->sl += (x - h->sl) >> 2;  /* (softened: ~1.8 kHz) */
                    x = h->sl;
                } else {
                    x = SINE[h->ph1 >> 22];
                    if (h->r2) x += (SINE[h->ph2 >> 22] * h->l2) >> 15;
                }
                s = (x * (ta0 >> 10)) >> 14;
                h->ph1 += inc, h->ph2 += inc2;
            }
            if (na0 > 0) {                      /* the noise, filtered */
                int32_t w = (int32_t)noise32(&h->rs) >> 17, hp;
                h->lp += (h->nf * h->bp) >> 15;
                hp = w - h->lp - h->bp;
                h->bp += (h->nf * hp) >> 15;
                x = I->nt ? h->bp : hp;
                if (h->sp == DS_SPRING) {       /* the rattle: a knock 20 times a second, each ringing ~6 ms */
                    uint32_t r = h->rph;
                    h->rph += h->rinc;
                    if (h->rph < r) h->pulse = 32767;
                    h->pulse -= h->pulse >> 8;
                    x = (x * (h->pulse + 8192)) >> 15;
                }
                s += (x * (na0 >> 10)) >> 14;
            }
            s = clamp(s, -70000, 70000);        /* (x vel, at most ~30000: under 2^31) */
            o[i] += (s * h->vel) >> (14 - PB);
        }
        h->ta = ta1, h->na = na1;
        if (h->kill || (ta1 < 256 && na1 < 256 && !(h->sp == DS_SOFT && h->cnt < 6u))) h->on = 0;
    }
}
static int drum_busy(void)                      /* a hit sounds */
{
    uint32_t k;
    for (k = 0; k < NDH; k++)
        if (dh_[k].on) return 1;
    return 0;
}

/* the engine as the tracks see it: no voices (note_on hands its notes to drum_hit); its knobs' words */
static void drum_begin(voice_t *v) { (void)v; }
static void drum_vblock(voice_t *v, const volatile int32_t *p, int32_t *mono, int32_t amp0, int32_t amp1)
{
    (void)v, (void)p, (void)mono, (void)amp0, (void)amp1;
}
static void drum_text(const volatile int32_t *p, uint32_t k, char *s)
{
    int32_t v = p[k];
    switch (k) {
    case 0: put_s(s, KIT_NAME[clamp(v, 0, NKIT - 1)]); return;
    case 1: {                                   /* TUNE: semitones */
        int32_t st = (clamp(v, 0, 127) - 64) * 3;
        st = st < 0 ? -((-st + 8) / 16) : (st + 8) / 16;
        if (st < 0) put_u(put_s(s, "-"), (uint32_t)-st);
        else put_u(put_s(s, st ? "+" : ""), (uint32_t)st);
        return;
    }
    case 2: put_s(put_u(s, (pow2_q16(clamp(v, 0, 127) * 6) >> 2) * 100u >> 16), "%"); return;   /* DECAY: x 25 .. 400 % */
    default: put_s(put_u(s, (uint32_t)clamp(v, 0, 127) * 100u / 127u), "%"); return;   /* HUMAN */
    }
}
static const engine_t DRUM_ENGINE = {"DRUM", {"KIT", "TUNE", "DECAY", "HUMAN"}, {NKIT - 1, 127, 127, 127},
                                     drum_begin, drum_vblock, drum_text};
