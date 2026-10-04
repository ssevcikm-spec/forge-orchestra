# Přesune blok "## 3.5 Implementační plán" z prostředí §3 (kde rozděluje
# fáze F0-F5) na konec §3, tedy ZA F5 a PŘED "## 4.".
# Důvod: F0-F5 jsou věcné členění §3; 3.5 je prováděcí pořadí a patří až za ně.
# Píše se přes bajty; nové řádky sjednoceny na \n (soubor je LF).
import io
import sys

CESTA = 'PLAN-ROZVOJ-ORCHESTRA.md'
START = '## 3.5 Implementační plán'
KONEC = '## 4. Co tenhle plán vědomě NEŘEŠÍ'


def main():
    with open(CESTA, 'rb') as f:
        raw = f.read()
    text = raw.decode('utf-8')

    if text.index(START) > text.index(KONEC):
        print('UŽ APLIKOVÁNO — 3.5 je za §3.')
        return 0

    i = text.index(START)
    j = text.index(KONEC)
    blok = text[i:j]
    zbytek = text[:i] + text[j:]

    # Oddělovač před §4 zůstává; blok vložíme před něj.
    # Najdeme poslední '---' před KONEC v novém textu.
    k = zbytek.index(KONEC)
    # pred KONEC je "\n---\n\n"; vložíme blok pred ten oddelovac
    oddelovac = zbytek.rfind('---', 0, k)
    if oddelovac == -1:
        print('CHYBA: nenašel jsem oddělovač před §4.')
        return 1

    novy = (
        zbytek[:oddelovac]
        + blok.rstrip('\n')
        + '\n\n---\n\n'
        + zbytek[oddelovac + 3:].lstrip('\n')
    )

    # Přepiš nadpis 3.5 na jasnější a doplň odkaz v úvodu §3.
    novy = novy.replace(
        '## 3.5 Implementační plán — pořadí, kterým se to má dělat',
        '## 3.5 Implementační plán — pořadí, kterým se to má dělat\n\n'
        '*(Následuje po fázích F0–F5; ty říkají, **co k čemu patří**, tenhle oddíl\n'
        'říká, **čím se začne**.)*',
        1,
    )

    with io.open(CESTA, 'w', encoding='utf-8', newline='') as f:
        f.write(novy)
    print('PŘESUNUTO: §3.5 je nyní za F5.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
