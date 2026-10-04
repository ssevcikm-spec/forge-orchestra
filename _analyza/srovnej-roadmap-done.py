#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Srovna `done` v roadmap.json hry se stavem, ktery zna conductor (D1).

PROC: soubor je zdroj pravdy o PLANU, D1 o STAVU. Dnes se rozesly - D1 vi
o 10 hotovych granulich, soubor jen o 2. A `/roadmap/reset` maze radky D1
a stav stavi ZNOVU ze souboru: co tam nema `done: true`, by se vydalo znovu
(a zachranila by to jen křehká cesta "parovani PR podle nazvu").

CO SKRIPT DELA:
  1. precte ZIVY stav z podkladu `tmp-roadmap-d1.json` (stahne ho Node,
     viz `hl-stahni-podklady.mjs` - Python urllib dostal z Cloudflare 403),
  2. precte `roadmap.json` hry,
  3. u granul, ktere D1 vede jako `done` a soubor ne, dopise `done` a
     `done_note` - text poznamky bere z podkladu `tmp-pr.json`,
  4. zapise soubor po RADCICH (2 mezery, pole na jednom radku), aby tvar
     zustal; po zapisu znovu precte a overi, ze je to platny JSON.

POZOR - pouceni z prvni verze: hledat "konec objektu" hledanim prvniho radku
`}` je spatne, protoze se do objektu musi vkladat UPROSTRED. Vklada se proto
PRIMO za radek s `depends_on` (kazda granule ho ma) a pred vlozenim i po nem
se soubor vzdy znovu precte a zkontroluje.

BEZ `--provest` jen VYPISE, co by zmenil.
Spusteni: $env:PYTHONIOENCODING='utf-8'; python _analyza\srovnej-roadmap-done.py [--provest]
"""
import datetime
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(r"C:\Users\Ssevc\Local-Deepseek")
RM = WS / "games" / "uo-shadows" / ".forge" / "roadmap.json"
PROVEST = "--provest" in sys.argv


def nacti_d1():
    p = WS / "_analyza" / "tmp-roadmap-d1.json"
    if not p.exists():
        raise SystemExit("CHYBI podklady - spust: node _analyza/hl-stahni-podklady.mjs")
    return json.loads(p.read_text(encoding="utf-8"))["roadmap"]


def nacti_pr():
    """task_id -> 'PR #N sloučené D. M.'"""
    p = WS / "_analyza" / "tmp-pr.json"
    if not p.exists():
        raise SystemExit("CHYBI podklady - spust: node _analyza/hl-stahni-podklady.mjs")
    out = {}
    for p2 in json.loads(p.read_text(encoding="utf-8")):
        if not p2.get("merged_at"):
            continue
        m = re.match(r"^forge/task-(\d+)$", str(p2.get("head", {}).get("ref", "")))
        if not m:
            continue
        tid = int(m.group(1))
        if tid in out:
            continue
        d = p2["merged_at"][:10].split("-")
        out[tid] = f"PR #{p2['number']} sloučené {int(d[2])}. {int(d[1])}."
    return out


def vloz_za_depends_on(radky, gid, nove):
    """Vlozi radky `nove` hned za radek s 'depends_on' te granule.

    Vraci novy seznam radku, nebo vyhodi ValueError s vysvetlenim.
    """
    i_id = next((i for i, l in enumerate(radky)
                 if re.match(rf'^\s*"id": {re.escape(json.dumps(gid))},\s*$', l)), None)
    if i_id is None:
        raise ValueError(f"{gid}: řádek s \"id\" nenalezen")
    i_dep = next((i for i in range(i_id, len(radky))
                  if re.match(r'^\s*"depends_on": \[.*\],\s*$', radky[i])), None)
    if i_dep is None:
        raise ValueError(f"{gid}: řádek s \"depends_on\" nenalezen")
    if i_dep - i_id > 12:
        raise ValueError(f"{gid}: 'depends_on' je podezřele daleko od 'id' ({i_dep - i_id} řádků)")
    return radky[:i_dep + 1] + nove + radky[i_dep + 1:]


d1 = nacti_d1()
pr = nacti_pr()
soubor = json.loads(RM.read_text(encoding="utf-8"))

# co je v D1 hotove a v souboru ne
zmeny = []
for row in d1:
    if row["status"] != "done":
        continue
    gid = str(row["item_id"]).split("/", 1)[1]
    g = next((x for x in soubor["grains"] if x["id"] == gid), None)
    if g is None:
        zmeny.append((gid, None, "V SOUROBU NENI (jen v D1)"))
        continue
    if g.get("done") is True:
        continue
    poznamka = pr.get(row["task_id"]) if row.get("task_id") else None
    if poznamka:
        zmeny.append((gid, poznamka, "doplnit done"))
    else:
        # POZOR: D1 vi o mergi, ale PR NENI slouceny - to je nesoulad stavu.
        # Zapisujeme ho jako done (aby se granule po resetu nevydala znovu),
        # ale v poznamce to MUSI byt videt - jinak by se vada zametla.
        zmeny.append((gid,
                      f"POZOR: v D1 hotovo (task {row.get('task_id')}), "
                      f"ale PR NENÍ sloučené – práce není v main",
                      "doplnit done (s poznámkou o nesouladu)"))

print(f"# mereno {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
print(f"# D1: {len(d1)} radku, z toho done {sum(1 for x in d1 if x['status'] == 'done')}")
print(f"# soubor: {len(soubor['grains'])} granul, z toho done:true "
      f"{sum(1 for x in soubor['grains'] if x.get('done') is True)}")
print(f"\n# ZMENY ({len(zmeny)}):")
for gid, note, co in zmeny:
    print(f"   {co:38s} {gid:18s} {note}")

if not PROVEST:
    print("\n# (bez --provest: nic se nezapsalo)")
    sys.exit(0)

# --- zapis: pro KAZDOU granuli znovu precti soubor, vloz a zkontroluj ---
radky = RM.read_text(encoding="utf-8").split("\n")
zapsano = 0
for gid, note, co in zmeny:
    if not co.startswith("doplnit done"):
        continue
    nove = [f'      "done": true,',
            f'      "done_note": {json.dumps(note, ensure_ascii=False)},']
    try:
        kandidat = vloz_za_depends_on(radky, gid, nove)
    except ValueError as e:
        print(f"   ! PRESKOCENO {e}")
        continue
    text = "\n".join(kandidat)
    try:
        json.loads(text)
    except json.JSONDecodeError as e:
        print(f"   ! {gid}: výsledek není platné JSON ({e}) – NEZAPSÁNO")
        continue
    radky = kandidat
    zapsano += 1

RM.write_text("\n".join(radky), encoding="utf-8", newline="")
print(f"\n# ZAPSANO: {zapsano} granul")
# kontrola po zapisu
hotovo = json.loads(RM.read_text(encoding="utf-8"))
print(f"# kontrola: platné JSON, {len(hotovo['grains'])} granul, "
      f"done:true {sum(1 for x in hotovo['grains'] if x.get('done') is True)}")
