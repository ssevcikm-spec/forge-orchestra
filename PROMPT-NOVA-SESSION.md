# PROMPT PRO NOVÝ CHAT — ověření práce session `eb127abd` + pokračování

> **Co tenhle dokument JE:** postup. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

> ## ⚠ HISTORICKÝ DOKUMENT — NEPOUŽÍVEJ TENHLE PROMPT
>
> **Co tenhle soubor JE:** **jednorázový prompt** pro session, která ověřovala
> práci session `eb127abd` (2. 10. 2026). Jeho **Krok 1 je SPLNĚNÝ — 12/12
> bodů** (výsledek v `HANDOFF.md` §7.5) a **bod 8 v něm už neplatí** (PR #28–#31
> jsou sloučené). **Nespouštěj ho znovu.**
>
> **Co z něj platí dál:** je to **vzor, jak se ptát** — „ověř to, nevěř tomu".
> **Aktuální postup předávání je ale v `PREDAVANI-SESSION.md`** (dva kroky:
> plánovací a akční session, se šablonami promptů). Tenhle soubor se **nechává
> jako doklad** toho, jak vypadalo zadání k ověření — a protože se z něj
> do `PREDAVANI-SESSION.md` převzala metodika.
>
> **Aktuální stav je vždy v `HANDOFF.md`; aktuální zadání
> v `NEXT-SESSION-INSTRUKCE.md`.**

*(Zkopíruj celý tenhle soubor jako první zprávu do nového chatu. Je psaný tak,
aby nová session nemusela hádat, co se stalo — a aby **nevěřila** tomu, co
tvrdí předchozí session, ale **změřila to**.)*

---

Pracuješ v `C:\Users\Ssevc\Local-Deepseek`. Jsi **nová session** — kód ani
dokumenty, o kterých tu bude řeč, jsi nepsal. **To je tvoje hlavní výhoda,
ne formalita:** `AGENTS.md` vyžaduje, aby analýzu a ověření cizí práce dělal
**někdo jiný** než autor (*„Autor není nezávislý reviewer."*).

**Než začneš, načti v tomto pořadí:**

1. `AGENTS.md` — trvalá pravidla (**závazná**, ne metodika).
2. **`HANDOFF.md`** — stav práce. **Přečti ho celý**, je kvůli tobě přepsaný:
   §1 co je hotové, §2 co je otevřené, §3 nálezy N1–N8,
   **§7.2 výzva k ověření** (to je tvůj hlavní úkol), §8 vlastní omyly.
3. Skill **`dsh-prostredi`** — pasti prostředí (kódování, sandbox, tiché
   přeskakování souborů). **Načti ho `skill` toolem**, ne očima.
4. Skill **`overovani`** — jak poznat, že brána **skutečně měří**. Použiješ ho
   na každou kontrolu níž.

---

## Co se stalo (a proč je tenhle prompt takhle postavený)

**2. 10. 2026 pracovaly v tomhle workspace TŘI session současně:**

| Session | Co dělala |
|---|---|
| `7cd67c66` | druhé kolo hloubkové analýzy orchestra (S31–S37) |
| `7db45275` | jazykový inventář — kde je v kódu čeština na místě identifikátoru |
| **`eb127abd`** | **provedla plány A1–A4 a Z1–Z8** — tedy **měnila kód obou repů** |

**Následek:** `HANDOFF.md` psaly dvě session současně (jedna přepsala verzi
druhé), a třetí session pak **změnila kód, čímž zastarala analýzu**, která je
jinak výchozím bodem pro každou další session. Vznikly **tři dokumenty, každý
s jiným „dnešním stavem"** — tedy přesně ta vada, o které ta analýza je
(*„stav, který si systém hlásí sám, se rozešel se stavem, který je vidět"*).

**Session `eb127abd` to sjednotila** a **sama si při tom našla 5 vlastních
omylů** (HANDOFF §8, omyly 5–10). To je důvod, proč **nesmíš věřit jejím
číslům** — a proč je tvůj první úkol ověřit je.

---

## TVŮJ ÚKOL

### Krok 1 — OVĚŘIT PRÁCI PŘEDCHOZÍ SESSION (hlavní úkol)

**Předchozí session o sobě tvrdí, že A1–A4 a Z1–Z8 jsou hotové a ověřené.**
Každé to tvrzení má **spustitelný důkaz** — a tvůj úkol je **zkusit je
vyvrátit**. Tabulka je v `HANDOFF.md` §7.2; je to **10 bodů**:

| # | Co ověřit | Jak |
|---|---|---|
| 1 | **A1 rozhoduje podle `merged`** | vlož zpět `if (ok)` (bez `&& merged`) a spusť `python _analyza\a1-a2-over.py` → **musí spadnout** |
| 2 | **A2 rozlišuje `null` (nevím) od prázdného stromu** | změň `stromMain !== null && owns.length > 0` na `owns.length > 0` → **musí spadnout** |
| 3 | **A3 je v OBOU kopiích** | smaž `exit 1` v **herní** kopii `agent.yml` → `python _analyza\a3-over.py` **musí hlásit chybu ve hře** |
| 4 | **Z4/Z7 mají shodné hashe** | `Get-FileHash` na obou dvojicích → **531AE859…** a **FE639998…** |
| 5 | **Analýza je zastaralá v 5 tvrzeních** | `python _analyza\n8-zastarala-analyza.py` a **5 tvrzení ověř v kódu sám** |
| 6 | **N1 je pravda** (inventář se sám negeneruje) | změň soubor, spusť `hl-rizika-jazyka.py` **bez** regenerace → **musí hlásit vady, které nejsou** |
| 7 | **N3 je pravda** (jiný krok v herním repu) | `python _analyza\z8-probe.py` → **dva různé kroky** |
| 8 | **Tři PR jsou pořád nesloučené** | `node _analyza\hl2-s29-s30.mjs` → `merged_at: null` |
| 9 | **Nic není pushnuté** | `git rev-list --count origin/main..HEAD` → **1** v každém repu |
| 10 | **Brány nejsou slepé** | spusť **všechny** z `HANDOFF.md` §6 a u **každé** ověř, že soubor **vůbec otevřela** |
| 11 | **Čísla v `AGENTS.md` sedí se zdrojem** | `python _analyza\ag-over-cisla.py` → **5 v pořádku, 2 historická, 0 rozchodů** |
| 12 | **Ten nástroj sám měří správně** | vlož do `AGENTS.md` vadu (`39 sloupců` → `32`) → musí **spadnout**; pak větu **přeformuluj** („pět tabulek") → musí hlásit **„NENAŠEL JSEM TVRZENÍ"**, ne „OK" |

**U každého bodu napiš: prošlo / neprošlo / nedalo se ověřit — a čím.**
**Neprošlý bod je nález, ne tvoje chyba.**

> **Past, na kterou si dej pozor (S27):** *„zelená" u nového dokumentu
> neznamená nic, dokud neověříš, že ho brána **má v seznamu**.* Naměřeno
> 2. 10. 2026: `kontrola-diakritiky.py` hlásila „VŠE OK" nad dokumentem,
> který **nikdy neotevřela** — a stalo se to **pětkrát**.

> **Druhá past:** statická kontrola musí číst **KÓD, ne komentáře.**
> Naměřeno: test hledal `locked.add(lockKeys(...))` a **našel to v komentáři,
> který vadu popisuje** — prošel i s vrácenou vadou. Před hledáním vzorců
> **odstraň komentáře**.

### Krok 2 — ROZHODNOUT, CO DÁL

Až budeš mít výsledek ověření, projdi **`HANDOFF.md` §2 (co je otevřené)**
a **`IMPLEMENTACE-NOVE-NALEZY-Z-UKOTVENI.md` (N1–N9)** a rozhodni:

- které nálezy se opraví **hned** a které se předají jako zadání,
- **O3** — má se sáhnout na běžícího conductora? (**Pozor: deploy je z gitu,
  takže „nasadit" znamená pushnout — a to vyžaduje vyžádání.**),
- **tři visící PR** (#28 `save.gd`, #29 `hud.gd`, #30 `mining.gd`) — sloučit
  ručně, nebo doplnit `size_lines` a nechat projet znovu?
- **N9:** má se `ag-over-cisla.py` zapojit do `validate-all.mjs`, nebo se
  pouští ručně? A **která další čísla v `AGENTS.md` v něm ještě nejsou**
  (pokrývá 5, zbytek ne) — částečný nástroj může budit falešný dojem úplnosti.

> **Krok 2 je navíc o jedné věci, kterou předchozí session nestihla:** projít
> **`_analyza\`** a rozhodnout, které nástroje mají být **součástí
> `validate-all.mjs`** a které zůstanou ruční.
> **Naměřeno 2. 10. 2026:** v `_analyza\` je **24 souborů změněných ten den**
> (tři session), z toho **6 vytvořila tato session** (`a1-a2-over.py`,
> `a3-over.py`, `z8-probe.py`, `n8-zastarala-analyza.py`,
> `handoff-kontrola-uplnost.py`, `ag-over-cisla.py`) — a **žádný z nich není
> v CI**. To je stav, kdy na některý někdo zapomene.


### Krok 3 — ZAPSAT

- **Výsledek ověření** do `HANDOFF.md` (nová sekce, nic nemaž).
- **Svoje vlastní omyly** do `HANDOFF.md` §8 — je to **nejsilnější důkaz, že
  se měřilo.** Dvě session přede mnou jich měly dohromady deset a většinu
  našel až **mutační test nebo kontrola úplnosti**.

---

## Metodika (povinná)

- **Metriku ověř na známém správném I známém chybném případu.** „Prošlo to"
  bez toho neznamená nic. *(Předchozí session na tomhle sama padla — omyl č. 9:
  její skript měl obrácenou podmínku a hlásil „0 zastaralých" u kódu, který
  sama změnila. Odhalilo se to **jen tím, že znala správný výsledek**.)*
- **Napsal jsi test? Vrať do kódu vadu a podívej se, že spadne.** Mutační test
  je jediný důkaz, že test měří.
- **Ke každému číslu patří postup a čas.** Kód se v tomhle projektu mění
  **i během session** — naměřeno.
- **Nula a „nezměřeno" nejsou úspěch.** Když se nic nezměřilo, musí to být
  vidět.
- **Hledej `grep` toolem, ne PowerShellem** — a **na plošné skeny použij
  Python walk** (grep tool tiše přeskakuje skryté složky; naměřeno **80 ku 0**).
- **Ověřovací skripty spouštěj s `$env:PYTHONIOENCODING='utf-8'`.**
- **Síť jen Node `fetch`** (TLS z PowerShellu nefunguje), **git přes
  `orchestra\tools\git.cmd`**.
- **Do `.ps1` se píše bajty** (UTF-8 BOM + CRLF) a po editaci se ověřuje
  parserem.

## Co NEDĚLAT

- **Nepushovat a necommitovat bez vyžádání.** Před commitem i pushem ukázat
  `git status` a `git diff --stat`.
- **Nepřekládat dokumentaci plošně** — brány ty české texty **hledají**.
- **Nezakládat druhou hru** ani nemazat `forge-quest` (živá hra).
- **Nevypisovat PAT** ze `orchestra\.secrets\`.
- **Neplnit znovu `ANALYZA-HLOUBKOVA-2-ZADANI.md`** — je **splněné** (9/9).
- **Neotáčet pořadí A1/A3** (A3 před A1 vyrobí smyčku:
  PR nesloučen → běh červený → úloha zpět `ready` → dispatch znovu).
- **Nevěřit číslům z handoffu bez ověření** — ale **než nějaké označíš za
  nepravdivé, zopakuj ho TÝMŽ postupem, jakým vzniklo.**

## Hotovo znamená (měřitelné)

- [ ] **Všech 10 bodů z §7.2** má výsledek: **prošlo / neprošlo / nedalo se
      ověřit** — a u každého je **příkaz a výstup**.
- [ ] **Aspoň u 3 bodů je proveden mutační test** (vrácená vada → spadne).
- [ ] U **každé** spuštěné brány je ověřeno, že **soubor vůbec otevřela** (S27).
- [ ] **Napsané, co se ověřit NEDALO** a proč (přiznaná mez je užitečnější
      než uhlazený závěr).
- [ ] **Aspoň jeden tvrzený výsledek je vyvrácen nebo zpřesněn** — a je vidět
      čím. *(Když **nic** nevyvrátíš, napiš to taky — ale pak zvaž, jestli
      jsi měřil, nebo opisoval.)*
- [ ] **Tvoje vlastní omyly** jsou zapsané v `HANDOFF.md` §8.
- [ ] Nic se neztratilo: `python _analyza\handoff-kontrola-uplnost.py` → **0 chyb**.
- [ ] Všechny brány z `HANDOFF.md` §6 spuštěné, výsledek **s časem**.

**Když některý bod nesplníš, napiš to a vysvětli proč.** Přiznaná mez je
užitečnější než uhlazený závěr.

---

## Dvě věci, které platí i po téhle session

1. **Skill smí mít konkrétní příklady, šablona hry ne.** Testovací otázka pro
   obecnou část: *„Platí to i pro systém, který ještě neexistuje?"*
   **Skill bez příkladů je nepoužitelný; šablona s cizími příklady šíří
   pozůstatky staré hry.**
2. **Znalost patří k naměřenému příkladu, ne k pravidlu.** „Ověřuj" nikoho nic
   nenaučí; **past s číslem, souborem a datem ano.** Když narazíš na past,
   která v žádném skillu není, **doplň ji tam** i s příkladem.

**A poslední věc, kterou stojí za to mít na paměti:** předchozí session
napáchala **pět vlastních omylů** a **všechny vypadaly jako nález o systému**
(„chybí zadání", „kód je slepý", „analýza je v pořádku"). **Většina z nich
byla vada měření.** Počítej, že i tvoje první číslo bude někde mimo.
