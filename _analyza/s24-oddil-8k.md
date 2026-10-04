
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

### 8k. Omyly PLÁNOVACÍ (ověřovací) session 2. 10. 2026 (16:4x–17:1x UTC) — **97–101**

**Kontext:** pět omylů vzniklo jedné session při **ověřování cizí práce** —
a **všechny jsou v měřidlech nebo v postupu měření**, ani jeden není nález
o cizím kódu. **Dva z nich (`99`, `100`) by neodhalilo čtení kódu**; odhalil je
až **mutační test**. To je týž podíl jako v blocích `8e`–`8j` — **trend se
nezlepšil**, ani když session dělala **jen ověřování**.

| # | Co jsem udělal | Jak to vzniklo | Jak se to poznalo | Správně |
|---|---|---|---|---|
| **97** | **Měřil jsem „brána to nehlásí" podle VÝPISU, a výpis je zkrácený** | `s24-slepota-audit2b.py` usoudil „`audit2b` vložené tvrzení nevidí", protože ho nenašel ve výstupu | Ručně jsem došel na to, že `audit2b` tiskne ze ZÁZNAMŮ jen **prvních 40** (`histor[:40]`) — takže „není ve výpisu" **není** „nevidí to" | Měřit **ČÍTAČ ze souhrnu** (`ROZCHODŮ: N`), ne výskyt ve výpisu. Vzniklo `s24-slepota-audit2b-presne.py`. Je to `overovani` **§9.4**: *naměřeno 0 má tři různé významy* |
| **98** | **Nechal jsem si ověřovatele spočítat jen ČÁST měření** | v hrubé verzi jsem kontroloval jen `ROZCHODŮ`, ale tvrdil jsem něco o **klasifikaci** (záznam vs. tvrzení) | Tentýž běh: tvrzení se ve výpisu objevilo, ale **nebylo v rozchodech** — a moje zpráva to nerozlišila | Oddělit **dvě otázky**: (a) *vidí to brána?* (b) *zařadila to správně?* — a ptát se na každou **jiným měřením**. Obě jsou teď v přesné verzi |
| **99** | **Tři neúspěšné verze jedné kontroly — a každá SELHALA JINAK** | do nové brány `s24-meridla-over.py` jsem psal kontrolu „kolik bloků omylů je mimo kotvy brány" | **M1:** vzor `### 8[a-z]` — mutace `8h-test` mu **vyhověla** → kontrola nereagovala. **M2:** „padni, když odpovídá VŠE" — mutace shodu **snížila** (10 → 7) → taky nereagovala, **a navíc padala na zdravém stavu** (`8i`/`8j`). **M3 (správně):** kotva brány musí v dokumentu **existovat** | `overovani` **§7.14**: mutace musí obrátit **MĚŘENOU PODMÍNKU**, ne jen změnit soubor — a **směr podmínky se musí ověřit na OBOU stranách** (zdravý stav musí projít, vada musí spadnout). Cena: **tři kola**, každé odhalil až mutační test |
| **100** | **Použil jsem NEAKTUÁLNÍ předpoklad o cizím nástroji** | do brány jsem napsal, že `validate-all` má `otevřela:` **prázdné** (tak to bylo v auditu) | Běh ukázal **`otevřela: 3`** — a to **není počet souborů, ale `NALEZENO 3 PROBLÉMŮ`**. Past **zůstala**, jen **změnila projev** | Ověřovat **živý stav**, ne zápis v auditu; a **vzor, který umí trefit chybovou hlášku, je vada i tehdy, když vypadá jako číslo**. Zapsáno do `HANDOFF.md` §24.6 a do zadání jako Úkol 2a |
| **101** | **Zápis vlastního výstupu do složky, kterou táž brána prochází** | `python _analyza\g1-…py > _analyza\_tmp-g1.txt` — PowerShell zapsal **UTF-16LE** | `g1` ohlásil **`exit 1`** s jedinou vadou: `_tmp-g1.txt … NELZE PŘEČÍST: UnicodeDecodeError` → **vadou byl můj vlastní soubor** | Nástroj **`audit-cleanup.py`** na to existuje **od auditu** a audit tuhle past **sám zapsal** („první běh `g1` skončil `exit 1` a jediná vada byl můj vlastní výstupní soubor"). **Je to počtvrté** → zapsáno jako nález **H30** |

**Vzor z těch pěti (a je nepříjemný):** **pět z pěti** vzniklo
**v měřidle nebo v postupu**, a **dva** by bez **mutačního testu** odešly jako
hotová práce. **A ještě jeden údaj do trendu:** omyl **97** je **třetí výskyt
téže třídy** („měřidlo odpovídá na jinou otázku") v jedné session — po **98**
(nezměřená část) a **99** (třikrát špatný směr kontroly).

---
