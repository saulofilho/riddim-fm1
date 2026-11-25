# RIDDIM — plano do firmware

Groovebox de **reggae roots** para o M-VAVE FM-1: rocksteady, one drop, rockers, steppers e **dub tocado ao vivo**.
A banda inteira sai do aparelho: bateria, baixo de sub, skank, bubble de órgão, melódica e metais, tudo sintetizado, e
uma mesa de dub com mola, eco de fita e mutes para "versionar" a música enquanto ela toca.

Firmware livre (GPL-3.0-only), como o GL!TCH, o COQUÍ e o BAILE.

**Mood board:** [`docs/moodboard/index.html`](docs/moodboard/index.html) (abra no navegador). O resumo está em
[Mood](#mood).

Criado em 2026-11-25. Pasta: `projetos-git/riddim-fm1`.

## A decidir antes da Fase 0

| Código | O quê | Proposta |
| --- | --- | --- |
| D1 | Base | **Decidido em 2026-11-25: GR!MM 2.0.2** (tag `v2.0.2`, commit `b519acb`, remoto `upstream`), trazendo do COQUÍ o que é nosso e serve (ver [Por que esta base](#por-que-esta-base)) |
| D2 | Nome | **Decidido em 2026-11-25: RIDDIM** (livre no catálogo do Hub nesse dia). Evitar "DUB": já existe o DUB-1 (dub techno). Ver [Vizinho no Hub](#vizinho-no-hub-sloop-dub) |
| D3 | Identidade | **`FM-1_932`** (livre no catálogo em 2026-11-25, conferido no dia da Fase 1). Evitar 95x (série da KAWA) e 97x (série de outro autor) |
| D4 | Idioma da tela | **Inglês** na tela, porque o vocabulário do gênero é jamaicano (SKANK, BUBBLE, ONE DROP, VERSION); manual e hub em PT e EN |
| D5 | Nyabinghi | Fora da 1.0. É música de rito; só entra se for feita com cuidado e o autor aprovar |
| D6 | Vermelho, ouro e verde | Usar como cores de tinta e papel de cartaz, **nunca** como faixa de bandeira. Ver [Mood](#mood) |

## Vizinho no Hub: sloop-DUB

Achado em 2026-11-25: o **sloop-DUB** (`FM-1_234`, de outro autor, no Hub desde 2026-11-11, 217 instalações) já é um
firmware de dub/reggae: isolador de 4 bandas com mutes, filtro de DJ, **throws de eco por track**, eco de fita, voz de
sirene, e 75 riddims famosos da Riddim Collection (African Beat, Real Rock, Sleng Teng), com samples CC0.

O RIDDIM precisa ser outra coisa, e o plano já é:

| sloop-DUB | RIDDIM |
| --- | --- |
| Riddims famosos copiados, um banco de patterns | Nada copiado: estilos de bateria (GROOVE) e linhas geradas sobre o acorde que você segura |
| Samples CC0 | Tudo sintetizado, a banda inteira |
| Mixagem de DJ (isolador, filtro) | Mesa de dub de estúdio: **mola**, mutes no compasso, **VERSION** (o dub que se mixa sozinho) |
| | HUMAN (atrás do tempo), visual de cartaz e dub plate, manual em PT e EN |

Na descrição do Hub (`fmhub.json`), dizer isso em uma frase: "a roots band you play, not a bank of riddims".

## Por que esta base

O GR!MM (base do GL!TCH e do COQUÍ) já tem o que uma banda de reggae precisa, e o COQUÍ já provou o caminho:

| O reggae roots precisa de | O GR!MM tem | O COQUÍ já fez (código nosso) |
| --- | --- | --- |
| Uma banda: bateria, baixo, skank, órgão | 4 tracks, 7 fontes (VA, FM, SAMPLE, WHEEL, PHYS, PHASE) | A fonte PERC, sintetizada, com até 10 golpes sem roubar vozes |
| Estilos de bateria que tocam sozinhos | Sequenciador de 64 passos, swing, chance, ratchets | **GROOVE**: estilos de 2 compassos com acento, ghost, FILL e FEEL |
| Skank, bubble e baixo sobre o acorde | Arpejador, acorde numa tecla | **Linhas do ARP** sobre o acorde segurado (TUMBAO, MONTUNO) |
| Tocar atrás do tempo | | **HUMAN**: cada golpe um pouco atrasado e mais fraco |
| Dub: eco de fita e reverb | Tape, delay, reverb, grain | **AMBIENTE**: cenas de efeito (já tem uma DUB) |
| Visualizador no palco | Áudio por USB | O adaptador SysEx que o Afterglow lê |

A KAWA (base do BAILE) tem 64 efeitos live e fatias de break, que são ótimos para funk, mas o reggae raiz é uma banda
tocando, não sample picotado. Alternativa: fork direto do COQUÍ (mais rápido, mas herda 14 estilos e 44 sons latinos
para trocar).

## Decisões (propostas)

| Tema | Proposta |
| --- | --- |
| Gêneros da 1.0 | Rocksteady, early reggae (1968–70), one drop, rockers, steppers, flyers (o chimbal aberto no contratempo), rub-a-dub, dub |
| Tempo | Padrão **76 BPM**, 16 passos por compasso, com FEEL (shuffle) ligado. Rocksteady e early ganham projetos no tempo deles |
| Formato | 4 tracks: **T1 bateria** (GROOVE), **T2 baixo**, **T3 skank** (guitarra e piano), **T4 bubble** (órgão), melódica ou metais |
| Som | 100 % sintetizado. **Nenhuma gravação de disco, nenhum riddim famoso copiado nota por nota.** Os 4 slots de sample ficam para o usuário |
| Dub | É o coração: página DUB com mutes por track no compasso, THROW para o eco, mola, filtro e VERSION (o dub que se mixa sozinho) |
| Temas no FM-1 | **NOITE** (feito). **PAPEL** (creme, para luz do dia): a decidir, ver Andamento |
| Hardware | Simulador e emulador web até haver teste no FM-1. Aceitar as duas flashes (`0x856014` e `0xB36014`), como o COQUÍ |
| Repositório | git local; trabalho no `main`; o autor faz push, merge e tags; público só quando o autor mandar |
| Licença | GPL-3.0-only, autoria de cada parte em `LICENSING.md` |
| READMEs | PT e EN atualizados no mesmo commit de cada melhoria (regra do BAILE) |

## Fases

0. **Ambiente.** Clonar o GR!MM 2.0.2 (remoto `upstream`, commit fixo), toolchain JieLi + SDK AC79 em Docker como no
   COQUÍ. Compilar o original, rodar os testes host e o emulador web. Medir o orçamento (CPU, flash, RAM) antes de
   mudar código.
1. **Identidade.** `PRODUCT` (D3), `APP_NAME`, pacote `riddim.fwsc`, magics próprios (projeto, sample, ajustes,
   SysEx; não lê saves de outros firmwares). Temas NOITE e PAPEL. Tela de boot: a agulha desce num selo de compacto
   que gira, e o nome ecoa. `LICENSING.md`, READMEs PT e EN.
2. **Bateria.** Fonte DRUM (a partir da PERC do COQUÍ), sintetizada: bumbo abafado e afinado, **cross-stick** (a alma
   do one drop), caixa com rimshot, chimbal fechado e aberto, chimbal de pedal, tons de virada, shaker, **syndrum**
   ("piu" do fim dos anos 70), crash da mola. Quatro kits: STUDIO (seco, anos 70), YARD (sala), DUB (curto, para a
   mola), STEPPERS (bumbo em todos os tempos). Custo por voz medido.
3. **GROOVE.** Estilos de 2 compassos: ONE DROP, ROCKERS, STEPPERS, FLYERS, ROCKSTEADY, EARLY, RUB-A-DUB. FILL a
   cada 4 ou 8 compassos (a virada de tons que cai no "um"), FEEL (shuffle) e HUMAN (atrás do tempo).
4. **A banda.** Modos novos do ARP sobre o acorde segurado: **SKANK** (o corte no 2 e no 4, abafado), **BUBBLE** (o
   órgão em colcheias, com a mão esquerda e a direita), **BASS** (linhas de raiz, quinta, oitava e passagem, com o
   espaço no lugar certo: o baixo respira), **HORNS** (frases curtas de metais no fim da frase). Sons de fábrica: SUB
   BASS, ROUND BASS, SKANK GUITAR (PHYS, abafada), UPRIGHT PIANO, BUBBLE ORGAN (drawbar com chorus girando), CLAV,
   MELODICA, HORNS (trompete, sax e trombone), DUB SIREN, SYNDRUM. O baixo e o skank trazem a linha ao carregar.
5. **Dub.** O que o GR!MM não tem: **MOLA** (reverb de mola, com o "boing" ao chacoalhar), **ECO** de fita que vai
   até a auto-oscilação e muda de tom ao girar o TIME, filtro passa-alta e passa-baixa para varrer, **THROW** (manda a
   track para o eco enquanto segura, a cauda continua), mutes de track que entram no compasso. **VERSION**: um botão
   que faz o dub sozinho (tira e devolve tracks, joga ecos nos fins de frase) com uma quantidade de 0 a 100. Cenas no
   estilo do AMBIENTE: SECO, STUDIO, YARD, SOUND SYSTEM, DUB, ESPAÇO.
6. **Projetos de fábrica.** Um por estilo, com banda completa, e uma "versão" dub de cada um.
7. **Web.** Hub (cena do boot animada, cada estilo com áudio do próprio firmware, a banda tocável, a mesa de dub),
   emulador, editor, instalador no navegador, manual e guia de primeiros passos em PT e EN, adaptador do Afterglow.
8. **Release.** `./build.sh --release 1.0`, teste no FM-1 (instalar a partir do V15 e de outro firmware, sair,
   voltar, update interrompido), `docs/TEST-RESULTS-1.0.md`, envio ao FM-1 Firmware Hub com `fmhub.json`.

## Andamento

**2026-11-25: Fase 0, em parte.** GR!MM 2.0.2 clonado nesta pasta (branch `main` na tag `v2.0.2`, remoto
`upstream`), sem mudança no código. O plano e o mood board ainda não estão em commit.

- `tests/run_host.sh`: **passa** (14 suítes, 302 checagens). No Mac o host não compila direto (o
  `section(".pool")` é sintaxe ELF): rodar num contêiner Linux:
  `docker run --rm -v "$PWD":/work -w /work python:3.12-bookworm sh -c "pip install -q Pillow mido; sh tests/run_host.sh"`
- `./build.sh` (com `PATH="$PWD/.venv/bin:$PATH"`, Docker ligado): **compila**, `build/grimm.fwsc`, 610160 B,
  identidade ainda `FM-1_966` (a do GR!MM; troca na Fase 1).
- Falta na Fase 0: o emulador web (`web/`), o stress test.

**2026-11-25: Fase 1, identidade (em parte).** Pasta renomeada para `riddim-fm1`.

- Nome **RIDDIM** (`APP_NAME`), identidade **`FM-1_932`** (`tools/build.py`, `platform.c`, `fm1_sample_upload.py`,
  `tests/device_names.py`), pacote `build/riddim.fwsc`.
- Magics próprios: projeto `RDOB`, slots `RDSL`, ajustes `RDST`, samples `RDSP`, sons `R` (GR!MM: `GRMK`, `GRLS`,
  `DNGY`, `GSMP`, `T`). Editor web e os samples de fábrica gerados (`firmware/gen/riddim_samples.h`) acompanham.
- Arquivos: `firmware/src/grimm.c` → `riddim.c`, `firmware/gen/grimm_*.h` → `riddim_*.h`, e os nomes em minúsculas
  (binário de host, wasm, chaves do editor, arquivos de backup) de `grimm` para `riddim`. Links e créditos do GR!MM
  ficam.
- SysEx continua `F0 7D 47 52` ("GR"), como no COQUÍ: o editor e o Afterglow falam com a família GR!MM por ele; a
  identidade já separa os firmwares.
- Teste de saves: o antigo ("o projeto do GR!MM 1.0 carrega igual") virou "o projeto do GR!MM 1.0 **não** é lido: o
  aparelho fica como novo". `rc9_test.py` usa o magic `R`.
- `tests/run_host.sh`: **passa** (14 suítes, 302 checagens, mais o de saves). `./build.sh`: **compila**,
  610160 B, `FM-1_932`. Nada testado no FM-1.
- Falta na Fase 1: temas NOITE e PAPEL, tela de boot, HOME, os textos "GR!MM" que aparecem na tela e na web,
  `LICENSING.md`, READMEs PT e EN, `fmhub.json`.

**2026-11-25: Fase 1, a tela.** Telas em `docs/screens/riddim-boot.png` e `riddim-home.png` (do modo host).

- **Paleta NOITE** (`ui.c`): tinta `#17130E`, tinta gasta, papel na sombra, papel cinza, papel `#EFE4CB`. Cores de
  destaque do SYSTEM: RED, GOLD, GREEN, BLUE (eram RED, AMBER, TEAL, VIOLET). Tinta por track na HOME: T1 vermelho,
  T2 verde, T3 ouro, T4 azul.
- **Boot:** o compacto gira (um brilho nos sulcos, uma volta a cada ~1,8 s), o braço desce em ~1,5 s, e o nome
  aparece com três ecos azuis caindo atrás dele. Linha de baixo: `FM-1 / ROOTS / DUB / V0.1`.
- **HOME:** a pilha do sound system, uma caixa por track; o cone empurra com o som da track (depois do LEVEL); track
  muda (ou fora do solo) apaga e leva a fita DROP; o rótulo da track selecionada na cor de destaque. Saíram o olho, as
  teias, as estrelas, as velas, os morcegos e as gotas do GR!MM.
- Versão **0.1** (`tools/build.py`, `tests/run_host.sh`, `web/build_web.sh`). Texto "VOLUME (AS GR!MM 1.0)" virou
  "VOLUME (CLASSIC)".
- `tests/data/home_shot.txt`: roteiro de host que mostra a HOME (mute no T3, notas no T1 e no T2).
- `tests/run_host.sh` passa (14 suítes, 302 checagens, mais o de saves); `./build.sh` compila: 503216 B (eram
  506108), RAM 86232 B (eram 87928). **Nada testado no FM-1**: o custo de desenhar a HOME e o boot no aparelho não
  foi medido.
- **PAPEL fica para depois:** o GR!MM tem uma paleta fixa, sem troca de tema; um tema claro pede que todas as
  figuras de todas as páginas funcionem nas duas paletas. Decidir se vale.
- Falta na Fase 1: os textos "GR!MM" do editor e do emulador web (junto com o emulador, que pede o Emscripten; o
  `web/test_web.mjs` confere alguns deles e a versão "2.0"), `LICENSING.md`, READMEs PT e EN, `fmhub.json`.

**2026-11-25: emulador e editor web.** Fecha a Fase 0 (falta só o stress test).

- `web/build_web.sh` roda no contêiner `emscripten/emsdk:3.1.74` (sem instalar o SDK no Mac):
  `docker run --rm -v "$PWD":/work -w /work emscripten/emsdk:3.1.74 sh web/build_web.sh` → `web/dist/`, 688 KB de wasm.
- `node web/test_web.mjs` roda num contêiner Node (compara com o binário de host, que é Linux):
  `docker run --rm -v "$PWD":/work -w /work node:22-bookworm node web/test_web.mjs`. **Passa: 100 checagens**, som e
  telas iguais ao modo host, pixel a pixel. Rodar depois do `tests/run_host.sh`.
- Textos: título, descrição, CONNECT, mensagens de erro e rodapés dizem RIDDIM; o rodapé leva ao repositório do
  RIDDIM e diz "based on GR!MM"; o cabeçalho do editor diz EDITOR 0.1. As notas sobre versões do GR!MM (1.0, 2.0,
  26B2) saíram ou viraram "firmware". Os comentários do código continuam creditando o GR!MM.
- `web/fm1_frames.json` é uma gravação de um FM-1 de verdade com o GR!MM 1.0: o teste agora confere que o som de
  fábrica dele (magic "T") é **recusado**. Gravar os frames de um FM-1 com o RIDDIM (`tools/fm1_editor_test.py
  --record`) quando houver um.
- Visto no navegador (`riddim-web` no `launch.json` do workspace, porta 8821): boot e HOME no emulador, editor sem
  erro no console.
- **Risco anotado:** o SysEx é o mesmo do GR!MM e do COQUÍ (`7D 47 52`), e o INFO não diz o nome do firmware; o
  editor do RIDDIM pode se conectar a um FM-1 com GR!MM. Os sons gravados seriam recusados lá (magic diferente), mas
  um restore de backup escreveria ajustes e slots. Antes da 1.0: o INFO dizer o nome, e o editor conferir.
- O visual do editor e do emulador ainda é o do GR!MM (cores, a gota): o redesenho é da Fase 7.

**2026-11-25: Fase 1 fechada no papel, e o site.** (Falta o teste no FM-1 de tudo isso.)

- **Regra: nada de GR!MM na vitrine.** README, site, páginas web e `fmhub.json` não falam do GR!MM; o crédito fica
  onde a GPL pede: `LICENSING.md` e os cabeçalhos de copyright no código (inclusive os comentários das páginas).
  Igual ao BAILE com a KAWA.
- `LICENSING.md`: a camada "RIDDIM's changes" por cima do licenciamento do GR!MM, que fica inteiro (nomes de arquivo
  atualizados), como no COQUÍ.
- `README.md` (inglês) e `README.pt.md`: o que a 0.1 tem, o plano, como compilar e testar, por que ainda não instalar.
- `fmhub.json`: descrição honesta da 0.1 ("a band you play, not a bank of riddims"), emulador e editor do site.
  `image` aponta para `docs/screens/riddim-home.png` até haver um card.
- **Site (GitHub Pages):** `site/index.html` (capa no estilo do mood board, EN e PT com botão), `tools/build_site.sh`
  (junta `site/`, o emulador e o editor em `emu/`, o mood board em `moodboard/`), `.github/workflows/pages.yml`
  (compila o emulador no contêiner do Emscripten e publica; nada compilado no git). Endereço:
  <https://saulofilho.github.io/riddim-fm1/>. **Do autor:** Settings › Pages › Source: GitHub Actions, uma vez; depois
  cada push no `main` que mexe em `site/`, `web/`, `firmware/` ou no mood board publica. Visto localmente
  (`riddim-site`, porta 8822): sem rolagem lateral no celular nem no computador, todos os links respondem.
- `web/test_web.mjs`: 100 checagens passam (a etiqueta do editor agora leva ao site, `../`).
- Ainda com GR!MM por dentro (não é vitrine, fica para depois): `MANUAL.md` (o manual do GR!MM, sem link nos
  READMEs), `docs/` (BUILDING, API, RULES, EDITOR_PROTOCOL, ui-concept, as telas antigas e `docs/card.png`), os sons e
  samples de fábrica.

Orçamento da base, igual ao medido no COQUÍ em 2026-11-05:

| Recurso | Usado | Limite | Livre |
| --- | --- | --- | --- |
| Código + constantes | 506108 B | 581564 B | ~74 KB |
| RAM `.data` + `.bss` | 87928 B | 98304 B | ~10 KB |
| Pool | 342392 B | 344064 B | ~1,6 KB |
| Pilha do usuário (pior caso) | 2996 B | 24320 B | 21 KB |

A pool está cheia (reverb, delay, grain, tape). A mola e o eco de fita da Fase 5 só cabem tirando algo: candidatos
o GRAIN e os coros do VOICE (o COQUÍ fez o mesmo), e reaproveitar o buffer do delay para o eco.

## Mood

Direção **"cartaz de dance e dub plate"**: o reggae raiz visto pelo que se imprimia, carimbava e pintava à mão para o
sound system. Três referências, misturadas:

- **Cartaz de dance:** letras de tipo de madeira, condensadas e pesadas, tinta preta sobre papel de cor gasto de sol,
  várias linhas em tamanhos diferentes, estrelas e setas.
- **Dub plate / selo de compacto:** o círculo do selo, carimbo, data escrita à mão, o furo no meio. É o boot.
- **Caixa de som:** os cones que empurram o ar. É a HOME: cada track é uma caixa da pilha, o cone pulsa no golpe.

E uma marca própria: **tipografia em eco**. A palavra se repete, deslocada e mais fraca, como a cauda de um delay.

- **Paleta:** tinta `#17130E` (fundo do NOITE, traço), papel `#EFE4CB` (texto, fundo do PAPEL), cinza papel
  `#A39882` (legendas), e as tintas de cartaz: vermelho `#C7382B`, ouro `#E8A825`, verde `#2E7A47`, mais o azul do
  eco `#3E6E9E` só para caudas de efeito. Uma cor por track: bateria vermelho, baixo verde, skank ouro, bubble azul.
- **Tipografia:** Anton (título de cartaz), Alfa Slab One (tipo de madeira, rótulos), IBM Plex Mono (legendas). No
  FM-1, as letras grandes como bitmaps gerados.
- **Status** pela quantidade de tracks tocando: QUIET, WARMING, ROCKING, HEAVY.
- **Vocabulário da tela:** RIDDIM, SKANK, BUBBLE, DROP, ROCKERS, STEPPERS, VERSION, THROW, SPRING, ECHO, SOUND.
- **Regras:** papel e tinta, nada de neon nem gradiente; textura de impressão (registro torto, tinta falhada) com
  moderação; cor é track; o som manda no desenho (o cone pulsa, o eco deixa rastro).
- **Evitar:** leão, retratos, folha, bandeira em faixas, símbolos religiosos do rastafarianismo, patois de caricatura,
  nomes de artistas, estúdios ou riddims famosos. A celebração é do som, da banda e do sound system.

## Riscos

- **CPU.** Mola e eco de fita juntos, mais 4 tracks e a bateria: medir no simulador desde a Fase 0 e no FM-1 cedo.
- **Grave em alto-falante pequeno.** O sub do reggae some no alto-falante do FM-1. Reusar o que o BAILE aprendeu no
  GRAVE+ (harmônicos, sem subir o pico).
- **Respeito cultural.** É música com raiz religiosa e política. Seguir as regras do Mood; na dúvida, fica de fora.
- **Direitos.** Linhas e estilos são escritos no estilo, nunca transcritos de gravações.
- **Nome.** Conferir no Hub e no GitHub no dia da Fase 1.
