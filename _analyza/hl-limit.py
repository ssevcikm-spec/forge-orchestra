#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Proc auto-merge odmitl PR #28 (persist.save) a #29 (ui.hud)?

Overuje: deklarovany limit granule (max_linesOf ze size_lines, vychozi 60)
proti skutecne velikosti PR (+additions). Jen cteni.
Spusteni: $env:PYTHONIOENCODING='utf-8'; python _analyza/hl-limit.py
"""
import json
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\Ssevc\Local-Deepseek"
rm = json.load(open(WS + r"\games\uo-shadows\.forge\roadmap.json", encoding="utf-8"))


def max_lines_of(size_lines):
    """Presna replika maxLinesOf() z conductor/src/index.ts:149-153."""
    m = re.search(r"\d+", str(size_lines or ""))
    n = int(m.group(0)) if m else 0
    return n if n > 0 else 60


# velikosti PR z GitHub API (additions), zmereno 1. 10. 14:35 UTC
PR = {
    "persist.save": {"pr": 28, "add": 90, "soubory": ["scripts/save.gd", "scripts/save.gd.uid"]},
    "ui.hud": {"pr": 29, "add": 76, "soubory": ["scripts/hud.gd", "scripts/hud.gd.uid"]},
}

print("granule        | model  | size_lines   | max_lines | PR  | +radku | verdikt")
print("---------------|--------|--------------|-----------|-----|--------|--------")
for g in rm["grains"]:
    if g["id"] not in PR:
        continue
    p = PR[g["id"]]
    lim = max_lines_of(g.get("size_lines"))
    # .uid se do velikosti nepocita (agent.yml preskoci *.import|*.uid)
    skut = p["add"]
    verdikt = "ZAMITNUTO" if skut > lim else "proslo by"
    print(f"{g['id']:14s} | {str(g.get('model', 'any')):6s} | {str(g.get('size_lines', '(neni)')):12s} | "
          f"{lim:9d} | #{p['pr']:2d} | {skut:6d} | {verdikt}")

print()
print("Co z toho plyne:")
for g in rm["grains"]:
    if g["id"] not in PR:
        continue
    lim = max_lines_of(g.get("size_lines"))
    skut = PR[g["id"]]["add"]
    print(f"  {g['id']:14s} deklaruje {lim} radku, agent napsal {skut} "
          f"→ {'PR se NEsloucil' if skut > lim else 'OK'}")
print()
print("POZOR: obe granule maji 'model': chybi (tj. 'any') a 'size_lines' chybi.")
print("      Deklarovany limit je tedy vychozich 60 radku pro VSECHNY granule")
print("      krome tech, ktere maji 'size_lines' (dnes: entity.player 120,")
print("      sim.crafting 100, entity.enemy 90, sim.offline 100, engine.shell 120).")
