#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 RIDDIM
"""RIDDIM's first-steps guide, in English and Portuguese: eight A4 pages as HTML (site/guide/en.html, pt.html, also on
the site) and as PDF (docs/riddim-first-guide.pdf, docs/riddim-guia.pdf: tools/build_site.sh copies them to the site), printed by headless
Chrome (CHROME, or Google Chrome's usual place on a Mac). Every recipe in it was played in host mode first.
  python3 tools/gen_guide.py [--no-pdf]
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
URL = "saulofilho.github.io/riddim-fm1"

KEYS = ["KICK", "HAT", "CROSS", "PEDAL HAT", "SNARE", "OPEN HAT", "RIMSHOT", "TOM LO", "SHAKER", "TOM MID", "COWBELL",
        "TOM HI", "STEP KICK", "WOOD", "SYNDRUM", "SYN HI", "SYN LO", "STICKS", "SPRING", "FLOOR TOM", "CROSS HI",
        "TIMBALE", "RIDE", "CRASH", "DUB KICK", "SNARE HI", "SPRING HI"]
NOTES = ["F3", "F#3", "G3", "G#3", "A3", "A#3", "B3", "C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4",
         "A#4", "B4", "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5"]
BLACK = {1, 3, 5, 8, 10, 13, 15, 17, 20, 22, 25}

T = {
"en": dict(
    lang="en", file="riddim-first-guide", title="RIDDIM — First Guide", kicker="FM-1 · FIRST GUIDE",
    lead="Your first guide: switch it on, play the kit, build a one drop and dub it — step by step, no rush.",
    sub="Roots reggae firmware for the M-VAVE FM-1 · version 0.1 (in development: the drums are here, the band and the dub desk are next)",
    p2h="The device at a glance", p2k="WHERE EVERYTHING IS",
    p2t="The FM-1 has four knobs on the left, four on top, a grid of buttons and 27 keys. On RIDDIM they do this:",
    ctl=[("MASTER", "the volume"), ("SELECT", "the tempo on HOME; the cursor in the sequencer"), ("PRESETS", "the next sound (on SEQ: the tempo)"),
         ("ALGORITHM", "picks the track, T1 to T4"), ("KNOB 1–4", "the four values at the bottom of the screen"),
         ("OCT− / OCT+", "octave; back / confirm in menus"), ("the buttons", "one tap opens a page, another tap the next; hold one for its combo"),
         ("the 27 keys", "play the track; on a DRUM track each key is a drum")],
    p3h="First steps", p3k="POWER ON AND PLAY IN A MINUTE",
    steps3=["Connect the FM-1 to headphones or a speaker and switch it on. A record turns on the screen, the tonearm sets down and the name echoes: that's RIDDIM.",
            "Turn <b>MASTER</b> to a comfortable level and press a key: you hear the selected track.",
            "Turn <b>ALGORITHM</b> to move between the four tracks, T1 to T4. HOME shows them as four speaker boxes; the cones push when a track plays.",
            "Turn <b>PRESETS</b> to change the track's sound. The nine drum kits are in the <b>DRUMS</b> category (PRESETS 31 to 39).",
            "Turn <b>SELECT</b> on HOME to set the tempo. Roots reggae sits around <b>72–80 BPM</b>.",
            "Don't worry about saving: when you stop and leave it alone for a moment, RIDDIM keeps everything."],
    p4h="Play the kit", p4k="A ROOTS DRUM KIT ON THE KEYS",
    p4t="Turn PRESETS to <b>ONE DROP KIT</b>. Now each key is a drum, the same at any octave. The DRUM page (EDIT) draws the kit and lights the piece you hit.",
    p4try="<b>Try the one drop:</b> tap HAT (F#3) on every eighth, and on beat 3 tap KICK (F3) and CROSS (G3) together. Nothing on beat 1: that's the drop.",
    p4knobs="<b>Or let it play:</b> press <b>PLAY</b> and the kit plays its own style by itself, a drummer behind the beat (EDIT › GROOVE: STYLE, PARTS, FILL, FEEL). <b>EDIT › SOUND:</b> KIT · TUNE · DECAY · HUMAN.",
    p5h="Build a one drop", p5k="THE SEQUENCER, THREE TRACKS",
    p5t="A step holds one note per track, so the beat goes on three tracks, each with the ONE DROP KIT. About three minutes.",
    steps5=["On HOME, SELECT to <b>76 BPM</b>. Put the ONE DROP KIT on T1, T2 and T3 (ALGORITHM, then PRESETS).",
            "<b>T1, the hats.</b> Press <b>SEQ</b> (the grid), then <b>REC</b>. Press HAT: it writes step 1 and moves to step 2. Turn SELECT one step on, press HAT again; and so on: steps 1, 3, 5 … 15.",
            "<b>T2, the kick.</b> ALGORITHM to T2. On the grid with REC on, turn SELECT to <b>step 9</b> and press KICK.",
            "<b>T3, the cross-stick.</b> ALGORITHM to T3, SELECT to <b>step 9</b>, press CROSS. Press REC again to stop recording.",
            "Press <b>PLAY</b>. That's the one drop. For lilt: SEQ again (PATTERN SETTINGS), turn SWING up a little on each track.",
            "Made a mistake? Hold <b>EDIT</b> and press <b>OCT−</b> to undo."],
    p6h="Dub it", p6k="THE ENGINEER'S MOVES",
    steps6=["<b>Echo on the cross-stick.</b> On T3, press HOME twice (MIXER 1), turn SELECT to the DELAY tile and KNOB 1 up.",
            "<b>Shape the echo.</b> Press FX until DELAY: TIME on a dotted eighth, FEEDBACK past the middle, WEAR for a darker tape.",
            "<b>Throw.</b> Hold <b>FX</b> and hold <b>A3</b> (ECHO THROW): everything goes into the echo while you hold; let go and the tail rings on.",
            "<b>Drop the band out.</b> Hold <b>GLO</b> and tap <b>F3–B3</b> to mute T1–T4 (C4–F4 to solo). On HOME the muted box wears DROP.",
            "<b>Sweep.</b> FX until MASTER: TYPE HP or LP, turn CUTOFF slowly. Hold FX + D4 / E4 for a quick filter down / up.",
            "Spring reverb, throws on one track and VERSION, the dub that mixes itself, come in the next versions."],
    p7h="The buttons", p7k="ONE TAP, AND HOLD",
    btn=[("HOME", "HOME, MIXER 1, MIXER 2", "SYSTEM settings"), ("EDIT", "SOUND, SOURCE (FM, PHASE: more)", "with OCT−/OCT+: undo / redo"),
         ("SEQ", "GRID, PATTERN SETTINGS", "+ white key: tools; + SELECT: length"), ("PLAY", "start / stop", ""),
         ("REC", "record into the pattern", "~1 s: clear the track's pattern"), ("FX", "TAPE, GRAIN, DELAY, SPACE, MASTER, DRIVE", "PERFORM: throws, stutter, filter; GENERATE"),
         ("SEL", "SCALE, CHORD", "alone: chord mode; + OCT+: LATCH"), ("ENV / LFO", "the track's envelope / LFO", ""),
         ("ARP", "the arpeggiator", "alone: on / off"), ("SAVE", "SOUNDS, PROJECTS", "+ C4–F4: save A–D; + F3–B3: recall"),
         ("GLO", "SONG", "+ F3–B3: mute T1–T4; + C4–F4: solo")],
    p8h="The kit, and the cheat sheet", p8k="27 KEYS, NINE KITS",
    kits="ONE DROP · ROCKERS · STEPPERS · DUB · RUB-A-DUB · ROCKSTEADY · DEEP ROOTS · TIGHT · BOOMY",
    save="<b>It saves itself</b> when you stop and leave it ~2.5 s. Slots A–D: hold SAVE + C4–F4 to save, + F3–B3 to recall.",
    more=f"More: the manual, the editor, the web emulator and the live view at <b>{URL}</b>. Not yet tested on an FM-1: see the README before installing.",
    th_key="Key", th_drum="Drum", th_btn="Button", th_tap="One tap", th_hold="Hold",
),
"pt": dict(
    lang="pt-BR", file="riddim-guia", title="RIDDIM — Guia de primeiros passos", kicker="FM-1 · GUIA DE PRIMEIROS PASSOS",
    lead="Seu primeiro guia: ligar, tocar o kit, montar um one drop e fazer o dub — passo a passo, sem pressa.",
    sub="Firmware de reggae roots para o M-VAVE FM-1 · versão 0.1 (em desenvolvimento: a bateria está aqui, a banda e a mesa de dub vêm depois)",
    p2h="O aparelho num relance", p2k="ONDE FICA CADA COISA",
    p2t="O FM-1 tem quatro knobs à esquerda, quatro em cima, uma grade de botões e 27 teclas. No RIDDIM eles fazem isto:",
    ctl=[("MASTER", "o volume"), ("SELECT", "o tempo na HOME; o cursor no sequenciador"), ("PRESETS", "o próximo som (no SEQ: o tempo)"),
         ("ALGORITHM", "escolhe a trilha, T1 a T4"), ("KNOB 1–4", "os quatro valores embaixo da tela"),
         ("OCT− / OCT+", "oitava; voltar / confirmar nos menus"), ("os botões", "um toque abre uma página, outro a seguinte; segure para o combo"),
         ("as 27 teclas", "tocam a trilha; numa trilha DRUM cada tecla é um tambor")],
    p3h="Primeiros passos", p3k="LIGAR E TOCAR EM UM MINUTO",
    steps3=["Ligue o FM-1 a um fone ou caixa e ligue o aparelho. Um disco gira na tela, o braço desce e o nome ecoa: é o RIDDIM.",
            "Gire o <b>MASTER</b> até um volume confortável e aperte uma tecla: você ouve a trilha selecionada.",
            "Gire o <b>ALGORITHM</b> para passar pelas quatro trilhas, T1 a T4. A HOME mostra as quatro como caixas de som; os cones empurram quando a trilha toca.",
            "Gire o <b>PRESETS</b> para trocar o som da trilha. Os nove kits de bateria estão na categoria <b>DRUMS</b> (PRESETS 31 a 39).",
            "Gire o <b>SELECT</b> na HOME para o tempo. O reggae roots fica por volta de <b>72–80 BPM</b>.",
            "Não se preocupe em salvar: quando você para e deixa o aparelho um instante, o RIDDIM guarda tudo."],
    p4h="Toque o kit", p4k="UMA BATERIA ROOTS NAS TECLAS",
    p4t="Gire o PRESETS até o <b>ONE DROP KIT</b>. Agora cada tecla é um tambor, igual em qualquer oitava. A página DRUM (EDIT) desenha o kit e acende a peça tocada.",
    p4try="<b>Tente o one drop:</b> toque o HAT (F#3) em cada colcheia e, no tempo 3, o KICK (F3) e o CROSS (G3) juntos. Nada no tempo 1: esse é o drop.",
    p4knobs="<b>Ou deixe tocar:</b> aperte <b>PLAY</b> e o kit toca o seu estilo sozinho, um baterista atrás do tempo (EDIT › GROOVE: STYLE, PARTS, FILL, FEEL). <b>EDIT › SOUND:</b> KIT · TUNE · DECAY · HUMAN.",
    p5h="Monte um one drop", p5k="O SEQUENCIADOR, TRÊS TRILHAS",
    p5t="Um passo guarda uma nota por trilha, então a batida vai em três trilhas, cada uma com o ONE DROP KIT. Uns três minutos.",
    steps5=["Na HOME, SELECT em <b>76 BPM</b>. Ponha o ONE DROP KIT em T1, T2 e T3 (ALGORITHM, depois PRESETS).",
            "<b>T1, os chimbais.</b> Aperte <b>SEQ</b> (a grade) e depois <b>REC</b>. Aperte HAT: ele grava o passo 1 e vai para o 2. Gire o SELECT um passo, aperte HAT de novo; e assim por diante: passos 1, 3, 5 … 15.",
            "<b>T2, o bumbo.</b> ALGORITHM em T2. Na grade com REC ligado, gire o SELECT até o <b>passo 9</b> e aperte KICK.",
            "<b>T3, o cross-stick.</b> ALGORITHM em T3, SELECT no <b>passo 9</b>, aperte CROSS. Aperte REC de novo para parar de gravar.",
            "Aperte <b>PLAY</b>. Esse é o one drop. Para o balanço: SEQ de novo (PATTERN SETTINGS), suba um pouco o SWING em cada trilha.",
            "Errou? Segure <b>EDIT</b> e aperte <b>OCT−</b> para desfazer."],
    p6h="Faça o dub", p6k="OS MOVIMENTOS DO ENGENHEIRO",
    steps6=["<b>Eco no cross-stick.</b> Na T3, aperte HOME duas vezes (MIXER 1), gire o SELECT até o quadro DELAY e suba o KNOB 1.",
            "<b>Molde o eco.</b> Aperte FX até DELAY: TIME numa colcheia pontuada, FEEDBACK passando do meio, WEAR para uma fita mais escura.",
            "<b>Jogue.</b> Segure <b>FX</b> e segure <b>A3</b> (ECHO THROW): tudo vai para o eco enquanto você segura; solte e a cauda continua.",
            "<b>Tire a banda.</b> Segure <b>GLO</b> e toque <b>F3–B3</b> para mutar T1–T4 (C4–F4 para solo). Na HOME a caixa muda leva DROP.",
            "<b>Varra.</b> FX até MASTER: TYPE HP ou LP, gire o CUTOFF devagar. Segure FX + D4 / E4 para o filtro descer / subir rápido.",
            "A reverb de mola, o throw por trilha e o VERSION, o dub que se mixa sozinho, vêm nas próximas versões."],
    p7h="Os botões", p7k="UM TOQUE, E SEGURAR",
    btn=[("HOME", "HOME, MIXER 1, MIXER 2", "ajustes do SYSTEM"), ("EDIT", "SOUND, SOURCE (FM, PHASE: mais)", "com OCT−/OCT+: desfazer / refazer"),
         ("SEQ", "GRID, PATTERN SETTINGS", "+ tecla branca: ferramentas; + SELECT: tamanho"), ("PLAY", "toca / para", ""),
         ("REC", "grava no padrão", "~1 s: apaga o padrão da trilha"), ("FX", "TAPE, GRAIN, DELAY, SPACE, MASTER, DRIVE", "PERFORM: throws, stutter, filtro; GENERATE"),
         ("SEL", "SCALE, CHORD", "sozinho: modo acorde; + OCT+: LATCH"), ("ENV / LFO", "o envelope / LFO da trilha", ""),
         ("ARP", "o arpejador", "sozinho: liga / desliga"), ("SAVE", "SOUNDS, PROJECTS", "+ C4–F4: salva A–D; + F3–B3: chama"),
         ("GLO", "SONG", "+ F3–B3: muta T1–T4; + C4–F4: solo")],
    p8h="O kit, e a cola", p8k="27 TECLAS, NOVE KITS",
    kits="ONE DROP · ROCKERS · STEPPERS · DUB · RUB-A-DUB · ROCKSTEADY · DEEP ROOTS · TIGHT · BOOMY",
    save="<b>Ele salva sozinho</b> quando você para e deixa ~2,5 s. Slots A–D: segure SAVE + C4–F4 para salvar, + F3–B3 para chamar.",
    more=f"Mais: o manual, o editor, o emulador web e a visão ao vivo em <b>{URL}</b>. Ainda não testado num FM-1: leia o README antes de instalar.",
    th_key="Tecla", th_drum="Tambor", th_btn="Botão", th_tap="Um toque", th_hold="Segurar",
),
}

CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
:root { --tinta:#0E0C0A; --papel:#EFE2BC; --papel2:#E2D3A8; --cinza:#6D6150; --vermelho:#C21F1A; --ouro:#E9B12C; --verde:#1F7A3C; --folha:#5C8F2C; --eco:#4B4FB0; --creme:#F6EBC8; }
html, body { margin: 0; background: #888; }
body { font: 11.5pt/1.5 Archivo, system-ui, sans-serif; color: var(--tinta); }
.page { width: 210mm; height: 297mm; margin: 0 auto 8mm; background: var(--papel); padding: 18mm 18mm 16mm; position: relative; overflow: hidden; page-break-after: always; }
@media print { html, body { background: none; } .page { margin: 0; } }
.kick { font: 500 9pt "IBM Plex Mono", monospace; letter-spacing: .14em; color: var(--cinza); text-transform: uppercase; }
h1 { display: inline-block; font: 400 88pt/0.95 "Lilita One", sans-serif; margin: 6mm 0 0; padding: 2mm 6mm 1mm; background: var(--tinta); color: var(--ouro); -webkit-text-stroke: 1.6pt var(--vermelho); text-shadow: 3pt 4pt 0 var(--vermelho); transform: rotate(-1.2deg); }
h2 { display: inline-block; font: 400 25pt/1.05 "Lilita One", sans-serif; margin: 2mm 0 5mm; padding: 1.5mm 4mm 1mm; background: var(--verde); color: var(--tinta); text-shadow: -1pt -1pt 0 var(--ouro), 1pt -1pt 0 var(--ouro), -1pt 1pt 0 var(--ouro), 1pt 1pt 0 var(--ouro), 2.5pt 2.5pt 0 var(--vermelho); }
.lead { font-size: 15pt; max-width: 150mm; margin: 14mm 0 0; }
.sub { color: var(--cinza); margin-top: 4mm; max-width: 150mm; }
.foot { position: absolute; left: 18mm; right: 18mm; bottom: 9mm; display: flex; justify-content: space-between; font: 500 8pt "IBM Plex Mono", monospace; letter-spacing: .1em; color: var(--cinza); text-transform: uppercase; border-top: 2px solid var(--tinta); padding-top: 2mm; }
.plate { position: absolute; right: 16mm; bottom: 62mm; width: 80mm; }
.page.cover { background: var(--folha); }
.page.cover .lead, .page.cover .sub { background: var(--creme); padding: 3mm 4mm; color: var(--tinta); }
.page.cover .kick { color: var(--creme); }
.page.cover .foot { color: var(--creme); border-color: var(--creme); }
.boxes { position: absolute; left: 0; right: 0; bottom: 20mm; height: 34mm; display: flex; gap: 2mm; padding: 0 4mm; }
.boxes i { flex: 1; border: 1.2mm solid var(--tinta); display: flex; align-items: center; justify-content: center; }
.boxes i::after { content: ""; width: 60%; aspect-ratio: 1; border-radius: 50%; background: var(--eco); border: 1.4mm solid var(--tinta); box-shadow: inset 0 0 0 3mm var(--eco), inset 0 0 0 4mm var(--tinta); }
ol.steps { counter-reset: s; list-style: none; padding: 0; margin: 0; }
ol.steps li { counter-increment: s; position: relative; padding: 2.4mm 0 2.4mm 13mm; border-bottom: 1px solid var(--papel2); }
ol.steps li::before { content: counter(s); position: absolute; left: 0; top: 2mm; width: 9mm; height: 9mm; background: var(--vermelho); color: var(--ouro); font: 400 14pt "Lilita One"; display: flex; align-items: center; justify-content: center; }
.row { display: flex; gap: 7mm; align-items: flex-start; }
.shot { width: 62mm; flex: none; border: 3mm solid var(--tinta); image-rendering: pixelated; }
.shot.big { width: 78mm; }
.cap { font: 500 8pt "IBM Plex Mono"; color: var(--cinza); text-transform: uppercase; letter-spacing: .08em; margin-top: 1.5mm; }
table { border-collapse: collapse; width: 100%; font-size: 10.5pt; }
th { text-align: left; font: 400 12pt "Lilita One"; border-bottom: 2px solid var(--tinta); padding: 1.6mm 2mm; }
td { border-bottom: 1px solid var(--papel2); padding: 1.6mm 2mm; vertical-align: top; }
td b, li b { font-weight: 800; }
.box { background: var(--tinta); color: var(--creme); padding: 4mm 5mm; margin-top: 5mm; font: 400 13pt "Lilita One"; }
.box b { color: var(--ouro); }
.note { background: var(--papel2); padding: 3mm 4mm; margin-top: 4mm; }
.fm1 { background: #1e1a16; border-radius: 4mm; padding: 5mm; display: grid; grid-template-columns: 30mm 1fr 52mm; gap: 4mm; color: var(--papel); font: 500 7pt "IBM Plex Mono"; letter-spacing: .05em; margin: 2mm 0 6mm; }
.fm1 .k { display: flex; align-items: center; gap: 2mm; margin: 1.5mm 0; }
.fm1 .k i { width: 7mm; height: 7mm; border-radius: 50%; background: #3a322a; border: 1mm solid #6E6352; flex: none; }
.fm1 .scr { background: #000; border: 1.5mm solid #050403; display: flex; align-items: center; justify-content: center; aspect-ratio: 1; }
.fm1 .scr img { width: 100%; image-rendering: pixelated; }
.fm1 .bt { display: grid; grid-template-columns: repeat(6, 1fr); gap: 1.2mm; align-content: start; }
.fm1 .bt span { background: #3a322a; padding: 1.4mm 0; text-align: center; font-size: 5.6pt; }
.fm1 .top { grid-column: 2 / 4; display: flex; gap: 3mm; }
.fm1 .top .k i { width: 6mm; height: 6mm; }
.keys27 { grid-column: 1 / -1; display: flex; gap: .8mm; height: 13mm; }
.keys27 span { flex: 1; background: var(--papel); }
.keys27 span.b { background: #3a322a; height: 8mm; }
.kb { display: flex; gap: .6mm; margin: 3mm 0 5mm; }
.kb div { flex: 1; height: 30mm; background: #fffaf0; border: .4mm solid var(--tinta); position: relative; font: 500 5.6pt "IBM Plex Mono"; }
.kb div.b { background: var(--tinta); color: var(--papel); height: 20mm; }
.kb div span { position: absolute; bottom: 1mm; left: 0; right: 0; text-align: center; writing-mode: vertical-rl; transform: rotate(180deg); margin: 0 auto; height: 70%; }
.kb div.hl { background: var(--ouro); }
.kb div.b.hl { background: var(--vermelho); }
.grid16 { display: grid; grid-template-columns: 22mm repeat(16, 1fr); gap: .8mm; font: 500 7pt "IBM Plex Mono"; margin: 4mm 0; align-items: center; }
.grid16 i { height: 6mm; background: var(--papel2); }
.grid16 i.on { background: var(--tinta); }
.grid16 i.x { background: var(--vermelho); }
.grid16 i:nth-of-type(4n+1) { outline: .3mm solid var(--cinza); }
"""

PLATE = """<svg class="plate" viewBox="0 0 300 300"><defs><path id="arc" d="M150,150 m-74,0 a74,74 0 1,1 148,0 a74,74 0 1,1 -148,0"/></defs>
<circle cx="150" cy="150" r="148" fill="#0b0907"/><g fill="none" stroke="#2a221a" stroke-width="1.2"><circle cx="150" cy="150" r="138"/><circle cx="150" cy="150" r="126"/><circle cx="150" cy="150" r="114"/><circle cx="150" cy="150" r="102"/></g>
<circle cx="150" cy="150" r="88" fill="#E8A825"/><circle cx="150" cy="150" r="88" fill="none" stroke="#C7382B" stroke-width="6"/>
<text font-family="Alfa Slab One" font-size="13" fill="#17130E" letter-spacing="3"><textPath href="#arc">PRE-RELEASE · SOUND SYSTEM SPECIAL · 0.1 ·</textPath></text>
<text x="150" y="146" text-anchor="middle" font-family="Anton" font-size="34" fill="#17130E">RIDDIM</text>
<text x="150" y="170" text-anchor="middle" font-family="IBM Plex Mono" font-size="10" fill="#17130E" letter-spacing="2">FIRST STEPS</text><circle cx="150" cy="150" r="5" fill="#0b0907"/></svg>"""


def foot(L, n):
    return f'<div class="foot"><span>RIDDIM · {L["title"].split("— ")[1]}</span><span>{URL} · {n}/8</span></div>'


def page(inner, L, n, cls=""):
    return f'<section class="page {cls}">{inner}{foot(L, n)}</section>'


def keyboard(hl=()):
    out = '<div class="kb">'
    for i, k in enumerate(KEYS):
        out += f'<div class="{"b " if i in BLACK else ""}{"hl" if k in hl else ""}"><span>{NOTES[i]} {k}</span></div>'
    return out + "</div>"


def grid16(rows):
    out = '<div class="grid16">'
    for name, steps, cls in rows:
        out += f"<span>{name}</span>" + "".join(f'<i class="{cls if c != "." else ""}"></i>' for c in steps)
    return out + "</div>"


def build(L):
    p = []
    boxes = "".join(f'<i style="background:{c}"></i>' for c in ("#C21F1A", "#E9B12C", "#1F7A3C", "#C21F1A", "#E9B12C", "#1F7A3C"))
    p.append(page(f'<div class="kick">{L["kicker"]}</div><h1>RIDDIM</h1><p class="lead">{L["lead"]}</p><p class="sub">{L["sub"]}</p>'
                  f'{PLATE}<div class="boxes">{boxes}</div>', L, 1, "cover"))
    ctl = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td></tr>" for a, b in L["ctl"])
    fm1 = ('<div class="fm1"><div>' + "".join(f'<div class="k"><i></i>{k}</div>' for k in ("MASTER", "SELECT", "PRESETS", "ALGORITHM")) +
           '</div><div class="scr"><img src="../img/home.png" alt=""></div><div class="bt">' +
           "".join(f"<span>{b}</span>" for b in "FX SEL ENV LFO EDIT GLO HOME SAVE ARP SEQ PLAY REC".split()) +
           '<span style="grid-column:span 3">OCT−</span><span style="grid-column:span 3">OCT+</span>'
           '<div class="top" style="grid-column:1/-1;margin-top:2mm">' + "".join(f'<div class="k"><i></i>{k}</div>' for k in ("K1", "K2", "K3", "K4")) +
           '</div></div><div class="keys27">' + "".join(f'<span class="{"b" if i in BLACK else ""}"></span>' for i in range(27)) + "</div></div>")
    p.append(page(f'<div class="kick">{L["p2k"]}</div><h2>{L["p2h"]}</h2><p>{L["p2t"]}</p>{fm1}<table>{ctl}</table>', L, 2))
    s3 = "".join(f"<li>{s}</li>" for s in L["steps3"])
    p.append(page(f'<div class="kick">{L["p3k"]}</div><h2>{L["p3h"]}</h2><div class="row"><ol class="steps">{s3}</ol>'
                  f'<div><img class="shot" src="../img/boot.png" alt=""><div class="cap">BOOT</div><br><img class="shot" src="../img/home.png" alt=""><div class="cap">HOME</div></div></div>', L, 3))
    p.append(page(f'<div class="kick">{L["p4k"]}</div><h2>{L["p4h"]}</h2><p>{L["p4t"]}</p>{keyboard(("KICK", "HAT", "CROSS"))}'
                  f'<div class="row"><div><p class="note">{L["p4try"]}</p>'
                  + grid16([("HAT", "x.x.x.x.x.x.x.x.", "on"), ("KICK", "........x.......", "x"), ("CROSS", "........x.......", "x")]) +
                  f'<p>{L["p4knobs"]}</p></div><div><img class="shot" src="../img/drum.png" alt=""><div class="cap">EDIT › SOUND · DRUM</div></div></div>', L, 4))
    s5 = "".join(f"<li>{s}</li>" for s in L["steps5"])
    p.append(page(f'<div class="kick">{L["p5k"]}</div><h2>{L["p5h"]}</h2><p>{L["p5t"]}</p><div class="row"><ol class="steps">{s5}</ol>'
                  f'<div><img class="shot" src="../img/seq.png" alt=""><div class="cap">SEQ › GRID</div></div></div>'
                  + grid16([("T1 HAT", "x.x.x.x.x.x.x.x.", "on"), ("T2 KICK", "........x.......", "x"), ("T3 CROSS", "........x.......", "x")]), L, 5))
    s6 = "".join(f"<li>{s}</li>" for s in L["steps6"])
    p.append(page(f'<div class="kick">{L["p6k"]}</div><h2>{L["p6h"]}</h2><div class="row"><ol class="steps">{s6}</ol>'
                  f'<div><img class="shot" src="../img/mixer1.png" alt=""><div class="cap">HOME › MIXER 1</div><br><img class="shot" src="../img/perform.png" alt=""><div class="cap">FX (HOLD) › PERFORM</div></div></div>', L, 6))
    rows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in L["btn"])
    p.append(page(f'<div class="kick">{L["p7k"]}</div><h2>{L["p7h"]}</h2><table><tr><th>{L["th_btn"]}</th><th>{L["th_tap"]}</th><th>{L["th_hold"]}</th></tr>{rows}</table>', L, 7))
    half = (len(KEYS) + 1) // 2
    kt = lambda a, b: "".join(f"<tr><td>{NOTES[i]}</td><td><b>{KEYS[i]}</b></td></tr>" for i in range(a, b))
    p.append(page(f'<div class="kick">{L["p8k"]}</div><h2>{L["p8h"]}</h2><div class="row">'
                  f'<table><tr><th>{L["th_key"]}</th><th>{L["th_drum"]}</th></tr>{kt(0, half)}</table>'
                  f'<table><tr><th>{L["th_key"]}</th><th>{L["th_drum"]}</th></tr>{kt(half, len(KEYS))}</table></div>'
                  f'<div class="box">KITS: <b>{L["kits"]}</b></div><p class="note">{L["save"]}</p><p>{L["more"]}</p>', L, 8))
    return (f'<!doctype html><html lang="{L["lang"]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{L["title"]}</title><link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link href="https://fonts.googleapis.com/css2?family=Lilita+One&family=Anton&family=Archivo:wght@500;800&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">'
            f'<style>{CSS}</style></head><body>{"".join(p)}</body></html>')


def chrome():
    c = os.environ.get("CHROME") or shutil.which("google-chrome") or shutil.which("chromium")
    mac = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    return c or (mac if Path(mac).exists() else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args()
    (SITE / "guide").mkdir(parents=True, exist_ok=True)
    for code, L in T.items():
        html = SITE / "guide" / f"{code}.html"
        html.write_text(build(L))
        print(f"{code}: {html.relative_to(ROOT)}")
        if a.no_pdf:
            continue
        c = chrome()
        if not c:
            sys.exit("gen_guide: no Chrome (set CHROME)")
        pdf = ROOT / "docs" / f"{L['file']}.pdf"
        subprocess.run([c, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000",
                        f"--print-to-pdf={pdf}", html.as_uri()], check=True, capture_output=True)
        print(f"{code}: {pdf.relative_to(ROOT)} ({pdf.stat().st_size // 1024} KB; tools/build_site.sh puts it on the site)")


if __name__ == "__main__":
    main()
