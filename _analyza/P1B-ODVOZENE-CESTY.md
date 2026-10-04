# P1b — ODVOZENÉ CESTY (co sken přímých cest NEVIDÍ)

> **Co tenhle dokument JE:** **kontrolní seznam** k přesunu na `E:`
> (krok **P1b** zadání). Generuje `_analyza\p1b-odvozene-cesty.py` —
> **nepřepisuj ručně**, přegeneruj.
> Nejde o soubory, které cestu **uvádějí**, ale o ty, které si ji
> **odvozují z umístění sebe sama**. V `sken-cest-celek.py` se
> **nevyskytnou**, protože v nich žádný literál `Local-Deepseek` není.

## ⚠ Klíčové rozlišení: od SEBE (bezpečné) vs. od RODICE (riziko)

| Odvození | Příklad | Po přesunu |
|---|---|---|
| **od sebe** | `Path(__file__).parent`, `import.meta.url`, `$PSScriptRoot` | **SPRÁVNĚ** — soubor se přesune s repem, odvozená cesta se posune s ním |
| **od rodiče** | `$PSScriptRoot\..`, `Split-Path … -Parent`, `parents[N≥1]` | **JINAM** — mezi starým a novým umístěním je **jiný rodič** (`Local-Deepseek` vs. `E:\Workspaces`) |

**Proč je RODIČ ta past:** dnes je rodičem obou repů `Local-Deepseek`
(a v něm `projects\`, `games\`, `_analyza\`). Po přesunu je rodičem
`E:\Workspaces` — a v něm je **jen dvojice repů-sourozenců**, žádné
`projects\` ani `games\`. Nástroj, který odvozuje z rodiče, proto
**nespadne — jen hledá jinam**, a to je přesně ta tichá vada, kterou
chceme vidět.

## Souhrn

- souborů s odvozenou cestou: **255**
- z toho **RIZIKO** (odvozuje od rodiče): **21**
- z toho **OK** (odvozuje od sebe): **234**

| Oblast | Souborů s odvozenou cestou |
|---|---:|
| `_analyza/` | 181 |
| `games/` | 19 |
| `nastroje stanice/` | 18 |
| `orchestra/` | 28 |
| `root workspace` | 9 |
| **CELKEM** | **255** |

## ⚠ RIZIKO — odvozuje od RODICE (po přesunu míří jinam)

| # | Soubor | Vzory rizika |
|---:|---|---|
| 1 | `_analyza\hl-instal.mjs` | gameforge |
| 2 | `_analyza\p1b-odvozene-cesty.py` | Split-Path -Parent, gameforge |
| 3 | `_asar_probe\verify-skill.mjs` | gameforge |
| 4 | `dsh-consolidation\cleanup\migrate-dsh-data.ps1` | Split-Path -Parent |
| 5 | `dsh-consolidation\cleanup\reminder-karantena.ps1` | Split-Path -Parent |
| 6 | `dsh-consolidation\cleanup\setup-reminder.ps1` | Split-Path -Parent |
| 7 | `dsh-consolidation\cleanup\test-migrace.ps1` | Split-Path -Parent |
| 8 | `dsh-update-0.2.0\verify.ps1` | gameforge |
| 9 | `games\uo-shadows\.forge\node\termux-setup.sh` | gameforge |
| 10 | `games\uo-shadows\tools\blender\_analyze.py` | gameforge |
| 11 | `games\uo-shadows\tools\make_iso_tiles.py` | gameforge |
| 12 | `games\uo-shadows\tools\make_spriteframes.gd` | gameforge |
| 13 | `orchestra\.test\work\forge-quest\scripts\player.gd` | gameforge |
| 14 | `orchestra\.test\work\forge-quest\tools\make_spriteframes.gd` | gameforge |
| 15 | `orchestra\conductor\src\index.ts` | gameforge |
| 16 | `orchestra\install-into-repo.ps1` | Split-Path -Parent |
| 17 | `orchestra\tools\git.cmd` | gameforge |
| 18 | `orchestra\tools\over-dokumentaci.py` | gameforge |
| 19 | `orchestra\tools\repo-files.mjs` | gameforge |
| 20 | `orchestra\tools\test-local.ps1` | Split-Path -Parent, gameforge |
| 21 | `orchestra\tools\verify-setup.py` | gameforge |

## OK — odvozuje od SEBE (po přesunu správně)

| # | Soubor | Vzory |
|---:|---|---|
| 1 | `_analyza\_registr-bran.py` | __file__ |
| 2 | `_analyza\_s24-sonda-1201.py` | __file__ |
| 3 | `_analyza\_s24-sonda-normalizace.py` | __file__ |
| 4 | `_analyza\_s24-sonda-over.py` | __file__ |
| 5 | `_analyza\_s24-sonda-over2.py` | __file__ |
| 6 | `_analyza\_s24-sonda-over3.py` | __file__ |
| 7 | `_analyza\_s24-sonda-vzor.py` | __file__ |
| 8 | `_analyza\_s24-sonda-vzor5.py` | __file__ |
| 9 | `_analyza\_s25-brany-co-chrani.py` | __file__ |
| 10 | `_analyza\_s25-prejmenuj-zalohu.py` | __file__ |
| 11 | `_analyza\_s25-sonda-8.py` | __file__ |
| 12 | `_analyza\_s25-sonda-b5.py` | __file__ |
| 13 | `_analyza\_s25-sonda-bloky.py` | __file__ |
| 14 | `_analyza\_s25-sonda-citace.py` | __file__ |
| 15 | `_analyza\_s25-sonda-citace2.py` | __file__ |
| 16 | `_analyza\_s25-sonda-citace3.py` | __file__ |
| 17 | `_analyza\_s25-sonda-g3.py` | __file__ |
| 18 | `_analyza\_s25-sonda-id.py` | __file__ |
| 19 | `_analyza\_s25-sonda-kontrol.py` | __file__ |
| 20 | `_analyza\_s25-sonda-m3.py` | __file__ |
| 21 | `_analyza\_s25-sonda-pocet.py` | __file__ |
| 22 | `_analyza\_s25-sonda-rozchody.py` | __file__ |
| 23 | `_analyza\_s25-sonda-s1.py` | __file__ |
| 24 | `_analyza\_s25-sonda-vzorky.py` | __file__ |
| 25 | `_analyza\_s25-test-pocet.py` | __file__ |
| 26 | `_analyza\_s25-zapis-handoff.py` | __file__ |
| 27 | `_analyza\a-kdo-ma-registr.py` | __file__ |
| 28 | `_analyza\a-mutace-run.py` | __file__ |
| 29 | `_analyza\a-oprav-test.py` | __file__ |
| 30 | `_analyza\a-vyrob-stary-blok.py` | __file__ |
| 31 | `_analyza\a2-mutace-izo.py` | __file__ |
| 32 | `_analyza\a3-roadmapa-over.py` | __file__ |
| 33 | `_analyza\a3-srovnej-roadmapu.py` | __file__ |
| 34 | `_analyza\a4-zapis-handoff.py` | __file__ |
| 35 | `_analyza\a5-zapis-kronika.py` | __file__ |
| 36 | `_analyza\a6-zapis-handoff-2.py` | __file__ |
| 37 | `_analyza\aplikuj-skill-patch.py` | __file__ |
| 38 | `_analyza\audit-cleanup.py` | __file__ |
| 39 | `_analyza\audit-snapshot-over.py` | __file__ |
| 40 | `_analyza\audit-snapshot.py` | __file__ |
| 41 | `_analyza\audit1-inventar.py` | __file__ |
| 42 | `_analyza\audit1-mutace.py` | __file__ |
| 43 | `_analyza\audit1b-koren-sonda.py` | __file__ |
| 44 | `_analyza\audit2-rozpory.py` | __file__ |
| 45 | `_analyza\audit2a-mutace.py` | __file__ |
| 46 | `_analyza\audit2a-schema.py` | __file__ |
| 47 | `_analyza\audit2a-sonda.py` | __file__ |
| 48 | `_analyza\audit2b-cisla-proti-zdroji.py` | __file__ |
| 49 | `_analyza\audit2b-over.py` | __file__ |
| 50 | `_analyza\audit2b-sonda.py` | __file__ |
| 51 | `_analyza\audit3-duplikace.py` | __file__ |
| 52 | `_analyza\audit3-hlavicky-over.py` | __file__ |
| 53 | `_analyza\audit4-umisteni.py` | __file__ |
| 54 | `_analyza\audit5-cas-bran.py` | __file__ |
| 55 | `_analyza\audit5b-cena-cteni.py` | __file__ |
| 56 | `_analyza\audit5c-rucni-seznamy.py` | __file__ |
| 57 | `_analyza\audit6-brany-mutace.py` | __file__ |
| 58 | `_analyza\audit7-overeni-zadani.py` | __file__ |
| 59 | `_analyza\b-mutace.py` | __file__ |
| 60 | `_analyza\b-oprav-test.py` | __file__ |
| 61 | `_analyza\b-sonda-65.py` | __file__ |
| 62 | `_analyza\b-sonda-proc-prosel.py` | __file__ |
| 63 | `_analyza\b5-mutace.py` | __file__ |
| 64 | `_analyza\c1-dukaz-selhani.py` | __file__ |
| 65 | `_analyza\c1-oprav-a3.py` | __file__ |
| 66 | `_analyza\c2-hl-rizika-puvodni.py` | __file__ |
| 67 | `_analyza\c2-mutace.py` | __file__ |
| 68 | `_analyza\c2-oprav-n1.py` | __file__ |
| 69 | `_analyza\c2-oprava-uvozovek.py` | __file__ |
| 70 | `_analyza\c2-sonda-uvozovky.py` | __file__ |
| 71 | `_analyza\f1-b1-conductor.py` | __file__ |
| 72 | `_analyza\f2-oprav-cooldown-test.py` | __file__ |
| 73 | `_analyza\f2-over-cooldown.py` | __file__ |
| 74 | `_analyza\f2-sonda-cooldown.py` | __file__ |
| 75 | `_analyza\f2-test-cooldown-puvodni.py` | __file__ |
| 76 | `_analyza\g1-diakritika-novych.py` | __file__ |
| 77 | `_analyza\g1-mutace-diakritika.py` | __file__ |
| 78 | `_analyza\g2-dopln-skilly.py` | __file__ |
| 79 | `_analyza\g3-brany.py` | __file__ |
| 80 | `_analyza\h17-kontrola-klonu.py` | __file__ |
| 81 | `_analyza\h17-kronika-mutace.py` | __file__ |
| 82 | `_analyza\h17-lint-roadmapa.py` | __file__ |
| 83 | `_analyza\h17-mutace-a.py` | __file__ |
| 84 | `_analyza\h17-mutace-b.py` | __file__ |
| 85 | `_analyza\h17-over-c2.py` | __file__ |
| 86 | `_analyza\h17-sonda-vetve.py` | __file__ |
| 87 | `_analyza\handoff-mutace.py` | __file__ |
| 88 | `_analyza\hl-gitattributes.py` | __file__ |
| 89 | `_analyza\hl-konce-radku-v-repu.py` | __file__ |
| 90 | `_analyza\hl-kontrola-pred-commitem.py` | __file__ |
| 91 | `_analyza\hl-neanglicky-v-kodu.py` | __file__ |
| 92 | `_analyza\hl-rizika-jazyka.py` | __file__ |
| 93 | `_analyza\hlavicky-dopln.py` | __file__ |
| 94 | `_analyza\js-tokeny.mjs` | import.meta.url |
| 95 | `_analyza\k21-kronika.py` | __file__ |
| 96 | `_analyza\k21b-kronika-tabulka.py` | __file__ |
| 97 | `_analyza\k21c-oprav-l16.py` | __file__ |
| 98 | `_analyza\k21d-oprav-handoff.py` | __file__ |
| 99 | `_analyza\k21e-dokonci-75.py` | __file__ |
| 100 | `_analyza\kronika-kontrola.py` | __file__ |
| 101 | `_analyza\over-dokumentaci-mutace.py` | __file__ |
| 102 | `_analyza\p18-prompt-tokeny.py` | __file__ |
| 103 | `_analyza\p18-sonda-tpm.py` | __file__ |
| 104 | `_analyza\p19-push.py` | __file__ |
| 105 | `_analyza\p19-sonda-groq.py` | __file__ |
| 106 | `_analyza\p19g-granule-vs-groq.py` | __file__ |
| 107 | `_analyza\p19h-groq-presne.py` | __file__ |
| 108 | `_analyza\p19i-co-zmensit.py` | __file__ |
| 109 | `_analyza\p19i-sonda.py` | __file__ |
| 110 | `_analyza\p19i-sonda2.py` | __file__ |
| 111 | `_analyza\priprav-skill-patch.py` | __file__ |
| 112 | `_analyza\rozdel-sesny-podklad.py` | __file__ |
| 113 | `_analyza\s16-zapis-handoff.py` | __file__ |
| 114 | `_analyza\s17-zapis-handoff.py` | __file__ |
| 115 | `_analyza\s17b-prepis-handoff.py` | __file__ |
| 116 | `_analyza\s17b-zapis-handoff.py` | __file__ |
| 117 | `_analyza\s18-prepocitej-omyly.py` | __file__ |
| 118 | `_analyza\s18-zapis-handoff.py` | __file__ |
| 119 | `_analyza\s18c-dopln-omyl68.py` | __file__ |
| 120 | `_analyza\s18d-sestav-handoff.py` | __file__ |
| 121 | `_analyza\s18e-dopln-l13.py` | __file__ |
| 122 | `_analyza\s18f-oprav-hlavicku.py` | __file__ |
| 123 | `_analyza\s19-dopln-odpoved-groq.py` | __file__ |
| 124 | `_analyza\s19-zapis-handoff.py` | __file__ |
| 125 | `_analyza\s19b-dopln-souhrn.py` | __file__ |
| 126 | `_analyza\s19c-dopln-kroniku.py` | __file__ |
| 127 | `_analyza\s19d-dopln-h13.py` | __file__ |
| 128 | `_analyza\s19e-oprav-hlavicku.py` | __file__ |
| 129 | `_analyza\s19f-oprav-deploy.py` | __file__ |
| 130 | `_analyza\s19g-zapis.py` | __file__ |
| 131 | `_analyza\s19h-souhrn-8g.py` | __file__ |
| 132 | `_analyza\s19i-souhrn-oprava.py` | __file__ |
| 133 | `_analyza\s19j-hlavicka-ziva.py` | __file__ |
| 134 | `_analyza\s19k-zapis.py` | __file__ |
| 135 | `_analyza\s19l-souhrn-8g.py` | __file__ |
| 136 | `_analyza\s19m-dopln-commity.py` | __file__ |
| 137 | `_analyza\s20-odloz-groq.py` | __file__ |
| 138 | `_analyza\s20b-plan-poradi.py` | __file__ |
| 139 | `_analyza\s20c-zapis-rozhodnuti.py` | __file__ |
| 140 | `_analyza\s20d-sonda.py` | __file__ |
| 141 | `_analyza\s20d-zadani.py` | __file__ |
| 142 | `_analyza\s20e-zadani-doplnky.py` | __file__ |
| 143 | `_analyza\s21-zapis-handoff.py` | __file__ |
| 144 | `_analyza\s23-kronika.py` | __file__ |
| 145 | `_analyza\s23-zapis.py` | __file__ |
| 146 | `_analyza\s23b-dopln.py` | __file__ |
| 147 | `_analyza\s23c-dopln2.py` | __file__ |
| 148 | `_analyza\s24-dopln-h31.py` | __file__ |
| 149 | `_analyza\s24-dopln-h32.py` | __file__ |
| 150 | `_analyza\s24-dopln-kronika.py` | __file__ |
| 151 | `_analyza\s24-dopln-snapshot.py` | __file__ |
| 152 | `_analyza\s24-g3-souhrn.py` | __file__ |
| 153 | `_analyza\s24-meridla-mutace.py` | __file__ |
| 154 | `_analyza\s24-meridla-over.py` | __file__ |
| 155 | `_analyza\s24-opatreni-dukazy.py` | __file__ |
| 156 | `_analyza\s24-opatreni6-pokryti.py` | __file__ |
| 157 | `_analyza\s24-slepota-audit2b-presne.py` | __file__ |
| 158 | `_analyza\s24-slepota-audit2b.py` | __file__ |
| 159 | `_analyza\s24-zapis-handoff.py` | __file__ |
| 160 | `_analyza\s8f-omyl60-zapis.py` | __file__ |
| 161 | `_analyza\s8f-prepis-handoff.py` | __file__ |
| 162 | `_analyza\s8f-zapis-handoff.py` | __file__ |
| 163 | `_analyza\t1-m3-brana.py` | __file__ |
| 164 | `_analyza\t3-kronika-mutace.py` | __file__ |
| 165 | `_analyza\t6-commit.py` | __file__ |
| 166 | `_analyza\t8-zapis-push.py` | __file__ |
| 167 | `_analyza\t8d-prepocet-kroniky.py` | __file__ |
| 168 | `_analyza\t8e-srovnej-cisla.py` | __file__ |
| 169 | `_analyza\t8f-dosrovnej.py` | __file__ |
| 170 | `_analyza\test-neanglicky-skener.py` | __file__ |
| 171 | `_analyza\test-skill-patch.py` | __file__ |
| 172 | `_analyza\v1-kotvy.py` | __file__ |
| 173 | `_analyza\v2-m3-lek.py` | __file__ |
| 174 | `_analyza\v3-kronika-stavy.py` | __file__ |
| 175 | `_analyza\v4-omyly-nezavisle.py` | __file__ |
| 176 | `_analyza\v5-radky-souboru.py` | __file__ |
| 177 | `_analyza\v7-kryti-dokumentu.py` | __file__ |
| 178 | `_analyza\v8-kotvy-handoff.py` | __file__ |
| 179 | `_analyza\zaloha\audit2a-schema.pred-opravou.py` | __file__ |
| 180 | `dsh-consolidation\cleanup\cleanup-dsh.ps1` | PSScriptRoot |
| 181 | `dsh-consolidation\old-desktop-shell\scripts\ensure-icon.js` | __dirname |
| 182 | `dsh-consolidation\old-desktop-shell\scripts\feed-server.js` | __dirname |
| 183 | `dsh-consolidation\old-desktop-shell\scripts\gen-whale-path.js` | __dirname |
| 184 | `dsh-consolidation\old-desktop-shell\scripts\make-icon.js` | __dirname |
| 185 | `dsh-consolidation\old-desktop-shell\scripts\patch-dsh.js` | __dirname |
| 186 | `dsh-consolidation\old-desktop-shell\scripts\preview-status.js` | __dirname |
| 187 | `dsh-consolidation\old-desktop-shell\scripts\prune-node-modules.js` | __dirname |
| 188 | `dsh-consolidation\old-desktop-shell\scripts\update-dsh.js` | __dirname |
| 189 | `dsh-consolidation\old-desktop-shell\scripts\verify-package.js` | __dirname |
| 190 | `dsh-consolidation\old-desktop-shell\src\main.js` | __dirname |
| 191 | `dsh-consolidation\old-home\plugins-collection\extracted\dsh-openwolf-0.10.0\package\bin\wolf.mjs` | import.meta.url |
| 192 | `dsh-plugins\naklad-indikator\test-tarif.mjs` | import.meta.url |
| 193 | `dsh-plugins\temata\kontrola-temat.mjs` | import.meta.url |
| 194 | `dsh-update-0.2.0\preflight.ps1` | PSScriptRoot |
| 195 | `dsh-update-0.2.0\update-dsh.ps1` | PSScriptRoot |
| 196 | `games\uo-shadows\.forge\baseline.py` | __file__ |
| 197 | `games\uo-shadows\.forge\check-assets.py` | __file__ |
| 198 | `games\uo-shadows\.forge\node\providers-check.mjs` | import.meta.url |
| 199 | `games\uo-shadows\.forge\node\self-test.mjs` | import.meta.url |
| 200 | `games\uo-shadows\.forge\node\vision.test.mjs` | import.meta.url |
| 201 | `games\uo-shadows\.forge\node\worker.mjs` | import.meta.url |
| 202 | `games\uo-shadows\.forge\pick-provider.mjs` | import.meta.url |
| 203 | `games\uo-shadows\.forge\report.mjs` | import.meta.url |
| 204 | `games\uo-shadows\tools\blender\_smoke.py` | __file__ |
| 205 | `games\uo-shadows\tools\blender\build_character.py` | __file__ |
| 206 | `games\uo-shadows\tools\blender\postprocess.py` | __file__ |
| 207 | `games\uo-shadows\tools\gamewindow_preview.py` | __file__ |
| 208 | `games\uo-shadows\tools\items_postprocess.py` | __file__ |
| 209 | `games\uo-shadows\tools\make_npc.py` | __file__ |
| 210 | `games\uo-shadows\tools\sword_contact.py` | __file__ |
| 211 | `obrazky\comfy_supervisor.py` | __file__ |
| 212 | `obrazky\comfy_txt2img.py` | __file__ |
| 213 | `obrazky\run_comfy_debug.py` | __file__ |
| 214 | `obrazky\start-comfy.ps1` | PSScriptRoot |
| 215 | `orchestra\bin\task.mjs` | import.meta.url |
| 216 | `orchestra\repo\.forge\baseline.py` | __file__ |
| 217 | `orchestra\repo\.forge\check-assets.py` | __file__ |
| 218 | `orchestra\repo\.forge\node\providers-check.mjs` | import.meta.url |
| 219 | `orchestra\repo\.forge\node\self-test.mjs` | import.meta.url |
| 220 | `orchestra\repo\.forge\node\vision.test.mjs` | import.meta.url |
| 221 | `orchestra\repo\.forge\node\worker.mjs` | import.meta.url |
| 222 | `orchestra\repo\.forge\pick-provider.mjs` | import.meta.url |
| 223 | `orchestra\repo\.forge\report.mjs` | import.meta.url |
| 224 | `orchestra\tools\asset-fetch.mjs` | import.meta.url |
| 225 | `orchestra\tools\cancel-stale-runs.mjs` | import.meta.url |
| 226 | `orchestra\tools\diag-baseline.py` | __file__ |
| 227 | `orchestra\tools\roadmap-reset.mjs` | import.meta.url |
| 228 | `orchestra\tools\status.mjs` | import.meta.url |
| 229 | `orchestra\tools\telegram-chat-id.mjs` | import.meta.url |
| 230 | `orchestra\tools\test-check-schema.py` | __file__ |
| 231 | `orchestra\tools\test-cooldown.py` | __file__ |
| 232 | `orchestra\tools\test-licence.py` | __file__ |
| 233 | `orchestra\tools\test-zamek-owns.py` | __file__ |
| 234 | `vision.test.mjs` | import.meta.url |
