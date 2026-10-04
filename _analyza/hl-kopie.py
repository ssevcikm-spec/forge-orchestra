#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hloubkova analyza orchestra - trojice vision.test.mjs, .env lavice, modelovy retezec.
Meri, co se v ktere kopii lisi (po odstraneni komentaru) a co to znamena."""
import os, re, sys, hashlib, json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\Ssevc\Local-Deepseek"
KOPIE = [
    ("root (osirely)", os.path.join(WS, "vision.test.mjs")),
    ("sablona", os.path.join(WS, "orchestra", "repo", ".forge", "node", "vision.test.mjs")),
    ("hra", os.path.join(WS, "games", "uo-shadows", ".forge", "node", "vision.test.mjs")),
]


def rd(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        return None


def bez_kom(t):
    t = re.sub(r"/\*(?:.|\n)*?\*/", "", t)
    out = []
    for l in t.splitlines():
        m = re.search(r"(?<!:)//", l)
        out.append(l[:m.start()] if m else l)
    return "\n".join(out)


print("=== TRI KOPIE vision.test.mjs ===")
data = {}
for label, p in KOPIE:
    t = rd(p)
    if t is None:
        print(f"  {label:16s} NEEXISTUJE")
        continue
    b = open(p, "rb").read()
    data[label] = t
    print(f"  {label:16s} {len(b):7d} B  sha256={hashlib.sha256(b).hexdigest()[:12]}  radku={len(t.splitlines())}  test()={len(re.findall(r'\btest\(', t))}")

# jmena testu (title stringy)
print("\n  --- jmena testu v kazde kopii ---")
jmena = {}
for label, t in data.items():
    js = re.findall(r"test\(\s*['\"`](.+?)['\"`]", t)
    jmena[label] = js
    print(f"  {label}: {len(js)} testu")
vse = set()
for js in jmena.values():
    vse |= set(js)
print(f"\n  --- srovnani ({len(vse)} ruznych jmen) ---")
for j in sorted(vse):
    ma = "".join("X" if j in jmena.get(l, []) else "." for l in KOPIE if l in data)
    print(f"    [{ma}] {j[:90]}")

print("\n=== VISION.MJS: jsou kopie shodne? ===")
for label, p in [("sablona", os.path.join(WS, "orchestra", "repo", ".forge", "vision.mjs")),
                 ("hra", os.path.join(WS, "games", "uo-shadows", ".forge", "vision.mjs"))]:
    b = open(p, "rb").read()
    print(f"  {label:10s} {len(b):7d} B  sha256={hashlib.sha256(b).hexdigest()}")

print("\n=== .env SOUBORY: ktere existuji, co obsahuji (hodnoty skryty) ===")
ENVY = [
    ("sablona", os.path.join(WS, "orchestra", "repo", ".forge", "node", ".env")),
    ("sablona", os.path.join(WS, "orchestra", "repo", ".forge", "provider.env")),
    ("sablona", os.path.join(WS, "orchestra", "repo", ".forge", "provider.json")),
    ("hra", os.path.join(WS, "games", "uo-shadows", ".forge", "node", ".env")),
    ("hra", os.path.join(WS, "games", "uo-shadows", ".forge", "provider.env")),
    ("hra", os.path.join(WS, "games", "uo-shadows", ".forge", "provider.json")),
]
for kde, p in ENVY:
    t = rd(p)
    if t is None:
        print(f"  {kde:8s} {os.path.relpath(p, WS):56s} NEEXISTUJE")
    else:
        klice = [l.split("=")[0].strip() for l in t.splitlines() if "=" in l and not l.strip().startswith("#")]
        print(f"  {kde:8s} {os.path.relpath(p, WS):56s} klice={klice}")

print("\n=== KDO CTE .env VE HRE A SABLONE (ktere promenne) ===")
for f in ["orchestra/repo/.forge/pick-provider.mjs", "orchestra/repo/.forge/node/worker.mjs",
          "orchestra/repo/.forge/report.mjs", "orchestra/repo/.forge/node/providers-check.mjs"]:
    p = os.path.join(WS, f.replace("/", os.sep))
    t = rd(p)
    if t is None:
        print(f"  {f}: NEEXISTUJE")
        continue
    prom = sorted(set(re.findall(r"process\.env\.([A-Z_][A-Z0-9_]*)", t)) |
                  set(re.findall(r"process\.env\[['\"]([A-Z_][A-Z0-9_]*)['\"]\]", t)))
    print(f"  {os.path.basename(f):24s} {prom}")

print("\n=== MODELOVY RETEZEC: co je v providers.json (uplne) ===")
pj = json.loads(rd(os.path.join(WS, "orchestra", "repo", ".forge", "providers.json")))
for pr in pj["providers"]:
    print(f"  {pr.get('name'):12s} base={pr.get('baseUrl') or pr.get('url')}")
    for k, v in pr.items():
        if k in ("name", "baseUrl", "url"):
            continue
        print(f"      {k}: {json.dumps(v, ensure_ascii=False)[:150]}")

print("\n=== GEMINI A KLICE: ktere workflowy nastavuji ktere klice ===")
import glob
for f in glob.glob(os.path.join(WS, "orchestra", "repo", ".github", "workflows", "*.yml")) + \
         glob.glob(os.path.join(WS, "games", "uo-shadows", ".github", "workflows", "*.yml")):
    t = rd(f)
    kl = sorted(set(re.findall(r"secrets\.([A-Z_][A-Z0-9_]*)", t)) | set(re.findall(r"vars\.([A-Z_][A-Z0-9_]*)", t)))
    print(f"  {os.path.relpath(f, WS).replace(chr(92), '/'):58s} secrets={kl}")
