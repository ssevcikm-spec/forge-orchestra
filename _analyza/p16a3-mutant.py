#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Kontrola struktury STANICE a obou repů — po přesunu na `E:` (P13c).

PROČ BYL PŘEPSANÝ (nález H50, 4. 10. 2026)
------------------------------------------
Původní verze měla **pevnou cestu na starý kořen**:
`W = r"C:\Users\Ssevc\Local-Deepseek"` a očekávala 9 sourozeneckých složek
staré stanice (`orchestra`, `games`, `games/uo-shadows`, …). Po přesunu na `E:`
hlásila **6× CHYBI** — a protože ji **nic nespouštělo**, nikdo to neviděl
(předpovězeno v `HANDOFF.md` §2.6 jako N8, proměřeno až ověřením přesunu).

Nebyla to ale vada dat: **kontrolovala strukturu, která už neexistuje.**
Rozhodnutí (zadání, Úkol C) je proto **PŘEPSAT na dnešní strukturu**, ne
archivovat — dnešní struktura je jiná (dva repy + kořen stanice), a to je právě
to, co má smysl kontrolovat.

CO KONTROLUJE DNES
------------------
  1. **kořen STANICE** — složky a dokumenty, které na něm mají být, a co na něm
     být NEMÁ (`gameforge`, `uo-sandbox`, `uo-sandbox-repo`).
     Cesta se dá přebít proměnnou `FORGE_STANICE`.
     **⚠ OPRAVENO 5. 10. 2026 (H72, H73) — seznam se ODVOZUJE z `AGENTS.md`.**
     Do té doby tu stály dva RUČNÍ literály (`DOKUMENTY_STANICE` 6,
     `SLOZKY_STANICE` 5), ačkoli komentář nad nimi tvrdil, že se **čtou
     z `AGENTS.md`**; se seznamem v `AGENTS.md` se **neshodovaly** (**7 dokumentů**
     brána nehlídala, u složek rozdíl na **4 místech**) a **úbytek pokrytí nikdo
     nehlásil** (mutace `DOKUMENTY_STANICE = []` → `exit 0`).
     Dnes se seznam čte **z dokumentu** (řádek „dokumenty STANICE" / „nástroje
     stanice", buňka s nejvíc zpětnými apostrofy), vzory (`token-saving-*.md`)
     se **rozvinou** a **cokoli, co se přečíst nedá, je CHYBA** — ne ticho.
     Co je na disku a v `AGENTS.md` **není vyjmenované**, se **vypíše jako
     poznámka** (aby úbytek pokrytí nebyl tichý).
  2. **repo orchestra** (`<tento soubor>/..`) — klíčové soubory na SVÝCH dnešních
     cestách + platnost JSON (roadmapa šablony, providers.json).
  3. **repo hry** (`<repo orchestra>/../uo-shadows` — SOUROZENEC, ne potomek) —
     klíčové soubory, platnost `roadmap.json` a `forge.json`, `git` stav.
  4. **kódování dokumentů** — že jsou platné UTF-8 (čte se BAJT po BAJTU;
     `Get-Content` bez `-Encoding utf8` rozsype češtinu a vypadá to jako vada
     souboru, skill `dsh-prostredi` §2b). **⚠ OPRAVENO 5. 10. 2026 (H73):**
     kontroly z §5, §6 a §7 šly **mimo čítač** — započítaly se, **jen když
     spadly** (naměřeno: `49 → 50`). Dnes se počítají **vždy**, takže
     `ZMĚŘENO: N kontrol` je **počet OPRAVDU provedených kontrol**, ne počet
     těch, které volají `zkontroluj`.

Návratový kód: 0 = vše na svém místě | 1 = chybí / rozbité (vypíše se co).
„Nezměřeno" není zelená: chybějící složka se hlásí jako CHYBI, ne jako ticho.

Použití:  python tools\verify-setup.py
"""

import json
import os
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── CESTY SE ODVOZUJÍ (P8) ───────────────────────────────────────────────────
# Repo orchestra = `tools/..`. Hra je SOUROZENEC repa (přesun na E:, 4. 10. 2026).
REPO = pathlib.Path(__file__).resolve().parents[1]
HRA = REPO.parent / "uo-shadows"
# Kořen stanice je JINÝ DISK, takže se odvodit nedá — bere se z prostředí,
# s dokumentovanou výchozí hodnotou (a vždycky se VYPÍŠE, aby bylo vidět, co
# se kontrolovalo).
STANICE = pathlib.Path(os.environ.get("FORGE_STANICE", r"C:\Users\Ssevc\Local-Deepseek"))
GIT = REPO / "tools" / "git.cmd"

chyb = 0
kontrol = 0


def zkontroluj(popis: str, ok: bool, detail: str = "") -> None:
    global chyb, kontrol
    kontrol += 0 if ok else 1
    if not ok:
        chyb += 1
    print(f"  {'OK   ' if ok else 'CHYBI'} {popis}")
    if detail and not ok:
        print(f"        {detail}")


def soubor(p: pathlib.Path, popis: str = "") -> None:
    zkontroluj(popis or str(p), p.is_file(),
               f"hledáno na: {p}")


def slozka(p: pathlib.Path, popis: str = "") -> None:
    zkontroluj(popis or str(p), p.is_dir(), f"hledáno na: {p}")


print("=" * 78)
print("KONTROLA STRUKTURY — stanice + orchestra + hra")
print("=" * 78)
print(f"  STANICE = {STANICE}   (lze přebít proměnnou FORGE_STANICE)")
print(f"  REPO    = {REPO}")
print(f"  HRA     = {HRA}   (sourozenec repa)")
print()

# ── 1) KOŘEN STANICE ─────────────────────────────────────────────────────────
print("=== 1) kořen STANICE: co tam má být ===")
if not STANICE.is_dir():
    print(f"  CHYBA: kořen stanice {STANICE} neexistuje — dál se nedá měřit.")
    print("         (Když je stanice jinde, nastav FORGE_STANICE.)")
    sys.exit(1)

# Dokumenty stanice = to, co si nechala stanice (D6). Píše se do `AGENTS.md`
# v kořeni stanice — seznam se proto čte z něj, ne z ruky (jinak by zastaral).
#
# ⚠ NÁLEZ H72 (5. 10. 2026, P14): tenhle komentář tu stál i dřív — ale POD NÍM
# byly dva RUČNÍ literály (`DOKUMENTY_STANICE` 6 jmen, `SLOZKY_STANICE` 5), které
# se s `AGENTS.md` **neshodovaly** (7 dokumentů brána nehlídala; u složek rozdíl
# na 4 místech). A **úbytek pokrytí nikdo nehlásil**: mutace `DOKUMENTY_STANICE
# = []` dala `exit 0` a jen o pár kontrol míň. Komentář nebyl lež — byl to
# **záměr, který se nikdy nenaplnil** (`overovani` §7.10).
# Od 5. 10. 2026 se seznam **skutečně čte z dokumentu** — a co přečíst nejde,
# je **CHYBA**, ne ticho.
def _bunky(radek: str) -> list[str]:
    """Buňky řádku markdownové tabulky (bez prázdných)."""
    return [b.strip() for b in radek.split("|") if b.strip()]


def _bunka_se_seznamem(radky: list[str], popis: str) -> tuple[str, list[str]]:
    """Vrátí (řádek, položky v `` `…` ``) pro řádek tabulky obsahující `popis`.

    Bere buňku s **nejvíc položkami v `` `…` ``** — u „dokumenty STANICE" je to
    poslední buňka (12), u „nástroje stanice" prostřední (5). Na pořadí se
    nehádá (`overovani` §10.1: ptej se, KTERÝ výskyt vzor trefí).

    **⚠ Proč je tu podmínka „aspoň 2 položky":** prostřední buňka řádku
    „dokumenty STANICE" (`tento koren (`*.md`)`) má taky zpětný apostrof — a když
    je seznam vyprázdněný, stala by se „vítězem" a `*.md` by se tvářil jako
    deklarace. To je přesně tichý úbytek pokrytí (H72). Seznam má vždy **víc
    než jednu** položku; jednočlenná buňka je popis místa, ne seznam.
    Dvojznačnost i krátká buňka proto vracejí **prázdný seznam** = CHYBA.
    """
    radek = next((l for l in radky if popis in l), "")
    if not radek:
        return "", []
    bunky = _bunky(radek)
    if not bunky:
        return radek, []
    polozky = [re.findall(r"`([^`]+)`", b) for b in bunky]
    maxima = max(len(p) for p in polozky)
    if maxima < 2 or [len(p) for p in polozky].count(maxima) > 1:
        return radek, []
    return radek, polozky[[len(p) for p in polozky].index(maxima)]


def _rozvin(polozky: list[str]) -> tuple[list[str], list[str]]:
    """Rozvine vzory (`token-saving-*.md`) proti obsahu stanice.

    Vrací `(jména, vzory_bez_shody)`. Vzor, který nic netrefí, NENÍ ticho —
    je to **zestárlá deklarace** a patří do `chyb`.
    """
    jmena: list[str] = []
    prazdne: list[str] = []
    for polozka in polozky:
        kandidat = polozka.strip().rstrip("\\/")
        if not kandidat:
            continue
        if "*" in kandidat or "?" in kandidat:
            nalezeno = sorted(p.name for p in STANICE.glob(kandidat) if p.is_file())
            if not nalezeno:
                prazdne.append(kandidat)
            jmena += nalezeno
        else:
            jmena.append(kandidat)
    return jmena, prazdne


AGENTS_STANICE = STANICE / "AGENTS.md"
try:
    _agents_radky = AGENTS_STANICE.read_text(encoding="utf-8").splitlines()
except Exception as e:                                      # noqa: BLE001
    print(f"  CHYBA: seznam nejde odvodit — `{AGENTS_STANICE}` "
          f"({type(e).__name__}: {e})")
    print("         Seznam dokumentů a nástrojů stanice je DEKLAROVANÝ tam.")
    sys.exit(1)

_radek_dok, _polozky_dok = _bunka_se_seznamem(_agents_radky, "dokumenty STANICE")
_radek_slo, _polozky_slo = _bunka_se_seznamem(_agents_radky, "nástroje stanice")
DOKUMENTY_STANICE, _prazdne_dok = _rozvin(_polozky_dok)
SLOZKY_STANICE, _prazdne_slo = _rozvin(_polozky_slo)

# Kontrola ODVOZENÍ se počítá taky — jinak by „seznam se čte z dokumentu"
# mohlo tiše přestat platit a čítač by to neukázal.
zkontroluj("`AGENTS.md` stanice: řádek „dokumenty STANICE“ se seznamem",
           bool(_radek_dok) and bool(_polozky_dok),
           "řádek nenalezen, nebo v něm není ani jedna položka v `…`")
zkontroluj("`AGENTS.md` stanice: řádek „nástroje stanice“ se seznamem",
           bool(_radek_slo) and bool(_polozky_slo),
           "řádek nenalezen, nebo v něm není ani jedna položka v `…`")
zkontroluj(f"vzory v dokumentech se rozvinuly ({len(DOKUMENTY_STANICE)} jmen)",
           not _prazdne_dok, "vzor bez souboru: " + ", ".join(_prazdne_dok))
zkontroluj(f"vzory v nástrojích se rozvinuly ({len(SLOZKY_STANICE)} jmen)",
           not _prazdne_slo, "vzor bez souboru: " + ", ".join(_prazdne_slo))

print(f"  seznam ODVOZEN z {AGENTS_STANICE}:")
print(f"    dokumenty ({len(DOKUMENTY_STANICE)}): {', '.join(DOKUMENTY_STANICE)}")
print(f"    nástroje  ({len(SLOZKY_STANICE)}): {', '.join(SLOZKY_STANICE)}")

for f in DOKUMENTY_STANICE:
    soubor(STANICE / f, f"stanice/{f}")

# Složky, které stanici zůstaly (nástroje stanice, ne projektu).
for d in SLOZKY_STANICE:
    slozka(STANICE / d, f"stanice/{d}/")

# Co je na disku a `AGENTS.md` to NEVYJMENOVÁVÁ → POZNÁMKA (ne vada).
# Bez tohohle by „úbytek pokrytí" (přesně vada H72) zůstal tichý: brána by
# hlásila zelenou nad menším světem, než jaký existuje.
try:
    _na_disku_dok = sorted(p.name for p in STANICE.glob("*.md") if p.is_file())
    _na_disku_slo = sorted(p.name for p in STANICE.iterdir() if p.is_dir())
except OSError as e:                                        # noqa: BLE001
    _na_disku_dok, _na_disku_slo = [], []
    print(f"  POZN  obsah kořene stanice nejde vypsat ({type(e).__name__}: {e})")
_nedeklarovane_dok = [f for f in _na_disku_dok if f not in DOKUMENTY_STANICE]
_nedeklarovane_slo = [d for d in _na_disku_slo if d not in SLOZKY_STANICE]
print(f"  POZN  na disku, ale v `AGENTS.md` NEVYJMENOVANÉ: "
      f"dokumentů {len(_nedeklarovane_dok)}, složek {len(_nedeklarovane_slo)}")
if _nedeklarovane_dok:
    print(f"        dokumenty: {', '.join(_nedeklarovane_dok)}")
if _nedeklarovane_slo:
    print(f"        složky:    {', '.join(_nedeklarovane_slo)}")
print("        (poznámka, ne vada: deklarace je v `AGENTS.md`; tohle jen říká,")
print("         co tam vyjmenované NENÍ — aby úbytek pokrytí nebyl tichý)")

print()
print("=== 2) co na stanici být NEMÁ (smazané projekty) ===")
# POZOR: `forge-quest` tu NEBYL nikdy a je to ŽIVÝ repozitář na GitHubu —
# kontrolovat ho jako „má zmizet" znamenalo nutit mazat živý projekt.
for k in ["gameforge", "uo-sandbox", "uo-sandbox-repo"]:
    zkontroluj(f"smazané: {k}", not (STANICE / k).exists(),
               f"STÁLE EXISTUJE: {STANICE / k}")
print("  (poznámka: repo `forge-quest` na GitHubu je ŽIVÉ — není to smazaná složka)")

# ── 3) REPO ORCHESTRA ────────────────────────────────────────────────────────
print()
print("=== 3) repo orchestra: klíčové soubory ===")
ORCH_SOUBORY = [
    "AGENTS.md", "README.md", "HANDOFF.md", "KRONIKA-PROJEKTU.md",
    "NEXT-SESSION-INSTRUKCE.md",
    "conductor/src/index.ts", "conductor/wrangler.toml", "conductor/schema.sql",
    "conductor/tsconfig.json",
    "repo/.forge/providers.json", "repo/.forge/roadmap.json",
    "repo/.forge/check-schema.py",
    "tools/git.cmd", "tools/status.mjs", "tools/validate-all.mjs",
    "tools/over-dokumentaci.py", "tools/kontrola-diakritiky.py",
    "_analyza/g3-brany.py", "_analyza/hl-rizika-jazyka.py",
]
for f in ORCH_SOUBORY:
    soubor(REPO / f, f"orchestra/{f}")

# Tajemství: přítomnost se hlásí, ale OBSAH se nikdy nevypisuje.
for f in [".env", ".secrets/github_pat.txt"]:
    zkontroluj(f"orchestra/{f} (tajemství — obsah se nevypisuje)",
               (REPO / f).is_file(), f"hledáno na: {REPO / f}")

# ── 4) HRA ───────────────────────────────────────────────────────────────────
print()
print("=== 4) hra (sourozenec repa): klíčové soubory ===")
HRA_SOUBORY = [
    "project.godot", "main.tscn", "CONVENTIONS.md", "forge.json", "hra.cmd",
    ".github/workflows/agent.yml", ".github/workflows/ci.yml",
    ".github/workflows/release.yml",
    ".forge/roadmap.json", ".forge/providers.json", ".forge/pick-provider.mjs",
    ".forge/vision-profile.json", ".forge/node/worker.mjs",
    "assets/spec.json",
]
for f in HRA_SOUBORY:
    soubor(HRA / f, f"hra/{f}")

# ── 5) PLATNOST JSON ─────────────────────────────────────────────────────────
print()
print("=== 5) platnost JSON ===")
JSONY = [
    (REPO / "repo" / ".forge" / "providers.json", "orchestra/repo/.forge/providers.json"),
    (REPO / "repo" / ".forge" / "roadmap.json", "orchestra/repo/.forge/roadmap.json (šablona)"),
    (HRA / ".forge" / "roadmap.json", "hra/.forge/roadmap.json"),
    (HRA / "forge.json", "hra/forge.json"),
    (HRA / "assets" / "spec.json", "hra/assets/spec.json"),
]
for p, popis in JSONY:
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:                                  # noqa: BLE001
        zkontroluj(f"{popis} je platný JSON", False, f"{type(e).__name__}: {e}")
        continue
    # ⚠ NÁLEZ H73: úspěch se MUSÍ počítat taky. Do 5. 10. 2026 se §5 a §6
    # ptaly jen na chybu (`zkontroluj(False)`), kdežto úspěch se jen vypsal —
    # takže `ZMĚŘENO: N kontrol` byl počet těch, které volají `zkontroluj`,
    # a **úbytek pokrytí** (když kontrola zmizela) nikdo neviděl.
    zkontroluj(f"{popis} je platný JSON", True)
    if isinstance(d, dict) and "grains" in d:
        g = d["grains"]
        print(f"        {len(g)} granulí, "
              f"{sum(1 for x in g if x.get('done'))} hotových, "
              f"{sum(1 for x in g if x.get('model') == 'strong')} strong")

# ── 6) DOKUMENTY JSOU PLATNÉ UTF-8 ───────────────────────────────────────────
print()
print("=== 6) dokumenty jsou platné UTF-8 (čte se bajtově) ===")
DOKUMENTY = [
    (STANICE / "README.md", "stanice/README.md"),
    (STANICE / "AGENTS.md", "stanice/AGENTS.md"),
    (REPO / "AGENTS.md", "orchestra/AGENTS.md"),
    (REPO / "HANDOFF.md", "orchestra/HANDOFF.md"),
    (REPO / "KRONIKA-PROJEKTU.md", "orchestra/KRONIKA-PROJEKTU.md"),
    (HRA / "AGENTS.md", "hra/AGENTS.md"),
    (HRA / "CONVENTIONS.md", "hra/CONVENTIONS.md"),
    (pathlib.Path(os.path.expanduser("~")) / ".dsh" / "skills" / "orchestra" / "SKILL.md",
     "~/.dsh/skills/orchestra/SKILL.md"),
]
for p, popis in DOKUMENTY:
    try:
        p.read_bytes().decode("utf-8")
    except UnicodeDecodeError as e:
        zkontroluj(f"{popis} je platné UTF-8", False, f"UnicodeDecodeError: {e}")
        continue
    except Exception as e:                                  # noqa: BLE001
        zkontroluj(f"{popis} jde přečíst", False, f"{type(e).__name__}: {e}")
        continue
    # ⚠ H73: úspěšná kontrola se počítá TAKY — jinak se §6 objeví v čítači jen
    # ve chvíli, kdy spadne (naměřeno před opravou: 49 → 50).
    zkontroluj(f"{popis} je platné UTF-8", True)

# ── 7) GIT STAV OBOU REPŮ ────────────────────────────────────────────────────
print()
print("=== 7) git stav obou repů ===")
for popis, cesta in [("orchestra", REPO), ("hra", HRA)]:
    if not (cesta / ".git").exists():
        zkontroluj(f"{popis}: je to git repo", False, f"{cesta / '.git'} neexistuje")
        continue
    r = subprocess.run([str(GIT), "-C", str(cesta), "status", "--porcelain"],
                       capture_output=True, shell=True)
    zmeny = [l for l in (r.stdout or b"").decode("utf-8", "replace").splitlines() if l.strip()]
    r2 = subprocess.run([str(GIT), "-C", str(cesta), "rev-list", "--count", "origin/main..HEAD"],
                        capture_output=True, shell=True)
    nepushnuto = (r2.stdout or b"").decode("utf-8", "replace").strip() or "?"
    # ⚠ H73: i tahle kontrola se počítá (dřív se jen vypsala).
    zkontroluj(f"{popis}: git stav jde přečíst", True,
               f"git status v {cesta} nevrátil odpověď")
    print(f"        {len(zmeny)} necommitnutých změn, "
          f"origin/main..HEAD = {nepushnuto}   (nic se nepushuje)")

print()
# Čítač se vypisuje VŽDY — `exit 0` bez počtu kontrol je ticho, ne zelená
# (a `g3-brany.py` ho čte jako „kolik toho brána otevřela").
print(f"ZMĚŘENO: {kontrol} kontrol, {chyb} chyb")
if chyb:
    print(f"NALEZENO {chyb} PROBLÉMŮ (viz CHYBI výš)")
    sys.exit(1)
print("VŠE OK — struktura stanice i obou repů odpovídá dnešnímu uspořádání.")
sys.exit(0)
