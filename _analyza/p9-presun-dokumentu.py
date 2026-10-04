# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
# Dokumenty, ktere zustaly STANICI (D6): na ty se saha absolutne.
_STANICE_DOKUMENTY = _pl.Path(r"C:\Users\Ssevc\Local-Deepseek")
"""P9 — PRESUN PROJEKTOVYCH DOKUMENTU A `_analyza\\` DO REPA (D3, D6).

ROZHODNUTI D6 (zavazne, plan §10.3b) — co zustava STANICI:
  README · POZOR-E-DSH-NEMAZAT · ANALYZA-EFEKTIVITY-DSH · DEPLOY-VYLEPSENI ·
  token-saving-* · sdxl-* · RESEARCH-public-repos · ANALYZA-VYVOJ-APLIKACI-A-HER ·
  ZADANI-CREATOR-INDIKATORY · MOZNOSTI-AGENTA · OTEVRENA-TEMATA · PREDAVANI-SESSION
  (posledni tri proto, ze na ne projektova pravidla odkazuji a stanice je pouziva
  i pro DSH/obrazky — orchestra na ne bude odkazovat absolutni cestou)
Vse ostatni projektove (HANDOFF, KRONIKA, PLAN-*, ANALYZA-*, ZADANI-*,
IMPLEMENTACE-*, NEXT-SESSION-INSTRUKCE, PROMPT-*, SOUBEH-*, ...) jde S REPEM.
`_analyza/` jde s repem cely (D3) — je to projektovy analyticky nastroj.

CO SE ZAMERNE ODDALUJE (a proc): pet souboru, do kterych tahle session jeste
BUDE psat pri kroku P12. Kdyby se presunuly hned, prisel bych o ne na konci
session. Presunou se proto jako POSLEDNI, po dokonceni P12.

Pouziti:
  python p9-presun-dokumentu.py --kontrola   # jen vypise, co by se stalo
  python p9-presun-dokumentu.py              # provede
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(_STANICE)
REPO = Path(r"E:\Workspaces\forge-orchestra")

# zustava stanici (D6) — vzory na jmeno souboru
STANICE_PRESNE = {
    "README.md", "POZOR-E-DSH-NEMAZAT.md", "ANALYZA-EFEKTIVITY-DSH.md",
    "DEPLOY-VYLEPSENI.md", "RESEARCH-public-repos.md",
    "ANALYZA-VYVOJ-APLIKACI-A-HER.md", "ZADANI-CREATOR-INDIKATORY.md",
    "MOZNOSTI-AGENTA.md", "OTEVRENA-TEMATA.md", "PREDAVANI-SESSION.md",
    "AGENTS.md",  # koren stanice: obecne/projektove pravidlo se resi zvlast
}
STANICE_PREFIXY = ("token-saving-", "sdxl-")

# oddaleny presun — tahle session do nich jeste pise (P12)
ODDELANE = {
    "PLAN-SEPARACE-WORKSPACE.md", "HANDOFF.md", "KRONIKA-PROJEKTU.md",
    "NEXT-SESSION-INSTRUKCE.md",
}

# adresare na koreni, ktere NEJSOU projektove (zustavaji stanici)
STANICE_ADRESARE = {
    "_archiv-bordel",  # pro jistotu; nize se vypise, co se naslo
}


def je_stanice(jmeno: str) -> bool:
    if jmeno in STANICE_PRESNE:
        return True
    return any(jmeno.startswith(p) for p in STANICE_PREFIXY)


def main(argv: list[str]) -> int:
    kontrola = "--kontrola" in argv
    k_presunu: list[Path] = []
    zustava: list[str] = []

    for p in sorted(WS.glob("*.md")):
        if je_stanice(p.name):
            zustava.append(p.name)
        elif p.name in ODDELANE:
            print(f"  ⏸ ODDÁLENO (P12 do nich píše): {p.name}")
            k_presunu.append(p)
        else:
            k_presunu.append(p)

    print(f"dokumentu k presunu: {len(k_presunu)}")
    print(f"zustava stanici:     {len(zustava)}")
    for z in zustava:
        print(f"    {z}")
    print()
    for p in k_presunu:
        cil = REPO / p.name
        stav = "PREPISE" if cil.exists() else "novy"
        print(f"  {p.name:52} -> {stav}")

    # _analyza
    an_src = WS / "_analyza"
    an_dst = REPO / "_analyza"
    souboru = sum(1 for f in an_src.rglob("*") if f.is_file())
    print(f"\n_analyza/: {souboru} souboru -> {an_dst}")

    if kontrola:
        print("\n(KONTROLA — nic se nepresouva)")
        return 0

    chyby = 0
    for p in k_presunu:
        cil = REPO / p.name
        try:
            if p.name in ODDELANE:
                shutil.copy2(p, cil)   # zdroj ZUSTAVA (jeste se do nej pise)
                continue
            shutil.move(str(p), str(cil))
        except Exception as e:  # noqa: BLE001
            print(f"  CHYBA u {p.name}: {e}")
            chyby += 1

    if an_src.exists():
        for f in sorted(an_src.rglob("*"), reverse=True):
            if f.is_file():
                cil = an_dst / f.relative_to(an_src)
                cil.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(f, cil)
                except Exception as e:  # noqa: BLE001
                    print(f"  CHYBA u {f}: {e}")
                    chyby += 1
        print(f"_analyza zkopirovana ({souboru} souboru) — ZDROJ ZATIM ZUSTAVA")

    print(f"\nhotovo, chyb: {chyby}")
    return 1 if chyby else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
