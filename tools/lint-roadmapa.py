import pathlib as _pl

# P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni skriptu.
# `tools/` je primo v koreni repa, takze _PARENT = root repa.
_PARENT = _pl.Path(__file__).resolve().parents[1]
"""Statický lint roadmapy: najde nekonzistence, které by zdržely nebo zablokovaly DAG.

Proč: orchestra odhaluje vady plánu až za běhu – a každé zjištění stojí kvótu
free modelu. Tenhle lint projde plán ještě před dispatchováním a najde:

  1. závislost na granulí, která v plánu není (DAG se nikdy neuzavře),
  2. cyklus v závislostech (nikdy se nespustí nic z cyklu),
  3. dvě granule, které vlastní stejný soubor (zámek je pustí jen sériově,
     ale plán to tvrdí jako paralelní),
  4. soubor v `owns`, který v projektu neexistuje a nemá ho vytvořit žádná
     jiná granule,
  5. granule `done: true`, na kterou se odvolává jiná granule – u té je
     kritické, aby měla řádek v D1 (jinak zůstane závislost viset),
  6. granule bez `owns` (agent nemá co editovat),
  7. `model: strong` bez deklarovaného `size_lines` (neví se, proč je silná),
  8. prázdný nebo chybějící `prompt`,
  9. chybějící `size_lines` u granule, jejíž soubory už v `main` jsou přes
     výchozích 60 řádků – to je příčina zaseknutých PR (A4a).
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(_PARENT / 'uo-shadows')
if not ROOT.is_dir():
    # ⚠ P13c (4. 10. 2026): hra je SOUROZENEC repa (přesun na `E:`), ne potomek.
    # Do téhle chvíle tu byla jen cesta `_PARENT / 'uo-shadows'`, která po
    # přesunu **neexistuje** → `FileNotFoundError` a brána se čtla jako
    # „červená", přitom **vůbec neměřila**. Zkouší se obojí (potomek i sourozenec),
    # aby nástroj fungoval před přesunem i po něm.
    _sourozenec = _PARENT.parent / 'uo-shadows'
    if _sourozenec.is_dir():
        ROOT = _sourozenec
ROADMAP = ROOT / ".forge" / "roadmap.json"


def main() -> int:
    data = json.loads(ROADMAP.read_text(encoding="utf-8"))
    grains = data["grains"]
    podle_id = {g["id"]: g for g in grains}
    problemy = []

    # 1) závislosti na neexistující granuli
    for g in grains:
        for d in g.get("depends_on", []):
            if d not in podle_id:
                problemy.append(f"[1] {g['id']}: depends_on '{d}', ale taková granule v plánu není")

    # 2) cykly
    stav = {}  # 0 = neviděno, 1 = v rekurzi, 2 = hotovo

    def cyklus(gid, cesta):
        if stav.get(gid) == 1:
            problemy.append(f"[2] cyklus v závislostech: {' -> '.join(cesta + [gid])}")
            return
        if stav.get(gid) == 2:
            return
        stav[gid] = 1
        for d in podle_id.get(gid, {}).get("depends_on", []):
            if d in podle_id:
                cyklus(d, cesta + [gid])
        stav[gid] = 2

    for g in grains:
        cyklus(g["id"], [])

    # 3) soubor vlastněný dvěma granulemi
    vlastnici = {}
    for g in grains:
        for f in g.get("owns", []):
            vlastnici.setdefault(f, []).append(g["id"])
    for f, kdo in vlastnici.items():
        if len(kdo) > 1:
            problemy.append(f"[3] soubor '{f}' vlastní víc granulí: {', '.join(kdo)} (poběží sériově, ne paralelně)")

    # 4) soubor v owns, který neexistuje a nikdo ho nevytvoří
    vsechny_owns = set(vlastnici)
    for g in grains:
        for f in g.get("owns", []):
            if not (ROOT / f).exists() and f not in vsechny_owns:
                problemy.append(f"[4] {g['id']}: owns '{f}', soubor neexistuje a žádná granule ho nevytváří")

    # 5) done: true granule, na kterou se odvolávají jiné
    hotove = {g["id"] for g in grains if g.get("done")}
    zavislych = {}
    for g in grains:
        for d in g.get("depends_on", []):
            zavislych.setdefault(d, []).append(g["id"])
    for gid in sorted(hotove):
        if gid in zavislych:
            problemy.append(
                f"[5] {gid} je 'done: true' a čeká na ni {len(zavislych[gid])} granulí "
                f"({', '.join(zavislych[gid])}) – musí mít řádek v D1, jinak závislosti "
                f"zůstanou viset")

    # 6) granule bez owns
    for g in grains:
        if not g.get("owns"):
            problemy.append(f"[6] {g['id']}: nemá 'owns' – agent neví, co editovat")

    # 7) strong bez size_lines
    for g in grains:
        if g.get("model") == "strong" and not g.get("size_lines"):
            problemy.append(f"[7] {g['id']}: model=strong, ale chybí size_lines (není z čeho poznat proč)")

    # 8) prompt
    for g in grains:
        p = (g.get("prompt") or "").strip()
        if len(p) < 40:
            problemy.append(f"[8] {g['id']}: prompt je prázdný nebo příliš krátký ({len(p)} znaků)")

    # 9) chybějící size_lines (A4a) – ZÁMĚRNĚ mimo `problemy`.
    # `size_lines` mají jen granule určené silnému modelu; u slabého modelu je
    # výchozích 60 SPRÁVNĚ. Kdyby to byla „vada", lint by začal blokovat i to,
    # co je v pořádku – tedy brána, která nemá jak nezasáhnout.
    # Přesto to musí být VIDĚT: naměřeno 2. 10. 2026 — `size_lines` chybí
    # u 13 z 18 granul a je to příčina všech tří visících PR (#28 save.gd +91,
    # #29 hud.gd +77, #30 mining.gd +66 – všechny přes výchozích 60).
    bez_velikosti = [g["id"] for g in grains if not g.get("size_lines")]

    # --- výstup ---
    print(f"Granulí: {len(grains)} | hotových: {len(hotove)} | strong: {sum(1 for g in grains if g.get('model')=='strong')}")
    print(f"Nalezeno problémů: {len(problemy)}")
    print()
    if not problemy:
        print("Nic nenalezeno.")
    for p in problemy:
        print("  " + p)

    # Přehled zámků: kolik granulí se může rozběhnout paralelně.
    print()
    print("=== SOUBORY Vlastněné VÍC GRANULEMI (brzdí paralelismus) ===")
    kolize = {f: k for f, k in vlastnici.items() if len(k) > 1}
    print(f"  {len(kolize)} souborů" if kolize else "  žádné")

    # 9) chybějící size_lines – informativní, viz komentář výš.
    print()
    print("=== GRANULE BEZ 'size_lines' (platí výchozích 60 řádků) ===")
    if bez_velikosti:
        print(f"  {len(bez_velikosti)} z {len(grains)}: {', '.join(bez_velikosti)}")
        print("  Není to vada u slabého modelu. U granule, jejíž změna je větší,")
        print("  ale 'size_lines' chybí, gate auto-merge PR zamítne (pravidlo 60).")
    else:
        print("  žádné – všechny granule mají deklarovanou velikost")
    # ⚠ Čítač MUSÍ BÝT VŽDY — `g3-brany.py` z něj čte „kolik toho brána
    # otevřela". Do 4. 10. 2026 se čítač tiskl jen v nenulové větvi, takže
    # u zdravé roadmapy zůstal sloupec `otevřela:` prázdný (a prázdno se čte
    # jako „brána neměřila" — past S27).
    print(f"ZMĚŘENO: {len(grains)} granulí zkontrolováno, "
          f"{len(problemy)} problémů, {len(kolize)} kolizí souborů")
    return 0


if __name__ == "__main__":
    sys.exit(main())
