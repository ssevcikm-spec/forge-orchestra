"""Hledá v herním repu čtenáře getterů, které hráč (zatím) nemá.

PROČ TO EXISTUJE: `hud.gd` obchází chybějící `hp` přes `has_method("get_hp")`
a `hud.gd`/`save.gd` se ptají i na `get_equipped`. Než obejití odstraním
(Úkol 1 bod 4 zadání), musím vědět, KDO všechno ten getter poskytuje — jinak
bych "opravil" kód, který je v pořádku (past z AGENTS.md).
"""
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOREN = "games/uo-shadows"
VZORY = ["get_hp", "get_equipped", "add_item", "remove_item", "component(", "equipped"]
PRIPONY = (".gd", ".md", ".json", ".py", ".tscn", ".cfg", ".yml")

nalezy = {v: [] for v in VZORY}
souboru = 0
for root, dirs, files in os.walk(KOREN):
    dirs[:] = [d for d in dirs if d not in (".godot", ".git")]
    for f in files:
        if not f.endswith(PRIPONY):
            continue
        p = os.path.join(root, f)
        try:
            s = open(p, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        souboru += 1
        for n, line in enumerate(s.splitlines(), 1):
            for v in VZORY:
                if v in line:
                    nalezy[v].append((p.replace("\\", "/"), n, line.strip()[:120]))

print("prohledano souboru: %d" % souboru)
for v in VZORY:
    print("\n=== %s (%d vyskytu) ===" % (v, len(nalezy[v])))
    for p, n, l in nalezy[v]:
        print("  %s:%d  %s" % (p, n, l))
