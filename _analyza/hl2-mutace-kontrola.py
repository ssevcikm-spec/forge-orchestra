# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
r"""Mutační test kontroly `hl2-kontrola.py` — ověří, že kontrola umí SPADNOUT.

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\hl2-mutace-kontrola.py

Bez tohohle testu je „VYSLEDEK: vsech 9 bodu splneno" jen zelená, o které
nevíme, jestli není slepá (AGENTS.md: „Napsal jsi test? Vrať do kódu vadu
a podívej se, že spadne.").
"""
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(_STANICE)
DOK = WS / "ANALYZA-HLOUBKOVA-ORCHESTRA-2.md"
KONTROLA = WS / "_analyza" / "hl2-kontrola.py"

orig = DOK.read_text(encoding="utf-8")


def spust():
    r = subprocess.run([sys.executable, str(KONTROLA)], capture_output=True, text=True, encoding="utf-8")
    chybi = [l.strip() for l in r.stdout.splitlines() if "CHYBI" in l]
    return r.returncode, chybi


CHYBY = []


def mutace(nazev, uprava, ocakavany_exit):
    DOK.write_text(uprava(orig), encoding="utf-8")
    kod, chybi = spust()
    ok = (kod != 0) == (ocakavany_exit != 0)
    print(("  OK   " if ok else "  CHYBI ") + f"{nazev}: exit={kod} (ocekavan {'nenulovy' if ocakavany_exit else 'nulovy'})")
    for c in chybi:
        print("         " + c)
    if not ok:
        CHYBY.append(nazev)


print("=== Mutacni test kontroly (kazda mutace musí zmenit verdikt) ===\n")

# 0) vychozi stav musi projit
kod, _ = spust()
print(("  OK   " if kod == 0 else "  CHYBI ") + f"vychozi dokument bez mutace: exit={kod} (ocekavan nulovy)")
if kod != 0:
    CHYBY.append("vychozi stav")

# 1) ponechat jen 4 tridy selhani -> "aspon 5" musí spadnout
#    POZOR: trid je ted 7 (S31-S37). Kdyby se odebiraly jen dve, zustane 5
#    a mutace NIC neotestuje (kontrola projde spravne). Namereno 2. 10. 2026:
#    presne to se stalo, kdyz pribyla S37. Proto se odebiraji vsechny krom
#    prvnich ctyr -- a pocet se bere z dokumentu, ne natvrdo.
def m1(t):
    tridy = re.findall(r"^### (S\d+)", t, re.M)
    if len(tridy) <= 4:
        raise AssertionError(f"dokument ma jen {len(tridy)} trid, mutace by nic netestovala")
    out = t
    for s in tridy[4:]:
        out = re.sub(r"^### " + s + r" .*$", "### (smazano mutaci)", out, flags=re.M)
    zbyle = re.findall(r"^### (S\d+)", out, re.M)
    assert len(zbyle) == 4, f"mutace neprovedla to, co mela: zbyle {zbyle}"
    return out

mutace("ponechany jen S31-S34 (4 tridy, pozadovano 5)", m1, 1)

# 2) smazat tabulku ukotveni
mutace("tabulka 'stav -> cim je ukotveno' smazana",
       lambda t: t.replace("čím je dnes ukotveno", "XXX"), 1)

# 3) prejmenovat variantu B
mutace("Varianta B prejmenovana (zbyde 1 varianta)",
       lambda t: t.replace("Varianta B", "Varianta Q"), 1)

# 4) smazat podminku selhani
mutace("podminky selhani smazany",
       lambda t: t.replace("**Podmínka selhání**", "**Neco**"), 1)

# 5) smazat oddil "co by analyzu vyvratilo"
mutace("oddil 'Co by tuhle analyzu vyvratilo' smazan",
       lambda t: t.replace("Co by tuhle analýzu vyvrátilo", "Neco jineho"), 1)

# 6) smazat vsechny odpovedi na otazky
mutace("tabulka odpovedi na otazky smazana",
       lambda t: re.sub(r"^\| \*\*\d+\*\* \|.*$", "", t, flags=re.M), 1)

# vratit original
DOK.write_text(orig, encoding="utf-8")
kod, _ = spust()
print()
print(("  OK   " if kod == 0 else "  CHYBI ") + f"po vraceni originalu: exit={kod} (ocekavan nulovy)")
if kod != 0:
    CHYBY.append("navrat originalu")

print()
if CHYBY:
    print(f"VYSLEDEK: kontrola je SLEPA v {len(CHYBY)} pripadech: {', '.join(CHYBY)}")
    sys.exit(1)
print("VYSLEDEK: kontrola umi selhat ve vsech 6 mutacich a vychozi stav prochazi")
sys.exit(0)
