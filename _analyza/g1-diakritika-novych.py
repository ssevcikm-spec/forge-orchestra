# -*- coding: utf-8 -*-
"""Ověří diakritiku u VŠECH textových souborů, které mají brány projektu číst.

PROČ TENHLE SKRIPT EXISTUJE (a proč je přepsaný):
  `kontrola-diakritiky.py` má **PEVNÝ SEZNAM** cest — vada **S27**, zapsaná
  v `AGENTS.md` i v `overovani` §7.10. Naměřeno **dvanáctkrát**: nový dokument
  projde „zeleně", aniž ho brána kdy otevřela. Do 2. 10. 2026 se sem proto
  **ručně dopisovaly** soubory, které session zapsala — a v tom seznamu bylo
  **190 cest**. To není brána, to je ruční účetnictví.

  **Od 2. 10. 2026 (nález H8 → návrh NA8/NA15) se seznam NEVEDE: složka se
  PROJDE.** Seznam nahradily tři kořeny a filtr na textové soubory, takže nový
  soubor je vidět **ve chvíli vzniku**, ne až když si na něj někdo vzpomene.

CO SE PROCHÁZÍ (a proč zrovna tohle):
  * **kořen workspace** — `*.md` (dokumenty, ze kterých se řídí celý projekt)
  * **`_analyza/`** — všechny textové soubory; je to pracovní stůl session
  * **`orchestra/tools/`** — nástroje, které běží v CI (`.py`, `.mjs`)

CO SE NEPROCHÁZÍ: repa her a orchestra (mají vlastní brány a vlastní CI)
a přílohy/assety (nejsou text).

⚠ DVĚ VĚCI, KTERÉ SE NESMÍ UDĚLAT „PRO ČISTOTU" (obě naměřené):
  1. **`kontrola-diakritiky.py` se NESMÍ kontrolovat stejně jako ostatní** —
     obsahuje vzorek rozbitých znaků **jako literál** (musí, jinak by neměl co
     hledat) a spadl by sám na sobě. Kontroluje se **jinak**: náhradním znakem
     a pěti českými slovy, stejně jako to dělá ona sama.
  2. **Binární soubor není vada.** `_analyza/` obsahuje i obrázky a archivy
     (naměřeno: **12** souborů, které se jako UTF-8 přečíst nedají). Přeskočí
     se, ale **VYPÍŠOU SE POČTEM** — tiché přeskočení je přesně ta vada, před
     kterou tenhle skript vznikl („prázdný seznam, který se tiše proiteruje",
     `overovani` §2.3).

Použití:  python _analyza\\g1-diakritika-novych.py
Návrat:   0 = žádná rozbitá diakritika | 1 = nález (vypíše soubor a znaky)
"""

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent

# Stejné znaky jako v bráně, ale sestavené z kódových bodů — aby je tenhle
# soubor neobsahoval doslovně (jinak by spadl sám na sobě).
ROZBITE = [chr(0x00C3), chr(0x00C4), chr(0x00C5)]
NAHRADNI = "\ufffd"
# Vzorek pro SEBEKONTROLU — dva rozbité znaky HNED PO SOBĚ. Jeden rozbitý znak
# nestačí: brány samy definují svůj vzorek jako seznam jednotlivých znaků
# (`ROZBITE = [chr(0x00C3), chr(0x00C4), chr(0x00C5)]`). Dvojice je to, co
# v souboru vznikne **jen rozbitím** (např. „začínají" → dvě rozbité sekvence
# za sebou).
#
# ⚠ 2. 10. 2026 (19:0x): tenhle komentář měl ty znaky DŘÍV DOSLOVNĚ — a protože
# `kontrola-diakritiky.py` od té doby prochází složku (opatření 6), našel je
# a nahlásil tenhle soubor jako vadný. **Byl to falešný poplach na správném
# souboru** (`overovani` §7.5): citace vzorku není vzorek. Proto se tu píše
# `chr(...)`, ne znak. Poučení obecně: **kdo cituje vzorek, musí ho citovat
# tak, aby ho sám neobsahoval** — jinak si brána najde svůj vlastní popis.
ROZBITE_DVOJICE = [a + b for a in ROZBITE for b in ROZBITE]

# Marker, kterým řádek deklaruje „obsahuji vzorek jen jako CITACI, ne jako
# definici" — výjimka patří ŘÁDKU, ne jménu souboru (`overovani` §9.5).
MARKER_V_CITACI = "VZOREK-V-CITACI"
# Co se markerem přihlásilo — vypisuje se v souhrnu, aby byla vidět velikost
# výjimky (sebede klarace, ne nezávislý důkaz — viz docstring `radky_se_vzorkem`).
RADKY_S_MARKEREM = []
# Soubory, které obsahují vzorek rozbitých znaků JAKO LITERÁL — musí ho mít,
# jinak by neměly co hledat. Kontrolují se proto jinak (viz `zkontroluj`).
# ⚠ SEZNAM JE ZÁMĚRNĚ KRÁTKÝ A MĚŘENÝ: kdyby se „výjimka" dala přidělit
# jakémukoli souboru, který obsahuje rozbité znaky, byla by to díra v bráně.
# Každý z těch souborů je **sám brána** (hledá ty znaky v jiných souborech).
SAMOKONTROLA = {
    "kontrola-diakritiky.py",
    "over-dokumentaci.py",
    "oprav-ps1-kodovani.py",
}
# Sebekontrola `kontrola-diakritiky.py` — stejná kritéria jako v té bráně.
VLASTNI_JMENO = "kontrola-diakritiky.py"
VLASTNI_TEXTY = ["diakritiky", "kódování", "souborů", "příliš", "žluťoučký"]
# Tenhle soubor sám sebe nekontroluje (má `ROZBITE` z kódových bodů, ne
# doslovně) — a přesto se v procházené složce najde. Vylučuje se jménem.
VLASTNI_NAZEV = pathlib.Path(__file__).name
# ⚠ ZÁLOHY (`*-pred-*.md`) se NEKONTROLUJÍ — a je to správně, ne díra:
# jsou to **snímky souboru PŘED opravou**, uložené jako doklad (vzor
# `overovani` §2.1: „zálohuj kopií, ne prevencí gitu"). Kdyby se kontrolovaly,
# hlásily by vadu, kterou **právě dokládají** — naměřeno 2. 10. 2026:
# `_analyza\kronika-pred-k21b.md` obsahuje starý text s rozbitým znakem,
# protože vznikl jako záloha PŘED jeho opravou. **Mazat se nesmí** (je to
# důkaz) a **hlásit se nemá** (není to živý dokument).
ZALOHY_VZOR = "pred-"
ZALOHY_PRIPONA = ".md"

# (složka, vzory) — prochází se CELÁ složka, seznam souborů se nevede.
KORENY = [
    (WS, ["*.md"]),
    (WS / "_analyza", ["*.md", "*.py", "*.mjs", "*.json", "*.gd", "*.txt", "*.ps1"]),
    (WS / "orchestra" / "tools", ["*.py", "*.mjs"]),
]


def textove_soubory():
    """Vrátí (soubory, binarni, zalohy) — každá vynechaná skupina se VYPÍŠE."""
    soubory, binarni, zalohy = [], [], []
    for slozka, vzory in KORENY:
        if not slozka.is_dir():
            print("  CHYBA složka k projití neexistuje: %s" % slozka)
            continue
        for vzor in vzory:
            for f in sorted(slozka.glob(vzor)):
                if not f.is_file() or f in soubory or f in binarni or f in zalohy:
                    continue
                if f.name == VLASTNI_NAZEV:
                    # Sám sebe nekontroluje: `ROZBITE` má z kódových bodů
                    # (`chr(0x00C3)`), takže rozbité znaky v něm nejsou — ale
                    # být by tam mohly a pak by hlásil vadu na sobě.
                    continue
                if ZALOHY_VZOR in f.name and f.suffix == ZALOHY_PRIPONA:
                    zalohy.append(f)
                    continue
                try:
                    f.read_bytes().decode("utf-8")
                except (UnicodeDecodeError, OSError):
                    binarni.append(f)
                    continue
                soubory.append(f)
    return soubory, binarni, zalohy


def radky_se_vzorkem(s: str) -> list:
    """Které řádky smějí rozbité znaky obsahovat LEGITIMNĚ (jsou to definice vzorku).

    PROČ VZOREC A NE PARSER (naměřeno 2. 10. 2026): zkusil jsem napřed odstranit
    komentáře a řetězce (`bez_komentaru`) — a půlparser **selhal na jednoduchých
    uvozovkách**: vzorek psaný jako seznam jednoznakových literálů v uvozovkách
    má `"` jako literál, takže se uvozovky spárovaly špatně a rozbitý znak
    zůstal „v kódu". Falešný poplach na SPRÁVNÉM souboru je stejná vada jako
    slepá kontrola.

    Legitimní je proto jen to, co je vidět na řádku: definice seznamu vzorku
    nebo jeho použití při hledání. Všechno ostatní (docstring, hláška, text)
    legitimní NENÍ — a přesně tam `AGENTS.md` zakazuje ukázku rozbitého
    kódování doslovnými znaky.

    ⚠ DOPLNĚNO 2. 10. 2026 (19:0x) — **výjimka deklarovaná SAMOTNÝM SOUBOREM**:
    `kontrola-diakritiky.py` od té doby prochází složku (opatření 6), takže
    vidí i tenhle soubor — a nahlásil jako vadu **dva řádky DOCSTRINGU výš**
    (ty, které popisují, proč půlparser selhal). To jsou **naměřené důkazy
    rozhodnutí**, ne definice vzorku: smazat je znamená ztratit znalost
    (a `AGENTS.md` říká, že historická znalost se needituje).

    Řádek se proto smí přihlásit markerem **`VZOREK-V-CITACI`** v komentáři.
    **Proč marker a ne seznam jmen souborů** (`overovani` §9.5): výjimka
    klíčovaná JMÉNEM je ruční seznam — kdo soubor přejmenuje nebo přidá nový,
    dostane falešný poplach nebo díru. Marker je **u konkrétního řádku** a je
    vidět při čtení.

    ⚠ **PŘIZNANÁ MEZ:** marker si píše sám kontrolovaný soubor, takže je to
    **sebede klarace**, ne nezávislý důkaz. Kdo ho zneužije plošně, vypne si
    kontrolu — proto se **počet řádků s markerem VYPISUJE** v souhrnu.
    """
    povolene = []
    for L in s.splitlines():
        if re.search(r"(ROZBITE|rozbito)\s*=", L) or re.search(r"for\s+\w+\s+in\s+(ROZBITE|rozbito)", L):
            povolene.append(L)
        elif MARKER_V_CITACI in L.upper():
            # Výjimka deklarovaná SAMOTNÝM ŘÁDKEM (viz docstring výš) — nikoli
            # jménem souboru. Počet se vypisuje, aby bylo vidět, jak je velká.
            povolene.append(L)
            RADKY_S_MARKEREM.append(L.strip()[:70])
    return povolene


def zkontroluj(f: pathlib.Path, s: str) -> tuple:
    """Vrátí (ok, popis_rozbiti).

    TŘI REŽIMY, protože jinak by brány spadly samy na sobě:
      * **běžný soubor** — vadou je JEDINÝ rozbitý znak kdekoli v textu;
      * **soubor se vzorkem** (`SAMOKONTROLA`) — rozbité znaky jsou legitimní
        **jen na řádcích, které vzorek definují nebo používají**; kde koli
        jinde (docstring, hláška, komentář) je to vada. Naměřeno 2. 10. 2026:
        bez tohohle rozlišení hlásila kontrola vadu na **třech správných
        branách** — a naopak u `over-dokumentaci.py` odhalila **skutečnou**
        ukázku rozbitého kódování v docstringu (což `AGENTS.md` zakazuje);
      * **`kontrola-diakritiky.py`** — úplně jinak: náhradní znak + pět
        českých slov (má vzorek i v `VLASTNI_TEXTY`, takže by si své slovo
        vždycky našel; důvod je popsaný v té bráně samé).
    """
    if f.name == VLASTNI_JMENO:
        chybejici = [t for t in VLASTNI_TEXTY if t not in s]
        nahradnich = s.count(NAHRADNI)
        if chybejici or nahradnich:
            duvod = []
            if chybejici:
                duvod.append("chybí text %s" % ", ".join(chybejici))
            if nahradnich:
                duvod.append("%d× náhradní znak" % nahradnich)
            return False, "; ".join(duvod)
        return True, "ne (sebekontrola: %d českých slov, 0 náhradních znaků)" % len(VLASTNI_TEXTY)
    if f.name in SAMOKONTROLA:
        povolene = radky_se_vzorkem(s)
        mimo = [L.strip() for L in s.splitlines()
                if L not in povolene and any(z in L for z in ROZBITE)]
        if mimo:
            return False, ("ANO (%d řádků s rozbitými znaky MIMO definici vzorku; "
                           "první: %s)" % (len(mimo), mimo[0][:60]))
        return True, ("ne (soubor se vzorkem: %d řádků definuje vzorek, "
                      "mimo ně 0)" % len(povolene))
    nalezene = [z for z in ROZBITE if z in s]
    if nalezene:
        return False, "ANO (%d znaků)" % len(nalezene)
    return True, "ne"


def main() -> int:
    print("=" * 78)
    print("DIAKRITIKA — PROJITÍM SLOŽKY (ne podle ručního seznamu)")
    print("=" * 78)
    for slozka, vzory in KORENY:
        print("  procházím: %-24s vzory: %s" % (slozka.name or str(slozka), ", ".join(vzory)))
    print()

    soubory, binarni, zalohy = textove_soubory()
    chyb = 0
    print("  %-46s %9s  %s" % ("soubor", "znaků", "rozbito"))
    print("  " + "-" * 74)
    for f in soubory:
        try:
            s = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as e:                     # noqa: BLE001
            print("  CHYBA %-40s NELZE PŘEČÍST: %s" % (f.name, type(e).__name__))
            chyb += 1
            continue
        ok, popis = zkontroluj(f, s)
        if not ok:
            chyb += 1
        # Popisek nese i rodiče: bez toho se v `_analyza` jmenuje desítky
        # souborů stejně a není poznat, který je vadný.
        popis_cesty = str(f.relative_to(WS)) if WS in f.parents else f.name
        print("  %s %-40s %9d  %s"
              % ("OK  " if ok else "CHYBA", popis_cesty, len(s), popis))

    print()
    # Nula a „nezměřeno" nejsou úspěch: kolik se jich přeskočilo, musí být vidět.
    # Každá vynechaná skupina je VYPSANÁ i s důvodem — tiché přeskočení je
    # přesně ta vada, před kterou tenhle skript vznikl.
    print("  ZMĚŘENO: textových souborů=%d, přeskočeno jako binární=%d, "
          "přeskočeno jako ZÁLOHA=%d, vad=%d"
          % (len(soubory), len(binarni), len(zalohy), chyb))
    # Výjimka deklarovaná SOUBOREM se musí VYPISOVAT — jinak je to tichá díra
    # (`overovani` §9.5: výjimka klíčovaná jménem je ruční seznam).
    print("  VÝJIMKY DEKLAROVANÉ SOUBOREM (`%s`): %d řádků"
          % (MARKER_V_CITACI, len(RADKY_S_MARKEREM)))
    for r in RADKY_S_MARKEREM:
        print("      %s" % r)
    if zalohy:
        print("  (zálohy `*-pred-*.md` se nekontrolují — jsou to snímky PŘED opravou;")
        print("   hlásily by vadu, kterou právě dokládají. Nemažou se:)")
        for f in zalohy:
            print("      %s" % f.name)
    if binarni:
        print("  (binární se nehlásí jako vada — nejsou text; výpis pro kontrolu:)")
        for f in binarni[:15]:
            print("      %s" % f.name)
        if len(binarni) > 15:
            print("      … a dalších %d" % (len(binarni) - 15))
    print()
    if chyb:
        print("NALEZENY CHYBY (%d)" % chyb)
        return 1
    print("VŠE OK — %d textových souborů, žádná rozbitá diakritika" % len(soubory))
    return 0


if __name__ == "__main__":
    sys.exit(main())
