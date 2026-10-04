# PROMPT PRO NOVÝ CHAT — hloubková analýza orchestra, druhé kolo

> **Co tenhle dokument JE:** zadání. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

> ## ✅ TENHLE PROMPT JE SPLNĚNÝ — NEOPAKOVAT (ověřeno 2. 10. 2026)
>
> **Co to je:** zadání pro **druhé kolo** hloubkové analýzy. Uživatel ho sem
> vložil jako „prompt k poslední hluboké kontrole" a **očekával, že se podle něj
> bude pracovat.** Podle něj se **pracovalo** — session `7cd67c66` („Přečtení
> analýzy hloubkové zadání") ho provedla 2. 10. 2026 a výstup je hotový.
>
> **Ověřeno 2. 10. 2026 spuštěním, ne čtením** (`_analyza\hl2-kontrola.py`,
> brána na „Hotovo znamená" níž):
>
> | Bod „Hotovo znamená" | Naměřeno |
> |---|---|
> | Dokument se všemi 12 oddíly | **12/12** |
> | Tabulka „stav → čím je ukotven" | **je** (16 řádků, §⑪) |
> | Aspoň 5 nových tříd selhání nad S1–S30 | **7** (S31–S37) |
> | Aspoň 3 vlastní měření | **6** (§5.1–5.6 v `HLOUBKOVA-MERENI-3.md`) |
> | Aspoň 1 vyvrácené tvrzení 1. kola | **ano** |
> | Odpovězeno aspoň 6 z 10 otázek | **7** |
> | 2 varianty s cenou/rizikem/co nedělá/podmínkou | **ano** |
> | „Co by vyvrátilo" i „co nezjistila" | **ano** |
> | U čísel zdroj a čas | **ano** (sekce 0) |
>
> **Výsledek: 9/9 bodů, `exit 0`.** A ta brána **umí selhat** — mutační test
> `_analyza\hl2-mutace-kontrola.py` chytí **6/6** mutací.
>
> **Výstupy:** `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` (S31–S37) +
> `_analyza\HLOUBKOVA-MERENI-3.md` (podklady).
>
> ⚠ **Co je na tomhle dokumentu pořád živé:** je to **vzor, jak psát zadání pro
> novou session** (`HANDOFF.md` §8.9). A je to **jediné zadání, které mělo
> výslovný zákaz měnit kód** — ten byl 2. 10. 2026 **zrušen** mandátem
> (`HANDOFF.md` §8.2). **Zákaz „neměnit kód" v textu níž tedy NEPLATÍ.**
>
> **Nemaž ho** (je to záznam o plánu) — ale **neplň ho znovu.**

*(Původní instrukce, která už neplatí: „Zkopíruj celý tenhle soubor jako první
zprávu do nového chatu." — splněno.)*


---

Jsi **nová session**. Orchestra jsi nepsal, neopravoval ani neanalyzoval —
a to je tvoje hlavní výhoda, ne formalita. `AGENTS.md` to vyžaduje: *„Autor není
nezávislý reviewer."*

**Než začneš, přečti v tomto pořadí:**

1. `AGENTS.md` — trvalá pravidla (závazná, ne metodika).
2. `HANDOFF.md` — stav poslední session („pick up here").
3. `ANALYZA-HLOUBKOVA-ORCHESTRA.md` — analýza z 1. 10. 2026 (1 624 řádků).
   **Tohle je tvůj výchozí bod, ne tvůj cíl** — má projít revizí, ne opsáním.
4. `_analyza\HLOUBKOVA-MERENI.md` a `_analyza\HLOUBKOVA-MERENI-2.md` — surová
   naměřená čísla s příkazy. Když se analýza a podklady rozejdou, platí podklady.
5. Skill **`hlouchkova-analyza`** — postup, kterým se máš řídit (fáze 0–5).

   **Načti ho `skill` toolem** (`skill("hlouchkova-analyza")`), ne že si ho
   přečteš očima a uděláš si vlastní postup. Použij z něj:
   **sekci 2 jako pořadí práce**, **sekci 5 jako osnovu výstupu**,
   **sekci 4 jako seznam pastí** (devět z deseti problémů je jedna z nich)
   a **sekci 6 jako příklady** — ale **neopisuj je do obecné části**.

   **Dvě věci, které platí i pro tebe (a jsou zapsané v `HANDOFF.md` §0):**
   - **Skill smí mít konkrétní příklady, šablona hry ne.** Testovací otázka pro
     obecnou část: *„Platí to i pro systém, který ještě neexistuje?"*
   - **Znalost patří k naměřenému příkladu, ne k pravidlu.** Proto v každém
     skillu i v tomhle zadání je u pastí **číslo, soubor a datum**.

---

## Co je úkolem

**Téma druhého kola: „stav, který si systém hlásí sám".**

První kolo naměřilo, že orchestra je **mrtvá 82,7 % času** a že příčina je
v pěti místech kódu (S12, S13, S14, S21, S28). Zároveň ale našlo **dvě vady,
které jsou jiného druhu** a zůstaly nevyřešené:

- **S29** — úkol je v databázi `done`, ale **práce není v `main`** (PR #28 a #29
  leží nesloučené, `save.gd` a `hud.gd` v hlavní větvi nejsou).
- **S30** — granule, na kterou **všichni čekají a nikdo na ni nepočká**:
  `core.attributes` a `entity.item` mají sloučené PR, ale **řádek v D1 někdo
  smazal**; drží to pohromadě jen párování PR **podle titulku**.

**Obě mají stejný tvar:** stav, který systém **sám o sobě tvrdí**, se rozešel
se stavem, který je **skutečně vidět** (v gitu, v PR, ve výstupu brány).
A **nikdo to neporovnává**.

**Tvůj úkol je projít orchestra jako systém a odpovědět na jednu otázku:**

> **Která tvrzení o stavu si orchestra vyrábí sama — a čím by se každé z nich
> dalo ukotvit ve skutečnosti?**

A navrhnout architekturu, ve které **každý stav má svůj protějšek**: buď
v gitu, nebo v PR, nebo ve výstupu brány. Ne „přidat kontrolu" — **odvodit
stav z věci, která existuje nezávisle na systému.**

### Devět optik, kterými to projdi (zadání §4.1, ale s důrazem na tuhle otázku)

Projdi všech devět z `ANALYZA-HLOUBKOVA-ZADANI.md` §4.1 — a u každé se **nově
ptej, odkud systém bere svá tvrzení**. Zvláštní důraz:

- **O2 (zdroje pravdy)** — kolik jich je a **která jsou jen v D1**?
- **O3 (smlouvy)** — která rozhraní jsou deklarovaná a která **odvozená
  z konvence** (a co se stane, když konvence přestane platit)?
- **O5 (tichá selhání)** — jaký je **společný mechanismus** nových vad
  (S29, S30) a liší se od těch starých (S1–S18)?
- **O6 (testovatelnost)** — **co by šlo ověřit offline** z toho, co dnes
  ověřit nejde? (První kolo to ukázalo u SQL: `hl-sql.py` čte dotaz ze zdroje.)

### Otázky, na které dnes nikdo nezná odpověď

1. **Kolik z polí v D1 je odvozených a kolik opsaných?** (`roadmap.status`,
   `tasks.status`, `runs.status`, `workers.jobs_done`, `games.active` — kdo je
   autorita u každého?)
2. **Co se stane, když se D1 smaže a postaví znovu?** (Reset existuje —
   naměřeno, že staví ze souboru. Co by se ztratilo a co by se vydalo znovu?)
3. **Kde všude je stav vyjádřený ve DVOU místech** a nikde se neporovnává?
   (První kolo našlo: úloha vs. PR; granule vs. soubor; `schvalil` vs. člověk.)
4. **Jak by se poznalo, že PR se sloučil, kdyby ho nikdo nesloučil?**
   (Dnes: podle `run.conclusion`, což je stav **běhu**, ne práce.)
5. **Která brána měří něco, co si sama vyrobila?** (Např. cache, kterou
   v CI nikdy nepoužije.)
6. **Kolik granul je dnes v `roadmap.json` hotových jen na papíře?**
   (První kolo: 2 ze 18 měly `done: true` v souboru; 8 dalších bylo hotových
   jen v D1 — **srovnáno**, ale princip zůstal.)
7. **Co dělá člověk ručně a mělo by to být vidět jako „čeká na člověka"?**
   (Dnes: 2 otevřené PR a nikde žádný stav, který by to řekl.)
8. **Kde je v orchestra „autorita" o hotovém díle — soubor, D1, PR, nebo `main`?**
9. **Která z vad S19–S30 je ve skutečnosti tatáž vada v jiné vrstvě?**
   (První kolo naznačilo tři: kód → drift → dokumentace. Doplň nebo vyvrať.)
10. **Co by se muselo stát, aby se S29 a S30 už nikdy neopakovaly?**

**Odpověz aspoň na šest z deseti.**

---

## Metodika (povinná)

- **Značky u každého tvrzení:** `měřeno` (spusť to), `kód` (`soubor:řádek`),
  `odvozeno`, `nevím` (patří do oddílu o mezích, ne do těla).
- **Tři úrovně důkazu:** přečtu (nikdy nestačí) → spustím izolovaně (pro logiku)
  → spustím v provozu (pro chování). **U provozních vlastností přiznej úroveň 1**
  místo abys ji tvrdil.
- **U každého čísla napiš, ODKUD je** (endpoint, skript) a **KDY jsi ho měřil**.
  Kód se v tomhle projektu mění i během session — naměřeno 1. 10. 2026.
- **Nástroje, které už existují a dá se na nich stavět:**
  `_analyza\hl-sql.py` (SQL conductora v SQLite + `hl-mutace.py` — mutační test),
  `hl-vytizeni.mjs` (využití), `hl-priciny.mjs` (rozpad selhání),
  `hl-d1-rada.mjs` (soubor vs. D1), `hl-stahni-podklady.mjs` (síť přes Node —
  TLS z PowerShellu a Python urllib na tuhle stanici nefungují).
- **Síť jen Node `fetch`**; git přes `orchestra\tools\git.cmd`; plošné skeny
  Python walkem (grep tool tiše přeskakuje skryté složky).

## Struktura výstupu

Drž se `ANALYZA-HLOUBKOVA-ZADANI.md` §5 (**12 oddílů**), ale **část I zkrať**
(první kolo ji má hotovou — odkaž na ni) a **část II a III rozšiř**:

- **Část II** musí mít **aspoň dvě varianty** návrhu s cenou, rizikem a tím,
  co každá **NEDĚLÁ** — a **měřitelnou podmínku, kdy selhala**.
- **Část III** musí obsahovat **co analýza nezjistila** a **co by ji vyvrátilo**.
- Navíc: **tabulka „tvrzení systému o sobě → čím je ukotveno"** pro každý stav
  v D1 (to je jádro druhého kola).

**Výstup:** `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` + podklady
`_analyza\HLOUBKOVA-MERENI-3.md`.

## Co NEDĚLAT

- **Neměnit kód orchestra ani her.** Analytik zapisuje jen dokumenty a skripty
  v `_analyza\`. (Když ti přijde, že něco opravit musíš, **napiš to** — patří to
  do zadání pro implementační session.)
- **Nepushovat a necommitovat.** Před jakýmkoli commitem ukázat `git status`
  a `git diff --stat` a počkat na vyžádání.
- **Nezakládat druhou hru** ani nemazat `forge-quest` (živá hra).
- **Nevypisovat PAT** ze `orchestra\.secrets\`.
- **Neopakovat, co první kolo změřilo** — ověř to, a kde to nesedí, **napiš to**.
  (První kolo mělo pět vlastních omylů; čekej, že i tvoje čísla někde nesedí.)

## Hotovo znamená (měřitelné)

- [ ] Existuje dokument se **všemi 12 oddíly** z §5.
- [ ] **Tabulka „stav → čím je ukotven"** pro **všechny** stavy v D1.
- [ ] **Aspoň 5 nových tříd selhání** nad rámec S1–S30.
- [ ] **Aspoň 3 vlastní měření**, která nejsou v předchozích dokumentech
      (u každého příkaz, výsledek, čas).
- [ ] **Aspoň 1 tvrzení z analýzy z 1. 10. 2026 je vyvráceno nebo zpřesněno**
      — a je vidět, čím.
- [ ] Odpovězeno na **aspoň 6 z 10 otázek** výše.
- [ ] Návrh má **aspoň 2 varianty** s cenou, rizikem, „co nedělá" a podmínkou selhání.
- [ ] Napsané, **co by analýzu vyvrátilo** a **co nezjistila**.
- [ ] **Nula změn v obou repech** (`git status`) — a když se repa pohnou,
      je to vidět v dokumentu (čas u každého tvrzení o stavu).

**Když některý bod nesplníš, napiš to a vysvětli proč.** Přiznaná mez je
užitečnější než uhlazený závěr.

---

## Co si z toho odnést i po téhle session (dvě pravidla o znalostech)

1. **Obecnost šablony a konkrétnost skillu nejsou tatáž pravidla.**
   Šablona hry nesmí tvrdit nic o projektu, který ještě nevznikl. **Skill je pro
   člověka, ne pro cizí projekt — a konkrétní příklady mít MÁ.** Jen oddělené
   od obecného postupu (v `hlouchkova-analyza` je to sekce 6).
   Naměřeno 1. 10. 2026: šablona nesla 12 zmínek o `uo-shadows` a každá nová hra
   je dědila; **skill bez příkladů je naopak nepoužitelný.**
2. **Znalost patří k naměřenému příkladu, ne k pravidlu.**
   „Ověřuj" nikoho nic nenaučí. **Past s číslem, souborem a datem ano.**
   Když v analýze narazíš na past, která v žádném skillu není, **doplň ji tam**
   — a k ní ten naměřený příklad.
