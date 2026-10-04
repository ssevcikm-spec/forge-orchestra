# -*- coding: utf-8 -*-
"""AUDIT 1 — INVENTÁŘ: jediná tabulka o stavu každého dokumentu.

Zadání (plán auditu, fáze 1): inventář se **GENERUJE, nevede ručně** — jinak je
to vada S27 po třinácté. U každého dokumentu se měří osm sloupců a **žádný
nesmí být prázdný**: nula a „nezměřeno" musí být VIDĚT (`AGENTS.md`).

CO SE PROCHÁZÍ:
  * kořen workspace — `*.md`
  * `_analyza/` — `*.md` (rekurzivně; podsložky se drží zvlášť, jsou to
    pracovní kopie a worktree, ne dokumentace)
  * `~/.dsh/skills/*/SKILL.md` — skilly

CO SE NEHLÁSÍ JAKO CHYBA (a proč):
  * `_analyza/a-ukol-scratch`, `t1-kladna`, `v2-kladna` jsou **git worktree**
    s import cache Godotu (1 233 souborů každý). Nejsou to dokumenty — kdyby
    se počítaly, inventář tvrdí o workspace něco, co v něm není.

SLOUPCE (a jak se měří):
  druh                      — z hlavičky „Co tenhle dokument JE"; když ji nemá,
                              z názvu; když ani to ne, `NEURČENO` (nikdy prázdno)
  odkazu_v_jadru            — kolik z 8 dokumentů jádra se o něm zmiňuje
  odkazu_celkem             — zmínky ve všech ostatních inventovaných .md
  otevira_brána             — je v `kontrola-diakritiky.py` / `g1-*` / `kronika-kontrola.py`?
                              (`seznam` = ruční seznam, `slozka` = projití složky)
  v_gitu                    — `git ls-files` v obou repech; jinak `NE`
  zmenen                    — `git log -1 --format=%cI`; mimo git `mtime`
  hlavicka_datum_spotreby   — ANO / NE / `neni-clanek` (u skillu se nevyžaduje)
  je_zaloha                 — vzor `*-pred-*` / `*zaloha*` / `*zaloha*`

Použití:  python _analyza/audit1-inventar.py [--json _analyza/audit-inventar.json]
Návrat:   0 = inventář úplný | 1 = některý sloupec chybí (to je vada měření)
"""

import json
import pathlib
import re
import subprocess
import sys
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
SKILLS = pathlib.Path.home() / ".dsh" / "skills"
GIT = WS / "orchestra" / "tools" / "git.cmd"
REPA = {"orchestra": WS / "orchestra", "uo-shadows": WS / "games" / "uo-shadows"}

# Jádro = dokumenty, ze kterých se řídí každá session (viz AGENTS.md „Kam pro co").
JADRO = ["AGENTS.md", "HANDOFF.md", "PREDAVANI-SESSION.md", "KRONIKA-PROJEKTU.md",
         "PLAN-DALSI-KROK.md", "NEXT-SESSION-INSTRUKCE.md", "MOZNOSTI-AGENTA.md",
         "OTEVRENA-TEMATA.md"]

BRANY = {
    "kontrola-diakritiky.py": WS / "orchestra" / "tools" / "kontrola-diakritiky.py",
    "g1-diakritika-novych.py": WS / "_analyza" / "g1-diakritika-novych.py",
    "kronika-kontrola.py": WS / "_analyza" / "kronika-kontrola.py",
    "over-dokumentaci.py": WS / "orchestra" / "tools" / "over-dokumentaci.py",
    "over-skilly.py": WS / "orchestra" / "tools" / "over-skilly.py",
    "handoff-kontrola-uplnost.py": WS / "_analyza" / "handoff-kontrola-uplnost.py",
    "g3-brany.py": WS / "_analyza" / "g3-brany.py",
}

VLASTNI = pathlib.Path(__file__).name

# Worktree a pracovní kopie — nejsou dokumentace (viz docstring).
VYLUCENE_SLOZKY = {"a-ukol-scratch", "t1-kladna", "v2-kladna", "godot-appdata",
                   "a-godot-user", "gdcheck-appdata", "gdcheck-user", "__pycache__"}

# ⚠ PŘEDPONY, KTERÉ SE VYLUČUJÍ TAKY (doplněno 2. 10. 2026, Úkol 0 zadání
# `ZADANI-DOKONCENI-AUDITU.md` — a je to **nález o měřidle, který si vyrobila
# sama oprava**): `_analyza\audit-snapshot.py` kopíruje dokumentaci do
# `_analyza\snapshot-<čas>\`, aby šla porovnat. Tím se ale **kopie staly
# dokumenty** pro tenhle inventář: naměřeno po prvním snapshotu
# **159 dokumentů místo 98** a **66 záloh místo 8** — a číslo „dokumentů bez
# hlavičky" vyskočilo z **62 z 98** na **116 z 159**. Kdo by ta čísla četl
# jako stav dokumentace, čte **svůj vlastní snapshot**.
# Opatření 9 (zmrazit snapshot) tedy **samo sobě zneplatnilo baseline** —
# a to je přesně to, před čím varuje `AGENTS.md`: měřidlo musí vědět, co měří.
VYLUCENE_PREDPONY = ("snapshot-",)

# ── Klasifikace druhu ───────────────────────────────────────────────────────
VZORY_DRUHU = [
    (r"^AGENTS\.md$", "pravidla"),
    (r"^PREDAVANI-SESSION\.md$", "postup předávání"),
    (r"^HANDOFF\.md$", "stav"),
    (r"^KRONIKA", "kronika"),
    (r"^NEXT-SESSION", "zadání"),
    (r"ZADANI", "zadání"),
    (r"^PLAN|^s\d+.*plan", "plán"),
    (r"^ANALYZA|^HLOUBKOVA|^C-PODKLAD|^ARCHITEKTURA", "analýza"),
    (r"^IMPLEMENTACE|^A-UKOL-ZAZNAM|ZAZNAM", "záznam o provedení"),
    (r"^MOZNOSTI|^FORGE-ORCHESTRA-MOZNOSTI", "rejstřík schopností"),
    (r"^OTEVRENA-TEMATA", "seznam"),
    (r"^SKILLY-AKTUALIZACE", "historie"),
    (r"^README", "rozcestník"),
    (r"^POZOR-", "stav"),
    (r"^PROMPT", "zadání"),
    (r"^SOUBEH", "záznam o provedení"),
    (r"^DEPLOY", "rozcestník"),
    (r"^ORCHESTRA-STAV", "stav"),
    (r"^JAK-PSAT", "metodika"),
    (r"^RESEARCH|^sdxl|^token-saving", "rešerše"),
    (r"-oddil|-doplneni|-radek|^s\d+[a-z]?-", "pracovní úryvek"),
    (r"^SKILL\.md$", "skill"),
]

HLAVICKA_VZORY = [
    r"Co tenhle dokument JE", r"Co je tenhle soubor", r"Co tenhle soubor je",
    r"Co tenhle dokument je",
]
# Klíčová slova, kterými dokument o sobě říká, ČÍM JE. Druh je krátká
# kategorie — ne opis věty (naměřeno: doslovný opis dával nesmysly).
DEKLARACE = [
    (r"\bzadání\b", "zadání"),
    (r"\bplán\b|\bplan\b", "plán"),
    (r"\banalýz", "analýza"),
    (r"záznam o provedení|záznam o tom", "záznam o provedení"),
    (r"\bsnapshot\b|snímek", "snapshot"),
    (r"\bpravidla\b", "pravidla"),
    (r"\bpostup\b", "postup"),
    (r"kronika|příběh projektu", "kronika"),
    (r"\bstav\b", "stav"),
    (r"rejstřík|rozcestník", "rejstřík"),
    (r"\bmetodika\b", "metodika"),
    (r"\bseznam\b|ledger", "seznam"),
    (r"\bnástroj\b|měřidlo", "nástroj"),
    (r"\bskill\b|dovednost", "skill"),
]
SPOTREBA_VZORY = [r"DATUM SPOT[ŘR]EBY", r"datum spotřeby", r"SPLNĚNO", r"ZÁZNAM O PROVEDENÍ"]


def nacti(p: pathlib.Path):
    try:
        return p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def radky(s: str) -> int:
    """splitlines(), NE split('\\n') — soubor končící newline dává prázdný prvek
    navíc (naměřeno: 183 místo 182 u `ci.yml`; `AGENTS.md` to popisuje)."""
    return len(s.splitlines())


def klasifikuj(p: pathlib.Path, s: str):
    """Vrátí (druh, odkud) — `odkud` říká, ČÍM to bylo určeno, aby se dalo
    poznat, co je tvrzení dokumentu o sobě a co je odhad z názvu.

    ⚠ NAMĚŘENO PŘI PRVNÍM BĚHU: první verze brala druh z hlavičky jako
    DOSLOVNÝ TEXT — a vyšly z ní nesmysly typu
    „Co tenhle dokument JE:** sur (z hlavička)". Druh je KRÁTKÁ KATEGORIE,
    ne citát. Proto se v hlavičce hledá KLÍČOVÉ SLOVO, ne opisuje věta.
    """
    # 1. Co o sobě dokument tvrdí (hlavička „Co tenhle dokument JE").
    for v in HLAVICKA_VZORY:
        m = re.search(v, s[:4000])
        if not m:
            continue
        konec = len(s)
        for stop in ("\n\n", "\n"):
            i = s.find(stop, m.end())
            if i != -1:
                konec = min(konec, i)
                break
        veta = s[m.end():min(konec, m.end() + 200)]
        for vzor, druh in DEKLARACE:
            if re.search(vzor, veta, re.I):
                return druh, "hlavička"
        return "jiné (hlavička bez klíčového slova)", "hlavička"
    # 2. Z názvu souboru.
    for vzor, druh in VZORY_DRUHU:
        if re.search(vzor, p.name, re.I):
            return druh, "název"
    return "NEURČENO", "neurčeno"


def git_info():
    """{rel_cesta: (repo, iso_datum)} pro oba repy. `git log -1` na každý soubor
    by byl 200× subprocess — proto se použije jeden `ls-files` a jeden `log`."""
    info = {}
    for jmeno, repo in REPA.items():
        if not (repo / ".git").exists():
            continue
        try:
            r = subprocess.run([str(GIT), "-C", str(repo), "ls-files"],
                               capture_output=True, shell=True, timeout=120)
            soubory = r.stdout.decode("utf-8", "replace").splitlines()
        except Exception:                                        # noqa: BLE001
            soubory = []
        for rel in soubory:
            info[str((repo / rel).resolve()).lower()] = jmeno
        try:
            r = subprocess.run([str(GIT), "-C", str(repo), "log", "-1",
                                "--format=%cI", "--", "."],
                               capture_output=True, shell=True, timeout=120)
            info["__repo_datum__" + jmeno] = r.stdout.decode("utf-8", "replace").strip()
        except Exception:                                        # noqa: BLE001
            info["__repo_datum__" + jmeno] = ""
    return info


def git_datum(repo: pathlib.Path, rel: str) -> str:
    try:
        r = subprocess.run([str(GIT), "-C", str(repo), "log", "-1",
                            "--format=%cI", "--", rel],
                           capture_output=True, shell=True, timeout=60)
        return r.stdout.decode("utf-8", "replace").strip()
    except Exception:                                            # noqa: BLE001
        return ""


def zjisti_branny_seznam():
    """Které soubory brány otevírají — a JAK (ruční seznam vs. projití složky).

    Čte se ZDROJ brány, ne výstup: `kontrola-diakritiky.py` má 100+ cest
    v literálech, `g1` prochází složku. Rozdíl je podstatný — je to nález S27.
    """
    vysledek = {}
    for jmeno, cesta in BRANY.items():
        s = nacti(cesta)
        if s is None:
            vysledek[jmeno] = ("CHYBA: nelze přečíst", [])
            continue
        cesty = re.findall(r'"([^"\n]{3,120}\.(?:md|py|mjs|yml|json|txt))"', s)
        cesty += re.findall(r"r\"([^\"\n]{3,120})\"", s)
        cesty += re.findall(r'WS\s*/\s*"([^"]+)"', s)
        cesty += re.findall(r'"(WS[^"]*)"', s)
        vzory = re.findall(r'"\*\.(\w+)"', s)
        zpusob = "slozka" if ("glob(" in s and vzory) else "seznam"
        vysledek[jmeno] = (zpusob, cesty)
    return vysledek


def je_v_brane(cesta: pathlib.Path, brany):
    """Vrátí (rucni, slozka) — dvě RŮZNÉ věci, které se nesmí slít.

    ⚠ NAMĚŘENO PŘI PRVNÍM BĚHU TOHOHLE INVENTÁŘE (2. 10. 2026): první verze
    vracela jen „je v nějaké bráně" — a protože `g1-diakritika-novych.py`
    **prochází složku**, byl „v bráně" KAŽDÝ dokument v kořeni i v `_analyza`.
    Kategorie „sirotek" tím vyšla PRÁZDNÁ (0 z 97) — tedy přesně ta vada,
    před kterou varuje `overovani` §2.3: brána, která projde nad čímkoli,
    nerozliší nic. Přitom právě sirotci jsou to, co má audit najít.

    Rozlišení, které to spravuje:
      * **rucni** = soubor je v RUČNĚ VEDENÉM SEZNAMU brány. To je úmysl —
        někdo ho tam musel napsat, takže o dokumentu něco tvrdí.
      * **slozka** = brána ho vidí jen proto, že prochází složku. To je
        AUTOMATICKÉ pokrytí — o důležitosti dokumentu netvrdí NIC.
    """
    jmena = cesta.name
    relativni = str(cesta).replace(str(WS) + "\\", "").replace("\\", "/")
    rucni, slozka = [], []
    for jmeno, (zpusob, cesty) in brany.items():
        if jmeno == "g1-diakritika-novych.py" and cesta.suffix in (
                ".md", ".py", ".mjs", ".json", ".gd", ".txt", ".ps1"):
            if cesta.parent in (WS, WS / "_analyza", WS / "orchestra" / "tools"):
                slozka.append(jmeno)
                continue
        if jmeno == "kontrola-diakritiky.py" and cesta.name == "SKILL.md":
            slozka.append(jmeno)
            continue
        for c in cesty:
            c = c.replace("\\", "/").split("/")[-1]
            if c and (c == jmena or c == relativni):
                rucni.append(jmeno)
                break
    return (", ".join(sorted(set(rucni))) if rucni else "—",
            ", ".join(sorted(set(slozka))) if slozka else "—")


def main() -> int:
    argv = sys.argv[1:]
    json_cesta = WS / "_analyza" / "audit-inventar.json"
    if "--json" in argv:
        json_cesta = pathlib.Path(argv[argv.index("--json") + 1])

    # ── 1. Sebrat dokumenty ────────────────────────────────────────────────
    dokumenty = []
    for f in sorted(WS.glob("*.md")):
        dokumenty.append((f, "koren"))
    for f in sorted((WS / "_analyza").rglob("*.md")):
        if any(cast in VYLUCENE_SLOZKY for cast in f.parts):
            continue
        # Snapshot je KOPIE dokumentace, ne dokument (viz VYLUCENE_PREDPONY).
        if any(cast.startswith(VYLUCENE_PREDPONY) for cast in f.parts):
            continue
        dokumenty.append((f, "analyza" if f.parent == WS / "_analyza" else "analyza/podslozka"))
    for f in sorted(SKILLS.glob("*/SKILL.md")):
        dokumenty.append((f, "skill"))

    dokumenty = [(f, k) for f, k in dokumenty if f.name != VLASTNI]

    # ── 2. Načíst obsah (jednou) ───────────────────────────────────────────
    obsah = {}
    for f, _ in dokumenty:
        obsah[f] = nacti(f)

    jadro_texty = {}
    for j in JADRO:
        s = obsah.get(WS / j)
        jadro_texty[j] = s if s else ""

    # ── 3. Git ─────────────────────────────────────────────────────────────
    g = git_info()

    # ── 4. Brány ───────────────────────────────────────────────────────────
    brany = zjisti_branny_seznam()

    # ── 5. Zmínky ──────────────────────────────────────────────────────────
    def zminky(cil: pathlib.Path, zdroje):
        """Počet zmínek podle KMENE jména.

        ⚠ DVĚ PASTI NAMĚŘENÉ V PRVNÍ VERZI (obě dělaly falešný nález):
          * `SKILL.md` má kmen „SKILL" — pět znaků, takže se neměřil a KAŽDÝ
            skill vycházel jako „jádro:0", tedy jako sirotek. Přitom o
            `dsh-prostredi` se v jádru píše 19×. Klíčem u skillu je jméno
            SLOŽKY, ne souboru.
          * příliš krátké jméno dělá falešné nálezy („PLAN" je podřetězec
            kdečeho) → pod 6 znaků se neměří, a je to vidět jako „—".
        """
        kmen = cil.parent.name if cil.name == "SKILL.md" else cil.stem
        if len(kmen) < 6:
            return 0, []
        kdo = []
        for jm, s in zdroje:
            if not s or jm == cil.name:
                continue
            n = s.count(kmen)
            if n:
                kdo.append((jm, n))
        return sum(n for _, n in kdo), kdo

    zaznamy = []
    problemy = []

    for f, kategorie in dokumenty:
        s = obsah[f]
        z = {
            "cesta": str(f.relative_to(WS)) if WS in f.parents else str(f),
            "kategorie": kategorie,
        }

        # sloupec: velikost, řádků
        try:
            st = f.stat()
            z["bajtu"] = st.st_size
            z["mtime"] = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
        except OSError as e:
            z["bajtu"], z["mtime"] = None, "CHYBA: " + type(e).__name__
        z["radku"] = radky(s) if s is not None else "NEZMĚŘENO (nelze přečíst jako UTF-8)"

        # sloupec: druh
        if s is None:
            z["druh"], z["druh_odkud"] = "NEURČENO", "nelze přečíst"
        else:
            z["druh"], z["druh_odkud"] = klasifikuj(f, s)

        # sloupec: odkazy
        v_jadre, kdo_jadro = zminky(f, list(jadro_texty.items()))
        ostatni = [(str(ff.relative_to(WS)) if WS in ff.parents else str(ff), obsah[ff])
                   for ff, _ in dokumenty if ff != f]
        celkem_mimo, kdo_mimo = zminky(f, ostatni)
        z["odkazu_v_jadru"] = v_jadre
        z["odkazu_v_jadru_kdo"] = "; ".join("%s×%d" % (a, b) for a, b in kdo_jadro) or "—"
        z["odkazu_mimo_jadro"] = celkem_mimo
        z["odkazu_celkem"] = v_jadre + celkem_mimo

        # sloupec: brána
        rucni_br, slozka_br = je_v_brane(f, brany)
        z["otevira_brana"] = rucni_br
        z["kryto_projitim_slozky"] = slozka_br

        # sloupec: git
        klic = str(f.resolve()).lower()
        if klic in g:
            repo = g[klic]
            z["v_gitu"] = repo
            rel = str(f.resolve().relative_to(REPA[repo].resolve())).replace("\\", "/")
            z["zmenen"] = git_datum(REPA[repo], rel) or "NEZMĚŘENO (git log nic nevrátil)"
        else:
            z["v_gitu"] = "NE (mimo oba repy)"
            z["zmenen"] = z["mtime"] + " (mtime, mimo git)"

        # sloupec: hlavička
        if s is None:
            z["hlavicka"] = "NEZMĚŘENO"
        else:
            ma_hlavicku = any(re.search(v, s[:4000]) for v in HLAVICKA_VZORY)
            ma_spotrebu = any(re.search(v, s[:4000]) for v in SPOTREBA_VZORY)
            if kategorie == "skill":
                z["hlavicka"] = "neni-clanek (skill)"
            else:
                z["hlavicka"] = ("ANO" if ma_hlavicku else "NE") + (
                    " +spotřeba" if ma_spotrebu else "")

        # sloupec: záloha — hledá se v CELÉ relativní cestě, ne jen ve jméně:
        # `_analyza\g2-skilly-zaloha\dsh-prostredi.md` má zálohu ve SLOŽCE,
        # a první verze (testovala `f.name`) ho proto vedla mezi ŽIVÝMI.
        z["je_zaloha"] = bool(re.search(r"pred-|zaloha|zálo|snapshot|snímek",
                                        z["cesta"], re.I))
        # Fixtur a pracovních kopií (patch/, patch-test/) — nejsou to dokumenty,
        # ale ani smetí: jsou to vstupy testů. Patří do vlastní kategorie,
        # aby nezkreslovaly počty živých dokumentů.
        z["je_kopie"] = bool(re.search(r"(^|\\)(patch|patch-test|g2-skilly-zaloha)(\\|$)",
                                       z["cesta"], re.I))

        # sloupec: kategorie podle života (viz plán §1)
        # ⚠ „v bráně" se počítá JEN ruční seznam. Projití složky (`g1`) je
        # automatické pokrytí — kdyby se počítalo taky, sirotků by vyšlo 0
        # a kategorie by nic nerozlišovala (naměřeno v první verzi).
        z["kategorie_zivota"] = (
            "zaloha" if z["je_zaloha"] else
            "kopie" if z["je_kopie"] else
            "ziva" if (v_jadre > 0 or z["otevira_brana"] != "—") else
            "sirotek")

        zaznamy.append(z)

        # ── kontrola úplnosti: prázdný sloupec je VADA MĚŘENÍ ──────────────
        for sloupec in ("bajtu", "radku", "druh", "odkazu_v_jadru", "odkazu_celkem",
                        "otevira_brana", "kryto_projitim_slozky", "v_gitu", "zmenen",
                        "hlavicka", "je_zaloha", "je_kopie", "kategorie_zivota"):
            v = z.get(sloupec)
            if v is None or v == "":
                problemy.append("%s: sloupec '%s' je prázdný" % (z["cesta"], sloupec))

    # ── 6. Výstup ──────────────────────────────────────────────────────────
    zive = [z for z in zaznamy if z["kategorie_zivota"] == "ziva"]
    siroty = [z for z in zaznamy if z["kategorie_zivota"] == "sirotek"]
    zalohy = [z for z in zaznamy if z["kategorie_zivota"] == "zaloha"]
    kopie = [z for z in zaznamy if z["kategorie_zivota"] == "kopie"]

    print("=" * 96)
    print("AUDIT 1 — INVENTÁŘ DOKUMENTŮ (generovaný)")
    print("=" * 96)
    print("  zdrojů: %d .md + %d SKILL.md = %d dokumentů"
          % (len([1 for _, k in dokumenty if k != "skill"]),
             len([1 for _, k in dokumenty if k == "skill"]), len(zaznamy)))
    print()

    for titulek, skupina in (("ŽIVÉ (cituje jádro NEBO je v RUČNÍM seznamu brány)", zive),
                             ("SIROTCI (nikdo je v jádru necituje a v ručním seznamu žádné brány nejsou)", siroty),
                             ("ZÁLOHY A SNÍMKY (nechat, ale označit)", zalohy),
                             ("KOPIE A FIXTURY (vstupy testů — nejsou to dokumenty)", kopie)):
        print("-" * 96)
        print("  %s — %d" % (titulek, len(skupina)))
        print("-" * 96)
        if not skupina:
            print("      (žádný — a to je měřená nula, ne ticho)")
        for z in sorted(skupina, key=lambda x: -(x["bajtu"] or 0)):
            print("  %-52s %8s B  %5s ř.  jádro:%d  brána:%s"
                  % (z["cesta"][:52], z["bajtu"], z["radku"], z["odkazu_v_jadru"],
                     z["otevira_brana"][:22]))
            print("      druh: %-28s (z %s)   git: %s   hlavička: %s"
                  % (z["druh"][:28], z["druh_odkud"], z["v_gitu"][:34], z["hlavicka"]))
        print()

    print("-" * 96)
    print("  SOUHRN")
    print("-" * 96)
    print("  dokumentů celkem        : %d" % len(zaznamy))
    print("  živých / sirotků / záloh / kopií: %d / %d / %d / %d"
          % (len(zive), len(siroty), len(zalohy), len(kopie)))
    bez_hlavicky = [z for z in zaznamy if z["hlavicka"].startswith("NE")
                    and z["kategorie"] != "skill"]
    print("  bez hlavičky „Co tenhle dokument JE”: %d" % len(bez_hlavicky))
    print("  mimo git (oba repy)     : %d"
          % len([z for z in zaznamy if z["v_gitu"].startswith("NE")]))
    print("  druh NEURČENO           : %d"
          % len([z for z in zaznamy if z["druh"] == "NEURČENO"]))
    print()

    if problemy:
        print("  CHYBY MĚŘENÍ (prázdný sloupec = vada, ne nula):")
        for p in problemy:
            print("      " + p)
    else:
        print("  Žádný sloupec nezůstal prázdný (každý dokument má všech 11).")

    json_cesta.write_text(json.dumps({
        "generovano": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dokumentu": len(zaznamy),
        "zive": len(zive), "sirotci": len(siroty), "zalohy": len(zalohy),
        "kopie": len(kopie),
        "dokumenty": zaznamy,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("  JSON: %s" % json_cesta)

    return 1 if problemy else 0


if __name__ == "__main__":
    sys.exit(main())
