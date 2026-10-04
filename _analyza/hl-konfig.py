#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hloubkova analyza orchestra - konfigurace: kdo co vlastni, kde je zdroj pravdy,
ktere klice se pouzivaji a ktere jsou mrtve. Plosny Python walk (ne grep tool).
"""
import os, re, sys, json, hashlib

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\Ssevc\Local-Deepseek"
TPL = os.path.join(WS, "orchestra", "repo")
GAME = os.path.join(WS, "games", "uo-shadows")
SKIP = {".git", "node_modules", "__pycache__", ".godot", ".test"}


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


print("=== KONFIGURACNI SOUBORY: ktere existuji a co v nich je ===")
CONF = [
    ("sablona", ".forge/providers.json"),
    ("sablona", ".forge/vision-profile.json"),
    ("sablona", ".forge/roadmap.json"),
    ("sablona", ".forge/provider.env"),
    ("sablona", ".forge/provider.json"),
    ("sablona", ".forge/node/.env"),
    ("sablona", ".forge/node/.env.example"),
    ("hra", ".forge/providers.json"),
    ("hra", ".forge/vision-profile.json"),
    ("hra", ".forge/roadmap.json"),
    ("hra", ".forge/node/.env"),
]
for kde, rel in CONF:
    root = TPL if kde == "sablona" else GAME
    p = os.path.join(root, rel)
    if os.path.exists(p):
        b = open(p, "rb").read()
        print(f"  {kde:8s} {rel:34s} {len(b):7d} B  {hashlib.sha256(b).hexdigest()[:10]}")
    else:
        print(f"  {kde:8s} {rel:34s} NEEXISTUJE")

print("\n=== providers.json: zdroj pravdy pro modely ===")
for kde, root in [("sablona", TPL), ("hra", GAME)]:
    p = os.path.join(root, ".forge/providers.json")
    if not os.path.exists(p):
        print(f"  {kde}: NEEXISTUJE")
        continue
    j = json.loads(rd(p))
    print(f"  {kde}: klice={list(j.keys())}")
    provs = j.get("providers") or j.get("poskytovatele") or []
    if isinstance(provs, list):
        for pr in provs:
            if isinstance(pr, dict):
                nm = pr.get("name") or pr.get("nazev") or "?"
                sil = pr.get("strongModels") or pr.get("silne") or []
                print(f"     - {nm:12s} model={str(pr.get('model'))[:34]:34s} strong={len(sil) if isinstance(sil,list) else sil} skromny={pr.get('skromny')}")
    else:
        print(f"     (jiný tvar: {type(provs)})")

print("\n=== KDE JE PROVIDERS.JSON CITAN (runtime fetch vs kopie) ===")
for f in walk(WS):
    rel = os.path.relpath(f, WS).replace("\\", "/")
    if rel.startswith(("_analyza/", "_retired/")) or rel.startswith("orchestra/.test/"):
        continue
    if not f.lower().endswith((".mjs", ".js", ".ts", ".py", ".yml", ".yaml", ".md")):
        continue
    txt = rd(f)
    if "providers.json" in txt:
        lines = [i + 1 for i, l in enumerate(txt.splitlines()) if "providers.json" in l]
        print(f"  {rel}: {lines}")

print("\n=== VISION-PROFILE: ktere klice kod SKUTECNE cte ===")
for kde, root in [("sablona", TPL), ("hra", GAME)]:
    p = os.path.join(root, ".forge/vision-profile.json")
    if os.path.exists(p):
        j = json.loads(rd(p))
        print(f"  {kde}: klice={sorted(j.keys())}")
        print(f"     hra={j.get('hra')!r} popis_stylu={(j.get('popis_stylu') or '')[:40]!r} "
              f"role={j.get('role')} zakazy={len(j.get('zakazy') or [])} poskytovatele={len(j.get('poskytovatele') or j.get('providers') or [])}")

vm = rd(os.path.join(TPL, ".forge/vision.mjs"))
print(f"\n  vision.mjs cte klice profilu: {sorted(set(re.findall(r'profil(?:e)?[.\[]\s*[\\\"' + chr(39) + r']?([a-zA-Z_]+)', vm)))[:20]}")
for klic in ["hra", "popis_stylu", "role", "zakazy", "poskytovatele", "stropy", "ocekavany_obsah", "snimek"]:
    n = len(re.findall(r"\b" + klic + r"\b", vm))
    print(f"     {klic:20s} vyskytu ve vision.mjs: {n}")

print("\n=== VISION-PROFILE: kdo ho cte v celem strome ===")
for f in walk(WS):
    rel = os.path.relpath(f, WS).replace("\\", "/")
    if rel.startswith(("_analyza/", "_retired/")) or rel.startswith("orchestra/.test/"):
        continue
    if not f.lower().endswith((".mjs", ".js", ".ts", ".py", ".yml", ".yaml")):
        continue
    txt = rd(f)
    if "vision-profile" in txt:
        print(f"  {rel}")

print("\n=== MRTVE KLICE: acceptance / provides / kind ===")
for klic in ["acceptance", "provides", "kind"]:
    n_celk = 0
    kde = []
    for f in walk(WS):
        rel = os.path.relpath(f, WS).replace("\\", "/")
        if rel.startswith(("_analyza/", "_retired/", "games/", "orchestra/repo/")) or rel.startswith("orchestra/.test/"):
            continue
        if not f.lower().endswith((".mjs", ".js", ".ts", ".py")):
            continue
        txt = rd(f)
        m = len(re.findall(r"\b" + klic + r"\b", txt))
        if m:
            n_celk += m
            kde.append(f"{rel}({m})")
    print(f"  {klic:12s} v KODU (bez herniho repa): {n_celk}x  {', '.join(kde[:8])}")

print("\n=== BOOTSTRAP: co dostane nova hra (install-into-repo.ps1) ===")
ins = rd(os.path.join(WS, "orchestra", "install-into-repo.ps1"))
print(f"  radku={len(ins.splitlines())}")
for i, l in enumerate(ins.splitlines(), 1):
    if re.search(r"Copy-Item|New-Item|Set-Content|param\(|\$Game|\$Cil|\$Zdroj|-Force", l):
        print(f"  :{i}  {l.strip()[:130]}")

print("\n=== CO SE Z HRY NEKOPIRUJE (seznam v install-into-repo) ===")
for m in re.finditer(r"(?:vyjimk|ignor|nesync|preskoc)\w*", ins, re.I):
    print(f"  nalezeno slovo: {m.group(0)}")
