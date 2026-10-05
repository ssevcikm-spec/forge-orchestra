# -*- coding: utf-8 -*-
"""Sonda: co konkrétně volá `join(` v souborech, které doplnění importu přeskočilo."""
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = pathlib.Path(r"E:\Workspaces\forge-orchestra")
HRA = WS.parent / "uo-shadows"

CIL = [
    (WS, "_analyza/dsh-session-prehled.mjs"),
    (WS, "_analyza/js-tokeny.mjs"),
    (WS, "conductor/src/index.ts"),
    (WS, "repo/.forge/files-to-edit.mjs"),
    (WS, "repo/.forge/node/mock-conductor.mjs"),
    (WS, "repo/.forge/node/provider-choice.test.mjs"),
    (WS, "tools/mock-conductor.mjs"),
    (HRA, ".forge/files-to-edit.mjs"),
    (HRA, ".forge/node/mock-conductor.mjs"),
    (HRA, ".forge/node/provider-choice.test.mjs"),
]

for koren, rel in CIL:
    p = koren / rel
    print("=" * 70)
    print("###", rel)
    if not p.is_file():
        print("   NENÍ")
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    for i, l in enumerate(t.splitlines(), 1):
        if re.search(r"\b(join|dirname|resolve|basename)\s*\(", l):
            print(f"   {i}: {l.strip()[:120]}")
    print("   --- importy ---")
    for i, l in enumerate(t.splitlines(), 1):
        if l.strip().startswith("import ") or "require(" in l:
            print(f"   {i}: {l.strip()[:120]}")
