# PROMPT pro novou session (dokončení auditu)

**Co tenhle dokument JE:** hotový prompt ke zkopírování do nového chatu.
Vznikl podle šablony v `PREDAVANI-SESSION.md` §4.

**Proč není v `NEXT-SESSION-INSTRUKCE.md`:** ten soubor patří **souběžné
session**, která ho naposledy zapsala v **17:38** (naměřeno). Přepsat ho by
znamenalo zahodit cizí práci.

---

<!-- ▼▼▼ ZKOPÍRUJ CELÉ DO NOVÉHO CHATU ▼▼▼ -->
Jsi **akční session** ve workspace `C:\Users\Ssevc\Local-Deepseek`.

**Zadání pro tebe je v `ZADANI-DOKONCENI-AUDITU.md` — přečti ho CELÝ.**
Postup předávání je v `PREDAVANI-SESSION.md`, pravidla v `AGENTS.md`,
stav v `HANDOFF.md` (§22) a plán v `PLAN-DALSI-KROK.md`.

> **⚠ Nepoužívej `NEXT-SESSION-INSTRUKCE.md` jako svoje zadání.** Ten soubor
> patří souběžné session (naposledy zapsán 17:38). Tvoje zadání je samostatný
> dokument `ZADANI-DOKONCENI-AUDITU.md`.

**Než začneš cokoli dělat, proveď kontrolu zadání:**
1. Zkontroluj hlavičku zadání: `git -C orchestra rev-parse HEAD` a
   `git -C games\uo-shadows rev-parse HEAD` proti tomu, co zadání tvrdí
   (`d1cde9bbf` / `279f58486`). Když se to liší, **přeměř všechny údaje
   o stavu** a zapiš to jako nález.
2. Ověř **aspoň tři** klíčová tvrzení zadání spuštěním (ne čtením). Nejpřímější
   je `python _analyza\audit7-overeni-zadani.py` — ověří kotevní řetězce,
   počty granulí i to, že `ag-mutace.py` není v `g3-brany.py`.
3. Když něco nesedí, **zastav se v tom bodě**, zapiš to jako nález a jdi na
   body, které sedí. **Nepřepisuj zadání podle sebe.**

**Cíl:** opravit tři naměřené vady dokumentace a jejich měřidla. (1) `AGENTS.md`
si na dvou místech odporuje o počtu sloupců schématu — řádek 62 tvrdí „správně
je 39", řádek 337 a živý `schema.sql` tvrdí 40; číslo 39 bylo správně před B1
a chybí u něj značka času. (2) `_analyza\ag-mutace.py` — jediný test, který
dokazuje, že brána nad autoritou měří — **neproběhne**, protože hledá řetězec,
který v dokumentu není, a **není v `g3-brany.py`**, takže si jeho `exit 1`
nikdo nevšimne. (3) Dva další mutační testy se nedají spustit a nikde to není
napsané.

**Hlavní riziko:** v témže workspace **pracovala souběžná session** — během
auditu se `HANDOFF.md`, `AGENTS.md` i dva skilly měnily pod rukama. Proto je
**Úkol 0 (zmrazit snapshot) první a nesmí se vynechat**; bez něj naměříš zase
něco jiného. **Druhé riziko:** audit **stáhl vlastní nález R3** — v `HANDOFF.md`
se „21 granul" **nesmí opravovat**, jsou to datované záznamy a přepsání by
zničilo historii. **Třetí:** u Úkolu 2 nestačí, že `ag-mutace.py` vyjde `exit 0`
— musíš **vložit vadu do `AGENTS.md:337`** a vidět, že brána spadne.

**Na konci povinně:** proveď **Úkol 6** ze zadání (přegeneruj
`_analyza\_inventar.json`, přidej `ZADANI-DOKONCENI-AUDITU.md` do seznamu
v `kontrola-diakritiky.py`, zapiš výsledky a **vlastní omyly** do `HANDOFF.md`,
doplň **řádek do `KRONIKA-PROJEKTU.md`** včetně nových návrhů ve stavu
`NEOVĚŘENO`) a spusť **všechny** brány — u každé ověř, že soubor **otevřela**.
Pak napiš zadání pro další session podle `PREDAVANI-SESSION.md` **§6.2 F**
(pozor: `NEXT-SESSION-INSTRUKCE.md` přepiš **jen když se od 17:38 nezměnil**,
jinak napiš nový soubor a v `HANDOFF.md` vysvětli proč) a **do chatu vlož
prompt pro uživatele** podle §4 **i se STAVOVÝM ŘÁDKEM** podle §2.1.
**Před commitem a pushem vždy nejdřív ukaž `git status` a `git diff --stat`
a počkej na vyžádání.**
<!-- ▲▲▲ KONEC BLOKU KE ZKOPÍROVÁNÍ ▲▲▲ -->

---

## Co je v promptu schválně a proč

| Prvek | Proč tam je |
|---|---|
| Odkaz na `ZADANI-DOKONCENI-AUDITU.md`, ne na `NEXT-SESSION-INSTRUKCE.md` | Zadání žije v souboru, kde se dá ověřit — a ten druhý patří cizí session |
| `audit7-overeni-zadani.py` jako kontrola | Ověří **tři** tvrzení zadání jedním příkazem; jinak by je session musela hledat |
| „Úkol 0 je první a nesmí se vynechat" | Naměřeno: dokumenty se měnily v průběhu auditu |
| „R3 se NESMÍ opravovat" | Audit stáhl vlastní nález; bez varování by ho session „opravila" a zničila historii |
| „Nestačí `exit 0` — vlož vadu" | `exit 0` u mutačního testu není důkaz, že měří |
| Odkaz na §6.2 F s podmínkou na `mtime` | Řetěz předávání musí pokračovat, ale nesmí přepsat cizí práci |
