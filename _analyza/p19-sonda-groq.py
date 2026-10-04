# -*- coding: utf-8 -*-
r"""SONDA: je Groqův limit opravdu jen TPM 8 000, nebo je to něco jiného?

OTÁZKA UŽIVATELE (2. 10. 2026): „Není 8k tokenů nějak málo? Neblbne to náhodou?"

Odpověď se NESMÍ dělat dojmem — hledá se v logu běhu #146 (`litellm` to hlásí
sám) a porovnává se s tím, co o Groqu říká `providers.json`.

Co skript hledá:
  1. KAŽDÝ řádek s `token` v logu (celý okolní kontext hlášky),
  2. jestli je v hlášce `Request too large` (limit na JEDEN request) nebo
     `rate limit` (limit na minutu) — to je zásadní rozdíl,
  3. co o Groqu tvrdí `providers.json` (denní strop) — a je-li to v rozporu.

Použití:  python _analyza\p19-sonda-groq.py
"""

import json
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
LOG = WS / "_analyza" / "p18-log-36999784822.txt"

assert LOG.is_file(), "chybí log %s (stáhni ho: node _analyza/p18-stahni-log.mjs 36999784822)" % LOG

# Log z GitHubu má ANSI barvy; bez jejich odstranění vzory nesedí.
ANSI = re.compile(r"\x1b\[[0-9;]*m")
text = ANSI.sub("", LOG.read_text(encoding="utf-8", errors="replace"))

print("=" * 78)
print("P19 — JE GROQŮV LIMIT OPRAVDU 8 000 TOKENŮ? (z logu, ne z dojmu)")
print("=" * 78)
print("  log: %s (%d znaků po odstranění ANSI)" % (LOG.name, len(text)))

# ── 1) všechny hlášky o tokenech ────────────────────────────────────────────
print()
print("A) VŠECHNY ŘÁDKY S 'token' (hledá se v logu, ne v dokumentaci)")
print("-" * 78)
radky = [l.strip() for l in text.splitlines() if "token" in l.lower()]
print("  řádků s 'token': %d" % len(radky))
from collections import Counter
cistem = Counter()
for l in radky:
    # odstranit prefix s časem a ANSI zbytky, ať se dají seskupit
    c = re.sub(r"^\d{4}-\d{2}-\d{2}T[\d:.]+Z\s*", "", l)
    cistem[c[:150]] += 1
for radek, pocet in cistem.most_common(12):
    print("   %3dx  %s" % (pocet, radek))

# ── 2) KLÍČOVÁ OTÁZKA: je to limit na request, nebo na minutu? ─────────────
print()
print("B) JE TO LIMIT NA JEDEN REQUEST, NEBO NA MINUTU?")
print("-" * 78)
vzory = {
    "Request too large": r"Request too large",
    "rate limit reached": r"rate limit reached",
    "tokens per minute (TPM)": r"tokens per minute \(TPM\)",
    "tokens per day (TPD)": r"tokens per day \(TPD\)",
    "requests per minute (RPM)": r"requests per minute \(RPM\)",
    "rate_limit_exceeded": r"rate_limit_exceeded",
    "429": r"\b429\b",
}
for popis, v in vzory.items():
    print("   %-28s %dx" % (popis, len(re.findall(v, text))))

# ── 3) celá hláška, jak je (včetně zalomení) ───────────────────────────────
print()
print("C) CELÁ HLÁŠKA (spojí se zalomené řádky, aby bylo vidět, co se žádalo)")
print("-" * 78)
# Spojit log do jednoho proudu bez prefixů s časem — teprve pak je hláška celá.
bez_casu = re.sub(r"\d{4}-\d{2}-\d{2}T[\d:.]+Z\s*", "", text)
i = bez_casu.find("Request too large")
if i < 0:
    print("  CHYBA: 'Request too large' v logu není")
else:
    usek = bez_casu[i:i + 900]
    print("  " + usek.replace("\n", " ⏎ ")[:900])

# ── 4) kolik tokenů si Aider sám hlásil ────────────────────────────────────
print()
print("D) CO O TOKENECH HLÁSÍ AIDER SÁM (jeho vlastní čísla, ne moje odhad)")
print("-" * 78)
aider = re.findall(r"Tokens:\s*([\d.]+k?)\s*sent,\s*([\d.]+k?)\s*received", bez_casu)
print("  'Tokens: X sent, Y received'  %d×" % len(aider))
for s, r in aider[:10]:
    print("     sent %s, received %s" % (s, r))
for vzor in (r"context window[^\n]{0,80}", r"using sane defaults[^\n]{0,60}",
             r"Unknown context window[^\n]{0,60}"):
    for m in re.findall(vzor, bez_casu)[:3]:
        print("     %s" % m.strip())

# ── 5) co o Groqu tvrdí providers.json ─────────────────────────────────────
print()
print("E) CO O GROQU TVRDÍ REPO (a je to v rozporu s logem?)")
print("-" * 78)
prov = json.loads((WS / "games" / "uo-shadows" / ".forge" / "providers.json").read_text(encoding="utf-8"))
for p in prov.get("providers", []):
    if p["name"] == "groq":
        for k, v in p.items():
            if k.startswith("_"):
                print("   %s:" % k)
                print("     %s" % str(v)[:400])
            else:
                print("   %-14s %s" % (k, v))
