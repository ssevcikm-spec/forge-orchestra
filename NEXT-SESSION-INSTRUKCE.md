# ZADÁNÍ PRO DALŠÍ SESSION — rozhodnout tři otevřené věci a vrátit se k práci na projektu

**Zkontrolováno při:** `19a2195` (orchestra — **commit, na kterém měřila P19**, a zároveň její rodič) · hra `44dd454` · **6. 10. 2026, 10:1x UTC**
**Stav obou repů při psaní:** `forge-orchestra` = `19a2195`, `origin/main` = **`19a2195`** (push P19 proběhl v **§A**) — po commitu P19 se `HEAD` posune o **1** · `uo-shadows` = `44dd454`, `origin/main` **shodná**, strom **čistý**
**Ověřeno živě:** `git ls-remote origin refs/heads/main` — orchestra **`19a2195`**, hra **`44dd454`** (měřeno před commitem P19; po něm viz „přibylo commitů" níž)
**GIT (živě, při předání):** `HEAD` orchestry je **`19a2195`** + **1 commit P19** (záznamy + doklady `p19-*` + opravené brány) — **pushnutý**, takže `origin/main..HEAD` je **0** (měřeno po pushi)

> **⚠ P19 JE COMMITNUTÁ I PUSHNUTÁ — a `zadani-kontrola.py` proto SPRÁVNĚ VARUJE.**
> Uživatel 6. 10. 2026 rozhodl **„commitnout i pushnout"**. Záznamy
> (`HANDOFF.md` **§37** + **§8y** + **§2.10**, `KRONIKA-PROJEKTU.md` řádek **33**,
> §2.13 a §3), doklady **`_analyza/p19-*`**, opravené brány (**`n32`**, **`h79`**,
> **`g3`**) i **tohle zadání** jsou v **jednom commitu P19** nad `19a2195`.
> **Tím vzniká `přibylo commitů: 1`** — a to **není vada zadání ani session**:
> je to **vlastnost odkazu na vlastní commit** (SHA commitu závisí na jeho obsahu).
> `zadani-kontrola.py` to hlásí jako **varování** a **právě to má dělat** — nutí
> příští session **přeměřit stav živě** místo věřit hlavičce (nález **NA31**).

> **⚠ PROČ JE V HLAVIČCE `19a2195`, A NE COMMIT P19 — a je to ZÁMĚR.**
> `19a2195` je **commit, na kterém P19 SKUTEČNĚ MĚŘILA** (a je to i **rodič**
> commitu P19), takže je to **správná kotva měření**. Kdyby tu stálo SHA commitu
> P19, odkazovalo by dokument na commit, jehož obsah **závisí na tomhle textu**.
> **Hlavička se NEOPRAVUJE na dnešek** — pak by přestala být záznamem o tom,
> **proti čemu se měřilo** (nález **NA31**).

**Co je v `HANDOFF.md`:** **§37 = P19** (Úkoly A–E + nálezy **H97–H100** + rozhodnutí + omyly **186–194** v **§8y**) · **§2.10 = stav otevřených bodů po P19** · §36 = P18 · §35 = P17 · **§2 = co je otevřené**
**Co je v `KRONIKA-PROJEKTU.md`:** řádek **33** (P19) · nálezy **H97–H100** v **§2.13** · blok omylů **8y** · **souhrn: 25 bloků, 32 sessions, 189 omylů (163 = 86 %), 54 nálezů**
**Co tenhle dokument JE:** **zadání pro ROZHODOVACÍ session P20** — P19 **rozhodla a provedla** všechno povinné (push, H93, H94, `g3`, záznamy). **Technický dluh z ověřovacích sessions je tím vyčerpaný**; zbývají **tři rozhodnutí** a pak je na řadě **práce na projektu** (hra, conductor), ne na měřidlech.
**Datum spotřeby:** údaje o stavu níž jsou **k 6. 10. 2026, 10:1x UTC**; co je starší, je v `HANDOFF.md` **§37** a je to **záznam**, ne stav.

> **⚠ PRVNÍ VĚC, KTEROU UDĚLEJ:** `git status --porcelain` a **`git fetch`**
> v obou repech — a **ověř `origin/main..HEAD` ŽIVĚ** (`git ls-remote`), ne
> podle tohohle textu. Uživatel mohl mezitím pushnout, nebo se stav změnil.
>
> **⚠ A DRUHÁ:** **`git.cmd` ŽERE `^`** — `git show <sha>^` tiše vrátí stav **PO**
> commitu. Používej **`~1`**, nebo **`git.exe`**. Naměřeno P17: `git.cmd … 'ce49234^'`
> → **`ce49234`** (sám sebe), `~1` → `c620a06`. Detail: skill `dsh-prostredi` **§5c**.
>
> **⚠ A TŘETÍ (nově z P19):** **`Set-Content -Encoding utf8` v PowerShellu přidá
> do `.py` BOM** → soubor přestane být zkompilovatelný a **NA32 ho právem vykáže**
> (omyl **189**). Kód edituj **`edit`/`write` toolem**, ne `Set-Content`; a po
> zápisu zkontroluj **první tři bajty** (`.py` **NESMÍ** mít BOM, `.ps1` **MUSÍ**).

---

## 0. Co P19 naměřila a co je HOTOVÉ (neopakuj to znovu)

| # | Co P19 udělala | Výsledek (doklad v `_analyza/`) |
|---|---|---|
| **A** | **PUSH** (rozhodl uživatel) | `ce49234..19a2195` — **6 commitů** (P17, P18, P18b–P18e), `exit 0`; `ls-remote` = `HEAD`, `origin/main..HEAD` = **0**. **Build na správném commitu:** žádný workflow se nespouští a je to **dokázané** (`deploy.yml` filtruje `conductor/**`, diff má 0 souborů v `conductor/`, + pozitivní kontrola API). **Artefakt:** orchestra **Pages nemá** (HTTP 404), hra je `44dd454` = commit stavby `release.yml #78 completed/success`, `last-modified` **`21:38:16 GMT`** (nezměněno — do hry se nepushovalo) — `p19-a-push-overeni.mjs` (**15/0**) |
| **B** | **H93** — a co se u toho našlo | NA32 počítal **178 živých**, z toho **2** zmrazené snapshoty a **19** pracovních kopií. **Opraveno v OBOU branách** (NA32 i H79): kategorie se **vylučují** a **každá má vlastní čítač**; nové souhrny `158 živých / 2 snapshot-* / 19 *-scratch`. Doklady **29/0** a **23/0** (mutace v kopii bránu **nezčervení**, v živém stromě **zčervení**) — `p19-b-kontroly.py`, `p19-b2-kontroly-h79.py` |
| **C** | **H94** — a P18 to měřila neúplně | Živých podpisů je **5** (ne 4): `is not recognized` **PowerShell i cmd vydávají**. Pro `g3` je ale mrtvý (`g3` **shell nepoužívá**) → seznam **zúžen na 4 živé**, 4 odebrané **pojmenované v komentáři**. Invariant: **v seznamu není mrtvý podpis** — `p19-c-h94-podpisy.py` (**25/0**) |
| **D** | **`g3` je NYNÍ BRÁNA — ale soudí jen sebe** | `exit 1`, když brána **nezačala** nebo **běžela bez čítače mimo `OCEKAVANE_BEZ_CITACE`**; `exit 2` při **nulovém počtu bran**. **O červených nerozhoduje** — jen je vypíše jako „k rozhodnutí". Důkaz **16/0** — `p19-d-kontroly.py` |
| **E** | **Brány a záznamy** | `g3` **37 bran, 1 nenulový** (`zadání kontrola` — **očekávaný**), 0 nezačatých, **`exit 0`** · `validate-all` **✓ VŠE V POŘÁDKU** · `KRONIKA SEDÍ` · handoff **83/83** · inventář přegenerován **jako poslední krok** |
| **nálezy** | **H97** (H93 měl vyvrácená čísla), **H98** (kopie jako živý kód v obou branách), **H99** (BOM: spustit vs zkompilovat), **H100** (§36.8 tvrdil 0 nenulových exitů, doklad má 1) | `HANDOFF.md` §37.6, `KRONIKA-PROJEKTU.md` §2.13 |

---

## 1. Cíl (jedna věta)

**Rozhodnout tři zbývající věci z P19 (verdikt `g3` nad červenými branami, BOM
v `.py`, zařazení opakovatelných ověřovacích skriptů do `g3`) — a pak se vrátit
k práci na projektu místo k měřidlům.**

---

## 2. Úkoly (v tomto pořadí)

### 2.1 Úkol A — verdikt `g3` nad ČERVENÝMI branami (nález NA23b)

**Stav:** `g3` od P19 **spadne jen za sebe** (nezačatá brána / brána bez čítače
mimo deklarovaný stav) a **o červených nerozhoduje** — jen je vypíše jako
„k rozhodnutí". **Při měření P19 byl nenulový PRÁVĚ JEDEN:** `zadání kontrola`
(`exit=1`, protože zadání bylo kotvené na commitu měření P18 — NA31). **Po
přepsání zadání (kotva = živý `HEAD`) je nenulových `0`** — a **po commitu P20
bude zase `1`**, protože si zadání **schválně** drží kotvu měření. To je
**očekávaný případ**, ne vada.

1. **Přeměř, které brány končí nenulově** a **proč** (`_analyza/_g3-*.txt` nebo
   nový běh) — a **u každé napiš, jestli je to stav, nebo vada**.
2. **Rozhodni:** má `g3` soudit i červené? Když ano, musí vzniknout
   **`OCEKAVANE_NENULOVE`** (deklarovaný seznam očekávaných nenulových exitů —
   dnes `{"zadání kontrola"}`), a `g3` musí **umět spadnout i na nečekaném**.
3. **Když zavedeš nový `sys.exit`, DOLOŽ, že umí spadnout** — vzorem je
   `_analyza/p19-d-kontroly.py` (fixtury, kopie živého `g3`, žádná mutace živého
   souboru). **A dolož i opak:** že **očekávaný** nenulový exit `g3` **neshodí**
   (jinak by brána padala po každém commitu).

### 2.2 Úkol B — BOM v `.py`: vada, nebo ne? (nález H99)

**Stav:** `python soubor.py` s BOM **funguje**, ale `compile()` ho **odmítne** →
**NA32 i H79** takový soubor hlásí jako vadu živého stromu. Dnes **žádný živý
`.py` s BOM není**.

1. **Přeměř to** (fixtura s BOM: spuštění vs `compile()` vs obě brány).
2. **Rozhodni**, co je správně, a **zapiš to jako pravidlo**:
   * buď je BOM v `.py` **zakázaný** (pak je dnešní chování obou bran správné
     a patří to do `AGENTS.md` jako konvence),
   * nebo je **povolený** (pak ho obě brány musí přestat hlásit — a **obě
     NARÁZ**, protože dvě brány, které se o témž souboru rozcházejí, jsou dražší
     než ta nepřesnost).
3. **Ať rozhodneš jakkoli:** dolož to **mutací oběma směry** (soubor s BOM
   v živém stromě vs. bez BOM) a **nezapomeň, že `.ps1` BOM MÍT MÁ** — pravidlo
   se týká **`.py`**.

### 2.3 Úkol C — mají opakovatelné ověřovací skripty vstoupit do `g3`?

**Stav:** doklady **`ov-*` (P18)** i **`p19-*` (P19)** zůstaly **mimo `g3`**
(rozhodnutí uživatele u P18). **Opakovatelné** z nich jsou:
`ov-b1-compile.py`, `ov-e-h79-mez.py`, `ov-g-h92-sken.py`, `ov-g-neovereno.py`,
`p19-b-kontroly.py`, `p19-b2-kontroly-h79.py`, `p19-c-h94-podpisy.py`,
`p19-d-kontroly.py`. **Jednorázové/stavové** (`ov-a` závisí na nasazení,
`ov-f` je diagnostika, `p19-a`, `p19-b-h93-snapshot.py`) tam **nepatří**.

1. **U každého kandidáta změř, jak dlouho běží** a **co měří** (stav? mutaci? obojí?).
2. **Rozhodni a zapiš:** které se zařazují (a s jakým čítačem do `BRANY`), které
   zůstávají doklady a **proč**. **Brána bez čítače = `g3` dnes spadne** — takže
   každý zařazený skript musí **vykazovat číslo**.
3. **Po každé změně `BRANY` spusť `g3`** (a ověř, že nová brána **něco otevřela**).

### 2.4 Úkol D — ZÁZNAMY A OVĚŘENÍ STAVU (povinné na konci)

1. **Přepiš `NEXT-SESSION-INSTRUKCE.md`** pro další session.
2. **Zapiš výsledky a omyly do `HANDOFF.md`** (nový oddíl; **jen přidávej**).
3. **Doplň řádek do `KRONIKA-PROJEKTU.md`** (tabulka sessions + tabulka omylů +
   její `celkem` — **všechny tři**, jinak se součet rozejde).
4. **Ověř, že nezůstalo `NEOVĚŘENO`** — vlastním skriptem, ne grepem.
5. **Přegeneruj inventář** a spusť `g3` **a pak** `validate-all`
   (**NE SOUČASNĚ** — oba sahají na `_inventar.json`).
   **⚠ Inventář přegeneruj jako POSLEDNÍ krok** (jeho otisk počítá **i `.md`**,
   takže každý zápis do dokumentace ho invaliduje).
6. **Do chatu vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.**

### 2.5 Úkol E — až budou A–D hotové: **práce na projektu, ne na měřidlech**

**P19 dočerpala frontu technického dluhu z ověřovacích sessions.**
Další session by se měla vrátit k **věcné práci** — nabídka z `HANDOFF.md` **§2**
(a je na uživateli, kterou vybere):

* **hra:** pozice hráče ve smlouvě (`save.gd` ji dnes přepíše spawnem — §2.9 B),
  DAG u `entity.player`, další granule z roadmapy;
* **conductor:** **O3** (opravit vady conductoru a nasadit), **O10**, **N0.2**
  (brána na závislosti bran), **N0.3** (stav CI cílové hry v `/health`);
* **orchestra:** otevřené otázky **O5–O8** z `PLAN-ROZVOJ-ORCHESTRA.md` §6.

---

## 3. „Hotovo znamená" pro tuhle session

| # | Podmínka | Jak se to pozná |
|---|---|---|
| 1 | **NA23b rozhodnutý** | buď `g3` soudí i červené (s `OCEKAVANE_NENULOVE` a **důkazem, že umí spadnout i nezhavarovat na očekávaném**), nebo je zapsané, že nesoudí a proč |
| 2 | **BOM rozhodnutý** | pravidlo je **v `AGENTS.md`** a **obě brány se chovají shodně** (doloženo mutací) |
| 3 | **Zařazení skriptů rozhodnuté** | každý kandidát má verdikt (do `g3` / zůstává doklad) **a důvod**; brány v `g3` mají **čítač** |
| 4 | **Záznamy sedí** | `kronika-kontrola.py` → **`KRONIKA SEDÍ`**; `handoff-kontrola-uplnost.py` → **83/83** |
| 5 | **Brány zelené** | `g3` → **`exit 0`** (a výslovně: co je nenulové a proč); `validate-all` → **`✓ VŠE V POŘÁDKU`** |
| 6 | **Žádné `NEOVĚŘENO`** | ověřeno skriptem, ne dojmem |
| 7 | V chatu je **prompt pro uživatele** i **stavový řádek** | ke zkopírování |

---

## 4. Co NEDĚLAT

- **Nepushovat bez vyžádání** — P19 pushla **na výslovné rozhodnutí uživatele**;
  další push je **zase rozhodnutí**, ne automatika.
- **Nepřepisovat `HANDOFF.md` ani `KRONIKU`** — jen **přidávat**; historická čísla
  se **nechávají citovaná** (a staví se **vedle** nich dnešní). **Konkrétně:**
  řádky **H93/H94** v kronize **§2.12** zůstávají ve znění P18 (i s čísly, která
  P19 vyvrátila) — oprava je ve **§2.13**.
- **Nemazat `_analyza/p16*`, `p17*`, `ov-*` ani `p19-*`** — jsou to **doklady**.
- **Nepřesouvat nic zpátky na `C:`**; `_archiv` a zálohu v
  `C:\Users\Ssevc\Local-Deepseek\_zalohy\` **nemařit** (jsou to cesty zpět).
- **Nespouštět `g3` a `validate-all` SOUČASNĚ** — oba sahají na `_inventar.json`.
- **⚠ Needitovat `.py` přes `Set-Content`** (přidá BOM — omyl **189**); a **nikdy
  nepsat české uvozovky do zdrojáků** (`„…“` v řetězci je `SyntaxError`).
  Po každém zápisu `.py` spusť `ast.parse` **a zkontroluj první tři bajty**.
- **Nepoužívat `python - <<'PY'`** (heredoc v PowerShellu **neexistuje**) ani
  `python -c` s regexy/`$()` — **piš skript do souboru** (`dsh-prostredi` §3d/§3e/§3f).
- **Nespoléhat na to, „co P19 tvrdí"** — **každé tvrzení přeměř**; autor není
  nezávislý reviewer. **A platí to i na tenhle dokument.** P19 přitom **dvakrát
  vyvrátila tvrzení P18 jejím vlastním uloženým výstupem** (H97, H100) — což je
  přesně to, co má příští session dělat taky.

---

## 5. Naměřená východiska (aby se nemusela měřit znovu)

```
# hlavička a stav (6. 10. 2026, 10:1x UTC — PŘED commitem P19)
#   ⚠ hodnoty níž jsou STAV V ČASE MĚŘENÍ; po commitu P19 se HEAD posunul o 1.
git -C E:\Workspaces\forge-orchestra rev-parse --short HEAD        -> 19a2195  (kotva měření P19)
git -C E:\Workspaces\forge-orchestra rev-parse --short origin/main -> 19a2195  (po pushi P19)
git -C E:\Workspaces\forge-orchestra rev-list --count origin/main..HEAD -> 0   (PŘED commitem P19)  [po něm: 1]
git -C E:\Workspaces\forge-orchestra status --porcelain (radku)    -> 10  (3 opravene brany + 7 dokladu p19-*)  [po commitu: 0]
git -C E:\Workspaces\uo-shadows      rev-parse --short HEAD        -> 44dd454
git -C E:\Workspaces\uo-shadows      rev-list --count origin/main..HEAD -> 0   (v sync)
git ls-remote (orchestra) -> 19a21957158f8269e5d2f7f7e079c56789f5914f   (git ls-remote (hra) -> 44dd4544…)

# P19: co se měřilo a jak to vyšlo  (doklady: _analyza/p19-*)
node   _analyza\p19-a-push-overeni.mjs      -> 15 kontrol, 0 chyb (push dorazil; build se nespouští; artefakt hry neovlivněn)
python _analyza\p19-b-h93-snapshot.py       -> 178 živých = 157 živý kód + 2 snapshot-* + 19 *-scratch (soubor po souboru)
python _analyza\p19-b-kontroly.py           -> 29 kontrol, 0 chyb  (NA32: mutant v kopii nezčervení, v živém zčervení)
python _analyza\p19-b2-kontroly-h79.py      -> 23 kontrol, 0 chyb  (H79: totéž, vada = neplatná escape sekvence)
python _analyza\p19-c-h94-podpisy.py        -> 25 kontrol, 0 chyb  (5 živých podpisů obecně, 4 pro g3; M1 změní, M2/M3 ne)
python _analyza\p19-d-kontroly.py           -> 16 kontrol, 0 chyb  (g3 umí spadnout: 0/1/2 + červená s čítačem = 0)
python _analyza\n32-kompilovatelnost.py     -> ZMERENO: 158 souboru, 0 nekompilovatelnych, 260 (_archiv), 2 (snapshot-*), 19 (*-scratch)
python _analyza\h79-escape-sken.py          -> ZMERENO: 0 neplatnych v 158 zivych (… snapshot-* 2/0, *-scratch 19/0)
python _analyza\g3-brany.py                 -> 37 bran, 1 nenulovy (zadani kontrola — ocekavany), 0 nezacatych, exit 0
node   tools\validate-all.mjs               -> VSE V PORADKU, exit 0
python _analyza\kronika-kontrola.py         -> KRONIKA SEDI (189 omylu / 100 nalezu / 32 sessions)
python _analyza\handoff-kontrola-uplnost.py -> 83/83
python _analyza\zadani-kontrola.py          -> exit 1 s 1 varovanim ("pribylo commitu") — OCEKAVANE (NA31)

# inventar se MUSI pregenerovat po kazde zmene souboru ve stromu (H60/NA1)
#   a jako POSLEDNI krok (otisk pocita i .md):
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json

# ⚠ IZOLACE (z P18, plati dal): `git worktree` MUSÍ ležet uvnitř `E:\Workspaces`
# a MUSÍ mít junction `uo-shadows` na živou hru; a NESMÍ ležet v měřeném stromě.
# ⚠ A P19 k tomu přidala: GENEROVANÝ HARNESS si nesmí odvozovat cesty z umístění
# — v podadresáři se `WS = parents[1]` posune a výsledky vyjdou PRÁZDNÉ (omyl 191).
#   Do kopie se vkládá ABSOLUTNÍ root (viz `p19-c-h94-podpisy.py` a `p19-d-kontroly.py`).
```

**Uložené doklady (ne rekonstrukce):** `_analyza/p19-a-push-overeni.mjs`,
`p19-a-push-vysledky.json`, `p19-b-h93-snapshot.py`, `p19-b-kontroly.py`,
`p19-b2-kontroly-h79.py`, `p19-c-h94-podpisy.py`, `p19-d-kontroly.py`,
`p19-kronika-typy.py`
(+ gitignorované výstupy `p19-*-vystup.txt`) a **`p19-scratch/`** (gitignorovaný:
push skript a fixtury — **není v repu**).

---

## 6. Prompt pro uživatele (zkopíruj do nového chatu)

```text
Jsi ROZHODOVACÍ session. Repa jsou na E:
  orchestra = E:\Workspaces\forge-orchestra
  hra       = E:\Workspaces\uo-shadows

Zadání pro tebe je v E:\Workspaces\forge-orchestra\NEXT-SESSION-INSTRUKCE.md
— přečti ho CELÝ.

Kontext: P19 (HANDOFF.md §37) dokončila frontu technického dluhu. Pushnuto
(6 commitů P17+P18, ověřeno třemi kroky: orchestra žádný workflow nespouští —
conductor/** se nezměnil — a hra má artefakt z 44dd454 neovlivněný).
H93 opraveno V OBOU branách: NA32 i H79 teď nepočítají snapshot-* ani *-scratch
jako živý kód a každá kategorie má vlastní čítač (dřív 178 "živých", z toho
2 zmrazené snapshoty a 19 pracovních kopií, 13 z nich bajt na bajt shodných
s živými soubory hry). H94 zúženo na 4 ŽIVÉ podpisy (is not recognized je živý
obecně, ale ne pro g3 — g3 shell nepoužívá). g3 je NYNÍ BRÁNA: spadne, když
brána nezačala nebo běžela bez čítače mimo deklarovaný stav, a o červených
NEROZHODUJE (dnes je legitimně nenulový jeden: zadání kontrola).
Navíc P19 vyvrátila DVĚ tvrzení P18 jejím vlastním uloženým výstupem: H97
(H93 měl rozdíl 2, ne 14) a H100 (§36.8 tvrdil 0 nenulových exitů, doklad má 1).

Pořadí: A (verdikt g3 nad červenými / NA23b) → B (BOM v .py, H99) →
C (mají opakovatelné ověřovací skripty do g3?) → D (záznamy a ověření stavu) →
E (návrat k věcné práci: hra / conductor).

Než začneš: `git status --porcelain` a `git fetch` v obou repech, a NEpoužívej
`git show <sha>^` — git.cmd žere `^` (H89), používej `~1`. A needituj .py přes
Set-Content (přidá BOM → omyl 189); kontroluj první tři bajty.

Nepřepisuj HANDOFF.md ani KRONIKU (jen přidávej), nemaž _analyza/p16*, p17*,
ov-* ani p19-* (jsou to doklady), nepřesouvej nic zpátky na C:, nepushuj bez
vyžádání. Po každé změně souboru ve stromě přegeneruj inventář (NA1/H60) —
a naposledy až jako POSLEDNÍ krok (otisk počítá i .md).

Na konci povinně: přepiš NEXT-SESSION-INSTRUKCE.md pro další session, zapiš
výsledky a omyly do HANDOFF.md, doplň řádek do KRONIKA-PROJEKTU.md (včetně
souhrnu celkem), rozhodni nálezy ve stavu NEOVĚŘENO (ověř, že žádné nejsou),
a do chatu vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.
```
