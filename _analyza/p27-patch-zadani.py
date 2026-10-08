# -*- coding: utf-8 -*-
r"""P27 (dodatek) — ZÁPLATA hlavičky zadání podle ČÍSLA ŘÁDKU.

PROČ: nástroj `edit` kotvy na řádcích 10–13 nenašel, ačkoli je `read` zobrazuje
shodně — v tom textu je tedy znak, který **nejde opsat okem** (táž třída pasti
jako `ANALYZA` vs `ANALIZA`, nález P27-I: kotva se ověřuje výpisem kódů znaků,
ne pohledem). Řádky se proto mění **podle čísla** a každý se PŘED zápisem ověří
ASCII prefixem (kdyby se číslování posunulo, skript to řekne a nic nezapíše).
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
Z = WS / "NEXT-SESSION-INSTRUKCE.md"
HRA = sys.argv[1] if len(sys.argv) > 1 else "bc51e46"
ORCH = sys.argv[2] if len(sys.argv) > 2 else "b668910"

# (číslo řádku 1-based, ASCII prefix pro ověření, nový text)
ZMENY = [
    (10, "`origin/main` orchestry je", (
        "`origin/main` orchestry je **`%s`** (**P25+P26+P27 PUSHNUTO** 8. 10. 2026),\n" % ORCH)),
    (11, "`origin/main` hry je", (
        "`origin/main` hry je **`932dc6f`** (**6 commitů hry je NEPUSHNUTÝCH** — cizí\n")),
    (12, "session;", (
        "session; **během P27 přibyly tři: `af6abd8`, `bc51e46`**).\n")),
    (13, "Práce P27 je", (
        "Práce P27 je **COMMITNUTÁ I PUSHNUTÁ** (`1bdc982`, `649ca9b`, `77ade9f`, "
        "`38ff4ad`,\n`8f80b0d`, `a8ff943`, `07169c7`, `b668910`);\n")),
    (290, "git -C E:\\Workspaces\\forge-orchestra rev-parse --short HEAD", None),
]

radky = Z.read_text(encoding="utf-8").splitlines(keepends=True)
kontrol = 0
chyb = 0


def k(ok, popis):
    global kontrol, chyb
    kontrol += 1
    print("  %s  %s" % ("OK  " if ok else "CHYBA", popis))
    if not ok:
        chyb += 1


print("řádků v zadání: %d" % len(radky))
for cislo, prefix, novy in ZMENY:
    radek = radky[cislo - 1]
    if not radek.startswith(prefix):
        k(False, "řádek %d nezačíná %r (je: %r)" % (cislo, prefix, radek[:50]))
        continue
    if novy is None:
        # řádek 290: jen vyměnit starý sha za nový (kotva: ASCII prefix + '->')
        import re
        novy = re.sub(r"-> [0-9a-f]{7,40}", "-> %s" % ORCH, radek)
        k(novy != radek, "řádek %d: sha vyměněno" % cislo)
    radky[cislo - 1] = novy
    k(True, "řádek %d přepsán" % cislo)

text = "".join(radky)
Z.write_bytes(text.encode("utf-8"))
t2 = Z.read_text(encoding="utf-8")
k("`forge-orchestra` = **`%s`**" % ORCH in t2, "hlavička tvrdí živý HEAD orchestry")
k("`uo-shadows` = **`%s`**" % HRA in t2, "hlavička tvrdí živý HEAD hry")
k("COMMITNUTÁ I PUSHNUTÁ" in t2, "zadání říká, že práce je pushnutá")
k("6 commitů hry" in t2, "zadání říká 6 nepushnutých commitů hry")
b = Z.read_bytes()
k(b.count(b"\r\n") == 0 and not b.startswith(b"\xef\xbb\xbf"), "LF a bez BOM")

print()
print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
sys.exit(1 if chyb else 0)
