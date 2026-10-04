r"""Ověří, čím `kontrola-driftu.mjs` došel k hlášení „jen v šabloně".

Naměřeno 2. 10. 2026: drift hlásil `jen v šabloně (kroky): Kontrola parsování
GDScriptu (rychlá brána), Kontrola class_name ...`, ale v herním `agent.yml`
TYTÉŽ kroky jsou (ověřeno výpisem řádků `- name:`). Buď je rozdíl jinde, nebo
je vada v měřidle.

Postup: spustí se TAtÁŽ funkce `strukturaWorkflow` jako v `kontrola-driftu.mjs`
(volaná z Node, aby se neopisovala) a porovnají se množiny kroků.

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\drift-proc.py
"""
import json
import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
NODE = "node"

# Malý mjs pomocník, který vytáhne strukturu PŘESNĚ tou funkcí z nástroje.
POMOCNIK = r"""
import { readFileSync } from 'node:fs';
const cesta = process.argv[2];
const text = readFileSync(cesta, 'utf8').replace(/\r\n/g, '\n');
const radky = text.split('\n');
const vstupy = [], kroky = [], envKlice = [];
let vVstupech = false, vEnv = false;
for (const l of radky) {
  const bezKomentare = l.replace(/\s+#.*$/, '');
  if (/^\s{2,}workflow_dispatch:/.test(bezKomentare)) { vVstupech = true; vEnv = false; continue; }
  if (/^\s{2,}(permissions|concurrency|jobs):/.test(bezKomentare)) { vVstupech = false; }
  if (/^\s+- name:\s*(.+)$/.test(bezKomentare)) { kroky.push(RegExp.$1.trim()); vEnv = false; continue; }
  if (/^\s+env:\s*$/.test(bezKomentare)) { vEnv = true; continue; }
  if (vVstupech) { const m = /^\s{6}([a-z_]+):\s*$/.exec(bezKomentare); if (m) vstupy.push(m[1]); }
  if (vEnv) {
    const m = /^\s+([A-Z_]+):/.exec(bezKomentare);
    if (m) { envKlice.push(m[1]); continue; }
    if (/^\s+(run|uses|with):/.test(bezKomentare)) vEnv = false;
  }
}
console.log(JSON.stringify({ vstupy, kroky, envKlice }));
"""

pom = WS / "_analyza" / "_drift-struktura.mjs"
pom.write_text(POMOCNIK, encoding="utf-8")

sablona = WS / "orchestra/repo/.github/workflows/agent.yml"
hra = WS / "games/uo-shadows/.github/workflows/agent.yml"

vysledky = {}
for jmeno, cesta in [("šablona", sablona), ("hra", hra)]:
    r = subprocess.run([NODE, str(pom), str(cesta)], capture_output=True, shell=True)
    if r.returncode != 0:
        print("CHYBA node:", r.stderr.decode("utf-8", "replace")[:400])
        sys.exit(2)
    vysledky[jmeno] = json.loads(r.stdout.decode("utf-8"))

print("=" * 78)
print("CO VIDÍ FUNKCE `strukturaWorkflow` Z `kontrola-driftu.mjs`")
print("=" * 78)
for jmeno, v in vysledky.items():
    print(f"\n{jmeno}: vstupy={v['vstupy']}")
    print(f"  kroků: {len(v['kroky'])}")
    for k in v["kroky"]:
        print(f"    - {k}")
    print(f"  env klíčů: {len(v['envKlice'])}  (unikátních {len(set(v['envKlice']))})")

a, b = set(vysledky["šablona"]["kroky"]), set(vysledky["hra"]["kroky"])
print("\n" + "=" * 78)
print("ROZDÍL MNOŽIN KROKŮ")
print("=" * 78)
print(f"  jen v šabloně: {sorted(a - b)}")
print(f"  jen ve hře:    {sorted(b - a)}")
print(f"  společné:      {len(a & b)}")

print("\n" + "=" * 78)
print("ENV KLÍČE — jsou to MNOŽINY, nebo SEZNAM? (na tom záleží)")
print("=" * 78)
ea, eb = vysledky["šablona"]["envKlice"], vysledky["hra"]["envKlice"]
print(f"  šablona: {len(ea)} výskytů, {len(set(ea))} unikátních")
print(f"  hra:     {len(eb)} výskytů, {len(set(eb))} unikátních")
print(f"  rozdíl MNOŽIN: jen v šabloně {sorted(set(ea) - set(eb))}, jen ve hře {sorted(set(eb) - set(ea))}")
if ea != eb and set(ea) == set(eb):
    print("  → MNOŽINY JSOU SHODNÉ, liší se jen POČET VÝSKYTŮ — a to je klíčové:")
    print("     `FORGE_ATTEMPT` je v obou kopiích, ale v JINÉM KROKU. Porovnání")
    print("     množin to NEVIDÍ; vidělo by to jen porovnání podle KROKŮ.")
