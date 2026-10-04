# Opraví pořadí v PLAN-ROZVOJ-ORCHESTRA.md:
#   3.5 (implementační plán) se má přesunout ZA F5 a PŘED "## 4.".
# Pracuje pořadově podle výskytů nadpisů, ne podle bloků — předchozí pokus
# přesunul blok sám před sebe, protože 3.5 leželo PŘED F0 (ne za ním).
# Píše UTF-8 bez BOM, LF.
import io
import sys

CESTA = 'PLAN-ROZVOJ-ORCHESTRA.md'
H35 = '## 3.5 Implementační plán'
HF0 = '### F0 — Základ'
H4 = '## 4. Co tenhle plán vědomě NEŘEŠÍ'


def main():
    with open(CESTA, 'rb') as f:
        raw = f.read()
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError as e:
        print('CHYBA: soubor není UTF-8:', e)
        return 1

    i35 = text.find(H35)
    iF0 = text.find(HF0)
    i4 = text.find(H4)
    if min(i35, iF0, i4) < 0:
        print('CHYBA: nenalezen některý nadpis.')
        return 1

    if i35 > iF0:
        print('UŽ APLIKOVÁNO — 3.5 je za F0.')
        return 0

    # Blok 3.5 = od jeho nadpisu po nadpis F0 (včetně oddělovače před F0).
    blok = text[i35:iF0]
    zbytek = text[:i35] + text[iF0:]

    # Najít oddělovač "---" těsně před "## 4." v novém textu a vložit blok před něj.
    i4b = zbytek.find(H4)
    oddel = zbytek.rfind('---', 0, i4b)
    if oddel == -1:
        print('CHYBA: nenašel jsem oddělovač před §4.')
        return 1

    novy = zbytek[:oddel] + blok.rstrip() + '\n\n' + zbytek[oddel:]

    with io.open(CESTA, 'w', encoding='utf-8', newline='') as f:
        f.write(novy)
    print('HOTOVO: 3.5 přesunuto za F5.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
