#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hloubkova analyza orchestra - mapa rozhrani a plosnych vazeb.
Plosne skeny = Python walk (grep tool nad rodicovskou slozkou tise preskoci .forge/.github).
"""
import os, re, sys, json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\Ssevc\Local-Deepseek"
SKIP = {".git", "node_modules", "__pycache__", ".npm-cache", ".wrangler", ".godot"}


def walk(root, skip=SKIP):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in skip]
        for f in fn:
            yield os.path.join(dp, f)


TS = os.path.join(WS, "orchestra", "conductor", "src", "index.ts")
LINES = open(TS, encoding="utf-8").read().splitlines()

print("=== MAPA ROZHRANI CONDUCTORA (vsechny vetve path ===) ===")
routes = []
for i, ln in enumerate(LINES, 1):
    for m in re.finditer(r"""path\s*===\s*['"]([^'"]+)['"]""", ln):
        met = "GET/POST"
        mm = re.search(r"""request\.method\s*===\s*['"]([A-Z]+)['"]""", ln)
        if mm:
            met = mm.group(1)
        routes.append((m.group(1), met, i))
    for m in re.finditer(r"""path\.startsWith\(\s*['"]([^'"]+)['"]""", ln):
        routes.append((m.group(1) + "*", "?", i))
    for m in re.finditer(r"""path\.match\(\s*/([^/]+)/""", ln):
        routes.append(("/" + m.group(1) + "/", "?", i))
seen = set()
uniq = []
for r, met, i in routes:
    key = (r, met)
    if key in seen:
        continue
    seen.add(key)
    uniq.append((r, met, i))
    print(f"  {r:34s} {met:9s} :{i}")
print(f"ZMERENO: conductor-endpointu={len(uniq)}")

print("\n=== KDO VOLA KTERY ENDPOINT (plosny sken, walk) ===")
names = [r for r, _, _ in uniq]
calls = {n: [] for n in names}
for f in walk(WS):
    if not f.lower().endswith((".mjs", ".js", ".ts", ".py", ".ps1", ".yml", ".yaml", ".cmd", ".md", ".json")):
        continue
    try:
        txt = open(f, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    rel = os.path.relpath(f, WS).replace("\\", "/")
    if rel.startswith("_analyza/") or "/_retired/" in rel:
        continue
    for n in names:
        if n.endswith("*"):
            pat = re.escape(n[:-1])
        elif n.startswith("/") and n.endswith("/"):
            pat = re.escape(n)
        else:
            pat = re.escape(n) + r"(?![a-zA-Z0-9_/-])"
        if re.search(pat, txt):
            calls[n].append(rel)
for n in names:
    lst = calls[n]
    print(f"  {n:30s} {len(lst):3d}x  {', '.join(lst[:6])}{' ...' if len(lst) > 6 else ''}")

print("\n=== ABSOLUTNI CESTY VE STROMU ORCHESTRA (plosny sken) ===")
pat_abs = re.compile(r"C:[\\/]Users[\\/][^\s'\"\)\]]+")
hits = {}
for f in walk(os.path.join(WS, "orchestra")):
    rel = os.path.relpath(f, WS).replace("\\", "/")
    if rel.startswith("orchestra/.test/") or rel.startswith("orchestra/tools/godot/"):
        continue
    try:
        txt = open(f, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    for m in pat_abs.finditer(txt):
        hits.setdefault(rel, []).append(m.group(0))
print(f"ZMERENO: absolutni-cesty souboru={len(hits)} vyskytu={sum(len(v) for v in hits.values())}")
for rel, vs in sorted(hits.items()):
    print(f"  {rel}: {len(vs)}x  napr. {vs[0][:70]}")

print("\n=== MISTA, KDE SE CTE ROADMAP.JSON (kdo je zdroj pravdy) ===")
for f in walk(WS):
    rel = os.path.relpath(f, WS).replace("\\", "/")
    if rel.startswith(("_analyza/", "_retired/")) or rel.startswith("orchestra/.test/"):
        continue
    if not f.lower().endswith((".mjs", ".js", ".ts", ".py", ".ps1", ".yml", ".yaml")):
        continue
    try:
        txt = open(f, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    if "roadmap" in txt.lower():
        n = len(re.findall(r"roadmap", txt, re.I))
        print(f"  {rel}: {n}x 'roadmap'")

print("\n=== TOOLS: ktere nastroje jsou zive (volane odjinud) ===")
tools_dir = os.path.join(WS, "orchestra", "tools")
tools = sorted(os.listdir(tools_dir))
others = []
for f in walk(WS):
    rel = os.path.relpath(f, WS).replace("\\", "/")
    if rel.startswith(("orchestra/tools/", "orchestra/.test/", "orchestra/tools/godot", "_analyza/", "_retired/")):
        continue
    if f.lower().endswith((".mjs", ".js", ".ts", ".py", ".ps1", ".yml", ".yaml", ".cmd", ".md", ".json", ".txt")):
        try:
            others.append((rel, open(f, encoding="utf-8", errors="replace").read()))
        except Exception:
            pass
print(f"ZMERENO: tools/{len(tools)} polozek, prohledano {len(others)} souboru mimo tools/")
zive, mrtve = [], []
for t in tools:
    if os.path.isdir(os.path.join(tools_dir, t)):
        continue
    refs = [rel for rel, txt in others if t in txt]
    # a reference z jinych tools
    in_tools = []
    for t2 in tools:
        if t2 == t or os.path.isdir(os.path.join(tools_dir, t2)):
            continue
        try:
            if t in open(os.path.join(tools_dir, t2), encoding="utf-8", errors="replace").read():
                in_tools.append(t2)
        except Exception:
            pass
    total = len(refs) + len(in_tools)
    (zive if total else mrtve).append((t, len(refs), in_tools))
print(f"ZMERENO: nastroju-v-tools={len([t for t in tools if not os.path.isdir(os.path.join(tools_dir,t))])} "
      f"zminenych-nekde={len(zive)} nezminenych-nikde={len(mrtve)}")
print("  --- nezminene nikde (kandidati na mrtvy kod) ---")
for t, a, b in mrtve:
    print(f"    {t}")
print("  --- zive (pocet referenci mimo tools) ---")
for t, a, b in sorted(zive, key=lambda x: -x[1]):
    print(f"    {t:40s} mimo={a:2d} v-tools={len(b)}")
