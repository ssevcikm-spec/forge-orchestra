r"""Zápis session 2. 10. 2026 (dokončení auditu) do `KRONIKA-PROJEKTU.md`.

KRONIKA se **NIKDY nepřepisuje, jen doplňuje** (`AGENTS.md`, `PREDAVANI-SESSION.md`
§2 bod 4) — a je to jediné místo, kde přežije celý příběh projektu. Skript proto:
  1. vkládá na **přesně určená místa** (kotvy se assertují, aby se nic nezdvojilo),
  2. **nic neodebere** — po zápisu ověří, že každý neprázdný řádek původního
     textu je i v novém,
  3. zapíše **bajty** (`write_bytes`) → zůstanou LF,
  4. na konci spustí `kronika-kontrola.py` a **`exit 1`, když nesedí**.

Zapisuje se PĚT věcí (všechno, co `PREDAVANI-SESSION.md` §2 bod 4 žádá):
  * §1 — **jeden nový řádek** přehledové tabulky (session 19),
  * §2 — **nové nálezy H24–H28**,
  * §3 — **řádek bloku `8j`** do podrobné tabulky + přepočtené součty,
  * §5 — **nová poučení L21–L24**,
  * §6 — **nové návrhy NA20–NA23 ve stavu `NEOVĚŘENO`**.

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\s23-kronika.py
"""
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
K = WS / "KRONIKA-PROJEKTU.md"
KONTROLA = WS / "_analyza" / "kronika-kontrola.py"

# ── 1) Řádek do přehledové tabulky ─────────────────────────────────────────
RADEK_SESSION = (
    "| **19** | 2. 10. 2026 18:1x | **akční** | **Dokončení auditu dokumentace** "
    "(`ZADANI-DOKONCENI-AUDITU.md`): snapshot, tři vady a jejich měřidla, "
    "sběrný běh všech bran | `HANDOFF.md` **NEDOTČENÝ** (SHA-256 shodný se "
    "snapshotem, jen `mtime`); `ag-mutace.py` **2/2 chyceno** a **nově v `g3`** "
    "(29 → **30 bran**); `audit2b` **0 rozchodů u `granulí`** (bylo 11 "
    "falešných); `audit2a-schema.py` → **`exit 0`** — **ale kritérium zadání "
    "bylo nesplnitelné, viz H24** | **87–93** |\n"
)

# ── 2) Nálezy H24–H28 ──────────────────────────────────────────────────────
NALLEZY = """### 2.4 Nálezy H24–H28 (z dokončení auditu dokumentace, 2. 10. 2026 18:1x–19:0x)

**Všechny jsou to vady MĚŘIDEL, DOKLADU nebo OPATŘENÍ — a všechny jsou
doložené spuštěním** (`HANDOFF.md` **§23**). Dva z nich (H24, H28) jsou
**vady ZADÁNÍ**, které se projevily až při provádění — a to je nový vzorec:
**zadání je taky měřidlo** (říká, co je „hotovo") a má tytéž pasti.

| # | Nález | Stav | Kdo to řeší |
|---|---|---|---|
| **H24** | **Zadání mělo u Úkolu 1 NESPLNITELNÉ kritérium a mířilo vedle.** Tvrdí: „číslo 39 je tam v přítomném čase a bez značky času → `audit2a-schema.py` je `exit 1`". **Naměřeno po provedení předepsané opravy: `exit 1` zůstal a 6 „rozchodů" — a ANI JEDEN nebyl tvrzení o dnešku** (1× citace `„32 sloupců"` v `AGENTS.md`, 1× datovaný záznam v kronize, 4× citace v tabulkách omylů `HANDOFF.md`). **A ta horší polovina:** vzor `(\\d+)\\s+sloupc` potřebuje jednotku **hned za číslem**, takže na skutečné tvrzení („správně je **39**") **vůbec nedosáhl** — brána u `AGENTS.md:62` hlásila „tvrdí 32", tedy četla **citaci**, a **vadu R1 nikdy neměřila**. `exit 1` byl **správný výsledek ze špatného důvodu** | **opraveno** — měřidlo přepsáno (mutačně **4/4**, vč. vrácení `39` bez značky času) a `audit2a-schema.py` → `exit 0`; **zapsáno jako past** (`AGENTS.md`, `overovani` §10.1–10.2) | tato session |
| **H25** | **`audit2b` má sám vadu, kterou vytýká `audit2-rozpory.py`.** Veličina `kontrol` (`(\\d+)\\s+kontrol`) srovnává čísla z **RŮZNÝCH BRAN**, které hlásí různé počty kontrol **SPRÁVNĚ** (23, 59, 60, 61, 65…) → **27 „rozchodů", z toho většina falešných**. Je to přesně ta past, kterou audit popsal u `audit2-rozpory.py` („různé brány hlásí různé počty kontrol správně") — a `audit2b`, který měl být tou lepší variantou, ji má taky | **otevřeno** — zadání žádalo opravit jen `granulí`; zbytek je **návrh NA22** | příští session |
| **H26** | **Dvě opatření auditu nebyla zadáním PŘIDĚLENA ŽÁDNÉ session.** `ZADANI-DOKONCENI-AUDITU.md` §6 posílá do session B opatření **6, 7, 8**, do C **4, 5**, do D **10, 12** — **opatření 2** (popisek v `ag-over-cisla.py`) a **3** (rozšířit `ag-over-cisla.py` na řádek 62) v tom výčtu **nejsou**. Opatření tedy **nejsou zamítnutá, jen bez vlastníka** — a to je horší, protože je nikdo neudělá a nikdo si toho nevšimne. **Opatření 2 jsem provedl** (patří k R1); **opatření 3 zůstává otevřené** | **opatření 2 hotové**, opatření 3 **otevřeno** | tato session (2) / příští (3) |
| **H27** | **Snapshot (opatření 9) ZNE Platnil baseline inventáře — sám sobě.** `audit-snapshot.py` kopíruje dokumentaci do `_analyza\\snapshot-<čas>\\`; `audit1-inventar.py` ty **kopie začal počítat jako dokumenty**: naměřeno **159 dokumentů místo 98**, **66 záloh místo 8**, „bez hlavičky" **116 z 159** místo **62 z 98**. Kdo by ta čísla četl jako stav dokumentace, **čte vlastní snapshot**. **Je to omyl 92** (vlastní) a zároveň **obecný nález**: opatření, které něco kopíruje, musí říct všem měřidlům, že je to kopie | **opraveno** — `audit1-inventar.py` vylučuje předponu `snapshot-`; inventář zpět na **101 dokumentů / 8 záloh** (101 = 98 + 2 nové dokumenty + 1 oddílový soubor) | tato session |
| **H28** | **Kritérium „porovnej `mtime` s 17:38" dalo NEPRAVDIVOU odpověď.** Zadání podle něj mělo rozhodnout, zda v `NEXT-SESSION-INSTRUKCE.md` pracuje jiná session. **Naměřeno:** `mtime` se změnil (17:38:17 → 18:32:22), **ale SHA-256 obsahu je ve DVOU snapshotech i na disku shodný** (`9c05c6b434d5d026…`, 17 841 B). `mtime` hnul **mutační test** `_analyza\\zadani-mutace.py:50` (zapisuje a řádky 100/115/129 vrací), který spouští `audit6-brany-mutace.py`. **Kritérium by tedy tvrdilo „pracuje v tom souboru jiná session", což není pravda** — a žádná jiná session aktivní není | **zapsáno** — rozhodnutí se opřelo o **hash obsahu**; `NEXT-SESSION-INSTRUKCE.md` zůstal **nedotčený**, zadání je v novém souboru (`HANDOFF.md` §23.7). **Návrh NA20** | příští session |

---

"""

# ── 3) §3: řádek bloku 8j + přepočtené součty ──────────────────────────────
RADEK_8J = ("| **8j** | akční (dokončení auditu) 2. 10. 18:1x | **7** | **7** | **0** |\n")
RADEK_CELKEM_STARY = ("| **celkem** | **9 bloků, 18 sessions** | **81** | **65 = 80 %** | **37** |")
RADEK_CELKEM_NOVY = ("| **celkem** | **10 bloků, 19 sessions** | **88** | **72 = 82 %** | **37** |")

# ── 4) §5: poučení L21–L24 ─────────────────────────────────────────────────
POUCENI = (
    "| **L21** | **Brána může číst CITACI místo TVRZENÍ — a mít `exit 1` ze "
    "špatného důvodu.** Vzor rozhoduje o tom, CO se vůbec přečte; „vzor něco "
    "našel\" a „vzor našel to, co hledám\" jsou dvě různé věty | naměřeno "
    "2. 10. 2026 (H24): `audit2a-schema.py` hledal `(\\d+)\\s+sloupc`, takže "
    "zabral na **„32 sloupců\"** (citace dřívějšího chybného tvrzení) a skutečné "
    "tvrzení „správně je **39**\" **neměřil vůbec** — jednotka u něj nestojí. "
    "Brána hlásila 6 rozchodů a **ani jeden nebyl tvrzení o dnešku** | "
    "`AGENTS.md` („Jak ověřovat\"), `overovani` **§10.1–10.2** |\n"
    "| **L22** | **Měřidlo musí VYPISOVAT VELIKOST OKNA, které použilo — "
    "velkorysé okno není opatrnost, je to slepota** | naměřeno 2. 10. 2026 "
    "(omyl **89**): první verze brala „blok\" jako souvislý běh neprázdných "
    "řádků; v `AGENTS.md` je oddíl „## Jak dokumentovat\" **jeden blok o 5 441 "
    "znacích se sedmi daty** → jediné datum kdekoli v něm **umlčelo celá "
    "oddíl**. Zúžení na jednu odrážku (**824 znaků**) **ZVÝŠILO pokrytí** "
    "(26 → 27 rozchodů). Odhalil to až mutační test — a jen proto, že se "
    "velikost okna vypisovala | `overovani` **§10.4–10.5** |\n"
    "| **L23** | **Nástroj, který KOPÍRUJE dokumenty, musí měřidlům říct, "
    "že je to kopie** — jinak si příští session přečte vlastní snapshot jako "
    "stav dokumentace | naměřeno 2. 10. 2026 (H27, omyl **92**): "
    "`audit-snapshot.py` (opatření 9) zkopíroval dokumentaci do `_analyza\\"
    "snapshot-<čas>\\` a `audit1-inventar.py` ji začal počítat jako dokumenty "
    "→ **159 místo 98**, **66 záloh místo 8**. Je to **nález o OPATŘENÍ**, "
    "ne o nástroji: opatření samo sobě zneplatnilo baseline | `AGENTS.md` "
    "(„Jak ověřovat\"), `_analyza\\audit1-inventar.py` |\n"
    "| **L24** | **`mtime` není obsah — a mutační test `mtime` MĚNÍ.** "
    "Kritérium „změnil se soubor?\" se musí ptát na **hash**, ne na časovou "
    "značku | naměřeno 2. 10. 2026 (H28): zadání mělo podle `mtime` proti "
    "17:38 rozhodnout, zda v `NEXT-SESSION-INSTRUKCE.md` pracuje jiná session. "
    "`mtime` se změnil (→ 18:32:22), **ale SHA-256 obsahu je shodný ve dvou "
    "snapshotech i na disku** (`9c05c6b4…`, 17 841 B) — hnul jím "
    "`_analyza\\zadani-mutace.py`, který soubor zapisuje a vrací. "
    "**Kritérium tvrdilo nepravdu.** Totéž platí pro `HANDOFF.md`: je "
    "označený jako **„jen mtime\"**, obsah beze změny | `HANDOFF.md` §23.1, "
    "§23.7 |\n"
)

# ── 5) §6: návrhy NA20–NA23 ────────────────────────────────────────────────
NAVRHY = (
    "| **NA20** | **Kritérium „změnil se soubor?\" přepnout z `mtime` na "
    "SHA-256 obsahu** — v zadáních i v nástrojích. Kde je po ruce snapshot "
    "(Úkol 0), porovnávat proti němu; `mtime` používat jen jako **upozornění "
    "k dohledání** | **H28**: `mtime` `NEXT-SESSION-INSTRUKCE.md` se změnil "
    "(17:38:17 → 18:32:22), ale hash obsahu je **shodný ve dvou snapshotech "
    "i na disku**; hnul jím `_analyza\\zadani-mutace.py`. Kritérium zadání "
    "(„porovnej `mtime` s 17:38\") by dalo **nepravdivou odpověď** | "
    "**`NEOVĚŘENO`** — k rozhodnutí příští session | — |\n"
    "| **NA21** | **Každý nástroj, který KOPÍRUJE dokumenty do workspace, "
    "musí být zapsán ve vyloučených složkách všech inventářů** — nebo to mít "
    "v docstringu jako deklaraci. Konkrétně: `snapshot-*` v `audit1-inventar.py` "
    "(**hotovo**) a totéž pro `kronika-kontrola.py` a `v7-kryti-dokumentu.py` | "
    "**H27**: snapshot zvedl inventář z **98 na 159 dokumentů** a ze **8 na 66 "
    "záloh**; opatření 9 tak zneplatnilo baseline auditu | **částečně "
    "`APLIKOVÁNO`** (v `audit1-inventar.py`); zbytek **`NEOVĚŘENO`** | — |\n"
    "| **NA22** | **`audit2b`: u každé veličiny doložit, KTERÝ ZDROJ to číslo "
    "měří.** Veličina `kontrol` dnes srovnává čísla z různých bran (23, 59, 60, "
    "61, 65…) a hlásí **27 rozchodů, z toho většinu falešných**. Buď ji "
    "rozpadnout na `kontrol:<brána>`, nebo ji z nástroje **vyřadit** a přiznat "
    "to v docstringu (jako se to udělalo u `audit2-rozpory.py`) | **H25**: "
    "`audit2b` má sám vadu, kterou audit vytkl `audit2-rozpory.py` "
    "(„různé brány hlásí různé počty kontrol SPRÁVNĚ\") | **`NEOVĚŘENO`** — "
    "k rozhodnutí příští session | — |\n"
    "| **NA23** | **`g3-brany.py`: (a) u brány bez čítače vypsat `—` nebo "
    "`NEZMĚŘENO`, nikdy prázdný řetězec** — dnes má `validate-all (CELEK)` "
    "`otevřela:` **prázdné**, protože vzor `NALEZENO (\\d+)|VŠE V PO` má druhou "
    "alternativu **bez skupiny**. **(b) Zvážit baseline očekávaných nenulových "
    "exitů** — dnes `g3` **nemá `sys.exit`** a je to **přehled**, ne brána; "
    "kdyby se měl stát blokujícím, musí znát **které** nenulové exity jsou "
    "správné (dnes `mutace A: pres-level`), ne jen jejich počet | naměřeno "
    "2. 10. 2026: `g3-brany.py` skončil **`exit 0`** i s jedním nenulovým "
    "řádkem; `validate-all` vypsal prázdno; past zapsána do `overovani` §10.8 | "
    "**`NEOVĚŘENO`** — k rozhodnutí příští session | — |\n"
)


def main() -> int:
    text = K.read_text(encoding="utf-8")
    pred = K.read_bytes()

    # ── Pojistky proti dvojímu zápisu ──────────────────────────────────────
    for popis, znacka in (("§2.4", "### 2.4 Nálezy H24–H28"),
                          ("řádek 19", "| **19** | 2. 10. 2026 18:1x |"),
                          ("blok 8j", "| **8j** | akční (dokončení auditu)"),
                          ("L21", "| **L21** |"),
                          ("NA20", "| **NA20** |")):
        assert text.count(znacka) == 0, "%s už v kronize je — zápis by zdvojil!" % popis

    # ── 1) řádek do přehledové tabulky (před „Jak číst tabulku") ───────────
    kotva1 = "\n**Jak číst tabulku:**"
    assert text.count(kotva1) == 1, "kotva „Jak číst tabulku\" není 1×"
    i = text.index(kotva1)
    text = text[:i] + "\n" + RADEK_SESSION + text[i:]

    # ── 2) nálezy H24–H28 (před `---` za §2.3) ─────────────────────────────
    kotva2 = "\n---\n\n## 3. Počty omylů"
    assert text.count(kotva2) == 1, "kotva pro §2.4 není 1×"
    text = text.replace(kotva2, "\n" + NALLEZY + "## 3. Počty omylů", 1)

    # ── 3) §3: řádek 8j + součty ───────────────────────────────────────────
    assert text.count(RADEK_CELKEM_STARY) == 1, "řádek „celkem\" není 1×"
    text = text.replace(RADEK_CELKEM_STARY,
                        RADEK_8J + RADEK_CELKEM_NOVY, 1)
    assert '| **omylů v 8 blocích, které brána ZNÁ** | **75** |' in text
    text = text.replace(
        "| **omylů celkem v `HANDOFF.md` (unikátní id)** | **86** |",
        "| **omylů celkem v `HANDOFF.md` (unikátní id)** | **93** |", 1)
    text = text.replace(
        "| **z toho vad MĚŘIDLA** | **65 = 80 %** |",
        "| **z toho vad MĚŘIDLA** | **72 = 82 %** |", 1)
    text = text.replace(
        "| **bloků omylů** | **9** (1–13, 8b–**8i**) **+ §13.2** |",
        "| **bloků omylů** | **10** (1–13, 8b–**8j**) **+ §13.2** |", 1)

    # ── 4) §5: poučení (na konec tabulky poučení) ──────────────────────────
    kotva4 = "\n---\n\n## 6. Návrhy na zlepšení"
    assert text.count(kotva4) == 1, "kotva pro §5 není 1×"
    text = text.replace(kotva4, "\n" + POUCENI + "\n---\n\n## 6. Návrhy na zlepšení", 1)

    # ── 5) §6: návrhy (na konec tabulky návrhů) ────────────────────────────
    kotva5 = "\n---\n\n## 7. Kam se zapisuje co"
    assert text.count(kotva5) == 1, "kotva pro §6 není 1×"
    text = text.replace(kotva5, "\n" + NAVRHY + "\n---\n\n## 7. Kam se zapisuje co", 1)

    K.write_bytes(text.encode("utf-8"))

    # ── Ověření: nic nezmizelo ─────────────────────────────────────────────
    po = K.read_bytes().decode("utf-8")
    stare = [l for l in pred.decode("utf-8").splitlines() if l.strip()]
    chybejici = [l for l in stare if l not in po]
    print("=" * 88)
    print("ZÁPIS DO `KRONIKA-PROJEKTU.md` — session 19")
    print("=" * 88)
    print("  řádků: %d -> %d" % (len(pred.decode("utf-8").splitlines()),
                                len(po.splitlines())))
    print("  bajtů: %d -> %d" % (len(pred), len(po.encode("utf-8"))))
    print("  neprázdných řádků původního textu, které v novém NEJSOU: %d"
          % len(chybejici))
    if chybejici:
        for l in chybejici[:5]:
            print("      CHYBI: %s" % l[:100])
        return 1

    r = subprocess.run([sys.executable, str(KONTROLA)], cwd=str(WS),
                       capture_output=True, timeout=300)
    v = r.stdout.decode("utf-8", "replace")
    for l in v.splitlines():
        if l.strip().startswith(("omylů celkem", "nálezů H", "sessions v kronice",
                                 "odkazů na .md", "KRONIKA SEDÍ", "CHYBA")):
            print("  %s" % l.strip())
    print("\n  `kronika-kontrola.py` → exit=%d" % r.returncode)
    if r.returncode != 0:
        print("\nVYSLEDEK: kronika NESEDÍ → exit 1")
        return 1
    print("\nVYSLEDEK: zapsáno, nic nezmizelo, brána kroniky sedí. exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
