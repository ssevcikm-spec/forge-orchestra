# -*- coding: utf-8 -*-
"""Co přesně zapsala souběžná session (měřeno v jednom okamžiku)."""

import datetime
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
SK = pathlib.Path.home() / ".dsh" / "skills"

print("=" * 92)
print("SNÍMEK STAVU — %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 92)
print()

for jmeno in ("HANDOFF.md", "NEXT-SESSION-INSTRUKCE.md", "PLAN-DALSI-KROK.md",
              "KRONIKA-PROJEKTU.md", "AGENTS.md"):
    p = WS / jmeno
    s = p.read_text(encoding="utf-8")
    print("  %-28s %8d B  %5d řádků   mtime %s"
          % (jmeno, p.stat().st_size, len(s.splitlines()),
             datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime("%H:%M:%S")))
print()
print("  Poslední oddíly HANDOFF.md:")
h = (WS / "HANDOFF.md").read_text(encoding="utf-8")
for L in [l for l in h.splitlines() if l.startswith("## ")][-4:]:
    print("      %s" % L[:92])
print()
print("  Sekce skillu overovani:")
o = (SK / "overovani" / "SKILL.md").read_text(encoding="utf-8")
for L in [l for l in o.splitlines() if l.startswith("## ")]:
    print("      %s" % L[:92])
print()
print("  Hlavička NEXT-SESSION-INSTRUKCE.md:")
n = (WS / "NEXT-SESSION-INSTRUKCE.md").read_text(encoding="utf-8")
for L in n.splitlines()[:12]:
    if L.strip():
        print("      %s" % L[:104])
