#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hloubkova analyza orchestra - O7: cena zmeny. Kolik souboru se musí zmenit,
kdyz se prida hra / engine / brana / poskytovatel. A kde je kod vazany na Godot."""
import os, re, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\Ssevc\Local-Deepseek"
SKIP = {".git", "node_modules", "__pycache__", ".godot", ".test", ".npm-cache", ".wrangler", "godot"}


def walk(root, skip=SKIP):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in skip]
        for f in fn:
            yield os.path.join(dp, f)


def rd(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""


print("=== O7a: SOUBORY VAZANE NA GODOT (mimo samotnou hru) ===")
godot_soubory = []
for f in list(walk(os.path.join(WS, "orchestra", "repo"))) + list(walk(os.path.join(WS, "orchestra", "conductor"))) + \
         list(walk(os.path.join(WS, "orchestra", "tools"))):
    rel = os.path.relpath(f, WS).replace("\\", "/")
    if not rel.endswith((".py", ".mjs", ".yml", ".yaml", ".sh", ".md", ".ts", ".toml", ".json")):
        continue
    t = rd(f)
    n = len(re.findall(r"\b(godot|Godot|GODOT)\b", t))
    if n:
        godot_soubory.append((rel, n))
godot_soubory.sort(key=lambda x: -x[1])
print(f"  ZMERENO: souboru se zminkou o Godotu = {len(godot_soubory)}")
for rel, n in godot_soubory:
    print(f"    {n:4d}x  {rel}")

print("\n=== O7b: BRANY: ktere jsou spolecne a ktere Godot-specificke ===")
brany = ["check-schema.py", "check-assets.py", "check-wiring.py", "verify-level-render.py",
         "vision.mjs", "baseline.py", "files-to-edit.mjs", "check-licence.py", "pick-provider.mjs"]
for b in brany:
    cesty = [p for p in walk(WS) if os.path.basename(p) == b and "/.test/" not in p.replace("\\", "/")]
    for c in cesty:
        t = rd(c)
        g = len(re.findall(r"\b(godot|Godot|\.gd\b|tscn|res://)", t))
        print(f"    {os.path.relpath(c, WS).replace(chr(92), '/'):58s} radku={len(t.splitlines()):4d} godot-vazeb={g}")

print("\n=== O7c: KDO VSEchno by se musel zmenit pri PRIDANI HRY ===")
kroky = [
    ("registrace v D1", "POST /game (conductor/src/index.ts)"),
    ("roadmap.json hry", "novy soubor v repu hry (.forge/roadmap.json)"),
    ("tajemstvi v repu hry", "GitHub Secrets: 5 LLM klicu + FORGE_PAT + FORGE_WEBHOOK_SECRET + FORGE_CONDUCTOR_URL"),
    ("providers.json", "sdileny v orchestra (runtime fetch) — nemusi se menit"),
    ("workflows", "kopie .github/workflows/* z sablony (4 soubory)"),
    ("brany", "kopie .forge/* z sablony (13 souboru)"),
    ("profil vize", "vision-profile.json — nutno upravit pro hru"),
    ("spec.json + mapy", "assets/spec.json, assets/levels/*.json — jen ve hre, orchestra je nezna"),
    ("klic vize", "DEEPSEEK_API_KEY nebo GEMINI_API_KEY v Secrets hry"),
]
for co, kde in kroky:
    print(f"    - {co:24s} {kde}")

print("\n=== O7d: kolik souboru se zmeni pri zmene poskytovatele LLM ===")
p = os.path.join(WS, "orchestra", "repo", ".forge", "providers.json")
t = rd(p)
print(f"    providers.json v orchestře: {len(t)} B — jedna zmena, vsechny hry ji vidi (runtime fetch)")
print(f"    ale: klice zustavaji v Secrets KAZDE hry (GitHub ToS) → pridani providera = novy secret v N repech")
print(f"    a: pick-provider.mjs je v KAZDE hre (kopie) — zmena logiky = N zmen")

print("\n=== O7e: kolik kopii ma stejny soubor (sablona vs hra) ===")
TPL = os.path.join(WS, "orchestra", "repo")
GAME = os.path.join(WS, "games", "uo-shadows")
spolecne = []
for f in walk(TPL):
    rel = os.path.relpath(f, TPL)
    g = os.path.join(GAME, rel)
    if os.path.exists(g):
        spolecne.append(rel.replace("\\", "/"))
print(f"    ZMERENO: souboru existujicich v obou = {len(spolecne)}")
shod = rozdil = 0
for rel in spolecne:
    a = open(os.path.join(TPL, rel), "rb").read()
    b = open(os.path.join(GAME, rel), "rb").read()
    if a == b:
        shod += 1
    else:
        rozdil += 1
print(f"    z toho bajtove SHODNYCH = {shod}, ROZDILNYCH = {rozdil}")
print(f"    → dnes je kazda oprava v tech {rozdil} souborech prace na dvou mistech (nebo drift)")

print("\n=== O7f: co hlida drift (kterych souboru) ===")
d = rd(os.path.join(WS, "orchestra", "tools", "kontrola-driftu.mjs"))
seznam = re.findall(r"^\s*['\"]([^'\"]+)['\"]\s*,?\s*$", d, re.M)
print(f"    kontrola-driftu.mjs uvadi {len([s for s in seznam if '/' in s or s.endswith('.md')])} cest")
for s in seznam:
    if "/" in s or s.endswith(".md"):
        print(f"      {s}")
