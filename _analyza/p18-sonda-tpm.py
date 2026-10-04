# -*- coding: utf-8 -*-
"""SONDA (plánovací session 2. 10. 2026): co je OPRAVDU v logu běhu #146?

PROČ: `HANDOFF.md` §17.5 (nález H5) tvrdí `TPM: Limit 8000, Requested 14398`.
Při přeměření týmž skriptem (`h17-vsechny-behy.mjs`) vyšlo
`limit 8000, zadano 2026`. Rozdíl je buď
  (a) v měřidle (regex chytá první výskyt, ne ten rozhodující), nebo
  (b) v datech (log se mezitím změnil / je stránkovaný).

Metoda: stáhne log CELÝ, najde VŠECHNY výskyty TPM hlášky, vypíše je
s okolím a spočítá, kolikrát se která dvojice (limit, requested) objevuje.

Použití:  python _analyza\\p18-sonda-tpm.py [<run_id>]
"""

import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(__file__).resolve().parent.parent
ORCH = WS / "orchestra"
REPO = "ssevcikm-spec/uo-shadows"
RUN_ID = sys.argv[1] if len(sys.argv) > 1 else "36999784822"   # #146

PAT = (ORCH / ".secrets" / "github_pat.txt").read_text(encoding="utf-8").strip()

VZOR = re.compile(r"tokens per minute \(TPM\):\s*Limit\s+(\d+),\s*Requested\s+(\d+)")


def gh(url: str) -> bytes:
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {PAT}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "p18-sonda-tpm",
    })
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


print("=" * 78)
print("P18 — SONDA: co je v logu běhu %s (repo %s)?" % (RUN_ID, REPO))
print("=" * 78)

beh = json.loads(gh(f"https://api.github.com/repos/{REPO}/actions/runs/{RUN_ID}"))
print("  run_number  :", beh.get("run_number"))
print("  head_sha    :", (beh.get("head_sha") or "")[:9])
print("  status      :", beh.get("status"), "/", beh.get("conclusion"))
print("  created_at  :", beh.get("created_at"))
print("  log velikost:", beh.get("logs_url") and "je logs_url")

job = None
for j in json.loads(gh(f"https://api.github.com/repos/{REPO}/actions/runs/{RUN_ID}/jobs")).get("jobs", []):
    if (j.get("name") or "").startswith("Agent"):
        job = j
        break
if job is None:
    print("  CHYBA: job 'Agent…' nenalezen")
    sys.exit(1)
print("  job         : #%s %s" % (job.get("id"), job.get("name")))
for s in job.get("steps", []):
    print("      %-10s %s" % (s.get("conclusion"), s.get("name")))

# Log se stahuje přes /logs (přesměruje na blob); urllib přesměrování sleduje.
print()
print("  stahuji log…")
surove = gh(f"https://api.github.com/repos/{REPO}/actions/jobs/{job['id']}/logs")
print("  staženo: %d B" % len(surove))

# POZOR: log je obarvený ANSI escape sekvencemi; TPM hláška může být
# přerušená barevným kódem. Proto se barvy nejdřív odstraní.
ANSI = re.compile(r"\x1b\[[0-9;]*m")
text = ANSI.sub("", surove.decode("utf-8", "replace"))

vsechny = VZOR.findall(text)
print()
print("  VÝSKYTŮ hlášky TPM: %d" % len(vsechny))
from collections import Counter
for (limit, req), pocet in Counter(vsechny).most_common():
    print("     limit=%s  requested=%s   %dx" % (limit, req, pocet))

print()
print("  --- všechny výskyty s 200 znaky kontextu PŘED ---")
for m in VZOR.finditer(text):
    a = max(0, m.start() - 200)
    kontext = text[a:m.end() + 60].replace("\n", " ⏎ ")
    print("   • %s" % kontext[-320:])
    print()

# Klíčová otázka: je v logu vůbec číslo 14398?
print("  obsahuje log '14398'?          :", "14398" in text)
print("  obsahuje log 'Requested 2026'? :", "Requested 2026" in text)
print("  obsahuje log 'Requested 14398'?:", "Requested 14398" in text)

m = re.search(r"\[test\] (\d+) kontrol, (\d+) selh", text)
print("  [test] souhrn v logu           :", m.group(0) if m else "NENALEZEN")
print("  výskytů '[test]' v logu        :", len(re.findall(r"\[test\]", text)))
