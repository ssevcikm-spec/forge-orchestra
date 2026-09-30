"""Ověří, že se všechny skilly načítají: frontmatter je platný YAML a má name+description."""

import pathlib
import re
import sys

import yaml

SKILLS = pathlib.Path(r"C:\Users\Ssevc\.dsh\skills")

chyb = 0
for d in sorted(SKILLS.iterdir()):
    if not d.is_dir():
        continue
    p = d / "SKILL.md"
    if not p.exists():
        print(f"  CHYBA {d.name}: SKILL.md chybí")
        chyb += 1
        continue
    t = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m:
        print(f"  CHYBA {d.name}: frontmatter nenalezen")
        chyb += 1
        continue
    try:
        fm = yaml.safe_load(m.group(1))
    except Exception as e:
        print(f"  CHYBA {d.name}: frontmatter není platný YAML – {e}")
        chyb += 1
        continue
    name = fm.get("name")
    desc = str(fm.get("description", ""))
    telo = len(t.splitlines())
    if name != d.name:
        print(f"  CHYBA {d.name}: name v frontmatteru je '{name}' (má být '{d.name}')")
        chyb += 1
        continue
    if not desc:
        print(f"  CHYBA {d.name}: chybí description")
        chyb += 1
        continue
    print(f"  OK   {d.name:16} řádků={telo:4} description={len(desc)} znaků")

print()
print(f"Skillů: {len([x for x in SKILLS.iterdir() if x.is_dir()])}, chyb: {chyb}")
print("VŠE OK" if chyb == 0 else "NALEZENY CHYBY")
sys.exit(0 if chyb == 0 else 1)
