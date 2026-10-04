#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hloubkova analyza orchestra - smlouvy: ktera pole roadmapy/granule se KDE ctou
a ktera jsou mrtva. Cte kod obou repu (sablona + hra) a workflowy."""
import os, re, sys, json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\Ssevc\Local-Deepseek"
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


def bez_komentaru(txt, jazyk):
    """Odstrani komentare - aby pole popsane v komentari nevypadalo jako pouzite."""
    if jazyk == "py":
        txt = re.sub(r'"""(?:.|\n)*?"""', "", txt)
        txt = re.sub(r"'''(?:.|\n)*?'''", "", txt)
        return "\n".join(re.sub(r"#.*$", "", l) for l in txt.splitlines())
    if jazyk == "mjs":
        txt = re.sub(r"/\*(?:.|\n)*?\*/", "", txt)
        out = []
        for l in txt.splitlines():
            m = re.search(r"(?<!:)//", l)
            out.append(l[:m.start()] if m else l)
        return "\n".join(out)
    if jazyk == "yml":
        return "\n".join(re.sub(r"(?<!\S)#.*$", "", l) for l in txt.splitlines())
    return txt


KLIC = "test"
print("=== SMLOUVA GRANULE: ktera pole se ctou V KODU (komentare odstraneny) ===")
POLE = ["id", "title", "kind", "prompt", "owns", "depends_on", "acceptance",
        "size_lines", "model", "done", "done_note", "provides"]
mista = {p: [] for p in POLE}

for root, label in [(os.path.join(WS, "orchestra", "conductor"), "conductor"),
                    (os.path.join(WS, "orchestra", "repo"), "sablona"),
                    (os.path.join(WS, "games", "uo-shadows"), "hra"),
                    (os.path.join(WS, "orchestra", "tools"), "tools")]:
    for f in walk(root):
        ext = os.path.splitext(f)[1].lower()
        if ext not in (".ts", ".mjs", ".py", ".yml", ".yaml"):
            continue
        jazyk = {"ts": "mjs", "mjs": "mjs", "py": "py", "yml": "yml", "yaml": "yml"}[ext.lstrip(".")]
        txt = bez_komentaru(rd(f), jazyk)
        rel = os.path.relpath(f, WS).replace("\\", "/")
        for p in POLE:
            # hledej jako .pole, ['pole'], "pole":, pole v JSON.parse
            if re.search(r"[.\[]\s*['\"]?" + p + r"['\"]?\s*[\]:,)]", txt) or re.search(r"\b" + p + r"\b", txt):
                n = len(re.findall(r"\b" + re.escape(p) + r"\b", txt))
                mista[p].append(f"{label}:{os.path.basename(f)}({n})")

for p in POLE:
    lst = mista[p]
    print(f"  {p:12s} {len(lst):2d} souboru  {', '.join(lst[:7])}{' ...' if len(lst) > 7 else ''}")

print("\n=== KDO CTE `acceptance` (jmenovite) ===")
for f in list(walk(os.path.join(WS, "orchestra"))) + list(walk(os.path.join(WS, "games", "uo-shadows"))):
    if os.path.splitext(f)[1].lower() not in (".ts", ".mjs", ".py", ".yml", ".yaml", ".gd", ".md"):
        continue
    txt = bez_komentaru(rd(f), "yml" if f.endswith((".yml", ".yaml")) else ("py" if f.endswith(".py") else "mjs"))
    if re.search(r"\bacceptance\b", txt):
        rel = os.path.relpath(f, WS).replace("\\", "/")
        ls = [i + 1 for i, l in enumerate(txt.splitlines()) if re.search(r"\bacceptance\b", l)]
        print(f"  {rel}: {ls}")

print("\n=== KDO CTE `provides` (jmenovite) ===")
n = 0
for f in list(walk(os.path.join(WS, "orchestra"))) + list(walk(os.path.join(WS, "games", "uo-shadows"))):
    if os.path.splitext(f)[1].lower() not in (".ts", ".mjs", ".py", ".yml", ".yaml", ".gd", ".md", ".json"):
        continue
    txt = rd(f)
    if re.search(r"\bprovides\b", txt):
        rel = os.path.relpath(f, WS).replace("\\", "/")
        print(f"  {rel}: {len(re.findall(r'provides', txt))}x")
        n += 1
print(f"  celkem souboru s 'provides': {n}")

print("\n=== INPUTS WORKFLOWU agent.yml: co conductor posila a co workflow pouziva ===")
ag = rd(os.path.join(WS, "orchestra", "repo", ".github", "workflows", "agent.yml"))
inp = re.search(r"^on:\n(?:.|\n)*?^jobs:", ag, re.M)
if inp:
    blok = inp.group(0)
    for m in re.finditer(r"^      (\w+):\n        description: (.+)$", blok, re.M):
        print(f"  input {m.group(1):16s} {m.group(2)[:80]}")
    print(f"  inputs.required: {re.findall(r'required: true', blok)}")
pouziti = sorted(set(re.findall(r"inputs\.(\w+)", ag)))
print(f"  v tele workflowu pouzite inputs: {pouziti}")

print("\n=== KROKY agent.yml, ktere rozhoduji (if:) ===")
for i, l in enumerate(ag.splitlines(), 1):
    if re.match(r"\s*if:\s*\S", l) and ("steps." in l or "inputs." in l):
        print(f"  :{i}  {l.strip()[:150]}")

print("\n=== KRITICKE KROKY: auto-merge, report, testy ===")
lines = ag.splitlines()
for vzor, popis in [(r"Pravidla – smí se to sloučit samo", "PRAVIDLA AUTO-MERGE"),
                    (r"Report do conductora", "REPORT"),
                    (r"Testy hry", "TESTY"),
                    (r"Kontrola parsování", "PARSE GATE"),
                    (r"Verdikt a vytvoření patche", "VERDIKT")]:
    for i, l in enumerate(lines, 1):
        if re.search(vzor, l):
            print(f"\n  --- {popis} (:{i}) ---")
            for j in range(i, min(i + 34, len(lines))):
                print(f"  {j+1:4d}| {lines[j][:150]}")
            break

print("\n=== CI: ktere brany a s jakym continue-on-error ===")
ci = rd(os.path.join(WS, "orchestra", "repo", ".github", "workflows", "ci.yml"))
for i, l in enumerate(ci.splitlines(), 1):
    if re.search(r"name:|run:|continue-on-error|^\s+if:", l) and re.search(r"check-|vision|run_tests|smoke|verify|baseline|exit", l):
        print(f"  :{i}  {l.strip()[:140]}")

print("\n=== GD: kolik scriptu a funkci ma hra (pro brany) ===")
gd = list(walk(os.path.join(WS, "games", "uo-shadows", "scripts"))) if os.path.isdir(os.path.join(WS, "games", "uo-shadows", "scripts")) else []
print(f"  scripts/*.gd: {len([f for f in gd if f.endswith('.gd')])}")
for f in sorted(gd):
    if f.endswith(".gd"):
        t = rd(f)
        print(f"    {os.path.basename(f):22s} radku={len(t.splitlines()):4d} funkci={len(re.findall(r'^func ', t, re.M))}")
