r"""Uklidí `NEXT-SESSION-INSTRUKCE.md` po přepsání stavu Úkolu A.

CO SE STALO: nový stav (A2/A3/A5 hotové) se vložil NAD starý text, takže
v souboru zůstaly DVĚ verze téhož — stará A2/A3/A4/A5 (popis stavu PŘED
pushem) a nová. Duplicitní zadání se čte jako „ještě to není hotové".

CO SKRIPT DĚLÁ:
  1) smaže starý blok od `### A2. Rozhodnout push` po konec staré A5
     (včetně odstavce „Zbývající N", který je i v nové verzi),
  2) přesune `### A1.` NAD `### A2.` (pořadí musí zůstat A1→A5),
  3) ověří, že každé `### A?` je v souboru právě JEDNOU.

Idempotentní: když blok už není, jen to řekne.
Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\uklid-zadani.py
"""
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CIL = pathlib.Path("NEXT-SESSION-INSTRUKCE.md")
text = CIL.read_text(encoding="utf-8")
puvodni = text

# ── 1) SMAZAT starý blok A2..A5 ─────────────────────────────────────────────
START = "### A2. Rozhodnout push `orchestra` (= rozhodnutí **O3**)"
KONEC = """**Zbývající N:** N4 (rozhodnout: drift hlídá strukturu, nebo i `env`?),
N6 (doplnit **čas měření** k číslům — nepřepisovat hodnoty),
N8 (rozšířit `n8-*` o další dvojice — **ale nejdřív opravit V3**),
N9 (`ag-over-cisla.py` pokrývá **5 + 2 z 80** řádků s číslem)."""

if START in text:
    i = text.index(START)
    j = text.index(KONEC, i) + len(KONEC)
    smazano = text[i:j]
    text = text[:i] + text[j:]
    print(f"smazán starý blok A2–A5: {len(smazano.splitlines())} řádků")
else:
    print("starý blok A2–A5 už v souboru není (dobře)")

# ── 2) PŘESUNOUT A1 NAD A2 ──────────────────────────────────────────────────
A1_START = "### A1. ✅ HOTOVO — dvě zastaralá tvrzení v `HANDOFF.md` opravena"
A2_NOVY = "### A2. ✅ HOTOVO — push orchestra proveden a nasazen"

if A1_START in text and A2_NOVY in text and text.index(A1_START) > text.index(A2_NOVY):
    i = text.index(A1_START)
    # konec bloku A1 = poslední řádek před dalším "### " nebo "---"
    m = re.search(r"\n(?=### |---)", text[i + len(A1_START):])
    j = i + len(A1_START) + (m.start() + 1 if m else len(text) - i - len(A1_START))
    blok = text[i:j]
    text = text[:i] + text[j:]
    # vložit před novou A2 (a uklidit případné zdvojené prázdné řádky)
    k = text.index(A2_NOVY)
    text = text[:k] + blok + text[k:]
    print(f"blok A1 ({len(blok.splitlines())} řádků) přesunut před A2")
else:
    print("A1 je už před A2 (nebo chybí)")

# ── 3) UKLIDIT vícenásobné prázdné řádky ────────────────────────────────────
text = re.sub(r"\n{4,}", "\n\n\n", text)

if text != puvodni:
    CIL.write_text(text, encoding="utf-8", newline="")
    print("zapsáno")
else:
    print("beze změny")

# ── 4) OVĚŘENÍ: každé zadání právě jednou ───────────────────────────────────
nove = CIL.read_text(encoding="utf-8")
print("\n--- KONTROLA (každé `### A?` musí být právě 1x) ---")
ok = True
for pismeno in "A1 A2 A3 A4 A5".split():
    kolik = len(re.findall(rf"^### {pismeno}\.", nove, flags=re.M))
    stav = "OK " if kolik == 1 else "CHYBA"
    if kolik != 1:
        ok = False
    print(f"  {stav} ### {pismeno}. ... {kolik}x")

print("\n--- pořadí nadpisů Úkolu A ---")
for m in re.finditer(r"^### (A\d)\..*$", nove, flags=re.M):
    print(f"  {m.group(0)[:78]}")

poradi = [m.group(1) for m in re.finditer(r"^### (A\d)\.", nove, flags=re.M)]
ocekavane = ["A1", "A2", "A3", "A4", "A5"]
if poradi[:5] != ocekavane:
    print(f"\nCHYBA: pořadí je {poradi[:5]}, čekáno {ocekavane}")
    ok = False

# ── 5) Nic nesmí zmizet: klíčové věty ze ZADÁNÍ musí zůstat ─────────────────
KLICE = [
    "`done` je tvrzení, ne důkaz",
    "RETRY_HOURS",
    "persist.save.state",
    "Pravidlo, které se v tomhle workspace nevyplácí porušit",
    "Nedělej plánovací session sám",
    "Nepushovat `d0bf4f9`",
    "Znalost patří k naměřenému příkladu",
]
print("\n--- klíčové body zadání (nesmí zmizet) ---")
for k in KLICE:
    je = k in nove
    if not je:
        ok = False
    print(f"  {'OK ' if je else 'CHYBA'} {k}")

print("\nsoubor:", f"{len(nove.splitlines())} řádků, {len(nove)} znaků")
sys.exit(0 if ok else 1)
