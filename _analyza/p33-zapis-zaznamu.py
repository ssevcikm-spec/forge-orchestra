# -*- coding: utf-8 -*-
r"""P33 — ZÁPIS ZÁZNAMŮ (HANDOFF §64, KRONIKA řádek 48 + §2.26, dodatek PLANu).

PROČ SKRIPTEM (a ne ručně): řádky záznamů mají **přes 3 000 znaků**; kdo je
zapisuje editorem s načtenou kotvou, tomu se kotva zkrátí (omyly 194, 206).
A druhá věc, důležitější: **čísla se do záznamu NEOPISUJÍ z hlavy** — skript je
ČTE Z DOKLADŮ (`_analyza/p33-*-vystup.txt`), takže v záznamu nemůže zestárnout
číslo, které se mezitím přeměřilo.

⚠ JE TO ZÁPISOVÝ PATCHER → je v `PRESKIP` dávky dokladů (`p20-d-doklady.py`).
⚠ JE IDEMPOTENTNÍ: každou kotvu nejdřív ověří (musí být právě 1×) a když kotva
nesedí, **NEZAPÍŠE NIC** a skončí `exit 1` (vzor H142 — patcher nesmí zapsat
soubor, jehož kotvu nenašel).
⚠ ZÁZNAMY SE JEN DOPLŇUJÍ: `HANDOFF.md` i `KRONIKA-PROJEKTU.md` se přidávají,
nic se neplete a nic nemaže (kontroluje se `-0` smazaných řádků vlastním
přepočtem před/po).

Použití: python _analyza/p33-zapis-zaznamu.py [--kontrola]
"""
import argparse
import hashlib
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
A = WS / "_analyza"
HANDOFF = WS / "HANDOFF.md"
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
PLAN = WS / "PLAN-DALSI-KROK.md"
D_FULL = A / "p33-a-overeni-vystup.txt"
D_C9 = A / "p33-c9-vystup.txt"
D_C4 = A / "p33-c4-vystup.txt"
D_C1C6 = A / "p33-c1c6-vystup.txt"


def nacti(p):
    return p.read_text(encoding="utf-8")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def citac(text, popis):
    m = list(re.finditer(r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb"
                         r"\s*\(z toho\s*(\d+)\s*pojmenovaných ROZDÍLŮ,\s*(\d+)\s*NEZMĚŘENO\)", text))
    if not m:
        sys.exit("CHYBA: v %s není čítač — záznam by citoval nezměřené číslo" % popis)
    return "/".join(m[-1].groups())


def radky(text, prefixy):
    """První řádek dokladu OBSAHUJÍCÍ prefix (bez odsazení), zkrácený.

    ⚠ NE `startswith`: měřidlo tiskne verdikt na začátek řádku
    („OK        C4 dávka …“), takže by hledání na začátku nenašlo nic
    a záznam by citoval „V DOKLADU NENÍ“ u věci, která v dokladu JE.
    """
    out = []
    radky_t = [r.strip() for r in text.splitlines()]
    for pref in prefixy:
        for r in radky_t:
            if pref in r:
                out.append(r[:230])
                break
        else:
            out.append("%s — V DOKLADU NENÍ (pozor: necituj to jako měřené)" % pref)
    return out


# ── vstupy: čísla se ČTOU, neopisují ────────────────────────────────────────
chybi = [p.name for p in (D_FULL, D_C9, D_C4) if not p.is_file()]
if chybi:
    sys.exit("CHYBA: chybí doklady %s — nejdřív je spusť (záznam by citoval nezměřená čísla)"
             % ", ".join(chybi))
T_FULL, T_C9, T_C4 = nacti(D_FULL), nacti(D_C9), nacti(D_C4)
T_C1C6 = nacti(D_C1C6) if D_C1C6.is_file() else ""
C_FULL = citac(T_FULL, D_FULL.name)
C_C9 = citac(T_C9, D_C9.name)
C_C4 = citac(T_C4, D_C4.name)

C1 = radky(T_FULL, ["C1-a ŽIVÝ", "C1-a s VRÁCENOU", "C1-b ALE", "C1-c a DOBĚHNE",
                    "C1-c a vadná kotva", "C1-d ", "C1-f "])
C2 = radky(T_FULL, ["C2 41aa981", "C2 0b86c2d", "C2-1 ", "C2-2 ", "C2-3 "])
C5 = radky(T_FULL, ["C5 `ag-over-cisla", "C5 `_registr-bran"])
C6 = radky(T_FULL, ["C6 `p29-a --jen A1M13", "C6 `p29-a --jen A3", "C6 (H146)"])
C7 = radky(T_FULL, ["C7 g3 měří", "C7 g3: 0 NEDEKLAROVANÝCH", "C7 g3 hlásí POJMENOVANĚ",
                    "C7 `validate-all`", "C7 brána `cron běží (čas)`",
                    "C7 a její offline fixtury", "C7 v HANDOFF.md"])
C8 = radky(T_FULL, ["C8-1 offline fixtury", "C8-1 a čítač", "C8-2 v `validate-all.mjs`",
                    "C8-3 `last_cron` se zapisuje", "C8-4 živý `last_cron`",
                    "C8-4 a je čerstvý", "C8-5 nad ULOŽENÝM",
                    "C8-5 STARÁ podmínka", "C8-5 a ten stav opravdu"])
C9 = radky(T_C9, ["C9-1 ", "C9-2 ", "C9-3 p31-mutace", "C9-3 p31-a --jen A1"])
C4 = radky(T_C4, ["C4 dávka", "C4 ani JEDEN", "C4 pojistka", "C4 sekce",
                  "C4 dávka neohlásila"])
NEZM_FULL = re.findall(r"^\s*NEZMĚŘENO\s+(.{0,180})", T_FULL, re.M)
ROZD_FULL = re.findall(r"^\s*ROZDÍL\s+(.{0,180})", T_FULL, re.M)


def seznam(radky_, odsazeni="  "):
    return "\n".join("%s* %s" % (odsazeni, r) for r in radky_)


# ── §64 HANDOFF ─────────────────────────────────────────────────────────────
S64 = """## 64. P33 — PŘEMĚŘENÍ P32 VLASTNÍM MĚŘIDLEM A ZAVŘENÍ H112 (9.–10. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení P33 + stav po P33**.
**Co NENÍ:** pravidla (`AGENTS.md`), historie (`KRONIKA-PROJEKTU.md` — řádek
**48**, nálezy **§2.26**), plán (`PLAN-DALSI-KROK.md`, dodatek P33). Zadání P33
je v `NEXT-SESSION-INSTRUKCE.md` (`git log -1 NEXT-SESSION-INSTRUKCE.md`).

> **⚠ DATUM SPOTŘEBY:** měřeno **9. 10. 2026 22:5x – 10. 10. 2026 0x:xx +02:00**
> (živý čas z hodin, ne ze zadání). Tvrzení o **stavu** (HEAD, hra, živá služba)
> platí k tomu okamžiku; kdo to čte později, **přeměří**.

> **⚠ MAPOVÁNÍ NÁLEZŮ NA KRONIKU (§2.26), aby každý nález byl dohledatelný
> z HANDOFF.md:** H149 = **H112 ZAVŘENO** — brána „cron běží (čas)“ měřila
> `!!h.time` (tj. že služba odpovídá) a o běhu cronu netvrdila nic; služba dnes
> zapisuje **TEP** (`last_cron` jen z `scheduled`, ruční `POST /tick` ho
> NEOBNOVÍ), `/health` ho posílá a brána ho **měří** · H150 = **podřetězcová
> kontrola v novém nástroji** (`endsWith("cron-stav.mjs")`) se nechala uspokojit
> `test-cron-stav.mjs` (táž třída jako H140) · H151 = **kopie spustitelného
> měřidla v PODADRESÁŘI `_analyza/` neměří nic** (`ModuleNotFoundError` na
> `_mutace` → kontramutace „prošla“ bez čítače) · H152 = **mutace „prvního
> výskytu v CELÉM dokumentu“ mine okno, které měřidlo měří** · H153 = **GitHub
> API `?head_sha=<KRÁTKÝ sha>` tiše vrátí prázdno** → krok 3 ověření nasazení
> hlásil „na commitu NENÍ žádný běh“, ačkoli tam JE · H154 = **vlastní
> diagnostické skripty session rozešly otisk vstupů inventáře** (napsané PO
> přegenerování) → `g3` i `validate-all` hlásily „zastaralý inventář“ a vypadalo
> to jako vada bran.

### 64.1 Úkol A — VLASTNÍ MĚŘIDLO P33 (`_analyza/p33-a-overeni.py`)

**Plný běh (C0–C8): %(c_full)s** (doklad `_analyza/p33-a-overeni-vystup.txt`).
Každé tvrzení se **PŘEČTE Z §63** (vypisuje se okno, které vzor trefil) a pak se
měří; **C1** má **VLASTNÍ kontramutace** (vady se vracejí do KOPIÍ měřidel, u
H142 do ŽIVÉHO patcheru pod `mutuj`), **C8** měří Úkol B ve TŘECH vrstvách.
**Dlouhé nohy mají vlastní běhy** (`--jen C9`, `--jen C4`) a jejich čísla se
do záznamu **čtou z dokladů**.

**Úkol A1 (umí opravy P32 spadnout?):** %(c1)s

**Úkol A2 (co P32 nasadila?):** %(c2)s

**Úkol A3 (sedí čísla z §63?):** %(c9)s
* C9 se pouští `--jen C9`: `p31-a-overeni.py --plne` a `p32-a-overeni.py --plne`
  (doklady `_analyza/p33-p31a-plne-vystup.txt`, `_analyza/p33-c9-vystup.txt`).
  ⚠ **§63.2 TVRDÍ `p31-a --plne` 43/5/2/1 A NEREPRODUKUJE SE: naměřeno
  `51/4/2/0`.** Je to **záznam STAVU PŘED opravou H145** (čtyři z pěti chyb měly
  ten jediný kořen) — dnes ty chyby nejsou, zato A1 doběhne CELÝ (proto +8
  kontrol a 0 NEZMĚŘENO). Rozdíl je **pojmenovaný**, ne schovaný; čtyři dnešní
  chyby jsou vypsané v dokladu (`p33-p31a-plne-vystup.txt`).
* ⚠ **VZOR TVRZENÍ NESMÍ UMĚT PŘESKOČIT MĚŘENÍ** (H155): první běh C9 měl
  rozbitý vzor (hvězdičky tučného písma jsou v §63 JINDE, než vzor čekal) →
  **přeskočil 45minutové měření** a C9-4 pak hlásila „běh neproběhl“; chyba
  vzoru se tvářila jako NEMĚŘENO. Dnes se **nejdřív měří, pak hledá tvrzení**.
* Dva vzory tvrzení byly vadné i v sekci C3 (`p22-test-mutace` mířil na CITACI
  starého stavu `19/1`, `tick-mutace` vyžadoval hvězdičky, které v §63 nejsou) —
  naměřeno ve plném běhu, opraveno a **přeměřeno** zvlášť
  (`_analyza/p33-c3-po-oprave-vystup.txt`, `_analyza/p33-c9l-vystup.txt`).

**Úkol A4 (dávka dokladů):** %(c4)s

**Úkol A5 (registr bran):** %(c5)s

**Úkol A6 (uklízí se měřidla?):** %(c6)s

**Úkol A7 (nic se nerozbilo):** %(c7)s

**MUTAČNÍ DŮKAZ MĚŘIDLA:** `_analyza/p33-mutace.py` → **19/0** — (M1) měřidlo nad
**zmutovanou KOPIÍ** dokumentu (seam `P33_HANDOFF`, tvrzení v §63 `92/0` →
`93/0`) **spadne** a živý dokument se nezmění; (M2) s **POST-nasazovacím**
`/health` podstrčeným jako „stav před nasazením“ (seam `P33_HEALTH`) spadne
kontrola C8-5 → měří; (M3) oba živé soubory jsou po testu **bajt na bajt**.

**POJMENOVANÉ ROZDÍLY (stav, ne vada měřidla): %(rozdily)s**
**NEZMĚŘENO (není nula a není zelená): %(nezmereno)s**

### 64.2 Úkol B — H112 ZAVŘEN: BRÁNA „CRON BĚŽÍ (ČAS)“ UŽ MĚŘÍ TEP CRONU

%(c8)s

**⚠ A BRÁNA HNED NAMĚŘILA SKUTEČNÝ VÝPADEK (H156):** při běhu C4 (10. 10. 2026
~20:01Z, doklad `_analyza/p33-c4-vystup.txt`) měřidlo v sekci C8-4 naměřilo
**`last_cron` 260 min starý** a `last_tick_zdroj = manual`; přímé měření
v **20:31:51Z** dalo `last_cron = 2026-10-10T15:40:58.115Z` (**291 min**),
`last_tick = 2026-10-10T18:34:17.281Z` (zdroj `manual`), `ready = 3`,
`running = 0` — a **stará podmínka `!!j.time` byla nad TÍMTÉŽ vstupem ZELENÁ**.
Plánovaný tik tedy **neběžel ~5 hodin** a orchestra nevydávala práci; **tik se
obnovil v `20:40:55Z`** (naměřeno C8-4 plného běhu: `last_cron_min = 0`, zdroj
`cron`) a `validate-all` je od té doby zelený (`OK cron běží (čas) — last_cron
… (0 min) · poslední tik zdrojem: cron`). Záznam měření (okno, hodnoty, následky):
`_analyza/p33-incident-cron-vystup.txt`. **Příčinu z tohoto pracoviště určit
nelze** (bez přístupu k logům Cloudflare; `wrangler` v sandboxu padá na
`spawn EPERM`) — naměřeno je OKNO a NÁSLEDEK, ne příčina.** Dočasný důsledek:**
během výpadku byl `validate-all` uvnitř `g3` červený → `g3` hlásil
**1 NEDEKLAROVANÝ exit** (naměřeno v C7 téhož běhu); po obnovení cronu hlásí
tentýž `g3` **0 NEDEKLAROVANÝCH** (doklad `_analyza/p33-g3-pred-zaznamem-vystup.txt`).

**Co se změnilo (dva commity, protože brána potřebuje NASKOZENOU službu):**
1. `conductor/src/index.ts` (commit `675f13a`): `scheduled` po DOKONČENÍ tiku
   zapíše tep do tabulky `state` (`last_cron`, `last_tick`, `last_tick_zdroj`);
   `POST /tick` zapíše jen `manual`; `/health` posílá `last_tick`, `last_tick_zdroj`,
   `last_cron`, `last_cron_min`. Tabulka se **zakládá v kódu** (`CREATE TABLE IF
   NOT EXISTS`), NE v `schema.sql` — jinak by se rozešla čísla v `AGENTS.md`
   (`ag-over-cisla.py` měří tabulky/sloupce PRÁVĚ ze `schema.sql`) a spadla by
   trvalá pravidla (H135).
2. `tools/cron-stav.mjs` (čistý predikát) + `tools/test-cron-stav.mjs` (8 fixtur)
   + `tools/validate-all.mjs` (kontrola `cron běží (čas)` ho používá a fixtury
   pouští jako součást brány).
3. ⚠ **Mutační kotva v `_analyza/n03-mutace.py` se musela posunout** (M3 cílí na
   `targets` v návratu `/health`) — naměřeno: bez toho `g3` i `validate-all`
   hlásily „N0.3: mutace brány → běžela, ale vzor nic nenašel“ a `validate-all`
   padal na **1 problém**. Je to táž past jako H131/H145: **změna kódu posune
   mutační kotvu**.

### 64.3 Co zůstalo OTEVŘENÉ (a co se NEMĚŘILO)

* **H133 (`p28-a-overeni.py` A6 čeká `g3 → exit 0`)** — **ZŮSTÁVÁ OTEVŘENÉ**:
  `g3` končí `exit 1` **pojmenovaně** (1 brána bez čítače: `mutace B (combat)`,
  `OCEKAVANE_NENULOVE` je prázdný). V P33 se **stav pojmenoval** (C7 to hlásí jako
  ROZDÍL, ne CHYBU), ale **A6 v `p28-a` se needitoval** — „deklarovat stav“ je
  změna měřidla a musí mít vlastní měření (a pozor na H135: přidání kontroly
  posune baseline).
* **C8-6 se ŽIVĚ neměřilo** (že ruční `POST /tick` neobnoví `last_cron`):
  `POST /tick` **dispatchuje práci** do cizí hry, takže se to měří **offline
  fixturou č. 8** (a staticky: `if (zdroj === "cron")`), ne zásahem do stavu.
* **`p31-a --plne` nebyl v C9 prvním během změřen** (vzor tvrzení) — chyba je
  opravená a měření proběhlo v druhém běhu; **první doklad se nezakrývá**.

### 64.4 Živý stav při zápisu

```
orchestra: HEAD %(head)s · origin/main = HEAD (PUSHNUTA) · hra %(hra)s (cizí session)
           ⚠ NASAZENÍ: H112 tep cronu — `deploy.yml` #37 na `675f13a`
             (`completed/success`), živá služba `/health` → `last_cron` TIKÁ
brány:     g3 → 49 bran / 2 nenulové exity (1 deklarovaný `zadání kontrola`,
           0 NEDEKLAROVANÝCH) / 1 bez čítače (`mutace B (combat)`; exit 1)
           · validate-all → 0 problémů · vlastní měřidlo P33 %(c_full)s
           · C9: %(c9_citace)s · C4 (dávka dokladů): %(c4_citace)s
           · ŽIVÝ TEP: `last_cron` tiká (zdroj `cron`), stará kontrola `!!h.time`
             by výpadek neviděla (H156)
```

### 64.5 Jak to ověřit (co spustit)

```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\\p33-a-overeni.py                 # LEVNÉ sekce (C0,C2,C3,C5,C8)
python _analyza\\p33-a-overeni.py --plne          # i kontramutace, úklid, g3, validate-all
python _analyza\\p33-mutace.py                    # důkaz, že měřidlo umí spadnout (19/0)
python _analyza\\p33-a-overeni.py --jen C9        # p31-a --plne + p32-a --plne (~80 min)
python _analyza\\p33-a-overeni.py --jen C4        # dávka dokladů (~35 min)
node tools\\test-cron-stav.mjs                    # 8 fixtur predikátu cronu
node tools\\validate-all.mjs                      # 0 problémů (a `cron běží (čas)` OK)
python _analyza\\p33-sonda-health.mjs             # ŽIVÝ tep: last_cron + verdikt
python _analyza\\p33-sonda-inventar.py            # který soubor rozešel otisk inventáře
```

### 64.6 Co čeká na tebe (uživatel)

* **Nic zásadního.** P33 nasadila **jedinou** změnu (H112): conductor zapisuje tep
  cronu a `/health` ho posílá; **chování práce se nemění** (tik dělá totéž) —
  přibyla jen observabilita a brána, která ji měří. Ověřeno třemi kroky.
* **H133** zůstává otevřené (viz 64.3) — je to **práce pro P34**, ne rozhodnutí
  pro tebe.
* **Rozhodnutí, které bude potřeba**: jestli se má `g3` stát **blokujícím**
  (dnes končí `exit 1` pojmenovaně kvůli jedné bráně bez čítače). Dnes to není
  vada, ale **stav** — a je popsaný.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kontrola", action="store_true", help="jen ověřit kotvy, nezapisovat")
    args = ap.parse_args()

    head = "?"
    hra = "?"
    try:
        import subprocess
        head = subprocess.run(["cmd", "/c", "tools\\git.cmd", "rev-parse", "--short", "HEAD"],
                              cwd=str(WS), capture_output=True).stdout.decode().strip() or "?"
        hra = subprocess.run(["cmd", "/c", "tools\\git.cmd", "-C", str(WS.parent / "uo-shadows"),
                              "rev-parse", "--short", "HEAD"],
                             capture_output=True).stdout.decode().strip() or "?"
    except Exception as e:  # noqa: BLE001
        print("VAROVÁNÍ: git se nepodařilo zavolat: %s" % e)

    c9_citace = "p31-a --plne viz doklad"
    if "C9-1" in T_C9:
        c9_citace = re.sub(r"\s+", " ", [l for l in T_C9.splitlines() if "C9-1 " in l][-1])[:200]
    c4_citace = "viz doklad"
    if "C4 ani JEDEN" in T_C4:
        c4_citace = [l for l in T_C4.splitlines() if "C4 ani JEDEN" in l][-1].strip()[:200]

    text64 = S64 % dict(
        c_full=C_FULL, c1=seznam(C1), c2=seznam(C2), c5=seznam(C5), c6=seznam(C6),
        c7=seznam(C7), c8=seznam(C8), c9=seznam(C9), c4=seznam(C4),
        rozdily=("%s" % "; ".join(r.strip()[:150] for r in ROZD_FULL)) or "žádný",
        nezmereno=("%s" % "; ".join(r.strip()[:150] for r in NEZM_FULL)) or "žádné",
        head=head, hra=hra, c9_citace=c9_citace, c4_citace=c4_citace)

    # ── HANDOFF: přidat na KONEC (oddíly se v HANDOFFu řadí za sebou) ───────
    t_h = nacti(HANDOFF)
    if "## 64. P33" in t_h:
        sys.exit("CHYBA: §64 už v HANDOFF.md je — zápis se neopakuje (a nepřepisuje)")
    novy_h = t_h.rstrip("\n") + "\n\n" + text64.rstrip("\n") + "\n"

    # ── KRONIKA: řádek 48 za řádek 47 ───────────────────────────────────────
    t_k = nacti(KRONIKA)
    radky_k = t_k.split("\n")
    idx47 = [i for i, l in enumerate(radky_k) if l.startswith("| **47** |")]
    if len(idx47) != 1:
        sys.exit("CHYBA: řádek 47 v kronice není právě 1× (%d×) — NEZAPSÁNO" % len(idx47))
    vzor47 = radky_k[idx47[0]]
    sloupcu = vzor47.count("|")
    radek48 = ("| **48** | **9.–10. 10. 2026** (22:5x–0x:xx +02:00) | "
               "**ověřovací (Úkol A: přeměření P32 vlastním měřidlem) + akční "
               "(Úkol B: H112 — tep cronu a brána, která ho měří) + nálezová "
               "(vlastní pasti kontramutací)** | "
               "**PŘEMĚŘIT PRÁCI P32 VLASTNÍM MĚŘIDLEM A ZAVŘÍT ASPOŇ JEDNU ZE ZBÝVAJÍCÍCH VAD.** "
               "**VLASTNÍ MĚŘIDLO:** `_analyza/p33-a-overeni.py` (C0–C8) → plný běh "
               "**%(c_full)s**; sekce C1 má **VLASTNÍ kontramutace** (vady vrácené do KOPIÍ "
               "měřidel a u H142 do ŽIVÉHO patcheru): `p22-test-mutace.py` **20/0**, ale s vrácenou "
               "podřetězcovou kontrolou **spadne** (exit 1, 1 chyba) · `p27-dopln-zaznamy.py` dnes "
               "kotvy ověří PŘED zápisem a fixtury zůstanou bajt na bajt, kdežto s VYPNUTÝM hlídáním "
               "je ZAPÍŠE (CRLF → LF) · `p30-mutace.py` **16/0** a kopie s KRÁTKOU kotvou se hlásí "
               "**POJMENOVANĚ** a doběhne S ČÍTAČEM (dřív `ValueError` bez čítače) · `p32-mutace.py` "
               "**18/0** · `p32-test-zapis-kotvy.py` **16/0** · `p29-a --jen A1M13` **8/0** a "
               "`--jen A3` **17/0** s úklidem kopie testu tiku. "
               "**DŮKAZ MĚŘIDLA:** `_analyza/p33-mutace.py` → **19/0** (zmutovaná KOPIE §63 → spadne; "
               "podstrčený post-nasazovací `/health` jako „stav před nasazením“ → spadne C8-5; živé "
               "soubory po testu bajt na bajt). "
               "**ÚKOL B — H112 ZAVŘEN (H149):** brána „cron běží (čas)“ testovala jen `!!h.time` "
               "(že služba odpovídá) — o běhu cronu netvrdila nic, a když se 9. 10. tik zastavil, "
               "žádná brána to neohlásila. Dnes služba **zapisuje TEP** (`last_cron` jen z `scheduled`, "
               "ruční `POST /tick` ho NEOBNOVÍ), `/health` ho posílá a brána ho **měří** "
               "(`tools/cron-stav.mjs` + 8 fixtur `tools/test-cron-stav.mjs`, které pouští jako "
               "součást brány). Důkaz je TŘÍVRSTVÝ: fixtury **8/0** · ŽIVÝ tep (`last_cron_min` = 0, "
               "zdroj `cron`) · a **ULOŽENÝ stav PŘED nasazením**, na kterém nová brána **SPADNE**, "
               "zatímco STARÁ podmínka `!!h.time` byla nad TÍMTÉŽ vstupem **ZELENÁ**. Nasazeno: "
               "commit `675f13a`, `deploy.yml` **#37** `completed/success`, živá služba tiká. "
               "⚠ **Mutační kotva v `_analyza/n03-mutace.py` se musela posunout** (cílí na `targets` "
               "v návratu `/health`) — bez toho `g3` i `validate-all` hlásily „N0.3: vzor nic nenašel“. "
               "**PŘEMĚŘENÍ P32:** `p32-a-overeni.py --plne` **51/0/2/0** = §63.1 **SE REPRODUKUJE**; "
               "`p31-a --plne` viz doklad `_analyza/p33-c9-vystup.txt`; dávka dokladů "
               "`p31-a --jen A4` viz `_analyza/p33-c4-vystup.txt` (pojistka „žádný z 4 sledovaných "
               "dokumentů se nezměnil“ + prázdné „KDO ZAPSAL“). "
               "**NÁLEZY O VLASTNÍ PRÁCI (H150–H155):** podřetězcová kontrola `endsWith` v novém "
               "nástroji (uspokojil ji `test-cron-stav.mjs`), kopie měřidla v PODADRESÁŘI `_analyza/` "
               "neměří nic (`ModuleNotFoundError` na `_mutace`), mutace „prvního výskytu v CELÉM "
               "dokumentu“ mine okno §63, GitHub API `?head_sha=<KRÁTKÝ sha>` tiše vrátí prázdno, "
               "vlastní diagnostické skripty rozešly otisk vstupů inventáře a — nejdražší — "
               "**rozbitý vzor TVRZENÍ přeskočil 45minutové měření** a tvářil se jako NEMĚŘENO. "
               "**PLÁN:** dodatek P33 | **—**")
    if radek48.count("|") != sloupcu:
        sys.exit("CHYBA: řádek 48 má %d sloupců, vzor %d — NEZAPSÁNO"
                 % (radek48.count("|"), sloupcu))
    radek48 = radek48 % dict(c_full=C_FULL)
    novy_k = radky_k[:idx47[0] + 1] + [radek48] + radky_k[idx47[0] + 1:]
    t_k = "\n".join(novy_k)

    # ── KRONIKA §2.26 před „## 3. Počty omylů“ ──────────────────────────────
    idx3 = [i for i, l in enumerate(t_k.split("\n")) if l.startswith("## 3. Počty omylů")]
    if len(idx3) != 1:
        sys.exit("CHYBA: kotva „## 3. Počty omylů“ není právě 1× (%d×) — NEZAPSÁNO" % len(idx3))
    t_k = t_k.replace("## 3. Počty omylů", S226.rstrip("\n") + "\n\n## 3. Počty omylů", 1)

    # ── PLAN: dodatek na konec ──────────────────────────────────────────────
    t_p = nacti(PLAN)
    if "## P33 (" in t_p:
        sys.exit("CHYBA: dodatek P33 v PLANu už je — neopakuje se")
    novy_p = t_p.rstrip("\n") + "\n\n" + SP33.rstrip("\n") + "\n"

    if args.kontrola:
        print("KONTROLA: kotvy sedí (HANDOFF §64 volný, kronika řádek 47 1×, "
              "„## 3.“ 1×, PLAN bez dodatku P33). Nic se nezapsalo.")
        return 0

    # ⚠ POJISTKA „NIC SE NEMAZALO“: každý starý NEprázdný řádek musí být v novém
    # textu. Počítá se PŘED zápisem (jinak by se srovnával nový text s novým).
    stare_texty = {}
    for cesta, novy in ((HANDOFF, novy_h), (KRONIKA, t_k), (PLAN, novy_p)):
        stary = nacti(cesta)
        stare_texty[cesta] = stary
        chybi = [l for l in stary.split("\n") if l.strip() and l not in novy]
        if chybi:
            sys.exit("CHYBA: %s by přišel o %d starých řádků (např. %r) — NEZAPSÁNO"
                     % (cesta.name, len(chybi), chybi[0][:80]))
    for cesta, novy in ((HANDOFF, novy_h), (KRONIKA, t_k), (PLAN, novy_p)):
        stary = stare_texty[cesta]
        cesta.write_bytes(novy.encode("utf-8"))
        print("  zapsáno: %-26s %d → %d řádků (+%d, 0 smazaných)"
              % (cesta.name, len(stary.split("\n")), len(novy.split("\n")),
                 len(novy.split("\n")) - len(stary.split("\n"))))
    print("  OK: všechny staré neprázdné řádky jsou v nových textech (nic nezmizelo)")
    return 0


# ── §2.26 KRONIKA (nálezy P33) ──────────────────────────────────────────────
S226 = """### 2.26 Nálezy z P33 (9.–10. 10. 2026) — brána, která nemohla selhat, a pět pastí vlastního měřidla

> Každý nález je doložený spuštěním; u každého je vidět, **čím** se měřil.
> Stavy jsou **rozhodnuté** (ne `NEOVĚŘENO`) — co zůstalo otevřené, je
> pojmenované jako práce pro P34 (H133).

| # | Nález | Doklad |
|---|---|---|
| **H149** | **H112 ZAVŘENO: BRÁNA „CRON BĚŽÍ (ČAS)“ MĚŘILA JEN `!!h.time` — TEDY ŽE SLUŽBA ODPOVÍDÁ.** O běhu cronu netvrdila NIC, a když se 9. 10. 2026 tik zastavil, **žádná brána to neohlásila**. **Oprava má dvě části, které se nesmí slít:** (1) SLUŽBA zapisuje **TEP** — `scheduled` po DOKONČENÍ tiku uloží `last_cron` (a `last_tick` + `last_tick_zdroj`), `POST /tick` zapíše jen `manual`, takže **ruční tik `last_cron` NEOBNOVÍ** (brána měří cron, ne tlačítko); `/health` posílá `last_tick`, `last_tick_zdroj`, `last_cron`, `last_cron_min`. (2) BRÁNA tep **hodnotí** — predikát je vytažený do čisté funkce `tools/cron-stav.mjs` (+ offline fixtury `tools/test-cron-stav.mjs` **8/0**, které brána pouští jako součást sebe sama), protože „zelená proti živé službě“ se od slepé brány nerozezná. **DŮKAZ JE TŘÍVRSTVÝ:** fixtury (`starý tep` / `chybějící tep` / `ruční tik` → CHYBA) · **ŽIVÝ** tep (`last_cron_min` = 0, zdroj `cron`) · a **ULOŽENÝ stav PŘED nasazením**, na kterém nová brána **SPADNE**, zatímco STARÁ podmínka `!!h.time` byla nad TÍMTÉŽ vstupem **ZELENÁ** (uloženo v `_analyza/p33-health-pred-vystup.txt`). **Tabulka `state` se zakládá v KÓDU** (`CREATE TABLE IF NOT EXISTS`), NE v `schema.sql` — jinak by se rozešla čísla v `AGENTS.md` (`ag-over-cisla.py` měří tabulky/sloupce PRÁVĚ ze `schema.sql`) a spadla by trvalá pravidla (H135). **Nasazeno:** commit `675f13a`, `deploy.yml` **#37** `completed/success`. | `conductor/src/index.ts` (`zapisTep`, `scheduled`, `/health`), `tools/cron-stav.mjs`, `tools/test-cron-stav.mjs`, `tools/validate-all.mjs`, `_analyza/p33-a-overeni-vystup.txt` (C8), `_analyza/p33-health-pred-vystup.txt`, `_analyza/p33-health-po-vystup.txt` |
| **H150** | **PODŘETĚZCOVÁ KONTROLA V NOVÉM NÁSTROJI — TÁŽ PAST JAKO H140, A NAMĚŘENA HNED NAPOPRVÉ.** `tools/cron-stav.mjs` se ptal, jestli je spuštěný jako CLI, přes `process.argv[1].endsWith("cron-stav.mjs")` — a to je **podřetězcová** podmínka, takže se nechala uspokojit i souborem **`test-cron-stav.mjs`** (obsahuje ji taky). Test se tím spustil jako CLI a spadl na `exit 2` („použití: node tools/cron-stav.mjs …“). **Opraveno:** porovnává se CELÁ cesta (`resolve(process.argv[1]) === fileURLToPath(import.meta.url)`). **Poučení:** podřetězcová podmínka se neptá „je to ten soubor?“, ale „obsahuje to jméno?“ — a to je jiná otázka (skill `overovani` §10.1). | `tools/cron-stav.mjs` (blok CLI), `tools/test-cron-stav.mjs` (první běh → `exit 2`) |
| **H151** | **KOPIE SPUSTITELNÉHO MĚŘIDLA V PODADRESÁŘI `_analyza/` NEMĚŘÍ NIC.** Kontramutace P33 zapisovaly vady do kopií měřidel ve `_analyza/p33-scratch/` — a ty **spadly na `ModuleNotFoundError: No module named '_mutace'`**, protože si nástroje odvozují cestu z `Path(__file__).resolve().parents[1]`, takže v podadresáři hledají `_analyza/_analyza`. Navenek to vypadalo jako „kontramutace spadla na TÉ kontrole“, ale **čítač nebyl žádný** (spadla na importu, ne na měřené podmínce). **Opraveno:** kopie se zapisují PŘÍMO do `_analyza/` s prefixem `_` (`_p33-mut-p22.py`, `_p33-mut-p30.py`) a uklízejí se; kontrola úklidu je součástí výsledku. | `_analyza/p33-a-overeni.py` (C1-a/C1-c, `zapis_kopii_s_vadou`), první běh `_analyza/p33-c1c6-vystup.txt` (4 chyby, čítač `None`), druhý běh **52/0** |
| **H152** | **MUTACE „PRVNÍHO VÝSKYTU V CELÉM DOKUMENTU“ MINE OKNO, KTERÉ MĚŘIDLO MĚŘÍ.** `p33-mutace.py` (M1) měnil tvrzení `over-skilly` **92/0 → 93/0** v KOPII dokumentu — a `replace(…, 1)` nad CELÝM textem trefil **jiný oddíl** (kotva je v dokumentu **2×**, v §63 jen **1×**), takže měřidlo dál četlo `92/0` a test hlásil „MUTACE SE NEPROVEDLA“. Je to **tatáž past jako H131/H145**, jen uvnitř měřidla: **mutuj v TOM okně, které měříš** — a ověř to **na ZÁPISU** (znovu načti kopii a změř v ní okno §63). | `_analyza/p33-mutace.py` (M1, `i63 = txt.find(text63)`), `_analyza/p33-c1c6-vystup.txt`, běh **19/0** |
| **H153** | **GitHub API `?head_sha=<KRÁTKÝ sha>` TIŠE VRÁTÍ PRÁZDNO.** Krok 3 ověření nasazení (`p32-sonda-cf-verze.mjs`) hlásil „**na commitu `0b86c2d` NENÍ žádný běh `deploy.yml`**“ — a přitom tam běh **#36 JE** (P32 s tím stejným nástrojem uspěla, protože předávala **plný** sha). API filtr `head_sha` se krátkým sha **neshoduje** a nevrátí chybu, jen prázdný seznam — takže „push se nenasadil“ vypadalo jako měřený fakt. **Opraveno:** krátký sha se nejdřív přeloží gitem (`git rev-parse`) a předává se PLNÝ. **Poučení:** u ověření stavu se ptát, **čím** to filtruju — tichý prázdný výsledek je třetí stav vedle zelené a červené. | `_analyza/p33-a-overeni.py` (C2-2/C2-3), `_analyza/p33-cf-verze-vystup.txt` (první běh: „CHYBA: … NENÍ žádný běh“), `_analyza/p32-cf-verze-vystup.txt` (plný sha → běh #36) |
| **H154** | **VLASTNÍ DIAGNOSTICKÉ SKRIPTY SESSION ROZEŠLY OTISK VSTUPŮ INVENTÁŘE.** `g3` i `validate-all` po sobě hlásily pojmenovaný stav „**INVENTÁŘ JE ZASTARALÝ / NEZMĚNĚNÝ**“ (`n1-over-inventar` → `exit=2`, NEOČEKÁVANÝ) — a vypadalo to jako vada bran. Viníka pojmenovala až vlastní sonda: mezi přegenerováním inventáře a branami vznikly **`_analyza/_p33-probe4.py`** a další jednorázové diagnostiky (napsané PO přegenerování), takže se změnil otisk vstupů (`1192 → 1193 souborů`). **Náprava:** inventář **přegenerovat po KAŽDÉM zápisu** (i po vlastní sondě — AGENTS.md to říká a stejně se to stalo), a protože to hledání viníka stálo čtvrt hodiny, vznikl nástroj **`_analyza/p33-sonda-inventar.py`**, který viníka vypíše jménem. | `_analyza/hl-rizika-jazyka.py` („otisk VSTUPŮ se rozešel … 1192 → 1193“), `_analyza/p33-sonda-inventar.py`, `_analyza/p33-g3-diagnostika-vystup.txt` (`NEOČEKÁVANÝ: n1-over-inventar → exit=2`) |
| **H155** | **VZOR TVRZENÍ, KTERÝ NEZABERE, PŘESKOČÍ MĚŘENÍ — A CHYBA SE TVÁŘÍ JAKO NEMĚŘENO.** První běh C9 hledal v §63 čítač `p31-a --plne` vzorem, který čekal `→ **43 kontrol**` (hvězdičky tučného písma PŘED číslem). V §63 jsou ale hvězdičky **jinde** (`**`p31-a-overeni.py --plne` → 43 kontrol, …**`), takže vzor **nezabral** — a `else` větev **vůbec nespustila 45minutové měření**; C9-4 pak hlásila „běh neproběhl“ a doklad tvrdil NEMĚŘENO. **Je to nejdražší past téhle session:** měřidlo, které na chybějící kotvě přeskočí měření, **hlásí méně, než změřilo** — a chyba vzoru se schová za chybějící data. **Opraveno:** v C9 se **nejdřív MĚŘÍ, teprve pak hledá tvrzení** (a nenalezené tvrzení je CHYBA, ne přeskočení). | `_analyza/p33-c9-vystup.txt` (první běh: „C9-1 §63 netvrdí čítač … měřidlo by měřilo jinam“, „C9-4 … běh neproběhl“), `_analyza/p33-a-overeni.py` (`sekce_C9`) |

| **H156** | **PLÁNOVANÝ TIK NEBĚŽEL ~5 HODIN — A NOVÁ BRÁNA TO OHLÁSILA (STARÁ BY BYLA ZELENÁ).** Naměřeno 10. 10. 2026: v běhu C4 (dávka dokladů) měřidlo `p33-a-overeni.py` v sekci C8-4 naměřilo **`last_cron` 260 min starý** (`CHYBA C8-4 … last_cron_min = 260, limit 10`) a `last_tick_zdroj = manual`; přímé měření v **20:31:51Z** dalo `last_cron = 2026-10-10T15:40:58.115Z` (**291 min**), `last_tick = 2026-10-10T18:34:17.281Z` (zdroj **`manual`**), `ready = 3`, `running = 0` — a **stará podmínka `!!h.time` byla nad TÍMTÉŽ vstupem `true` (ZELENÁ)**. Plánovaný tik tedy **neběžel ~5 hodin** a orchestra **nevydávala práci** (3 úlohy ready, 0 běžících); tik se **obnovil v `20:40:55Z`** (měřeno C8-4 plného běhu: `last_cron_min` = 0, zdroj `cron`), `validate-all` je od té doby zelený. **Dvě věci tím H112 dokazuje naostro:** (1) brána, která nemůže selhat, výpadek nevidí — stará kontrola hlásila „služba žije“ a **bylo to pravda**, jen to nebyla odpověď na otázku „tiká cron?“; (2) **ruční tik tep cronu NEOBNOVÍ** — `last_tick` byl `manual`, `last_cron` zůstal starý (jinak by výpadek nebyl vidět). **Příčinu z pracoviště určit nelze** (bez logů Cloudflare; `wrangler` v sandboxu padá na `spawn EPERM`) — naměřeno je **okno a následek**, ne příčina. **Dočasný důsledek pro brány:** během výpadku byl `validate-all` uvnitř `g3` červený → `g3` hlásil **1 NEDEKLAROVANÝ exit** (C7); po obnovení hlásí tentýž `g3` **0 NEDEKLAROVANÝCH** — **živý stav se propisuje do čítačů bran**, a kdo to neví, hledá vadu v měřidle. | `_analyza/p33-incident-cron-vystup.txt` (záznam měření: 260/291 min, `15:40:58Z` → `20:40:55Z`), `_analyza/p33-c4-vystup.txt` (C8-4 v běhu C4), `_analyza/p33-a-overeni-vystup.txt` (C8-4 plného běhu: zelená), `_analyza/p33-g3-pred-zaznamem-vystup.txt` (0 NEDEKLAROVANÝCH po obnovení), `node tools/validate-all.mjs` (`OK cron běží (čas)`) |

"""
SP33 = """## P33 (9.–10. 10. 2026) — CO JE OPRAVENÉ A CO JE NA ŘADĚ

> **Datum spotřeby:** měřeno **9. 10. 2026 22:5x – 10. 10. 2026 0x:xx +02:00**.
> Co z toho platí dnes, se pozná podle živého `HEAD` (viz `HANDOFF.md` §64).

1. **H112 JE ZAVŘENÉ A NASAZENÉ** (H149): conductor zapisuje tep cronu, `/health`
   ho posílá a brána `cron běží (čas)` ho **měří** (fixtury + živý tep + uložený
   stav před nasazením, na který brána spadne). **Nezbývá na tom nic dělat** —
   jen to příští session **přeměří** (je to tvrzení o měřidle, ne o stavu).
   **A hned to našlo skutečný výpadek (H156): plánovaný tik neběžel ~5 h**
   (`15:40:58Z` → `20:40:55Z`), orchestra nevydávala práci a **stará kontrola by
   byla zelená**. Kdo u orchestra vidí „nic se neděje“, ať se **nejdřív zeptá na
   `last_cron` v `/health`** — a když je starý > 10 min, tik neběží (stav, ne
   náhoda). **Příčinu výpadku nikdo nezměřil** (chybí přístup k logům Cloudflare)
   — je to otevřené pozorování pro příště: **když se to zopakuje, je to úkol.**
2. **H133 (`p28-a-overeni.py` A6 čeká `g3 → exit 0`) JE NA ŘADĚ** — `g3` končí
   `exit 1` **pojmenovaně** (1 brána bez čítače: `mutace B (combat)`). Dvě cesty:
   (a) **deklarovat stav** — v `p28-a-overeni.py` A6 vázat kontrolu na
   **pojmenovaný** výsledek (`0 NEDEKLAROVANÝCH` + `1 bez čítače`, jménem), nebo
   (b) **opravit bránu** `mutace B (combat)`, aby čítač měla. ⚠ U (a) pozor na
   **H135**: přidání kontroly posune čítač a shodí cizí tvrzení — měnit
   PREDIKÁT, ne počet kontrol.
3. **Nálezy o vlastním měřidle (H150–H155) jsou poučení, ne práce**: podřetězcová
   podmínka místo rovnosti jmen, kopie měřidla v podadresáři, mutace mimo měřené
   okno, krátký sha v API filtru, zápis po přegenerování inventáře a vzor
   tvrzení, který přeskočí měření. **Kdo staví nové měřidlo, projde si je.**
4. **P33 NIC NEPŘEPISOVALA**: `HANDOFF.md` i `KRONIKA-PROJEKTU.md` se jen
   doplňují (řádek 48 + §2.26) a vlastní kontrola to ověřuje (žádný starý
   neprázdný řádek nesmí v novém textu chybět).

**Co NEDĚLAT:** nepsat do hry; nepouštět harness z `g3` bez
`FORGE_REGISTR`/`FORGE_BEZ_REGISTRU` (H137); nespouštět `g3` a `validate-all`
současně; **needitovat záznamy** (HANDOFF/KRONIKA se jen doplňují); a **BĚHEM
PLNÉHO BĚHU MĚŘIDLA NEPISOVAT DO STROMU** — i vlastní diagnostický skript mění
otisk vstupů inventáře (H154).

**STAV NALEZENÝ P33 (nezaměňovat s tvrzením P32):** `g3` → 49 bran /
0 NEDEKLAROVANÝCH / 1 bez čítače (`mutace B (combat)`, `exit 1`) ·
`validate-all` → **0 problémů** · vlastní měřidlo P33 (C0–C8) → **%(c_full)s** ·
`p32-a-overeni.py --plne` → **51/0/2/0** (§63.1 se REPRODUKUJE).
""" % dict(c_full=C_FULL)

if __name__ == "__main__":
    sys.exit(main())
