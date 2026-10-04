# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
"""Přeměří čísla, která tvrdí AGENTS.md — trvalá pravidla jsou taky měřidlo.

PROČ TO EXISTUJE
----------------
`AGENTS.md` je **autorita**, ze které vycházejí všechny session. A tvrdí
v sobě čísla („5 tabulek, 39 sloupců", „161 souborů, 2 002 nálezů", …).

Naměřeno 2. 10. 2026: **jedno z těch čísel bylo špatné od začátku** — u
`schema.sql` tvrdil **32 sloupců**, správně je **39**, a schéma se přitom
od 30. 9. nezměnilo. Přes šest session si toho nikdo nevšiml, protože se
**nečetlo proti zdroji**. (Nález N9.)

Chyba v autoritě se neprojeví jako chyba — projeví se jako **důsledek na
pěti jiných místech**. Proto se práh „trvalá pravidla" musí **periodicky
remeřit**, stejně jako cokoli jiného.

JAK SE TO POUŽÍVÁ
-----------------
    python _analyza\\ag-over-cisla.py

Vypíše u každého čísla: co tvrdí `AGENTS.md`, co je naměřeno, a verdikt.
Nenulový kód vrací, když se něco rozešlo (`--gate`), jinak jen reportuje.

POZOR na dvě věci, které tu jsou schválně:
  1. **Historická čísla se nepřepisují.** Např. „10 míst s českým
     identifikátorem" bylo správně **ve svém čase**; dnes je 0, protože
     Z1–Z8 je přejmenovaly. Rozdíl je **čas**, ne nepravda — a musí být
     vidět jako „zastaralé (opraveno)", ne jako „CHYBA".
  2. **Kontrolní vzorky.** Skript měří i čísla, u kterých VÍM, že sedí.
     Kdyby hlásil chybu u všech, je rozbitý on, ne dokument.
"""

import pathlib
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(_STANICE)
AGENTS = WS / "AGENTS.md"
# OD 4. 10. 2026: obecné části trvalých pravidel bydlí v DSH_HOME (mimo
# workspace). Tvrzení se proto hledají ve DVOU dokumentech — jinak by skript
# po přesunu hlásil „NENAŠEL JSEM TVRZENÍ" u pravidla, které je v pořádku,
# jen se přestěhovalo. (Přesně ta vada, kterou níž řeší `nenalezeno`.)
OBECNA = pathlib.Path(r"C:\Users\Ssevc\.dsh\AGENTS.md")
ORCHESTRA = WS
GIT = str(ORCHESTRA / "tools" / "git.cmd")

if not AGENTS.is_file():
    print(f"CHYBA: {AGENTS} neexistuje")
    sys.exit(2)
if not OBECNA.is_file():
    # Chybějící obecná pravidla NEJSOU „nic k měření" — jsou to pravidla, která
    # má dostat každá session. Když soubor zmizí, musí to být vidět.
    print(f"CHYBA: {OBECNA} neexistuje (obecná pravidla stanice)")
    sys.exit(2)

text = AGENTS.read_text(encoding="utf-8")
text_obecna = OBECNA.read_text(encoding="utf-8")
DOKUMENTY = ((AGENTS, text), (OBECNA, text_obecna))
JINDE: list[str] = []      # tvrzení nalezená mimo projektový AGENTS.md


# ── měření ───────────────────────────────────────────────────────────────────
def schema_sloupce() -> tuple[int, int, int]:
    """(tabulky, sloupce, české názvy sloupců) v conductor/schema.sql."""
    sql = (ORCHESTRA / "conductor" / "schema.sql").read_text(encoding="utf-8")
    sql = re.sub(r"--[^\n]*", "", sql)
    tabs = re.findall(r"CREATE TABLE IF NOT EXISTS\s+(\w+)\s*\((.*?)\n\);", sql, re.S)
    celkem, ceske = 0, 0
    for _, body in tabs:
        for l in body.split("\n"):
            l = l.strip()
            if not l or l.startswith(")"):
                continue
            if l.upper().startswith(("PRIMARY", "FOREIGN", "UNIQUE", "CHECK", "CONSTRAINT")):
                continue
            nazev = l.split()[0]
            celkem += 1
            if any(ord(c) > 127 for c in nazev):
                ceske += 1
    return len(tabs), celkem, ceske


def md_diakritika() -> tuple[int, int]:
    """(znaky s diakritikou, všechny znaky) v .md souborech orchestra."""
    diak, vse = 0, 0
    for p in ORCHESTRA.rglob("*.md"):
        if "node_modules" in str(p):
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except Exception:
            continue
        vse += len(t)
        diak += sum(1 for c in t if ord(c) > 127)
    return diak, vse


def nonascii_nazvy() -> tuple[int, int]:
    """(soubory s non-ASCII v názvu, všechny soubory) v orchestra."""
    vse = nonascii = 0
    for p in ORCHESTRA.rglob("*"):
        if "node_modules" in str(p) or ".git" in p.parts:
            continue
        if p.is_file():
            vse += 1
            if any(ord(c) > 127 for c in p.name):
                nonascii += 1
    return nonascii, vse


def radku_v_blobu(cesta: str) -> int | None:
    """Počet řádků blobu v HEAD (autorita je blob, ne disk).

    POZOR: `ci.yml` je v `repo/.github/workflows/`, NE v `.github/workflows/`
    (šablona je `orchestra/repo/`). Kdo hledá v kořeni orchestra, **nenajde ho**
    a dostane `None` — což vypadá jako „nepodařilo se změřit", ale je to
    špatná cesta. Naměřeno při psaní tohohle skriptu.
    """
    try:
        r = subprocess.run([GIT, "-C", str(ORCHESTRA), "show", f"HEAD:{cesta}"],
                           capture_output=True, shell=True)
        if r.returncode != 0:
            return None
        # POUŽIJ `splitlines()`, NE `split("\n")`!
        # Naměřeno 2. 10. 2026 (při psaní tohohle skriptu): `split("\n")` dalo
        # **183** u souboru, který má **182** řádků — protože končí newline
        # a `split` vyrobí na konci prázdný prvek. Skript pak hlásil, že se
        # AGENTS.md rozešel se zdrojem, a přitom **se rozešel skript**.
        # Je to PŘESNĚ past, před kterou `AGENTS.md` varuje u
        # `Measure-Object -Line` (166 vs 182) — a spadl jsem do ní znovu.
        return len(r.stdout.decode("utf-8", "replace").splitlines())
    except Exception:
        return None


# ── PARSOVÁNÍ TVRZENÍ Z AGENTS.md ────────────────────────────────────────────
# ⚠ TADY BYLA VÁŽNÁ VADA PRVNÍ VERZE (odhalil ji až MUTAČNÍ TEST):
# čísla byla v seznamu NAPSANÁ NAPEVNO, takže skript měřil zdroj a porovnával
# ho **sám se sebou** — o `AGENTS.md` vůbec nešel. Když jsem do dokumentu
# vrátil vadu (39 → 32), skript **pořád skončil `exit 0`**.
# Je to přesně past S27: „brána je zelená nad dokumentem, který nikdy
# neotevřela." **Tvrz… měřeno musí být PŘEČTENO Z DOKUMENTU**, ne opsáno.
def tvrzi(vzor: str, skupina: int = 1, prevod=str) -> str | None:
    """Vytáhne tvrzené číslo z DOKUMENTŮ S PRAVIDLY. None = tvrzení se nenašlo.

    Hledá v projektovém `AGENTS.md` i v obecných pravidlech (DSH_HOME) a když
    najde jinde než v projektu, zapíše to do `JINDE` — aby bylo vidět, ODKUD
    tvrzení je. Číslo bez dokumentu se nedá ověřit ani vyvrátit.
    """
    for cesta, t in DOKUMENTY:
        m = re.search(vzor, t)
        if m:
            if cesta != AGENTS:
                JINDE.append(cesta.name)
            return prevod(m.group(skupina).replace("\u00a0", " ").replace(" ", ""))
    return None


def jako_int(s: str) -> int:
    return int(s)


# (popis, naměřená hodnota, tvrzené číslo PŘEČTENÉ Z DOKUMENTU, detail, historické?)
tabulky, sloupce, ceske = schema_sloupce()
diak, vse_znaku = md_diakritika()
nonascii, vse_souboru = nonascii_nazvy()
radky_ci = radku_v_blobu("repo/.github/workflows/ci.yml")

KONTROLY = [
    ("5 tabulek D1", tabulky,
     tvrzi(r"(\d+) tabulek, \*\*\d+ sloupců", 1, jako_int),
     "tabulky v conductor/schema.sql", False),
    # ⚠ POPISEK OPRAVEN 2. 10. 2026 (Úkol 1 zadání `ZADANI-DOKONCENI-AUDITU.md`,
    # nález R1 — „popisek a hodnota si odporují a brána hlásí OK"):
    # tady stálo `"39 sloupců D1"` — tedy číslo NAPSANÉ NAPEVNO v popisku,
    # které zestaralo (dnes je 40). Výstup pak tvrdil `OK 39 sloupců D1 = 40`,
    # což je spor PŘÍMO V JEDNOM ŘÁDKU. Popisek proto **nesmí nést hodnotu,
    # kterou sám nijak neověřuje** — naměřené číslo se tiskne za `=` a tvrzené
    # se čte z dokumentu (`tvrzi(...)` níž). Kdo sem číslo vrátí, vrátí i tu vadu.
    ("sloupců D1", sloupce,
     tvrzi(r"\d+ tabulek, \*\*(\d+) sloupců", 1, jako_int),
     "sloupce v conductor/schema.sql", False),
    ("českých sloupců 0", ceske,
     tvrzi(r"sloupců, českých (\d+)\*\*", 1, jako_int),
     "non-ASCII názvy sloupců", False),
    ("non-ASCII v názvu: 0", nonascii,
     tvrzi(r"(\d+) souborů, non-ASCII v názvu: \*\*(\d+)\*\*", 2, jako_int),
     f"z {vse_souboru} souborů orchestra", False),
    ("ci.yml 182 řádků", radky_ci,
     # POZOR: věta se v AGENTS.md ZALAMUJE mezi „**166**," a „správně je" —
     # vzor proto musí počítat s newline a odsazením (`\s+`), ne jen s mezerou.
     # Naměřeno při psaní: s `, ` místo `,\s+` se tvrzení „nenašlo" a kontrola
     # hlásila slepé místo, které přitom v dokumentu bylo.
     tvrzi(r"u `ci\.yml` hlásil \*\*\d+\*\*,\s+správně je \*\*(\d+)\*\*", 1, jako_int),
     "blob v HEAD (ne disk!) — soubor je v repo/.github/workflows/", False),
    # ── historická (ve svém čase správná) ────────────────────────────────────
    ("10 míst s českým identifikátorem", 0,
     tvrzi(r"IDENTIFIKÁTOR \| \*\*(\d+) míst\*\*", 1, jako_int),
     "STAV PO Z1–Z8 — bylo 10, dnes 0 (opraveno)", True),
    ("znaků v .md orchestra (44 781)", vse_znaku,
     tvrzi(r"znaků ze ([\d ]+) =", 1, jako_int),
     "AGENTS.md měřeno 1. 10.; .md se pak commitovaly (3a2e691) → text narostl. "
     "POMĚR zůstal (5,7 % vs 5,8 %) = týž jev, jiný čas", True),
]

print("=" * 78)
print("PŘEMĚŘENÍ ČÍSEL V TRVALÝCH PRAVIDLECH — pravidla jsou taky měřidlo")
print("=" * 78)
print(f"  dokumenty: {AGENTS.name} ({len(text)} znaků) + "
      f"{OBECNA.name} v DSH_HOME ({len(text_obecna)} znaků)")
print()

rozeslo, historicka, ok = [], [], 0
nenalezeno = []
for popis, namereno, tvrzeno, detail, je_historicke in KONTROLY:
    if tvrzeno is None:
        # TVRZENÍ SE V DOKUMENTU NENAŠLO. To NENÍ „prošlo" — je to slepé
        # místo: buď se přeformuloval text, nebo kontrola měří něco jiného.
        print(f"  ?? NENAŠEL JSEM TVRZENÍ  {popis}")
        print(f"            → hledal jsem ho v {AGENTS.name}, ale text se změnil")
        nenalezeno.append(popis)
        continue
    if namereno is None:
        print(f"  ?  NEPODAŘILO SE ZMĚŘIT     {popis} ({detail})")
        continue
    if namereno == tvrzeno:
        print(f"  OK        {popis:34} = {namereno}")
        ok += 1
    elif je_historicke:
        print(f"  HISTOR.   {popis:34} tvrdí {tvrzeno}, dnes {namereno}")
        print(f"            → {detail}")
        historicka.append(popis)
    else:
        print(f"  ✗ ROZEŠLO SE  {popis:30} tvrdí {tvrzeno}, naměřeno {namereno}")
        print(f"            → {detail}")
        rozeslo.append(popis)

# Diakritika se hlásí zvlášť — je to poměr, ne přesné číslo.
if vse_znaku:
    procento = 100.0 * diak / vse_znaku
    print(f"  INFO      diakritika v .md orchestra: {diak} z {vse_znaku} "
          f"= {procento:.1f} %")

print()
print(f"  v pořádku: {ok} | historická (ne chyba): {len(historicka)} | "
      f"ROZEŠLO SE: {len(rozeslo)} | NENAŠLA SE TVRZENÍ: {len(nenalezeno)}")
if JINDE:
    # Vynechaný vstup musí být VIDĚT: tvrzení, která už nejsou v projektu,
    # se čtou z obecných pravidel — a to je jiný dokument, jiný vlastník.
    print(f"  INFO: {len(JINDE)} tvrzení se našlo v OBECNÝCH pravidlech "
          f"({', '.join(sorted(set(JINDE)))}) — od 4. 10. 2026 jsou mimo projekt")
print()

if nenalezeno:
    print("ZÁVĚR: některé tvrzení se v dokumentu nenašlo — kontrola je slepá na")
    print("místech, která si myslí, že měří. To je stejná vada jako zelená brána")
    print("nad neotevřeným souborem (S27). Opravit vzory, ne dokument.")
    sys.exit(1)

if rozeslo:
    print("ZÁVĚR: číslo v TRVALÝCH PRAVIDLECH se rozešlo se zdrojem.")
    print("To je dražší než chyba v běžném dokumentu — podle AGENTS.md se")
    print("rozhoduje ve všech session. Opravit a zapsat, čím se to naměřilo.")
    sys.exit(1)

print("ZÁVĚR: čísla v AGENTS.md odpovídají zdroji.")
print("(Historická čísla jsou ve svém čase správná — nepřepisovat, jen označit.)")
sys.exit(0)
