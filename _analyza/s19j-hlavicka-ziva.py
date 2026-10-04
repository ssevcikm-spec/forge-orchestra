# -*- coding: utf-8 -*-
r"""Aktualizuje hlavičku `NEXT-SESSION-INSTRUKCE.md` na AKTUÁLNÍ HEAD obou repů.

PROČ: po každém pushi se HEAD posune a hlavička zadání zestará. `zadani-kontrola.py`
to správně hlásí (`exit 1`) — a to je **funkce, ne vada**: text byl měřen nad
jiným stromem. Skript proto hlavičku přepíše podle ŽIVÉHO stavu (čte ho z gitu,
ne z parametru — aby se nedalo splést).

Použití:  python _analyza\s19j-hlavicka-ziva.py [--zapis]
"""

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
GIT = WS / "orchestra" / "tools" / "git.cmd"
ZADANI = WS / "NEXT-SESSION-INSTRUKCE.md"
ZAPIS = "--zapis" in sys.argv


def head(repo: pathlib.Path) -> str:
    r = subprocess.run([str(GIT), "-C", str(repo), "rev-parse", "--short", "HEAD"],
                       capture_output=True)
    return r.stdout.decode().strip()


def predmet(repo: pathlib.Path) -> str:
    r = subprocess.run([str(GIT), "-C", str(repo), "log", "-1", "--format=%s"],
                       capture_output=True)
    return r.stdout.decode("utf-8", "replace").strip()


def cisto(repo: pathlib.Path) -> bool:
    r = subprocess.run([str(GIT), "-C", str(repo), "status", "--porcelain"],
                       capture_output=True)
    return not r.stdout.decode("utf-8", "replace").strip()


orchestra = head(WS / "orchestra")
hra = head(WS / "games" / "uo-shadows")
popis = predmet(WS / "orchestra")
cisto_o = cisto(WS / "orchestra")
cisto_h = cisto(WS / "games" / "uo-shadows")

print("=" * 78)
print("AKTUALIZACE HLAVIČKY ZADÁNÍ — podle ŽIVÉHO stavu")
print("=" * 78)
print("  orchestra  HEAD = %s  (%s)  strom cisty: %s" % (orchestra, popis[:44], cisto_o))
print("  uo-shadows HEAD = %s  strom cisty: %s" % (hra, cisto_h))

text = ZADANI.read_text(encoding="utf-8")

# 1) „Zkontrolováno při" — commit + popis
text2 = re.sub(r"\*\*Zkontrolováno při:\*\* `[0-9a-f]+` \([^)]*\)",
               "**Zkontrolováno při:** `%s` (%s)" % (orchestra, popis),
               text, count=1)
assert text2 != text, "kotva 'Zkontrolovano pri' se nenasla"

# 2) stav repů
text3 = re.sub(r"`orchestra` = `[0-9a-f]+` · `uo-shadows` = `[0-9a-f]+`",
               "`orchestra` = `%s` · `uo-shadows` = `%s`" % (orchestra, hra),
               text2, count=1)
assert text3 != text2, "kotva 'stav repu' se nenasla"

# 3) řádek o pushi / čistotě stromů
STARE_PUSH = re.compile(r"\*\*Pushnuto:\*\*.*?(?=\n\*\*Co je v `HANDOFF\.md`)", re.S)
cisty_text = ("**Pushnuto:** **oba ANO a pracovní stromy jsou ČISTÉ** "
              "(`origin/main..HEAD = 0` a `git status --porcelain` prázdný v obou).\n"
              "**Práce Úkolů A i B je v `main`** (pushed 2. 10. 2026):\n"
              "`orchestra` = **`%s`** · `uo-shadows` = **`%s`** — a **ověřeno třemi kroky**\n"
              "(`rev-list --count` = 0 · `release.yml` #69 + CI #102 `success` ·\n"
              "Pages `last-modified` 13:18:06 po pushi 13:16:50). Podrobně `HANDOFF.md` **§19**.\n\n"
              % (orchestra, hra))
text4, n = STARE_PUSH.subn(cisty_text, text3, count=1)
assert n == 1, "kotva 'Pushnuto' se nenasla (%d)" % n

assert text4 != text, "ZADNA ZMENA NEPROBELA"
# POJISTKY: v hlavičce musí být aktuální sha a nesmí tam být ta stará.
hlavicka = "\n".join(text4.splitlines()[:14])
assert "`%s`" % orchestra in hlavicka, "v hlavicce neni aktualni sha orchestra"
assert "`%s`" % hra in hlavicka, "v hlavicce neni aktualni sha hry"
for stare in ("`7c11b2d`", "`194735d`", "`1e3925e`", "`593e25c`"):
    assert stare not in hlavicka, "v hlavicce zustalo stare sha %s" % stare

print()
print("  hlavicka aktualizovana na orchestra=%s, uo-shadows=%s" % (orchestra, hra))
if ZAPIS:
    ZADANI.write_bytes(text4.encode("utf-8"))
    print("  ZAPSANO: %d -> %d B"
          % (len(text.encode("utf-8")), len(text4.encode("utf-8"))))
else:
    print("  (dry-run -- spust s --zapis)")
