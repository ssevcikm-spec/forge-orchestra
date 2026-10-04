#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hloubkova analyza orchestra - staticka analyza conductora a sablony.
Cte KOD (komentare se odstranuji tam, kde by zkreslily vysledek).
Nic nemeni. Strojove radky = ZMERENO:.
"""
import os, re, sys, json, hashlib

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\Ssevc\Local-Deepseek"
TS = os.path.join(WS, "orchestra", "conductor", "src", "index.ts")
SQL = open(os.path.join(WS, "orchestra", "conductor", "schema.sql"), encoding="utf-8").read()
SRC = open(TS, encoding="utf-8").read()
LINES = SRC.splitlines()


def strip_comments(text):
    """Odstrani // ... a /* ... */ (bez ohledu na retezce - pro statistiku staci)."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    out = []
    for ln in text.splitlines():
        # pozor: http:// v retezci - proto hledame // jen kdyz pred nim neni :
        m = re.search(r"(?<!:)//", ln)
        out.append(ln[:m.start()] if m else ln)
    return "\n".join(out)


CODE = strip_comments(SRC)
CODE_LINES = CODE.splitlines()


def find(pattern, text=None, flags=0):
    text = CODE if text is None else text
    return [i + 1 for i, ln in enumerate(text.splitlines()) if re.search(pattern, ln, flags)]


print("=== CONDUCTOR: rozhrani (HTTP endpointy) ===")
for i, ln in enumerate(CODE_LINES, 1):
    m = re.search(r"""url\.pathname\s*===?\s*['"]([^'"]+)['"]""", ln)
    if m:
        print(f"  route {m.group(1):28s} :{i}")
    m2 = re.search(r"""pathname\.startsWith\(\s*['"]([^'"]+)['"]""", ln)
    if m2:
        print(f"  route {m2.group(1) + '*':28s} :{i}  (startsWith)")
    m3 = re.search(r"""method\s*===?\s*['"]([A-Z]+)['"]""", ln)
    if m3:
        print(f"        metoda {m3.group(1):6s}           :{i}")

print("\n=== CONDUCTOR: exportovane a hlavni funkce ===")
for i, ln in enumerate(CODE_LINES, 1):
    m = re.search(r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)", ln)
    if m:
        print(f"  fn {m.group(1):28s} :{i}")
    m = re.search(r"^(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\(", ln)
    if m:
        print(f"  const-fn {m.group(1):24s} :{i}")

print("\n=== CONDUCTOR: SQL dotazy (SELECT/INSERT/UPDATE/DELETE) ===")
sql_lines = []
for i, ln in enumerate(CODE_LINES, 1):
    if re.search(r"\b(SELECT|INSERT INTO|UPDATE|DELETE FROM)\b", ln, re.I):
        sql_lines.append(i)
        print(f"  :{i}  {ln.strip()[:120]}")
print(f"ZMERENO: conductor-sql-radku={len(sql_lines)}")

print("\n=== CONDUCTOR: tabulky v schema.sql a jejich pouziti v kodu ===")
tables = re.findall(r"CREATE TABLE IF NOT EXISTS\s+(\w+)", SQL)
for t in tables:
    n = len(find(rf"\b{t}\b"))
    print(f"  tabulka {t:12s} vyskytu-v-kodu={n}")

print("\n=== CONDUCTOR: konstanty a env ===")
for i, ln in enumerate(CODE_LINES, 1):
    m = re.search(r"^\s*(?:export\s+)?const\s+([A-Z][A-Z0-9_]*)\s*=", ln)
    if m:
        # nacti hodnotu: text po = na tomtez radku
        val = ln.split("=", 1)[1].strip().rstrip(";")
        print(f"  {m.group(1):24s} = {val[:80]:80s} :{i}")
print("  --- env.X ---")
envs = sorted(set(re.findall(r"env\.([A-Z][A-Z0-9_]*)", CODE)))
for e in envs:
    print(f"  env.{e}")

print("\n=== CONDUCTOR: kde se cte roadmap sloupec (dispatch, guard) ===")
for pat, label in [(r"rm\.updated_at", "rm.updated_at"),
                   (r"RETRY_HOURS", "RETRY_HOURS"),
                   (r"ESCALATE_AFTER", "ESCALATE_AFTER"),
                   (r"MAX_ATTEMPTS", "MAX_ATTEMPTS"),
                   (r"lockKeys", "lockKeys"),
                   (r"listGames", "listGames"),
                   (r"owns", "owns"),
                   (r"depends_on", "depends_on"),
                   (r"acceptance", "acceptance"),
                   (r"provides", "provides"),
                   (r"size_lines", "size_lines"),
                   (r"strongModels|strong", "strong")]:
    ls = find(pat)
    print(f"  {label:14s} {len(ls):3d}x  radky: {ls[:40]}")

print("\n=== SABLONA vs HRA: soubory, ktere existuji v obou ===")
TPL = os.path.join(WS, "orchestra", "repo")
GAME = os.path.join(WS, "games", "uo-shadows")


def walk(root, skip={".git", "node_modules", "__pycache__", ".godot"}):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in skip]
        for f in fn:
            yield os.path.relpath(os.path.join(dp, f), root).replace("\\", "/")


t = set(walk(TPL))
g = set(walk(GAME))
forgenode = {x for x in t if x.startswith(".forge") or x.startswith(".github")}
gnode = {x for x in g if x.startswith(".forge") or x.startswith(".github")}
both = sorted(forgenode & gnode)
only_t = sorted(forgenode - gnode)
only_g = sorted(gnode - forgenode)
print(f"ZMERENO: sablona-.forge+.github={len(forgenode)} hra={len(gnode)} shodne-jmenem={len(both)} "
      f"jen-v-sablone={len(only_t)} jen-ve-hre={len(only_g)}")

diff = []
for rel in both:
    a = open(os.path.join(TPL, rel), "rb").read()
    b = open(os.path.join(GAME, rel), "rb").read()
    if a != b:
        diff.append((rel, len(a), len(b), hashlib.sha256(a).hexdigest()[:8], hashlib.sha256(b).hexdigest()[:8]))
print(f"ZMERENO: shodne-jmenem-a-ROZDILNY-OBSAH={len(diff)}")
for rel, la, lb, ha, hb in diff:
    print(f"  ROZDIL {rel:44s} sablona={la:7d}B/{ha} hra={lb:7d}B/{hb}")
print(f"ZMERENO: jen-v-sablone={len(only_t)}")
for f in only_t:
    print(f"  JEN-SABLONA {f}")
print(f"ZMERENO: jen-ve-hre={len(only_g)}")
for f in only_g:
    print(f"  JEN-HRA {f}")

print("\n=== KDO JE V SEZNAMU DRIFT KONTROLY ===")
drift = os.path.join(WS, "orchestra", "tools", "kontrola-driftu.mjs")
if os.path.exists(drift):
    d = open(drift, encoding="utf-8").read()
    names = re.findall(r"['\"]([.\w][^'\"]*\.(?:mjs|py|json|yml|yaml|md|sh|gd))['\"]", d)
    names = sorted(set(names))
    print(f"ZMERENO: kontrola-driftu uvadi {len(names)} nazvu souboru:")
    for n in names:
        print(f"   {n}")
    print("  --- ignorovane (nesynchronizovat) ---")
    m = re.search(r"(?:IGNOROV|NESYNC|VYJIMK)\w*\s*=\s*\[([^\]]*)\]", d, re.S)
    if m:
        print("   " + " ".join(m.group(1).split())[:600])
else:
    print("  soubor NEEXISTUJE")

print("\n=== GATES v .github/workflows (sablona) ===")
wf = os.path.join(TPL, ".github", "workflows")
for f in sorted(os.listdir(wf)):
    txt = open(os.path.join(wf, f), encoding="utf-8").read()
    steps = re.findall(r"^\s*-?\s*name:\s*(.+)$", txt, re.M)
    runs = re.findall(r"^\s*run:\s*(.+)$", txt, re.M)
    cont = len(re.findall(r"continue-on-error", txt))
    print(f"  {f}: radku={len(txt.splitlines())} kroku-name={len(steps)} run={len(runs)} continue-on-error={cont}")
    for s in steps:
        print(f"      - {s.strip()[:100]}")
