r"""OVĚŘENÍ ÚKOLU 3 — hlavičky u testů, které NEPROBĚHNOU (nález R6).

PROČ TO EXISTUJE: zadání `ZADANI-DOKONCENI-AUDITU.md` (Úkol 3) žádá, aby oba
testy měly na začátku komentář „co to je / že dnes neproběhne / proč / co by ho
zprovoznilo". **Dokumentace, která to jen tvrdí, je bezcenná** — a přesně na
tuhle past projekt opakovaně narazil (`overovani` §7.10: brána je zelená nad
dokumentem, který nikdy neotevřela). Tenhle skript proto:

  1. oba soubory **otevře a parsuje** (`ast.parse`) — ne že „někde existují";
  2. ověří, že **docstring** obsahuje všech pět povinných značek;
  3. **SPUSTÍ oba testy** a ověří, že pořád padají **tím konkrétním důvodem**,
     který hlavička tvrdí — kdyby se příčina změnila, hlavička by lhala
     a nikdo by si toho nevšiml (to je celý smysl nálezu R6);
  4. a změří, že **`exit 1` neznamená nález o kódu** — ve výstupu nesmí být
     ani jeden souhrn `[test] N kontrol, M selhání` (tedy: neproběhl žádný běh).

Kontrola č. 3 je jádro: **hlavička a skutečnost se musí rozejít hlasitě.**

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\audit3-hlavicky-over.py
"""
import ast
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent

# (soubor, co MUSÍ být v docstringu, co MUSÍ být ve výstupu při spuštění)
PRIPADY = [
    ("_analyza/h17-mutace-a.py",
     ["NEPROBĚHNE", "NEPROBĚHLO", "h17-kladna", "worktree neexistuje",
      "ZPROVOZNILO", "NEMÁ SMAZAT"],
     "worktree neexistuje"),
    ("_analyza/mutace-testu.py",
     ["NEPROBĚHNE", "NEPROBĚHLO", "merge-scratch", "rc=128",
      "ZPROVOZNILO", "NEMÁ SMAZAT"],
     "MUTACE NEPROBĚHLA"),
]

chyby = []
print("=" * 92)
print("OVĚŘENÍ ÚKOLU 3 — hlavičky u testů, které NEPROBĚHNOU (nález R6)")
print("=" * 92)

for rel, znacky, ocekavany_duvod in PRIPADY:
    p = WS / rel
    print("\n  %s" % rel)
    if not p.is_file():
        chyby.append("%s: soubor NEEXISTUJE (a mazat se nemá — A1/A7)" % rel)
        print("    CHYBA: soubor neexistuje")
        continue

    zdroj = p.read_text(encoding="utf-8")
    try:
        strom = ast.parse(zdroj)
    except SyntaxError as e:
        chyby.append("%s: NEPARSuje se (%s)" % (rel, e))
        print("    CHYBA: neparsuje se: %s" % e)
        continue
    doc = ast.get_docstring(strom) or ""
    print("    parsuje se: ANO · docstring: %d znaků" % len(doc))
    if not doc:
        chyby.append("%s: NEMÁ docstring (hlavička nikde)" % rel)

    chybejici = [z for z in znacky if z not in doc]
    for z in znacky:
        print("      %-22s %s" % (z, "OK" if z in doc else "CHYBI"))
    if chybejici:
        chyby.append("%s: v hlavičce chybí %s" % (rel, chybejici))

    # ── 3+4) spustit a porovnat se TVRZENÍM hlavičky ────────────────────────
    r = subprocess.run([sys.executable, str(p)], capture_output=True,
                       cwd=str(WS))
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    souhrny = re.findall(r"\[test\] \d+ kontrol, \d+ selhání", v)
    print("    SPUŠTĚNO: exit=%d · souhrnů testů ve výstupu=%d"
          % (r.returncode, len(souhrny)))
    if r.returncode == 0:
        chyby.append("%s: dnes PROCHÁZÍ (exit 0) — hlavička „neproběhne\" je "
                     "zastaralá, přeměř ji" % rel)
        print("      !! exit 0 — hlavička je ZASTARALÁ (test už běží)")
    if ocekavany_duvod not in v:
        chyby.append("%s: padá z JINÉHO důvodu, než hlavička tvrdí "
                     "(„%s\" ve výstupu není)" % (rel, ocekavany_duvod))
        print("      !! důvod „%s\" ve výstupu NENÍ — hlavička LHÁ" % ocekavany_duvod)
    else:
        print("      důvod „%s\" potvrzen" % ocekavany_duvod)
    if souhrny:
        chyby.append("%s: ve výstupu je souhrn testů (%s) — takže se NĚCO "
                     "změřilo; hlavička tvrdí „nula běhů\"" % (rel, souhrny[:2]))
        print("      !! ale je tam souhrn testů: %s" % souhrny[:2])
    else:
        print("      žádný běh testů neproběhl (0 souhrnů) — souhlasí s hlavičkou")

print("\n" + "=" * 92)
print("  ZMĚŘENO: souborů=%d, každý parsován i SPUŠTĚN, chyb=%d"
      % (len(PRIPADY), len(chyby)))
if chyby:
    print()
    for c in chyby:
        print("  CHYBA: %s" % c)
    print("\nVYSLEDEK: Úkol 3 NENÍ ověřen → exit 1")
    sys.exit(1)
print("\nVYSLEDEK: oba testy mají hlavičku, pořád padají TÍMŽ důvodem a ani")
print("          jeden nezměřil běh — „neproběhlo\" je pojmenované. exit 0")
sys.exit(0)
