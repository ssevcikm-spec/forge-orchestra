# -*- coding: utf-8 -*-
r"""P19 — Úkol B (H93 a co k tomu přibylo): CO všechno NA32 počítá jako ŽIVÉ.

ZADÁNÍ: „Přeměř to sám: spočítej .py v orchestra s vylučovacím seznamem NA32
a bez snapshotů. Hledej SOUBOR PO SOUBORU, ne jen součty."

PROČ TAKHLE: součty (178 vs 176) se dají vysvětlit i špatně — a P18 to tak
skutečně zapsala (viz H97). Tenhle skript proto každý `.py` ZAŘADÍ do kategorie
a vypíše, co z toho NA32 dnes počítá jako živé:
  * `.git/`        — interní objekty gitu (NA32 vylučuje)
  * `_archiv/`     — archiv (NA32 vylučuje a VYKAZUJE)
  * `snapshot-*/`  — zmrazené kopie dokumentace (NA32 **počítá jako živé** = H93)
  * `*-scratch/`   — pracovní kopie pro mutace/worktree (NA32 **počítá jako živé**)
  * zbytek         = živý kód

U kopií (snapshot/scratch) se navíc měří, jestli mají PROTĚJŠEK v živém stromě
a jestli je bajt na bajt shodný — bez toho by „je to kopie" byl dohad.
Nic se needituje ani nemaže — skript jen čte a měří.
Použití: python _analyza/p19-b-h93-snapshot.py
"""

import hashlib
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
HRA = WS.parent / "uo-shadows"
REPA = [("orchestra", WS), ("hra", HRA)]
SNAP_RE = re.compile(r"^snapshot-\d")
# ⚠ OMyl 187 (naměřeno tady): `re.match` kotví na ZAČÁTEK, takže vzor
# `-scratch$` přes `match` NIKDY nesedl — kategorie `*-scratch` vyšla 0 a
# 19 souborů se tiše počítalo jako ŽIVÉ. Vypadalo to jako měření.
# Správně je `re.search` s explicitní kotvou (nebo vzor začínající `.*`).
SCRATCH_RE = re.compile(r".*-scratch$")


def je_snapshot(cast: str) -> bool:
    return bool(SNAP_RE.search(cast))


def je_scratch(cast: str) -> bool:
    return bool(SCRATCH_RE.search(cast))


def kategorie(p: pathlib.Path) -> str:
    casti = p.parts
    if ".git" in casti:
        return ".git"
    if "_archiv" in casti:
        return "_archiv"
    if any(je_snapshot(c) for c in casti):
        return "snapshot-*"
    if any(je_scratch(c) for c in casti):
        return "*-scratch"
    return "zive"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_obsah(b: bytes) -> str:
    """SHA-256 OBSAHU — s konci řádků sjednocenými na LF.

    ⚠ PROČ (omyl 188, naměřeno tady): kopie v scratchi měla jinou VELIKOST
    (13 783 B vs 14 096 B) a vypadalo to jako „LIŠÍ SE". Rozdíl byl přesně
    313 bajtů = 313 konců řádků (LF vs CRLF); `sha_obsah` je SHODNÝ.
    `core.autocrlf` na checkoutu přidá `\\r` — „autorita je blob, ne velikost
    souboru" (DSH_HOME\\AGENTS.md). Kdo to neudělá, vyrobí nález, který není.
    """
    return hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()


kategorie_podle = {}
for jmeno, koren in REPA:
    if not koren.is_dir():
        print(f"  {jmeno}: kořen NEEXISTUJE ({koren})")
        continue
    for p in sorted(koren.rglob("*.py")):
        kategorie_podle.setdefault((jmeno, kategorie(p)), []).append(p)

print("=" * 78)
print("P19/B — co NA32 počítá jako ŽIVÝ kód (soubor po souboru)")
print("=" * 78)

print("\n--- POČTY PO KATEGORIÍCH ---")
print(f"  {'repo':10} {'.git':>6} {'_archiv':>8} {'snapshot-*':>11} {'*-scratch':>10} {'ŽIVÉ':>6}")
zive_celkem = 0
for jmeno, _ in REPA:
    radky = {k: len(kategorie_podle.get((jmeno, k), []))
             for k in (".git", "_archiv", "snapshot-*", "*-scratch", "zive")}
    zive_celkem += radky["zive"]
    print(f"  {jmeno:10} {radky['.git']:>6} {radky['_archiv']:>8} "
          f"{radky['snapshot-*']:>11} {radky['*-scratch']:>10} {radky['zive']:>6}")
print(f"  → NA32 dnes hlásí jako živé: {zive_celkem} + snapshoty + scratch = "
      f"{zive_celkem + sum(len(kategorie_podle.get((j, k), [])) for j, _ in REPA for k in ('snapshot-*', '*-scratch'))}")

for kat in ("snapshot-*", "*-scratch"):
    print(f"\n--- KATEGORIE `{kat}`: soubor po souboru + má živý protějšek? ---")
    for jmeno, koren in REPA:
        for p in kategorie_podle.get((jmeno, kat), []):
            rel = p.relative_to(koren)
            # Protějšek = stejná cesta s kategorií VYHOZENOU z cesty — hledá se
            # ve VŠECH třech živých stromech, protože scratch je worktree HRY
            # (a `repo/` je šablona). Hledat jen ve stejném repu by dalo falešné
            # „NEEXISTUJE" — a to je závěr, který by se četl jako nález.
            casti = [c for c in rel.parts if not je_snapshot(c) and not je_scratch(c)]
            # ⚠ Scratch leží UVNITŘ `_analyza/`, takže kopie `tools/x.py` má
            # cestu `_analyza/a-ukol-scratch/tools/x.py` — a po odebrání scratch
            # složky zbude `_analyza/tools/x.py`, což NENÍ cesta protějšku.
            # Proto se zkoušejí i VŠECHNY SUFIXY cesty ve všech třech stromech
            # (`repo/` je šablona). Bez toho by „NENALEZEN" byl falešný nález.
            info = f"protějšek {pathlib.Path(*casti)} NENALEZEN v žádném stromě"
            for koren_hledani in (koren, HRA, WS / "repo"):
                for start in range(len(casti)):
                    kand = koren_hledani.joinpath(*casti[start:])
                    if kand.is_file():
                        b_kand, b_zdroj = kand.read_bytes(), p.read_bytes()
                        stejny = sha_obsah(b_kand) == sha_obsah(b_zdroj)
                        if stejny and b_kand != b_zdroj:
                            konec = "liší se JEN konce řádků (LF vs CRLF)"
                        elif stejny:
                            konec = "bajt na bajt"
                        else:
                            konec = "OBSAH SE LIŠÍ"
                        info = f"protějšek {kand} → SHODNÝ ({konec})" if stejny \
                            else f"protějšek {kand} → {konec}"
                        break
                if "SHODNÝ" in info or "LIŠÍ SE" in info:
                    break
            print(f"  [{jmeno}] {rel}\n         {info}")

print("\n--- KOMPILOVATELNOST PO KATEGORIÍCH ---")
chyby = {}
for (jmeno, kat), soubory in sorted(kategorie_podle.items()):
    for p in soubory:
        try:
            compile(p.read_text(encoding="utf-8-sig", errors="replace"), str(p), "exec")
        except SyntaxError as e:
            chyby.setdefault(kat, []).append((jmeno, p.name, e.lineno, e.msg))
        except (OSError, ValueError) as e:                        # noqa: BLE001
            chyby.setdefault(kat, []).append((jmeno, p.name, None, repr(e)))
for kat in (".git", "_archiv", "snapshot-*", "*-scratch", "zive"):
    n = len(chyby.get(kat, []))
    print(f"  {kat:12} nekompilovatelných: {n}")
    for jmeno, nazev, ln, msg in chyby.get(kat, []):
        print(f"      [{jmeno}] {nazev}:{ln} {msg}")
# ⚠ Čtení přes `utf-8-sig` (ne `utf-8`): BOM na začátku souboru Python při
# SPUŠTĚNÍ souboru ignoruje, kdežto `compile()` nad řetězcem s `U+FEFF` spadne.
# Rozdíl je nález H98 — měřený zvlášť, tady jen aby čísla nebyla falešně červená.
bom = []
for (jmeno, kat), soubory in sorted(kategorie_podle.items()):
    for p in soubory:
        if p.read_bytes()[:3] == b"\xef\xbb\xbf":
            bom.append((kat, jmeno, p))
print(f"\n  souborů s BOM: {len(bom)}")
for kat, jmeno, p in bom:
    try:
        compile(p.read_text(encoding="utf-8"), str(p), "exec")
        stav = "utf-8 OK"
    except SyntaxError as e:
        stav = f"utf-8 SyntaxError: {e.msg}"
    print(f"    [{kat}/{jmeno}] {p.name} — {stav}")

print("\n--- CO Z TOHO PLYNE ---")
snap = sum(len(kategorie_podle.get((j, "snapshot-*"), [])) for j, _ in REPA)
scr = sum(len(kategorie_podle.get((j, "*-scratch"), [])) for j, _ in REPA)
print(f"  • NA32 počítá jako živé i {snap} souborů ve `snapshot-*` a {scr} v `*-scratch`.")
print(f"  • Bez nich by hlásila {zive_celkem} živých souborů "
      f"(místo {zive_celkem + snap + scr}).")
print(f"  • `_archiv` je vyloučený a VYKAZUJE SE — stejný vzor se dá použít na obojí.")
print("=" * 78)

sys.exit(1 if chyby.get("zive") else 0)
