# -*- coding: utf-8 -*-
r"""P13c: doplní do HANDOFF.md §8 tabulku omylů **144–148** (sekce `8s`).

HANDOFF.md je **append-only záznam** — skript proto vkládá **novou sekci**
za `8r` a před `## 9.`, a nic jiného nemění. Před zápisem i po něm se ověřuje,
že kotvy existují právě jednou (`overovani` §9.8).
"""

import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = pathlib.Path(r"E:\Workspaces\forge-orchestra\HANDOFF.md")
t = P.read_text(encoding="utf-8")

KOTVA = "\n---\n\n## 9. Co už otevřené NENÍ\n"
assert t.count(KOTVA) == 1, f"kotva `## 9.` nalezena {t.count(KOTVA)}x"

NOVY = """
---

### 8s. Omyly 144–148 — AKČNÍ session 5. 10. 2026 (P13c: OPRAVA PĚTI MĚŘIDEL)

**Pět omylů, a všechny mají stejný podpis jako předchozí sekce: měřil jsem
něco jiného, než jsem si myslel.** Záznam: `HANDOFF.md` **§31.8**.
**Tři z nich (144, 145, 148) vznikly ve VLASTNÍM MĚŘIDLE** — a dva z nich
(147, 148) by vedly k **nepravdivému nálezu o správném kódu**.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **144** | „Vrátím do `g3` STARÝ literál cesty (`orchestra/tools/over-skilly.py`) — to je přece vada H48." | **Není.** Vada H48 je **nedosazený ZÁZNAMNÍK** (`<TOOLS>`), ne jiná (neexistující) cesta. `dosad()` s takovým textem nemá co dělat a `NEDOSAZENÉ CESTY` **správně mlčelo** | **Měřená podmínka se musí obrátit, ne jen „něco změnit"** (`overovani` §7.14). Oprava: mutace **vypíná substituci** — záznamník zůstane v příkazu a soubor s ostrými závorkami neexistuje |
| **145** | „S vadou se v zachyceném výstupu objeví `can't open file` — na to se dá ptát." | **Neobjeví.** PowerShell spouštěl neexistující cestu a spadl **sám** (`WinError 2`); v `capture_output` nebylo NIC z toho, co jsem hledal. Test proto hlásil „brána vadu nevidí" | **Predikát mířil na TEXT interpretu, ne na VÝSLEDEK.** Oprava: signál = `exit=2` **a zároveň** žádný čítač **a zároveň** krátký výstup. (A je to táž past, jakou zadání samo používá: `can't open file` je text **Pythonu**, ne stav.) |
| **146** | „Mutace `install-into-repo.ps1` je jen náhrada textu — kódování neřeším." | Zápis **zahodil UTF-8 BOM** (soubor ho má), a `blok_generatoru()` čte `utf-8-sig` → mutace by měřila **jiný jev** | **Zapisuj ve stejném kódování, v jakém čteš** (`dsh-prostredi` §5b). Oprava: BOM se detekuje, zapisuje se s ním a po zápisu se **jeho přítomnost ověří** |
| **147** | „Když soubor obsahuje `ZMĚŘENO`, najdu to vzorem `ZMĚŘENO`." | **Ve třech souborech bylo `ZMEŘENO`** — chybělo `Ě` (`verify-setup.py`, `lint-roadmapa.py`, `f3-over-deploy.mjs`). **Výpis vypadal dobře, vadný byl SOUBOR** | **Přesně obrácená past, než popisuje `dsh-prostredi` §2b** (tam vypadá vadně soubor, a je to výpis). Našel to **mutační test**; opraveno `_analyza/p13c-oprav-diakritiku.py` a ověřeno **čtením z disku** |
| **148** | „Sken na chybějící importy hlásí 57 souborů — to je velký nález." | **Většina byla falešných.** Vzor `\\bjoin\\s*\\(` chytal i **`arr.join(',')`** (metoda pole). `conductor/src/index.ts` má 9× `Array.join` a `join()` z `node:path` **nikdy nevolá** | **Falešný poplach nutí „opravovat" správný kód** (`overovani` §9.5) — a tady by přidal **import, který soubor nepotřebuje**. Oprava: předpona `.`/`?.`/`\\w` volání vylučuje; `resolve` se **vůbec nehlídá** (`new Promise((resolve) => …)` je jiné `resolve`) |

**Vzor z těch pěti (a je poučnější než u 138–143):** u **třech** z nich šlo
o to, že **měřidlo měřilo samo sebe nebo svůj text** — a **všechny tři** by
vyrobily **nepravdivý závěr o bráně** („je slepá", „neměří", „má 57 nálezů").
**Dva (144, 145) odhalil až běh testu, ne čtení kódu** — což je týž závěr jako
u předchozích sekcí: **mutace, která se tiše neprovede nebo míří na jinou
podmínku, tvrdí totéž co mutace, která projde.**
"""

t = t.replace(KOTVA, NOVY + KOTVA, 1)
P.write_text(t, encoding="utf-8", newline="")
zpet = P.read_text(encoding="utf-8")
assert "### 8s. Omyly 144–148" in zpet, "sekce 8s se nevložila"
assert zpet.count("### 8s. Omyly 144–148") == 1
assert "## 9. Co už otevřené NENÍ" in zpet
print("§8s vložena;", len(zpet.splitlines()), "řádků")
