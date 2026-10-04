# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
r"""Mutační test A1/A2 na ŽIVÉM souboru `index.ts` — ověří, že brána a1-a2-over.py měří.

Proč takhle: `a1-a2-over.py` je statická kontrola, která čte rozhodovací logiku
ze zdroje conductora. „Prošlo" u ní znamená jen to, že soubor existuje a vzorce
tam jsou — dokud se nezkusí vadu VRÁTIT. Naivní mutace přes PowerShell
`-replace` je past (skill `overovani` §7.9: s em-dash se mutace TICHE neprovede
a vypadá to jako slepá brána). Proto se mutuje v Pythonu, kde je kódování
zaručené, a PŘED spuštěním brány se ověří, že mutace opravdu proběhla.

Druhá past: `index.ts` má NEcommitnuté změny (A1/A2 jsou z 2. 10. 2026 a nejsou
pushnuté). `git checkout --` by je smazal. Proto se zálohuje KOPIÍ a vrací se
bajt po bajtu.

Spusteni:  $env:PYTHONIOENCODING='utf-8'; python _analyza\a1-a2-mutace.py
"""
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(_STANICE)
INDEX = WS / "conductor" / "src" / "index.ts"
BRANA = WS / "_analyza" / "a1-a2-over.py"

if not INDEX.is_file():
    print(f"CHYBA: {INDEX} neexistuje")
    sys.exit(2)

orig_bajty = INDEX.read_bytes()
orig = orig_bajty.decode("utf-8")

# (nazev, najdi, nahrad) — kazda mutace vráti vadu, kterou A1/A2 opravily.
# Vzory musi byt JEDNOZNACNE (1 vyskyt v souboru) — jinak se mutace neda
# provest a vysledek by nic neznameal. Namereno pri psani: `awaiting_human`
# je v souboru 4x (2x komentar, 2x SQL) a `ORIGIN_MAIN_TTL_MS` 2x; kratke
# vzory proto tise mutovaly i komentar nebo jinou vetev.
#
# POZOR (namereno 2. 10. 2026): mutace, ktera je SEMANTICKY NEUTRALNI, nema
# v tomhle seznamu co delat. Měl jsem tu „prejmenuj konstantu
# `ORIGIN_MAIN_TTL_MS` -> `ORIGIN_MAIN_CACHE_MS`" a hlasil ji jako slepou
# branu — jenze kod po ni dela TOTÉŽ. Brána, která projde, má pravdu.
# Vada by to byla jen tehdy, kdyby se prejmenovalo JEN v deklaraci (to by
# kód rozbilo) — a to je jina mutace, ne tahle.
MUTACE = [
    ("A1: `ok && merged` zpet na `ok`",
     "if (ok && merged) {", "if (ok) {"),
    ("A2: odstraneno rozliseni `null` vs. prazdny strom",
     "stromMain !== null && owns.length > 0", "owns.length > 0"),
    ("A2: TTL se prestal pouzivat — cache slouzi navzdy (N7)",
     "expiruje: ted + ORIGIN_MAIN_TTL_MS }",
     "expiruje: ted + 999999999 }"),
    ("A1: stav `awaiting_human` prejmenovan v zapisu do D1",
     "UPDATE tasks SET status='awaiting_human'",
     "UPDATE tasks SET status='pending_review'"),
]


def spust_branu():
    r = subprocess.run([sys.executable, str(BRANA)],
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, (r.stdout or "").strip()


print("=== Mutační test A1/A2 na živém index.ts ===\n")

kod, vystup = spust_branu()
posledni = vystup.splitlines()[-1] if vystup else "(zadny vystup)"
print(f"  0) vychozi stav: exit={kod} | {posledni}")
if kod != 0:
    print("     POZOR: vychozi stav neprochazi — mutace by nic netestovaly.")
    INDEX.write_bytes(orig_bajty)
    sys.exit(1)

selhalo = []          # brana prosla i s vadou = SLEPA BRANA (nalez o brane)
nezmutovano = []      # mutaci nešlo provést = nalez o TESTOVACIM SKRIPTU
try:
    for i, (nazev, najdi, nahrad) in enumerate(MUTACE, start=1):
        pocet = orig.count(najdi)
        if pocet != 1:
            print(f"  {i}) {nazev}: NEZMUTOVANO — vzor je v souboru {pocet}x (cekam 1x)")
            print("        (to neni nalez o brane: mutace se vubec neprovedla)")
            nezmutovano.append(nazev)
            continue
        zmutovany = orig.replace(najdi, nahrad)
        # overeni, ze mutace OPRAVDU probehla (past ze skillu overovani §7.9)
        assert najdi not in zmutovany, "mutace se neprovedla!"
        assert nahrad in zmutovany, "mutace nezapsala nahradu!"
        INDEX.write_text(zmutovany, encoding="utf-8", newline="")
        kod, vystup = spust_branu()
        chyby = [l.strip() for l in vystup.splitlines() if "CHYBA:" in l]
        ok = kod != 0
        print(f"  {i}) {nazev}: exit={kod} -> {'SPRAVNE SPADLA' if ok else 'SLEPA (prosla i s vadou!)'}")
        for c in chyby[:2]:
            print(f"        {c}")
        if not ok:
            selhalo.append(nazev)
finally:
    INDEX.write_bytes(orig_bajty)
    assert INDEX.read_bytes() == orig_bajty, "original index.ts se nepodarilo vratit!"

kod, vystup = spust_branu()
print(f"\n  po vraceni originalu: exit={kod} | {vystup.splitlines()[-1] if vystup else ''}")

provedeno = len(MUTACE) - len(nezmutovano)
print()
print(f"  mutaci provedeno : {provedeno} z {len(MUTACE)}")
print(f"  brana chytila    : {provedeno - len(selhalo)}")
print(f"  slepa brana      : {len(selhalo)}")
print(f"  nezmutovano      : {len(nezmutovano)}")
if selhalo:
    print(f"\nVYSLEDEK: brana je SLEPA v {len(selhalo)} pripadech: {'; '.join(selhalo)}")
    sys.exit(1)
if nezmutovano:
    print(f"\nVYSLEDEK: brana chytila vsechny PROVEDENE mutace ({provedeno}), ale")
    print(f"          {len(nezmutovano)} mutaci se neprovedlo — vzory je nutne zpresnit:")
    for n in nezmutovano:
        print(f"            - {n}")
    sys.exit(2)
print(f"\nVYSLEDEK: brana chytila vsechny {len(MUTACE)} mutace a vychozi stav prochazi.")
sys.exit(0)
