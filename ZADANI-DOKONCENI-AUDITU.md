# ZADÁNÍ — DOKONČENÍ AUDITU A PROVEDENÍ OPATŘENÍ

**Zkontrolováno při:** `d1cde9bbf` (orchestra) · `279f58486` (uo-shadows)
**Datum:** 2. 10. 2026, 18:05 UTC+2
**Stav obou repů:** **čisté** (`status --porcelain` = 0) a **pushnuté**
(`origin/main..HEAD` = 0 v obou)
**Co tenhle dokument JE:** **zadání pro AKČNÍ session.** Není to stav (ten je
v `HANDOFF.md`) ani plán (ten je v `PLAN-DALSI-KROK.md`).
**Podklad:** `_analyza\AUDIT-DOKUMENTACE.md` — naměřená fakta, o která se
tohle zadání opírá. **Nemusíš je měřit znovu; musíš je ověřit, než na nich
postavíš.**

> ### ⚠ DVĚ VĚCI, KTERÉ MUSÍŠ VĚDĚT DŘÍV, NEŽ ZAČNEŠ
>
> **1. `NEXT-SESSION-INSTRUKCE.md` NEPŘEPISUJ.** Ten soubor patří **souběžné
> session**, která ho naposledy zapsala v **17:38** (naměřeno). Kdybys ho
> přepsal, zahodíš cizí práci — a to je přesně ta škoda, kterou dokumentuje
> `SOUBEH-SESSION-NALEZY.md`. Tenhle dokument je proto **samostatný**.
>
> **2. Než začneš psát, zjisti, jestli v workspace nepracuje jiná session.**
> V průběhu auditu **pracovala** — `HANDOFF.md` 17:33, `NEXT-SESSION-INSTRUKCE.md`
> 17:34 a 17:38, **`AGENTS.md` 17:38**. Nástroj:
> `node _analyza\dsh-session-prehled.mjs`
> **Důsledek, který se nesmí zopakovat:** audit naměřil čísla, a ta se mu
> v průběhu měnila pod rukama. Proto je **Úkol 0 zmrazení snapshotu** — dělej
> ho PRVNÍ, ne poslední.

---

## 1. NEŽ ZAČNEŠ (povinné, ale krátké — schválně)

Přečti **jen tohle** (audit naměřil, že povinné čtení je nejdražší položka
session — 503 511 znaků; nezvětšuj to):

1. `_analyza\AUDIT-DOKUMENTACE.md` — **§0** (odpověď na otázku), **§2** (rozpory
   R1–R6), **§5.6** (brány), **§6** (opatření). Zbytek podle potřeby.
2. `AGENTS.md` — pravidla. **Hlavně**: „Než začneš", „Jak ověřovat",
   „Co nikdy".
3. Skilly `dsh-prostredi` a `overovani` (`skill` toolem) — pasti prostředí
   a jak ověřit, že brána měří.

**Nepovinné, ale užitečné:** `_analyza\audit6-vysledky.json` (pokrytí bran).

---

## 2. CO JE NAMĚŘENÉ (neopakuj měření — ověř ho)

| Zjištění | Naměřeno | Příkaz, kterým to ověříš |
|---|---|---|
| Všech 29 bran dohromady | **40,75 s** | `python _analyza\audit5-cas-bran.py` |
| Povinné čtení | **503 511 znaků** | `python _analyza\audit5b-cena-cteni.py` |
| `HANDOFF.md` = 85 % historie | 3 616 řádků, stav je posledních **183** | `python _analyza\audit3-duplikace.py` |
| **R1** `AGENTS.md` si odporuje (39 vs 40) | zdroj = **40** | `python _analyza\audit2a-schema.py` → **`exit 1`** |
| **R5** `ag-mutace.py` neproběhne | `exit 1`, obě mutace „NEZMUTOVANO" | `python _analyza\ag-mutace.py` |
| **R6** 2 mutační testy se nedají spustit | `h17-mutace-a.py`, `mutace-testu.py` | tamtéž, viz §5.6 auditu |
| ~~**R3** `HANDOFF.md` tvrdí „21 granul", živě **22**~~ | **STAŽENO — není to vada** | `python _analyza\audit7-overeni-zadani.py` — 11× „21" je **všechno v datovaných oddílech §14–§21**, kde bylo 21 správně |
| Dokumentů bez hlavičky | **62 z 98** | `python _analyza\audit1-inventar.py` |
| Dokumentů mimo git | **98 ze 98** | tamtéž (`v_gitu` = NE) |
| Bran s doloženým mutačním testem | **20 z 30** | `python _analyza\audit6-brany-mutace.py` |

---

## 3. ÚKOLY (v tomto pořadí — pořadí je závazné)

### Úkol 0 — ZMRAZIT SNAPSHOT *(dělej první)*

**Proč:** audit naměřil, že se dokumenty mění v průběhu práce. Bez snapshotu
naměříš zase něco jiného a nebude se to dát porovnat.

**Co udělat:** napiš `_analyza\audit-snapshot.py`, který
1. zkopíruje jádro (8 dokumentů), všech 37 `.md` v kořeni a 12 skillů do
   `_analyza\snapshot-<RRRRMMDD-HHMM>\`,
2. zapíše `manifest.json` s **SHA-256, velikostí a mtime** každého souboru,
3. po druhém spuštění **vypíše, co se od minule změnilo** (porovnáním hashů),
4. skončí `exit 1`, když se některý soubor změnil od posledního snapshotu.

**Hotovo:** snapshot existuje, manifest má u **každého** souboru hash
(žádné prázdné), a druhé spuštění hlásí rozdíly — ne ticho.

---

### Úkol 1 — OPRAVIT R1: ROZPOR V AUTORITĚ

**Kde:** `AGENTS.md`, řádek **62–63**. Dnes tam stojí (doslova):

> `AGENTS.md` tvrdil u `conductor/schema.sql` **„32 sloupců"**, správně je
> **39** — a schéma se přitom od 30. 9. **nezměnilo** …

**Co je špatně:** číslo **39** je tam **v přítomném čase a bez značky času**,
zatímco `AGENTS.md:337` tvrdí **40** a živý zdroj je **40**.

**Proč to není lež:** 39 bylo správně **do B1** (2. 10. 2026), než přibyl
sloupec `naposledy_selhalo`. Rozdíl je **čas**.

**Co udělat (A2 — historická čísla se NEPŘEPISUJÍ, jen označují):**
doplnit k „39" značku času, např. `**39** (stav před B1; dnes **40**)`.
**Nic dalšího v tom odstavci neměň** — je to poučení a to je správné.

**Hotovo:** `python _analyza\audit2a-schema.py` → **`exit 0`** (dnes `exit 1`).

---

### Úkol 2 — OPRAVIT R5: MUTAČNÍ TEST AUTORITY

**Kde:** `_analyza\ag-mutace.py`, řádky **57, 63, 64, 80, 84**.

**Co je špatně:** skript hledá v `AGENTS.md` **doslovný řetězec `39 sloupců`**.
Ten v dokumentu **není** (ověřeno `Select-String -SimpleMatch` → **0 výskytů**),
takže `pocet != 1` → obě mutace se **neprovedou** → `exit 1`.
A protože `ag-mutace.py` **není v seznamu `BRANY` v `g3-brany.py`** (ověřeno:
`grep` → 0 výskytů), **nikdo to nevidí**.

**Co udělat:**
1. Změň kotevní řetězec na ten, který v dokumentu **skutečně je a je
   jednoznačný**: `40 sloupců` (řádek 337, výskytů **1**).
   Mutace pak je `40 sloupců` → `32 sloupců`.
2. Zachovej **obě** kontroly, které tam už jsou: `assert`, že se text změnil,
   **A** `assert`, že vada je v souboru po zápisu (past `overovani` §7.9).
3. **Přidej `ag-mutace.py` do `BRANY` v `g3-brany.py`** — jinak se to za měsíc
   rozbije znovu a zase si toho nikdo nevšimne.

**Hotovo:**
- `python _analyza\ag-mutace.py` → **`exit 0`**
- a **hlavně**: vlož vadu do `AGENTS.md:337` (`40` → `32`) ručně, spusť
  `python _analyza\ag-over-cisla.py` a **musí spadnout**. Pak vadu vrať.
  Bez tohohle kroku nevíš, že test měří.

---

### Úkol 3 — POJMENOVAT R6: TESTY, KTERÉ NEPROBĚHNOU

**Kde:** `_analyza\h17-mutace-a.py` a `_analyza\mutace-testu.py`.

**Naměřeno:** první padá na `AssertionError: worktree neexistuje`
(`_analyza\h17-kladna` neexistuje), druhý na
`CHYBA: 9efbb076…:scripts/save.gd nejde přečíst (rc=128)`.

**Co udělat:** **NEMAŽ je** (A1, A7). Na začátek každého napiš komentář:
co je to za test, **že dnes neproběhne**, **proč** (konkrétní naměřená chyba)
a **co by ho zprovoznilo**. Cíl: kdo uvidí `exit 1`, nesmí si to splést
s nálezem o kódu (`overovani` §7.13 — „neproběhlo" je **třetí stav**).

**Hotovo:** oba soubory mají hlavičku s důvodem; v `AUDIT-DOKUMENTACE.md` §5.6
je stav pořád pravdivý (případně ho doplň).

---

### Úkol 4 — NIC NEOPRAVUJ V `HANDOFF.md` (R3 je staženo)

**Tohle je v zadání schválně jako „úkol", aby se neudělalo.**

Audit nejdřív tvrdil, že `HANDOFF.md` „lže" o počtu granulí (21 vs. živých 22).
**Přeměřeno 18:0x → nález NEPLATÍ** a je **stažen** (`AUDIT-DOKUMENTACE.md` §2, R3):

| | Naměřeno |
|---|---|
| `21 granul` v `HANDOFF.md` | **11 míst — všechna v oddílech §14–§21** |
| `22 granul` | 6 výskytů — v §21 a §22 |
| míst s „21", která popisují DNEŠNÍ stav | **0** |

Oddíly §14–§21 jsou **datované záznamy**. V té době bylo 21 správně — granule
`tests.harness` teprve vznikala, a §21 sám obojí vypráví (nejdřív ověří
„21, `harness` 0×", po přidání hlásí 22). **Přepsat to by byla A2 v akci.**

**Co tedy UDĚLAT:** nic v `HANDOFF.md`. Místo toho **oprav nástroj**, který
ten falešný nález vyrobil:

- `_analyza\audit2b-cisla-proti-zdroji.py` — jeho heuristika `CITACE` hledá
  slova v **okolí** („tvrdil", „dřív", „bylo"). **Datum v NADPISU oddílu**
  jí projde, ačkoli je to nejsilnější znak minulosti.
- **Doplň:** najdi oddíl, do kterého výskyt patří (`## …`), a když jeho nadpis
  obsahuje **datum nebo „Provedeno"/„Ověření"**, zařaď výskyt jako `[záznam]`
  — ne mezi rozchody.
- **Ověř mutací:** `21 granul` na řádku 1143 musí po opravě zmizet
  z „ROZCHODŮ" a objevit se v „ZÁZNAMECH".

**Hotovo:** `python _analyza\audit2b-cisla-proti-zdroji.py` už **nehlásí
žádný rozchod u `granulí`**, a `HANDOFF.md` je **nedotčený**.

---

### Úkol 5 — OVĚŘIT, ŽE SE NIC NEROZBILO

Spusť **všechno** a zapiš výsledky:

```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\audit2a-schema.py              # musí být exit 0
python _analyza\ag-mutace.py                   # musí být exit 0
python _analyza\handoff-kontrola-uplnost.py    # musí být 83/83
python _analyza\kronika-kontrola.py            # musí být exit 0
python _analyza\audit1-inventar.py             # žádný sloupec nesmí být prázdný
python _analyza\audit6-brany-mutace.py         # nesmí přibýt "neproběhlo"
python _analyza\g1-diakritika-novych.py        # musí být exit 0
python _analyza\g3-brany.py                    # 29 bran, porovnej s baseline
python _analyza\audit-snapshot.py              # co se změnilo proti Úkolu 0
```

**Baseline pro `g3-brany.py`** (naměřeno v auditu, 2. 10. 2026): **29 bran**,
**2 nenulové exity** — `mutace A: pres-level` (`exit 1`, a to je SPRÁVNĚ)
a `validate-all (CELEK)` (`exit 1`, **NEPROBĚHLO — PROSTŘEDÍ**, ne regrese).

---

### Úkol 6 — POVINNÉ ZÁPISY A REGENERACE INVENTÁŘE

Tohle **není práce navíc** — je to povinná část každé akční session podle
`PREDAVANI-SESSION.md` **§6.2 D a D1**. Vynechání má konkrétní následek,
proto je to tady vyjmenované:

**a) PŘEGENERUJ INVENTÁŘ — pokaždé, když sáhneš na kód.**
```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json
```
`_analyza\_inventar.json` je **generovaný meziprodukt** a `hl-rizika-jazyka.py`
ho porovnává s **otiskem vstupů** (772 souborů, `sha256`). Když zestará, brána
**správně** skončí `exit 1` — a kdo to neví, hledá vadu v nástroji.
**Vstupem skeneru je i `kontrola-diakritiky.py` a každý skill, do kterého
píšeš** — naměřeno: **dvakrát v jedné session**. **Nevypínej tu kontrolu.**

**b) Nový dokument → přidej ho do seznamu v `kontrola-diakritiky.py`.**
Týká se to i **tohohle zadání** (`ZADANI-DOKONCENI-AUDITU.md`).
*(Ruční seznam je vada S27 a opatření 6 ho jednou nahradí projitím složky —
 ale dokud existuje, platí konvence. Nebuď překvapený, že to je ruční krok;
 audit to naměřil jako nejdražší položku projektu.)*

**c) Zápisy (nic se nemaže):**
- výsledky → `HANDOFF.md`
- **vlastní omyly → `HANDOFF.md` §8** — i ty v měřidle. Je to nejsilnější
  důkaz, že se měřilo.
- nové pasti měřidel → `AGENTS.md` a skill `overovani`
- **řádek → `KRONIKA-PROJEKTU.md`** + nové návrhy do jejího §5 ve stavu
  `NEOVĚŘENO`

**d) Na konci spusť VŠECHNY brány a u každé ověř, že soubor OTEVŘELA**
(kolik souborů / kontrol). `exit 0` bez počtu je ticho, ne zelená.

---

## 4. HOTOVO ZNAMENÁ (měřitelné)

- [ ] `_analyza\snapshot-*/manifest.json` existuje a **každý** soubor má hash
- [ ] `audit2a-schema.py` → `exit 0` (R1 opraven)
- [ ] `ag-mutace.py` → `exit 0` **a je v `g3-brany.py`** (R5 opraven)
- [ ] Vložená vada do `AGENTS.md:337` **shodí** `ag-over-cisla.py` — doloženo
- [ ] `h17-mutace-a.py` i `mutace-testu.py` mají hlavičku s důvodem (R6)
- [ ] `audit2b-cisla-proti-zdroji.py` po opravě **nehází falešný rozchod u `granulí`**
- [ ] **`HANDOFF.md` je NEDOTČENÝ** — dolož hash/mtime proti Úkolu 0
- [ ] `handoff-kontrola-uplnost.py` → **83/83** (kontrola, že se nic nerozbilo)
- [ ] `kronika-kontrola.py` → `exit 0`
- [ ] `g1-diakritika-novych.py` → `exit 0`
- [ ] `g3-brany.py` → 29 bran, **žádný nový nenulový exit** proti baseline
- [ ] `_analyza\_inventar.json` **přegenerovaný** (`hl-rizika-jazyka.py` → `exit 0`)
- [ ] `ZADANI-DOKONCENI-AUDITU.md` **přidaný do seznamu** v `kontrola-diakritiky.py`
- [ ] **Zápisy hotové:** `HANDOFF.md` (výsledky + vlastní omyly v §8) ·
      řádek v `KRONIKA-PROJEKTU.md` · zadání pro další session (§6.2 F)
- [ ] **`git status --porcelain` v obou repech je čistý** (nebo je vysvětleno, co v něm je)

---

## 5. CO NEDĚLAT

- **NEPŘEPISUJ `NEXT-SESSION-INSTRUKCE.md` NA ZAČÁTKU** — patří souběžné
  session (napsala ho v 17:38). **Na konci session se ho ale dotknout MUSÍŠ**
  podle `PREDAVANI-SESSION.md` §6.2 F, protože je to řetěz předávání.
  **Jak to rozhodnout:** porovnej jeho `mtime` s **17:38**. Když se mezitím
  změnil, **pracuje v něm jiná session** → napiš zadání pro další session
  do **nového souboru** (`ZADANI-<téma>.md`) a v `HANDOFF.md` napiš proč.
  Když se nezměnil, přepiš ho podle konvence.
- **Nemaž nic.** Ani `h17-mutace-a.py`, ani „21 granul", ani záložny `*-pred-*`.
- **Nepřepisuj historická čísla** (A2). Rozdíl je čas, ne nepravda.
- **⚠ Než označíš číslo za vadu, zjisti, K ČEMU PATŘÍ.** Tohle je poučení
  z R3 (staženo): `HANDOFF.md` má správně obsahovat stará čísla, protože je to
  **append-only záznam**. Rozpor vzniká jen tam, kde dokument tvrdí, že
  popisuje **dnešek**. Ptej se „je to záznam, nebo tvrzení?" — ne jen
  „sedí to na zdroj?". Nástroj `audit2b` tuhle otázku zatím neumí (Úkol 4).
- **Nezmenšuj `HANDOFF.md`** v téhle session — to je Úkol pro session C a má
  nejvyšší riziko. Tady se jen opravuje číslo.
- **Nedělej víc než tyhle úkoly.** Audit naměřil, že příčinou pomalé práce je
  nabobtnalý vstup, ne málo práce v session. Když úkoly stihneš dřív, **skonči
  a předej** — nezačínej další opatření „když je čas".
- **Nepiš zjištění jen do chatu.** Patří do `HANDOFF.md` (jako nález)
  a `KRONIKA-PROJEKTU.md` (jako řádek).

---

## 6. CO JE NAD RÁMEC TÉHLE SESSION (roadmap pro další)

Tohle **neprováděj** — je to proto, aby se to nezačalo dělat „mimochodem".

| Session | Opatření | Riziko | Proč samostatně |
|---|---|---|---|
| **B** | **6** ruční seznam → projití složky (105 cest, 96 řádků komentářů) · **7** hlavičky 62 dokumentům · **8** verzovat dokumentaci (98 souborů mimo git) | nízké | Objemné, ale bezpečné. **Nejlepší poměr přínos/riziko ze všech.** |
| **C** | **4+5** `HANDOFF.md`: pravidla na odkaz, oddíly §10–§22 do kroniky (3 056 řádků) | **VYSOKÉ** | 84,5 % dokumentu. **Největší přínos pro čas, největší riziko.** Nutně `83/83` + porovnání **množiny** klíčových bodů, ne počtu |
| **D** | **10** zrušit/ztlumit brány bez výsledku (3× `otevřela: —`) · **12** doplnit mutační testy 9 branám | vysoké / střední | **Jen po mutačním testu PŘED zrušením** |

**Rozhodovací session (uživatel, ne agent):**
- verdikty u **6 sirotků** v `_analyza\` (audit navrhuje: nechat, označit jako
  spotřebovaný meziprodukt)
- co s **3 dokumenty zmíněnými jen z odškrtnuté `[x]` položky**
  v `OTEVRENA-TEMATA.md`
- zda **251 nezapojených skriptů** v `_analyza\` někdo potřebuje
  (to je otázka pro člověka, ne pro skript)

---

## 7. NÁSTROJE, KTERÉ MŮŽEŠ POUŽÍT (z auditu, všechny spustitelné)

| Nástroj | Co dělá |
|---|---|
| `audit0-snimek.py` | otisk jádra s časem |
| `audit1-inventar.py` | generovaný inventář 98 dokumentů × 12 sloupců |
| `audit1-mutace.py` | mutační test inventáře (3/3) |
| `audit2a-schema.py` | **číslo proti zdroji** — sloupce schématu, `exit 1` při rozchodu |
| `audit2b-cisla-proti-zdroji.py` | 9 veličin proti živým zdrojům |
| `audit3-duplikace.py` | opakovaná pravidla + rozklad `HANDOFF.md` |
| `audit4-umisteni.py` | co je na špatném místě |
| `audit5-cas-bran.py` | wall time každé z 29 bran |
| `audit5b-cena-cteni.py` | cena povinného čtení |
| `audit6-brany-mutace.py` | umí každá brána spadnout? |
| `audit-cleanup.py` | převod výstupů z UTF-16LE na UTF-8 |

> ⚠ **`audit2-rozpory.py` je SLEPÝ nástroj** — hledá „táž veličina, různé
> hodnoty" pouhým vzorem a najde 15 „rozporů", z toho téměř všechny falešné
> (různé brány hlásí různé počty kontrol **správně**). Nechán v repu
> **s varováním v docstringu**. Používej `audit2b-*`.
>
> ⚠ **Výstupy neukládej přes `>` v PowerShellu** — zapíše UTF-16LE a brána
> diakritiky to pak buď nepřečte, nebo **tiše přeskočí**. Piš je Pythonem
> nebo je převeď `audit-cleanup.py` (naměřeno: stálo to jedno falešné červené).
