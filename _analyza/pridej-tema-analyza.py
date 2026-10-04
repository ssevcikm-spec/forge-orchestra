# Přidá do OTEVRENA-TEMATA.md téma: hloubková analýza orchestry je připravená
# a čeká na spuštění v nové session. Píše se přes bajty (utf-8-sig).
import io
import sys

CESTA = 'OTEVRENA-TEMATA.md'
ZNAK = 'Hloubková analýza orchestry je ZADANÁ a neprovedená'

NOVE = """
- [ ] **Hloubková analýza orchestry je ZADANÁ a neprovedená.**
      Zadání je hotové a ověřené: `ANALYZA-HLOUBKOVA-ZADANI.md` (388 řádků) —
      metodika (značky měřeno/kód/odvozeno/nevím, tři úrovně důkazu, **pět
      naměřených pastí** P1–P5), **devět optik návrhu** architektury (O1–O9),
      struktura výstupu ve **12 oddílech**, **10 dosud nezodpovězených otázek**
      (Q1–Q10), pravidla práce a **měřitelné „hotovo znamená"**.
      Kontrolní skript `_analyza\\over-zadani.py` ověřuje, že **všech 33 cest**
      v zadání existuje a že struktura je úplná → **VŠE OK**.
      **Proč to není hotové:** analýzu má dělat **nová session** (autor zadání
      orchestra dokumentoval, takže není nezávislý reviewer — `AGENTS.md`).
      **Co je potřeba:** založit nový chat se zadáním jako prvním vstupem.
      **Pozor:** tohle je ANALÝZA a NÁVRH, ne implementace — implementační plán
      je jiný dokument (`PLAN-ROZVOJ-ORCHESTRA.md` §3.5).
"""


def main():
    with open(CESTA, 'rb') as f:
        text = f.read().decode('utf-8-sig')
    if ZNAK in text:
        print('UŽ APLIKOVÁNO.')
        return 0
    if not text.endswith('\n'):
        text += '\n'
    text += NOVE
    with io.open(CESTA, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(text)
    print('ZAPSÁNO do', CESTA)
    return 0


if __name__ == '__main__':
    sys.exit(main())
