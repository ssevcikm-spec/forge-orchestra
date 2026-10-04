
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
### 8j. Omyly AKČNÍ session 2. 10. 2026 (dokončení auditu dokumentace) — **87–93**

**Kontext:** sedm omylů vzniklo jedné session při **opravě měřidel podle
auditu** (`ZADANI-DOKONCENI-AUDITU.md`). **Všech sedm je v měřidlech nebo
v postupu měření** — ani jeden není nález o cizím kódu. **Dva z nich (`87`,
`88`) by neodhalilo čtení kódu**; odhalil je až **mutační test**.

| # | Co jsem udělal | Jak to vzniklo | Jak se to poznalo | Správně |
|---|---|---|---|---|
| **87** | **Mutační skript spadl na přehnaně přísném assertu** — a mohl nechat `HANDOFF.md` zmutovaný | `assert "Provedeno 2. 10. 2026" not in zmut` kontroloval **celý dokument**, ale ten řetězec je i v **§16** a **§21** | `AssertionError` **na správné mutaci**; škoda nevznikla jen tím, že assert byl **PŘED** zápisem | Assert o „podmínka přestala platit" **zúžit na měřenou jednotku** (ten nadpis, ten řádek), ne na soubor. A **každou mutaci obal `try/finally`**, které soubor vrátí. *(Obě pravidla zapsána do `overovani` §10.6)* |
| **88** | **Značka času se mi přilepila od SOUSEDNÍHO tvrzení** | má funkce `ma_znacku_casu()` hledala „stav před" **kdekoliv v okně ±60 znaků** | **mutační test M2**: číslo `32` dostalo značku od třicetidevítky (`**„32 sloupců"**, správně je **39** (stav před B1…)`) → brána ho zařadila jako `[záznam]` a byla **slepá přesně k vadě R1** | Značka musí být k číslu **PŘIPOJENÁ**: mezi číslem a značkou nesmí být **jiné číslo**. *(→ `overovani` §10.3)* |
| **89** | **Okno „blok výskytu" jsem vzal 5 441 znaků** | první verze brala „souvislý běh neprázdných řádků" | **mutační test M2** — a jen proto, že jsem **vypisoval velikost okna**. V `AGENTS.md` je oddíl „## Jak dokumentovat" **jeden blok o 5 441 znacích se sedmi daty** → jediné datum kdekoli v něm **umlčelo celá oddíl** | Okno **zastavit na začátku dalšího celku** (odrážka, tabulka, nadpis) → **824 znaků**. A **zúžení ZVÝŠILO pokrytí** (26 → 27 rozchodů): **velkorysé okno není opatrnost, je to slepota.** *(→ §10.4)* |
| **90** | **Můj ověřovatel měřil JINÝM OKNEM než nástroj** | v `audit2b-over.py` jsem blok spočítal znovu — jako „souvislé neprázdné řádky" (5 441 znaků), kdežto nástroj už používal **jednu odrážku** (824) | výpis ověřovatele ukazoval **čísla z jiného okna, než jaké se měřilo** — a přitom vypadal jako důkaz | Když ověřovatel reimplementuje logiku nástroje, musí to být **řádek po řádku táž logika** + komentář „MUSÍ BÝT SHODNÉ S…". Je to **§9.2 znovu, o vrstvu níž**. *(→ §10.5)* |
| **91** | **Zálohu jsem udělal u `audit2a-schema.py`, ale NE u `audit2b-cisla-proti-zdroji.py`** | `Copy-Item` jsem použil u prvního souboru a u druhého jsem rovnou přepsal | Naštěstí **nic nevzniklo** — měl jsem celé původní znění z čtení. Ale `overovani` §2.1 říká **„zálohuj kopií"** a u souboru, který **není v gitu**, je to jediná cesta zpět | **Záloha PŘED prvním zápisem**, ne před druhým. A týž den se to málem vymstilo i u `HANDOFF.md` (omyl 87) |
| **92** | **Snapshot sám sobě zneplatnil baseline inventáře** | `audit-snapshot.py` (Úkol 0) kopíruje dokumentaci do `_analyza\snapshot-<čas>\` — a `audit1-inventar.py` ty **kopie začal počítat jako dokumenty** | `audit1-inventar.py` po prvním snapshotu: **159 dokumentů místo 98**, **66 záloh místo 8**, „bez hlavičky" **116 z 159** místo **62 z 98** | Vyloučit předponu `snapshot-` (doplněno do `audit1-inventar.py`). **Obecné poučení: opatření, které něco KOPÍRUJE, musí říct všem měřidlům, že je to kopie** — jinak si příští session přečte vlastní snapshot jako stav dokumentace |
| **93** | **První dojem z rozdílu proti baseline byl „regrese"** | `audit6-brany-mutace.py` i `g3-brany.py` hlásily proti auditu **jiná čísla** (`validate-all (CELEK)` `exit 1` → `exit 0`) | Než jsem to zapsal, všiml jsem si, že audit to vedl jako **„NEPROBĚHLO — PROSTŘEDÍ"** — a teď je sandbox **`danger-full-access`** | Je to **§7.13**: „neproběhlo" se pod širším oprávněním **změní na zelenou** a **není to oprava kódu**. Do zápisu patří **obojí**: co se změnilo a **čím to bylo** |

**Vzor z těch sedmi (a je nepříjemný):** **sedm ze sedmi** vzniklo
**v měřidle nebo v postupu**, a **dva** z nich by bez **mutačního testu**
odešly jako hotová práce. To je týž podíl jako v předchozích blocích — **trend
se nezlepšil**, i když session dělala právě opravu měřidel. Nejlepší vysvětlení,
které pro to mám: **oprava měřidla je sama měření**, takže na ni platí tytéž
pasti — a kdo je nezná, projde jimi znovu.

**A jeden údaj, který tomu nasvědčuje:** omyl **88** je **třetí výskyt téže
třídy** („měřidlo odpovídá na jinou otázku") v jedné session — po omylu **89**
(okno) a **90** (jiné okno v ověřovateli). Všechny tři mají stejný podpis jako
nálezy z 1. 10. a přesto se opakovaly.
