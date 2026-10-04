r"""Co dělala jiná session — z jejího rozbaleného logu.

Vstup:  _analyza\tmp-session-<id>.jsonl  (rozbaleno hl2-rozbal-session2.mjs)
Spuštění:
  $env:PYTHONIOENCODING='utf-8'; python _analyza\hl2-co-delala.py <session-id>

Vypíše: které nástroje session volala, které SOUBORY zapsala (write/edit),
jaké příkazy pustila, a co řekla uživateli.
"""
import collections
import json
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
sid = sys.argv[1] if len(sys.argv) > 1 else "7db45275"
p = WS / "_analyza" / f"tmp-session-{sid}.jsonl"
if not p.exists():
    print(f"CHYBI {p} — nejdriv: node _analyza\\hl2-rozbal-session2.mjs {sid}")
    sys.exit(1)

radky = [l for l in p.read_text(encoding="utf-8", errors="replace").split("\n") if l.strip()]
zapsane = collections.Counter()
cenne = collections.Counter()
prikazy = []
texty = []

for l in radky:
    try:
        o = json.loads(l)
    except Exception:
        continue
    s = json.dumps(o, ensure_ascii=False)
    for m in re.finditer(r'"(write|edit|read|pwsh|grep|glob|present|skill|subagent|todo_write)"', s):
        cenne[m.group(1)] += 1
    # zapisy souboru
    for m in re.finditer(r'"(?:file_path|path)"\s*:\s*"([^"]+)"', s):
        zapsane[m.group(1).replace("\\\\", "\\")] += 1
    # prikazy
    for m in re.finditer(r'"command"\s*:\s*"((?:[^"\\]|\\.){0,500})"', s):
        prikazy.append(m.group(1))
    # textové zprávy asistenta
    if o.get("type") in ("message", "assistant/message", "text"):
        d = o.get("data") or {}
        for k in ("text", "content", "message"):
            v = d.get(k) if isinstance(d, dict) else None
            if isinstance(v, str) and len(v) > 40:
                texty.append(v)

print(f"# session {sid}: {len(radky)} radku\n")

print("## Soubory zminene v tool callech")
for c, n in zapsane.most_common(50):
    print(f"  {n:4}x  {c}")

print(f"\n## Prikazy ({len(prikazy)}) — hledam zapisujici")
zajimave = [c for c in prikazy if re.search(r"git |Set-Content|Out-File|New-Item|Remove-Item|Move-Item|Copy-Item|>>|>", c)]
for c in zajimave[-40:]:
    print("  " + c.replace("\\n", " ").replace("\\r", "")[:170])
print(f"  (zapisujicich/podezrelych: {len(zajimave)} z {len(prikazy)})")
