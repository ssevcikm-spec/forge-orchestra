# PLAN-ORCHESTRA-NG — implementační plán nové generace orchestra

> **Co tenhle dokument JE:** **plán** — co dělat, v jakém pořadí, s jakou branou
> mezi kroky a s jakým měřitelným „hotovo znamená". **Není to stav** (ten je
> v `HANDOFF.md`) **a není to zadání pro jednu session** (to je
> v `NEXT-SESSION-INSTRUKCE.md`).
>
> **Co implementuje:** `NAVRH-ORCHESTRA-NG.md` (technický návrh). Kdo plán čte
> bez návrhu, bude mít kroky, ale nebude vědět **proč** — a u prvního problému
> je opustí.
>
> **Datum vzniku:** 5. 10. 2026 (session P15).
> **Datum spotřeby:** **plán se spotřebovává rozhodnutím o variantě**
> (`NAVRH` §14). Do rozhodnutí platí **jen fáze 0 a §2 „co může začít hned"**.
> Po rozhodnutí platí **jen zvolená větev**; zbytek se označí jako
> „nepoužito" — a **nemaže se** (může se hodit, kdyby se varianta změnila).
> **Po každé dokončené fázi sem doplň, co se provedlo a čím to je doložené** —
> jinak se plán za týden čte jako popis dneška.
>
> **Odkud brát současný stav:** `HANDOFF.md` + živé měření. **Tenhle plán
> žádný stav netvrdí** — kapitola §1 uvádí jen to, na čem závisí pořadí,
> a to **s datem a zdrojem**.

---

## 0. Jak plán čte a k čemu se vztahuje

### 0.1 Vztah k existujícím plánům (aby se nic nezdvojilo)

| Existující plán | Co s ním tenhle plán dělá |
|---|---|
| `PLAN-ROZVOJ-ORCHESTRA.md` (F0–F5, A–D, L1–L17, ST1–ST10) | **Nahrazuje ho v části „kontrakt a jádro"** (F3, F4 a ST1–ST10 jsou v NG fázích 1, 2 a 7 **obsažené a rozšířené**). **Nenahrazuje** hotové věci (F0 ✅, fáze A ✅, B1 ✅) ani otevřené **B2–B5, C2–C5, D2–D5** — ty zůstávají **platné a nesplněné** a jsou v §2 zařazené jako „práce na starém systému, která má smysl, dokud běží". |
| `PLAN-ORCHESTRA-AI-AGENTI.md` (N0–N6) | **Přebírá N0.2 a N0.3** (brána na závislosti bran; stav CI cíle v `/health`) — obojí je v NG **fáze 5 a 6**. **N3.1** (zadání granule generovat ze schématu) je v NG **fáze 1** (work order). **N4** (uzel) je v NG **fáze 7** (schopnosti uzlu). Zbytek zůstává platný. |
| `PLAN-VISION-ORCHESTRA.md` | **Nedotčeno.** Vision zůstává **advisory** a NG ho jen **zařazuje do verdiktu** (`not_run` s důvodem, `severity: advisory`). F5 (CLIP) a N3.5 (změřit přesnost vision) zůstávají **otevřené a nejsou součástí NG**. |
| `PLAN-SEPARACE-WORKSPACE.md` | **Uzavřený** (přesun proveden 4. 10. 2026). Zůstávají z něj jen **otevřené body §11.6** (`install-into-repo.ps1`, `test-local.ps1`, `.secrets` ACL, `game-clone`, **`_archiv` není zálohovaný**) — a ty jsou v §2. |
| `NEXT-SESSION-INSTRUKCE.md` (Úkoly A–I, H70–H79) | **Běží souběžně a má přednost** — jsou to opravy **měřidel starého systému**, který během fází 0–6 **pořád běží**. NG plán je **nezastavuje**. |

> **⚠ Tři věci, které by plán rád zdůraznil, protože se pletou:**
> 1. **`F0` znamená ve třech dokumentech tři různé věci** (`PLAN-ROZVOJ` = zdroj
>    pravdy v gitu; `PLAN-ORCHESTRA-AI` má `N0` = zelený `main`; `PLAN-VISION`
>    = vision v CI). **V tomhle plánu se proto ID vždy uvádí s dokumentem** —
>    a fáze NG se jmenují **NG-0 … NG-8**, aby se to nepletlo.
> 2. **Většina práce NG se odehrává mimo orchestra** — je to **kód, testy
>    a dokumentace**, které píše agent v session. **Nespotřebovává kvótu free
>    modelů** (ta se spotřebovává jen během **shadow mode** a při ověřování).
> 3. **NG nic nenasazuje do provozu, dokud neproběhne shadow mode** (NG-3).

### 0.2 Graf závislostí fází (není to lineární seznam)

```
NG-0 Rozhodnutí a měření ──┬──► NG-1 Kontrakty ──┬──► NG-2 Jádro ──┬──► NG-3 Shadow
                           │                     │                 │
                           │                     │                 └──► NG-4 Modely (2)
                           │                     │
                           │                     └──► NG-6 Brány ──┬──► NG-7 Produkt + 2. stack
                           │                                      │
                           └──────────────────────────────────────┴──► NG-5 Stav a spolehlivost (2)
                                                                          │
                                                                          └──► NG-8 Provoz a vyhodnocení
```
**Lze paralelně:** NG-4 a NG-6 (obojí stojí na NG-1/NG-2, ne na sobě).
**Nelze:** NG-3 (shadow) bez NG-2; NG-7 bez NG-6; NG-8 bez NG-3.

---

## 1. Na čem plán závisí (a s jakou jistotou)

| Co | Hodnota | Zdroj | Jak je to jisté |
|---|---|---|---|
| Úspěšnost běhů free modelů | **28 / 247 = 11,3 %** | `hl-priciny.mjs` (247 běhů), 1. 10. 2026 | měřeno jinou session; **nepřeměřeno** |
| Běhů na úspěšnou granuli | **~9** | tamtéž | totéž |
| Selhané běhy do 30 s | **55 %** | tamtéž | totéž |
| Prompt běhu | **~14,4 tis. tokenů** | `HANDOFF` §18.17, log #146 | měřeno 1. 10. |
| Denní strop free řetězce | gemini ~20, openrouter 50, groq ~13–14 běhů | `providers.json` + §18.17 | **jen Groq je změřený**, ostatní jsou odhady v komentářích |
| Silné granule | **9 z 22** | `.forge/roadmap.json` | měřeno 5. 10. |
| Brány projektu | **30 bran, 0 nenulových exitů** | `g3-brany.py` (P14) | měřeno 5. 10. |
| Necommitnutá práce | **8 commitů + ~100 řádků** `git status` | `NEXT-SESSION` §5, podagent | měřeno 5. 10. |
| `_analyza/_archiv/` | **není zálohovaný**, gitignorovaný | §29.7, §30.18, §31.9, §32.12 | tvrzení dokumentů, **neověřeno živě** |
| Conductor je neutrální | **0 zmínek o enginu v kódu** (2 komentáře) | **vlastní čtení** 5. 10. | ověřeno |
| Vazba na stack | `.github/workflows/*` + `.forge/*` | **vlastní čtení** + analýzy | ověřeno |

> **Co z toho plyne pro plán:** čísla, která **nejsou přeměřená**, se v plánu
> **nepoužívají jako kritérium** — NG-0 je proto **měří znovu** a teprve pak
> se podle nich nastavují prahy.

---

## 2. Co může začít HNED (a vyplatí se v každé variantě)

**Tohle je jediná část plánu, která platí bez rozhodnutí o variantě.** Všechno
jsou to věci, které **nezhorší nic, i kdyby se NG nikdy nestavěla**.

| # | Co | Proč to má smysl vždy | Cena | Hotovo znamená |
|---|---|---|---|---|
| **H1** | **Zálohovat `_analyza/_archiv/`** a **ověřit zálohu obnovou** (ne jen že vznikla) | je to **jediná cesta zpět** a **není zálohovaná** (opakuje se v pěti sekcích napříč třemi dny) | hodiny | existují **dvě** kopie na různých místech a **test obnovy** projde (několik souborů zpět + shoda hash) |
| **H2** | **Přehrávací harness** (replay 247 běhů z GitHubu do jednoho JSONL) | je to **vstup pro NG-4** a **nezávislé měření** dnešního stavu; nedělá žádné rozhodnutí | 1–2 dny | soubor `_analyza/replay-runs.jsonl`, ke každému běhu `run_id`, `head_sha`, `conclusion`, `first_failed_step`, `tokens`, `model`, `prompt_size`, `duration_s`; **počet řádků = počet běhů stažených API** (ne odhad) |
| **H3** | **Doplnit `limits` s `source`** do `providers.json` (jen Groqovo změřené TPM; ostatní `value: null, source: "unknown"`) | **řeší důvod, proč NA14 čeká** (nezměřené se nevydává za změřené) a **nic nemění na chování** | hodiny | pole existuje; u Groqu `source: "observed"` + `evidence`; u ostatních `source: "unknown"`; **chování se nemění** (nikdo to zatím nečte) |
| **H4** | **Zrátovat `escovate`**: ověřit, že `ESCALATE_AFTER=8 > MAX_ATTEMPTS=5` platí v **nasazené** verzi | je to **jeden dotaz** a rozhoduje o tom, jestli watchdog někdy vystřelí | minuty | zapsané naměřené číslo + věta, **odkud** je |
| **H5** | **Dořešit Úkoly A–I** z `NEXT-SESSION-INSTRUKCE.md` (H70–H79) | starý systém **běží dál** a jeho měřidla se mají opravit dřív, než se podle nich bude cokoli rozhodovat | dle zadání | zadání samo |
| **H6** | **Zapsat `done_note` do čtenářů** — nikoli mazat, ale **číst**: conductor aspoň zaloguje `done_note` u granulí, které vypadají hotové | je to **jediné čitelné svědectví o S29** a dnes ho nikdo nečte | hodiny | v odpovědi `/tick` nebo `/health` je vidět, kolik granul má `done_note` — a **je to nenulové** (dnes 2) |

> **Pozor na H3:** návrh mění **význam** `providers.json` jen tak, že **přidává
> pole, které nikdo nečte**. Kdyby se do něj mělo zapisovat měření, musí to být
> **měření s důkazem** — ne odhad. To je celý rozdíl proti `NA14`.

---

## 3. Fáze NG-0 — Rozhodnutí a měření

**Cíl:** mít **rozhodnutou variantu** a **přeměřená** čísla, na kterých stojí
prahy. **Nic se nemění v kódu orchestra.**

| | |
|---|---|
| **Vstup** | `NAVRH-ORCHESTRA-NG.md` §14 (varianty) a §2 (co je naměřeno) |
| **Cena** | **1–2 session** |
| **Riziko** | nízké — nic se nemění |

**Kroky**

1. **Přehrát a přeměřit** (H2): stáhnout všechny běhy `agent.yml`, rozdělit
   podle **prvního selhaného kroku**, spočítat: úspěšnost, běhy do 30 s,
   distribuci `attempt` na granuli, prompty a tokeny.
   **Výstup:** `_analyza/ng0-baseline.json` + krátký dokument s čísly
   **a datem**.
2. **Ověřit tři klíčová tvrzení návrhu** (jsou to jeho nosné body):
   - T1 (jádro nezná engine) — hledání nad `index.ts`,
   - T6 (**S38**: timeout obchází strop) — čtení `:813–834` + `:618` + `:751`,
   - T7 (`/report` cooldown neobchází) — čtení `:1464–1472`.
   **Každé tvrzení, které neobstojí, se zapíše do návrhu jako oprava** —
   a je to **výsledek**, ne neúspěch.
3. **Rozhodnout variantu** (§14 návrhu) — **rozhoduje uživatel**, ne agent.
   Zapsat **do kroniky** řádkem a **do návrhu** datem spotřeby.
4. **Zapsat, které otevřené body starého systému se v NG zavírají a které ne**
   (aby se nezdálo, že NG vyřeší i to, co neřeší — LGTM, vision, `kind`,
   druhá hra, `prepisy.json` jako samostatná věc).

**„Hotovo znamená" pro NG-0**

- [ ] `_analyza/ng0-baseline.json` existuje a **počet řádků = počet běhů stažených API** (uvedeno obojí),
- [ ] tři nosná tvrzení **přeměřena vlastním spuštěním** a výsledek zapsán (i když vyvrátí návrh),
- [ ] varianta **rozhodnuta a zapsána** (ne „doporučena"),
- [ ] v návrhu je **datum spotřeby** s tím, co se z něj provedlo,
- [ ] je vypsané, **které otevřené body NG neřeší** — a jsou pojmenované,
- [ ] `git status` a `git diff --stat` ukázány uživateli **před** jakýmkoli commitem.

**Co NG-0 NEDĚLÁ:** nemění kód, nezasahuje do běžící orchestra, nezakládá
žádnou novou strukturu souborů.

**Kdy je NG-0 špatně:** když se v něm **začne psát kód jádra** („když už to
čtu, tak to rovnou opravím") — tím se rozhodnutí i měření znehodnotí.

---

## 4. Fáze NG-1 — Kontrakty (bez běhu)

**Cíl:** existují **čtyři kontrakty** jako **schémata + validátory**, a **nikdo
je ještě nečte v provozu**. Ověřují se **na reálném repu** a na **fixturách**.

| | |
|---|---|
| **Vstup** | `NAVRH` §8.3 (`project.json`), §8.4 (`plan.json`), §8.5 (work order), §8.6 (verdikt) |
| **Cena** | **2–4 session** |
| **Riziko** | nízké — nic se nenasazuje; riziko je jen v **rozsahu** (kontrakty mají být malé) |

**Kroky**

1. **Schémata** (`core/contracts/*.schema.json`) — čtyři, verzovaná
   (`forge.project/2`, `forge.plan/2`, `forge.work/1`, `forge.gate/1`).
2. **Validátory** — `forge-lint-project`, `forge-lint-plan`, `forge-lint-verdict`
   (spustitelné, výstup **VERDIKT**, ne text).
3. **Naplnit kontrakty pro dnešní hru** (`uo-shadows`) — vznikne
   `.forge/project.json` a `.forge/plan.json` **odvozený z `roadmap.json`**
   (převodník, ne ruční přepis; `roadmap.json` zůstává **platný vstup**).
4. **Fixtury a mutace:** ke každému validátoru **známý správný** a **známý
   chybný** případ; a **šest vynucení** z `NAVRH` §8.4 (chybějící `capability`,
   chybějící `size_lines`, `size_lines > 60` bez `strong`, neexistující brána
   v `acceptance`, `provides` bez tvaru dat, kolize `owns`) — **každé musí
   validátor shodit**, a to se **dokáže mutací** (vrať vadu, sleduj pád).

**„Hotovo znamená" pro NG-1**

- [ ] čtyři schémata existují a jsou **verzovaná**,
- [ ] validátory běží **z jakéhokoli adresáře** (cesty odvozené, ne absolutní),
- [ ] `.forge/plan.json` hry je **vygenerovaný z `roadmap.json`** a projde validátorem,
- [ ] **šest vynucení** má mutační důkaz: s vrácenou vadou validátor **skončí nenulově**; bez ní **nulově**,
- [ ] **ruční seznamy zmizely**: `project.json` je **jediné** místo s cestami bran,
- [ ] **kontrakt se čte** — validátor je zapojen tam, kde se plán vydává (i kdyby zatím jen v režimu „hlásit").

**Co NG-1 NEDĚLÁ:** nemění conductora, nemění běžící orchestra, **nezavádí
plugin systém** (schémata + CLI), **nenutí** hru přejít na `plan.json`
(`roadmap.json` je dál platný).

**Kdy je NG-1 špatně:** když kontrakty narostou nad ~300 řádků schémat —
pak se do nich dostalo to, co patří do kódu.

---

## 5. Fáze NG-2 — Jádro bez I/O

**Cíl:** rozhodovací logika je **čistá funkce** a **dá se testovat bez sítě
a bez databáze**. Starý conductor **zůstává v provozu a nemění se**.

| | |
|---|---|
| **Vstup** | `NAVRH` §8.7 (porty), §11.3 (invarianty) |
| **Cena** | **3–5 session** |
| **Riziko** | **střední** — tady se rozhoduje o falzifikátoru **F2**; a je tu pokušení „rovnou to opravit" |

**Kroky**

1. **Vytáhnout rozhodovací funkce z `index.ts`** (řádky v závorce jsou dnešní
   místa, ze kterých se logika bere — **ne opisuje**):
   `planFrontier` (blocked/ready, `:601–622`, `:723–732`),
   `lockKeys` (`:302–310`),
   `cooldownGuard` (`:618–621`, `:925–933`),
   `watchdog` (`:245–284`),
   `classifyFailure` (**nová** — dnes neexistuje),
   `evaluateGates` (**nová** — dnes neexistuje).
2. **Testy čtou SKUTEČNÝ text funkcí ze zdrojáku** — vzor
   `tools/test-zamek-owns.py` (jediný správný vzor v projektu). **Neopsané
   kopie** (`test-cooldown.py`, `test-eskalace.py` dělaly přesně tuhle chybu).
3. **Invarianty I1–I10** z `NAVRH` §11.3 — každý má test; u I6 se použije
   **existující** test (8 kontrol) a rozšíří se.
4. **Statická kontrola „jádro nemá I/O"**: `core/` nesmí obsahovat `fetch`,
   `DB`, `env.` — ověřeno skriptem, ne dohledem.

**„Hotovo znamená" pro NG-2**

- [ ] `core/` obsahuje **0** volání `fetch`/`DB` (doloženo skriptem),
- [ ] **každá** funkce z kroku 1 má test, který **čte její text ze zdrojáku**,
- [ ] invarianty **I1–I10** mají test; u každého je **mutační důkaz** (vrať vadu → test spadne),
- [ ] `core/` je **≤ ~1 500 řádků** (falzifikátor **F2**),
- [ ] starý conductor je **funkčně nezměněný** (`git diff` na něm je prázdný),
- [ ] testy **nesahají na síť ani na D1** a projdou **offline**.

**Co NG-2 NEDĚLÁ:** **nenasazuje nic**, nemění chování orchestra, neopravuje
vady starého systému (ty jsou v §2 H5), nezavádí nové stavy.

**Kdy je NG-2 špatně:** když do `core/` pronikne I/O „protože to tam bylo
jednodušší" — tím padá celý smysl fáze a je to **falzifikátor F2**.

---

## 6. Fáze NG-3 — Shadow mode (jádro počítá, starý systém rozhoduje)

**Cíl:** nové jádro **počítá totéž** a **výsledky se porovnávají** — ale
**dispatch dělá pořád starý conductor**. Tohle je jediná obrana proti tomu,
aby se migrace stala výměnou jednoho tichého selhání za jiné.

| | |
|---|---|
| **Vstup** | NG-2 hotová; běžící orchestra (stav viz `HANDOFF.md`) |
| **Cena** | **2–3 session + N dní běhu** |
| **Riziko** | střední — jen čtení, ale **rozdíly se musí vysvětlit**, ne obejít |

**Kroky**

1. **Hostitel `hosts/worker` čte stav** a volá `core/` — ale **jen zapisuje
   svůj názor** do tabulky/souboru `shadow_decisions`.
2. **Srovnávací report** (denně): které granule by jádro vydalo a které starý
   systém vydal; **každý rozdíl má vysvětlení** nebo je to **vada jádra**.
3. **Běží se tak dlouho, dokud rozdíly nejsou vysvětlené** — minimálně
   **do první úspěšně sloučené granule** za shadow režimu.
4. **Teprve po tom** se rozhodne o přepnutí dispatch (a to je **samostatné
   rozhodnutí uživatele**, protože jde o změnu stavu běžícího systému).

**„Hotovo znamená" pro NG-3**

- [ ] existuje **denní srovnávací report** s **počtem** rozhodnutí na obou stranách,
- [ ] **každý rozdíl** má zapsané vysvětlení, nebo je označen jako vada jádra,
- [ ] **nula neobjasněných rozdílů** za posledních N dní,
- [ ] **starý conductor je nezměněný** a jeho běhy jsou doložené,
- [ ] je zapsáno, **co se stane, když se jádro mýlí** (jak se vypne).

**Co NG-3 NEDĚLÁ:** **nepřepíná provoz**, nemění starý conductor, nezapisuje
do `tasks`/`roadmap`.

**Kdy je NG-3 špatně:** když se „rozdíly" vysvětlují tím, že **starý systém
se mýlí** — to je možné, ale **musí to být doložené**, ne předpokládané.

---

## 7. Fáze NG-4 — Modelová vrstva (učí se z historie, ne z naděje)

**Cíl:** router a kniha způsobilosti **rozhodují měřeně** — nejdřív **offline
nad historií**, teprve pak v shadow režimu.

| | |
|---|---|
| **Vstup** | NG-1 (work order), **H2 (replay)**, `NAVRH` §9 |
| **Cena** | **3–5 session** |
| **Riziko** | střední — hlavní riziko je **předpojatost malého vzorku** (proto dolní mez) |

**Kroky**

1. **Kniha způsobilosti** (`model_attempts`) + **odvozené metriky**
   (`p_success_lower_bound`, `limit_prompt_max_ok`, `limit_prompt_min_fail`,
   `fault_histogram`).
2. **Klasifikátor selhání** — deset tříd z `NAVRH` §9.4, každá **pojmenovatelná
   z logu**; nad reálnými logy se změří, **kolik běhů se dá zařadit**
   (a kolik zůstane „nezařazeno" — to je taky výsledek).
3. **Router** (`NAVRH` §9.3) — hard filtry, skóre, práh, **REFUSE**.
4. **Budgeter promptu** (`NAVRH` §9.5) — úrovně L0–L3.
5. **Přehrání historie** (klíčový krok): router dostane **247 historických
   zadání** a rozhoduje, **aniž by cokoli poslal**. Měří se:
   - kolik běhů by **nevyrobil** (a kolik z nich skutečně umíralo do 30 s),
   - kolik by jich poslal **jinému modelu** (a jak dopadly tenkrát),
   - kolik by **odmítl** a s jakým důvodem.

**„Hotovo znamená" pro NG-4**

- [ ] kniha se plní z **reálných** běhů; každý záznam má `evidence` (odkaz na běh),
- [ ] klasifikátor zařadí **≥ 70 %** selhaných běhů (a je vidět, kolik ne),
- [ ] **falzifikátor F3**: router vyřadí **≥ 50 %** běhů, které umíraly do 30 s;
      když ne, je kniha jen log a **fáze se zastaví**,
- [ ] router umí **REFUSE** a ten je **viditelný** (ne tichý skip),
- [ ] `limits` se plní **jen s důkazem** (`source`, `evidence`, datum),
- [ ] **žádný model nebyl vyřazen ručně** — jen měřením.

**Co NG-4 NEDĚLÁ:** **nenasazuje** router do provozu (to je až po NG-3 a po
rozhodnutí), **nemění `providers.json`** nad rámec `limits`, nezavádí placené
modely, neslibuje zlepšení procentem.

**Kdy je NG-4 špatně:** když se do knihy dostanou **odhady** místo měření —
pak se z ní stane další ruční seznam s lepším jménem.

---

## 8. Fáze NG-5 — Stav a spolehlivost (ať se chyba nemá kam schovat)

| | |
|---|---|
| **Vstup** | NG-2; `NAVRH` §11 |
| **Cena** | **3–4 session** |
| **Riziko** | střední — mění se **jen nové jádro**, ne starý conductor |

**Kroky**

1. **Události a projekce** — uzavřený výčet typů; **každá změna stavu má `cause`**.
2. **Leases s TTL a heartbeatem**; vypršení je událost `lease_expired`.
3. **Retry politika je data** (funkce třídy selhání), ne konstanta času.
4. **Strop a watchdog na GRANULI** — a watchdog **jedná** (tier → rozdělení
   granule → `human_required`).
5. **`/health` cíle** (`NAVRH` §11.4) — včetně **N0.3** (stav CI `main`).
6. **Sabotážní test `/health`**: postav `ci_main` na `failure` a dokaž, že to
   `/health` **ohlásí** — jinak je to jen další zelená nad neznámem.

**„Hotovo znamená" pro NG-5**

- [ ] **falzifikátor F4**: neexistuje cesta, jak změnit stav bez události (doloženo testem nad projekcí),
- [ ] lease má TTL i držitele; **vypršení je událost** (test),
- [ ] strop pokusů je na **granuli** (test — a **S14 i S38 jsou tím zavřené** ve novém jádře),
- [ ] watchdog **prokazatelně jedná**: test, kde po N pokusech změní tier / rozdělí granuli,
- [ ] **`/health` umí zčervenat** — sabotáž doložena oběma směry (červená se projeví, zelená se vrátí),
- [ ] **N0.2** (brána na závislosti bran) je součástí NG-6, ale `/health` už hlásí `gates_coverage`.

**Co NG-5 NEDĚLÁ:** nemění chování starého conductora; nezavádí nové stavy
jen proto, že jsou hezké (**stav bez čtenáře je zakázaný**).

---

## 9. Fáze NG-6 — Brány, které měří (a jejich pokrytí)

| | |
|---|---|
| **Vstup** | NG-1 (verdikt), existující brány v `.forge/` |
| **Cena** | **4–6 session** |
| **Riziko** | vyšší — **migrace bran se dotýká herního repa**; proto po jedné a s dvojím během |

**Kroky**

1. **Protokol verdiktu** (`forge.gate/1`) — obalit **existující** brány tak,
   aby vydávaly verdikt, **aniž by se měnilo, co měří**. Nejprve **paralelně**:
   starý i nový výstup, porovnání.
2. **Pokrytí** — `gates.declared / ran / not_run / unknown` v každém běhu;
   **`project.json` je jediný seznam** (mizí tři ruční seznamy — S1, S5, S27).
3. **Pravidlo `measured.items == 0` ⇒ nikdy `pass`** — a **fixtura**, kde brána
   nemá co měřit; musí vrátit `not_run` s důvodem. *(To je test na S3.)*
4. **Self-testy pro 5 bran, které žádný nemají** (`check-assets`, `check-wiring`,
   `verify-level-render`, `agent.yml`, `install-into-repo.ps1`) — s **třemi**
   fixturami (správná, chybná, prázdná).
5. **N0.2** — brána na **závislosti bran** (každá brána, která importuje
   knihovnu, ji musí mít v kroku, který ji pouští). *Naměřeno: chybějící Pillow
   zastavilo celé CI na 7,5 h.*
6. **`behaviour` brána** (nová, povinná) — místo `has_method` **volá** API
   a měří výsledek. Zavádí se **postupně po granulích**, ne najednou.

**„Hotovo znamená" pro NG-6**

- [ ] každá brána vydává **verdikt**, ne text (doloženo výstupem),
- [ ] **falzifikátor F5**: nedá se přeskočit brána, aniž by to bylo vidět v `ran < declared`,
- [ ] **pět bran bez testu** má offline self-test se **třemi** fixturami,
- [ ] **prázdná fixtura** vrací `not_run` (ne `pass`) — u každé brány,
- [ ] **mutace**: u každé brány vrácení vady způsobí `fail` (ne `pass`, ne ticho),
- [ ] **ruční seznamy jsou pryč** a je doloženo, že se nový soubor **objeví** sám,
- [ ] `behaviour` běží aspoň u **tří** granul a **jedna z nich s vrácenou vadou spadne**.

**Co NG-6 NEDĚLÁ:** nezavádí **nové** brány nad rámec `behaviour`; **nemění
vision** (zůstává advisory); **nepřidává bránu, dokud předchozí umí selhat**.

---

## 10. Fáze NG-7 — Produkt a druhý stack (zkouška neutrality)

| | |
|---|---|
| **Vstup** | NG-1, NG-6; `NAVRH` §10, §12 |
| **Cena** | **4–6 session** |
| **Riziko** | vyšší — **tady se poprvé sáhne na druhou technologii**; a je to **falzifikátor F1** |

**Kroky**

1. **Vynucení plánu** (`acceptance` se **čte**, `capability` předek, `size_lines`
   a `model` povinné, `owns` disjunktní) — v režimu **hlásit**, pak **blokovat**.
2. **`human_inbox`** — pojmenovaný stav s vlastníkem: snímek, hratelnost,
   obsah assetu. **Musí být vidět v `/health`** (aby nebyl smetištěm).
3. **Produktová `acceptance` na milnících** — ne na každém PR.
4. **Druhý adaptér** — **nejmenší možný** jiný stack (např. web/JS nebo Python
   CLI nástroj). **Cílem není druhý produkt, ale zkouška švu.**
5. **Změřit daň z druhého stacku** — **kolik souborů mimo `adapters/<stack>/`
   a `project.json`** se muselo změnit. **To je falzifikátor F1.**

**„Hotovo znamená" pro NG-7**

- [ ] **falzifikátor F1**: druhý stack si vyžádal **≤ 5 souborů** mimo adaptér a `project.json` — **a je to spočítané, ne odhadnuté**,
- [ ] granule bez `capability` **neprojde** plánovací branou (doloženo mutací),
- [ ] `acceptance` **se opravdu čte** — granule s nesplněnou `acceptance` **není** `done`,
- [ ] `human_inbox` je vidět v `/health` a **má vlastníka**,
- [ ] produktová `acceptance` proběhla **aspoň jednou** a je u ní **jméno člověka, který ji potvrdil**.

**Co NG-7 NEDĚLÁ:** **nepřináší druhý produkt** (jen zkoušku), nemění design
hry, nezavádí automatické hodnocení obsahu (to zůstává člověku).

---

## 11. Fáze NG-8 — Provoz a vyhodnocení (30 dní po přepnutí)

| | |
|---|---|
| **Vstup** | NG-3 až NG-7, **rozhodnutí uživatele o přepnutí** |
| **Cena** | průběžně |
| **Riziko** | — jde o **měření**, ne o stavbu |

**Co se měří** (proti baseline z NG-0):

| Metrika | Baseline (NG-0) | Cíl / falzifikátor |
|---|---|---|
| Úspěšnost běhů | 11,3 % | **rozhoduje F6**: aspoň jedna granule sloučená u modelu s dřívější `p=0` |
| Běhy na sloučenou granuli | ~9 | pokles; **bez určení čísla předem** (nemám to z čeho spočítat) |
| Podíl běhů do 30 s | 55 % | **F3** (≥ 50 % jich router nevyrobí) |
| Pokrytí bran (`ran/declared`) | neměřeno | **F5** — vždy vidět |
| `not_run` u `hard` bran | neviditelné | **F8** — vidět **a klesat** |
| `human_inbox` | neexistuje | **F7** — musí mít vlastníka a **nesmí růst bez čtení** |

**„Hotovo znamená" pro NG-8**

- [ ] existuje **měsíční srovnání** s baseline, **se zdrojem u každého čísla**,
- [ ] každý falzifikátor F1–F8 je **změřen** (i když vyjde špatně),
- [ ] je zapsané, **co se vypne**, kdyby se systém zhoršil (rollback),
- [ ] `HANDOFF.md` a `KRONIKA` mají záznam — **a otevřené body jsou vypsané**.

---

## 12. Rozhodovací body pro uživatele (blokují práci)

| # | Rozhodnutí | Blokuje | Návrh agenta (ne rozhodnutí) |
|---|---|---|---|
| **R1** | **Varianta A / B / C** | NG-1 a dál | **B** (§14.2 návrhu) |
| **R2** | **Smí se sáhnout na conductora?** (existující **O3** + **O10**) | NG-3 (přepnutí), §2 H5 | ne pro NG-0 až NG-2; **ano pro NG-3**, ale až po shadow režimu |
| **R3** | **Kdo je vlastník `human_inbox`** a s jakou odezvou | NG-7 | člověk = uživatel; **bez vlastníka se `human_inbox` nemá zavádět** |
| **R4** | **Zůstává `roadmap.json` platný** jako vstup, nebo se přechází na `plan.json`? | NG-1 | **zůstává platný** (dvoukolejnost je levnější než migrace naslepo) |
| **R5** | **Má se do NG-1 až NG-6 zapojit běžící orchestra**, nebo se jede jen lokálně? | tempo | **jen lokálně** — provoz se mění až v NG-3 |
| **R6** | **Push a commit** (dnes 8 + 1 commit nepushnutých) | kdykoli | **nepushovat bez vyžádání** |

---

## 13. Rizika a jejich ošetření

| Riziko | Jak vypadá | Ošetření |
|---|---|---|
| **Migrace rozbije běžící orchestra** | po přepnutí se nevydá ani granule | **shadow mode** (NG-3) + **rollback**: starý conductor zůstává **nezměněný** a vypnutý se dá zapnout |
| **Jádro spolkne I/O** | `core/` potřebuje databázi | **falzifikátor F2** + statická kontrola `fetch`/`DB` v `core/` |
| **Kontrakty nabobtnají** | schémata mají stovky řádků | limit ~300 řádků na schéma; co se nevejde, patří do kódu |
| **Kniha způsobilosti bude předpojatá** | model s 1 úspěchem ze 2 vypadá dobře | **dolní mez Wilsonova intervalu** + prahy, ne podíly |
| **Router nepošle nic** (příliš opatrný) | fronta stojí, všechny modely „nemají p ≥ prah" | **REFUSE je viditelný** a **odložení je platný stav** — ale musí být vidět, že se **odkládá**, ne že se **neděje nic** |
| **`human_inbox` se stane smetištěm** | roste a nikdo ji nečte | **falzifikátor F7** + vlastník (R3) |
| **Druhý adaptér se zvrhne v druhý projekt** | práce na cizím stacku místo na šev | cíl je **měření švu** (≤ 5 souborů), ne funkční produkt |
| **Práce na NG pohltí provoz** | orchestra nevydává granule, protože se staví | NG-0 až NG-2 **nesahají na provoz**; §2 H5 běží souběžně |
| **Ztráta znalosti v komentářích** | při přesunu se zahodí komentáře s naměřenými čísly | **komentáře se přesouvají s kódem**; nikdy „uklidit" při přesunu |
| **`_analyza/_archiv/` zmizí** | není zálohovaný | **H1** — záloha **a ověření obnovou** |

---

## 14. Co tenhle plán NEDĚLÁ

1. **Nezachraňuje tři visící PR** ani nic, co visí dnes — to je jiná práce.
2. **Neopravuje vady starého systému** nad rámec §2 (B2–B5, C2–C5, D2–D5
   zůstávají tam, kde jsou).
3. **Neřeší vision, LGTM, `kind`, Blender, CLIP, druhou hru** — NG je jen
   **zařazuje do verdiktu**, neopravuje.
4. **Nemigruje herní repo** (kromě `.forge/project.json` a `plan.json`
   v NG-1/NG-7).
5. **Neslibuje zlepšení procentem** — místo toho má falzifikátory.
6. **Nepřesouvá `HANDOFF.md` §10–§22** ani jiné „úklidy" (`PLAN-DALSI-KROK`
   §3/1: nejvyšší riziko).
7. **Nepushuje a necommituje** bez vyžádání.
8. **Nerozhoduje o směru** — R1–R6 jsou na uživateli.

---

## 15. Poctivost

1. **Odhad ceny je odhad.** „2–4 session" znamená **počet pracovních bloků
   agenta**, ne kalendářní dny — a **není podložený měřením** (nikdo takhle
   velkou migraci v tomhle projektu ještě nedělal). Je to **nejslabší číslo
   celého plánu** a je tak označené.
2. **Neznám skutečnou cenu `core/`.** „~1 500 řádků" je **odvozené** z toho,
   že `index.ts` má 1 497 řádků a většina rozhodování je v něm — **ne změřené**.
   Proto je to zároveň **falzifikátor F2**, ne slib.
3. **Nezměřil jsem, kolik z 247 běhů je možné přiřadit ke třídě selhání.**
   Proto je v NG-4 kritérium „≥ 70 %" **návrh prahu**, ne měření — a je
   **první věc, která se v NG-4 změří**.
4. **Falzifikátor F3 („≥ 50 % běhů do 30 s") je zvolený, ne odvozený.** Vychází
   z toho, že 55 % selhaných běhů umíralo do 30 s — ale **nevím, kolik z nich
   router dokáže rozpoznat**. Když to bude 20 %, je to **výsledek**, ne selhání
   plánu.
5. **Neznám živý stav orchestra** a **nespustil jsem ani jednu bránu**.
   Všechna čísla jsou převzatá s datem a zdrojem (§1) — a **NG-0 je má přeměřit**.
6. **Plán nepočítá s tím, že by uživatel pracoval jinak, než dosud** (session
   po několika hodinách). Kdyby tempo bylo jiné, **mění se počet session, ne
   pořadí** — pořadí je dané závislostmi (§0.2).

---

## 16. Shrnutí na jednu obrazovku

| Fáze | Cíl | Cena | Brána (měřitelné) |
|---|---|---|---|
| **§2 H1–H6** | co jde udělat hned: záloha `_archiv`, replay, `limits`, ověření eskalace, Úkoly A–I, čtení `done_note` | hodiny–dny | viz §2 |
| **NG-0** | rozhodnout variantu a **přeměřit** baseline | 1–2 session | tři nosná tvrzení přeměřena, varianta zapsána |
| **NG-1** | čtyři kontrakty + validátory s mutacemi | 2–4 session | šest vynucení **shodí** validátor; ruční seznamy pryč |
| **NG-2** | jádro bez I/O, testy čtou zdroják | 3–5 session | **F2**: 0 `fetch`/`DB`, ≤ 1 500 řádků, starý conductor nezměněn |
| **NG-3** | shadow mode | 2–3 session + N dní | 0 neobjasněných rozdílů; starý conductor nezměněn |
| **NG-4** | kniha způsobilosti, router, budgeter | 3–5 session | **F3**: ≥ 50 % běhů do 30 s nevyrobit; ≥ 70 % selhání zařazeno |
| **NG-5** | události, leases, watchdog, `/health` cíle | 3–4 session | **F4**: stav bez události neexistuje; `/health` **umí zčervenat** |
| **NG-6** | verdikt, pokrytí, self-testy bran | 4–6 session | **F5**: skip je vidět; prázdná fixtura nikdy `pass` |
| **NG-7** | vynucení plánu, `human_inbox`, **druhý stack** | 4–6 session | **F1**: druhý stack ≤ 5 souborů mimo adaptér |
| **NG-8** | 30 dní provozu a srovnání | průběžně | **F6–F8** změřené; rollback zapsaný |

> **Jedna věta, kterou je dobré si odnést:** *plán nestaví novou orchestra —
> plán **odděluje to, co už funguje**, od toho, co je vázané, a **dodává tři
> vrstvy, které chybí**: kontrakt, paměť modelů a verdikt brány. A u každé
> z nich je napsané, **jak se pozná, že selhala**.*
