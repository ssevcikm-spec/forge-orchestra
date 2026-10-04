# ZADÁNÍ PRO PLÁNOVACÍ (OVĚŘOVACÍ) SESSION

**Zkontrolováno při:** `d1cde9b` (orchestra — „Projití složky místo ručních seznamů
+ ukázky rozbitého kódování slovem") · `279f584` (uo-shadows — „Granule
`tests.harness` + lék na M3 (nález H12)") · **2. 10. 2026, 16:36 UTC**
**Stav obou repů při psaní:** `orchestra` = `d1cde9b` · `uo-shadows` = `279f584`
**Pushnuto:** **oba ANO** — `origin/main..HEAD = 0` v obou repech
**Necommitnuté:** `orchestra` **1 soubor** (`M tools/kontrola-diakritiky.py` —
přidán `ZADANI-DOKONCENI-AUDITU.md` do seznamu, Úkol 6b) · `uo-shadows` **čistý**
**Co je v `HANDOFF.md`:** **§23** (výsledky dokončení auditu) · **§8j** (vlastní
omyly **87–96**) · **§22** (ověření práce §21) · **§2** (co je otevřené)
**Co je v `KRONIKA-PROJEKTU.md`:** **19 sessions**, **91 omylů v 10 blocích**
(z toho **75 = 82 %** v měřidle), **28 nálezů** (H1–H28), **24 poučení**
(L1–L24), **23 návrhů** — **NA20–NA23 ve stavu `NEOVĚŘENO`**
**Co tenhle dokument JE:** zadání pro **plánovací** session, která přijde.
Není to stav (ten je v `HANDOFF.md`) ani plán (ten je v `PLAN-DALSI-KROK.md`).

> ## ⚠ PŘEČTI TYHLE DVĚ VĚCI PRVNÍ — jinak narazíš na to, na co už někdo narazil
>
> **1. `NEXT-SESSION-INSTRUKCE.md` NENÍ tvoje zadání.** Ten soubor patří
> **souběžné session**, která ho napsala v **17:38**; jeho obsah se od té doby
> **nezměnil ani o bajt** (SHA-256 `9c05c6b434d5d026…`, doloženo dvěma snapshoty).
> **Tvoje zadání je tenhle soubor.** Proč je oddělený, je vysvětlené v
> `HANDOFF.md` **§23.7** — a je to **nález H28**.
>
> **2. Zadání, ze kterého vzešla práce, kterou jdeš ověřovat, mělo
> NESPLNITELNÉ kritérium** (`HANDOFF.md` **§23.2**, nález **H24**). Nebylo to
> poprvé, co zadání tvrdilo něco, co měření nepotvrdilo. **Proto je tvůj první
> úkol ověřovat, ne věřit** — a to platí i na **tenhle** dokument.

---

## 1. Než začneš (povinné)

1. Přečti `PREDAVANI-SESSION.md` **§6.1** (co má plánovací session dělat),
   `AGENTS.md`, `HANDOFF.md` **§23 celý** (hlavně **§23.2**, **§23.5**,
   **§23.7**), **§8j** a `PLAN-DALSI-KROK.md`.
2. Načti skilly **`dsh-prostredi`** a **`overovani`** `skill` toolem.
   **V `overovani` je od 2. 10. 2026 nová sekce §10** — osm pastí měřidel
   naměřených přesně touhle prací (citace místo tvrzení, okno bez velikosti,
   přilepená značka času, ověřovatel s jiným oknem, mutace bez `try/finally`,
   čítač s cizím jménem, přehled místo brány, `Measure-Object -Line`).
   **Přečti ji dřív, než začneš psát měřidlo.**
3. **Ověř, že tohle zadání sedí na skutečnost** (jinak se v tom bodě zastav
   a zapiš to jako nález):
   ```powershell
   $env:PYTHONIOENCODING='utf-8'
   python _analyza\zadani-kontrola.py             # musí vyjít exit 0
   python _analyza\kronika-kontrola.py            # musí vyjít exit 0 (28 nálezů, 75 omylů v 8 blocích, které brána zná)
   python _analyza\handoff-kontrola-uplnost.py    # musí vyjít 83/83
   python _analyza\audit-snapshot.py --jen-kontrola --proti _analyza\snapshot-20261002-183213
   & orchestra\tools\git.cmd -C orchestra rev-parse HEAD
   & orchestra\tools\git.cmd -C games\uo-shadows rev-parse HEAD
   & orchestra\tools\git.cmd -C orchestra status --porcelain
   ```
4. **Pozor na DVĚ čísla téhož jména u omylů** (nález **H18**, `KRONIKA` §3):
   **75** = kolik jich vidí brána (zná **8 bloků pevným seznamem**),
   **89** = součet řádků tabulky v kronize (**10 bloků**),
   **94** = unikátních id v `HANDOFF.md`. **Žádné z nich není „to špatné".**

---

## 2. CO JDEŠ OVĚŘOVAT (práce session z 2. 10. 2026, 18:1x–19:0x)

**Předchozí session dokončila audit dokumentace** podle `ZADANI-DOKONCENI-AUDITU.md`.
**Tvůj úkol je zkusit ji vyvrátit** — ne ji opsat. Všechno, co tvrdí, je
v `HANDOFF.md` **§23**; **každé tvrzení má příkaz.**

### 2.1 Devět měřitelných tvrzení (u každého je příkaz)

| # | Co session tvrdí | Příkaz, kterým to ověříš | Co má vyjít |
|---|---|---|---|
| **1** | `AGENTS.md:63` už neodporuje sám sobě (39 má značku času) | `python _analyza\audit2a-schema.py` | `exit 0`, `ROZCHODŮ=0` |
| **2** | `ag-mutace.py` **proběhne** a je **v `g3-brany.py`** | `python _analyza\ag-mutace.py` | `exit 0`, `mutací=2, chyceno=2` |
| **3** | `ag-mutace.py` **umí spadnout** | `python _analyza\audit2a-mutace.py` **a** `python _analyza\ag-mutace.py` | 4/4 chyceny · 2/2 chyceny |
| **4** | `audit2b` **už nehlásí rozchod u `granulí`** | `python _analyza\audit2b-over.py` | `exit 0`, `granulí 0`, 2 mutace chyceny |
| **5** | **`HANDOFF.md` je NEDOTČENÝ** | hash proti `_analyza\snapshot-20261002-181237\manifest.json` | `451fc02aeea55000…` |
| **6** | Oba „neproběhnuvší" testy **mají hlavičku a pořád neprobíhají** | `python _analyza\audit3-hlavicky-over.py` | `exit 0`, 0 souhrnů testů |
| **7** | Všechny brány **otevřely**, co měly | `python _analyza\g3-brany.py` | **30 bran**, **1 nenulový exit** (`mutace A: pres-level` — správně) |
| **8** | Dokumenty odpovídají zdrojům | `python _analyza\hl-rizika-jazyka.py` · `python _analyza\g1-diakritika-novych.py` | oba `exit 0` |
| **9** | Inventář je **přegenerovaný** a `snapshot` se nepočítá jako dokument | `python _analyza\audit1-inventar.py` | `exit 0`, **101 dokumentů**, 8 záloh, žádný sloupec prázdný |

### 2.2 Tři věci, které NEMAJÍ být ověřeny jako „hotové" — jsou to nálezy

- **H24** — kritérium Úkolu 1 v zadání bylo **nesplnitelné**; brána
  `audit2a-schema.py` **měřila citaci místo tvrzení** a vadu R1 **nikdy
  neviděla**. Session to opravila **v měřidle** a v `AGENTS.md`, ale
  **zkontroluj obojí** — je to nejcennější nález té session a nejvíc se hodí
  k vyvrácení.
- **H25** — `audit2b` má **27 rozchodů, z toho většinu falešných**, protože
  veličina `kontrol` srovnává čísla z **různých bran**. **Záměrně neopraveno**
  (zadání žádalo jen `granulí`) → **návrh NA22**.
- **H28** — kritérium „porovnej `mtime` s 17:38" dalo **nepravdivou odpověď**
  (`mtime` hnul **mutační test**, obsah se nezměnil). → **návrh NA20**.

### 2.3 Kde je session nejzranitelnější (tam míř první)

1. **Vlastní měřidla.** Sedm z osmi omylů té session je **v měřidlech** a
   **dva z nich odhalil až mutační test** (`overovani` §10.3 a §10.4). Kdo se
   ptá „je ta oprava správná?", má největší šanci u `audit2a-schema.py`
   a `audit2b-cisla-proti-zdroji.py`.
2. **Exempce, které jsem zavedl.** `audit2b` teď **nehlídá append-only
   dokumenty** (`HANDOFF.md`, `KRONIKA-PROJEKTU.md`) — **přiznaná mez**
   v docstringu. **Ověř, že to není slepota**: vlož do `HANDOFF.md` (do
   **nedatovaného** oddílu) tvrzení, které zdroji neodpovídá, a podívej se,
   **jestli to brána ohlásí.** Když ne, je to nález — a vrátit dokument zpět.
3. **`audit-snapshot.py` počítá `AGENTS.md` dvakrát** (jako `jadro/`
   i `koren/`), takže „změněné obsahem = 3" je ve skutečnosti **2 soubory**.
   Je to kosmetika, ale je to **naměřené** a nemá to být zamlčené.

---

## 3. CO MÁŠ UDĚLAT (v tomto pořadí)

1. **Ověř devět tvrzení z §2.1** — spuštěním, ne čtením. U každého napiš
   **výstup**, ne „prošlo".
2. **Zkus vyvrátit aspoň jedno.** Pokud se to nepovede, **napiš to taky** —
   „nic jsem nevyvrátil" je tvrzení, které se ověřuje (`PREDAVANI-SESSION.md` §7).
3. **Projdi `_analyza\AUDIT-DOKUMENTACE.md` §6** (opatření 1–13) a porovnej
   se stavem: **která jsou hotová, která ne, a která nemají vlastníka**
   (nález **H26** — opatření 2 a 3 nebyla zadáním přidělena žádné session).
4. **Rozhodni návrhy `NA17`–`NA23`** v `KRONIKA-PROJEKTU.md` **§6** — každý
   na `APLIKOVÁNO` / `ZAMÍTNUTO` / `ODLOŽENO` **s důvodem** (§2.2). **Tohle je
   povinná část ověření**, ne dobrovolná.
5. **Napiš `PLAN-DALSI-KROK.md`** — co dál, proč, v jakém pořadí, s rizikem,
   a **výslovně, co NEDOPORUČUJEŠ dělat**.
6. **Napiš zadání pro akční session** (hlavička podle §3 `PREDAVANI-SESSION.md`):
   cíl, naměřená fakta s příkazy, úkoly, **„Hotovo znamená"** u každého
   (měřitelné), a **co NEDĚLAT**.

---

## 4. HOTOVO ZNAMENÁ (měřitelné)

- [ ] Devět tvrzení z §2.1 ověřeno **spuštěním**, u každého je **výstup**
- [ ] Aspoň jedno tvrzení **vyvráceno nebo zpřesněno** (nebo je doloženo, že ne)
- [ ] U **každé** spuštěné brány je ověřeno, že **soubor otevřela** (kolik)
- [ ] `AUDIT-DOKUMENTACE.md` §6: u každého ze 13 opatření je stav a vlastník
- [ ] Návrhy **NA17–NA23** rozhodnuté s důvodem
- [ ] `PLAN-DALSI-KROK.md` je aktuální (s datem spotřeby v hlavičce)
- [ ] Zadání pro akční session má hlavičku podle §3 a **měřitelné „Hotovo"**
- [ ] `HANDOFF.md` — nová sekce s výsledky, **vlastní omyly do §8**, nic nezmizelo
      (`handoff-kontrola-uplnost.py` → **83/83**)
- [ ] `KRONIKA-PROJEKTU.md` — **řádek**, nálezy, poučení, návrhy;
      `kronika-kontrola.py` → **`exit 0`**
- [ ] Nový dokument → do seznamu v `kontrola-diakritiky.py`
- [ ] `_analyza\_inventar.json` **přegenerovaný**, když sáhneš na kód nebo skill

---

## 5. CO NEDĚLAT

- **⚠ NEPŘEPISUJ `NEXT-SESSION-INSTRUKCE.md`.** Patří souběžné session; jeho
  obsah je **platné zadání** a zahodit ho je přesně ta škoda, kterou dokumentuje
  `SOUBEH-SESSION-NALEZY.md`. **Tvoje zadání je tenhle soubor** a zadání pro
  **další** session napiš **do nového souboru** (`ZADANI-<téma>.md`), dokud
  někdo nerozhodne, že `NEXT-SESSION-INSTRUKCE.md` je zase volný.
- **Neopravuj kód.** Jsi **plánovací (ověřovací)** session: kdo píše zadání,
  **nesmí si ho zároveň plnit** (`PREDAVANI-SESSION.md` §5). Když najdeš vadu,
  **zapiš ji** a **napiš na ni zadání** — ne opravu.
- **Nemaž nic** — ani „21 granul" v `HANDOFF.md` §14–§21 (datované záznamy),
  ani `h17-mutace-a.py`, ani `mutace-testu.py`, ani `_analyza\snapshot-*`.
- **Nepřepisuj historická čísla** (A2). Rozdíl je **čas**, ne nepravda.
  `HANDOFF.md` a `KRONIKA-PROJEKTU.md` jsou **append-only** — jen se doplňují.
- **Nepushuj bez vyžádání.** Předem ukaž `git status` a `git diff --stat`
  a **počkej**.
- **Nezmenšuj `HANDOFF.md`** — to je samostatná session C a má nejvyšší riziko.

---

## 6. KDE JE PRÁCE, KTERÁ ČEKÁ NA ROZHODNUTÍ ČLOVĚKA (ne agenta)

Z auditu (`AUDIT-DOKUMENTACE.md` §6 a §7) zůstávají **tři otázky pro uživatele** —
**neřeš je sám**:

1. verdikty u **6 sirotků** v `_analyza\` (audit navrhuje: nechat, označit
   jako spotřebovaný meziprodukt),
2. co s **3 dokumenty zmíněnými jen v odškrtnuté `[x]` položce**
   v `OTEVRENA-TEMATA.md`,
3. zda **251 nezapojených skriptů** v `_analyza\` někdo potřebuje.
