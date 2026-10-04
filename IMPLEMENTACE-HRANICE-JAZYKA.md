# Implementace: hranice jazyka v kódu orchestra a hry

> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

> ## ✅ PROVEDENO 2. 10. 2026 — TENHLE DOKUMENT JE ZÁZNAM, NE PLÁN
>
> **Provedla** session `eb127abd` („Hluboká kontrola a plán úprav"),
> **08:38–08:52 UTC**. **Nepushnuto, necommitnuto.**
>
> | # | Co | Stav |
> |---|---|---|
> | **Z1** | `ohlášeno` → `notified` (`index.ts`, patch `pridej-eskalaci.py`, `test-eskalace.py`) | ✅ |
> | **Z2** | rozhodování podle **hodnoty**, ne podle výslovně vykreslené pomlčky | ✅ |
> | **Z3** | „NEMĚNIT" (falešné poplachy) | ✅ beze změny |
> | **Z4** | `nesedí` → `mismatched` — **obě kopie** | ✅ |
> | **Z5** | `"cíl mrtev"` → `"target dead"` — **kód i zadání granule** | ✅ |
> | **Z6** | `pás` → `strip` | ✅ |
> | **Z7** | `vezmiPrepínac` → `readSwitch` — **obě kopie** | ✅ |
> | **Z8** | krok se hledá podle `env.FORGE_ATTEMPT`; **nově umí selhat** (`return 1`) | ✅ |
>
> **Ověřeno spuštěním:**
> - `hl-rizika-jazyka.py` → **0 očekávaných, 11 přejednaných, 0 vrácených**, `exit 0`
>   (**mutačně ověřeno**: vrácení `ohlášeno` → `exit 1`).
> - **Obě kopie mají shodný hash:** `check-schema.py` = `531AE859…`,
>   `vision.mjs` = `FE639998…` (24039 → 24222 B, resp. 17304 → 17296 B).
> - `kontrola-driftu.mjs` → **1 rozdíl** = **známý** rozdíl tří kroků
>   (šablona vs. hra), **nezávislý na Z4/Z7**.
> - Testy hry: **38 kontrol, 0 selhání**. `tsc --noEmit` → `exit 0`.
>
> ⚠ **Dvě věci, které plán §5 neříkal správně — a našly se až při provádění:**
> 1. **Inventář `_inventar.json` je MEZIPRODUKT, ne měření.** `hl-rizika-jazyka.py`
>    si ho vygeneruje **jen když chybí** — po renamenech tedy hlásil **7 vad,
>    které už byly opravené**. Kdo plán plní doslova, dostane **falešný poplach**
>    a může přejmenovat, co je hotové. → **N1/N2** v
>    `IMPLEMENTACE-NOVE-NALEZY-Z-UKOTVENI.md`.
> 2. **Z4 má 5 výskytů, ne 3** — a jeden z nich (`:403`) je **klíč strojového
>    výstupu** `"nesedi"` (malé s), který **čte `:445` téhož souboru**. Proto se
>    přejmenovala **jen proměnná**, klíč zůstal — jinak by se rozešel výstup.
> 3. **Z8 byl horší, než plán tvrdil:** v **herním** repu nese `FORGE_ATTEMPT`
>    **jiný krok** (`Vyber bezplatného poskytovatele LLM`) než v šabloně
>    (`Spusť agenta`). Kontrola procházela, ale **v každé kopii z jiného
>    důvodu** — viz **N3**. Naměřeno `_analyza\z8-probe.py`.
>
> **Hotovo znamená (§8) — stav:** inventář hlásí **0 identifikátorů
> s diakritikou** ✅ · obě kopie shodné + drift známý ✅ · `test-eskalace.py`
> i `check-schema.py` procházejí ✅ · **pravidlo z `AGENTS.md` v `CONVENTIONS.md`
> šablony — NEHOTOVO** ❌ (nebylo součástí Z1–Z8, zůstává otevřené).
>
> **Co NENÍ hotové a patří do další práce:** `CONVENTIONS.md` šablony.

---

**Vzniklo:** 1. 10. 2026 · **Stav:** PŘIPRAVENO, NEZAHÁJENO · **Nic z toho není
provedeno** — tenhle dokument je podklad pro implementační session, ne záznam
práce.

**Proč existuje:** uživatel se zeptal, jestli čeština v dokumentaci neškodí
technicky. Měření (`_analyza\hl-neanglicky-v-kodu.py`, **161 souborů, 2 002
nálezů, 0 nepokrytých**) ukázalo, že **dokumentace je v pořádku** a riziko je
v **10 místech kódu**, kde čeština stojí na místě identifikátoru, literálu
rozhraní nebo kritéria porovnání. Pravidlo je v `AGENTS.md` § „Jazyk: kde česky
a kde ne".

**Ze 172 „rizikových" nálezů klasifikátoru je 12 skutečných** (10 míst, dvě
jsou ve dvou kopiích): 30 jsou známé falešné poplachy fallbacků a **130 jsou
hlášky a texty promptů**, které klasifikátor nazval „klíč objektu", ale ve
zdroji to nejsou jména. Finální seznam s odůvodněním každého zařazení:
`python _analyza\hl-rizika-jazyka.py`.

---

## 1. Co se mění — a co NE

| Vrstva | Verdikt | Naměřeno |
|---|---|---|
| Dokumentace, komentáře, texty pro uživatele | **NEMĚNIT** | UTF-8 je standard; 2 533 znaků diakritiky z 44 781 (5,7 %) |
| Názvy souborů a cest | **NEMĚNIT** | non-ASCII v názvu: **0** ze 113 |
| Schéma D1 (`conductor/schema.sql`) | **NEMĚNIT** | 32 sloupců, českých **0** |
| Klíče a identifikátory CI | **NEMĚNIT** | `task_id`, `run_key`, `FORGE_*` — ASCII |
| `assets/spec.json` → `styl.zmenšování` | **NEMĚNIT** | je to **lidský popis**, 0 čtenářů v kódu |
| **6 souborů s českým identifikátorem** | **ZMĚNIT** | níž |

**Zásada, která se nesmí porušit:** mění se **jen identifikátory a literály
rozhraní**. Žádné přepisování hlášek, komentářů ani dokumentace — jinak se
rozbijí brány, které české texty **hledají** (viz §4).

---

## 2. Změny v orchestra (jádro)

### Z1 — `conductor/src/index.ts`: `ohlášeno` → `notified`

| Místo | Co |
|---|---|
| `:247` | `let ohlášeno = 0;` |
| `:278` | `ohlášeno++;` |
| `:283` | `return ohlášeno;` |
| `:759` | `` `… watchdog: ${eskalovano} ohlášeno (prah 8)` `` ← **jen text v šabloně** |

**Pozor — tohle je jediné místo, kde se to nesmí pokazit:**
- `:759` je **text pro člověka** (`eskalMsg`), ne identifikátor. Mění se
  **jen výraz `${ohlášeno}`**, ne slovo „ohlášeno" v hlášce.
- Patch `orchestra/tools/pridej-eskalaci.py:50,81,86` obsahuje **doslovnou kopii**
  téhož kódu (patch se aplikuje jako text). **Musí se změnit současně**, jinak
  patch přestane sedět na `index.ts`.
- Test `orchestra/tools/test-eskalace.py:45,54,61,66,112` má **vlastní
  zjednodušenou kopii** logiky — přejmenovat taky, ale je to samostatný soubor
  (nepáruje se s conductorem textem).
- `orchestra/README.md:257` cituje hlášku `watchdog: 0 ohlášeno (prah 8)` —
  **text zůstává**, mění se jen to, co je v něm vložené.
- **Brána:** `tools/over-dokumentaci.py:78` **hledá text** `"watchdog: 0 ohlášeno
  (prah 8)"` → **nesmí se změnit**, jinak brána spadne (a to je správně — je to
  kontrakt proti driftu dokumentace).

### Z2 — `tools/analyza-modelu.mjs:58`: porovnání s pomlčkou

```js
const trida_ok = poz === 'any' || poz === '—' ? '' : (…)
```

**Proč je to vada:** `poz` je sloupec „model" z reportu a `'—'` je **výplň,
kterou si skript sám vykreslil** pro prázdnou hodnotu. Když se výplň změní
(jiná pomlčka, `'?'`, `'-'`), logika se **tiše** rozjede. Není to „čeština",
je to **stav vyjádřený textem místo hodnotou**.

**Návrh:** `poz == null || poz === ''` místo porovnání s výplní; výplň nechť se
řeší až při tisku (`:59`).

### Z3 — `install-into-repo.ps1` a `tools/test-local.ps1`

**NEMĚNIT.** Nálezy v kategorii „KLÍČ (jméno atributu)" jsou **falešné poplachy**
mého fallbacku (chytá `:` v české větě). Ověřeno ručně u 7 + 4 řádků: všechny
jsou hlášky a komentáře.

---

## 3. Změny ve hře a v šabloně — POZOR NA DVĚ KOPIE

### Z4 — `check-schema.py:392`: `nesedí` → `mismatched`

```
orchestra/repo/.forge/check-schema.py:392     ← ŠABLONA
games/uo-shadows/.forge/check-schema.py:392   ← HRA
```

**⚠ TOTO JE NEJRISKANTNĚJŠÍ ZMĚNA.** Soubor existuje ve **dvou kopiích**
a drift test hlídá **shodný hash** (po commitu `3a2e691`/`d0bf4f9` je to
`sha256 81ba260c…`-ekvivalent pro `.gitattributes`, u brány 24 039 B).

Postup, který se nesmí zkrátit:
1. změnit **obě kopie** (jedna úprava, dvakrát aplikovaná),
2. ověřit **bajtovou shodnost** (`Get-FileHash` na obou),
3. `node orchestra\tools\kontrola-driftu.mjs` → **0 rozdílů**,
4. spustit bránu na klidovém stavu: `python .forge\check-schema.py .` → exit 0.

Proměnná je lokální (3 výskyty v jednom souboru) → riziko je **jen v párování
kopií**, ne v logice.

### Z5 — `scripts/assist.gd:15`: `"cíl mrtev"` → `"target dead"`

```gdscript
if rule.trigger == "hp < X" ...        # anglicky
elif rule.trigger == "mana < X" ...    # anglicky
elif rule.trigger == "cíl mrtev" ...   # česky  ← nekonzistentní
```

**Proč:** `add_rule(trigger, action)` je **veřejné rozhraní**; volající (člověk
i model) musí uhodnout jazyk. Dva triggery anglicky, třetí česky.

**Naměřeno — kdo to volá (1. 10. 2026):**
- `add_rule` má **5 výskytů, ale 0 volajících**: definice
  (`scripts/assist.gd:5`), zmínka v `docs/ARCHITEKTURA.md:142`, test existence
  (`tests/run_tests.gd:667-668` — jen `has_method`), a **zadání granule**
  (`.forge/roadmap.json:174`).
- Řetězec `"cíl mrtev"` je **na DVOU místech**: v kódu (`assist.gd:15`) a
  **v zadání granule** (`.forge/roadmap.json:174`).

**⚠ DRUHÉ MÍSTO JE PODSTATNÉ:** kdyby se přejmenoval jen kód, příští běh té
granule by **češtinu vrátil** — prompt v roadmapě je pro model zdroj pravdy.
Je to **tatáž vada jako párování PR podle titulku** (`HANDOFF.md` §3.2):
stav na dvou místech, který se neporovnává. **Mění se OBĚ naráz.**

**Co se rozbije, když se to udělá špatně:** nic — `add_rule` nikdo nevolá, takže
jde jen o konzistenci rozhraní a o zadání granule.

**Patří k fázi C2** (`HANDOFF.md` §4: „`test-eskalace.py` (opsaný `watchdog()`…)"),
protože se sahá na týž soubor jako další práce na `assist.gd`.

### Z6 — `tools/make_iso_tiles.py:261`: `pás` → `strip`

Lokální nástroj hry (`games/uo-shadows/tools/`), 3 výskyty (`:261`, `:263`,
`:264`). Není v šabloně → **jedna kopie**. Nejnižší riziko z celého seznamu.

### Z7 — `.forge/vision.mjs:42,47`: `vezmiPrepínac` → `readSwitch`

*(Nález zúženého kritéria, přidán 1. 10. 2026 — první kolo inventáře ho minul.)*

```
orchestra/repo/.forge/vision.mjs:42,47      ← ŠABLONA
games/uo-shadows/.forge/vision.mjs:42,47    ← HRA
```

**Druhá dvojice, která se musí měnit naráz** (stejná past jako Z4). Definice
funkce i její volání, 2 výskyty v každé kopii. Drift test hlídá shodný hash.

### Z8 — `tools/sjednot-sablonu.py:111`: porovnání s českým názvem kroku

```python
kroky = [s for s in data["jobs"]["agent"]["steps"] if s.get("name") == "Spusť agenta"]
env_ok = bool(kroky) and "FORGE_ATTEMPT" in kroky[0].get("env", {})
```

**Je to latentní past, ne dnešní vada** — ověřeno 1. 10. 2026: název
`- name: Spusť agenta` **v obou** `agent.yml` na `:116`, resp. `:121` **sedí**,
takže skript dnes funguje.

**Ale selhání je tiché:** kdyby se krok přejmenoval, `kroky` bude prázdný list
→ `env_ok` bude `False` → **skript vypíše „FORGE_ATTEMPT v env kroku: False"
a stejně skončí úspěšně** (nenulový kód nevrací). Přesně třída
„brána, která nemá jak selhat" z `AGENTS.md`.

**Doporučení:** hledat krok **jinak než podle českého názvu** — např. podle
`env.FORGE_ATTEMPT` nebo podle `run:` bloku. Přejmenovat název kroku by
znamenalo měnit ho na **třech místech** (dva `agent.yml` + tenhle skript),
což je víc práce a víc příležitostí k chybě než změnit kritérium.

---

## 4. Na co se NESMÍ sáhnout — brány, které české texty HLEDAJÍ

Tohle je hlavní důvod, proč se „poangličtění" nedělá plošně. **Když se změní
text, spadne brána, která ho hledá** — a to je zamýšlené chování:

| Soubor | Co hledá |
|---|---|
| `orchestra\tools\over-dokumentaci.py:78` | `"watchdog: 0 ohlášeno (prah 8)"` v README |
| `orchestra\tools\kontrola-diakritiky.py` | pevný seznam 26 souborů s diakritikou |
| `orchestra\tools\kontrola-echo-substituci.py` | české `echo` v `run:` blocích workflowů |
| `orchestra\tools\lint-roadmapa.py` | texty v roadmapě |
| `orchestra\tools\over-skilly.py` | frontmatter a diakritika skillů |
| `orchestra\tools\test-ci-workflow.mjs` | **názvy kroků** workflowu (česky!) |
| `orchestra\repo\.forge\node\vision.test.mjs` | české popisy scénářů |
| `games\uo-shadows\tests\run_tests.gd` | **hlášky testů** (102 řádků s diakritikou) |

**Pravidlo pro implementaci:** měníš-li text, spusť **všechny** brány z §5 a
očekávej, že některá spadne — pak opravit **ji i očekávání**, ne text vrátit.

---

## 5. Ověření po změnách (spustitelné, v tomto pořadí)

Z `C:\Users\Ssevc\Local-Deepseek`, s `$env:PYTHONIOENCODING='utf-8'`:

| # | Příkaz | Očekáváno |
|---|---|---|
| 1 | `python _analyza\test-neanglicky-skener.py` | **23 kontrol, 0 chyb** (skener měří) |
| 2 | `python _analyza\hl-neanglicky-v-kodu.py` | rizikových nálezů **52 → ~6** |
| 3 | `python orchestra\tools\kontrola-diakritiky.py` | **VŠE OK**, exit 0 |
| 4 | `python orchestra\tools\over-dokumentaci.py` | **63 kontrol, 0 chyb** |
| 5 | `python orchestra\tools\over-skilly.py` | **12 skillů, 0 chyb** |
| 6 | `node orchestra\tools\kontrola-driftu.mjs` | **0 rozdílů** (po Z4 kritické!) |
| 7 | `python orchestra\repo\.forge\check-schema.py games\uo-shadows` | exit 0 |
| 8 | `cd games\uo-shadows; python .forge\check-schema.py .` | „Schéma je v souladu", exit 0 |
| 9 | `python orchestra\tools\test-eskalace.py` | exit 0 (po Z1) |
| 10 | `python orchestra\tools\lint-roadmapa.py games\uo-shadows` | vady 1–4 žádné |
| 11 | `Get-FileHash` na obou `check-schema.py` | **shodné hashe** (po Z4) |
| 12 | `git -C orchestra status` a `git -C games\uo-shadows status` | jen zamýšlené změny |

**Brány, které potřebují širší oprávnění** (pod `workspace-write` padají na
`EPERM`/`PermissionError` — **nejsou rozbité**): `validate-all.mjs` (hlásí
4 problémy místo 1), `vision.test.mjs` (obě kopie), `baseline.py testy`,
`test-check-schema.py`.

---

## 6. Co tenhle plán NEDĚLÁ

- **Nepřekládá dokumentaci** do angličtiny ani naopak. Pravidlo z `AGENTS.md`
  je hotové; obsah dokumentů se nemění.
- **Nepřejmenovává české názvy v D1** — žádné tam nejsou (32 sloupců, 0 českých).
- **Nesahá na `spec.json`** (`styl.zmenšování` je popis, ne klíč logiky).
- **Nesahá na české hlášky a logy** — ty vidí člověk a jsou v pořádku.
- **Nezakládá novou bránu** pro jazyk. Skener `hl-neanglicky-v-kodu.py` je
  **analytický nástroj v `_analyza\`**, ne brána v CI. Kdyby se z něj brána
  dělala, musí nejdřív projít `overovani` (§4: brána bez možnosti selhat není
  brána) — a to je **samostatné rozhodnutí**, ne součást téhle práce.

---

## 7. Rizika a co je zmírňuje

| Riziko | Míra | Zmírnění |
|---|---|---|
| Rozjetí **dvou kopií** `check-schema.py` (Z4) | **vysoká** | ověření hashem + `kontrola-driftu.mjs` **po** změně, ne před |
| Patch `pridej-eskalaci.py` přestane sedět (Z1) | **střední** | měnit `index.ts` i patch **v jednom kroku**, pak spustit `test-eskalace.py` |
| **Zadání granule vrátí češtinu** (Z5) | **střední** | měnit `assist.gd` **i** `.forge/roadmap.json:174` naráz |
| Brána hledající český text spadne (§4) | **střední** | je to **správně**; opravit i očekávání brány a zapsat to |
| Neexistující volající `add_rule` (Z5) | **nízká** | naměřeno: 0 volajících → mění se jen konzistence rozhraní |
| Zbytečný „překlad" komentářů (proti zadání) | **střední** | mění se **jen identifikátory a literály rozhraní** (§1) |

---

## 8. Hotovo znamená

- [ ] Inventář `hl-neanglicky-v-kodu.py` hlásí **0 identifikátorů s diakritikou**
      (dnes 6 souborů) — s výjimkou `analyza-modelu.mjs` (Z2 je o hodnotě, ne o diakritice).
- [ ] **Obě kopie** `check-schema.py` mají **shodný hash** a drift hlásí 0 rozdílů.
- [ ] `test-eskalace.py` a `check-schema.py` (obě kopie) procházejí.
- [ ] Pravidlo z `AGENTS.md` je **citováno v `CONVENTIONS.md` šablony** — aby ho
      dostala každá nová hra (jinak zůstane jen v tomhle workspace).
- [ ] Všechny brány z §5 spuštěné, výsledek zapsaný **s časem**.
