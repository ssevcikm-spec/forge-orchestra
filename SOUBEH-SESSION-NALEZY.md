# Co proklouzlo souběhem dvou session — a co s tím

> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

**Vzniklo:** 2. 10. 2026, 06:25 UTC · **Zpracoval:** session `7cd67c66` (druhé kolo analýzy)
**Metoda:** dekomprimované logy obou session (`7cd67c66` = analýza, `7db45275` = jazyk
v kódu) → časová osa 148 zápisů → kontrola, co které session zapsala a co po kom zůstalo.

**Použité nástroje** (nové, v `_analyza\`):
`hl2-rozbal-session2.mjs` (zstd s 1081 rámci), `hl2-co-delala.py`,
`hl2-zapisy-session.py`, `hl2-soubeh.py`, `hl2-casova-osa.py`, `hl2-nic-nezmizelo.py`.

---

## 0. Závěr především: nic se neztratilo, ale tři věci je potřeba dodělat

**Co se NEZTRATILO:** obě session pracovaly na stejných souborech a **obě práce
v nich zůstala**. Ověřeno dvěma nezávislými způsoby:
- `hl2-soubeh.py`: u `HANDOFF.md`, `AGENTS.md` i `kontrola-diakritiky.py` se
  potkaly obě session — **ale všechny zápisy kromě dvou jsou `edit`** (cílená
  náhrada), ne `write` celého souboru. Riziko přepsání tedy bylo nízké.
- `hl2-nic-nezmizelo.py`: **žádný klíčový bod, který byl někdy zapsán, teď nechybí.**

**A jedna věc, kterou je potřeba říct rovnou:** druhá session **už mou práci
zkontrolovala a opravila** — v 08:00–08:10 doplnila §8.2, §8.3, §8.6 a **opravila
moje číslo 2 014 → 2 002**. Níž je seznam toho, co **zbývá**, ne toho, co udělala.

---

## 1. `DEPLOY-VYLEPSENI.md` — živý dokument, o kterém žádný handoff neví

**Naměřeno:** soubor existuje (7 719 B, 1. 10. 2026 13:25), tvrdí
*„připraveno k nasazení, nic není nasazené"* a je to **rozcestník** k 11 opatřením
s vyčíslenou úsporou (kumulativní cíl **$62,22 → $13,34, −79 %**).

**Proč to proklouzlo:** není zmíněný v `AGENTS.md`, v `HANDOFF.md` **ani**
v `OTEVRENA-TEMATA.md` (naměřeno: `0×` výskyt řetězce `DEPLOY-VYLEPSENI`).
Témata, která popisuje, v ledgeru **jsou** (`ast-grep` 3×, `naklad-indikator` 1×,
`ZADANI-CREATOR` 1×) — ale **nikde není odkaz na tenhle rozcestník**, takže
nová session se k němu nedostane.

**Na co odkazuje (vše ověřeno, že existuje):** `ANALYZA-EFEKTIVITY-DSH.md`,
`ANALYZA-VYVOJ-APLIKACI-A-HER.md`, `RESEARCH-public-repos.md`,
`ZADANI-CREATOR-INDIKATORY.md`, `dsh-plugins\naklad-indikator\`,
`dsh-plugins\temata\kontrola-temat.mjs`, `dsh-plugins\temata\SKILL.md`.

**Co je potřeba:** přidat `DEPLOY-VYLEPSENI.md` do `AGENTS.md` (§ „Kam pro co")
a odkázat na něj z `OTEVRENA-TEMATA.md`. **Nic víc** — obsah je v pořádku,
jen je nedohledatelný.

---

## 2. Tři dokumenty v rootu bez jediné zmínky

| Soubor | Velikost | Co to je | Verdikt |
|---|---|---|---|
| `DEPLOY-VYLEPSENI.md` | 7,7 kB | viz §1 | **živý, patří do rejstříku** |
| `sdxl-comfyui-2d-game-assets-research.md` | 45,6 kB | rešerše lokálního generování 2D grafiky (SDXL + ComfyUI, RX 6600) | **patří do rejstříku** — váže se na skill `imagegen-local` |
| `token-saving-tools-dsh-evaluation.md` | 53,9 kB | hodnocení 10 token-šetřících nástrojů vůči DSH | **patří do rejstříku** — váže se na `PLAN-*` a nákladová rozhodnutí |

**Ověřeno, že nejsou rozbité:** všechny tři jsou **validní UTF-8** a mají
**0 rozbitých vzorů**. To, že se v konzoli zobrazují s rozsypanou diakritikou,
je **past `Get-Content`** (čte jako cp1252) — **není to vada souborů**.
*(Kdyby to někdo „opravoval", přepíše správný soubor.)*

---

## 3. `HANDOFF.md` psaly dvě session — a je to v něm vidět, ale ne úplně

**Naměřeno (`hl2-casova-osa.py`):** `HANDOFF.md` zapsán **25×**, z toho
**2× `write` celého souboru** (oba mou session) a **23× `edit`**.
Časová osa ukazuje skutečné prokládání:

```
07:59:44  7cd67c66  write  HANDOFF.md     <- moje verze
08:00:22  7cd67c66  write  HANDOFF.md     <- moje opravená verze
08:00:25  7db45275  edit   HANDOFF.md     <- jejich §8.2 (mandát)
08:00:33  7db45275  edit   HANDOFF.md     <- oprava Z1-Z6 -> Z1-Z8
08:01:38  7db45275  edit   HANDOFF.md     <- přidán odstavec o souběhu
08:01:46  7db45275  edit   HANDOFF.md     <- OPRAVA 2 014 -> 2 002
08:02:23  7db45275  edit   HANDOFF.md     <- 4. vlastní omyl
08:10:33  7db45275  edit   HANDOFF.md     <- §8.6 (jak dovolat session)
```

**Dobrá zpráva:** druhá session to **sama zdokumentovala** („⚠ TENTO HANDOFF
PSALY DVĚ SESSION SOUČASNĚ") a **opravila mé číslo** 2 014 → 2 002 (§10).
**Ověřeno živě:** skener skutečně vrací **161 souborů, 2 002 nálezů, 0 nepokrytých**.
Můj §10 měl starší číslo; **jejich oprava je správná**.

**Co zbývá:** v §9 („Vlastní omyly této session") je **4. řádek od nich**, ale
tabulka je **společná pro obě session** a není na první pohled jasné, které
omyly jsou čí. Doporučuji do záhlaví §9 doplnit autorství.

---

## 4. `kontrola-diakritiky.py` — soubor, který psaly dvě session proti sobě

**Naměřeno:** `2× edit`, `7cd67c66` v **08:00:44**, `7db45275` v **08:01:17**.
Obě přidávaly do **stejného seznamu `SOUBORY`** — a **obě úpravy tam jsou**:

| Kdo | Co přidal |
|---|---|
| já (`7cd67c66`) | `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md`, `HLOUBKOVA-MERENI-3.md`, `IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md` |
| oni (`7db45275`) | `IMPLEMENTACE-HRANICE-JAZYKA.md` |

**Ověřeno diffem i spuštěním:** brána teď kontroluje **6 nových dokumentů**
a hlásí `VŠE OK`. **Nic se nepřepsalo.**

⚠ **Ale je to náhoda, ne konstrukce.** Kdyby obě session sáhly na stejný řádek
seznamu, jeden zápis by druhý přepsal a **nikdo by si toho nevšiml** — brána by
dál hlásila zelenou. **Tohle je samo o sobě argument pro nápravu S27**
(kontrolovat složku, ne ruční seznam): čím víc session pracuje současně, tím
větší je šance, že se seznam rozpadne.

---

## 5. Co druhá session zapsala a co je potřeba promítnout jinam

Druhá session zapsala **§8.2 mandát uživatele** („další session smí měnit kód
v obou repech") a **§8.3 pořadí Z1–Z8 vůči A1–A4**. Obojí je v `HANDOFF.md`.
**Co ale chybí:** tenhle mandát **zpochybňuje formulaci v zadání druhého kola**
(`ANALYZA-HLOUBKOVA-2-ZADANI.md`, „Neměnit kód orchestra ani her") a **není
promítnutý do `IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md`** — ten pořád začíná
jako zadání pro session, která „kód měnit nesmí".

**Co je potřeba:** do `IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md` doplnit odkaz na
`HANDOFF.md` §8.2, aby se příští session neřídila zrušeným zákazem.

---

## 6. Kdyby souběh dopadl zle — co jsem ověřoval a našel

Aby to nebyl dojem, hledal jsem **konkrétní stopy ztráty**, ne „snad to je OK":

| Co jsem hledal | Nástroj | Výsledek |
|---|---|---|
| Soubory psané dvěma session | `hl2-soubeh.py` | **3** (`HANDOFF.md`, `AGENTS.md`, `kontrola-diakritiky.py`) |
| Ztráta celého souboru (`write` po `edit`) | `hl2-soubeh.py` | **jen `HANDOFF.md`** — a tam zápis odmítl systém |
| Klíčové body, které zmizely | `hl2-nic-nezmizelo.py` | **0** (56 kontrolovaných bodů) |
| Dokumenty bez zmínky v rejstříku | Python walk | **4** (3 živé + sám rejstřík) |
| Rozbité kódování v nových dokumentech | kontrola + sabotáž | **0** |

**A jeden falešný poplach, který jsem si sám vyrobil:** `hl2-nic-nezmizelo.py`
ohlásil, že v `HANDOFF.md` chybí `2 014`. **Nebyla to ztráta** — druhá session
to číslo **správně opravila na 2 002**. Kdybych zprávě uvěřil bez ověření,
šel bych „vracet" správnou opravu. **Naměřeno spuštěním skeneru: 2 002.**

---

## 7. Hotový seznam pro předání

**Přidat k ostatním věcem v plánu:**

1. **`DEPLOY-VYLEPSENI.md` do rejstříku** — `AGENTS.md` §„Kam pro co"
   + odkaz z `OTEVRENA-TEMATA.md`. *(Živý dokument, 11 opatření, nikde není.)*
2. **`sdxl-comfyui-2d-game-assets-research.md` a
   `token-saving-tools-dsh-evaluation.md` do rejstříku** — dva velké dokumenty
   bez jediné zmínky.
3. **Mandát z `HANDOFF.md` §8.2 promítnout do
   `IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md`** — jinak se příští session bude
   řídit zákazem, který už neplatí.
4. **§9 v `HANDOFF.md` označit autorství omylů** (společná tabulka dvou session).
5. **S27 řešit jako reálné riziko souběhu** — čím víc session, tím větší šance,
   že se ruční seznam v bráně rozpadne tiše. *(Dnes se to **těsně** nestalo.)*

**Co naopak NENÍ potřeba:** nic se nevrací, nic se nedoplňuje zpětně —
`kontrola-diakritiky.py` má obě úpravy, `HANDOFF.md` má obě práce,
`AGENTS.md` má obě tabulky. **Ověřeno, ne odhadnuto.**
