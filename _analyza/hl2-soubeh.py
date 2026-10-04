# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
r"""Detekce SOUČASNÉHO PŘEPISU: soubor, který psaly DVĚ session.

Problém, který to řeší: `HANDOFF.md` a `AGENTS.md` psaly 2. 10. 2026 dvě
session současně (7cd67c66 = druhé kolo analýzy, 7db45275 = jazyk v kódu).
Když druhá zapisuje celý soubor z vlastní kopie, přepíše práci první.

Tenhle skript pro každý soubor zjistí, KTERÉ session ho psaly a KDY, a jestli
pozdější zápis mohl smazat dřívější (tzn. zda jde o `write` celého souboru,
ne o cílený `edit`).

Spuštění:
  $env:PYTHONIOENCODING='utf-8'; python _analyza\hl2-soubeh.py
"""
import collections
import json
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(_STANICE)
ROOT = pathlib.Path(r"C:\Users\Ssevc\.dsh\sessions\--C-Users-Ssevc-Local-Deepseek--")

# Rozbalene logy (tmp-session-*.jsonl) — vznikaji hl2-rozbal-session2.mjs
LOGY = sorted((WS / "_analyza").glob("tmp-session-*.jsonl"))
if not LOGY:
    print("Zadne rozbalene logy. Spust nejdriv:")
    print("  node _analyza\\hl2-rozbal-session2.mjs <session-id>")
    sys.exit(1)

print(f"# Sobeh zapisu — prochazim {len(LOGY)} rozbalenych session logu\n")

# (soubor) -> [(cas, session, nazev_toolu)]
historie = collections.defaultdict(list)

for log in LOGY:
    sid = log.stem.replace("tmp-session-", "")
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
        nazev = d.get("name") or d.get("tool") or "?"
        if nazev not in ("write", "edit"):
            continue
        args = d.get("arguments") or d.get("input") or {}
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                continue
        if not isinstance(args, dict):
            continue
        cesta = args.get("file_path") or args.get("path")
        if not cesta:
            continue
        cas = d.get("time") or o.get("time") or 0
        historie[cesta].append((cas, sid, nazev))

# Najdi soubory, ktere psaly ALESPON 2 session
kolize = {c: h for c, h in historie.items() if len({s for _, s, _ in h}) >= 2}

if not kolize:
    print("Zadny soubor nepsaly dve session soucasne.")
else:
    print("## SOUBORY PSANE VICE SESSION (kandidati na prepsani)")
    for cesta, h in sorted(kolize.items()):
        h = sorted(h, key=lambda x: x[0])
        druhy = [n for _, _, n in h]
        riziko = "VYSOKE (je tam 'write' celeho souboru)" if "write" in druhy else "nizke (jen 'edit')"
        print(f"\n  {cesta}")
        print(f"    zapisu: {len(h)}, session: {sorted({s[:8] for _, s, _ in h})}")
        print(f"    druhy:  {collections.Counter(druhy)}")
        print(f"    riziko: {riziko}")
        for cas, s, n in h[-6:]:
            print(f"      {n:6} {s[:8]}  t={cas}")

# Souhrn vsech zapisu
print("\n## Vsechny zapisovane soubory")
for cesta, h in sorted(historie.items(), key=lambda kv: -len(kv[1])):
    ss = sorted({s[:8] for _, s, _ in h})
    print(f"  {len(h):3}x  [{','.join(ss)}]  {cesta}")
