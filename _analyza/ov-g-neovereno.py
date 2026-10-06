# P18 — Úkol G povinná část: jsou VŠECHNY návrhy v kronice ROZHODNUTÉ?
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KR = pathlib.Path(r"E:\Workspaces\forge-orchestra\KRONIKA-PROJEKTU.md")
lines = KR.read_text(encoding="utf-8").splitlines()

STAVY = ("NEOVĚŘENO", "APLIKOVÁNO", "POTVRZENO", "ZAMÍTNUTO", "ODLOŽENO",
         "SPLNĚNO", "VYŘEŠENO")
print("=" * 90)
print("NÁVRHY V KRONICE — STAV U KAŽDÉHO (povinná část předání, §2.2)")
print("=" * 90)
nerozhodnute = []
celkem = 0
for i, l in enumerate(lines, 1):
    m = re.match(r"^\|\s*\*\*(NA\d+)\*\*\s*\|", l)
    if not m:
        continue
    celkem += 1
    # ⚠ Vlastní omyl P18: nejdřív jsem bral 4. sloupec podle `split('|')` — a ten
    # je ŠPATNĚ, protože buňky samy obsahují `|` (např. vzor `NALEZENO (\d+)|VŠE V PO`).
    # Index sloupce se tím posune a NA23 (ve skutečnosti `APLIKOVÁNO`) vyšel jako
    # „bez stavu" — falešný nález o správném záznamu. Stav se proto hledá v CELÉM
    # řádku; `NEOVĚŘENO` vyhrává (je to jediný stav, který znamená „čeká").
    nalezeny = [s for s in STAVY if s in l]
    if "NEOVĚŘENO" in l or not [s for s in nalezeny if s != "NEOVĚŘENO"]:
        nerozdecne = True
        nerozhodnute.append((m.group(1), i, ",".join(nalezeny) or "(žádný stav)"))
    else:
        nerozdecne = False
    print(f"  {m.group(1):6} r.{i:4}  {'!! ' if nerozdecne else '   '}"
          f"{nalezeny if nalezeny else '(žádný stav)'}")

print(f"\n  návrhů celkem: {celkem}")
print(f"  ve stavu NEOVĚŘENO (nebo bez stavu): {len(nerozhodnute)}")
for n, i, s in nerozhodnute:
    print(f"    !! {n} (r.{i}): {s}")

print("\n" + "=" * 90)
print("TOTÉŽ PRO NÁLEZY (Hxx) V HANDOFF.md — hledám 'NEOVĚŘENO' ve sloupci Stav")
print("=" * 90)
HO = pathlib.Path(r"E:\Workspaces\forge-orchestra\HANDOFF.md")
h_lines = HO.read_text(encoding="utf-8").splitlines()
n_h = 0
h_nev = []
for i, l in enumerate(h_lines, 1):
    m = re.match(r"^\|\s*\*\*(H\d+)\*\*\s*\|", l)
    if not m:
        continue
    n_h += 1
    if "NEOVĚŘENO" in l:
        h_nev.append((m.group(1), i))
print(f"  nálezů (řádků tabulek Hxx): {n_h}")
print(f"  s textem NEOVĚŘENO na tom řádku: {len(h_nev)}")
for h, i in h_nev:
    print(f"    !! {h} (r.{i})")

verdict = (len(nerozhodnute) == 0 and len(h_nev) == 0)
print("\n" + "=" * 90)
print("VÝSLEDEK: " + ("ŽÁDNÝ NÁVRH ANI NÁLEZ NEZŮSTAL VE STAVU NEOVĚŘENO"
                      if verdict else
                      f"POZOR — {len(nerozhodnute)} návrhů + {len(h_nev)} nálezů "
                      f"ve stavu NEOVĚŘENO"))
print("=" * 90)
sys.exit(0 if verdict else 1)
