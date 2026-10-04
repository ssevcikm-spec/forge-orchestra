# -*- coding: utf-8 -*-
"""SONDA 8 — spustí `main()` z nástroje s PODSTRČENÝMI daty a vypíše rozhodnutí.

Obejde se bez opisu logiky: zdroj nástroje se načte, přejmenuje se volání
`main()` v `__main__` bloku a funkce se zavolá ručně. Tím se měří **týž kód**,
který běží v bráně (`overovani` §10.5).
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
CESTA = WS / "_analyza" / "audit2b-cisla-proti-zdroji.py"
zdroj = CESTA.read_text(encoding="utf-8")

# Vyřízneme TĚLO funkce `je_citace` ze zdroje a spustíme ho samostatně.
i = zdroj.index("    def je_citace(")
j = zdroj.index("    # ── REGISTR BRAN", i)
telo = zdroj[i:j]
# odsazení 4 → 0
telo = "\n".join(l[4:] if l.startswith("    ") else l for l in telo.splitlines())

ns = {"re": re}
exec("UVOZOVKY = [(\"„\", \"“\"), (\"„\", '\"'), ('\"', '\"'), (\"`\", \"`\"), (\"*„\", \"“\")]\n"
     + telo, ns)
je_citace = ns["je_citace"]

text = (WS / "HANDOFF.md").read_text(encoding="utf-8")
print("=" * 100)
print("  VOLÁNÍ `je_citace()` ZE ZDROJE NÁSTROJE")
print("=" * 100)
for m in re.finditer(r"(\d+)\s+sloupc", text):
    radek = text[:m.start()].count("\n") + 1
    if radek not in (628, 743):
        continue
    vysledek = je_citace(text, m.start())
    print("  HANDOFF.md:%d  pos=%d  tvrdí %s  → je_citace = %s"
          % (radek, m.start(), m.group(1), vysledek))
    print("      kontext: %r" % text[max(0, m.start() - 40):m.start() + 14])
