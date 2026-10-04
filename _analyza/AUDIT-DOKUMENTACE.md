# AUDIT DOKUMENTACE — co přebývá, co si odporuje, co zdržuje

**Co tenhle dokument JE:** **záznam o provedení auditu** (fáze 1–6 plánu).
Není to zadání a **nic podle něj ještě není provedeno** — audit navrhuje
(pravidlo A3: autor auditu nesmí být ten, kdo podle něj maže).

**Kdy měřeno:** 2. 10. 2026, **17:1x–17:40** (lokální čas).
**Pravidlo A2 platí i na tenhle dokument:** každé číslo níž je **měření
v určitém čase**. Kde se soubor změnil v průběhu auditu, je to u čísla řečeno.

> ### Změřeno — a v průběhu auditu se to hnulo
> Během auditu **pracovala v témže workspace jiná session**. Naměřené zápisy:
> `PLAN-DALSI-KROK.md` 17:31:07 · skill `overovani` 17:32:52 (přibyla mu celá
> sekce **§9 „Desátá až šestnáctá past"**) · `dsh-prostredi` 17:32:44 ·
> `HANDOFF.md` 17:33:28 · `NEXT-SESSION-INSTRUKCE.md` 17:34:01 a **znovu
> 17:38:17** · **`AGENTS.md` 17:38:18**.
>
> **Není to detail — je to nález:** audit dokumentace se v tomhle workspace
> **nedá dělat na živých datech**, protože se pod rukama mění. Každé číslo
> proto níž nese čas.
>
> **A jedna věc se tím už vyřešila:** nález **R2** (zadání uvádělo „81 omylů
> v 9 blocích", brána hlásí 75) souběžná session **opravila v 17:38** — a líp,
> než jsem navrhoval: rozlišila **tři čísla téhož** (75 = co vidí brána,
> 81 = součet, 86 = unikátních). To je přesně ta odpověď, kterou `AGENTS.md`
> žádá („různé čítače nesou stejné jméno").
>
> **Naopak R1 a R5 se zápisem v 17:38 nezměnily** — ověřeno znovu v 17:4x:
> `AGENTS.md:62` i `:337` jsou na stejných řádcích se stejnými hodnotami
> (`audit2a-schema.py` → `exit 1`, 6 rozchodů) a vzor `39 sloupců`
> v `AGENTS.md` **není** → `ag-mutace.py` dál neproběhne.

---

## 0. ODPOVĚĎ NA OTÁZKU, KVŮLI KTERÉ AUDIT VZNIKL

> *„Práce agenta z pár minut trvá třeba půl hodiny — možná je to kvůli dokonalé
> metodice, možná kvůli nesmyslným nabobtnalým instrukcím."*

**Odpověď: je to to druhé. Metodika (brány) stojí 41 sekund. Vstup stojí
půl milionu znaků.**

| Co se měřilo | Naměřeno | Jak |
|---|---|---|
| **Všech 29 bran dohromady** | **40,75 s** | `python _analyza\g3-brany.py` pod `Measure-Command` |
| Týž součet nezávisle (přes šavli) | 42,2 s | `python _analyza\audit5-cas-bran.py` |
| **Povinné čtení před první prací** | **546 212 B / 7 421 řádků / 503 511 znaků** | `python _analyza\audit5b-cena-cteni.py` |
| Odhad tokenů z toho | ≈ 140–170 tis. (÷3 znaky/token) | heuristika, **ne měření** |
| Povinných dokumentů k přečtení | **10** | podle `NEXT-SESSION-INSTRUKCE.md` §1 |
| Povinných příkazů na začátku | **9** | tamtéž |

**Poměr je 1 : 12 000.** Kdyby šlo jen o běh bran, je session hotová za
tři čtvrtě minuty. Čas jde na **zpracování vstupu** — a u největšího dokumentu
je 85 % toho vstupu **append-only historie**, kterou agent musí přečíst, aby
v ní našel těch 5 %, které platí dnes:

| `HANDOFF.md` | Naměřeno |
|---|---|
| celkem | **3 616 řádků, 24 oddílů, 282 130 B** |
| **poslední oddíl (§22), tedy „stav"** | **183 řádků = 5,1 %** |
| oddíly §10–§22 (historie) | **3 056 řádků = 84,5 %** |
| jen §17 + §18 (dvakrát „ověření práce") | **1 219 řádků = 33,7 %** |

> **Pozor na výklad:** není to tvrzení, že historie je zbytečná. `KRONIKA-PROJEKTU.md`
> má historii **schválně** a je to správně. Vada je, že **historie a stav jsou
> v jednom souboru** — takže se stav nedá přečíst bez historie.

---

## 1. FÁZE 1 — INVENTÁŘ (generovaný, ne ruční)

**Nástroj:** `_analyza\audit1-inventar.py` → `_analyza\audit-inventar.json`
**Výstup:** `_analyza\audit1-vystup.txt`

```
dokumentů celkem        : 98   (37 kořen + 49 _analyza + 12 skillů)
živých / sirotků / záloh / kopií: 77 / 7 / 8 / 6
bez hlavičky „Co tenhle dokument JE": 72
mimo git (oba repy)     : 98
druh NEURČENO           : 5
Žádný sloupec nezůstal prázdný (každý dokument má všech 12).
```

> **Dvě poznámky k těm číslům (obojí je nález, ne detail):**
> 1. **Je to 98, ne 97** — inventář vidí **i tenhle auditní dokument**. Je to
>    správně: `AUDIT-DOKUMENTACE.md` v kořeni jádra zmíněný není a v ručním
>    seznamu žádné brány taky ne, takže **vychází jako sirotek** — tedy přesně
>    ten stav, který audit vytýká ostatním. (V `_analyza` to není vada; je to
>    pracovní dokument. Ale je to pěkná ilustrace, že „sirotek" není urážka.)
> 2. **Mezi prvním a posledním během auditu se počty hnuly** (živých 85 → 77):
>    nebyla to chyba měření, ale **dokončení klasifikace** — doplnil jsem
>    kategorii `kopie` pro fixtury (`_analyza\patch\`, `patch-test\`) a hledání
>    zálohy ve **celé cestě**, ne jen ve jménu souboru. Šest fixtur a dvě
>    zálohy se tím přesunuly ze „živých" tam, kam patří.

### Dvě vady, které odhalil SÁM SOBĚ (a jsou poučením)

Inventář měl v první verzi **dvě slepá místa** — a obě by vyrobila falešný
nález. Uvádím je, protože jsou to **tytéž pasti, které audit hledá v projektu**:

| # | Co jsem udělal špatně | Jak se to projevilo | Oprava |
|---|---|---|---|
| 1 | „Je v bráně?" počítalo **i projití složky** (`g1-diakritika-novych.py`) | **sirotků vyšlo 0 z 97** — kategorie byla prázdná, protože brána procházející složku „otevírá" každý soubor. Je to táž vada jako brána, která projde nad čímkoli | rozlišeno na **ruční seznam** (úmysl) vs. **projití složky** (automat) |
| 2 | Klíčem zmínky byl **kmen jména souboru** | `SKILL.md` má kmen „SKILL" (5 znaků) → **každý skill vycházel jako sirotek**, i když se o `dsh-prostredi` píše v jádru 19× | u skillu je klíčem **jméno složky** |

### Sirotci — 6, všichni v `_analyza\`

| Soubor | B | řádků | Co to je |
|---|---|---|---|
| `_analyza\s16-novy-oddil.md` | 25 873 | 387 | pracovní úryvek pro handoff |
| `_analyza\s21-oddil.md` | 13 514 | 170 | totéž |
| `_analyza\s21b-oddil-8h.md` | 7 942 | 18 | totéž |
| `_analyza\s8e-novy-oddil.md` | 5 151 | 31 | totéž |
| `_analyza\pr-mining-body.md` | 2 536 | 29 | neurčeno |
| `_analyza\s8f-omyl60.md` | 790 | 1 | jeden řádek tabulky omylů |

**Verdikt (návrh k potvrzení):** je to **pracovní materiál, ne dokumentace**.
Vznikl jako text, který se vložil do `HANDOFF.md` skriptem — a po vložení
zůstal ležet. **Není to „zapomenutý dokument"** (to by byl nález); je to
**spotřebovaný meziprodukt**. Doporučení: **nechat, ale označit** hlavičkou
„vloženo do HANDOFF.md §X, dál se nevyvíjí" — mazat se nemá (A1/A7).

### Nález, který inventář vydal mimo zadání

**Všech 97 dokumentů je mimo verzovací systém.** Kořen workspace **není git
repo** (`.git` neexistuje) a oba repozitáře (`orchestra`, `games\uo-shadows`)
obsahují jen své vlastní stromy. Důsledek: **dokumentace nemá historii změn** —
nedá se zjistit, co se v `AGENTS.md` změnilo a kdy, a omylem přepsaný dokument
se nedá vrátit. Přitom `AGENTS.md` staví pravidla na `git diff`,
`git cat-file` a „autorita je blob v `HEAD`".

---

## 2. FÁZE 2 — ROZPORY (nejcennější fáze)

**Nástroje:** `_analyza\audit2a-schema.py`, `_analyza\audit2-rozpory.py`,
`_analyza\audit2b-cisla-proti-zdroji.py`
**Výstupy:** `_analyza\audit2-vystup.txt`, `_analyza\audit2b-vystup.txt`

### R1 — `AGENTS.md` si odporuje SÁM SE SEBOU (a jeho vlastní brána to nechytí)

| Kde | Co tvrdí | Verdikt |
|---|---|---|
| `AGENTS.md:62–63` | „`AGENTS.md` tvrdil „32 sloupců", **správně je 39**" | **ROZCHOD** — živý zdroj je **40** |
| `AGENTS.md:337` | „5 tabulek, **40 sloupců**, českých 0" | **SOUHLASÍ** se zdrojem |
| `orchestra/conductor/schema.sql` | — | **40** (změřeno nezávisle, níž) |

**Pravda je 40.** Naměřeno `_analyza\audit2a-schema.py`:

```
tasks 10 + runs 12 + workers 7 + roadmap 6 + games 5 = 40
```

**Proč je tam 39 a není to lež:** číslo **39 bylo správné do 2. 10. 2026** —
pak B1 přidal sloupec `naposledy_selhalo` (aby se cooldown neptal na
`updated_at`, což byla vada S12). **Rozdíl je čas, ne nepravda** (A2).
Vada není v tom, že tam 39 je; vada je, že je tam **v přítomném čase a bez
značky času**, zatímco o 275 řádků níž stojí 40.

**A tady je ta horší část:** brána `ag-over-cisla.py` vypíše

```
OK        39 sloupců D1                      = 40
```

— tedy **popisek a hodnota si odporují a brána hlásí OK**. Popisek je
**zastaralý natvrdo zapsaný text** (`ag-over-cisla.py:155`) a kontrola čte
**jen tvrzení na řádku 337**, ne to na řádku 62. Vlastní pravidlo o tom, že
„i trvalá pravidla mají čísla a ta se musí periodicky přeměřit", tedy **jeho
vlastní brána nekontroluje**.

> **Metodická poznámka (můj vlastní omyl, který jsem chytil):** první verze
> `audit2a-schema.py` **neodstraňovala SQL komentáře** — a blok `CREATE TABLE
> roadmap` má uvnitř čtyři komentářové řádky. Vyšlo **44**. A protože obě
> „nezávislé metody" v tom skriptu používaly **tentýž** blokový regex, shodly
> se na stejné chybě a skript napsal „obě metody se shodují, číslo je
> spolehlivé". **Dvě metody nad jedním vadným vstupem nejsou dvě metody.**

### R2 — zadání pro příští session uvádělo nesplnitelnou kontrolu

`NEXT-SESSION-INSTRUKCE.md:37` (stav v 17:2x) přikazoval:

```
python _analyza\kronika-kontrola.py   # musí vyjít exit 0 (81 omylů v 9 blocích, 23 nálezů, 18 sessions)
```

**Skutečný výstup brány** (`kronika-kontrola.py`, spuštěno):

```
omylů celkem (skutečnost): 75
nálezů H v kronice:        23
sessions v kronice:        18
```

Hodnoty 23 a 18 sedí; **„81 omylů v 9 blocích" ne**. Session, která zadání čte,
narazí na rozpor a **nemá jak poznat, jestli je vadné zadání, nebo brána** —
což je přesně ten stav, před kterým varuje `AGENTS.md` („číslo bez postupu se
nedá ověřit ani vyvrátit").

> **✅ Tuhle vadu už souběžná session opravila** (naměřeno 17:35: `NEXT-SESSION-INSTRUKCE.md`
> nyní uvádí „**81 omylů v 9 blocích** (z toho **75** jich vidí brána …)").
> Uvádím ji i tak — je to doklad, že **rozpor vzniká sám**, když se dokument
> píše ve dvou krocích, a že ho nezachytí žádná brána.

### R3 — „21 granul" vs. živých 22 → **STAŽENO, není to vada**

**Původní znění nálezu:** `HANDOFF.md` uvádí „21 granul" v deseti místech,
živý zdroj má 22, „stavová čísla se neaktualizovala".

**Přeměřeno (`audit7-overeni-zadani.py`, 18:0x) — a nález NEplatí:**

| | Naměřeno |
|---|---|
| `21 granul` v `HANDOFF.md` | **11 míst** — **všechna v oddílech §14–§21** |
| `22 granul` v `HANDOFF.md` | **6 výskytů** — v §21 a §22 |
| živý zdroj (`roadmap.json` → `grains`) | **22** |
| míst s „21", která by popisovala DNEŠNÍ stav | **0** |

**Oddíly §14–§21 jsou DATOVANÉ ZÁZNAMY** („Provedeno 2. 10. 2026
(11:3x–12:0x UTC)…"). V té době bylo 21 **správně** — granule `tests.harness`
teprve vznikala. A §21 sám obojí vypráví: nejdřív ověří „21, `harness` 0×",
pak po přidání hlásí 22. **To je správný záznam, ne rozpor.**

**Kde jsem udělal chybu:** nástroj `audit2b-cisla-proti-zdroji.py` srovnává
**každé** číslo s živým zdrojem a **neumí spolehlivě rozeznat tvrzení od
záznamu** — má na to jen heuristiku `[citace?]` podle slov v okolí
(„tvrdil", „dřív", „bylo"…). Datum v **nadpisu oddílu** tou heuristikou
neprojde, ačkoli je to nejsilnější možný znak minulosti. Nástroj to má
v docstringu přiznané; **já jsem to přesto zapsal jako nález** — a to je
přesně vada, kterou audit vytýká jiným: *číslo bez kontroly významu.*

> **Poučení pro fázi 2 (a je to cennější než ten nález):**
> **U každého čísla se ptej, K ČEMU patří** — ne jen „sedí na zdroj?".
> `HANDOFF.md` je append-only záznam; má proto **správně** obsahovat stará
> čísla. Rozpor vzniká teprve tam, kde dokument o sobě tvrdí, že popisuje
> **dnešek** — jako `AGENTS.md:62` (R1, ten platí dál).
>
> **Náprava patří nástroji, ne dokumentu:** `audit2b` má brát v úvahu
> **nadpis oddílu** (datum v `## …`) a taková čísla řadit do `[záznam]`,
> ne mezi rozchody.

### R4 — plán auditu měl v hlavičce číslo mimo o řád

| Tvrzení plánu | Naměřeno |
|---|---|
| „`g3-brany.py` (29 bran, běh **~10 min**)" | **40,75 s** |

**14× méně.** A je to právě to číslo, o které se opírala hypotéza „zdržuje to
metodika".

### R5 — mutační test autority NEPROBĚHNE (a žádná brána si toho nevšimne)

`AGENTS.md:461` tvrdí o svém vlastním měřidle:

> `_analyza\ag-mutace.py` | mutační test `ag-over-cisla.py` — vada 39→32
> **i přeformulované tvrzení**; **mutačně ověřeno 5/5**

**Naměřeno 2. 10. 2026 (17:4x): `ag-mutace.py` → `exit 1`, a to takhle:**

```
1) vracím vadu: `39 sloupců` -> `32 sloupců`   (vzor 0x)
   NEZMUTOVANO — vzor neni jednoznacny
2) přeformuluji tvrzení: `39 sloupců` -> `pětatřicet sloupců`
   NEZMUTOVANO
po vraceni originalu: exit=0
VYSLEDEK: 2 problem: - mutace 1 se neprovedla / - mutace 2 se neprovedla
```

**Příčina (změřeno, ne odhad):** skript na řádku 57 hledá v `AGENTS.md`
**doslovný řetězec `39 sloupců`**. Ten v dokumentu **není** — ověřeno
`Select-String -SimpleMatch` → **0 výskytů**. `AGENTS.md:62` dnes zní
„…**„32 sloupců"**, správně je **39** — a schéma se přitom…", takže
`39` a `sloupců` **nejsou vedle sebe**.

**Tři věci, které z toho plynou (a každá je samostatná vada):**

| # | Co | Proč to je vada |
|---|---|---|
| 1 | **Mutace se neprovede** | `overovani` §7.9: „mutační test, který se neprovede, tvrdí totéž co test, který projde" |
| 2 | **`exit 1` nikdo nevidí** | `ag-mutace.py` **NENÍ v seznamu `BRANY` v `g3-brany.py`** (ověřeno: `grep 'ag-mutace' g3-brany.py` → 0). Rutinní běh bran ho tedy nespustí |
| 3 | **`AGENTS.md` tvrdí „5/5"** | To je **historické číslo bez značky času** — přesně vada, kterou `AGENTS.md` sám popisuje u „32 sloupců" |

> **Pozor na přiřčení (A2 + `overovani` §7.7):** `AGENTS.md` byl souběžnou
> session zapsán v **17:38:18**, tedy **v průběhu tohohle auditu**. Nemám
> snímek předtím, takže **nemůžu říct, který zápis to rozbil** — jen že
> **v 17:4x vzor v dokumentu není a test proto neproběhne**. Kdo to bude
> opravovat, ať to nejdřív ověří sám.

**A ještě jedna věc, kterou `ag-mutace.py` změřil a která patří k R1:**

```
řádků s číslem v AGENTS.md      : 106
z toho číslo s jednotkou (tvrzení): 22
nástroj kontroluje              : 5 v pořádku + 0 historických
-> zbytek čísel v AGENTS.md NENÍ kontrolován
```

**Nástroj, který hlídá autoritu, pokrývá 5 z 22 tvrzení** — a `AGENTS.md` to
sám přiznává („částečný nástroj, nález N9"). R1 (39 vs. 40) je přesně to
tvrzení, které mezi těmi patnácti nekrytými leží.

### R6 — dva další mutační testy se nedají spustit

| Test | `exit` | Co vypsal | Klasifikace |
|---|---|---|---|
| `h17-mutace-a.py` | 1 | `AssertionError: worktree neexistuje` (`_analyza\h17-kladna` → `Test-Path` = **False**) | **NEPROBĚHLO** |
| `mutace-testu.py` | 1 | `CHYBA: 9efbb076…:scripts/save.gd nejde přečíst (rc=128) — MUTACE NEPROBĚHLA` | **NEPROBĚHLO** |

**Ani jeden není „slepá brána" — ani jeden ale není zelená.** Podle
`overovani` §7.13 je to **třetí stav** a tak se musí i zapsat. Kdo je povede
v seznamu jako „červené", tvrdí o nich něco, co se nikdy neměřilo.

### Co fáze 2 NEnašla (a je to výsledek)

`ag-over-cisla.py` → **`exit 0`**, 5 čísel v pořádku, 2 historická označená.
`over-dokumentaci.py` → **63 kontrol, 0 chyb**. `handoff-kontrola-uplnost.py`
→ **83/83**. `kronika-kontrola.py` → **`exit 0`**.

**Zelené brány tedy nic z R1–R3 nechytí** — všechny tři rozpory jsou mimo
jejich záběr. To je nález o **pokrytí**, ne o bránách.

---

## 3. FÁZE 3 — NADBYTEČNOST

**Nástroj:** `_analyza\audit3-duplikace.py` → `_analyza\audit3-vystup.txt`
**Prohledáno:** 61 dokumentů (jádro + `_analyza\*.md` + skilly)

| Pravidlo | Výskytů | Dokumentů | Nejvíc kde |
|---|---|---|---|
| S27 „ruční seznam místo projití složky" | **138** | 20 | `HANDOFF.md` **28×**, `KRONIKA` 20× |
| „brána musí umět spadnout / mutační test" | **130** | 25 | `HANDOFF.md` **22×** |
| „dvě kopie se stejným hashem" | 82 | 12 | `HANDOFF.md` 14× |
| N9 „přeměřit čísla" | 71 | 11 | `HANDOFF.md` 14× |
| „83 klíčových bodů" | 62 | 13 | `HANDOFF.md` **18×** |
| „přegeneruj inventář" | 56 | 16 | `HANDOFF.md` **11×** |
| „datum spotřeby" | 9 | 7 | `AGENTS.md` 3× |

**`HANDOFF.md` je zdrojem č. 1 u KAŽDÉHO opakovaného pravidla.** To není
náhoda: handoff je append-only, takže každá session do něj pravidlo **znovu
napíše** — místo aby odkázala.

> **Návrh autority (k odsouhlasení, shodný s plánem):**
> trvalé pravidlo → `AGENTS.md` · postup předávání → `PREDAVANI-SESSION.md` ·
> stav → `HANDOFF.md` (jen poslední oddíl) · příběh → `KRONIKA-PROJEKTU.md` ·
> zadání → `NEXT-SESSION-INSTRUKCE.md`.
>
> **Duplikát se neškrtá — zkrátí se na odkaz.** Důvod je naměřený: `AGENTS.md`
> tvrdilo „32 sloupců" a přes **šest session** si toho nikdo nevšiml, protože
> se četlo z druhé ruky.

**Co duplikace stojí:** `HANDOFF.md` má 3 616 řádků a je **první u všech sedmi
pravidel**. Kdyby v něm pravidla byla jen jako odkazy, je to podle měření
**nejméně 155 řádků** (součet 11+18+22+28+14+14+11 výskytů) — a to jen
u sedmi sledovaných vzorů.

---

## 4. FÁZE 4 — CO JE NA ŠPATNÉM MÍSTĚ

**Nástroj:** `_analyza\audit4-umisteni.py` → `_analyza\audit4-vystup.txt`
**Kritérium:** *„Najde to session, která to bude potřebovat — bez toho, aby jí
to někdo řekl?"* Měřeno třemi otázkami: cituje to jádro? je to v ručním
seznamu brány? říká to samo, čím je a do kdy platí?

| Skupina | Dokumentů | Bajtů | S hlavičkou |
|---|---|---|---|
| `PLAN-*` | 5 | 182 857 | **jen 1** (`PLAN-DALSI-KROK.md`) |
| `ANALYZA-*` | 8 | 340 209 | **jen 1** (`ANALYZA-HLOUBKOVA-ORCHESTRA-2.md`) |
| `IMPLEMENTACE-*` | 3 | 52 113 | 1 ze 3 |
| `_analyza\*.md` | 39 | 826 911 | 4 z 39 |
| **celkem bez hlavičky** | — | — | **62 z 97 dokumentů** |

### Jednotlivé verdikty

| Dokument | Otázka plánu | Naměřeno | **Verdikt (návrh)** |
|---|---|---|---|
| `MOZNOSTI-AGENTA.md` (12 kB) | stav, nebo pravidlo? | citováno v jádru 3×, v ručním seznamu 2 bran, **bez hlavičky**, mtime 1. 10. | **Pravidlo.** `AGENTS.md` ho označuje za „zdroj pravdy o schopnostech" — patří k pravidlům a **má dostat hlavičku** |
| `OTEVRENA-TEMATA.md` (39 kB) | seznam, nebo dokument? | hlavička **ANO**, druh „seznam" podle hlavičky, citováno 5× | **Je to seznam (ledger) a je to v pořádku.** Nástroj `kontrola-temat.mjs` k němu existuje |
| `PLAN-*` (5 dokumentů, 183 kB) | plány, nebo archiv plánů? | 4 z 5 **nemají hlavičku**; `KRONIKA` §8 říká, že plán se píše do `PLAN-DALSI-KROK.md` | **4 jsou archiv.** Mají dostat hlavičku „nahrazeno žijícím plánem v `PLAN-DALSI-KROK.md`, ponecháno jako podklad" |
| `ANALYZA-*` (8 dokumentů, 340 kB) | mají datum spotřeby? | **7 z 8 NE** — přitom `AGENTS.md` to výslovně vyžaduje | **Vada podle vlastního pravidla projektu.** Doplnit hlavičky |
| `SKILLY-AKTUALIZACE.md` (50 kB) | historie, nebo nástroj? | druh „historie" z názvu, **bez hlavičky**, mtime 1. 10. | **Historie.** Patří k `KRONIKA-PROJEKTU.md` jako odkaz, ne jako 741 řádků v kořeni |
| `_analyza\` | pracovní stůl, nebo skladiště? | **271 skriptů, z toho 20 (7,4 %) v branách**; 39 .md, z toho **27 „pracovní úryvek"** | **Obojí.** Skripty = stůl (nechat). `.md` úryvky = skladiště |

### Tři dokumenty, které „nikdo necituje" — a není to pravda

Plán tvrdil **4 dokumenty zmíněné nikde**. Naměřeno (`audit1b-koren-sonda.py`):

| Dokument | Kde je zmíněn |
|---|---|
| `ANALYZA-VYVOJ-APLIKACI-A-HER.md` | `OTEVRENA-TEMATA.md:126` — **odškrtnutá** položka `- [x]` |
| `RESEARCH-public-repos.md` | `OTEVRENA-TEMATA.md:127` — **odškrtnutá** položka `- [x]` |
| `ZADANI-CREATOR-INDIKATORY.md` | `OTEVRENA-TEMATA.md:157` — zmíněn v poučení |
| `README.md` | jen jako **obecné slovo** („začala by čtením README", `AGENTS.md:324`) nebo jako **jiný soubor** (`orchestra\README.md`, `OTEVRENA-TEMATA.md:261`) |

**Opravený nález:** nejsou to 4 sirotci, ale **3 dokumenty, na které vede
jediná zmínka — a to z odškrtnuté položky v ledgeru**. To je horší než sirotek:
session, která hledá „co platí", se k nim nedostane, protože jsou v seznamu
**hotových** věcí. Skutečný sirotek je **jen `README.md`**.

> **Metodická poznámka:** můj čítač zmínek hlásil u `README.md` „jádro: 5×".
> Všechny výskyty byly **obecné slovo nebo jiný soubor** — krátké a běžné jméno
> dělá falešné nálezy. Proto sonda vypisuje i **kontext**, ne jen počet.

---

## 5. FÁZE 5 — CO ZDRŽUJE (a je to doložené, ne dojem)

**Nástroje:** `audit5-cas-bran.py`, `audit5b-cena-cteni.py`,
`audit5c-rucni-seznamy.py`, `audit5d-radky-metody.py`

### 5.1 Brány jsou LEVNÉ — hypotéza „dokonalá metodika" je vyvrácena

Naměřeno dvakrát, dvěma nezávislými způsoby:

| Brána | Sekundy | Podíl |
|---|---|---|
| kronika úplnost | 9,7 | 22,9 % |
| validate-all (CELEK) | 7,5 | 17,9 % |
| C2: mutace N1 (5 běhů) | 5,3 | 12,5 % |
| C1: důkaz selhání | 4,0 | 9,5 % |
| … zbývajících 25 bran | 15,6 | 37,2 % |
| **SOUČET** | **42,1** | |
| **CELÝ `g3-brany.py`** | **40,75** | (`Measure-Command`) |

**Tři brány vykázaly `otevřela: —`** (nedal se z výstupu vytáhnout počet):
`C1: důkaz selhání`, `C2: mutace N1 (5 běhů)`, `tsc (conductor)`. To **není
nutně vada** — u `tsc` je `—` správně (kompilátor nic nepočítá). U prvních dvou
je to **kandidát na „měřidlo, které nevykáže, co změřilo"**.

### 5.2 Ruční seznam v bráně diakritiky: 105 cest, 96 řádků komentářů

`orchestra\tools\kontrola-diakritiky.py`:

| Naměřeno | |
|---|---|
| cest v ručním seznamu `SOUBORY` | **105** (72 v `_analyza`, 26 v kořeni, 6 v `orchestra`) |
| řádků komentářů **uvnitř** toho seznamu | **96 z 202** |
| co ty komentáře říkají | že se to **zapomnělo** — „po páté", „po sedmé", „po dvanácté" |

**To je nejdražší položka fáze 5.** Seznam se musí doplňovat ručně při každém
novém dokumentu, **96 řádků komentářů dokumentuje, že se to nedaří**, a vedle
toho **existuje hotové řešení**: `g1-diakritika-novych.py` od 2. 10. 2026
**prochází složku** a nic doplňovat nepotřebuje.

### 5.3 `_analyza\`: 271 skriptů, 20 zapojených

| | |
|---|---|
| skriptů (`.py`/`.mjs`) v `_analyza` | **271** |
| z toho v `g3-brany.py` | **20 (7,4 %)** |
| nikde v branách | **251** |

**Není to automaticky smetí** — je to jednorázová sonda, kterou nějaká session
potřebovala. Ale **audit fáze 4 se ptá jinak**: najde ji session, až ji bude
potřebovat? U 251 skriptu bez odkazu z jádra je odpověď **ne**.

### 5.4 A ještě jeden druh zdržení: dokumenty, které se nedají ověřit

`AGENTS.md` vyžaduje u každého dokumentu hlavičku „Co tenhle dokument JE"
a datum spotřeby. Naměřeno: **62 z 97 dokumentů ji nemá** — včetně
**4 z 5 plánů** a **7 z 8 analýz**. Session, která takový dokument otevře,
**nemá jak poznat, jestli popisuje dnešek, nebo je to snapshot**.

### 5.5 Vedlejší nález: „počet řádků" vyšel třikrát jinak

| Metoda | Skillů řádků |
|---|---|
| plán auditu | 3 392 |
| PowerShell `(Get-Content).Count` (17:2x) | 3 678 |
| Python `splitlines()` (17:35) | **3 832** |

**Dvě z těch čísel nejsou „nepravdivá" — jsou z jiného času.** Skilly se
v průběhu auditu změnily (`overovani` 30 080 → 36 324 B). A třetí rozdíl je
metoda: `splitlines()` a počet `\n` se shodují na **3 832**; počet `\r\n` je
**595**, protože soubory mají LF.

### 5.6 Umí každá brána spadnout? — doloženo u 20 z 30

**Nástroj:** `audit6-brany-mutace.py` → `audit6-vysledky.json`

Cíl auditu žádá u **každé** brány doložit, že umí spadnout. Naměřeno:

| | |
|---|---|
| bran v `g3-brany.py` | **29** |
| bran s existujícím mutačním testem | **20 z 30** (30 = 29 + inventář auditu) |
| bran **bez jakéhokoli důkazu** | **10** |
| mutačních testů spuštěno mimo `g3` | 8 |
| z toho **`exit 0` a uklizeno** | **5** |
| z toho **neproběhlo** (R5, R6) | **3** |
| změn v obou repech před/po | **0 / 0** — všech 8 uklidilo |

**Brány bez mutačního testu (10):** `C1: a3-kontrola`, `C1: důkaz selhání`,
`handoff úplnost`, `over-dokumentaci`, `over-skilly`, `f2 over cooldown`,
`deploy B1`, `b5-over-tvrzeni`, `tsc (conductor)`,
`validate-all (CELEK)`.

> **U `tsc` je „žádný mutační test" správně** — kompilátor nemá co mutovat.
> U zbylých devíti platí `overovani`: *„když brána projde, ale ty neumíš říct,
> co změřila, nemáš zelenou — máš jen ticho."*

**Mutační testy, které `g3` spouští** (a v auditu 5 prošly s počty):
`a-mutace-run.py` (3 brány), `b-mutace.py` (2/2 chyceno),
`c2-mutace.py` (5 běhů), `g1-mutace-diakritika.py` (75 náhradních znaků),
`t3-kronika-mutace.py` (6 případů).

**Proč je to nejcennější část fáze 5:** ukazuje se, že **tři z pěti mutačních
testů spouštěných mimo `g3` dnes neproběhnou** — a dva z nich nejsou v `g3`
vůbec. Kdo se ptá „která brána nikdy nezabrala", musí se ptát i **„který test
se vůbec nespustil"** — jinak si `exit 1` přečte jako nález o kódu (§7.13).

---

## 6. FÁZE 6 — NÁVRH OPATŘENÍ

**Nic z toho není provedeno.** U každého bodu je riziko a **jak se ověří**.

| # | Opatření | Druh | Riziko | Jak se ověří |
|---|---|---|---|---|
| **1** | **`AGENTS.md:62` označit časem** („39 bylo správně do B1; dnes 40") | oprava rozporu | **nízké** — text se jen doplní | `audit2a-schema.py` → 0 rozchodů; `ag-over-cisla.py` `exit 0` |
| **2** | **Opravit popisek v `ag-over-cisla.py:155`** („39 sloupců" → číst z dokumentu) | oprava měřidla | **nízké** | `ag-mutace.py` (5/5 mutací) **+ nová mutace na řádek 62** |
| **3** | **`ag-over-cisla.py` rozšířit na řádek 62** (dnes čte jen 337) | pokrytí | nízké | mutace: změň 40 → 39 na řádku 337 **i** 62, brána musí spadnout **dvakrát** |
| **4** | **`HANDOFF.md`: pravidla zkrátit na odkaz** (7 vzorů, ≥155 řádků) | zjednodušení | **střední** | `handoff-kontrola-uplnost.py` **83/83, ne méně** |
| **5** | **`HANDOFF.md`: oddíly §10–§22 přesunout do kroniky** (3 056 řádků, 84,5 %) | **nejvyšší přínos pro čas** | **VYSOKÉ** — hrozí ztráta otevřeného bodu | 83/83 **+** `kronika-kontrola.py` **+** porovnat množinu klíčových bodů před/po (ne počet) |
| **6** | **Ruční seznam v `kontrola-diakritiky.py` nahradit projitím složky** (105 cest, 96 řádků komentářů) | odstranění S27 | nízké — vzor už existuje | `g1-diakritika-novych.py` jako kontrola; spustit **obě** a porovnat množiny |
| **7** | **Doplnit hlavičky** 62 dokumentům (hlavně 7 analýz a 4 plány) | úklid | nízké | `audit1-inventar.py` → `hlavicka: ANO` u všech |
| **8** | **Zavést verzování dokumentace** (97 souborů mimo git) | **ochrana** | střední — nový repo | `git log --oneline` nad kořenem |
| **9** | **Zmrazit snapshot před dalším auditem** | metodika | nízké | dva běhy inventáře s odstupem → shodné otisky |
| **10** | **Zrušit/ztlumit brány, které nic nevykázaly** (3× `otevřela: —`) | optimalizace | **vysoké** | **mutační test PŘED zrušením** — vlož vadu; spadne-li, je živá; když ne, **opravit, ne rušit** |
| **11** | **Opravit vzor v `ag-mutace.py`** (řádek 57 hledá `39 sloupců`, což v `AGENTS.md` není) **a přidat ho do `g3-brany.py`** | **obnova měřidla autority** | nízké | `ag-mutace.py` → `exit 0`; pak **vrať vadu** do `AGENTS.md` a brána musí spadnout |
| **12** | **Doplnit mutační testy 9 branám bez důkazu** (mimo `tsc`) | pokrytí | střední | `audit6-brany-mutace.py` → „brány bez důkazu: 0" |
| **13** | **`h17-mutace-a.py` a `mutace-testu.py` označit jako NEPROBĚHLO** (ne je vést jako červené) | poctivost stavu | nízké | oba musí buď proběhnout, nebo být pojmenované jako nefunkční |

> ### ⚠ Pravidlo pro celou fázi 6
> **Brána, která „nic nedělá", se neRuší podle dojmu.** V projektu je naměřeno
> obojí: brána bez chyby bývá **slepá** (`check-schema.py` prošel nad prázdným
> seznamem), ale i to, že **zelená je správně** (tři brány „neproběhlo
> (prostředí)" → po změně prostředí zelené). Postup je **vždy** vložit vadu
> a podívat se, jestli spadne.

### Pořadí, které z měření vyplývá

| # | Krok | Proč první |
|---|---|---|
| 1 | Opatření **9** (snapshot) | bez něj se čísla pod rukama mění — naměřeno v tomhle auditu |
| 2 | Opatření **1, 2, 3** | rozpor v autoritě je **vada**, ne nepořádek |
| 3 | Opatření **6** | nejlevnější odstranění nejdražší ruční práce (105 cest) |
| 4 | Opatření **7, 8** | úklid a ochrana |
| 5 | Opatření **4**, pak **5** | největší přínos pro čas, ale nejvyšší riziko — až po zelených branách |
| 6 | Opatření **10** | jen po mutačním testu |

---

## 7. CO AUDIT NEZMĚŘIL (přiznaná mez)

1. **Skutečný čas agenta.** Měřil jsem **strojový čas bran** a **velikost
   vstupu**. Kolik z půl hodiny je vlastní uvažování modelu, se z tohohle
   auditu **vyčíst nedá** — chtělo by to data z živé session (`dsh-usage`).
   Co ale říct lze: **41 s strojové práce proti 503 511 znakům vstupu**.
2. **Tokeny.** Přepočet „÷3 znaky" je **heuristika**, ne měření, a je tak
   označený.
3. **Rozpory v `_analyza\`.** Prohledal jsem jádro; 48 dokumentů v `_analyza`
   jsem měřil jen inventářem, ne obsahově.
4. **`audit2-rozpory.py` je slepý nástroj** a nechal jsem ho v repu
   **s varováním v docstringu**: hledá „táž veličina, různé hodnoty" pouhým
   vzorem a vyjde mu 15 „rozporů", z toho téměř všechny falešné (různé brány
   hlásí různé počty kontrol **správně**). **Použitelný je `audit2b-*`.**
5. **Nezměřil jsem, zda 251 nezapojených skriptů někdo potřebuje.** To je
   otázka pro člověka, ne pro skript.

---

## 8. NÁSTROJE, KTERÉ AUDIT VYTVOŘIL

Vše v `_analyza\` (jádro zůstalo **nedotčené**, jak bylo dohodnuto):

| Nástroj | Co dělá | Výstup |
|---|---|---|
| `audit0-snimek.py` | otisk stavu jádra s časem | konzole |
| `audit1-inventar.py` | **generovaný inventář** 98 dokumentů, 12 sloupců | `audit-inventar.json` |
| `audit1-mutace.py` | **mutační test inventáře** — 3 vrácené vady, **3 chyceny** | `exit 1` při slepém místě |
| `audit1b-koren-sonda.py` | kde přesně je dokument zmíněn (kontext, ne počet) | konzole |
| `audit2a-schema.py` | nezávislé přeměření sloupců schématu | `exit 1` při rozchodu |
| `audit2-rozpory.py` | ⚠ **slepý nástroj** — vzorem, ne významem | `audit2-rozpory.json` |
| `audit2b-cisla-proti-zdroji.py` | **číslo proti živému zdroji** (9 veličin) | `audit2b-vystup.txt` |
| `audit3-duplikace.py` | opakovaná pravidla + rozklad `HANDOFF.md` | `audit3-vystup.txt` |
| `audit4-umisteni.py` | co je na špatném místě (3 otázky) | `audit4-vystup.txt` |
| `audit5-cas-bran.py` | **wall time každé z 29 bran** (bez úpravy `g3`) | `audit5-cas.json` |
| `audit5b-cena-cteni.py` | cena povinného čtení | konzole |
| `audit5c-rucni-seznamy.py` | ruční seznamy, skladiště, skilly | konzole |
| `audit5d-radky-metody.py` | proč „počet řádků" vyšel třikrát jinak | konzole |
| `audit-cleanup.py` | převod výstupů z UTF-16LE na UTF-8 (viz níž) | konzole |
| `audit6-brany-mutace.py` | **umí každá brána spadnout?** — 30 bran × mutační test, s kontrolou čistoty repů před/po | `audit6-vysledky.json` |

### Všechny brány po auditu

```
python _analyza\g1-diakritika-novych.py   →  exit 0, 453 textových souborů, VŠE OK
```

### ⚠ Past, kterou jsem sám vyrobil (a stála jedno falešné červené)

Výstupy jsem ukládal přes `python ... > _analyza\audit1-vystup.txt 2>&1`.
**PowerShell přesměruje výstup jako UTF-16LE** — a brána diakritiky takový
soubor buď **nepřečte** (`exit 1`, „NELZE PŘEČÍST"), nebo ho **tiše přeskočí
jako binární**. Naměřeno: první běh `g1` skončil `exit 1` a **jediná vada byl
můj vlastní výstupní soubor**.

Je to táž past, na kterou upozorňuje `dsh-prostredi` §5b (`git show > soubor`
v PowerShellu = UTF-16LE), jen o vrstvu jinde — a poučení je stejné jako
u celého auditu: **nástroj, který tiše přeskočí vstup, hlásí totéž co nástroj,
který nic nenašel.** `audit-cleanup.py` to spravil (7 souborů převedeno,
z toho **2 z dřívější session** — `c3-validate-vystup*.txt` byly v UTF-16LE
už předtím a brána je mlčky přeskakovala).

### Hotovo znamená (podle plánu §7) — stav

- [x] `audit-inventar.json` existuje, je generovaný, **každý** dokument má
      vyplněné všechny sloupce (výstup hlásí: „Žádný sloupec nezůstal prázdný")
- [x] Každý rozpor má **dvojici citací** (soubor + řádek) a verdikt — R1, R2, R3
- [x] Každé tvrzení „přebývá" má **počet výskytů** a **jména dokumentů**
- [x] Každé tvrzení „zdržuje" má **naměřený počet** nebo **výsledek běhu**
- [x] Návrh úprav má u každého bodu **riziko** a **jak se ověří**
- [x] **Mutační test inventáře** — `python _analyza\audit1-mutace.py` →
      **3 mutace, 3 chyceny**:
      | Mutace | Co se vložilo | Výsledek |
      |---|---|---|
      | **A** | nový `.md` v `_analyza` | objevil se jako **sirotek** — CHYCENO |
      | **B** | přejmenování na `*-pred-*` | přesunul se mezi **zálohy** — CHYCENO |
      | **C** | vyjmutí z **ručního seznamu** brány | vypadl mezi **sirotky** — CHYCENO |

      Mutace C je nejdůležitější: testuje **klíčové rozlišení** „ruční seznam vs.
      projití složky". Kdyby inventář počítal za „v bráně" i projití složky
      (což dělala jeho první verze), mutace C by **prošla** a inventář by
      hlásil 0 sirotků nad čímkoli. Každá mutace se navíc ověřuje **assertem,
      že měřená podmínka přestala platit** — ne jen že se soubor změnil
      (`overovani` §7.14), a vše se vrací **kopií**, ne `git checkout` (A7).
- [x] **Ověření, že se dokumenty v průběhu měnily** — naměřeno (mtime
      `HANDOFF.md` 17:33:28, `NEXT-SESSION-INSTRUKCE.md` 17:34:01 a 17:38:17,
      `AGENTS.md` 17:38:18). U R2 je doloženo, **co** se změnilo; u R1 a R5
      je znovu ověřeno, že **se nezměnily**.
- [x] **U každé brány doloženo, že umí spadnout** (§5.6):
      **20 z 30** bran má mutační test · **5** mimo `g3` prošlo s `exit 0` ·
      **3 neproběhly** (R5, R6 — pojmenováno, ne zamlčeno) · **10** bran
      důkaz nemá a je to **vyjmenováno**.
- [x] **Nic se nemazalo ani nepřesouvalo mezi dokumenty** — ověřeno:
      všechny zápisy téhle session jsou v `_analyza\`; v kořeni se za celou
      dobu nezměnil žádný dokument mou rukou (změny `HANDOFF.md`,
      `NEXT-SESSION-INSTRUKCE.md`, `AGENTS.md`, `PLAN-DALSI-KROK.md` pocházejí
      od souběžné session).
