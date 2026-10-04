# -*- coding: utf-8 -*-
r"""Commit prace teto session do OBOU repu — dva commity, kazdy s vlastnim popisem.

PROC SKRIPTEM A NE PRIMO: `HANDOFF.md` je jen dokument; commituji se soubory
**v repech**. A aby se do repa nedostalo neco nechteneho, skript:

  1. **vypise, co se chysta** (`git status --porcelain`) a **odmitne běžet**,
     kdyby v pracovnim stromu bylo neco, co do commitu nepatří,
  2. **přidá jen vyjmenované soubory** (`git add <cesta>`), nikdy `git add -A`,
  3. po commitu **ověří**, že vznikl právě jeden commit a že pracovní strom
     je čistý,
  4. **nevypisuje PAT** (push je samostatny krok pres `p19-push.py`).

Použití:  python _analyza\t6-commit.py [--zapis]
"""

import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
GIT = WS / "orchestra" / "tools" / "git.cmd"
ZAPIS = "--zapis" in sys.argv

# Co se commituje — VYJMENOVANE, ne `-A`. Kazdy soubor je prace teto session.
REPA = [
    (
        "orchestra",
        WS / "orchestra",
        [
            "tools/kontrola-diakritiky.py",
            "tools/oprav-ps1-kodovani.py",
            "tools/over-dokumentaci.py",
        ],
        "Projití složky místo ručních seznamů + ukázky rozbitého kódování slovem\n\n"
        "- kontrola-diakritiky.py: skilly se procházejí (~/.dsh/skills/*/SKILL.md),\n"
        "  ne ručním seznamem 12 cest. Naměřeno: 12 z 12 (dřív 5 — chyběl i `overovani`).\n"
        "- oprav-ps1-kodovani.py + over-dokumentaci.py: docstringy měly DOSLOVNOU\n"
        "  ukázku rozbitého kódování, což AGENTS.md zakazuje. Nahrazeno popisem slovem.\n\n"
        "Nalezeno projitím složky v g1-diakritika-novych.py (nálezy H14, H15).\n"
        "Brány: kontrola-diakritiky.py -> VŠE OK; over-dokumentaci.py -> exit 0;\n"
        "ag-over-cisla.py -> 0 rozchodů.",
    ),
    (
        "uo-shadows",
        WS / "games" / "uo-shadows",
        [
            ".forge/roadmap.json",
            "tests/run_tests.gd",
        ],
        "Granule tests.harness + lék na M3 (nález H12): atrapa v rozporu\n\n"
        "- .forge/roadmap.json: nová granule `tests.harness` (vlastní jen\n"
        "  tests/run_tests.gd, size_lines \"<= 1200\", model strong, prompt se\n"
        "  7 naměřenými pastmi). Granul 22 (dřív 21); lint-roadmapa beze změny\n"
        "  (14 problémů, 11x [5], 13 z 22).\n"
        "- tests/run_tests.gd: kontrola „atributy přes hodnota(attr)\" tvrdila\n"
        "  jen `damage > 0`, což splní i hodnota 4 -> mutace M3 (vypuštění větve\n"
        "  hodnota()) prošla. Nyní atrapa V ROZPORU SE SEBOU (hodnota(\"Str\") = 100\n"
        "  vs. vlastnost Str = 10) a rovnost damage = 13; navíc čítač větve jako\n"
        "  druhý důkaz.\n\n"
        "Doloženo vlastním spuštěním (_analyza/t1-m3-brana.py):\n"
        "  zdravý kód 65/0 -> M3 65/2 (SPADLA) -> návrat 65/0.\n"
        "Měřená podmínka ověřena před během i po něm.",
    ),
]

print("=" * 78)
print("COMMIT — %s" % ("ZAPIS" if ZAPIS else "DRY-RUN"))
print("=" * 78)

for jmeno, repo, soubory, zprava in REPA:
    print()
    print("── %s ──" % jmeno)
    r = subprocess.run([str(GIT), "-C", str(repo), "status", "--porcelain"],
                       capture_output=True)
    stav = r.stdout.decode("utf-8", "replace")
    # ⚠ POZOR NA `strip()` NA CELÉM VÝSTUPU (naměřeno 2. 10. 2026, stálo to
    # tři kola): prvním znakem porcelain řádku je **stav INDEXU** a u změny
    # pouze v pracovním stromu je to **MEZERA** — `.strip()` na celém výstupu
    # ji sežere, `L[3:]` pak ukrojí první znak cesty (`tools/…` → `ools/…`)
    # a skript hlásí **„neočekávaná změna“ na SPRÁVNÉM souboru**.
    # **Mezera je tady DATA, ne formátování.** Postupuje se proto po řádcích:
    # `splitlines()` (zahodí jen `\n`/`\r\n`), teprve pak `L[3:]`.
    zmenene = [L[3:] for L in stav.splitlines() if L.strip()]
    print("   změněno v stromu: %s" % ", ".join(zmenene))

    # POJISTKA: v repu nesmí být nic, co do commitu nepatří.
    nechtene = [z for z in zmenene if z not in soubory]
    assert not nechtene, \
        "%s: v pracovním stromu je neočekávaná změna %s — commituji jen vyjmenované" \
        % (jmeno, nechtene)
    chybejici = [s for s in soubory if s not in zmenene]
    assert not chybejici, "%s: tyto soubory nejsou změněné: %s" % (jmeno, chybejici)

    pred = subprocess.run([str(GIT), "-C", str(repo), "rev-parse", "HEAD"],
                          capture_output=True).stdout.decode().strip()
    print("   HEAD před: %s" % pred[:9])

    if ZAPIS:
        for s in soubory:
            a = subprocess.run([str(GIT), "-C", str(repo), "add", s], capture_output=True)
            assert a.returncode == 0, "%s: git add %s selhal" % (jmeno, s)
        c = subprocess.run([str(GIT), "-C", str(repo), "commit", "-m", zprava],
                           capture_output=True)
        vystup = (c.stdout + c.stderr).decode("utf-8", "replace")
        assert c.returncode == 0, "%s: commit selhal:\n%s" % (jmeno, vystup[-800:])
        po = subprocess.run([str(GIT), "-C", str(repo), "rev-parse", "HEAD"],
                            capture_output=True).stdout.decode().strip()
        # Ověření VÝSTUPU: nový commit, jiný než předtím, a čistý strom.
        assert po != pred, "%s: HEAD se nezměnil — commit nevznikl" % jmeno
        r2 = subprocess.run([str(GIT), "-C", str(repo), "status", "--porcelain"],
                            capture_output=True).stdout.decode("utf-8", "replace").strip()
        assert not r2, "%s: pracovní strom není čistý:\n%s" % (jmeno, r2)
        pocet = subprocess.run([str(GIT), "-C", str(repo), "rev-list", "--count",
                                pred + ".." + po],
                               capture_output=True).stdout.decode().strip()
        assert pocet == "1", "%s: vzniklo %s commitů, čekal jsem 1" % (jmeno, pocet)
        print("   HEAD po:   %s  (commitů: %s, strom čistý)" % (po[:9], pocet))
    else:
        print("   (dry-run — spusť s --zapis)")

print()
print("=" * 78)
print("HOTOVO" if ZAPIS else "DRY-RUN OK — nic se nezapsalo")
