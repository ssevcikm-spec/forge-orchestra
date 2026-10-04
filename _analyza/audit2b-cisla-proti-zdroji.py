# -*- coding: utf-8 -*-
"""AUDIT 2b — ČÍSLO PROTI ZDROJI (fáze 2, druhý a třetí druh kontroly).

PROČ TENHLE SKRIPT A NE `audit2-rozpory.py`:
  `audit2-rozpory.py` hledá „táž veličina, různé hodnoty" POUHÝM VZOREM
  a vyjde mu 15 „rozporů" — z toho téměř všechny falešné, protože **různé
  brány hlásí různé počty kontrol správně** (měří různé věci). Je to tatáž
  past, na kterou upozorňuje `overovani` §8.3: „počet oddělovačů v řádku není
  identifikátor řádku" — ptát se na TVAR, ne na VÝZNAM.

  Tady se proto u každé veličiny **změří ŽIVÝ ZDROJ** (soubor, běh brány)
  a teprve s ním se porovnávají tvrzení z dokumentů. Rozpor je jen tam, kde
  se tvrzení liší od ZDROJE — ne tam, kde se liší dvě tvrzení o různých věcech.

CO SE MĚŘÍ (zdroj → co je autorita):
  skillů             ~/.dsh/skills/*/SKILL.md            (souborový systém)
  bran               počet bran v `g3-brany.py`          (živý seznam)
  klíčových bodů     `handoff-kontrola-uplnost.py`       (běh brány)
  omylů              `kronika-kontrola.py`               (běh brány)
  sloupců            `conductor/schema.sql`              (bez komentářů)
  tabulek            `conductor/schema.sql`
  dokumentů v kořeni `*.md` v kořeni workspace           (souborový systém)
  granulí            `games/uo-shadows/.forge/roadmap.json`
  kontrol (testy)    běh Godotu nad hrou

Použití:  python _analyza/audit2b-cisla-proti-zdroji.py
Návrat:   1 = některé tvrzení se rozešlo se zdrojem | 0 = vše souhlasí
"""

import json
import os
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
SKILLS = pathlib.Path.home() / ".dsh" / "skills"
GODOT = WS / "orchestra" / "tools" / "godot" / "Godot_v4.7.2-stable_win64_console.exe"

# Dokumenty, kde žijí NORMATIVNÍ tvrzení (ne pracovní poznámky v _analyza).
JADRO = ["AGENTS.md", "HANDOFF.md", "PREDAVANI-SESSION.md", "KRONIKA-PROJEKTU.md",
         "PLAN-DALSI-KROK.md", "NEXT-SESSION-INSTRUKCE.md", "MOZNOTI-AGENTA.md",
         "OTEVRENA-TEMATA.md", "MOZNOSTI-AGENTA.md"]


def spust(prikaz, vzor, env=None):
    """Spustí bránu a vytáhne z výstupu číslo. Když číslo není, je to VIDĚT
    (vrací None s důvodem) — ne tichá nula."""
    try:
        r = subprocess.run(prikaz, cwd=str(WS), capture_output=True, env=env,
                           timeout=300)
    except Exception as e:                                        # noqa: BLE001
        return None, "nepodařilo se spustit: %s" % type(e).__name__
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    m = re.search(vzor, v)
    if not m:
        return None, "výstup neobsahuje vzor %r" % vzor
    return int(m.group(1)), "exit=%d" % r.returncode


def schema_pocty():
    sql = (WS / "orchestra" / "conductor" / "schema.sql").read_text(encoding="utf-8")
    sql = re.sub(r"--[^\n]*", "", sql)          # komentáře NEJSOU sloupce
    bloky = re.findall(r"CREATE TABLE IF NOT EXISTS\s+(\w+)\s*\((.*?)\n\);", sql, re.S)
    sloupcu = sum(len([l for l in b.splitlines() if l.strip()]) for _, b in bloky)
    return len(bloky), sloupcu


def main() -> int:
    doklady = []

    # ── 1. Naměřit živé zdroje ─────────────────────────────────────────────
    tabulky, sloupcu = schema_pocty()

    roadmap = WS / "games" / "uo-shadows" / ".forge" / "roadmap.json"
    granul = "NEZMĚŘENO"
    if roadmap.is_file():
        try:
            d = json.loads(roadmap.read_text(encoding="utf-8"))
            if isinstance(d, dict):
                for k in ("grains", "items", "granule", "tasks"):
                    if isinstance(d.get(k), list):
                        granul = len(d[k])
                        break
                else:
                    granul = len(d)
            else:
                granul = len(d)
        except Exception as e:                                    # noqa: BLE001
            granul = "CHYBA: %s" % type(e).__name__

    g3 = (WS / "_analyza" / "g3-brany.py").read_text(encoding="utf-8")
    bran = len(re.findall(r'^\s{4}\("', g3, re.M))

    env = dict(os.environ)
    env["APPDATA"] = str(WS / "_analyza" / "a-godot-user")
    env["PYTHONIOENCODING"] = "utf-8"

    merene = [
        ("skillů", len(list(SKILLS.glob("*/SKILL.md"))), "souborový systém"),
        ("bran", bran, "g3-brany.py (seznam BRANY)"),
        ("sloupců", sloupcu, "conductor/schema.sql (bez komentářů)"),
        ("tabul", tabulky, "conductor/schema.sql"),
        ("dokumentů", len(list(WS.glob("*.md"))), "*.md v kořeni"),
        ("granulí", granul, "uo-shadows/.forge/roadmap.json"),
    ]
    for popis, prikaz, vzor in (
            ("klíčových bodů", ["python", "_analyza/handoff-kontrola-uplnost.py"],
             r"kontrolovaných klíčů:\s+(\d+)"),
            ("omylů", ["python", "_analyza/kronika-kontrola.py"],
             r"omylů celkem \(skutečnost\):\s+(\d+)"),
    ):
        h, poznamka = spust(prikaz, vzor, env)
        merene.append((popis, h if h is not None else "NEZMĚŘENO (%s)" % poznamka,
                       "běh brány"))
    if GODOT.is_file():
        h, poznamka = spust([str(GODOT), "--headless", "--path",
                             str(WS / "games" / "uo-shadows"),
                             "--script", "res://tests/run_tests.gd"],
                            r"\[test\]\s+(\d+) kontrol", env)
        merene.append(("kontrol", h if h is not None else "NEZMĚŘENO (%s)" % poznamka,
                       "běh Godotu nad hrou"))

    zdroje = {k: v for k, v, _ in merene}

    print("=" * 100)
    print("AUDIT 2b — ČÍSLO PROTI ZDROJI")
    print("=" * 100)
    print("  %-18s %-14s %s" % ("veličina", "ŽIVÝ ZDROJ", "odkud"))
    print("  " + "-" * 94)
    for k, v, odkud in merene:
        print("  %-18s %-14s %s" % (k, v, odkud))
    print()

    # ── 2. Porovnat s tvrzeními v dokumentech ──────────────────────────────
    # ⚠ MARKDOWN ZVÝRAZNĚNÍ UVNITŘ SLOVA — naměřeno 2. 10. 2026 (19:5x).
    # Kotva v `HANDOFF.md` zní
    #     „- **D1 má 16 řádků na 21 granul**"
    # a vedle ní je v témže bloku i tvar `**21 granul**ích` a **5 výskytů
    # slova `granul*` psaných s CYRILSKÝM `е`** (U+0435) místo latinského `e`
    # — tedy **jiný znak, který vypadá stejně**.
    # Vzor `(\d+)\s+granul` přes hranici zvýraznění **nesáhne** a výskyt se
    # **tiše vynechá**. To je přesně vada „měřidlo, které tiše vynechá vstup"
    # (`AGENTS.md`, „Co nikdy") — a projevila se tak, že `audit2b-over.py`
    # hlásil **falešný poplach** („kotva není v ZÁZNAMECH"), protože kotva
    # pro nástroj **vůbec neexistovala**.
    # **Náprava:** jednotka se hledá jako **první 4–6 znaků** a mezi číslem
    # a jednotkou se povolí **hvězdičky a mezery**; cyrilské `е` se povoluje
    # **jen u slova `granul*`** (jinde by to rozbilo jiné veličiny).
    VZORY = {
        "skillů": r"(\d+)\s+skill",
        "bran": r"(\d+)\s+bran",
        "sloupců": r"(\d+)\s+sloupc",
        "tabul": r"(\d+)\s+tabul",
        "dokumentů": r"(\d+)\s+dokument",
        # `granul` s tolerancí MARKDOWNOVÉHO ZVÝRAZNĚNÍ mezi číslem a slovem.
        # ⚠ Naměřeno 2. 10. 2026 na **14 reálných tvarech** z `HANDOFF.md`
        # a `AGENTS.md` (sonda `_analyza\_s24-sonda-vzor5.py`):
        #     původní vzor `(\d+)\s+granul`  → chytí **12 ze 14** (20 výskytů)
        #     tento vzor                     → chytí **14 ze 14** (22 výskytů)
        # Mine například `21** granul` a `21** granulí` (zvýraznění je
        # **PŘED** číslem) — a přesně jeden z těch tvarů je kotva, kterou
        # `audit2b-over.py` hledá, takže nástroj o výskytu **vůbec nevěděl**
        # a test hlásil **falešný poplach** („kotva není v ZÁZNAMECH").
        # **Je to vada „měřidlo tiše vynechá vstup"** (`AGENTS.md`).
        # Tolerance konce slova (`[íi]|\u0435|ch`) se **ZAMÍTÁ**: naměřeno
        # **13 ze 14** — vyhodí `4 granule**`, což je legitimní tvar.
        "granulí": r"(\d+)\s*\**\s*granul",
        "klíčových bodů": r"(\d+)\s+klíčov",
        "omylů": r"(\d+)\s+omyl",
        # ⚠ `(?!\w)` — DOPLNĚNO 2. 10. 2026 a je to samostatný nález:
        # vzor `(\d+)\s+kontrol` zabíral i **„2 kontrolní vzorky"**
        # (`b5-over-tvrzeni.py`) a **„2 kontrolní + 3 vady"** — tedy slovo
        # `kontrolní`, které **žádný počet kontrol není**. Naměřeno: v jádru
        # je takových výskytů **10**. `\b` to NEŘEŠÍ (`kontrol` + `\b` před
        # `ní` projde, protože `l`→`n` hranice není) — proto negativní
        # lookahead na slovo. `kontrol,` `kontrol.` `kontrol)` projdou dál.
        "kontrol": r"(\d+)\s+kontrol(?!\w)",
    }
    # Slova, po kterých je číslo CITACE minulosti, ne tvrzení o dnešku.
    CITACE = re.compile(r"tvrdil|dřív|dř[íi]ve|bylo|býval|opraveno|histor|místo|"
                        r"než\s|chybn|zastaral|před\s|SNAPSHOT|čekalo|naměřeno\s+\d",
                        re.I)

    # ⚠ `NENI_POCET` musí být definováno PŘED `je_pocet()` — Python čte tělo
    # funkce až při volání, ale kdyby se sem přidal `return` na modulové
    # úrovni, byla by to jemná past. Drží se to tady pohromadě schválně.
    # (Používá ho `je_pocet()` níž; konstanta stojí tady, aby byla po ruce
    # i čtenáři, který hledá, „co se ještě nepočítá".)
    NENI_POCET = re.compile(r"^\s*[),.;—–-]?\s*\**\s*(?:řádk|radk)", re.I)


    # ⚠ NAMĚŘENO 2. 10. 2026 (Úkol 1 zadání `ZADANI-OPRAVA-MERIDEL.md`), a je
    # to **druhá polovina vady**, kterou měl `audit2a` a `audit2b` **společnou**:
    # konstanta `CITACE` pozná **slova** minulosti, ale ne **uvozovky**.
    #
    #   `PLAN-DALSI-KROK.md:71` zní:
    #       | `sloupců` | **4** | **4** | všechny jsou **citace** `„32 sloupců"` |
    #   a `PREDAVANI-SESSION.md:193` zní:
    #       naměřeno u „32 sloupců" v `AGENTS.md`, nález **N9**).
    #
    # Na obou řádcích je `32 sloupců` **citace cizího tvrzení** — jenže mezi
    # otvírací uvozovkou a číslem stojí **uzavírací uvozovka z vnořené citace**,
    # takže „je číslo mezi uvozovkami?" se **míjí**.
    # Zavést se proto musel **skener**, ne „najdi uvozovku před číslem".
    #
    # ⚠ PROČ SE SKENUJE PO ŘÁDCÍCH, A NE STAVOVÝM AUTOMATEM PŘES CELÝ DOKUMENT:
    # jediná neuzavřená uvozovka kdekoli v 300kB dokumentu by přepnula stav
    # **pro zbytek souboru** — brána by pak za citaci považovala všechno
    # (nebo nic). `audit2a` na tuhle past upozorňuje ve `v_uvozovkach()`.
    # Řádek je přirozená hranice: markdown citace ani kódové rozpětí
    # **přes konec řádku nevedou** (a když ano, je to vada dokumentu, ne měřidla).
    UVOZOVKY = [("„", "“"), ("„", '"'), ('"', '"'), ("`", "`"), ("*„", "“")]

    def je_citace(s: str, index: int) -> bool:
        """Je znak na `index` uvnitř české uvozovky nebo kódového rozpětí?

        Skenuje se **jen ten jeden řádek**, zleva doprava, se zásobníkem
        otevřených uvozovek. Vnořené uvozovky (`„…` `` ` `` `` ` `` …") tím
        vyjdou správně — a to je přesně ten tvar, na kterém se obě měřidla
        rozešla.

        ⚠ VLASTNÍ OMYL, NAMĚŘENÝ PŘI PSANÍ TÉHLE FUNKCE (2. 10. 2026) — stojí
        za zapsání, protože vypadal jako „skener nefunguje":
        první verze testovala `if i > v_radku: break` **uvnitř** smyčky, tedy
        až **po** tom, co se pozice minula. U vnořené citace
        (`` `„32 sloupců"` ``) se tím číslo vyhodnotilo jako **mimo citaci**
        a brána hlásila **falešný rozchod** — 2× u téhož řádku.
        **Náprava není „přidat podmínku", ale spočítat ROZSAHY a pak se ptát
        na PŘÍSLUŠNOST** (`i <= v_radku < konec`). Je to táž třída jako
        `overovani` §9.4: **predikát hledání musí být týž jako predikát
        ověření** — jinak se „naměřeno 0" a „nenašlo se" nerozliší.
        """
        radky = s.splitlines()
        radek_idx = s.count("\n", 0, index)
        if radek_idx >= len(radky):
            return False
        radek = radky[radek_idx]
        v_radku = index - (s.rfind("\n", 0, index) + 1)
        if v_radku >= len(radek):
            return False

        # 1) spočítej ROZSAHY citací / kódových rozpětí na tom řádku
        rozsahy = []
        otevreno = []          # zásobník (znak, pozice otevření)
        i = 0
        while i < len(radek):
            if otevreno:
                if radek.startswith(otevreno[-1][0], i):
                    _zavr, poz = otevreno.pop()
                    rozsahy.append((poz, i + len(_zavr)))
                    i += len(_zavr)
                else:
                    i += 1
                continue
            # ⚠ UVNITŘ KÓDOVÉHO ROZPĚTÍ SE HLEDAJÍ I UVOZOVKY — a je to
            # naměřený případ, ne teorie. `HANDOFF.md:743` zní:
            #     …a v něm je `„32 sloupců"` **citované podruhé**.
            # Tedy: kódové rozpětí, a **v něm** česká citace. Kdyby se uvnitř
            # backticku nic nehledalo, číslo by vyšlo jako „mimo citaci"
            # a brána by hlásila **falešný rozchod**.
            # `„` je jednoznačný otvírací znak, takže se smí otevřít i uvnitř
            # backticku; `"` uvnitř backticku naopak NE (mohlo by to být
            # „uvozovka" v kódu).
            if otevreno and otevreno[-1][0] == "`":
                if radek.startswith("„", i):
                    otevreno.append(("“", i))
                    i += 1
                    continue
                i += 1
                continue
            for otev, zavr in UVOZOVKY:
                if radek.startswith(otev, i):
                    otevreno.append((zavr, i))
                    i += len(otev)
                    break
            else:
                i += 1
        # Neuzavřený ostrůvek na konci řádku: bere se jako citace až do konce
        # (radši „uvnitř" než „mimo" — falešný rozchod se hledá hůř).
        for _zavr, poz in otevreno:
            rozsahy.append((poz, len(radek)))

        # 2) a teprve TEĎ se ptej na PŘÍSLUŠNOST pozice
        return any(a <= v_radku < b for a, b in rozsahy)

    # ── REGISTR BRAN: smí se srovnávat s VÍC NEŽ JEDNÍM zdrojem ────────────
    # ⚠ JÁDRO OPRAVY (nález **H29**/Úkol 1). Do 2. 10. 2026 platilo: veličina
    # `kontrol` = **jedno** číslo (běh Godotu nad hrou) a s ním se srovnával
    # **každý** výskyt `(\d+)\s+kontrol` v jádru. Naměřeno v této session:
    # z **15** rozchodů u `kontrol` jich **11** vzniklo tak, že dokument
    # **správně citoval jinou bránu** (`a1-a2-over` 23 · skener 23 ·
    # `over-dokumentaci` 63 · `test-check-schema` 17 · `vision.test.mjs` 36 ·
    # `test-cooldown` 10 …). **Nebyla to vada dokumentu, ale měřidla.**
    #
    # Registr je **uzavřená množina NAMĚŘENÝCH hodnot** (`_registr-bran.py`),
    # každá s bránou, příkazem a dokladem. Není to „vše, co se mi hodí":
    #   * brána, která číslo nehlásí, se do registru nedostane (zůstane `None`);
    #   * hodnota, kterou nevydala žádná brána, se **pořád hlásí jako rozchod**
    #     (naměřeno: `38` i `39`) — registr tedy **neschová nový drift**.
    # Když registr chybí, je to vidět (`NEZMĚŘENO`) — nikdy tichá nula.
    REGISTR = WS / "_analyza" / "_registr-bran.json"
    registr, registr_pozn = {}, ""
    if REGISTR.is_file():
        try:
            registr = json.loads(REGISTR.read_text(encoding="utf-8"))
        except Exception as e:                                    # noqa: BLE001
            registr_pozn = "registr se nepodařilo přečíst (%s)" % type(e).__name__
    else:
        registr_pozn = ("registr bran NENÍ (`python _analyza/_registr-bran.py`) "
                        "— veličinu `kontrol` nelze srovnat s živými branami")

    # ── SUBSETOVÉ ČÍTAČE: „N z M" a „N bez …" nejsou „celkem N" ────────────
    # ⚠ Naměřeno 2. 10. 2026: `PLAN-DALSI-KROK.md:135` zní
    #     „### KROK 4 — 3 z 10 bran bez mutačního testu"
    # a `NEXT-SESSION-INSTRUKCE.md:92` „…se **5 z 6 omylů** tváří jako cizí vina".
    # Obě čísla jsou **správně** a ani jedno není „celkem bran"/„celkem omylů":
    # je to **výřez**. Ptát se jich na celkový počet je tatáž vada jako
    # u `kontrol` — jen o patro jinde (jeden čítač, dva významy).
    SUBSET = re.compile(r"^\s*(?:z\s+\d|bez\s|mimo\s|kontrolních)", re.I)

    def je_subset(s: str, konec: int) -> bool:
        """Následuje za číslem výřezový výraz („z 10 …", „bez …")?"""
        return bool(SUBSET.match(s[konec:konec + 14]))

    # Které veličiny se srovnávají s REGISTREM (víc bran), ne s jedním zdrojem.
    # ⚠ `kontrol` je tu ZÁMĚRNĚ: srovnávat ji s jedním číslem je **vada H29**.
    # Do součtu rozchodů proto nevstupuje — a je to vidět v tabulce zdrojů.
    S_REGISTREM = ("kontrol",)

    # ── DRUHÝ ZDROJ PRO `dokumentů` (a proč to nestačí jednou) ─────────────
    # ⚠ Naměřeno 2. 10. 2026: veličina `dokumentů` se srovnávala s **jedním**
    # číslem — počtem `*.md` v KOŘENI (40). Jenže dokumenty na tuhle veličinu
    # mluví ve **třech různých významech** a každý má jiný zdroj:
    #     „57 dokumentů" (PLAN-DALSI-KROK.md:175)  = seznam v bráně diakritiky
    #     „35 dokumentů" (HANDOFF.md:582)          = výstup TÉŽE brány
    #     „8 dokumentů"  (HANDOFF.md:583)          = **řádky tabulky**, ne dokumenty
    # První dvě se srovnají se **seznamem v bráně**, třetí **není počet**
    # (viz `NENI_POCET` níž). Stejná třída jako `kontrol`: jeden název,
    # víc čítačů (`dsh-prostredi` §5, „Různé čítače nesou stejné jméno").
    BRANA_DIA = WS / "orchestra" / "tools" / "kontrola-diakritiky.py"
    dokumentu_seznam = None
    if BRANA_DIA.is_file():
        _z = BRANA_DIA.read_text(encoding="utf-8")
        _m = re.search(r"SOUBORY\s*=\s*\[(.*?)\n\]", _z, re.S)
        if _m:
            dokumentu_seznam = len(re.findall(r"[\"'][^\"']+\.md[\"']", _m.group(1)))
    zdroje["dokumentů (seznam brány)"] = (dokumentu_seznam
                                          if dokumentu_seznam is not None
                                          else "NEZMĚŘENO")
    merene.append(("dokumentů (seznam brány)",
                   dokumentu_seznam if dokumentu_seznam is not None
                   else "NEZMĚŘENO (seznam se nepřečetl)",
                   "orchestra/tools/kontrola-diakritiky.py (seznam SOUBORY)"))

    # ── TŘETÍ VÝZNAM TÉHOŽ SLOVA: „N souborů" = kolik brána OTEVŘELA ───────
    # ⚠ Naměřeno 2. 10. 2026 (`HANDOFF.md:471`): „`kontrola-diakritiky` →
    # **35 souborů**" — a to je **třetí čítač téhož slova**. Brána dnes hlásí
    # `celkem ke kontrole 333` (naměřeno spuštěním). Do 2. 10. měla **ruční
    # seznam**, takže se číslo mohlo počítat z něj; dnes **prochází složku**
    # (nález NA15) a `35` je proto **staré měření**, ne cizí čítač.
    # Bere se z výstupu brány — ne odhadem (`overovani` §2.3).
    if BRANA_DIA.is_file():
        try:
            _r = subprocess.run(["python", "orchestra/tools/kontrola-diakritiky.py"],
                                cwd=str(WS), capture_output=True, timeout=600,
                                env=env)
            _v = (_r.stdout.decode("utf-8", "replace")
                  + _r.stderr.decode("utf-8", "replace"))
            _m = re.search(r"celkem ke kontrole\s+(\d+)", _v)
            dokumentu_otevrela = int(_m.group(1)) if _m else None
            _p = "exit=%d" % _r.returncode
        except Exception as e:                                    # noqa: BLE001
            dokumentu_otevrela, _p = None, "nepodařilo se spustit: %s" % type(e).__name__
        zdroje["souborů (brána diakritiky)"] = (dokumentu_otevrela
                                                if dokumentu_otevrela is not None
                                                else "NEZMĚŘENO (%s)" % _p)
        merene.append(("souborů (brána diakritiky)",
                       dokumentu_otevrela if dokumentu_otevrela is not None
                       else "NEZMĚŘENO (%s)" % _p,
                       "běh orchestra/tools/kontrola-diakritiky.py"))
    else:
        zdroje["souborů (brána diakritiky)"] = "NEZMĚŘENO (brána není)"
        dokumentu_otevrela = None

    # ── ČÍSLO, KTERÉ NENÍ POČET — a číslo, které PATŘÍ JINÉ JEDNOTCE ───────
    # ⚠ Dva naměřené případy 2. 10. 2026, oba na **jednom** řádku
    # (`HANDOFF.md:583`, omyl **22**), jen každý jinou pastí:
    #
    #   (a) „…vzor nenašel a **tabulka mi vyšla jako 0 řádků**"
    #       → nula je počet **ŘÁDKŮ**, ne dokumentů. Vzor `(\d+)\s+dokument`
    #       ji ale nespáruje — spáruje **jiné** číslo na tomtéž řádku (viz b).
    #
    #   (b) „`Get-Content` přečte UTF-8 dokument **správně** | **Ne** — …“
    #       → tady je jednotka **uprostřed věty**, ne za číslem. Vzor na tom
    #       řádku našel `8 dokument` — kde `8` patří slovu „**8 řádků**"
    #       o třicet znaků dál. **Číslo a jednotka k sobě NEPATŘÍ**, a přesto
    #       se spárovaly, protože jsou na jednom řádku.
    #       Je to táž past jako `2 kontrolní vzorky`: **rozhoduje okolí
    #       jednotky**, ne to, že jsou obě na řádku (`overovani` §10.1:
    #       „ptej se, KTERÝ výskyt vzor trefí").
    #
    # Guard proto zkoumá **mezeru mezi číslem a jednotkou**: když v ní stojí
    # jiné číslo nebo slovo jiné jednotky, počet to není.
    # ⚠ `kontrol` JE V TOM SEZNAMU ZÁMĚRNĚ — a je to **vlastní omyl** z 2. 10.
    # 2026: první verze porovnávala jednotku se seznamem VŠECH jednotek
    # (včetně `kontrol`), takže u `12 kontrol` vyhodnotila „jednotka je jiná
    # veličina" a **zahodila správné tvrzení**. Projevilo se to jako
    # „predikát odmítá 147 čísel".
    # **Pravidlo: množina zakázaných jednotek nesmí obsahovat tu, kterou
    # měřím** — ověřuje se to proti OČEKÁVANÉ jednotce (`OCEKAVANA` níž),
    # ne proti globálnímu seznamu.
    # (V seznamu zůstává proto, aby ho bylo vidět; používá ho ta kontrola.)
    JINA_JEDNOTKA = re.compile(r"\d|\b(?:řádk|radk|soubor|bod|znak|kontrol|"
                               r"sloupc|tabul|granul|omyl|bran|skill)", re.I)

    # Ke každé VELIČINĚ, kterou tenhle nástroj měří, patří její jednotka.
    # Číslo je POČET jen tehdy, když za ním stojí **ta** jednotka — ne když
    # je na tomtéž řádku o kus dál (viz (b) výš).
    OCEKAVANA = {
        "kontrol": "kontrol", "dokumentů": "dokument", "sloupců": "sloupc",
        "tabul": "tabul", "granulí": "granul", "omylů": "omyl",
        "bran": "bran", "skillů": "skill", "klíčových bodů": "klíčov",
    }

    # ⚠ `konec` JE INDEX ZA CELÝM SPOJENÍM „číslo + jednotka", NE za číslem.
    # To byl **vlastní omyl** naměřený při psaní téhle funkce (2. 10. 2026)
    # a stál dvě kola: první verze brala `s[konec:]` jako „zbytek za číslem",
    # takže u `39 kontrol, 0 selhání` viděla na prvním místě **`0`** — a protože
    # `JINA_JEDNOTKA` obsahuje `\d`, vyhodnotila „0 je jiná jednotka" a
    # **zahodila 147 správných tvrzení**. Vypadalo to jako „brána je přísná".
    # **Pravidlo: když funkce dostane index, musí si nejdřív ověřit, K ČEMU
    # ten index patří** (`overovani` §10.1) — jinak měří jiný výsek, než myslí.
    SPOJENI = re.compile(r"(?P<cislo>\d+)(?P<mezi>[ \t*_]*)(?P<jednotka>[A-Za-zÁ-Žá-ž]+)")

    def je_pocet(s: str, konec: int, ocekavana: str) -> bool:
        """Je číslo na konci `konec` opravdu POČET jednotky `ocekavana`?

        `konec` je index ZA spojením „číslo + jednotka". Funkce si spojení
        najde **zpětným pohledem** — a tím pádem měří přesně ten výsek, který
        vzor spároval (ne „něco za ním").

        Tři podmínky, každá z naměřené pasti:
          1. spojení musí končit přesně na `konec` (jinak měřím jiný výsek),
          2. jednotka musí odpovídat **té, kterou měřím** (`ocekavana`),
             jinak číslo patří jiné veličině na témž řádku,
          3. za jednotkou nesmí stát jiná jednotka („0 řádků").
        """
        konec_radku = s.find("\n", konec)
        if konec_radku < 0:
            konec_radku = len(s)
        zacatek_radku = s.rfind("\n", 0, konec) + 1
        m = None
        for m in SPOJENI.finditer(s, zacatek_radku, konec):
            pass                      # POSLEDNÍ spojení končící před `konec`
        if not m or m.end() != konec:
            return False              # spojení nesedí na `konec`
        jednotka = m.group("jednotka").lower()
        if not jednotka.startswith(ocekavana.lower()):
            return False              # jednotka je jiná veličina
        # a co stojí ZA jednotkou — nemluví to o jiné veličině?
        return not NENI_POCET.match(s[konec:konec_radku])


    # ⚠ DATUM JE NEJSILNĚJŠÍ ZNAK MINULOSTI — a do 2. 10. 2026 se hledalo JEN
    # NA ŘÁDKU. To je celý nález **R3**: `HANDOFF.md` má správně obsahovat stará
    # čísla (je to append-only záznam), ale datum bývá v **nadpisu oddílu**
    # („## 14. Provedeno 2. 10. 2026 …") — a ten heuristika neviděla, takže
    # 11 správných záznamů „21 granul" hlásila jako ROZCHOD.
    # Nově se zkouší ve TŘECH úrovních, od nejsilnější:
    #   1. slova minulosti na ŘÁDKU            (původní heuristika)
    #   2. NADPIS ODDÍLU s datem / „Provedeno" / „Ověření"   ← předepsáno Úkolem 4
    #   3. DATUM V BLOKU výskytu               ← doměřeno: bez toho zůstaly 3
    #      (`AGENTS.md:255`, `OTEVRENA-TEMATA.md:380` a `:494` — všechny tři jsou
    #      datované záznamy, ale datum mají o pár řádků výš, uvnitř téhož odstavce)
    # **BLOK se u tabulkového řádku bere JEN ten řádek** — jinak by celá tabulka
    # (v `HANDOFF.md` §8 má stovky řádků) byla jeden „blok", jediné datum kdekoli
    # v ní by umlčelo všechny její řádky a brána by přestala měřit (`overovani`
    # §9.6: očekávaná nepřítomnost není vada — ale ani jedno datum nesmí umlčet
    # celou tabulku).
    DATUM = re.compile(r"\d{1,2}\.\s*\d{1,2}\.\s*\d{4}")
    # ⚠ VELKÁ PÍSMENA A CHYBĚJÍCÍ SLOVA — naměřeno 2. 10. 2026 (19:4x):
    # pravidlo čte `z in nadpis.lower()`, ale `ZNAKY_ODDILU` byly **malými**
    # písmeny a `"ověření" in "## 24. Ověření práce §23 …"` je **False**,
    # protože nadpis má „**O**věření". Oddíl §24 (ten, který dokument
    # OVĚŘUJE) tím propadl na „není záznam" a jeho datovaný záznam
    # („21 granul") se **ohlásil jako rozchod**.
    # Je to **nejméně pětatřicátý** výskyt téže třídy v projektu: porovnává se
    # **tvarem**, ne **významem** (`overovani` §8.3). Nadpis se proto skládá
    # na malá písmena **jednou** a porovnává se case-insensitive.
    # Doplněna jsou i slova pro oddíly **měření** („Měření", „Kontrola",
    # „Závěr") — bez nich by každý nový měřicí oddíl vypadal jako tvrzení.
    ZNAKY_ODDILU = ("provedeno", "ověření", "ověřeno", "záznam",
                    "měření", "měřeno", "kontrola", "závěr", "souhrn")
    # Začátek nového celku: odrážka, číslovaná odrážka, tabulkový řádek, nadpis.
    ZACATEK = re.compile(r"^\s*(?:[-*+]\s|\d+\.\s|\||#)")

    def blok(s: str, i: int) -> str:
        """Okolí výskytu: u tabulkového řádku JEN ten řádek, jinak JEDNA
        odrážka / jeden odstavec (nikdy ne přes začátek další odrážky).

        ⚠ PROČ TAKHLE ÚZKCE (naměřeno 2. 10. 2026, vlastní omyl):
        první verze brala „souvislý blok neprázdných řádků" — a v `AGENTS.md`
        je oddíl „## Jak dokumentovat" **jeden takový blok o 5 441 znacích se
        sedmi daty**. Tím by jediné datum kdekoli v něm umlčelo **všechna**
        čísla oddílu, tedy i skutečné tvrzení o dnešku — brána by byla zelená
        a nikdo by nepoznal proč (`overovani` §9.6). Rozsah se proto zastavuje
        na začátku další odrážky/tabulky/nadpisu; odrážka, ve které výskyt je,
        se počítá celá (i její první řádek).
        """
        radky = s.splitlines()
        idx = s[:i].count("\n")
        if idx >= len(radky):
            return ""
        if radky[idx].lstrip().startswith("|"):
            return radky[idx]
        a = idx
        while a > 0 and radky[a - 1].strip() and not ZACATEK.match(radky[a - 1]):
            a -= 1
        if a > 0 and radky[a - 1].strip() and ZACATEK.match(radky[a - 1]):
            a -= 1                      # první řádek TÉ odrážky patří k bloku
        b = idx
        while (b + 1 < len(radky) and radky[b + 1].strip()
               and not ZACATEK.match(radky[b + 1])):
            b += 1
        return "\n".join(radky[a:b + 1])

    def nadpis_oddilu(s: str, i: int) -> str:
        """Nadpis `## …`, do kterého výskyt patří (prázdný, když žádný není).

        ⚠ ZKOUŠENO A VRÁCENO 2. 10. 2026 (19:5x): rozšířil jsem hledání na
        `### ` („nejbližší nadpis je přesnější") — a **zhoršilo to stav
        z 31 rozchodů na 127**. Ukázalo se, že `###` nadpisy v `HANDOFF.md`
        nesou **texty omylů a tabulek** („### 23.6 Vlastní omyly…"), takže se
        najednou jako záznamy oklasifikovaly **cizí** výskyty. **Vráceno.**
        Poučení: „přesnější" není totéž co „lepší" — a **každá změna měřidla
        se musí změřit PŘED i PO** (`overovani` §9.7).
        """
        radky = s.splitlines()
        idx = s[:i].count("\n")
        for k in range(min(idx, len(radky) - 1), -1, -1):
            if radky[k].startswith("## "):
                return radky[k]
        return ""

    print("=" * 100)
    print("  TVRZENÍ V JÁDRU vs. ŽIVÝ ZDROJ")
    print("=" * 100)
    rozchody, shody, histor = [], 0, []
    preskoceno = []        # čísla, která NEJSOU počet (musí být vidět!)

    # Hodnoty, které vydaly ŽIVÉ BRÁNY (z registru) — srovnávací množina
    # pro veličinu `kontrol`. Načítá se jednou, aby se u každého výskytu
    # dalo říct, KTERÁ brána to číslo vydala (nález NA17).
    brany = (registr or {}).get("brany", {})
    hodnoty_bran = {}
    for jmeno_b, z in brany.items():
        h = z.get("kontrol")
        if h is not None:
            hodnoty_bran.setdefault(h, []).append(jmeno_b)
    if registr_pozn:
        print("  ⚠ %s" % registr_pozn)
        print()

    # ── TABULKA ZDROJŮ (nález NA17: „celkem N" bez seznamu zdrojů je
    # neověřitelné). Vypisuje se PŘED rozchody, aby čtenář viděl, s ČÍM se
    # která veličina srovnává — a kolik rozchodů z toho vyšlo.
    print("  ZDROJE PODLE VELIČIN (s čím se srovnává a kolik z toho vyšlo):")
    print("      %-16s %-22s %s" % ("veličina", "ZMĚŘENÝ ZDROJ", "odkud"))
    print("      " + "-" * 88)
    for klic in VZORY:
        if klic in S_REGISTREM:
            if hodnoty_bran:
                popis = "brány: %s" % ", ".join(
                    "%d" % h for h in sorted(hodnoty_bran, reverse=True))
                odkud = ("%d bran z registru (`_registr-bran.py`)"
                         % len(hodnoty_bran))
            else:
                popis = "NEZMĚŘENO"
                odkud = "registr bran chybí nebo je prázdný — NENÍ to nula"
            print("      %-16s %-22s %s" % (klic, popis, odkud))
            continue
        zivy = zdroje.get(klic)
        odkud = dict((k, o) for k, _v, o in merene).get(klic, "?")
        print("      %-16s %-22s %s" % (klic, zivy, odkud))
    print()

    for jmeno in JADRO:
        cesta = WS / jmeno
        if not cesta.is_file():
            continue
        s = cesta.read_text(encoding="utf-8")
        radky = s.splitlines()
        for klic, vzor in VZORY.items():
            zivy = zdroje.get(klic)
            s_registrem = klic in S_REGISTREM
            if not s_registrem and not isinstance(zivy, int):
                continue
            for m in re.finditer(vzor, s):
                # ⚠ ČÍSLO, KTERÉ NENÍ POČET („0 řádků tabulky", „2 kontrolní
                # vzorky") se přeskočí s VYSVĚTLENÍM — ne tiše. Kdyby se
                # přeskočilo tiše, je to „měřidlo, které vynechá vstup".
                if not je_pocet(s, m.end(), OCEKAVANA.get(klic, klic)):
                    _kr = s.find("\n", m.start())
                    if _kr < 0:
                        _kr = len(s)
                    preskoceno.append((jmeno, s[:m.start()].count("\n") + 1,
                                       klic, int(m.group(1)),
                                       re.sub(r"\s+", " ",
                                              s[m.start():_kr]).strip()[:110]))
                    continue
                tvrzeno = int(m.group(1))
                radek = s[:m.start()].count("\n") + 1
                okoli = radky[radek - 1] if radek - 1 < len(radky) else ""
                nadpis = nadpis_oddilu(s, m.start())
                kontext = blok(s, m.start())

                # ── Který zdroj to číslo vydal? ────────────────────────────
                if s_registrem:
                    zdroj_pole = ",".join(sorted(hodnoty_bran.get(tvrzeno, [])))
                    sedi = bool(zdroj_pole)
                else:
                    zdroj_pole = str(zivy)
                    sedi = (tvrzeno == zivy)
                    # Další zdroje pro `dokumentů`: seznam v bráně diakritiky
                    # a počet souborů, které ta brána OTEVŘELA. Bere se jen
                    # tehdy, když číslo nesedí na kořen — a je to VIDĚT ve
                    # sloupci zdroje (nález NA17).
                    if not sedi and klic == "dokumentů":
                        if dokumentu_seznam is not None and tvrzeno == dokumentu_seznam:
                            zdroj_pole = "%d (seznam brány)" % dokumentu_seznam
                            sedi = True
                        elif (dokumentu_otevrela is not None
                              and tvrzeno == dokumentu_otevrela):
                            zdroj_pole = "%d (brána otevřela)" % dokumentu_otevrela
                            sedi = True

                # ── Rozhodnutí: záznam, citace, výřez, nebo tvrzení? ───────
                # POŘADÍ JE ZÁVAŽNÉ: citace a záznam jsou „není to tvrzení
                # o dnešku" — mají přednost před shodou i před výřezem.
                if CITACE.search(okoli):
                    duvod = "slova minulosti na řádku"
                elif DATUM.search(nadpis) or any(z in nadpis.lower()
                                                 for z in ZNAKY_ODDILU):
                    duvod = "oddíl: %s" % nadpis[:52]
                elif DATUM.search(kontext):
                    duvod = "datum v bloku výskytu"
                elif je_citace(s, m.start()):
                    duvod = "CITACE (uvozovky / kódové rozpětí)"
                elif sedi:
                    shody += 1
                    continue
                elif s_registrem and je_subset(s, m.end()):
                    duvod = "výřez, ne celkem („z N …“ / „bez …“)"
                else:
                    duvod = ""
                # ⚠ U KAŽDÉHO VÝSKYTU SE PAMATUJE I **KTERÁ BRÁNA** ČÍSLO VYDALA
                # (nález NA17 / požadavek zadání: „u každé veličiny říct, KTERÝ
                # ZDROJ ji měří"). U veličiny bez registru je to `""`.
                brana_zdroj = ""
                if s_registrem and zdroj_pole:
                    brana_zdroj = zdroj_pole
                zaznam = (jmeno, radek, klic, tvrzeno,
                          zdroj_pole if not s_registrem else (brana_zdroj or "—"),
                          duvod,
                          re.sub(r"\s+", " ", okoli).strip()[:110])
                (histor if duvod else rozchody).append(zaznam)

    print("  shod s živým zdrojem: %d" % shody)
    print()
    if preskoceno:
        # ⚠ VYNECHANÝ VSTUP MUSÍ BÝT VIDĚT (`AGENTS.md`). Kdyby se přeskočil
        # tiše, je to přesně ta vada, kterou tenhle nástroj hledá u jiných.
        print("  PŘESKOČENO — číslo, které NENÍ počet („…0 řádků tabulky“,")
        print("  „…2 kontrolní vzorky“): %d" % len(preskoceno))
        for j, r, k, t, u in preskoceno:
            print("      %-24s :%-5d %-14s %-5s u: %s" % (j, r, k, t, u[:80]))
        print()
    print("  ROZCHODY (tvrzení bez známky minulosti) — %d:" % len(rozchody))
    for j, r, k, t, z, _, okoli in rozchody:
        print("      %-24s :%-5d %-14s tvrdí %-6s zdroj %-12s"
              % (j, r, k, t, z if z else "—"))
        print("            %s" % okoli)
    print()
    # `histor[:40]` je **ZKRÁCENÝ VÝPIS** (a naměřeno 2. 10. 2026: kvůli tomu
    # hlásil ověřovatel `audit2b-over.py` **falešný poplach** — kotva na
    # ř. 1201 je v ZÁZNAMECH, ale za hranicí 40). `--vsechny-zaznamy` vypíše
    # všechny; **na měření to nemá vliv**, jen na to, co je vidět.
    vsechny_zaznamy = "--vsechny-zaznamy" in sys.argv
    limit_zaznamu = None if vsechny_zaznamy else 40

    print("  ZÁZNAMY A CITACE MINULOSTI (nejsou to rozchody) — %d:" % len(histor))
    for j, r, k, t, z, duvod, okoli in histor[:limit_zaznamu]:
        print("      %-24s :%-5d %-14s tvrdí %-6s zdroj %-12s | %s"
              % (j, r, k, t, z if z else "—", duvod))
        print("            %s" % okoli[:96])
    if limit_zaznamu is not None and len(histor) > limit_zaznamu:
        print("      … a dalších %d" % (len(histor) - limit_zaznamu))
        print("      (PLNÝ výpis: `python _analyza/audit2b-cisla-proti-zdroji.py "
              "--vsechny-zaznamy`)")

    # Kolik rozchodů zbylo u každé veličiny — ať je vidět, KDE jich je kolik
    # (jinak „0 rozchodů" u jedné veličiny splývá s 155 u zbytku).
    # ⚠ NA17: ke každému číslu patří i to, S ČÍM se srovnávalo — jinak
    # „0 rozchodů" neznamená „v pořádku", ale může znamenat „nemělo to
    # s čím srovnávat" (u `kontrol` je to přesně ten případ: srovnává se
    # s **registrem bran**, ne s jedním číslem).
    # ⚠ POPISEK JE KOTVA PRO JINÝ NÁSTROJ — `s24-meridla-over.py` (brána na
    # zadání) hledá přesně `ROZCHODY PO VELIČINÁCH`. Naměřeno 2. 10. 2026:
    # když jsem ho rozšířil na „ROZCHODY PO VELIČINÁCH (a čím se která veličina
    # měřila)", **brána zadání spadla** (`✗ audit2b nevypsal rozpad po
    # veličinách`) — a přitom rozpad **byl ve výpisu celou dobu**.
    # Je to táž past jako „kotva, která usne" (`overovani` §7.11): **text, který
    # čte jiný program, je ROZHRANÍ** — smí se přidávat za něj, ne do něj.
    print()
    print("  ROZCHODY PO VELIČINÁCH: (a čím se která veličina měřila)")
    from collections import Counter
    pocty = Counter(k for _, _, k, _, _, _, _ in rozchody)
    for klic, pocet in pocty.most_common():
        print("      %-18s %d" % (klic, pocet))
    for klic in VZORY:
        if klic in pocty:
            continue
        if klic in S_REGISTREM:
            print("      %-18s 0   ← srovnává se s %d BRÁNAMI z registru, "
                  "ne s jedním číslem" % (klic, len(hodnoty_bran)))
        else:
            print("      %-18s 0   ← u téhle veličiny NIC" % klic)

    print()
    print("=" * 100)
    print("  ROZCHODŮ: %d   |   ZÁZNAMŮ A CITACÍ: %d" % (len(rozchody), len(histor)))
    return 1 if rozchody else 0


if __name__ == "__main__":
    sys.exit(main())
