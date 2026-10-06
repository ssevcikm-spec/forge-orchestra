# -*- coding: utf-8 -*-
"""Spustí VŠECHNY brány a u každé vypíše, KOLIK toho otevřela (past S27).

PROČ: `AGENTS.md` — „u každé brány se ptej, PROBĚHLA, ne jen neprotestovala".
`exit 0` bez počtu kontrol je ticho, ne zelená. Tenhle skript proto u každé
brány hledá ve výstupu **počet kontrol / souborů / granulí** a ten vypíše.

Píše se i do souboru `_analyza/g3-brany-vystup.txt`, aby se dal zápis ověřit
bez opakovaného běhu.

⚠ NÁVRATOVÝ KÓD (od P19, 6. 10. 2026 — rozhodnutí Úkolu D; ⚠ ROZŠÍŘENO V P20):
  0 = přehled je ÚPLNÝ (každá brána začala a vykázala, co otevřela) **a žádný
      nenulový exit není mimo `OCEKAVANE_NENULOVE`**,
  1 = NĚCO SE NEMĚŘILO (brána vůbec nezačala, nebo běžela bez čítače a není
      v deklarovaném `OCEKAVANE_BEZ_CITACE`) **NEBO se brána rozešla s deklarací
      (NEOČEKÁVANÝ nenulový exit / visutý záznam)**,
  2 = neproběhla ANI JEDNA brána.
⚠ P19 o červených NEROZHODOVAL (nález NA23b) — **P20 to rozhodla**: seznam
`OCEKAVANE_NENULOVE` je níž a `g3` podle něj červené soudí. Důvod, proč to dřív
nešlo: „které nenulové exity jsou správné“ nebylo sepsané.

Použití: python _analyza/g3-brany.py
"""

import os
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── CESTY SE ODVOZUJÍ, NEPŘEPISUJÍ (P8) ──────────────────────────────────────
# ⚠ P13c (4. 10. 2026, nález H48): tenhle seznam měl **11 literálů starých cest**
# (`orchestra/tools/...`, `WS / "games" / "uo-shadows"`, `SOMEONE / "orchestra"`).
# Po přesunu na `E:` proto **15 bran vůbec neběželo** — `subprocess` vrátil
# `exit=2` s `can't open file` a v přehledu to vypadalo jako „červená".
# Naměřeno: `g3-brany-vystup.txt` mělo 15 sekcí s `can't open file`.
#
# Oprava není „přepsat na novou absolutní cestu" — ta by se při dalším přesunu
# rozešla znovu. Cesty se proto **odvozují z umístění tohohle souboru**:
#   WS        = kořen repa orchestra   (`_analyza/..`)
#   HRA       = SOUROZENEC repa        (`WS.parent / "uo-shadows"`)
#   STANICE   = kořen stanice          (dokumenty, které zůstaly stanici, D6)
#   GODOT     = obecný nástroj stanice (D7), s override přes `FORGE_GODOT`
WS = pathlib.Path(__file__).resolve().parent.parent
# ⚠ PŘENOSITELNOST (P22, 6. 10. 2026): `STANICE` a `HRA` byly ZAPEČENÉ absolutní
# cesty (`C:\Users\Ssevc\Local-Deepseek`, `WS.parent / "uo-shadows"`). Vzor pro
# override v repu UŽ BYL (`FORGE_GODOT`, `FORGE_STANICE` v `test-h72-h73.py`
# a `verify-setup.py`) — `g3` ho ale nepoužíval, takže sám blokoval zobecnění
# celého rámce bran. Defaulty zůstávají STEJNÉ, takže chování se nemění.
STANICE = pathlib.Path(os.environ.get("FORGE_STANICE")
                       or r"C:\Users\Ssevc\Local-Deepseek")
HRA = pathlib.Path(os.environ.get("FORGE_HRA") or (WS.parent / "uo-shadows"))
ANALYZA = WS / "_analyza"
TOOLS = WS / "tools"
FORGE = WS / "repo" / ".forge"

# Godot je od D7 OBECNÝ NÁSTROJ STANICE (`E:\Tools\godot\`), ne součást repa.
# Bere se z `FORGE_GODOT`, když je nastavená; jinak se hledá na obvyklých
# místech a **když se nenajde, řekne se to** (tichý `WinError 2` vypadá jako
# rozbitá brána, ne jako chybějící nástroj).
_NAZEV_GODOT = "Godot_v4.7.2-stable_win64_console.exe"


def _najdi_godot() -> pathlib.Path:
    kandidati = []
    if os.environ.get("FORGE_GODOT"):
        kandidati.append(pathlib.Path(os.environ["FORGE_GODOT"]))
    kandidati += [
        WS.parent.parent / "Tools" / "godot" / _NAZEV_GODOT,   # E:\Tools\godot
        pathlib.Path(r"E:\Tools\godot") / _NAZEV_GODOT,
        pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek\_tools\godot") / _NAZEV_GODOT,
    ]
    for k in kandidati:
        if k.is_file():
            return k
    # Nic se nenašlo: vrať první kandidát, ať je ve výpisu VIDĚT, co chybělo.
    # (`spust()` na tom skončí výjimkou a vypíše cestu — to je správné chování.)
    return kandidati[0]


GODOT = _najdi_godot()
USER_DIR = ANALYZA / "a-godot-user"
VYSTUP = ANALYZA / "g3-brany-vystup.txt"
# Registr živých bran — GENEROVANÝ `g3` (rozhodnutí 6. 10. 2026, §6.14).
# Do té doby to byl ruční soubor z 2. 10. s předpřesunovými cestami; dnes je to
# výstup běhu, takže se nemůže rozejít s tím, co se skutečně spouští.
REGISTR = ANALYZA / "_registr-bran.json"

# (popis, příkaz, co hledat ve výstupu jako "kolik otevřela")
#
# ⚠ CESTY V TOMHLE SEZNAMU JSOU ZÁZNAMNÍKY, NE LITERÁLY. `spust()` je před
# spuštěním nahradí odvozenými cestami (`<GODOT>`, `<TOOLS>`, `<FORGE>`,
# `<ANALYZA>`, `<HRA>`, `<STANICE>`) a **vypíše, kolik jich nahradil** — kdyby
# nějaký zůstal nenahrazený, je to vidět (`can't open file` s ostrými závorkami
# v cestě). Nahrazuje se i v parametrech, protože cesty jsou i tam
# (`<HRA>`, `<FORGE>/check-schema.py …`).
BRANY = [
    ("testy hry (Godot)", [str(GODOT), "--headless", "--path",
                           str(HRA),
                           "--script", "res://tests/run_tests.gd"],
     r"\[test\] (\d+) kontrol, (\d+) selhání"),
    # ⚠ P13c (4. 10. 2026): tady byly DVĚ brány `mutace A` a jedna
    # `C1: důkaz selhání` — všechny tři se OPÍRALY O JEDNORÁZOVÉ NÁSTROJE:
    #   * `a-mutace-run.py` potřebuje `a-oprav-test.py` (patch testu Úkolu A)
    #     a předpokládá, že `move()` v `player.gd` JEŠTĚ NENÍ. Dnes JE
    #     (`ffe9bd8` „smlouva move()"), takže nástroj správně hlásí
    #     „scratch není čistý ani po checkoutu" a skončí `exit 2`.
    #   * `c1-dukaz-selhani.py` mutuje `a3-kontrola.mjs` — nástroj kroku C1,
    #     který je od P8b v archivu a **nevrací se** (viz níž).
    # Ani jeden z nich **není opakovatelná brána**: měří jednorázovou opravu,
    # která je hotová. Nechat je v seznamu znamená mít v přehledu DVĚ „onemocnělé"
    # položky, které nikdy nezezelejí — a to je přesně tichá vada, kterou má
    # tenhle skript odhalovat. Jsou proto pojmenované v komentáři, ne v seznamu.
    #
    # CO ZŮSTÁVÁ: `mutace B (combat)` — ta je naopak OPAKOVATELNÁ: synchronizuje
    # si oba soubory z klonu a vrací vadu do `combat.gd` (nezávisí na jednorázovém
    # patchi testu). Naměřeno po opravě cest: `chyceno 2 z 2`.
    ("mutace B (combat)", ["python", "<ANALYZA>/b-mutace.py", "<ANALYZA>/a-ukol-scratch"],
     r"chyceno (\d+) z (\d+)"),
    # `C1: a3-kontrola` (node nad `a3-kontrola.mjs`) byl nahrazen ŽIVOU bránou
    # `a3-over.py` — tatáž podmínka, ale nad ZDROJEM conductoru, ne nad jedním
    # během. Nahrazení je záměrné a je vidět tady.
    ("C1: a3-over (náhrada za a3-kontrola.mjs)", ["python", "<ANALYZA>/a3-over.py"],
     r"ZM.\u0158ENO:\s*(\d+) kontrol"),
    ("C2: mutace N1 (5 běhů)", ["python", "<ANALYZA>/c2-mutace.py"], r"(\d+) kontrol, (\d+) chyb"),
    ("C2: sebekontrola diakritiky", ["python", "<ANALYZA>/g1-mutace-diakritika.py"],
     r"(\d+)× náhradní znak"),
    ("diakritika (brána)", ["python", "<TOOLS>/kontrola-diakritiky.py"],
     r"(\d+) znaků"),
    ("handoff úplnost", ["python", "<ANALYZA>/handoff-kontrola-uplnost.py"],
     r"kontrolovaných klíčů:\s+(\d+)"),
    # 2. 10. 2026 (12:5x): KRONIKA je nový TRVALÝ dokument. Brána kontroluje,
    # že počty omylů v ní odpovídají `HANDOFF.md` §8, že nálezy H1–H7 jsou
    # zmíněné tam, kde vznikly, a že odkazy na dokumenty existují.
    # ⚠ Mutační test je od 2. 10. 2026 (akční session) **`t3-kronika-mutace.py`**,
    # ne `h17-kronika-mutace.py`: ten starý testoval bránu **jen na ŽIVÉ kronice**
    # a ta neměla tvar, na kterém brána selhala (tabulka **nálezů** ve výřezu
    # bloku omylů) — vada proto **testem prošla** (nález **H16**). Nový test má
    # **fixturu s oběma tabulkami** a **6 případů**: 2 kontrolní (`exit 0`)
    # + 3 vady + kritérium tvaru.
    ("kronika úplnost", ["python", "<ANALYZA>/kronika-kontrola.py"],
     r"omylů celkem \(skutečnost\):\s+(\d+)"),
    # ⚠ PŘEPNUTO 2. 10. 2026 (akční session): dřív tu byl `h17-kronika-mutace.py`,
    # který testoval bránu **jen na ŽIVÉ kronice** — a ta neměla tvar, na kterém
    # brána selhala (tabulka **nálezů** ve výřezu bloku omylů). Vada proto
    # **testem prošla** (nález **H16**). Nový test má **fixturu s oběma tabulkami**
    # a **6 případů**: 2 kontrolní (`exit 0`) + 3 vady + kritérium tvaru.
    ("kronika mutace (6 případů)", ["python", "<ANALYZA>/t3-kronika-mutace.py"],
     r"PŘÍPADŮ CELKEM: (\d+)"),
    # ⚠ VZOR OPRAVEN 2. 10. 2026: `g1-diakritika-novych.py` **už nevede seznam**
    # (prochází složku), takže jeho výstup je `ZMĚŘENO: textových souborů=413, …`
    # a ne `VŠE OK — 127 souborů`. Starý vzor `(\d+) souborů` na novém výstupu
    # **nesedl** → brána vypsala `otevřela: —` (tedy „neměřila jsem nic"), ačkoli
    # kontrola proběhla. Je to táž past jako S27: **vzor, který usne.**
    ("diakritika nových souborů", ["python", "<ANALYZA>/g1-diakritika-novych.py"],
     r"textových souborů=(\d+)"),
    ("zadání kontrola", ["python", "<ANALYZA>/zadani-kontrola.py"], r"(\d+) řádků"),
    # ⚠ VZOR OPRAVEN 2. 10. 2026 (táž kontrola jako NA23): stálo tu holé
    # `r"(\d+)"` — „první číslo, které ve výstupu je". To **není čítač**;
    # naměřeno: `otevřela: 0`, protože první číslo výstupu byla nula z nějaké
    # statistické řádky. Brána sama přitom hlásí `Kontrol: 63, chyb: 0`.
    # (`overovani` §10.1 — ptej se, KTERÝ výskyt vzor trefí.)
    ("over-dokumentaci", ["python", "<TOOLS>/over-dokumentaci.py"],
     r"Kontrol:\s*(\d+)"),
    ("over-skilly", ["python", "<TOOLS>/over-skilly.py"], r"Skillů: (\d+)"),
    ("lint-roadmapa", ["python", "<TOOLS>/lint-roadmapa.py", "<HRA>"],
     r"(\d+) z (\d+)"),
    # ⚠ OPRAVENO 2. 10. 2026 (plánovací session, nález **H8**):
    # Tady dřív stálo `["node", "orchestra/tools/validate-all.mjs", "--jen", "hra"]`
    # — a to je VADA MĚŘIDLA: `validate-all.mjs` **nemá žádný přepínač `--jen`**
    # (naměřeno: `grep '--jen' validate-all.mjs` → **0 výskytů**) a **vůbec nečte
    # `process.argv`**. Příkaz tedy **spustil CELÝ validátor** a výsledek se
    # vypsal pod jménem „check-schema (hra)". Byla to **tatáž komanda jako
    # „validate-all (CELEK)" o dva řádky níž** — dva řádky přehledu měřily totéž
    # a ani jeden neměřil `check-schema`.
    # Správné volání (tak to dělá `validate-all.mjs:194`) je ten skript spustit
    # PŘÍMO nad klonem hry; `exit 0` = soulad, `1` = rozpory, `2` = chybí spec
    # (a `2` NENÍ úspěch — „nemám co měřit" se nesmí počítat jako zelená).
    ("check-schema (hra)", ["python", "<FORGE>/check-schema.py",
                            "<HRA>"],
     r"(Schéma je v souladu|schéma NENÍ v souladu|CHYBA[^\n]{0,40})"),
    ("test-cooldown", ["python", "<TOOLS>/test-cooldown.py"], r"(\d+) kontrol, (\d+) chyb"),
    ("f2 over cooldown", ["python", "<ANALYZA>/f2-over-cooldown.py"], r"(\d+) kontrol, (\d+) chyb"),
    # ⚠ OPRAVENO 2. 10. 2026 (po PUSHI obou repů, nález v §19 `HANDOFF.md`):
    # tady stálo `f3-over-deploy.mjs 7c11b2d` — tedy sha, který byl HEADem
    # **v době psaní** tohoto souboru. Po pushi se HEAD posunul na `1e3925e`,
    # nástroj dostal ten nový sha a **správně** odpověděl:
    #   „CHYBA deploy běžel na tomto commitu — na 1e3925e2c žádný deploy —
    #    push nezměnil conductor/**?"
    # To je **správné chování brány**, ne vada: `deploy.yml` má filtr
    # `paths: conductor/**` a commit `1e3925e` mění jen `tools/`.
    # **Kotva proto míří na poslední změnu `conductor/**`** (`7c11b2d` — B1),
    # protože na tom deploy #32 SKUTEČNĚ běžel. Kdyby se conductor změnil,
    # musí se změnit i ta konstanta — a to je vidět (`a3-kontrola.mjs` na to
    # upozorní sám: „poslední změna conductor/src/index.ts = …").
    ("deploy B1", ["node", "<ANALYZA>/f3-over-deploy.mjs", "7c11b2d"], r"(\d+) úloh"),
    ("ag-over-cisla", ["python", "<ANALYZA>/ag-over-cisla.py"], r"(\d+)"),
    # ⚠ PŘIDÁNO 2. 10. 2026 (Úkol 2 zadání `ZADANI-DOKONCENI-AUDITU.md`):
    # `ag-mutace.py` je JEDINÝ test, který dokazuje, že `ag-over-cisla.py` měří
    # DOKUMENT (a ne sám sebe — to byla vada N9). Do 2. 10. **v tomhle seznamu
    # NEBYL** (naměřeno: `grep 'ag-mutace' g3-brany.py` → **0 výskytů**),
    # a přesně proto jeho `exit 1` nikdo neviděl: skript hledal kotvu
    # `39 sloupců`, ta v `AGENTS.md` **není ani jednou**, obě mutace se tiše
    # neprovedly a test hlásil `2 problem`. Vada měřidla bez čtenáře.
    # ⚠ POZOR na vyklad: do P19 (6. 10. 2026) `g3-brany.py` **neměl `sys.exit`
    # VŮBEC** — byl to jen PŘEHLED. To je ale past „brána, která nemá jak
    # selhat“ (S27/H71/H87): kdyby g3 přestal měřit (rozbil by se klasifikátor,
    # zmizely by `BRANY`), **nikdo by to nepoznal**. Od P19 proto `exit` MÁ —
    # ale jen za to, co g3 SÁM TVRDÍ: že každá brána začala a řekla, kolik toho
    # otevřela (viz `OCEKAVANE_BEZ_CITACE` a `sys.exit` na konci souboru).
    # O ČERVENÝCH branách g3 NEROZHODUJE: které nenulové exity jsou správné,
    # dnes sepsané není (nález **NA23b**) a g3 to nepředstírá.
    ("ag-mutace (autorita)", ["python", "<ANALYZA>/ag-mutace.py"],
     r"mutací=(\d+), chyceno=(\d+)"),
    ("a1-a2-over", ["python", "<ANALYZA>/a1-a2-over.py"], r"Kontrol: (\d+)"),
    ("a3-over", ["python", "<ANALYZA>/a3-over.py"], r"(\d+)"),
    ("n8-zastarala", ["python", "<ANALYZA>/n8-zastarala-analyza.py"], r"(\d+) z (\d+)"),
    ("b5-over-tvrzeni", ["python", "<ANALYZA>/b5-over-tvrzeni.py"], r"(\d+)/(\d+)"),
    ("n1-over-inventar", ["python", "<ANALYZA>/n1-over-inventar.py"], r"(\d+)"),
    ("tsc (conductor)", ["node", "<WS>/conductor/node_modules/typescript/bin/tsc",
                         "--noEmit", "--project", "<WS>/conductor/tsconfig.json"],
     None),
    # ⚠ OPRAVENO 2. 10. 2026 (nález **NA23**, Úkol 2a) — DVAK RÁT, a ten druhý
    # je poučení:
    #
    # (1) Tady stálo `r"NALEZENO (\d+)|VŠE V PO"`. `validate-all.mjs` tiskne na
    #     KONCI `✗ NALEZENO 3 PROBLÉMŮ` (to je jeho souhrn), ale UPROSTŘED
    #     vypisuje výsledky jednotlivých bran — a v nich je `NALEZENO 15
    #     PROBLÉMŮ` (z `check-schema.py`). `re.search` bral **PRVNÍ** výskyt,
    #     takže sloupec `otevřela:` ukazoval **cizí číslo z vnořené brány**.
    #     Naměřeno: `otevřela: 3` (F5).
    #
    # (2) Zužil jsem vzor na `NALEZENO (\d+) PROBLÉM` + bral POSLEDNÍ výskyt —
    #     a vyskočilo **`otevřela: 3`** znovu. Jenže to pořád **NENÍ počet
    #     otevřených souborů**: je to **počet PROBLÉMŮ** („NALEZENO 3 PROBLÉMŮ").
    #     Predikát se spravil, **význam zůstal špatný** — a to je horší varianta
    #     než předtím, protože číslo teď vypadá věrohodně (`overovani` §10.1:
    #     „vzor něco našel" a „vzor našel to, co hledám" jsou dvě věty).
    #
    # **Správné řešení je `None`:** `validate-all` **nemá vlastní čítač
    # otevřených souborů** — je to AGGREGÁTOR a jeho děti si čítače vedou samy
    # (`VÝSLEDEK: 15 kontrol, 0 chyb` je čítač VNOŘENÉ brány, ne jeho).
    # Sloupec proto vypíše **`— (brána nemá čítač)`** — což je přesně to, co
    # zadání žádá u brány bez čítače: **nikdy prázdno ani cizí číslo**.
    ("validate-all (CELEK)", ["node", "<TOOLS>/validate-all.mjs"],
     None),
    # ⚠ PŘIDÁNO 4. 10. 2026 (P13c, nález H50): `tools/verify-setup.py` měl
    # pevnou cestu na STARÝ kořen, hlásil 6× CHYBI — a **nic ho nespouštělo**,
    # takže to nikdo neviděl. Byl přepsán na DNEŠNÍ strukturu (dva repy +
    # stanice) a je zařazen sem, aby ho příště vidět bylo. Sám si vede čítač
    # (`ZMĚŘENO: N kontrol, M chyb`), takže se dá číst sloupec `otevřela:`.
    ("verify-setup (struktura)", ["python", "<TOOLS>/verify-setup.py"],
     r"ZMĚŘENO:\s*(\d+) kontrol"),
    # ⚠ PŘIDÁNO 5. 10. 2026 (P13c-b, nálezy H57 + H68): `join()` volané bez
    # importu shodí modul **PŘED první kontrolou** — a v přehledu to vypadá jako
    # „brána našla vadu". Naměřeno: `tools/validate-all.mjs` a
    # `tools/test-ci-workflow.mjs` (obě brány); plošný sken pak **31 souborů**.
    ("chybějící importy (statická)", ["python", "<ANALYZA>/hl-chybejici-importy.py"],
     r"ZMĚŘENO:\s*(\d+) souborů"),
    # A rovnou i ta brána, kterou to odhalilo — do P13c-b v `g3` NEBYLA,
    # takže její `exit 1` nikdo neviděl (a byl to FALEŠNÝ POPLACH: hledala
    # `ci.yml` v `orchestra/uo-shadows`, což po přesunu neexistuje).
    ("CI workflow (šablona + hra)", ["node", "<TOOLS>/test-ci-workflow.mjs"],
     r"Testů OK:\s*(\d+)"),
    # ═══ PŘIDÁNO 5. 10. 2026 (AKČNÍ session P15, oprava nálezů H70–H79) ═══════
    # ⚠ ROZHODNUTÍ (Úkol F zadání): do `g3` jdou **jen měřidla, která měří
    # STAV nebo si stav sama vyrobí** (fixtura). Nepatří sem:
    #   * `p14a-g3-nezavisle.py` — čte `_analyza/g3-brany-vystup.txt`, což je
    #     během běhu `g3` **výstup PŘEDCHOZÍHO běhu** → `g3` by měřil sám sebe
    #     přes svůj minulý výstup (třída H60, „samoodkaz měřidla") a po každé
    #     změně `BRANY` by první běh hlásil falešnou červenou.
    #   * `test-h70-vetev.py` — **mutuje ŽIVÝ `_analyza/zadani-kontrola.py`**
    #     (a vrací ho). Je to táž třída jako `p14c-mutace-oprav.py`, který v tomhle
    #     seznamu taky není. Zůstává **dokladem** a pouští se ručně.
    ("escape sekvence (H79, statická)", ["python", "<ANALYZA>/h79-escape-sken.py"],
     r"ZMĚŘENO:\s*(\d+) neplatných"),
    ("escape sekvence (H79, mutace)", ["python", "<ANALYZA>/test-h79-escape.py"],
     r"VÝSLEDEK:\s*(\d+) kontrol, (\d+) chyb"),
    ("g3 klasifikátor nezačatých (H71)", ["python", "<ANALYZA>/test-h71-klasifikator.py"],
     r"VÝSLEDEK:\s*(\d+) kontrol, (\d+) chyb"),
    ("verify-setup seznam+čítač (H72/H73)", ["python", "<ANALYZA>/test-h72-h73.py"],
     r"VÝSLEDEK:\s*(\d+) kontrol, (\d+) chyb"),
    # ═══ PŘIDÁNO 5. 10. 2026 (AKČNÍ session P17, nález H85 / návrh NA32) ══════
    # ŠEST ŽIVÝCH `.py` NEŠLO ZKOMPILOVAT (`from __future__ import annotations`
    # až pod preludiem z P8b) — a žádná brána to neměřila. Soubor, který nejde
    # zkompilovat, se nespustí, takže jeho vady (i runtime) zůstávají neviditelné.
    # ⚠ Brána schválně používá `compile()`, ne `ast.parse()`: `ast.parse()`
    # špatně umístěný `from __future__` PŘIJME (naměřeno: 0 chyb vs. 6 chyb).
    # Čítač nese DVA údaje (soubory / nálezy) — jinak by se „zelená s 162
    # soubory" nedala odlišit od „červená, ale 162 souborů" ve sloupci `otevřela:`.
    ("kompilovatelnost živých .py (H85/NA32)",
     ["python", "<ANALYZA>/n32-kompilovatelnost.py"],
     r"ZMĚŘENO:\s*(\d+) souborů, (\d+) nekompilovatelných"),
    # A rovnou důkaz, že brána N32 má jak selhat (mutační test si vadu vyrobí
    # a VNÍTŘNÍM `finally` ji vrátí bajt na bajt). Bez něj by „0 nálezů"
    # neznamenalo nic — jen by to mohla být brána, která se nikdy nepodívala.
    ("kompilovatelnost — mutace (NA32)", ["python", "<ANALYZA>/test-n32-mutace.py"],
     r"VÝSLEDEK:\s*(\d+) kontrol, (\d+) chyb"),
    # A ještě důkaz pro H87 (návrh NA33): klasifikátor „nezačala" musí
    # rozhodovat podle CHOVÁNÍ, ne podle whitelistu 12 markerů. Fixtury jsou
    # doklady P16 (`p16a2-brana-bezmarkeru.py` a spol.); test je nemění.
    ("g3 klasifikátor podle chování (H87/NA33)",
     ["python", "<ANALYZA>/test-h87-klasifikator.py"],
     r"VÝSLEDEK:\s*(\d+) kontrol, (\d+) chyb"),
]

vse = []
radky_vypisu = []

# ⚠ `--soubor <cesta>` (P20): přepínač pro DOKLADY, které stavějí KOPII tohohle
# skriptu a čtou její VÝSTUP. Od P20 totiž `g3` **skončí nenulově i tehdy, když
# si jen dělá svou práci** (brána, která vůbec nezačala / běžela bez čítače /
# neočekávaný nenulový exit). Doklad, který si ověřuje KLASIFIKACI, tím dostane
# `exit 1` z legitimního důvodu — a nemůže rozlišit „harness promluvil správně“
# od „harness spadl“.
# ⚠ PROČ TO NENÍ „vypnutí brány“: přepínač NEMĚNÍ žádné rozhodnutí — jen
# **přesune návratový kód do jiné přihrádky** (do mezerou odděleného řádku
# `NAVRATOVY_KOD=<n>`), který si doklad přečte. Čtecí kód v CI ani v `g3` ho
# nepoužívá, takže se jím nedá nic obejít. Bez něj by se musel důkaz dělat
# HÁDÁNÍM, který z pěti důvodů nastal — a to je přesně chyba, kterou má
# `overovani` §10.1 zakázanou.
_POUZE_VYSTUP = "--soubor" in sys.argv

# Nahrazení záznamníků ODVOZENÝMI cestami. Kdyby se něco nenahradilo, je to
# vidět na `can't open file` s ostrými závorkami v cestě — a `nedosazene`
# to navíc pojmenuje ve souhrnu (aby to nebylo jen v plném výpisu).
ZNAMKY = {
    "<WS>": WS,
    "<HRA>": HRA,
    "<STANICE>": STANICE,
    "<ANALYZA>": ANALYZA,
    "<TOOLS>": TOOLS,
    "<FORGE>": FORGE,
    "<GODOT>": GODOT,
}
nedosazene = []
# BRÁNY, KTERÉ VŮBEC NEZAČALY (P13c): interpret ohlásil, že soubor nemá.
# Do opravy cest se to poznalo podle `can't open file` — jenže to je text
# KONKRÉTNÍHO interpretu a po dosazení PLNÉ cesty se změnil. Měří se proto to,
# co mají všechny tři případy společné (`python`, `node`, shell): **chybějící soubor**.
neotevrene = []
# TŘETÍ STAV (H87): brány, které BĚŽELY (promluvily), ale nevykázaly ČÍTAČ.
# Do opravy se tenhle stav sléval s „nezačala" — a právě proto fixtura bez
# markeru vypadala jako brána, která vůbec neběžela.
bez_citace = []


# ── KLASIFIKÁTOR „BRÁNA VŮBEC NEZAČALA" (P13c; OPRAVENO 5. 10. 2026 — H71) ───
# ⚠ NÁLEZ H71 (P14, 5. 10. 2026): do téhle opravy se „nezačala" poznalo podle
# TROJICE — `exit=2` + žádný čítač + **výstup < 500 B**. To je **měření DÉLKY,
# ne obsahu**, a naměřeno na `C2: mutace N1`: brána **proběhla**, **řekla to**
# („→ brána neprojde ani ve zdravém stavu; končím") a měla **476 B** → byla
# vykázána jako „BRÁNY, KTERÉ VŮBEC NEZAČALY (1)". Byl to **falešný nález
# o funkční bráně** — a to je horší než slepé místo (`overovani` §10.1).
#
# Rozhoduje se proto podle OBSAHU:
#   * brána, která vypíše **VLASTNÍ hlášení**, **běžela** (i s `exit=2`),
#   * „neběželo" je `exit=2` s **prázdným** výstupem, s **podpisem chybějícího
#     souboru** od interpretu, nebo s **jednořádkovým** výstupem bez hlášení.
# Markery jsou záměrně **krátké a konkrétní** — obecné („Error", „chyba")
# by spolkly i `can't open file`, a tím by klasifikátor osleply.
# ⚠ NÁLEZ H87 (P16, 5. 10. 2026; OPRAVENO P17): do téhle opravy se „běžela"
# poznalo podle **whitelistu 12 markerů** (`_VLASTNI_HLASENI`). Brána, která
# skončila `exit=2` s KRÁTKÝM VLASTNÍM HLÁŠENÍM bez markeru (fixtura
# `p16a2-brana-bezmarkeru.py`: `print('P16: hotovo, vse na svem miste')`),
# propadla na `len(_radky) <= 1` a vykázala se jako **„VŮBEC NEZAČALA"** —
# tedy FALEŠNÝ NÁLEZ O FUNKČNÍ BRÁNĚ. Táž třída jako H71.
#
# **Pravidlo (B2): rozhoduje CHOVÁNÍ, ne seznam slov.** Whitelist je pryč;
# „nezačala" znamená jen to, co se skutečně stalo:
#   * **výstup je PRÁZDNÝ** → interpret neřekl nic (nic neběželo),
#   * **výstup nese podpis chybějícího souboru** → interpret řekl, že soubor nemá.
# Cokoli jiného znamená, že brána **promluvila sama za sebe** → BĚŽELA.
# (Past `overovani` §7.13: „neproběhlo" je TŘETÍ stav vedle zelené a červené.)
# Slova jako „CHYBA" nebo „končím" v seznamu být NESMÍ — spolkla by i cizí
# nástroje a **falešný nález o funkční bráně je dražší než slepé místo**.
# ⚠ NÁLEZ H94 (P18) — PŘEMĚŘENO A ROZHODNUTO P19 (6. 10. 2026): ze **8 podpisů**
# mohou v TOMHLE klasifikátoru zabrat **čtyři**. Mrtvé položky jsou ODEBRANÉ
# (mrtvý podpis vypadá jako pokrytí a nechytá nic) a jsou tu POJMENOVANÉ
# s důvodem — kdyby se změnilo, co `g3` spouští, patří zpátky:
#
#   ŽIVÉ (naměřeno spuštěním interpretů nad NEEXISTUJÍCÍ cestou):
#     * `can't open file`           — Python; TÝŽ případ jako `No such file…`
#     * `No such file or directory` — Python; oba jsou v JEDNOM výstupu, takže
#       odebrat JEN JEDEN z nich nic nezmění (naměřeno mutací M2 i M3)
#     * `Cannot find module`        — Node
#     * `MODULE_NOT_FOUND`          — Node; týž případ jako `Cannot find module`
#   MRTVÉ PRO `g3` (a proč):
#     * `no such file or directory` (malá písmena) — žádný interpret na této
#       stanici tenhle text nevydá (Python píše `No such file or directory`)
#     * `WinError 2` — je to text VÝJIMKY, kterou `spust()` chytá zvlášť;
#       do zachyceného výstupu se nikdy nedostane
#     * `The system cannot find the file` — text shellu Windows; `g3` shell
#       NEPOUŽÍVÁ (`subprocess.run` se seznamem argumentů, žádné `shell=True`)
#     * `is not recognized` — text PowerShellu/cmd; `g3` shell nepoužívá.
#       ⚠ POZOR, měřeno: PowerShell i cmd tenhle text SKUTEČNĚ vydávají —
#       mrtvý je jen PRO TENHLE KLASIFIKÁTOR, ne obecně. Kdyby do `BRANY`
#       někdy přibyl `.cmd`/`.ps1` brána, patří sem zpátky i tenhle podpis.
#
# Měření (dá se zopakovat): `python _analyza/p19-c-h94-podpisy.py`
#   → vypíše, který podpis se v kterém výstupu objevuje, a mutacemi ověří,
#     že seznam je nosný (odebrání všech živých změní klasifikaci fixtury D).
# Kdyby se text interpretu změnil, pozná to `test-h87-klasifikator.py`
# (fixtura `neexistuje`) — ten je v `g3`, proto je zúžení bezpečné.
_PODPIS_CHYBEJICIHO_SOUBORU = (
    "can't open file", "Cannot find module", "MODULE_NOT_FOUND",
    "No such file or directory",
)


def je_neotevrena(exit_kod: int, nalezeno: str, vystup: str) -> bool:
    """TŘETÍ STAV vedle zelené a červené (`overovani` §7.13): brána nezačala.

    Rozhoduje **CHOVÁNÍ interpretu**, ne délka výstupu a ne seznam markerů
    (H71 + H87). Volá se z `spust()` a je mutačně ověřená testy
    `_analyza/test-h71-klasifikator.py` a `_analyza/test-h87-klasifikator.py`
    (oba berou tenhle soubor jako ZDROJ a mění jen `BRANY`, takže se živý
    soubor nemutuje).
    """
    if exit_kod != 2 or not nalezeno.startswith("—"):
        return False
    text = vystup.strip()
    if not text:
        return True                       # prázdný výstup = interpret neřekl nic
    return any(z in text for z in _PODPIS_CHYBEJICIHO_SOUBORU)


def dosad(prikaz: list) -> list:
    """Nahradí záznamníky (`<TOOLS>`, `<HRA>`…) odvozenými cestami."""
    out = []
    for cast in prikaz:
        if isinstance(cast, str):
            for znacka, cesta in ZNAMKY.items():
                if znacka in cast:
                    cast = cast.replace(znacka, str(cesta).replace("\\", "/"))
        if isinstance(cast, str) and "<" in cast and ">" in cast:
            nedosazene.append(cast)
        out.append(cast)
    return out


def spust(popis: str, prikaz: list, vzor) -> None:
    prikaz = dosad(prikaz)
    env = None
    if "godot" in prikaz[0].lower():
        env = dict(os.environ)
        env["APPDATA"] = str(USER_DIR)
        USER_DIR.mkdir(parents=True, exist_ok=True)
    # Pracovní strom pro mutace potřebuje:
    #   * import cache (`.godot/` je v `.gitignore`, do worktree se nezkopíruje)
    #     — bez ní dá 57/3 místo 59/0 a vypadá to jako regrese kódu
    #     (`dsh-prostredi` §4c),
    #   * AKTUÁLNÍ kód z klonu (jinak mutace měří starou verzi a spadne na
    #     „hledaný text v combat.gd není" — což vypadá jako vada mutace).
    scratch = ANALYZA / "a-ukol-scratch"
    if "a-ukol-scratch" in " ".join(prikaz) and scratch.is_dir():
        import shutil
        zdroj_godot = HRA / ".godot"
        if zdroj_godot.is_dir() and not (scratch / ".godot").is_dir():
            shutil.copytree(zdroj_godot, scratch / ".godot")
        for rel in ("scripts/combat.gd", "tests/run_tests.gd"):
            z = HRA / rel
            c = scratch / rel
            if z.is_file() and c.parent.is_dir():
                shutil.copyfile(z, c)
    try:
        r = subprocess.run(prikaz, cwd=str(WS), capture_output=True, env=env, timeout=1800)
    except Exception as e:                                  # noqa: BLE001
        print("  CHYBA %-28s nepodařilo se spustit: %s" % (popis, e))
        vse.append((popis, None, str(e)))
        return
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    radky_vypisu.append("=" * 78)
    radky_vypisu.append("### %s   (exit=%d)" % (popis, r.returncode))
    radky_vypisu.append("=" * 78)
    radky_vypisu.append(v)
    # ⚠ `—` MUSÍ BÝT VIDĚT (nález NA23, Úkol 2a): dřív tu bylo prázdné pole
    # a čtenář nerozeznal „brána nemá čítač" od „brána se nespustila".
    # Nikdy se nevypisuje prázdno ani cizí číslo.
    nalezeno = "—"
    if vzor:
        # ⚠ OD 2. 10. 2026 SE BERE **POSLEDNÍ** VÝSKYT, NE PRVNÍ (nález NA23).
        # Naměřeno: `validate-all (CELEK)` má uvnitř výpisy jednotlivých bran
        # a v nich `NALEZENO 15 PROBLÉMŮ`; jeho VLASTNÍ souhrn je na konci
        # (`✗ NALEZENO 3 PROBLÉMŮ`). `re.search` vzal první z nich → sloupec
        # `otevřela:` ukazoval **cizí číslo z vnořené brány**.
        # Souhrn je vždycky **poslední** — proto `finditer` a poslední shoda.
        # (`overovani` §10.1: ptej se, KTERÝ výskyt vzor trefí.)
        posledni = None
        for posledni in re.finditer(vzor, v):
            pass
        if posledni:
            skupiny = [g for g in posledni.groups() if g]
            if skupiny:
                nalezeno = " / ".join(skupiny)
    stav = "OK  " if r.returncode == 0 else "exit=%d" % r.returncode
    if not vzor:
        # Brána bez čítače: přiznat to, ne nechat prázdno.
        nalezeno = "— (brána nemá čítač)"
    # ⚠ SIGNÁL „BRÁNA VŮBEC NEZAČALA“ (P13c, 4. 10. 2026; PŘEPSÁN 5. 10. 2026, H71).
    #
    # První verze tohohle detektoru hledala v textu `can't open file` — a to
    # byla CHYBA, kterou odhalil až mutační test: **ten text se v zachyceném
    # výstupu vůbec neobjevil.** PowerShell spouštěl neexistující cestu a spadl
    # sám (`WinError 2`), takže v `capture_output` nebylo NIC z toho, co jsem
    # hledal. Signál se proto bral z **výsledku** — a to ze TŘÍ věcí současně:
    # `exit=2` + žádný čítač + **skoro prázdný výstup**.
    #   * `exit=2` + `—` + krátký výstup  = nespustilo se nic,
    #   * `exit=2` + `—` + DLOUHÝ výstup  = brána PROBĚHLA a sama hlásí chybu,
    #   * `exit=2` + NENULOVÝ čítač       = brána proběhla (např. `check-schema`
    #     vrací 2, když hra nemá `spec.json` — a to JE měření).
    #
    # ⚠ ALE „krátký výstup" NENÍ totéž co „neběželo" (H71, naměřeno: 476 B).
    # Rozhoduje proto `je_neotevrena()` podle OBSAHU — délka z toho vypadla.
    # (Past `overovani` §7.13: „neproběhlo" je TŘETÍ stav vedle zelené a červené.)
    if je_neotevrena(r.returncode, nalezeno, v):
        neotevrene.append((popis, "exit=2, žádný čítač a " + (
            "PRÁZDNÝ výstup" if not v.strip() else "podpis chybějícího souboru")))
    elif nalezeno == "—":
        # TŘETÍ STAV (H87): brána BĚŽELA a promluvila, ale nevykázala ČÍTAČ.
        bez_citace.append((popis, r.returncode,
                           "běžela, ale vzor nic nenašel (%d B)" % len(v)))
    print("  %-8s %-28s otevřela: %s" % (stav, popis, nalezeno))
    vse.append((popis, r.returncode, nalezeno, je_neotevrena(r.returncode,
                                                             nalezeno, v)))


print("=" * 78)
print("VŠECHNY BRÁNY — a co která otevřela")
print("=" * 78)
print("  (cesty se odvozují z umístění skriptu: WS=%s, HRA=%s)" % (WS, HRA))
print("  (Godot: %s)" % GODOT)
if not GODOT.is_file():
    print("  ⚠ GODOT NEEXISTUJE na %s — brány hry poběží jako „neproběhlo (prostředí)“" % GODOT)
print()
for popis, prikaz, vzor in BRANY:
    spust(popis, prikaz, vzor)

VYSTUP.write_bytes(("\n".join(radky_vypisu)).encode("utf-8"))
print()
print("plný výstup: %s (%d znaků)" % (VYSTUP.name, VYSTUP.stat().st_size))

selhalo = [(p, k) for p, k, _, _ in vse if k not in (0,)]
print()
print("brán celkem: %d, s nenulovým exit: %d" % (len(vse), len(selhalo)))
for p, k in selhalo:
    print("   CHYBA %s → exit=%s" % (p, k))

# ── DVĚ VĚCI, KTERÉ SE MUSÍ VYPISOVAT, JINAK SE TICHE ZTRATÍ ─────────────────
# 1) NEDOSAZENÉ ZÁZNAMNÍKY: cesta, ve které zůstala ostrá závorka, neexistuje.
#    Přesně tak vypadala vada H48 (15 bran „běželo“ na `orchestra/tools/...`).
if nedosazene:
    print()
    print("⚠ NEDOSAZENÉ CESTY (%d) — tyhle brány vůbec neběžely:" % len(nedosazene))
    for c in nedosazene:
        print("   %s" % c)
else:
    print("záznamníky cest: všechny dosazené (0 nedosazených)")

# ⚠ TOHLE JE HLAVNÍ VÝSTUP CELÉ OPRAVY (P13c): brána, jejíž soubor neexistuje,
# **není červená — je NEZMĚŘENÁ** (`overovani` §7.13). Do 4. 10. 2026 jich
# takových bylo 15 a v přehledu vypadaly jako „červená".
if neotevrene:
    print()
    print("⚠ BRÁNY, KTERÉ VŮBEC NEZAČALY (%d) — jejich `exit` NENÍ výsledek:"
          % len(neotevrene))
    for p, duvod in neotevrene:
        print("   %s  (%s)" % (p, duvod))
else:
    print("brány, které vůbec nezačaly: 0   (každá otevřela svůj soubor)")

# 2) BRÁNY, KTERÉ DOBĚHLY, ALE NEVYKÁZALY ČÍTAČ. To je past S27:
#    „zelená bez počtu kontrol je ticho, ne zelená".
# ⚠ H87: sem patří JEN brány, které PROKAZATELNĚ BĚŽELY (nejsou v `neotevrene`)
#    — do opravy tu byl každý `v == "—"` a stav „běžela, ale nic nezměřila" se
#    sléval se stavem „vůbec nezačala".
if bez_citace:
    print()
    print("? BRÁNY, KTERÉ BĚŽELY, ALE NEVYKÁZALY ČÍTAČ (%d) — nevíme, CO změřily:"
          % len(bez_citace))
    for p, k, d in bez_citace:
        print("   %s → exit=%s, %s" % (p, k, d))

# ── ROZHODNUTÍ P19 (Úkol D / nález NA23b): `g3` SMÍ SPADNOUT — ALE JEN ZA SEBE ─
# `g3` tvrdí jednu věc: **každá brána začala a řekla, kolik toho otevřela**.
# Když to neplatí, je to vada MĚŘENÍ (ne výsledek brány), a proto `exit != 0`.
# O červených branách do P20 nerozhodoval — seznam „očekávaně nenulových exitů“
# neexistoval (nález NA23b). ⚠ OD P20 SE ROZHODUJE: viz `OCEKAVANE_NENULOVE` níž.
#
# `OCEKAVANE_BEZ_CITACE` je deklarovaný výjimečný stav: brána, o které VÍME, že
# čítač nemá (a víme proč). Nová taková brána = `exit 1`, dokud se nerozhodne.
# ⚠ Záznam, který už není potřeba, se VYPÍŠE jako „už není potřeba“ — zastaralý
# baseline by jinak tiše krýval novou bránu se stejným jménem.
OCEKAVANE_BEZ_CITACE = {"C2: mutace N1 (5 běhů)"}

# ══ ROZHODNUTÍ P20 (Úkol A) — `g3` NYNÍ SOUDÍ I ČERVENÉ (NA23b VYŘEŠEN) ═══════
# Do P20 `g3` o červených **nerozhodoval** — chyběl mu seznam „které nenulové
# exity jsou správné“ (nález **NA23b**). Tím byla půlka jeho práce slepá:
# brána, která přestane platit, se v přehledu **objevila** — ale `g3` kvůli ní
# nespadl, takže `exit 0` vypadal stejně pro „všechno je v pořádku“ i pro
# „jedna brána tiše odešla“.
#
# `OCEKAVANE_NENULOVE` ten seznam JE. Formát je **`{jméno brány: očekávaný exit}`**
# a ten KÓD tam patří proto, že se to naměřilo (`_analyza/p20-a-kody-bran.py`):
# **`zadání kontrola` umí `0` i `1`** — `0`, když je zadání kotvené na živý
# `HEAD`, `1`, když je zastaralé (což je jeho SPRÁVNÁ práce, nález **NA31**).
# Kdyby deklarace nesla jen jméno, `g3` by nerozlišil „tatáž brána, jiný důvod“.
#
# Tři stavy, které z toho plynou (a každý se VYPISUJE — žádný není ticho):
#   * `exit` = deklarovaný    → brána je tam, kde má být, `g3` to neposuzuje dál;
#   * `exit` ≠ deklarovaný    → **`exit 1`**: je to NEOČEKÁVANÝ nenulový exit.
#   * deklarováno, ale `0`    → **poznámka, ne pád.** Pravidlo projektu je,
#     že se zadání **neopravuje na dnešek** (§37.5), takže se `zadání kontrola`
#     legitimně PŘEPÍNÁ mezi `0` a `1` podle toho, kde je `HEAD` — a `g3`
#     nesmí spadnout za to, že předpoklad mezitím pominul. Na rozdíl od
#     `OCEKAVANE_BEZ_CITACE` tu ale platí, že záznam, který **zmizí z `BRANY`**,
#     je VISUTÝ (deklarace o bráně, která už není) → **`exit 1`**.
OCEKAVANE_NENULOVE = {"zadání kontrola": 1}

print()
print("─" * 78)
# ── VERDIKT NAD ČERVENÝMI (P20): deklarované projdou, nedeklarované shodí g3 ──
# ⚠ OMyl P20/6 (naměřený `p19-d-kontroly.py`, případ 4): `selhalo` je KAŽDÝ
# nenulový exit — takže sem spadne i brána, která je DEKLAROVANÁ jako
# „běžela bez čítače“ (`OCEKAVANE_BEZ_CITACE`, dnes `C2: mutace N1`), a taky
# brána, která VŮBEC NEZAČALA. Ani jedna z nich není „neočekávaný nenulový
# exit“ — první je přiznaný stav a druhá je vada MĚŘENÍ, která se hlásí svou
# vlastní sekcí. Bez tohohle odečtení by `g3` padal za to, co sám deklaroval.
_pokryte_jinde = ({p for p, _, _ in bez_citace}
                  | {p for p, _ in neotevrene})
nazvy_bran = {p for p, _, _, _ in vse}
_exity = {q: k for q, k in selhalo}
nove_cervene = sorted((p, k) for p, k in selhalo
                      if OCEKAVANE_NENULOVE.get(p) != k
                      and p not in _pokryte_jinde)
cekane_cervene = sorted((p, k) for p, k in selhalo
                        if OCEKAVANE_NENULOVE.get(p) == k)
# Deklarace, kterou `BRANY` vůbec neobsahují = visutý záznam (deklarace o bráně,
# která už není). Na rozdíl od „už není potřeba“ tudy vede cesta k tichému krytí:
# kdyby brána z `BRANY` zmizela a jiná dostala stejné jméno, záznam by ji kryl.
visute = sorted(set(OCEKAVANE_NENULOVE) - nazvy_bran)
# Deklarace, která dnes platí, ale `exit` je 0 → předpoklad pominul (NENÍ vada:
# zadání se na dnešek záměrně neopravuje, §37.5).
uz_neni_nenulova = sorted(p for p in OCEKAVANE_NENULOVE
                          if p in nazvy_bran and _exity.get(p) is None)

if selhalo:
    print("NENULOVÉ EXITY: %d — z toho deklarovaných (očekávaných) %d "
          "a NEDEKLAROVANÝCH %d:" % (len(selhalo), len(cekane_cervene),
                                     len(nove_cervene)))
    for p, k in cekane_cervene:
        print("   očekávaný:   %s → exit=%s" % (p, k))
    for p, k in nove_cervene:
        print("   NEOČEKÁVANÝ: %s → exit=%s" % (p, k))
else:
    print("NENULOVÉ EXITY: 0 — každá brána doběhla s exit 0")
if uz_neni_nenulova:
    print("   (poznámka: v `OCEKAVANE_NENULOVE` už není potřeba: %s — "
          "brána dnes končí nulou; TO NENÍ VADA, zadání se na dnešek "
          "neopravuje)" % ", ".join(uz_neni_nenulova))
if visute:
    print("   ⚠ VISUTÉ záznamy v `OCEKAVANE_NENULOVE` (brána v `BRANY` není): %s"
          % ", ".join(visute))

nove_bez_citace = sorted(p for p, _, _ in bez_citace
                         if p not in OCEKAVANE_BEZ_CITACE)
uz_neni_potreba = sorted(OCEKAVANE_BEZ_CITACE
                         - {p for p, _, _ in bez_citace})
print("BRÁNY BEZ ČÍTAČE mimo deklarovaný stav: %d%s"
      % (len(nove_bez_citace), (" → " + ", ".join(nove_bez_citace))
         if nove_bez_citace else ""))
if uz_neni_potreba:
    print("   (poznámka: v `OCEKAVANE_BEZ_CITACE` už není potřeba: %s — "
          "brána teď čítač vykazuje)" % ", ".join(uz_neni_potreba))

kod = 0
if not vse:
    print("CHYBA: neproběhla ANI JEDNA brána — to není zelená, to je neměření.")
    kod = 2
elif neotevrene or nove_bez_citace:
    kod = 1
elif nove_cervene or visute:
    # ⚠ P20: tohle je ta polovina, která do P20 chyběla (NA23b). Nenulový exit
    # MIMO deklaraci znamená, že brána přestala platit (nebo se rozbila) —
    # a `g3` to musí říct nahlas, ne jen vypsat řádek do přehledu.
    kod = 1
print("VÝSLEDEK g3: %s" % {0: "PŘEHLED JE ÚPLNÝ (každá brána začala a vykázala, "
                              "co otevřela; žádný NEOČEKÁVANÝ nenulový exit)",
                           1: "NĚCO SE NEMĚŘILO NEBO SE ROZEŠLO S DEKLARACÍ — "
                              "viz výše (vady MĚŘENÍ a neočekávané exity, ne "
                              "výsledky bran)",
                           2: "NEMĚŘILO SE VŮBEC"}[kod])
# ══ REGISTR ŽIVÝCH BRAN — JEDNA AUTORITA (rozhodnutí 6. 10. 2026, §6.14) ══════
# PROČ: do 6. 10. 2026 existovaly **tři seznamy živých** a ANI JEDEN se neshodoval
# s během: `_analyza\_registr-bran.json` (ruční, `"kdy": "2026-10-02 22:06"`,
# s PŘEDPŘESUNOVOU cestou `C:\Users\Ssevc\Local-Deepseek\orchestra`), ruční výčet
# v `HANDOFF.md` §6 a devět nástrojů v `AGENTS.md`, z nichž tři nikde neběžely.
# Skutečná autorita (`BRANY` tady + `spust()` ve `validate-all.mjs` + `VZOR`
# v `p20-d`) nebyla v `AGENTS.md` **jmenovaná vůbec**.
#
# Náprava: `g3` — který brány **skutečně spouští** — zapíše seznam, jaký NAMĚŘIL.
# Registr tím přestává být tvrzení a stává se **výstupem běhu**; kdo ho chce
# aktualizovat, **pustí `g3`** (ne že ho přepíše rukou).
#
# ⚠ PÍŠE SE JEN V PLNÉM BĚHU. `_POUZE_VYSTUP` (řádek 321, `--soubor`) je režim,
# ve kterém `g3` jen **vypíše, co naměřil** a sám skončí `exit 0` — používají ho
# doklady a mutační testy, které si `BRANY` ve svém harnessu MĚNÍ. Kdyby registr
# zapsaly ony, uložil by se **zmrzačený seznam z mutace** (a příští session by
# se podle něj řídila). Proto: plný běh → zapiš; `--soubor` → nezapisuj.
if not _POUZE_VYSTUP:
    import json as _json
    import time as _time
    _registr = {
        "co_to_je": ("REGISTR ŽIVÝCH BRAN — GENEROVANÝ, needituj rukou. "
                     "Zdroj: `python _analyza/g3-brany.py` (plný běh). "
                     "Autorita je `BRANY` v `g3-brany.py` + `spust()` ve "
                     "`tools/validate-all.mjs` + `VZOR` v `p20-d-doklady.py`."),
        "kdy": _time.strftime("%Y-%m-%d %H:%M:%S"),
        "bran_celkem": len(vse),
        "s_nenulovym_exit": sorted(p for p, k, _, _ in vse if k not in (0,)),
        "ocekavane_nenulove": OCEKAVANE_NENULOVE,
        "bez_citace": sorted(p for p, _, _ in bez_citace),
        "neotevrene": sorted(p for p, _ in neotevrene),
        "brany": [],
    }
    _podle_jmena = {p: (k, n) for p, k, n, _v in vse}
    for _p, _prikaz, _vzor in BRANY:
        _k, _n = _podle_jmena.get(_p, (None, None))
        # ⚠ `dosad()` bere SEZNAM a vrací SEZNAM — první verze tu psala
        # `" ".join(dosad(pri) for pri in _prikaz)` a spadla na
        # `TypeError: sequence item 0: expected str instance, list found`
        # (`_prikaz` je seznam, ne řetězec). **A ta chyba byla TICHÁ:** `g3`
        # mezitím vypsal celý přehled i verdikt, `sys.exit(kod)` se ale
        # neprovedl a proces spadl s `exit 1` — což je NEROZEZNATELNÉ od
        # „deklarovaný nenulový exit". Registr se proto nezapsal a nikdo to
        # neviděl; odhalilo to až **měření obsahu souboru**, ne `exit` kódu.
        _prikaz_s = " ".join(dosad(_prikaz))
        _registr["brany"].append({
            "nazev": _p,
            "exit": _k,
            "otevrela": _n,
            "ma_citac": _p not in {x for x, _, _ in bez_citace},
            "prikaz": _prikaz_s,
        })
    REGISTR.write_bytes((_json.dumps(_registr, ensure_ascii=False, indent=2) + "\n")
                        .encode("utf-8"))
    print("registr zapsán: %s (%d bran, %d B)"
          % (REGISTR.name, _registr["bran_celkem"], REGISTR.stat().st_size))

# Viz komentář u `_POUZE_VYSTUP`: doklad si návratový kód přečte odsud a sám
# zůstane `exit 0` (jinak by nemohl rozlišit „správně promluvil“ od „spadl“).
if _POUZE_VYSTUP:
    print("NAVRATOVY_KOD=%d" % kod)
    sys.exit(0)
sys.exit(kod)
