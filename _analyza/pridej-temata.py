# Přidá do OTEVRENA-TEMATA.md dvě nová otevřená témata zjištěná 1. 10. 2026 večer.
# Píše se přes bajty (utf-8-sig) — PowerShell čte i píše tento soubor v cp1252
# a diakritiku by rozbil.
import io
import sys

CESTA = 'OTEVRENA-TEMATA.md'

NOVE = """
- [ ] **Šablona vydává release s doslovným `NAZEV-REPA` — nikdo ho nenahrazuje.**
      Naměřeno 1. 10. 2026 večer. Oprava z F0 (odkaz se „odvozuje z názvu repa")
      zavedla do `orchestra/repo/.github/workflows/release.yml` **placeholder**:
      `:82` a `:143` obsahují `https://ssevcikm-spec.github.io/NAZEV-REPA/`
      (a `:88` o něm mluví v textu poznámek). Jsou to **literály v `echo`**, ne
      `${{ github.repository }}` — GitHub Actions je nechá být.
      `install-into-repo.ps1` kopíruje `.github` **rekurzivně a bez substituce**
      (`:42` + `:96 Copy-Item -Recurse`) a `NAZEV-REPA` **nikde nenahrazuje**
      (Python walk celé `orchestra/`: jediný další výskyt je komentář
      v `repo/.forge/node/termux-setup.sh:97-98`).
      **Doloženo simulací:** zkopírování `repo/.github/*` přesně jako instalátor
      → v novém repu zůstane `NAZEV-REPA` **3×** doslovně.
      **Důsledek:** každá nová hra z šablony dostane v poznámkách release
      **nefunkční odkaz** na neexistující repo. Symptom se posunul (dřív odkaz na
      cizí živou hru, dnes na neexistující), **vada zůstala** — a je tichá, protože
      CI je zelené.
      **Existující hra je v pořádku** pouze proto, že ji někdo **ručně** přepsal:
      `games/uo-shadows/.github/workflows/release.yml:82,139` má správné
      `…/uo-shadows/` a živý release skutečně posílá správnou URL (ověřeno GitHub API).
      **Řešení:** v `release.yml` použít `${{ github.repository }}` (nebo
      substituci v instalátoru). Patří k F4.1/F4.2 (onboarding).
      **Vedlejší nález téhož měření:** naivní hledání `forge-quest` v `release.yml`
      najde **2 výskyty** a vypadá jako nesplněné L3 — oba jsou ale **text
      o opravě** (`:88` „dřív tu bylo natvrdo forge-quest…", `:141` komentář).
      Nesmazat: je to dokumentace rozhodnutí.
- [ ] **L1 z analýzy architektury je pořád nehotové a je to nejdůležitější levná
      oprava.** Naměřeno 1. 10. 2026 večer (skript `_analyza\\stav-doporuceni.mjs`):
      `validate-all.mjs` **stále pouští starou slepou kopii**
      (`tools/kontrola-schematu.py`, jediný výskyt v souboru) a **nenastavuje
      `process.exitCode`** → při „✗ NALEZENO 3 PROBLÉMŮ" skončí **exit 0**.
      Starý soubor navíc pořád existuje (`kontrola-schematu.py` vedle opraveného
      `.forge/check-schema.py`), takže S1 (dvě verze jednoho pravidla) **trvá**.
      Ze 13 kontrolovaných doporučení analýzy jsou hotová **2** (L4 prázdná
      roadmapa, L5 `.env` v `.gitignore`); L2/L3/L7/L9/L10/L16 a ST1/ST2/ST4/ST6
      **čekají**.
"""


def main():
    with open(CESTA, 'rb') as f:
        raw = f.read()
    text = raw.decode('utf-8-sig')
    if 'NAZEV-REPA' in text:
        print('UŽ APLIKOVÁNO — téma o NAZEV-REPA v ledgeru je, nic se nemění.')
        return 0
    if not text.endswith('\n'):
        text += '\n'
    text += NOVE
    # Zápis bajty: utf-8-sig zachová BOM, newline='' zabrání zdvojení CRLF.
    with io.open(CESTA, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(text)
    print('ZAPSÁNO do', CESTA)
    return 0


if __name__ == '__main__':
    sys.exit(main())
