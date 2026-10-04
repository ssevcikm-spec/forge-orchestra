# ZADÁNÍ — Hloubková analýza a návrh architektury orchestra

> **Co tenhle dokument JE:** zadání. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

**Pro:** novou session (čistý kontext) · **Datum zadání:** 1. 10. 2026
**Autor zadání:** session, která orchestra **neimplementovala** — ověřovala cizí
tvrzení, opravila dokumentaci a připravila implementační plán
**Vzor, ze kterého tenhle dokument vychází:** `ARCHITEKTURA-ANALYZA-ZADANI.md`
(osvědčil se — analýza z něj vznikla a našla 16 tříd selhání)

---

## 0. Proč to zadání existuje (a co se od tebe chce)

Uživatel to řekl takhle: *„ať to není jen moje ‚vše si ověř'."*

Má pravdu a je to přesná námitka. **„Ověř si všechno" je prázdný pokyn** — nedá
se podle něj postupovat, nedá se splnit ani nesplnit a každý si pod ním
představí něco jiného. **Tenhle dokument je pokus přeložit ten pokyn do
postupu**, který se dá vykonat, zastavit a zkontrolovat.

**Chce se po tobě jedna věc, ale pořádně:** aby o orchestra existoval
**dokument, podle kterého se dá rozhodovat o její architektuře** — ne seznam
nálezů, ne přepis toho, co už je napsané, ale **vysvětlení, jak orchestra
funguje jako systém, kde selhává a co s tím udělat.**

**Tři věty, které jsou jádrem zadání:**

1. **Projdi orchestra jako celek** — nejen to, co je rozbité. Vlastnosti,
   náležitosti, vazby, toky, smlouvy a hranice.
2. **Ověřuj vlastním měřením**, ne čtením cizích závěrů — a u každého tvrzení
   napiš, čím je doložené.
3. **Navrhni architekturu**, ne jen seznam oprav: kde jsou švy, co je jádro, co
   je kopie, co je kontrakt a co náhoda.

---

## 1. Kdo jsi a co je tvoje výhoda

**Jsi nová session. Orchestra jsi nepsal, neopravoval a neanalyzoval.**
To je tvoje nejsilnější vlastnost, ne formalita — `AGENTS.md` ji vyžaduje:

> *„Analýza, audit nebo rozhodnutí o něčem, co jsem sám psal → nová session.
> Autor není nezávislý reviewer."*

**Co z toho plyne konkrétně:**

- **Nevěř ničemu, co je napsané v dokumentaci** — včetně dokumentů, které
  vypadají jako měření. Některé z nich **lhaly** (viz §2.2) a jedna analýza byla
  označena za detailní, i když popisovala stav, který už neplatil.
- **Ale taky nedělej opak:** nezačínej tím, že všechno prohlásíš za nedůvěryhodné
  a začneš od nuly. Ušetři to, co je doložené, a **přesměruj sílu na to, co
  doložené není**.
- **Tvoje mez je stejná jako u každého:** co jsi neviděl běžet, nevíš.
  Napiš to (§8.5).

---

## 2. Co je orchestra — a v jakém stavu ji přebíráš

### 2.1 Co to je (kontext, ne úkol)

Samostatný projekt, který **vyvíjí hry pomocí bezplatných LLM**:

- **conductor** = Cloudflare Worker + D1 + cron každou minutu — rozhoduje, co se
  udělá. Sám nevolá žádné LLM.
- **agenti** = GitHub Actions v **repozitáři hry** — tam běží modely, tam vzniká PR.
- **šablona** `orchestra/repo/` = to, co dostane každá nová hra (`.forge/`, `.github/`).
- **hry** = samostatné repy (`games/uo-shadows` je živá, `forge-quest` je jiná
  **živá** hra s vlastními Pages — **nemaž ji**).

**Klíčová vlastnost, která z toho dělá architektonický problém:** orchestra je
**jeden systém, který se přepíná mezi projekty** — a zároveň **kopíruje soubory
do cizích repozitářů**. Každá kopie se může rozejít. To je zdroj většiny
nálezů, které v projektu jsou, a je to i hlavní otázka pro tvůj návrh.

### 2.2 Co se v projektu opravdu stalo (a proč má být analýza obezřetná)

Aby ses nepoučoval z nepravd, tady je **co je doloženo měřením** (tato tvrzení
byla ověřena 1. 10. 2026):

| Co | Stav |
|---|---|
| **Fáze F0** (šablona v gitu, prázdná roadmapa, obecný profil, nástroje v gitu, smazané záplaty, `.env` v `.gitignore`) | **hotová a pushnutá** — neřeš ji znovu, ověř ji |
| **Zámek `owns`** v dispatch smyčce | opraven (`6d2a856`), nasazen, má regresní test |
| **Tři vady conductoru** (3h zpoždění nové granule, obcházení cooldownu přes `/report`, strop na úkol místo na granuli) | **naměřené, NEOPRAVENÉ** |
| **`validate-all.mjs`** | vrací **vždy `exit 0`**, i když vypíše „✗ NALEZENO" — a volá **starou slepou kopii** brány |
| **`NAZEV-REPA`** v `release.yml` | **doslovný placeholder, který nikdo nenahrazuje** — nová hra dostane nefunkční odkaz |
| Dokumentace, která lhala | `HANDOFF.md` tvrdil „77 řádků `git status`" (bylo **0**), „běhy #355–#362" (byly **#235–#241**), „PR se sloučily samy" (`merged_by` = **člověk**) |

**Co z toho plyne pro tebe:** i dokumenty, které vypadají jako pečlivé měření,
**mohly zestárnout nebo být opsané**. Ověřuj. Ale **ověřování není cíl** —
cílem je architektura.

### 2.3 Co je zakázané (aby analýza neuškodila)

- **Neměnit kód orchestra ani her.** Jsi analytik. Jediné, co smíš zapsat, jsou
  tvé dokumenty — a i to jen když to uživatel schválí.
- **Nepushovat, necommitovat nic, co jsi nezměnil, a nic z toho, co jsi změnil,
  bez vyžádání.** (`AGENTS.md`: před commitem ukázat `git status` a `git diff --stat`.)
- **Nemazat `forge-quest`** ani jeho Pages — je to **živá hra**.
- **Nevypisovat PAT** ze `orchestra\.secrets\` a nepsat ho do historie příkazů.
- **Nespoléhat na to, že orchestra „něco nedělá" znamená, že je rozbitá** —
  dnes je zelená (CI hry `success`, conductor `ok: true`).

---

## 3. Jak analýzu PROVÉST (metodika — tohle je ta hlavní část)

### 3.1 Pravidlo značek: každé tvrzení má svůj zdroj

Tohle je **povinné**. Bez toho se analýza nedá číst ani opravit. Značky
přebíráme z `ANALYZA-ARCHITEKTURY-ORCHESTRA.md` (osvědčily se):

| Značka | Znamená | Příklad |
|---|---|---|
| **měřeno** | Spustil jsi to a vidíš výsledek. **Uveď příkaz.** | „`git ls-files tools` → **70**" |
| **kód** | Přečtený řádek zdrojáku — `soubor:řádek`, ověřitelný očima | „guard se ptá na čas (`index.ts:796-804`)" |
| **odvozeno** | Logický důsledek měření a kódu. **Není to přímý výstup nástroje.** | „dvě hry se navzájem vyhladoví" |
| **nevím** | Nedohlédl jsi. **Patří to do §8.5, ne do těla.** | „nikdy jsem neviděl orchestra dispatchovat" |

**Zakázané:** tvrzení bez značky. Věta „systém je křehký" není analýza, je to
dojem — a dojmy se v tomhle projektu už jednou draze vymstily.

### 3.2 Ověřování: tři úrovně důkazu (a jak poznat, že jsi skončil na první)

| Úroveň | Co to je | Kdy to stačí |
|---|---|---|
| **1. Přečtu** | Přečtu kód nebo dokument a opíšu závěr | **Nikdy** nestačí jako důkaz o chování |
| **2. Spustím izolovaně** | Replikuju logiku offline (SQL v SQLite, brána na fixtuře) | Pro **logiku** ano — je to nejsilnější dostupný důkaz bez provozu |
| **3. Spustím v provozu** | Zavolám živý endpoint, dispatchnu úlohu, podívám se na běh | Pro **chování systému** jediné pravé |

**Pro tuhle analýzu:** u všeho, co jde, se snaž dostat na **úroveň 2**.
U provozních vlastností (co conductor skutečně dělá, když běží) **přiznej
úroveň 1** místo abys to tvrdil.

#### Konkrétní postupy, které v projektu existují

- **Živý stav conductora:** `GET /health` (veřejný), `/games`, `/roadmap`,
  `/status`, `/failed`, `/queue` — secret je v `orchestra\.env`.
  **Node `fetch`, ne PowerShell** (TLS ze schváleného PowerShellu nefunguje).
- **Stav repů a CI:** `node orchestra\tools\zjisti-pages.mjs` (GitHub API),
  `_analyza\stav-ci.mjs`, `_analyza\stav-agent.mjs`, `_analyza\stav-release.mjs`.
  **Zdroj pravdy o stavu je API, ne dokument** — „běh #355" a `run_number`
  **#241** jsou různé čítače téhož.
- **Logika conductoru offline:** replika jeho SQL v SQLite — hotový skript je
  v `ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md` §1.2.
  Tím se dá ověřit guard cooldownu **bez sítě**.
- **Ověření, že brána měří:** sabotér `~\.dsh\skills\overovani\sabotuj.mjs`
  (+ `zmen.py` na výrobu vady). Projde na zdravém kódu → vloží vadu → **musí**
  spadnout.
- **Sken celého stromu (i skrytých složek):** Python walk, vzor
  `_analyza\sken-vazeb.py`. **`grep` tool nad rodičovskou složkou tiše přeskočí
  `.forge` a `.github`** — naměřeno 0 nálezů tam, kde jich bylo 80.
- **Testy, které pod sandboxem padají na `EPERM`/`PermissionError`**, nejsou
  rozbité — potřebují širší oprávnění. **Napiš, s jakým oprávněním jsi co měřil.**

### 3.3 Kontrola proti sobě: čtyři otázky po každé kapitole

Než kapitolu uzavřeš, projdi ji téma otázkami. **Když na některou neumíš
odpovědět, kapitola není hotová:**

1. **Čím to je doložené?** (značka + příkaz nebo `soubor:řádek`)
2. **Co by to vyvrátilo?** Kdyby to bylo opačně, jak bych to poznal?
   (Když neumíš odpovědět, je tvrzení nefalzifikovatelné — a tedy bezcenné.)
3. **Jaký je známý SPRÁVNÝ případ?** U každé kontroly musíš umět říct, jak
   vypadá, když je vše v pořádku — jinak nepoznáš vadu od klidu.
4. **Není to jen opsané z jiného dokumentu?** Když ano, **řekni to** a uveď
   zdroj; neopisuj to jako vlastní nález.

### 3.4 Pět pastí, na které v tomhle projektu lidé už narazili

**Každá z nich je naměřená. Všechny vypadají jako nález, ale jsou to chyby
metody:**

| # | Past | Jak vypadá | Jak se jí vyhnout |
|---|---|---|---|
| **P1** | **Statická metrika, která nic nespustí** | Spočítáš volání `test(` v souboru (**42**), vyjde ti, že dokument lže o počtu testů (**36/36**). Po spuštění: 36/36 — dokument měl pravdu | **Čísla o testech a chování čti z výstupu běhu.** Statický počet je stejně slabý jako čtení komentářů |
| **P2** | **Kontrola, která najde vadu v komentáři** | Hledáš řetězec v celém souboru a najdeš ho **v komentáři, který vadu popisuje** → test projde i s vrácenou vadou | **Před hledáním vzorců odstraň komentáře.** A pozor na opak: `forge-quest` v `release.yml` je **text o opravě**, ne vada |
| **P3** | **Nula a „nezměřeno" jako úspěch** | Brána projde nad **prázdným seznamem** (hledala vzorec, který v kódu není) a hlásí zelenou. `[]` vypadá jako naměřená nula | **Ptej se „proběhla kontrola?", ne jen „neprotestovala?"** Prázdno musí být pojmenované („nezměřeno"), ne tiché |
| **P4** | **Dokument, který popisuje minulý stav** | Analýza z dopoledne tvrdí „šablona má 8 změněných souborů" — odpoledne je commitnutá a má 0. Obě čísla byla správně, v různých časech | **U každého čísla si napiš DATUM měření.** A rozliš „stav, který byl" od „stav, který je" |
| **P5** | **Různé čítače nesou stejné jméno** | „běh #355" v dokumentu vs. `run_number` #241 v API; „20 běhů" vs. `total_count` 241. A „PR se sloučily samy" vyvrátí `merged_by` | **U čísel piš, odkud jsou** (endpoint, čítač). A **přiřazení je taky tvrzení** („samo" = ověřit) |

### 3.5 Jak poznat, že analýza NENÍ hotová

Sám sebe kontroluj proti tomuhle seznamu. **Když platí aspoň jedno, nekonči:**

- **Nemáš ani jedno tvrzení, které jsi musel změnit**, protože měření dopadlo
  jinak, než jsi čekal. (Analýza, která potvrdí všechno, co si myslela, obvykle
  nic nezměřila.)
- **Nemáš oddíl „co jsem nezjistil"** — nebo je v něm jen „neměl jsem čas".
- **Nenašel jsi nic, co není v existujících dokumentech.** Pak jsi jen
  přeformuloval cizí práci. **Napiš to** — je to legitimní výsledek, ale musí
  být přiznaný, ne schovaný.
- **Všechna tvoje doporučení jsou „přidat kontrolu"**. Architektura není jen
  přidávání bran.
- **Nedokážeš říct, co by tvoje doporučení ROZBILO.**

---

## 4. Jak rozepsat ARCHITEKTURU (co je výstupem)

Tohle je druhá polovina zadání. **Analýza nálezů není architektura.** Architektura
odpovídá na jinou otázku: *„jak to má být poskládané, aby to drželo?"*

### 4.1 Devět optik — projdi je všechny

Každá optika je **jiná otázka na tentýž systém**. Piš ke každé, co jsi zjistil,
a hlavně **co z toho plyne pro návrh**.

| # | Optika | Otázky, na které odpovídej |
|---|---|---|
| **O1** | **Tok hodnoty** | Co orchestra vyrábí? Pro koho? Kudy to teče od granule k hotové hře? **Kde se tok zastaví a proč?** |
| **O2** | **Zdroje pravdy a vlastnictví** | Kdo vlastní který soubor? Kde je jedna pravda a kde kopie? **Co se stane, když se kopie rozejdou — a pozná to někdo?** |
| **O3** | **Smlouvy (kontrakty)** | Jaká rozhraní existují mezi: conductor ↔ agent ↔ hra ↔ šablona? **Jsou deklarovaná, nebo odvozená z konvence?** Co se stane při jejich porušení? |
| **O4** | **Hranice a vrstvy** | Co je jádro orchestra (nezávislé na hře a enginu) a co obálka? **Kde je skutečný šev** — a je ten šev tam, kde si myslíme? |
| **O5** | **Tiché selhání** | Kde se chyba ztratí, aniž by si jí někdo všiml? **Jaký je společný mechanismus** všech tichých selhání (je jich víc než deset)? |
| **O6** | **Testovatelnost jako vlastnost** | Co se dá ověřit offline a co jen v provozu? **Kde je test jen opsaná logika** (a tedy nechytí nic)? Jaká rozhodovací logika by měla být testovatelná a není? |
| **O7** | **Ekonomie změny** | Kolik souborů se musí změnit, když se přidá: hra? engine? brána? poskytovatel LLM? **Je ta cena úměrná, nebo roste s počtem her?** |
| **O8** | **Provoz a lidé** | Kdo to pouští? Jak pozná, že to funguje? **Co dělá člověk ručně** a co by mělo být automatické? Jak vypadá 3:00 v noci, když se to rozbije? |
| **O9** | **Druhá hra jako test návrhu** | Ne „až bude čas", ale **návrhová páka**: co z dnešního kódu by druhá hra rozbila? **Odpověď je zadání pro návrh**, ne odklad |

### 4.2 Na co si dát pozor při navrhování (tři napětí, která se nedají vyřešit, jen vyvážit)

**Tohle nejsou otázky s jednou odpovědí.** Patří k nejzajímavější části analýzy:

1. **Univerzalita vs. jednoduchost.** Čím obecnější orchestra je, tím víc
   abstrakcí — a abstrakce pro jednoho konzumenta je náklad bez užitku.
   *Ptej se: kolik konzumentů ta abstrakce má DNES, ne kolik jich čekáme?*
2. **Sdílení vs. nezávislost.** Sdílený soubor (šablona, konfigurace) znamená
   jednu opravu na jednom místě — a zároveň riziko, že se kopie rozejdou.
   *Ptej se: co je horší — rozejitá kopie, nebo neexistující volnost?*
3. **Kontrola vs. propustnost.** Každá brána je ochrana i překážka. Brána, která
   nic neměří, je nejhorší varianta (vypadá jako ochrana). *Ptej se u každé
   kontroly: co by se stalo, kdyby tam nebyla? Když nic, je to dekorace.*

### 4.3 Jak zapsat návrh (aby se dal odmítnout nebo přijmout)

**Návrh, který se nedá odmítnout, není návrh.** Proto:

- **Vždycky nabídni aspoň DVĚ varianty** a napiš, co každá stojí a co přináší.
  Jednovariantní návrh je politické rozhodnutí vydávané za technické.
- **U každé varianty napiš, co NEDĚLAT** — co vědomě zůstane nevyřešené.
  Architektura je i o tom, co odmítneš.
- **Napiš, jak poznáš, že návrh selhal** — měřitelnou podmínku, ne dojem.
  („Když přidání druhé hry bude znamenat víc než 5 změněných souborů, kontrakt
  nestačil.")
- **Rozliš „dnes" a „za měsíc".** Co je dnes zdarma a za měsíc drahé? To je
  rozhodující kritérium projektu (`PLAN-ROZVOJ-ORCHESTRA.md` §2).
- **U každého švu napiš, jestli ho vidíš v kódu, nebo ho jen předpokládáš.**
  Předpokládaný šev je hypotéza — označ ji.

---

## 5. Struktura výstupu (co má dokument obsahovat)

Dodrž ji. Není to formalita — chybějící oddíl se pozná jako chybějící odpověď.

### Část I — Jak to dnes je

1. **Verdikt v pěti větách** — co orchestra je, kde je její hlavní problém a co
   by se s tím mělo stát. **Piš to na začátek a přepiš na konec** (když se
   verdikt nezměnil, je to taky výsledek — a je vidět, že jsi nezačínal hotový).
2. **Co je orchestra** — mapování: komponenty, běhová prostředí, toky dat,
   hranice systému. **Diagram, ne seznam.** (Textový strom nebo tabulka stačí.)
3. **Inventura vlastností** — systematicky, ne náhodně:
   - **soubory a jejich role** (co je jádro, co obálka, co kopie, co mrtvé)
   - **brány a kontroly** (co měří, kdy běží, co je tvrdé a co poradní)
   - **stavy a přechody** (co se děje s granuli od založení po merge)
   - **konfigurace a zdroje pravdy** (kdo co vlastní, co se odvozuje)
   - **rozhraní** (endpointy, workflow, soubory — a kdo je volá)
4. **Katalog tříd selhání** — pokračuj v číslování **S1–S18**, které už existuje
   (`ANALYZA-ARCHITEKTURY-ORCHESTRA.md` a jeho §8). U každé: **kde** (kód/měření),
   **jak se to pozná dnes**, **co by to odhalilo**. **Cíl: dostat se přes 20.**
5. **Co je dobré a nemá se ztratit** — bez toho je analýza jen výčet vad
   a návrh začne bourat i to, co funguje.

### Část II — Jak to má být

6. **Architektura v optikách** (§4.1) — každá optika jako podkapitola.
7. **Návrh kontraktů** — co je deklarované, kdo je zdroj, jakým směrem se co šíří.
   **Konkrétně:** jak vypadá soubor, který říká „jsem hra a tady je moje
   konfigurace"? Jak vypadá manifest šablony?
8. **Dvě (nebo tři) varianty dalšího vývoje** — s cenou, rizikem a tím, co každá
   **nedělá**.
9. **Co nedělat** — vědomě odložené a proč. (Tenhle oddíl je stejně důležitý
   jako návrh: chrání před předčasnou abstrakcí.)

### Část III — Poctivost

10. **Co analýza NEZJISTILA** — co jsi neměřil, co jsi nedohlédl, kde je tvoje
    tvrzení jen odvozené. **Povinné a myšlené vážně.**
11. **Čím je každé tvrzení doložené** — souhrnná tabulka „tvrzení → důkaz"
    u klíčových závěrů. (Ne u všech — u těch, na kterých stojí rozhodnutí.)
12. **Co by tuhle analýzu vyvrátilo** — kdyby se ukázalo, že se mýlíš, jak by to
    vypadalo? (Tohle je nejtěžší oddíl a nejvíc vypovídá o kvalitě práce.)

---

## 6. Na co se konkrétně zeptat (otázky, které nejsou v žádném dokumentu)

Tohle jsou **díry**, které jsem při psaní zadání našel. Nejsou to nálezy — jsou
to otázky, na které dnes nikdo nezná odpověď. **Odpověz aspoň na polovinu.**

| # | Otázka | Proč je důležitá |
|---|---|---|
| **Q1** | **Kolik z celkového času orchestra skutečně pracuje?** (Naměřeno jen jedno okno: 7,5 h výpadku.) | Bez toho se nedá říct, jestli je orchestra „pomalá", nebo „často mrtvá" |
| **Q2** | **Jaký je poměr úspěšných granulí k vydaným?** (`total_count` 241 běhů, ale kolik z nich dokončilo granuli?) | Rozhoduje o tom, jestli má smysl zvyšovat počet pokusů, nebo snižovat velikost granulí |
| **Q3** | **Kde orchestra tráví nejvíc volání modelu — a proč?** | Ekonomie free kvóty; ověřitelné z logů běhů |
| **Q4** | **Co se stane, když se registr her rozbije?** (Invariant 18 to popisuje, ale **co to udělá dnes**?) | Rozhoduje o prioritě fallbacku |
| **Q5** | **Je šablona `repo/` skutečně nezávislá na hře, nebo má skryté vazby?** (Ověřeno jen u několika souborů.) | Přímý vstup pro návrh kontraktu |
| **Q6** | **Které soubory v šabloně se NIKDY nepoužijí v nové hře?** | Mrtvá váha, kterou každá hra dědí |
| **Q7** | **Co dělá agent, když dostane granuli, které nerozumí?** | Selhání, které nikdo neměří |
| **Q8** | **Jak vypadá orchestrace, když pracuje na DVOU hrách zároveň?** (Nikdy nenastalo.) | Teoreticky popsané, prakticky neověřené |
| **Q9** | **Kolik z `tools/` (70 souborů) je živých?** | 70 nástrojů je samo o sobě nález |
| **Q10** | **Kde je v orchestra „zdroj pravdy o roadmapě" — soubor, nebo D1?** | Naměřeno, že obojí a synchronizace je ruční |

---

## 7. Kde co je (materiál, ze kterého čerpat)

**Přečti v tomhle pořadí** — a u každého si v duchu řekni, čemu z něj **nevěříš**:

| Soubor | Co v něm je | Pozor |
|---|---|---|
| `AGENTS.md` | trvalá pravidla, pasti prostředí, jak ověřovat | **Tohle je závazné** — ne metodika, ale pravidla |
| `HANDOFF.md` | stav poslední session + implementační plán | Je čerstvý, ale **i on je jen tvrzení** |
| `ORCHESTRA-STAV-A-ANALYZA.md` | stav doporučení L1–L17/ST1–ST10 (měřeno) | Nejužitečnější přehled „co je hotové" |
| `ANALYZA-ARCHITEKTURY-ORCHESTRA.md` | analýza architektury + §8 dodatek (S1–S18) | **Hlavní vstup** — a zároveň to, co máš **prohloubit**, ne opsat |
| `ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md` | audit conductora, inventura `tools/`, **spustitelný skript na cooldown** | Podklady; §1.2 je měřicí nástroj |
| `PLAN-ROZVOJ-ORCHESTRA.md` | fáze F0–F5 + §3.5 implementační plán + otázky O1–O10 | Plán, který **není** architektura |
| `PLAN-ORCHESTRA-AI-AGENTI.md`, `PLAN-SEPARACE-WORKSPACE.md` | dva další plány (provoz, separace) | Neřeš je; jen věz, že existují |
| `FORGE-ORCHESTRA-MOZNOSTI.md`, `MOZNOSTI-AGENTA.md` | nálezy a měřené schopnosti agenta | Druhé je zdroj pravdy o tom, co agent umí |
| `orchestra/README.md`, `orchestra/conductor/src/index.ts` | **samotný systém** | `index.ts` je ~1 400 řádků; čti ho po částech a **piš si řádky** |
| `~\.dsh\skills\orchestra\SKILL.md` | operativa, invarianty 1–19 | Invarianty jsou draze naučené — ale **čísla v nich zestarala** |
| `~\.dsh\skills\overovani\SKILL.md` | jak ověřit, že brána měří (sabotér) | Použij na každou bránu, kterou budeš hodnotit |

**Měřicí nástroje ve workspace:** `_analyza\stav-doporuceni.mjs` (stav doporučení),
`stav-ci.mjs`, `stav-agent.mjs`, `stav-release.mjs` (stav cíle přes API),
`sken-vazeb.py` (plošné skeny), `over-handoff-nic-nezmizelo.py` (kontrola úplnosti
přepisu — pouč se z toho vzoru).

---

## 8. Pravidla práce (aby analýza nezapadla nebo neuškodila)

1. **Zapisuj jen do svých dokumentů.** Kód orchestra je nedotknutelný.
2. **Zapiš téma do `OTEVRENA-TEMATA.md`, když se objeví** — ne na konci.
3. **Po každé editaci dokumentace spusť** `kontrola-diakritiky.py`,
   `over-dokumentaci.py`, `over-skilly.py`.
4. **Píšeš-li do dokumentace ukázku rozbitého kódování, popiš ji SLOVY** —
   kontrola diakritiky to jinak nahlásí jako vadu dokumentu.
5. **Nepushovat, necommitovat bez vyžádání.** Před commitem ukázat `git status`
   a `git diff --stat`.
6. **Nevypisuj PAT** a nepiš ho do historie příkazů.
7. **U `.ps1` volat `oprav-ps1-kodovani.py`** a ověřit parserem.
8. **Když si nejsi jistý, napiš „nedokázáno"** — ne sebejistotu.

---

## 9. Hotovo znamená (měřitelné, ne dojem)

Analýza je hotová, když **všechno** platí:

- [ ] Existuje dokument, který má **všech 12 oddílů** z §5.
- [ ] **Každé tvrzení o chování** má značku (**měřeno**/**kód**/**odvozeno**/**nevím**).
- [ ] **Aspoň 5 nových tříd selhání** nad rámec S1–S18 s doloženým zdrojem.
- [ ] **Aspoň 3 vlastní měření**, která v existujících dokumentech nejsou
      (u každého: příkaz, výsledek, datum).
- [ ] **Aspoň 1 tvrzení z existující dokumentace je vyvráceno nebo zpřesněno** —
      a je vidět, čím. (Když se to nepovede, **napiš to a řekni proč**;
      „všechno sedělo" je taky výsledek, ale musí být doložený.)
- [ ] Je odpovězeno na **aspoň 5 z 10 otázek** v §6.
- [ ] Návrh má **aspoň 2 varianty** s cenou, rizikem a tím, co každá **nedělá**.
- [ ] Je napsané, **co by analýzu vyvrátilo** (§5.12).
- [ ] Je napsané, **co analýza nezjistila** (§5.10) — a nejsou to fráze.
- [ ] **Nula změn v obou repech orchestra a hry** (`git status`).

---

## 10. Jedna věta na závěr

**Nejsi tu od toho, aby seznamoval vady.** Vad je v projektu dnes známo víc než
dvacet a každá má svoje číslo. Jsi tu od toho, aby řekl, **jak má orchestra
vypadat, aby těch vad bylo míň** — a aby to řekl tak, že se podle toho dá
rozhodnout a že se to dá odmítnout.

Když se ti to povede jen zčásti, **napiš, ve kterém místě se to nepovedlo**.
Přiznaná mez je užitečnější než uhlazený závěr — v tomhle projektu se to
potvrdilo už mockrát.
