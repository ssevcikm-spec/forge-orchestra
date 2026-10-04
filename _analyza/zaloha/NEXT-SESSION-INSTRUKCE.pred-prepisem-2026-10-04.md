# ZADÁNÍ PRO AKČNÍ SESSION

**Zkontrolováno při:** `d1cde9b` (`Projití složky místo ručních seznamů + ukázky rozbitého kódování slovem`) · **2. 10. 2026, 15:31 UTC**
**Stav obou repů při psaní:** orchestra = `d1cde9b` · uo-shadows = `279f584`
**Pushnuto:** **oba ANO** — `origin/main..HEAD = 0`, pracovní stromy **čisté**
**Nasazení:** `CI` **#103** a `release.yml` **#70** na `279f584` → **oba `completed/success`**; Pages `last-modified` **`html` 14:44:15 GMT / `png` 14:44:16 GMT** (push 14:43:10 UTC) — **ověřeno touto session** (§22.7)
**Co je v `HANDOFF.md`:** **§22** (výsledky ověření práce #17, včetně **§22.3** vyvrácení zadání a **§22.5** nálezů H18–H23) · **§8i** (vlastní omyly **81–86**) · **§8h** (omyly 72–80) · **§20** (Groq **ODLOŽEN**)
**Co je v `KRONIKA-PROJEKTU.md`:** 18 sessions, **81 omylů v 9 blocích** (z toho **75** jich vidí brána a **86** je unikátních v `HANDOFF.md` — tři čísla téhož jména, nález **H18**) · **65 = 80 % v měřidle** · **23 nálezů** (H1–H23) · **20 poučení** (L1–L20) · **19 návrhů** — **NA17/NA18/NA19 ve stavu `NEOVĚŘENO`**
**Co je v `PLAN-DALSI-KROK.md`:** §3.1–§3.6 = **tenhle plán** (pořadí je závazné)

**Co tenhle dokument JE:** zadání pro **akční** session. Není to stav (ten je
v `HANDOFF.md`) ani plán (ten je v `PLAN-DALSI-KROK.md`).

> **Tuhle session psala PLÁNOVACÍ (ověřovací) session, která OVĚŘOVALA** práci #17.
> **Její hlavní výsledek je NEPŘÍJEMNÝ:** zadání, které dostala, tvrdilo
> u léku na M3 něco, co **není pravda** (§22.3) — a **ona sama udělala 6 omylů,
> z toho 5 vypadalo jako nález o cizím kódu** (§8i). **Tvoje práce je opravit
> to, co ověření odhalilo** — a **neopakovat ty pasti**: čti **§8i** a **§22.5**
> **před** tím, než začneš psát měřidlo.

---

## 1. Než začneš (povinné, ne formalita)

1. Přečti `PREDAVANI-SESSION.md` **§6.2** (co má akční session dělat),
   `AGENTS.md`, `HANDOFF.md` **§22 celý** (hlavně **§22.3**, **§22.5**, **§22.6**),
   **§8i** a `PLAN-DALSI-KROK.md` celý.
2. Načti skilly **`dsh-prostredi`** a **`overovani`** `skill` toolem.
   **V `overovani` je od 2. 10. 2026 nová sekce §9** — přesně ty pasti, které
   ověřovací session naměřila (nezávislé měřidlo, dvě okna, tři významy slova
   „celkem", predikát přítomnosti, výjimka klíčovaná jménem, očekávaná
   nepřítomnost, slepá místa oprav). **Přečti ji dřív, než začneš psát kód.**
3. **Ověř, že zadání sedí na skutečnost** (jinak se v tom bodě zastav a zapiš to):
   ```powershell
   $env:PYTHONIOENCODING='utf-8'
   python _analyza\zadani-kontrola.py             # musí vyjít exit 0
   python _analyza\kronika-kontrola.py            # musí vyjít exit 0; vypíše „omylů celkem: 75" — což je počet v 8 blocích, které brána ZNÁ (v dokumentu je 86 unikátních, viz níž)
   python _analyza\handoff-kontrola-uplnost.py    # musí vyjít 83/83
   python _analyza\v4-omyly-nezavisle.py          # exit 1 je SPRÁVNĚ: hlásí nález H18
   & orchestra\tools\git.cmd -C orchestra rev-parse HEAD
   & orchestra\tools\git.cmd -C games\uo-shadows rev-parse HEAD
   & orchestra\tools\git.cmd -C orchestra status --porcelain
   & orchestra\tools\git.cmd -C games\uo-shadows status --porcelain
   python orchestra\tools\lint-roadmapa.py        # 22 granul, 14 problémů, 13 z 22
   ```
4. **Pozor na tři čísla, která mají víc významů** (a to je nález **H18**):
   **75** = co vidí brána kroniky (8 bloků pevným seznamem) · **81** = součet
   řádků tabulek (9 bloků) · **86** = unikátních id v `HANDOFF.md`. **Žádné
   z nich není „to špatné"** — každé odpovídá na jinou otázku.

---

## 2. Co je naměřené (s příkazem a výstupem — ne s odkazem)

Všechno níž naměřila **plánovací session** 2. 10. 2026 mezi **14:5x a 15:1x UTC**.
Úplný výpis: `HANDOFF.md` **§22**. **Žádné číslo není opsané** z §21.

### 2.1 Co obstálo (neověřuj znovu, je to doložené)

| Co | Naměřeno | Kde |
|---|---|---|
| **M3 je CHYCENÁ** (H12 uzavřen) | `t1-m3-brana.py`: zdravý **65/0** → M3 **65/2** → návrat **65/0**; podmínka ověřena **před během i po něm** | §22.3 |
| **Lék má DVĚ nezávislé části** | rovnost 13 **a** čítač `vetev_hodnota >= 1`; každá **sama** M3 chytí (`65/1`) | §22.3 |
| **Základ `pres-level` je 61** (ne 65) | `zdravy` **61/0**, `pres-level` **61/1**; jediný rozdíl `izo_pokusu: 0 → 1` | §22.2 |
| **Projití složky v `g1` je skutečné** | nový soubor **vidí** (419 → **422** → po smazání **421**) | §22.4 |
| **Brána kroniky spadne na živém dokumentu** | kopie s `8h = 99` → `exit 1` a `99 vs. 9`; SHA-256 originálů **před = po** | §22.4 |
| **Tři stavy brány kroniky fungují** | chybějící nadpis → `NEZMĚŘENO`; chybějící řádek v kronice → `ROZCHOD` | §22.4 |
| **Testy hry v klonu** | **65/0**, klon zůstal **čistý** | §22.7 |
| **Nasazení** | `CI` #103 i `release.yml` #70 `completed/success` na `279f584`; Pages po pushi | §22.7 |

### 2.2 ⚠ HLAVNÍ NÁLEZY: tři opravy z #17 mají REZIDUA (H18–H20)

**To je jádro téhle session.** Nejde o nové vady vedle — jde o to, že **oprava
měřidla má taky slepá místa a nikdo je neměří**:

| Nález | Co je špatně | Jak je doložený |
|---|---|---|
| **H19** | `kronika-kontrola.py` testuje **přítomnost** kotvy jako `od in hand` (kdekoliv), ale **výřez** bere `radek.startswith(od)` (začátek řádku). Když je kotva jen **citovaná v próze**, vrátí prázdný výřez a vypíše **„v HANDOFF.md je 0"** — **naměřenou nulu** | `v3-kronika-stavy.py`, případ `C5`; dosažitelné u bloků **8d** a **8g** (obě kotvy jsou v dokumentu **2×**) |
| **H18** | `kronika-kontrola.py` má **pevný seznam 8 kotev** → omyly **24–28** (v `HANDOFF.md` **§13.2**) **nevidí**; hlásí **75**, dokument má **86** unikátních. A `kontrola-diakritiky.py` prochází **skilly**, ale **dokumenty má v ručním seznamu 54 cest** → **11 z 37** kořenových `*.md` neotevře | `v4-omyly-nezavisle.py`, `v7-kryti-dokumentu.py` |
| **H20** | `g1-diakritika-novych.py` povoluje rozbité znaky na řádku s `(ROZBITE\|rozbito)\s*=` a u **3 ručně vyjmenovaných** souborů. Legitimní vzorek pod jménem `VZOREK_SPATNE` **i** `ROZBITE_DVOJICE` ⇒ **`CHYBA`, `exit 1`** — **falešný poplach na správném souboru** | sonda `_analyza\zz-vzorek-jine-jmeno.py` (vytvoř → spusť `g1` → smaž) |
| **H21** | Tři čísla v dokladu §21 se nedají zopakovat: „`mutace A (5 běhů)` → **61**" (ta brána spouští **JEDEN** mód a dává **59/0**), „**2 kontrolní**" (jsou **3**), „**1 205** řádků" (je **1 204** — `split("\n")`) | §22.5 |
| **H22** | Čas v hlavičce zadání: „**19:2x UTC**" vs. skutečnost **14:5x UTC** (posun ~4,4 h) | §22.5 |
| **H23** | **7 odkazů** míří na špatnou sekci kroniky: návrhy jsou v **§6**, odkazy (5× `PREDAVANI-SESSION.md`, 2× kronika) posílají do **§5** = „Poučení". **2 v kronize už opraveny** | §22.5 |

### 2.3 Co se té session povedlo (a je to poučení pro tebe)

**Ověřovací session neudělala ani jednu vadu v DATEch** — všech **6 jejích omylů
bylo v měřidlech** (§8i). **Pět z nich vypadalo jako nález o cizím kódu**:
„ten soubor je vadný", „brána to nehlásí", „brána to nevidí", „dokument má
špatná čísla". **Všechna tři „podezření na cizí vadu" se ukázala jako její
vlastní měření.** Ber to jako **konkrétní varování**: i s nezávislým pohledem
a znalostí všech pravidel se **5 z 6 omylů tváří jako cizí vina**.

---

## 3. Úkoly (pořadí je závazné)

### Úkol 1 — OPRAVIT H19 (priorita nejvyšší)

**Proč první:** je to jediná vada, která **vydává nepravdivé tvrzení o datech**.

1. V `_analyza\kronika-kontrola.py` nahraď test přítomnosti **týmž predikátem**,
   kterým se hledá: `if najdi_radek_nadpisu(hand, od) < 0:` → `NEZMĚŘENO`.
2. **Rozšiř fixturu** `_analyza\t3-kronika-mutace.py` o **dva tvary, které dnes
   nemá** (a proto vadu nechytí):
   * **kotva citovaná v próze** (tvar omylu 76 — kotva 2×, jednou jako nadpis,
     podruhé v textu),
   * **blok omylů zapsaný pod jiným nadpisem** (tvar §13.2).
3. **Ověř mutací:** vrať do **kopie** brány `od in hand` a ukaž, že nový případ
   **spadne**.

**Hotovo znamená:** `t3-kronika-mutace.py` → **`exit 0`**, **≥ 8 případů**;
s vráceným `od in hand` **spadne** na případu „kotva jen v próze"; živá kronika
→ **`exit 0`**; a v zápisu je **kolik případů** test otevřel.

### Úkol 2 — OPRAVIT H20 (výjimka klíčovaná jménem)

**Vyber jednu cestu a zdůvodni ji:**
* **(A) Deklarace v souboru** — soubor, který vzorek obsahuje legitimně, to řekne
  **markerem v komentáři**; brána povolí **jen řádky s markerem**.
* **(B) Pojmenovaná poznámka** — brána soubor **vypíše** jako „obsahuje vzorek —
  nekontrolováno" a **nezapočítá ho mezi vady**.

**Co NEDĚLAT:** nerozšiřovat výjimku na „cokoli, co obsahuje vzorek" — to je
**díra** (brána by oslepla na každém souboru, který vadu obsahuje).

**Hotovo znamená:** sonda `_analyza\zz-vzorek-jine-jmeno.py` **není vada** (a je
**vidět**, že byla otevřená), **a zároveň** skutečná vada (rozbité slovo
v docstringu) **vadou zůstane** — **dva běhy, dva výstupy**. Sondu po měření
**smaž** a ukaž, že počet souborů klesl zpět.

### Úkol 3 — OPRAVIT H18 (dokončit „projití složky")

1. V `_analyza\kronika-kontrola.py` najdi bloky omylů **podle TVARU NADPISU**
   (`^#{2,3}\s+8[b-z]?\.\s+Omyly` **i** `Vlastní omyly`), ne podle pevného
   seznamu — a **vypiš, KTERÉ bloky to byly** (strojově čitelný řádek;
   `overovani` §2.3). Tím se do měření dostane i **§13.2**.
2. **Rozhodni u `orchestra\tools\kontrola-diakritiky.py`**: buď dokumenty
   **projít složkou** (`glob("*.md")`), nebo do kódu napsat **pojmenovanou
   poznámku**, že dokumenty kryje `g1`. **Nic třetího nevymýšlej.**
   ⚠ Tenhle soubor **je v repu** → po editaci **`kontrola-driftu.mjs`**!
3. **Přepočti kroniku §3** a **pojmenuj, co které číslo znamená** (75 / 81 / 86).
   **Historická čísla nemaž.**

**Hotovo znamená:** `kronika-kontrola.py` **vidí i §13.2** (a jeho číslo je
**pojmenované**), `exit 0`; u **každé** brány je v zápisu **kolik bloků/souborů
otevřela**; `handoff-kontrola-uplnost.py` → **83/83**.

### Úkol 4 — OPRAVIT H21 a H22 (čísla a čas)

* **H21:** (a) v `_analyza\g3-brany.py` přejmenuj bránu „mutace A (5 běhů)" na
  to, co **skutečně dělá** (jeden mód), a v `HANDOFF.md` doplň, že otevírá
  **59/0** (ne 61); (b) „2 kontrolní" → **3**; (c) „1 205 řádků" → **1 204**
  (a napiš, že 1 205 dává `split("\n")`).
* **H22:** **historická čísla nepřepisuj** (`AGENTS.md`) — **označ je** jako
  „ve svém čase zapsaná chybně" a doplň **správnou hodnotu s postupem**.
  Do **své** hlavičky piš čas **měřený** (`(Get-Date).ToUniversalTime()`).

**Hotovo znamená:** u každého z těch čísel je v `HANDOFF.md` **řádek
s naměřenou hodnotou a příkazem** — a nikde netvrdí něco, co se nedá zopakovat.

### Úkol 5 — ROZHODNOUT NÁVRHY NA17 / NA18 / NA19

Projdi `KRONIKA-PROJEKTU.md` **§6** a u každého `NEOVĚŘENO` rozhodni
**potvrdit / zamítnout / odložit** a napiš **proč** (`PREDAVANI-SESSION.md`
§2.2). Když potvrdíš, **napiš kam** to patří (`AGENTS.md`, `overovani`, …).
**Tohle je povinná část, ne dobrovolná** — bez ní se návrhy hromadí.

### Úkol 6 — ZÁPIS (povinný, nic nemazat)

- [ ] **`HANDOFF.md`** — nová sekce s výsledky (s příkazy a výstupy) a **vlastní
      omyly do §8j**. **Nic nemazat** (`handoff-kontrola-uplnost.py` → **83/83, ne méně**).
- [ ] **`KRONIKA-PROJEKTU.md`** — **řádek do §1**, nové nálezy do §2,
      **přepočítané počty omylů v §3** → `kronika-kontrola.py` → `exit 0`,
      nová poučení do §5, nové návrhy do §6 se stavem `NEOVĚŘENO`.
      ⚠ **Tabulka v §3 má předepsaný tvar** (`| **<blok>** | <popis> | **<počet>** |`).
- [ ] **`PLAN-DALSI-KROK.md`** a **`NEXT-SESSION-INSTRUKCE.md`** — přepiš pro
      **plánovací** session (hlavička podle §3 `PREDAVANI-SESSION.md`); cílem
      bude **ověřit tvoje opravy** (autor není nezávislý reviewer).
- [ ] **`_analyza\_inventar.json` PŘEGENEROVAT** po **každé** změně kódu
      (`python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json`);
      **počítej s tím víckrát** — vstupem je i každý skill, do kterého píšeš.
- [ ] **Všechny brány** (`python _analyza\g3-brany.py`) a u **každé** řekni,
      **kolik souborů/kontrol otevřela** (past S27) a co je „neproběhlo
      (prostředí)" — **`validate-all` je dnes ten případ**.
- [ ] **Ukliď si worktree**, které jsi založil (`git worktree list`), a ověř
      `git status --porcelain` v obou repech.
- [ ] **STAVOVÝ ŘÁDEK do chatu** (`PREDAVANI-SESSION.md` §2.1).

### Úkol 7 — COMMIT A PUSH (až po zelených branách)

**Změny se týkají `orchestra\tools\` (repo!) i `_analyza\` (mimo repy).**
Postup: **ověřit → ukázat uživateli `git status` a `git diff --stat` → počkat
na rozhodnutí → commitnout → pushnout** a ověřit **tři kroky nasazení**
(`rev-list --count` = 0 · workflow na **tom** commitu · Pages `last-modified`
**po** pushi). **`_analyza\` se necommituje** — je mimo oba repy a to je záměr.

---

## 4. Co NEDĚLAT

- **⏸ SE GROQEM NEDĚLEJ NIC** — uživatel to **2. 10. 2026 ODLOŽIL**
  (`HANDOFF.md` §20). **Nevyřazuj Groq z rotace, nemeň `CONVENTIONS.md` ani
  `agent.yml`** (ani dvojitý prefix `openai/openai/…` z nálezu H4).
- **Nepřepisuj měřidla, aby „prošla".** Vzor projektu je opačný: **opravuje se
  dokument**; brána se opravuje **jen když měřila jinou věc** — a to musí být
  vidět **z mutace**.
- **Nerozšiřuj výjimku v `g1` na „cokoli, co obsahuje vzorek"** — to je díra
  (Úkol 2).
- **Neuklízej `_analyza\a-ukol-scratch`** — používá ho `g3-brany.py`; bez jeho
  `.godot` dávají testy **57/3 místo 61/0** a vypadá to jako regrese.
- **Nespouštěj `h17-mutace-a.py` / `-b.py` / `h17-sonda-vetve.py`** — jejich
  worktree **byl odstraněn**; padnou na `assert WT.is_dir()`. Použij
  **`t1-m3-brana.py`** nebo **`v2-m3-lek.py`** (zakládají si worktree samy).
- **Nemaž zálohy `*-pred-*.md`** — jsou to **snímky PŘED opravou** (doklad,
  ne smetí). Brána `g1` je **vynechává pojmenovaně** a vypíše je.
- **Nepřidávej `*-mutace.py` do sekce L** validátoru — přepisují soubory
  a pojistka je odmítá **správně**.
- **Neměň `combat.gd` zpátky** na `has()`, **neměň `player.gd:40`** a
  **nesjednocuj `TestAtributy`** — rozhodnuto dřív (`PLAN-DALSI-KROK.md` §4).
- **Neopravuj `validate-all`, který hlásí `exit 1`** — je to **třetí stav**
  (`PermissionError` na tempu sandboxu), **neproběhlo (prostředí)**.
- **Nenasazuj nic do conductora** bez schválení uživatele.
- **Necommituj `_analyza\`** do žádného z repů a **necommituj nic, co spadlo
  na bráně**.

---

## 5. Hotovo znamená (měřitelné, pro tuhle session)

- [ ] **H19 opraveno** a **doloženo mutací**: fixtura má **kotvu citovanou
      v próze** i **blok pod jiným nadpisem**; s vráceným `od in hand` test
      **spadne**; `t3-kronika-mutace.py` → `exit 0` s **≥ 8 případy**.
- [ ] **H20 opraveno**: sonda `zz-vzorek-jine-jmeno.py` **není vada**, skutečná
      vada **vadou zůstane** — **dva běhy**.
- [ ] **H18 opraveno**: `kronika-kontrola.py` **vidí §13.2** a **vypíše, které
      bloky změřil**; u `kontrola-diakritiky.py` je **rozhodnuto a zapsáno**;
      kronika §3 má **pojmenovaná** tři čísla.
- [ ] **H21/H22**: čísla mají **naměřenou hodnotu a příkaz**; historie
      **označena**, ne přepsána.
- [ ] **NA17/NA18/NA19 rozhodnuté** (potvrzeno/zamítnuto/odloženo) s důvodem.
- [ ] **`handoff-kontrola-uplnost.py` → 83/83** (ne méně), `kronika-kontrola.py`
      → `exit 0`, `hl-rizika-jazyka.py` → `exit 0` (po **přegenerování** inventáře).
- [ ] **Každá spuštěná brána** má v zápisu, **co otevřela**.
- [ ] **Uživatel viděl** `git status` a `git diff --stat` a **rozhodl** o commitu.
- [ ] **V chatu je prompt** pro uživatele podle `PREDAVANI-SESSION.md` §4.
- [ ] **V chatu je STAVOVÝ ŘÁDEK** podle §2.1 (🟢/🟡/🔴 + kde jsme + další krok).
- [ ] **Napsané, co se ověřit NEDALO** a proč.

---

## 6. Kde jsme v projektu (odvozeno z `PLAN-DALSI-KROK.md` §5)

| Krok | Stav |
|---|---|
| 1. **Opravit H19** (predikát přítomnosti + fixtura) | **nezačato** ← *další krok* |
| 2. Opravit H20 (výjimka klíčovaná jménem) | nezačato |
| 3. Opravit H18 (dokončit projití složky) | nezačato |
| 4. Opravit H21/H22 (čísla a čas) | nezačato |
| 5. Rozhodnout NA17/NA18/NA19 | nezačato |
| 6. Commit + push | až po zelených branách |
| ✅ **Ověření práce #17** (5 měření + posouzení H14–H17) | **HOTOVO** 2. 10. 2026 (§22) |
| ✅ granule `tests.harness` + lék na **M3** (H12) | **HOTOVO** 2. 10. 2026 |
| ⏸ **Groq limit 8k** (dynamická úprava balíčku) | **ODLOŽENO uživatelem** (`HANDOFF.md` §20) |

**Až budou hotové kroky 1–5**, řetěz se přepne do **závěrečné fáze**
(`PREDAVANI-SESSION.md` §2.3): **validační session → cyklus validace/oprav →
uzavírací session** se shrnutím, lessons learned a revizí nástrojů a skillů.
