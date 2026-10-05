# -*- coding: utf-8 -*-
"""Spustí VŠECHNY brány a u každé vypíše, KOLIK toho otevřela (past S27).

PROČ: `AGENTS.md` — „u každé brány se ptej, PROBĚHLA, ne jen neprotestovala".
`exit 0` bez počtu kontrol je ticho, ne zelená. Tenhle skript proto u každé
brány hledá ve výstupu **počet kontrol / souborů / granulí** a ten vypíše.

Píše se i do souboru `_analyza/g3-brany-vystup.txt`, aby se dal zápis ověřit
bez opakovaného běhu.

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
HRA = WS.parent / "uo-shadows"
STANICE = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
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
    # ⚠ POZOR na vyklad: `g3-brany.py` sám **nemá `sys.exit`** — je to
    # PŘEHLED, ne brána (a dobře tak: dva jeho řádky končí nenulově SPRÁVNĚ).
    # Viditelnost tady dělá sloupec `exit=` a `otevřela:`, ne návratový kód.
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
]

vse = []
radky_vypisu = []

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


def _radky(vystup: str) -> list[str]:
    return [l for l in vystup.splitlines() if l.strip()]


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
_VLASTNI_HLASENI = (
    "končím", "koncim", "končí", "očekáváno", "ocekavano", "CHYBA", "chyba:",
    "VÝSLEDEK", "VYSLEDEK", "ZMĚŘENO", "ZMERENO", "NELZE", "nelze",
)
_PODPIS_CHYBEJICIHO_SOUBORU = (
    "can't open file", "Cannot find module", "MODULE_NOT_FOUND",
    "No such file or directory", "no such file or directory",
    "WinError 2", "The system cannot find the file", "is not recognized",
)


def je_neotevrena(exit_kod: int, nalezeno: str, vystup: str) -> bool:
    """TŘETÍ STAV vedle zelené a červené (`overovani` §7.13): brána nezačala.

    Rozhoduje **OBSAH**, ne délka výstupu (H71). Volá se z `spust()` a je
    mutačně ověřená testem `_analyza/test-h71-klasifikator.py` (ten bere tenhle
    soubor jako ZDROJ a mění jen `BRANY`, takže se nemutuje živý soubor).
    """
    if exit_kod != 2 or not nalezeno.startswith("—"):
        return False
    text = vystup.strip()
    if not text:
        return True                       # prázdný výstup = nic neběželo
    if any(z in text for z in _VLASTNI_HLASENI):
        return False                      # brána mluvila sama za sebe → běžela
    if any(z in text for z in _PODPIS_CHYBEJICIHO_SOUBORU):
        return True                       # interpret hlásí chybějící soubor
    return len(_radky(text)) <= 1          # jednořádkový výstup bez hlášení


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
        neotevrene.append((popis, "exit=2, žádný čítač a výstup bez vlastního "
                                  "hlášení (%d B)" % len(v)))
    print("  %-8s %-28s otevřela: %s" % (stav, popis, nalezeno))
    vse.append((popis, r.returncode, nalezeno))


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

selhalo = [(p, k) for p, k, _ in vse if k not in (0,)]
neotevrelo = [(p, k, v) for p, k, v in vse if k is not None and v == "—"]
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

# 2) BRÁNY, KTERÉ DOBĚHLY S `exit 0`, ALE NEVYKÁZALY ČÍTAČ. To je past S27:
#    „zelená bez počtu kontrol je ticho, ne zelená“.
if neotevrelo:
    print()
    # ⚠ H80 (5. 10. 2026, naměřeno v běhu P15): tady stálo „PROŠLY, ale nevíme,
    # CO změřily" — a v seznamu byl i `C2: mutace N1` s **`exit=2`**. To je táž
    # třída jako H71: **sdělení o bráně tvrdilo něco, co neplatilo**. Vypisuje se
    # proto **exit kód** a nadpis už netvrdí „prošly".
    print("? BRÁNY BEZ ČÍTAČE (%d) — nevykázaly POČET, takže nevíme, CO změřily:"
          % len(neotevrelo))
    for p, k, v in neotevrelo:
        print("   %s → exit=%s, otevřela: %s" % (p, k, v))
