# -*- coding: utf-8 -*-
r"""P27 — OBNOVA CIZÍHO ZÁZNAMU: §56 (P26) byl omylem přepsán.

CO SE STALO: při doplňování finálních čísel se nový text řádku `| **C** | Brány
po sobě …` zapsal **dvakrát** — do §57 (správně) i do **§56** (špatně; §56 je
záznam P26 a historie se NEPŘEPISUJE). Skript bere PŮVODNÍ text z `HEAD`
(commit, kde §56 ještě přepsaný nebyl) a vrací ho na PRVNÍ výskyt (tj. do §56).
"""

import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
GIT = WS / "tools" / "git.cmd"
H = WS / "HANDOFF.md"

NOVY = ("| **C** | Brány po sobě (**inventář → `g3` → `validate-all`**, ne současně) "
        "| `g3` → **49 bran**; nenulové exity **2, oba NEDEKLAROVANÉ a oba MIMO REPO**")


def git(*a):
    r = subprocess.run([str(GIT), "-C", str(WS)] + list(a), capture_output=True,
                       shell=True, timeout=120)
    return r.stdout.decode("utf-8", "replace")


orig = git("show", "HEAD:HANDOFF.md").splitlines()
kandidati = [l for l in orig if l.startswith(NOVY[:40])]
if not kandidati:
    print("CHYBA: v HEAD není původní řádek §56 (`| **C** | Brány po sobě …`)")
    sys.exit(2)
puvodni_radek = kandidati[0]
print("původní řádek z HEAD (prvních 140 znaků):")
print("   " + puvodni_radek[:140])

text = H.read_text(encoding="utf-8")
radky = text.splitlines(keepends=True)
i57 = next(n for n, l in enumerate(radky) if l.startswith("## 57. P27"))
nalezy = [n for n, l in enumerate(radky) if l.startswith(NOVY[:40])]
print("výskytů nového textu: %d (řádky %s), §57 začíná na řádku %d"
      % (len(nalezy), [n + 1 for n in nalezy], i57 + 1))
if len(nalezy) != 2:
    print("CHYBA: očekávám právě 2 výskyty (jeden v §56, jeden v §57)")
    sys.exit(2)
cil = nalezy[0]
if cil > i57:
    print("CHYBA: první výskyt je až v §57 — není co obnovovat")
    sys.exit(2)
konec = "\n" if radky[cil].endswith("\n") else ""
radky[cil] = puvodni_radek + konec
H.write_bytes("".join(radky).encode("utf-8"))

# kontroly
t2 = H.read_text(encoding="utf-8")
r2 = t2.splitlines()
i57b = next(n for n, l in enumerate(r2) if l.startswith("## 57. P27"))
prvni = [n for n, l in enumerate(r2) if l.startswith(NOVY[:40])]
print("po obnově: výskytů %d (řádky %s)" % (len(prvni), [n + 1 for n in prvni]))
ok56 = r2[prvni[0]] == puvodni_radek
ok57 = prvni[1] > i57b
print("§56 (před §57) má PŮVODNÍ text z HEAD:", ok56)
print("§57 má NOVÝ text:", ok57)
b = H.read_bytes()
print("LF:", b.count(b"\r\n") == 0, "| BOM:", b[:3] == b"\xef\xbb\xbf")
sys.exit(0 if (ok56 and ok57 and len(prvni) == 2) else 1)
