r"""Co jiná session ZAPSALA — čte záznamy `workspace/changes` a `tool/call`.

Spuštění: $env:PYTHONIOENCODING='utf-8'; python _analyza\hl2-zapisy-session.py <session-id>

`workspace/changes` je autorita: říká, které soubory se v workspace změnily
během tahů té session. `tool/call` pak řekne, čím.
"""
import collections
import json
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
sid = sys.argv[1] if len(sys.argv) > 1 else "7db45275"
p = WS / "_analyza" / f"tmp-session-{sid}.jsonl"
radky = [l for l in p.read_text(encoding="utf-8", errors="replace").split("\n") if l.strip()]

zmeny = []
cally = []
for l in radky:
    try:
        o = json.loads(l)
    except Exception:
        continue
    t = o.get("type")
    if t == "workspace/changes":
        zmeny.append(o)
    elif t == "tool/call":
        cally.append(o)

print(f"# session {sid}\n")

print(f"## workspace/changes ({len(zmeny)} záznamů) — co se změnilo")
souhrn = collections.Counter()
for z in zmeny:
    d = z.get("data") or {}
    files = d.get("files") or d.get("changes") or d
    if isinstance(files, list):
        for f in files:
            cesta = f.get("path") if isinstance(f, dict) else str(f)
            druh = f.get("kind") or f.get("type") or "?" if isinstance(f, dict) else "?"
            souhrn[(cesta, druh)] += 1
    else:
        print("   (neznamy tvar):", json.dumps(d, ensure_ascii=False)[:300])
for (c, k), n in souhrn.most_common(60):
    print(f"   {n:3}x  [{k}]  {c}")

print(f"\n## tool/call ({len(cally)}) — rozpad podle nástroje")
nastroje = collections.Counter()
zapisujici = []
for c in cally:
    d = c.get("data") or {}
    nazev = d.get("name") or d.get("tool") or "?"
    nastroje[nazev] += 1
    if nazev in ("write", "edit"):
        args = d.get("arguments") or d.get("input") or {}
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                args = {}
        cesta = args.get("file_path") or args.get("path") or "?"
        zapisujici.append((nazev, cesta))
for n, k in nastroje.most_common(25):
    print(f"   {k:4}x  {n}")

print(f"\n## Zapisující volání ({len(zapisujici)}) — soubory")
pocet = collections.Counter(c for _, c in zapisujici)
for c, n in pocet.most_common(60):
    print(f"   {n:3}x  {c}")
