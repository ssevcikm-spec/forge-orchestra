# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
r"""Souběh dvou session: co se zapsalo PO mém posledním přečtení.

Problém: čtu soubor, jiná session ho přepíše, já zapíšu svou verzi z paměti
-> jejich práce zmizí. Přesně to se stalo u HANDOFF.md (systém zápis odmítl,
což je správně).

Tenhle skript seřadí VŠECHNY zápisy obou session podle času a vypíše je jako
časovou osu. Z ní je vidět, kdo psal po kom.

Spuštění: $env:PYTHONIOENCODING='utf-8'; python _analyza\hl2-casova-osa.py
"""
import collections
import datetime
import json
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(_STANICE)
LOGY = sorted((WS / "_analyza").glob("tmp-session-*.jsonl"))

zaznamy = []
for log in LOGY:
    sid = log.stem.replace("tmp-session-", "")[:8]
    for l in log.read_text(encoding="utf-8", errors="replace").split("\n"):
        if not l.strip():
            continue
        try:
            o = json.loads(l)
        except Exception:
            continue
        if o.get("type") != "tool/call":
            continue
        d = o.get("data") or {}
        nazev = d.get("name") or d.get("tool")
        if nazev not in ("write", "edit"):
            continue
        a = d.get("arguments") or d.get("input") or {}
        if isinstance(a, str):
            try:
                a = json.loads(a)
            except Exception:
                continue
        if not isinstance(a, dict):
            continue
        cesta = str(a.get("file_path") or a.get("path") or "?")
        cas = d.get("time") or o.get("time") or 0
        zaznamy.append((cas, sid, nazev, cesta))

zaznamy.sort()
print(f"# Časová osa zápisů obou session ({len(zaznamy)} záznamů)\n")

# Přelož ms -> čas (t je ms epoch)
def cas(ms):
    try:
        return datetime.datetime.fromtimestamp(ms / 1000).strftime("%H:%M:%S")
    except Exception:
        return "?"

# Session, které psaly SOUBORY V ROOTU (ne _analyza) -- tam je riziko
print("## Zápisy do souborů v ROOTU workspace (nejrizikovější)")
for cas_, sid, nazev, cesta in zaznamy:
    if "\\_analyza\\" in cesta:
        continue
    if ".dsh\\skills" in cesta:
        continue
    jm = cesta.split("\\")[-1]
    print(f"  {cas(cas_)}  {sid}  {nazev:5}  {jm}")

print("\n## Zápisy do skillů (mimo workspace)")
for cas_, sid, nazev, cesta in zaznamy:
    if ".dsh\\skills" not in cesta:
        continue
    jm = cesta.replace("\\", "/").split("/skills/")[-1]
    print(f"  {cas(cas_)}  {sid}  {nazev:5}  {jm}")

# Kdo psal po kom do stejného souboru
print("\n## Sledy: stejný soubor, dvě session")
podle = collections.defaultdict(list)
for cas_, sid, nazev, cesta in zaznamy:
    podle[cesta].append((cas_, sid, nazev))
for cesta, h in sorted(podle.items()):
    if len({s for _, s, _ in h}) < 2:
        continue
    h.sort()
    print(f"\n  {cesta.split(chr(92))[-1]}")
    for cas_, sid, nazev in h:
        print(f"    {cas(cas_)}  {sid}  {nazev}")
