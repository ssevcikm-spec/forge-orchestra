# P18 — Úkol G povinná část: jsou VŠECHNY návrhy v kronice ROZHODNUTÉ?
# P26 (7. 10. 2026) — nález P25-K: MĚŘIDLO TIŠE ZÚŽILO ROZSAH. Opraveno.
#
# ⚠ CO BYLO ŠPATNĚ (naměřeno P26, ne odhadnuto):
# Optimalizace KB (7. 10. 2026, commit `92aa80a`) přesunula tabulky nálezů Hxx
# z `HANDOFF.md` do `_archiv/HANDOFF-HISTORIE.md`. Tenhle skript ale čítal
# **jen `HANDOFF.md`** — a tam zbyl **1** řádek Hxx. Měřidlo tedy dál hlásilo
# „žádný nález ve stavu NEOVĚŘENO", ale **o 1 řádku místo o 99** (1 + 98)
# a verdikt „zelená" se tím stal zelenou nad **1 % původního rozsahu**.
# Nikdo to nepoznal, protože skript sice vypsal čítač, ale **nevypsal, KTERÉ
# soubory otevřel** — chybějící rozsah není vidět (`overovani` §7.13).
#
# ⚠ DRUHÁ VADA TÉHOŽ MÍSTA: sekce se jmenovala „hledám 'NEOVĚŘENO' ve sloupci
# Stav" — ale **žádný sloupec `Stav` v těch tabulkách není** (HANDOFF.md má
# 2 buňky, archiv 3: `# | Nález | Doklad`). Skript hledá **kdekoli na řádku**,
# takže by chytil i CITACI („bylo NEOVĚŘENO, dnes APLIKOVÁNO") v próze —
# přesně past „brána čte citaci místo tvrzení" (`AGENTS.md`). Dnes je takových
# řádků **0** (naměřeno P26 ve všech zdrojích), ale musí to být VIDĚT, ne
# předpokládáno: skript proto vypisuje i rozpad na buňky.
#
# ⚠ CO SE ZÁMĚRNĚ NEČTE: `_analyza/handoff-pred-*.md` a
# `_analyza/snapshot-*/…/HANDOFF.md` taky obsahují řádky Hxx (7–24) — jsou to
# **zmrazené kopie a zálohy**, ne živý záznam. Kdyby se čítaly, počítal by se
# týž nález vícekrát (táž past jako H93/H98). Skript je proto vypíše jako
# POJMENOVANOU POZNÁMKU („mimo živé zdroje"), aby zúžení rozsahu nebylo tiché.
#
# Použití:
#     python _analyza/ov-g-neovereno.py
#     python _analyza/ov-g-neovereno.py --handoff <cesta>   # přepínač pro mutační důkaz
import argparse
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ⚠ CESTY SE ODVOZUJÍ, NEZAPEKAJÍ (generalizace, 7. 10. 2026).
REPO = pathlib.Path(__file__).resolve().parents[1]
KR = REPO / "KRONIKA-PROJEKTU.md"
RADEK_H = re.compile(r"^\|\s*\*\*(H\d+)\*\*\s*\|")


def zive_zdroje():
    """Soubory, které NESOU ŽIVÝ záznam řádků Hxx.

    Odvozuje se (ne zapečený seznam): `HANDOFF.md` v kořeni + `_archiv/HANDOFF-*.md`.
    ⚠ NE `glob("HANDOFF*.md")` — na Windows je `glob` NECITLIVÝ NA VELIKOST
    PÍSMEN, takže by chytil i `_analyza/handoff-pred-*.md` (zálohy a snapshoty).
    Porovnává se proto `name.startswith("HANDOFF-")` nad SKUTEČNÝM jménem.
    """
    zdroje = [REPO / "HANDOFF.md"]
    arch = REPO / "_archiv"
    if arch.is_dir():
        zdroje += sorted(p for p in arch.iterdir()
                         if p.is_file() and p.name.startswith("HANDOFF-")
                         and p.suffix == ".md")
    return [p for p in zdroje if p.is_file()]


def radky_h(cesta):
    """(číslo řádku, text) pro každý řádek tabulky Hxx v souboru."""
    try:
        text = cesta.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return [(i, l) for i, l in enumerate(text.splitlines(), 1) if RADEK_H.match(l)]


def bunky(radek):
    """Buňky řádku tabulky bez krajních prázdných."""
    return [x.strip() for x in radek.split("|")[1:-1]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--handoff", action="append", default=None,
                    help="zdroj řádků Hxx (lze vícekrát); přebíjí odvozené živé zdroje. "
                         "Přepínač existuje kvůli MUTAČNÍMU DŮKAZU (fixtura).")
    ap.add_argument("--kronika", default=None, help="cesta ke kronice (pro mutaci)")
    args = ap.parse_args()

    kronika = pathlib.Path(args.kronika).resolve() if args.kronika else KR
    zdroje = ([pathlib.Path(x).resolve() for x in args.handoff]
              if args.handoff else zive_zdroje())

    lines = kronika.read_text(encoding="utf-8").splitlines()

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
    print("TOTÉŽ PRO NÁLEZY (Hxx) — hledám 'NEOVĚŘENO' KDEKOLI NA ŘÁDKU")
    print("⚠ POZOR: tabulky Hxx NEMAJÍ sloupec `Stav` (jsou 2–3 buňky:")
    print("   `# | Nález | Doklad`). Rozpad na buňky se proto vypisuje zvlášť —")
    print("   nález v buňce „Doklad“ může být CITACE, ne stav.")
    print("=" * 90)
    n_h = 0
    h_nev = []
    for cesta in zdroje:
        rs = radky_h(cesta)
        nev = [(m.group(1), i) for i, l in rs
               if (m := RADEK_H.match(l)) and "NEOVĚŘENO" in l]
        n_h += len(rs)
        h_nev += [(h, i, cesta.name) for h, i in nev]
        try:
            jmeno = str(cesta.relative_to(REPO))
        except ValueError:
            jmeno = str(cesta)
        print(f"  OTEVŘENO: {jmeno:44} řádků Hxx: {len(rs):4}  NEOVĚŘENO: {len(nev)}")
    print(f"\n  ZDROJŮ OTEVŘENO: {len(zdroje)}")
    print(f"  nálezů (řádků tabulek Hxx) CELKEM: {n_h}")
    print(f"  s textem NEOVĚŘENO na tom řádku: {len(h_nev)}")
    for h, i, jm in h_nev:
        print(f"    !! {h} ({jm} r.{i})")

    # ── ROZSAH MIMO ŽIVÉ ZDROJE: zúžení musí být VIDĚT, ne tiché (P25-K) ────
    zit = {p.resolve() for p in zdroje}
    mimo = []
    for p in sorted(REPO.rglob("*.md")):
        if ".git" in p.parts or p.resolve() in zit:
            continue
        if not p.name.lower().startswith("handoff"):
            continue
        rs = radky_h(p)
        if rs:
            mimo.append((str(p.relative_to(REPO)), len(rs)))
    print("\n  ── MIMO ŽIVÉ ZDROJE (zmrazené kopie a zálohy — ZÁMĚRNĚ se nečtou) ──")
    if mimo:
        for jm, n in mimo:
            print(f"    · {jm:52} řádků Hxx: {n}")
        print(f"    celkem mimo: {sum(n for _, n in mimo)} řádků v {len(mimo)} souborech")
        print("    (kdyby se čítaly, počítal by se týž nález vícekrát — past H93/H98)")
    else:
        print("    (žádné)")

    verdict = (len(nerozhodnute) == 0 and len(h_nev) == 0)
    print("\n" + "=" * 90)
    if n_h == 0:
        # ⚠ NULA NENÍ ÚSPĚCH: „0 nálezů ve stavu NEOVĚŘENO" nad PRÁZDNÝM rozsahem
        # je přesně vada P25-K. Prázdný rozsah se hlásí jako NEMĚŘENO.
        print("NEMĚŘENO — neotevřel se ANI JEDEN řádek tabulky Hxx.")
        print("Zelená nad prázdným rozsahem není měření (P25-K).")
        print("=" * 90)
        return 1
    print("VÝSLEDEK: " + ("ŽÁDNÝ NÁVRH ANI NÁLEZ NEZŮSTAL VE STAVU NEOVĚŘENO"
                          if verdict else
                          f"POZOR — {len(nerozhodnute)} návrhů + {len(h_nev)} nálezů "
                          f"ve stavu NEOVĚŘENO")
          + f"   [rozsah: {celkem} návrhů NAxx + {n_h} nálezů Hxx v {len(zdroje)} zdrojích]")
    print("=" * 90)
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
