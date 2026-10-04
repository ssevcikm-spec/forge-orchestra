# Aktualizuje OTEVRENA-TEMATA.md: dvě pracovní témata přesune do [x]
# (jejich provedení je v PLAN-ROZVOJ-ORCHESTRA.md §3.5) a přidá tři
# ROZHODNUTÍ, která blokují fázi B/D — ta zůstávají otevřená, dokud je
# uživatel nezodpoví.
# Píše se přes bajty (utf-8-sig) — PowerShell tento soubor čte v cp1252.
import io
import sys

CESTA = 'OTEVRENA-TEMATA.md'

# (starý text, který se má ZAVŘÍT, nový text s [x])
ZAVRIT = [
    (
        '- [ ] **L1 z analýzy architektury je pořád nehotové',
        None,  # jen změnit [ ] na [x] a připsat odkaz
    ),
    (
        '- [ ] **Šablona vydává release s doslovným `NAZEV-REPA`',
        None,
    ),
]

DOPLNIT_K_ZAVRENYM = """

  → **Přesunuto do `PLAN-ROZVOJ-ORCHESTRA.md` §3.5** (1. 10. 2026 večer):
  L1 = krok **A1**, `NAZEV-REPA` = krok **D1**. Téma se zavírá **v ledgeru**,
  protože je zapsané v plánu; **hotové to není** — plán říká, co s tím.
"""

NOVA = """
- [ ] **ROZHODNUTÍ (blokuje fázi B): smí se sáhnout na conductora?**
      Fáze B mění běžící orchestra (3h zpoždění nové granule, obcházení
      cooldownu přes `/report`, strop a watchdog na granuli, `listGames`
      fallback) a **deploy conductora je z gitu** — tedy změna stavu.
      Navíc **O10**: má být část **ST9** (testy conductora čtou SQL ze zdrojáku)
      součástí fáze B? Bez ní B1–B3 nemají čím dokázat, že fungují.
      Detail: `PLAN-ROZVOJ-ORCHESTRA.md` §3.5 fáze B a §6 (O3, O10).
      **Dokud tohle není zodpovězené, fáze B se nedělá.**
- [ ] **ROZHODNUTÍ (blokuje fázi D1): opravit `NAZEV-REPA` hned?**
      Je to **jeden řádek** (`release.yml` → `${{ github.repository }}`) a dnes
      to znamená, že **každá nová hra dostane v poznámkách release nefunkční
      odkaz** (doloženo simulací instalátoru: `NAZEV-REPA` zůstane v novém repu
      **3×**). Alternativa je nechat to na onboardingu (F4/D3).
      Detail: `ORCHESTRA-STAV-A-ANALYZA.md` §3.1, `PLAN-ROZVOJ-ORCHESTRA.md` §6 (O9).
- [ ] **Necommitnutá změna v orchestra: `README.md`.**
      Aktualizace rámečku „Stav obálky" (F0 uzavřeno) z 1. 10. večer. Drift
      kontrola ho **nesleduje**, takže se s herním repem nerozejde — ale je to
      **jediná změna v obou repech** a čeká na rozhodnutí, jestli se commitne.
      Ověřeno: `git -C orchestra status --short` → ` M README.md`.
"""


def main():
    with open(CESTA, 'rb') as f:
        raw = f.read()
    text = raw.decode('utf-8-sig')

    chyby = []
    for klic, _ in ZAVRIT:
        if klic not in text:
            chyby.append(klic)
    if chyby:
        print('CHYBA: nenalezen anchor (nic se nezapsalo):')
        for c in chyby:
            print('   ', c)
        return 1

    for klic, _ in ZAVRIT:
        i = text.index(klic)
        text = text[:i] + klic.replace('- [ ]', '- [x]', 1) + text[i + len(klic):]

    # Odkaz na plán přidat jen k prvnímu zavřenému tématu (NAZEV-REPA),
    # aby text zůstal čitelný.
    klic_repa = '- [x] **Šablona vydává release s doslovným `NAZEV-REPA`'
    if klic_repa in text:
        # připojit za konec toho odstavce (před další "- [")
        i = text.index(klic_repa)
        j = text.find('\n- [', i)
        if j == -1:
            j = len(text)
        text = text[:j] + DOPLNIT_K_ZAVRENYM + text[j:]

    if 'ROZHODNUTÍ (blokuje fázi B)' in text:
        print('UŽ APLIKOVÁNO — nová témata v ledgeru jsou.')
        return 0

    if not text.endswith('\n'):
        text += '\n'
    text += NOVA

    with io.open(CESTA, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(text)
    print('ZAPSÁNO do', CESTA)
    return 0


if __name__ == '__main__':
    sys.exit(main())
