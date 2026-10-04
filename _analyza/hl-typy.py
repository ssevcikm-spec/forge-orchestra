#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hloubkova analyza orchestra - Q7: ma typ, ktery model pouzil, vubec class_name?
A co presne dostal agent k dispozici (owns + owns zavislosti)."""
import os, re, sys, json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\Ssevc\Local-Deepseek"
G = os.path.join(WS, "games", "uo-shadows")

print("=== class_name v scripts/*.gd ===")
skripty = {}
for f in sorted(os.listdir(os.path.join(G, "scripts"))):
    if not f.endswith(".gd"):
        continue
    t = open(os.path.join(G, "scripts", f), encoding="utf-8", errors="replace").read()
    cn = re.findall(r"^class_name\s+(\w+)", t, re.M)
    ext = re.findall(r"^extends\s+(\w+)", t, re.M)
    funcs = re.findall(r"^func\s+(\w+)", t, re.M)
    skripty[f] = {"class_name": cn, "extends": ext, "funcs": funcs}
    print(f"  {f:18s} class_name={','.join(cn) if cn else '(ZADNY)':26s} extends={','.join(ext):10s} funcs={len(funcs)}")

print("\n=== TYPY, KTERE MODELY POUZILY A KTERE NEJSOU GLOBALNI ===")
# z merenych chyb parsovani (hl-chyby.json) + z logu
pouzite = ["GameItem", "Economy", "Skills", "World", "Merchant", "Attributes", "Player", "Item"]
globalni = {c for v in skripty.values() for c in v["class_name"]}
for t in pouzite:
    kde = [f for f, v in skripty.items() if t in v["class_name"]]
    print(f"  {t:12s} je globalni class_name: {'ANO (' + ','.join(kde) + ')' if kde else 'NE – model si typ VYMYSLIL'}")

print("\n=== CO DOSTANE AGENT: owns granule + owns JEJICH zavislosti (1. uroven) ===")
rm = json.load(open(os.path.join(G, ".forge", "roadmap.json"), encoding="utf-8"))
gr = {g["id"]: g for g in rm["grains"]}
for g in rm["grains"]:
    vlastni = g.get("owns") or []
    deps = g.get("depends_on") or []
    cteni = []
    for d in deps:
        cteni.extend(gr.get(d, {}).get("owns") or [])
    # 2. uroven (tranzitivni) - co by potreboval, aby videl smlouvy
    cteni2 = set()
    for d in deps:
        for d2 in (gr.get(d, {}).get("depends_on") or []):
            cteni2 |= set(gr.get(d2, {}).get("owns") or [])
    print(f"  {g['id']:18s} edituje={vlastni}")
    print(f"      {'':18s} cte(1.uroven)={sorted(set(cteni))}")
    if cteni2 - set(cteni):
        print(f"      {'':18s} NECTE (2.uroven)={sorted(cteni2 - set(cteni))}")

print("\n=== KOLIK Z ZAVISLOSTI MA class_name (tj. smlouvu, kterou model muze pouzit) ===")
chybi = 0
celkem = 0
for g in rm["grains"]:
    for d in (g.get("depends_on") or []):
        for f in (gr.get(d, {}).get("owns") or []):
            if f.endswith(".gd"):
                celkem += 1
                base = os.path.basename(f)
                if base in skripty and not skripty[base]["class_name"]:
                    chybi += 1
                    print(f"  bez class_name: {f}  (granule {g['id']} na ni zavisi pres {d})")
print(f"  ZMERENO: .gd souboru v zavislostech={celkem}, z toho bez class_name={chybi}")
