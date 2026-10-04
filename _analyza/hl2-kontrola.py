# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
r"""Kontrola splnění zadání druhého kola (ANALYZA-HLOUBKOVA-2-ZADANI.md §Hotovo znamená).

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\hl2-kontrola.py
Vrací nenulový exit, když některý bod chybí (aby to bylo použitelné jako brána).
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(_STANICE)
DOK = WS / "ANALYZA-HLOUBKOVA-ORCHESTRA-2.md"
MER = WS / "_analyza" / "HLOUBKOVA-MERENI-3.md"

t = DOK.read_text(encoding="utf-8")
m = MER.read_text(encoding="utf-8")

chyby = []


def bod(cislo, popis, ok, detail=""):
    print(("  OK   " if ok else "  CHYBI ") + f"{cislo}) {popis}" + (f"  [{detail}]" if detail else ""))
    if not ok:
        chyby.append(cislo)


print("=== Hotovo znamená (zadání druheho kola) ===\n")

# 1) vsech 12 oddilu z §5
sekce = [
    "Verdikt v pěti větách", "Co je orchestra", "Inventura vlastností",
    "Katalog tříd selhání", "Co je dobré", "Architektura v devíti optikách",
    "Návrh kontraktů", "Dvě varianty", "Co NEDĚLAT", "Co analýza NEZJISTILA",
    "Tabulka", "Co by tuhle analýzu vyvrátilo",
]
najdene = [s for s in sekce if s in t]
bod(1, "dokument se vsemi 12 oddily z §5", len(najdene) == 12, f"{len(najdene)}/12")

# 2) tabulka stav -> cim je ukotven
bod(2, "tabulka 'stav -> cim je ukotveno'", "čím je dnes ukotveno" in t)

# 3) aspon 5 novych trid selhani nad S30
tridy = re.findall(r"^### (S\d+)", t, re.M)
nove = [x for x in tridy if int(x[1:]) >= 31]
bod(3, "aspon 5 novych trid selhani nad S30", len(nove) >= 5, ", ".join(nove))

# 4) aspon 3 vlastni mereni
mereni = re.findall(r"^### 5\.\d+", m, re.M)
bod(4, "aspon 3 vlastni mereni (sekce 5.x v MERENI-3)", len(mereni) >= 3, f"{len(mereni)}")

# 5) aspon 1 tvrzeni vyvraceno/zpresneno
bod(5, "aspon 1 tvrzeni z 1. kola vyvraceno/zpresneno", "VYVRÁCENO" in m)

# 6) aspon 6 z 10 otazek
odpovedi = re.findall(r"^\| \*\*(\d+)\*\* \|", t, re.M)
bod(6, "odpovezeno na aspon 6 z 10 otazek", len(odpovedi) >= 6, f"{len(odpovedi)}")

# 7) aspon 2 varianty s cenou, rizikem, co nedela, podminkou selhani
v = t.count("Varianta A") > 0 and t.count("Varianta B") > 0
cena = t.count("**Cena**") >= 2
riziko = t.count("**Riziko**") >= 2
nedela = t.count("**Co NEDĚLÁ**") >= 2
podminka = t.count("**Podmínka selhání**") >= 2
bod(7, "2 varianty s cenou/rizikem/co nedela/podminkou selhani",
    all([v, cena, riziko, nedela, podminka]),
    f"cena={cena} riziko={riziko} nedela={nedela} podminka={podminka}")

# 8) napsane, co by analýzu vyvratilo a co nezjistila
bod(8, "'co by analyzu vyvratilo' i 'co nezjistila'",
    "Co by tuhle analýzu vyvrátilo" in t and "Co analýza NEZJISTILA" in t)

# 9) kazde cislo ma zdroj a cas  (heuristika: v MERENI-3 je cas u sekci)
bod(9, "u cisel je zdroj a cas (MERENI-3 ma sekci 0. Ramec)", "## 0. Rámec" in m)

# ── 10) OBSAH, NE JEN PRITOMNOST RETEZCU (doplneno 2. 10. 2026, naleZ V1) ─────
# Proc: body 1-9 se ptaly na PRITOMNOST nadpisu a klicovych slov. Namereno
# (`_analyza\hl2-kostra-test.py` + `hl2-kostra-kalibrace.py`): dokument o
# 12,5 % puvodniho textu, kde misto obsahu stoji `| **Cena** | X |`, prosel
# vsemi 9 body s `exit 0`. "9/9" tedy nebylo tvrzeni o obsahu analyzy.
#
# Co se meri: kazda z 12 pozadovanych sekci musi mit NETRIVIALNI obsah —
# aspon 4 neprazdne radky a aspon 200 znaku tela. Nejsou to magicka cisla:
# je to dolni mez, ktera odlisi "sekce existuje" od "sekce je prazdna".
# (Skutecne sekce maji 10-100 radku; kostra mela 0.)
MIN_RADKU = 4
MIN_ZNAKU = 200


def obsah_sekce(text: str, nazev: str) -> tuple[int, int]:
    """Vrati (radky, znaky) tela sekce — od NADPISU po dalsi nadpis STEJNE
    NEBO VYSSI urovne (podsekce patri do tela).

    Dve pasti, ktere tahle funkce prošla (obě naměřeny 2. 10. 2026):
      1. Hledat nazev KDEKOLIV v dokumentu nestačí — chytí se zmínka v textu
         („viz Inventura vlastností“) a sekce vyjde prazdna. Hledá se NADPIS.
      2. Prestat na JAKEMKOLIV nadpisu je spatne — sekce, ktera zacina
         podsekcemi (`### 3.1 …`, `### Varianta A …`), by vysla jako prazdna,
         i kdyz ma obsah. To je falesny poplach na spravnem dokumentu;
         odhalilo to az to, ze dokument prosel body 1-9 a spadl na 10.
    """
    radky = text.splitlines()
    vzor = re.compile(r"^(#{1,3})\s.*" + re.escape(nazev))
    start = uroven = None
    for i, r in enumerate(radky):
        m = vzor.match(r)
        if m:
            start, uroven = i, len(m.group(1))
            break
    if start is None:
        return 0, 0
    telo = []
    for r in radky[start + 1:]:
        m = re.match(r"^(#{1,3}) ", r)
        if m and len(m.group(1)) <= uroven:
            break                      # konec sekce (stejna nebo vyssi uroven)
        telo.append(r)
    nepr = [r for r in telo if r.strip()]
    return len(nepr), sum(len(r) for r in nepr)


slabe = []
for s in sekce:
    kolik_r, kolik_z = obsah_sekce(t, s)
    if kolik_r < MIN_RADKU or kolik_z < MIN_ZNAKU:
        slabe.append(f"{s} ({kolik_r} radku, {kolik_z} znaku)")

bod(10, f"kazda ze 12 sekci ma obsah (>= {MIN_RADKU} radku a >= {MIN_ZNAKU} znaku)",
    not slabe,
    "vsech 12 ma obsah" if not slabe else f"PRAZDNE/CHUDE: {', '.join(slabe)}")

# Kontrolni soucet: kdyby dokument byl jen nadpisy, vyjde to tady.
print(f"  INFO   dokument: {len(t.splitlines())} radku, {len(t)} znaku")

print()
if chyby:
    print(f"VYSLEDEK: CHYBI {len(chyby)} bodu: {', '.join(str(c) for c in chyby)}")
    sys.exit(1)
print("VYSLEDEK: vsech 10 kontrolovanych bodu splneno "
      "(9 ze zadani + obsahova kontrola V1)")
