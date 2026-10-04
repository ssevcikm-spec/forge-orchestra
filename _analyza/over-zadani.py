# Ověří, že vše, co ANALYZA-HLOUBKOVA-ZADANI.md slibuje, skutečně existuje.
# Zadání nesmí posílat novou session za soubory a nástroji, které nejsou.
import io
import os
import re
import sys

ZADANI = 'ANALYZA-HLOUBKOVA-ZADANI.md'

# Cesty, které zadání zmiňuje a které musí existovat.
MUSI_EXISTOVAT = [
    'AGENTS.md',
    'HANDOFF.md',
    'ORCHESTRA-STAV-A-ANALYZA.md',
    'ANALYZA-ARCHITEKTURY-ORCHESTRA.md',
    'ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md',
    'PLAN-ROZVOJ-ORCHESTRA.md',
    'PLAN-ORCHESTRA-AI-AGENTI.md',
    'PLAN-SEPARACE-WORKSPACE.md',
    'FORGE-ORCHESTRA-MOZNOSTI.md',
    'MOZNOSTI-AGENTA.md',
    'OTEVRENA-TEMATA.md',
    'ARCHITEKTURA-ANALYZA-ZADANI.md',
    'orchestra/README.md',
    'orchestra/conductor/src/index.ts',
    'orchestra/.env',
    'orchestra/.secrets',
    'orchestra/tools/zjisti-pages.mjs',
    'orchestra/tools/oprav-ps1-kodovani.py',
    'orchestra/tools/kontrola-diakritiky.py',
    'orchestra/tools/over-dokumentaci.py',
    'orchestra/tools/over-skilly.py',
    '_analyza/stav-doporuceni.mjs',
    '_analyza/stav-ci.mjs',
    '_analyza/stav-agent.mjs',
    '_analyza/stav-release.mjs',
    '_analyza/sken-vazeb.py',
    '_analyza/over-handoff-nic-nezmizelo.py',
    'dsh-plugins/temata/run.cmd',
]

# Cesty MIMO workspace (domovský adresář).
HOME = os.path.expanduser('~')
MUSI_EXISTOVAT_HOME = [
    '.dsh/skills/orchestra/SKILL.md',
    '.dsh/skills/overovani/SKILL.md',
    '.dsh/skills/overovani/sabotuj.mjs',
    '.dsh/skills/overovani/zmen.py',
    '.dsh/skills/dsh-prostredi/SKILL.md',
]

# Co zadání tvrdí o počtech — musí odpovídat realitě.
def main():
    chybi = []
    for c in MUSI_EXISTOVAT:
        if not os.path.exists(c):
            chybi.append(c)
    for c in MUSI_EXISTOVAT_HOME:
        if not os.path.exists(os.path.join(HOME, c)):
            chybi.append('~/' + c)

    with io.open(ZADANI, encoding='utf-8') as f:
        text = f.read()

    # Kontrola: zadání musí mít všech 12 oddílů výstupu (část I-III + číslované).
    for znak in ['1. **Verdikt', '2. **Co je orchestra', '3. **Inventura',
                 '4. **Katalog tříd selhání', '5. **Co je dobré',
                 '6. **Architektura v optikách', '7. **Návrh kontraktů',
                 '8. **Dvě (nebo tři) varianty', '9. **Co nedělat',
                 '10. **Co analýza NEZJISTILA', '11. **Čím je každé tvrzení',
                 '12. **Co by tuhle analýzu vyvrátilo']:
        if znak not in text:
            chybi.append('oddíl výstupu: ' + znak)

    # Kontrola: devět optik musí být v tabulce.
    optiky = re.findall(r'\*\*O(\d)\*\*', text)
    for n in range(1, 10):
        if str(n) not in optiky:
            chybi.append('optika O%d' % n)

    # Kontrola: deset otázek Q1-Q10.
    for n in range(1, 11):
        if '**Q%d**' % n not in text:
            chybi.append('otázka Q%d' % n)

    # Kontrola: pět pastí P1-P5.
    for n in range(1, 6):
        if '**P%d**' % n not in text:
            chybi.append('past P%d' % n)

    if chybi:
        print('CHYBI %d veci:' % len(chybi))
        for c in chybi:
            print('   ', c)
        return 1

    print('VŠE OK')
    print('  cest k souborům (workspace): %d' % len(MUSI_EXISTOVAT))
    print('  cest mimo workspace:         %d' % len(MUSI_EXISTOVAT_HOME))
    print('  oddílů výstupu:              12')
    print('  optik:                       9')
    print('  otázek:                      10')
    print('  pastí:                       5')
    print('  řádků zadání:                %d' % len(text.splitlines()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
