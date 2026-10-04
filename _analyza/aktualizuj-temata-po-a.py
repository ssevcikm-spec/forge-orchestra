# Aktualizuje OTEVRENA-TEMATA.md po fázi A:
#   1) uzavře rozhodnutí o NAZEV-REPA (provedeno),
#   2) přidá nové téma: validate-all je červený kvůli S12 (čeká na B1).
# Píše se přes bajty (utf-8-sig) — PowerShell tento soubor čte v cp1252.
import io
import sys

CESTA = 'OTEVRENA-TEMATA.md'
KLIC_REPA = '- [ ] **ROZHODNUTÍ (blokuje fázi D1): opravit `NAZEV-REPA` hned?**'
KLIC_B = '- [ ] **ROZHODNUTÍ (blokuje fázi B): smí se sáhnout na conductora?**'
NOVE_TEMA = 'validate-all.mjs je od 1. 10. 2026 ČERVENÝ'

DOPLNIT = """
      → **VYŘEŠENO 1. 10. 2026 (rozhodl a provedl agent):** `release.yml` bere
      odkaz z `${{ github.repository }}` na **obou** místech, YAML ověřen
      parserem, **simulace instalátoru → zástupný text 0×** (dřív 3×).
"""

NOVE = """
- [ ] **`validate-all.mjs` je od 1. 10. 2026 ČERVENÝ — hlásí vadu S12.**
      Není to regrese, je to **poprvé, co validátor nelže**: do té doby hlásil
      „✗ NALEZENO 3 PROBLÉMŮ" a **stejně skončil `exit 0`**. Krok A3 zapojil do
      validátoru nový `test-cooldown.py`, který spouští **skutečný SQL**
      conductora — a ten na scénáři „nová granule" vrací **nevydá se**
      (čekáno `True`, naměřeno `False`). To je přesně **S12** (3h zpoždění).
      **Co to blokuje:** nic — je to správný stav, dokud se neudělá **B1**
      (`naposledy_selhalo` místo `updated_at`). Po B1 test zčervená v opačném
      směru a donutí scénář přepsat (nezůstane viset na staré pravdě).
      **Pozor pro každého, kdo uvidí červenou:** než začne „opravovat"
      validátor, ať si přečte `PLAN-ROZVOJ-ORCHESTRA.md` §3.5 fázi A a B1.
      Naměřeno: `node orchestra\\tools\\validate-all.mjs` → `✗ NALEZENO 1 PROBLÉMŮ`,
      `exit 1`.
"""


def main():
    with open(CESTA, 'rb') as f:
        text = f.read().decode('utf-8-sig')

    if NOVE_TEMA in text:
        print('UŽ APLIKOVÁNO.')
        return 0
    if KLIC_REPA not in text:
        print('CHYBA: nenalezen anchor pro NAZEV-REPA.')
        return 1

    # 1) zavřít rozhodnutí o NAZEV-REPA a dopsat, co se provedlo
    i = text.index(KLIC_REPA)
    j = text.find('\n- [', i)
    if j == -1:
        j = len(text)
    blok = text[i:j].replace('- [ ]', '- [x]', 1)
    text = text[:i] + blok.rstrip() + '\n' + DOPLNIT + text[j:]

    # 2) přidat nové téma o červeném validátoru
    if not text.endswith('\n'):
        text += '\n'
    text += NOVE

    with io.open(CESTA, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(text)
    print('ZAPSÁNO do', CESTA)
    return 0


if __name__ == '__main__':
    sys.exit(main())
