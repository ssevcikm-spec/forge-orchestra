# -*- coding: utf-8 -*-
r"""Push obou repů s PAT ze souboru — bez vypsání tajemství.

PROČ SKRIPTEM: `git push` s PAT se dělá přes
`-c http.extraHeader="AUTHORIZATION: basic <b64>"`. Kdyby se to psalo do
příkazové řádky, **PAT se objeví v historii příkazů** — a to `AGENTS.md`
zakazuje („nikdy ho nevypisuj ani ho nepiš do historie příkazů").

Skript proto:
  1. přečte PAT ze `orchestra\.secrets\github_pat.txt`,
  2. sestaví Basic hlavičku (`base64("x-access-token:<PAT>")`),
  3. spustí push **jako seznam argumentů** (ne shellový řetězec),
  4. **vypíše jen to, co je bezpečné** — a ověří, že výstup PAT neobsahuje.

Použití:  python _analyza\p19-push.py [orchestra|hra|oba]
"""

import base64
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
GIT = WS / "orchestra" / "tools" / "git.cmd"
PAT_SOUBOR = WS / "orchestra" / ".secrets" / "github_pat.txt"

REPA = {
    "orchestra": WS / "orchestra",
    "hra": WS / "games" / "uo-shadows",
}

pat = PAT_SOUBOR.read_text(encoding="utf-8").strip()
assert pat, "PAT je prázdný"
assert len(pat) > 20, "PAT je podezřele krátký"
hlavicka = "AUTHORIZATION: basic " + base64.b64encode(
    ("x-access-token:" + pat).encode("utf-8")).decode("ascii")

cil = sys.argv[1] if len(sys.argv) > 1 else "oba"
jmena = ["orchestra", "hra"] if cil == "oba" else [cil]
assert all(j in REPA for j in jmena), "neznámý rep: %s" % cil

print("=" * 78)
print("PUSH — %s (PAT načten ze souboru, do výstupu se nedostane)" % ", ".join(jmena))
print("=" * 78)

vse_ok = True
for jmeno in jmena:
    repo = REPA[jmeno]
    print()
    print("── %s (%s) ──" % (jmeno, repo))
    pred = subprocess.run([str(GIT), "-C", str(repo), "rev-parse", "--short", "HEAD"],
                          capture_output=True)
    print("   HEAD před pushem: %s" % pred.stdout.decode().strip())

    r = subprocess.run(
        [str(GIT), "-C", str(repo), "-c", "http.extraHeader=" + hlavicka,
         "push", "origin", "HEAD:main"],
        capture_output=True)
    vystup = (r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace"))
    # POJISTKA: kdyby se PAT objevil ve výstupu, NESMÍ se vypsat.
    if pat in vystup:
        vystup = vystup.replace(pat, "<PAT-ODSTRANEN>")
        print("   ! POZOR: PAT byl ve výstupu gitu — odstraněn")
    for radek in vystup.strip().splitlines()[-6:]:
        print("   %s" % radek)
    print("   push exit=%d" % r.returncode)
    if r.returncode != 0:
        vse_ok = False

print()
print("=" * 78)
print("VÝSLEDEK: %s" % ("oba pushy prošly" if vse_ok else "NĚKTERÝ PUSH SELHAL"))
sys.exit(0 if vse_ok else 1)
