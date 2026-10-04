# -*- coding: utf-8 -*-
r"""Opraví hlavičku `NEXT-SESSION-INSTRUKCE.md` po PUSHI obou repů.

PROČ: po pushi se `HEAD` obou repů posunul (`orchestra` `7c11b2d` → `1e3925e`,
`uo-shadows` `194735d` → `c40bdd5`) a zadání tím **zastaralo** — přesně to
naměřil `zadani-kontrola.py`:
    ⚠ orchestra: zadání tvrdí 7c11b2d, skutečný HEAD je 1e3925e2c
    ⚠ uo-shadows: zadání tvrdí 194735d, skutečný HEAD je c40bdd556
**To není vada zadání — je to informace** (`PREDAVANI-SESSION.md` §3): text byl
psaný nad jiným stromem, takže se musí přeměřit. Tady se přeměřil a přepisuje.

Použití:  python _analyza\s19e-oprav-hlavicku.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
ZADANI = WS / "NEXT-SESSION-INSTRUKCE.md"
ZAPIS = "--zapis" in sys.argv

t = ZADANI.read_text(encoding="utf-8")

# ⚠ Kotvy jsou KRÁTKÉ a bez českých uvozovek: ty rozbily v téhle session
# sedm skriptů (past `dsh-prostredi` §3d). Nahrazuje se po JEDNOM výskytu
# a u každé změny se ověří, že kotva byla právě 1×.
ZMENY = [
    # 1) řádek „Zkontrolováno při"
    ("**Zkontrolováno při:** `7c11b2d`",
     "**Zkontrolováno při:** `1e3925e`"),
    # 2) popis posledního commitu (už to není B1)
    ("(„B1: naposledy_selhalo misto updated_at\")",
     "(„kontrola diakritiky: doplnit dalsich 14 souboru\")"),
    # 3) stav repů
    ("`orchestra` = `7c11b2d` · `uo-shadows` = `194735d`",
     "`orchestra` = `1e3925e` · `uo-shadows` = `c40bdd5`"),
    # 4) pushnuto: TEĎ UŽ I PRÁCE, ne jen commity
    ("**Pushnuto:** **oba ANO** (`origin/main..HEAD = 0` v obou) — ale **v pracovním\nstromu obou je necommitnutá práce**:\n`orchestra` **1 soubor** (`tools/kontrola-diakritiky.py`) ·\n`uo-shadows` **4 soubory** (`.forge/roadmap.json`, `docs/ARCHITEKTURA.md`,\n`scripts/combat.gd`, `tests/run_tests.gd` — **377 insertions, 41 deletions**).",
     "**Pushnuto:** **oba ANO a pracovní stromy jsou ČISTÉ** (`origin/main..HEAD = 0`\n"
     "a `git status --porcelain` prázdný v obou). **Práce Úkolů A i B je v `main`**\n"
     "(pushed 2. 10. 2026 13:16–13:33 UTC): `orchestra` **`593e25c` + `1e3925e`**,\n"
     "`uo-shadows` **`c40bdd5`** — a **ověřeno třemi kroky** (viz §19 v `HANDOFF.md`)."),
    # 5) kontrolní příkaz na deploy: 7c11b2d je SPRÁVNÝ commit (poslední změna
    #    conductor/**), ale 1e3925e deploy nemá a mít nemá
    ("node _analyza\\f3-over-deploy.mjs 7c11b2d       # B1 musí být nasazené",
     "node _analyza\\f3-over-deploy.mjs 7c11b2d       # B1 JE nasazené (deploy #32)\n"
     "#   POZOR: `orchestra` `1e3925e` deploy NEMÁ — a je to SPRÁVNĚ: commit mění\n"
     "#   jen `tools/`, kdežto `deploy.yml` má filtr `paths: conductor/**`.\n"
     "#   Nástroj na to správně odpoví 'na tomto commitu žádný deploy'."),
]

print("=" * 78)
print("OPRAVA HLAVIČKY PO PUSHI — zastaralé commity")
print("=" * 78)

novy = t
for i, (stary, novy_t) in enumerate(ZMENY, 1):
    pocet = novy.count(stary)
    print("  %d) %-52s %dx" % (i, repr(stary)[:52], pocet))
    if pocet == 1:
        novy = novy.replace(stary, novy_t, 1)
    elif pocet == 0:
        print("       → kotva tam není (už opraveno?) — kontroluji ručně")
    else:
        print("       → CHYBA: kotva je %dx, neopravuji" % pocet)
        sys.exit(1)

assert novy != t, "ŽÁDNÁ ZMĚNA NEPROBĚHLA"
# POJISTKY: staré sha se v hlavičce nesmí objevit, nové ano.
hlavicka = "\n".join(novy.splitlines()[:20])
for stare in ("`7c11b2d`", "`194735d`"):
    assert stare not in hlavicka, "v hlavičce zůstalo staré sha %s" % stare
for nove in ("`1e3925e`", "`c40bdd5`"):
    assert nove in hlavicka, "v hlavičce chybí nové sha %s" % nove
assert "ČISTÉ" in novy, "text o čistých stromech se nevepsal"
print()
print("  pojistky OK: stará sha v hlavičce nejsou, nová ano")

if ZAPIS:
    ZADANI.write_bytes(novy.encode("utf-8"))
    print("  ZAPSÁNO: %d -> %d B"
          % (len(t.encode("utf-8")), len(novy.encode("utf-8"))))
else:
    print("  (dry-run — spusť s --zapis)")
