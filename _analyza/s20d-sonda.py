# -*- coding: utf-8 -*-
r"""Sonda: zmizí z `NEXT-SESSION-INSTRUKCE.md` oddíl „## 6." při přepisu?"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
t = (WS / "NEXT-SESSION-INSTRUKCE.md").read_text(encoding="utf-8")

K6 = "## 6. Kde jsme v projektu"
print("v ORIGINÁLE: '## 6.' na indexu %d (z %d)" % (t.find(K6), len(t)))

# Zopakuj kroky skriptu a u každého nahlásit, jestli tam „## 6." ještě je.
i = t.find("### Úkol 1 — zastavit plýtvání běhy ⚠ NEJDŘÍV")
j = t.find("### Úkol 2 — commit a push OBOU repů")
print("Úkol1 na %d, Úkol2 na %d" % (i, j))

NOVY_U1 = "### Úkol 1 — granule `tests.harness` (rozhodnuto uživatelem)\n\ntext\n"
t1 = t[:i] + NOVY_U1 + "\n" + t[j:]
print("po nahrazení Úkolu 1: '## 6.' = %d, délka %d" % (t1.find(K6), len(t1)))

NOVY_U2 = "### Úkol 2 — ✅ COMMIT a PUSH obou repů je HOTOVÝ (2. 10. 2026)\n\ntext\n"
k = t1.find("### Úkol 2 — commit a push OBOU repů")
t2 = t1[:k] + NOVY_U2 + "\n"
print("po nahrazení Úkolu 2: '## 6.' = %d, délka %d" % (t2.find(K6), len(t2)))

i3 = t2.find("### Úkol 3 — granule")
print("starý '### Úkol 3 — granule' na %d" % i3)
i4 = t2.find("### Úkol 4 —", i3) if i3 > 0 else -1
print("'### Úkol 4 —' na %d" % i4)
if i3 > 0 and i4 > i3:
    t3 = t2[:i3] + t2[i4:]
    print("po smazání starého Úkolu 3: '## 6.' = %d, délka %d" % (t3.find(K6), len(t3)))
    print("   obsahuje '## 4. Co NEDĚLAT'? %s" % ("## 4. Co NEDĚLAT" in t3))
    print("   obsahuje '## 5. Hotovo'?     %s" % ("## 5. Hotovo" in t3))
    # kde skončil starý Úkol 3 a co po něm následovalo
    print()
    print("   okolí indexu %d (konec starého Úkolu 3):" % i4)
    print("   %r" % t2[i4:i4 + 200])
