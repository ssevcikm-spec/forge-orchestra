# -*- coding: utf-8 -*-
"""P16/A5 — ověření ČÍSEL, která P15 zapsala k H80–H83 (a H79).

Každé tvrzení se měří jinudy, než jak vzniklo:

| # | Co P15 tvrdí | Jak to měřím tady |
|---|---|---|
| H80 | vada H70 byla v souboru DVAKRÁT | **v gitu není stav před P15** → měřím, že to z gitu doložit NELZE (a že dnešní stav je 0 v kódu) |
| H81 | `g3` měl nadpis „prošly" u brány s `exit=2` | čtu KÓD `g3-brany.py`: nadpis ani text nesmí tvrdit „prošly" a musí vypisovat `exit` |
| H82 | buňka `tento koren (*.md)` má taky apostrof → prázdný seznam = CHYBA | **fixtura stanice**, kde je seznam prázdný / dvojznačný → brána MUSÍ skončit `exit 1` |
| H83 | push hry byl odmítnut (stale tracking ref) a řešen MERGEM, ne force pushem | **topologie gitu**: `44dd454` je merge se DVĚMA rodiči a remote commit `7ad8d04` je jeho předek (nic se nepřepsalo) |
"""

import ast
import os
import pathlib
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
HRA = WS.parent / "uo-shadows"
ANALYZA = WS / "_analyza"
GIT = str(WS / "tools" / "git.cmd")
G3 = ANALYZA / "g3-brany.py"
VS = WS / "tools" / "verify-setup.py"
FIX = ANALYZA / "p16a5-stanice"

kontrol = 0
chyb = 0


def zk(ok, popis, detail=""):
    global kontrol, chyb
    kontrol += 1
    if ok:
        print(f"  OK   {popis}" + (f"  [{detail}]" if detail else ""))
    else:
        chyb += 1
        print(f"  CHYBA {popis}" + (f"  [{detail}]" if detail else ""))


def git(cesta, *args):
    r = subprocess.run([GIT, "-C", str(cesta), *args], capture_output=True, shell=True)
    return (r.returncode, (r.stdout or b"").decode("utf-8", "replace").strip())


print("=" * 78)
print("P16/A5 — čísla P15 u nálezů H80–H83")
print("=" * 78)

# ── H80 ────────────────────────────────────────────────────────────────────
print("\n--- H80: vada H70 byla v souboru DVAKRÁT ---------------------------")
_, bez = git(WS, "show", "ce49234~1:_analyza/zadani-kontrola.py")
_, s = git(WS, "show", "ce49234:_analyza/zadani-kontrola.py")
zk("nepodařilo přiřadit" not in bez,
   "`ce49234~1` (P13b) větev H70 VŮBEC NEOBSAHUJE → stav před P15 v gitu NENÍ "
   "(P13c+P14+P15 se commitly společně)")
zk(s.count("for j, _ in zivy") >= 2 and bez.count("for j, _ in zivy") == 0,
   "H80 tedy NELZE z gitu nezávisle doložit — doklad je jen test P15; "
   "nezávisle je doloženo, že DNES je v KÓDU 0 (měřidlo A1)",
   f"pred={bez.count('for j, _ in zivy')} po={s.count('for j, _ in zivy')} (v komentářích)")

# ── H81 ────────────────────────────────────────────────────────────────────
print("\n--- H81: g3 tvrdil prošly o bráně s exit=2 -------------------------")
zdroj_g3 = G3.read_text(encoding="utf-8")
radky = [l for l in zdroj_g3.splitlines() if "BRÁNY BEZ ČÍTAČE" in l]
print(f"  nadpis sekce: {radky[0].strip() if radky else '—'}")
zk(bool(radky) and "prošly" not in radky[0].lower(),
   "nadpis sekce už NETVRDÍ „prošly“", radky[0].strip()[:70] if radky else "—")
zk("exit=%s" in zdroj_g3,
   "a u každé takové brány se VYPISUJE exit kód (`exit=%s`)")

# ── H82 ────────────────────────────────────────────────────────────────────
print("\n--- H82: prázdný / dvojznačný seznam = CHYBA, ne tichý úbytek -------")
if FIX.exists():
    shutil.rmtree(FIX)
FIX.mkdir(parents=True)
(FIX / "nastroj-a").mkdir()
(FIX / "nastroj-b").mkdir()


def spust_vs(obsah_agents):
    (FIX / "AGENTS.md").write_text(obsah_agents, encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["FORGE_STANICE"] = str(FIX)
    r = subprocess.run([sys.executable, str(VS)], capture_output=True,
                       cwd=str(WS), env=env)
    v = (r.stdout or b"").decode("utf-8", "replace") \
        + (r.stderr or b"").decode("utf-8", "replace")
    m = re.search(r"ZMĚŘENO:\s*(\d+) kontrol,\s*(\d+) chyb", v)
    return r.returncode, v, (m.groups() if m else (None, None))


# (a) seznam je PRÁZDNÝ — v řádku je jen popis místa s jedním apostrofem
kod_a, v_a, (n_a, ch_a) = spust_vs(
    "| Co | Kde | Poznámka |\n|---|---|---|\n"
    "| **dokumenty STANICE** | tento koren (`*.md`) | popis místa, ne seznam |\n"
    "| **nástroje stanice** | `nastroj-a`, `nastroj-b` | dvě složky |\n")
print(f"  (a) prázdný seznam: exit={kod_a}, {n_a} kontrol, {ch_a} chyb")
zk(kod_a == 1, "prázdný seznam dokumentů shodí bránu (`exit 1`)", f"exit={kod_a}")
zk("vzory v dokumentech se rozvinuly (0 jmen)" in v_a,
   "a je to VIDĚT jako pojmenovaná vada („0 jmen“)")

# (b) DVOJZNAČNÝ seznam — dvě buňky se stejným počtem položek
kod_b, v_b, (n_b, ch_b) = spust_vs(
    "| Co | Kde | Poznámka |\n|---|---|---|\n"
    "| **dokumenty STANICE** | `README.md`, `AGENTS.md` | `a`, `b` |\n"
    "| **nástroje stanice** | `nastroj-a`, `nastroj-b` | dvě složky |\n")
print(f"  (b) dvojznačný: exit={kod_b}, {n_b} kontrol, {ch_b} chyb")
zk(kod_b == 1, "DVOJZNAČNÝ řádek taky skončí `exit 1` (ne tichým výběrem)",
   f"exit={kod_b}")

# ── H83 ────────────────────────────────────────────────────────────────────
print("\n--- H83: push hry řešen MERGEM, ne force pushem --------------------")
_, rodice = git(HRA, "rev-list", "--parents", "-1", "44dd454")
casti = rodice.split()
print(f"  rodiče 44dd454: {casti[1:]}")
zk(len(casti) == 3, "`44dd454` je MERGE (dva rodiče)", f"{len(casti) - 1}")
kod, _ = git(HRA, "merge-base", "--is-ancestor", "7ad8d04", "44dd454")
zk(kod == 0, "commit orchestry `7ad8d04` (PR #37) je PŘEDEK `44dd454` "
   "→ cizí práce se NEPŘEPSALA (force push by ji zahodil)")
_, pred = git(HRA, "rev-list", "--count", "7ad8d04..44dd454")
print(f"  commitů mezi 7ad8d04 a 44dd454: {pred}")
_, local = git(HRA, "rev-parse", "--short", "HEAD")
zk(local == "44dd454", "a lokální HEAD hry je pořád `44dd454`", local)

print("\n" + "=" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
print("=" * 78)
sys.exit(1 if chyb else 0)
