# -*- coding: utf-8 -*-
r"""P28/D — ZÁPIS ZÁZNAMŮ DO KRONIKY: řádek session **43** + nálezy **§2.21**.

PROČ SKRIPTEM: řádky kroniky mají **přes 2000 znaků** a kotva načtená z řádku ho
zkrátí (omyly **194** a **206**). Skript proto pracuje s **řádky jako celky**,
vkládá je (nikdy nepřepisuje) a ověřuje, že **nic neubylo**.

Je **idempotentní**: když řádek 43 i §2.21 existují, jen to ověří.

Použití:
    python _analyza/p28-zapis-zaznamu.py
    python _analyza/p28-zapis-zaznamu.py --kontrola   # nic nezapíše
"""
import argparse
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
RADEK_ID = re.compile(r"^\|\s*\*\*(\d+)\*\*\s*\|")

RADEK_43 = (
    "| **43** | **8. 10. 2026** (15:45 – ~19:1x +02:00) | **ověřovací (Úkol A) "
    "+ akční (Úkol B5)** | **Přeměřit práci P27 VLASTNÍM měřidlem a opravit slepé "
    "místo brány `over-skilly`**: vlastní měřidlo `_analyza/p28-a-overeni.py` "
    "(A1–A7; A2/A3 poškozuje **ODPOVĚĎ handleru** i **TEXT dotazu**) + jeho "
    "mutační důkaz `p28-b-mutace.py`. Tvrzení P27 „`p27-a --plne` → **133/0**“ "
    "**dnes neplatí**: naměřeno **139 kontrol, 5 chyb** a **5× NEZMĚŘENO** "
    "(běh 60,4 min) — příčiny pojmenované v §2.21 (P28-A). **B5:** brána "
    "`over-skilly` měřila **jiný TVAR cest**, než dokumenty používají — naměřeno "
    "**71 zmínek viděla, 90 jich je** (16 v ``` bloku nebo za `python …`); "
    "opraveno včetně **deklarovaných výjimek** pro 3 šablony skillu `vision`, "
    "mutační test **8/0 → 17/0**. **Obnoven smazaný řádek kroniky 24** (commit "
    "`c3ee946` ho smazal a vložil na jeho místo 25; text byl dohledatelný jen "
    "v gitu `411f0bb`) nástrojem `_analyza/p28-obnov-kroniku.py` (**9/0**, bajt "
    "na bajt) a `kronika-kontrola.py` **nově hlídá KONTINITU ID** (mutace: chybí "
    "řádek 30 → `exit 1`, P28-E). Nálezy **P28-A…P28-H** v **§2.21**. |"
)

SEKCE_221 = """### 2.21 Nálezy z P28 (8. 10. 2026) — měřidlo, které sníží čítač, slepá brána a ZTRACENÝ ZÁZNAM

> **Co je změřeno:** vlastním měřidlem `_analyza/p28-a-overeni.py` (session P28,
> 15:45–19:1x +02:00) a jeho mutačním důkazem `_analyza/p28-b-mutace.py`.
> **Surové výstupy:** `_analyza/p28-a-overeni-vystup.txt`,
> `_analyza/p28-a1-vystup.txt`, `_analyza/p28-vzdy-p27a-plne-vystup.txt`.

**P28-A — TVRZENÍ P27 „133/0“ DNES NEPLATÍ: naměřeno 139/5 + 5× NEZMĚŘENO.**
Dnešní běh `p27-a --plne` (60,4 min, doklad) vykázal **139 kontrol, 5 chyb**.
Tři z těch chyb nejsou regrese kódu, ale **vada POŘADÍ měření**: měřidlo P27
pouští `g3` a `validate-all` v etapě A6 — tedy **poté**, co jeho vlastní předchozí
etapy zapsaly do stromu soubory, které vstupují do obsahového otisku inventáře.
Inventář je pak „zastaralý“, `g3` hlásí **2 NEDEKLAROVANÉ exity** (`n1-over-inventar`,
`validate-all (CELEK)`) a `validate-all` sám padá — přičemž náprava je jediná:
**přegenerovat inventář**. P28 to dělá (a měří to) **před** během `g3`.
Zbylé dvě chyby jdou za **14. skillem mimo repo** (P28-C) — `p26-a` má kvůli němu
trvale červenou a tím padá i diferenciál `p26-b` (**26/2** místo tvrzených 26/0).

**P28-B — SEDM ENDPOINTŮ JE VOLÁNO I KONTROLOVÁNO — doloženo POŠKOZENOU ODPOVĚDÍ.**
P27 to dokazovala zarážkou v handleru; P28 to měří **jinak**: v kopii zdroje se
poškodí **HODNOTA v odpovědi** daného endpointu (`ready`, `attempts`, `log_tail`,
`pr_url`, `kinds`, `active`) a měří se, které kontroly zčervenají. Naměřeno:
u **každého** ze sedmi endpointů zčervenala **aspoň jedna kontrola JEHO skupiny**
a **žádná** kontrola ostatních šesti (negativní kontrola), kontrolní
`A: /tick odpoví 200` zůstala zelená. Druhá polovina téhož: poškození **TEXTU
dotazu** (`ORDER BY … DESC`, filtr `active=1`) zčervenalo kontroly, které
poškození hodnoty **nechalo zelené** (`AC: čte se CELÝ řádek`,
`AD: a filtr active=1 tam NENÍ`) — tím je měřený rozdíl **TVAR vs OBSAH**.

**P28-C — BRÁNA `over-skilly` BYLA SLEPÁ K TVARU CEST (nález §51.3 opraven).**
Naměřeno sondou `_analyza/p28-sonda-cesty.py` (jednorázová, v `PRESKIP` dávky):
brána hledala cestu **jen hned za backtickem** a viděla **71 zmínek**, zatímco
v týchž dokumentech jich je **90** — **16** bylo v ``` bloku, za `python `/`node `
nebo v `--json …`. „0 mrtvých cest“ tedy **nebylo důkaz**. Vzor je rozšířený
(cesta kdekoliv na řádku, se zachováním přeskočení vzorů se `*`/`?`) a brána
nově **vypisuje**, kolik zmínek našla mimo backticky. Tři cesty skillu `vision`
(`tools\\vision.py`, `tools\\make_vision_test_shot.py`, `tools\\vision-test-shot.png`)
jsou **legitimní šablona pro projekt s vlastním `.python`** (skill to říká slovem
„v repu“) → dostaly **deklarovanou výjimku s důvodem**, klíčovanou dvojicí
(skill, cesta): **táž cesta v jiném skillu bránu pořád shodí** (měřeno).
Mutační test `test-over-skilly-delegovane.py` rozšířen o 9 kontrol → **17/0**.

**P28-D — DVĚ BRÁNY MAJÍ RŮZNÝ TVAR ČÍTAČE.** `over-dokumentaci.py`
a `test-over-skilly-delegovane.py` tisknou `Kontrol: 64, chyb: 0`, ostatní
`N kontrol, M chyb`. Měřidlo, které čte **jen jeden** tvar, dostane `None`
a zapíše „nesedí“ — což vypadá jako rozchod, ale je to **jiný formát**.

**P28-E — ZTRACENÝ ZÁZNAM JE TICHO (nejdražší nález P28).** Kronika měla
**41 řádků** session s id 1..42 — **id 24 CHYBĚLO**. `git show c3ee946` dokládá,
že ten commit řádek **SMAZAL** (a na jeho místo vložil řádek 25); text se v živé
kronice nevyskytoval (fráze „obecných pravidel“ → 0 výskytů), ale byl
dohledatelný v gitu (`411f0bb`). **Žádná brána to neviděla**: `kronika-kontrola.py`
kontrolovala počet řádků (≥ 10), datum a typ — a přesně na tuhle třídu upozorňuje
poučení P22 („chybějící záznam není rozchod, je to ticho“). **Náprava:**
řádek 24 je **obnoven bajt na bajt** (`_analyza/p28-obnov-kroniku.py`, 9/0)
a `kronika-kontrola.py` **nově hlídá kontinuitu id** (mutace: kopie kroniky bez
řádku 30 → `exit 1` a id je pojmenované).

**P28-F — MĚŘIDLO, KTERÉ NENAJDE TVRZENÍ, TIŠE SNÍŽÍ ČÍTAČ.** V měřidle P27
vede nenalezené tvrzení na **NEZMĚŘENO** (dnes 5×, v A4 například
`A4 tvrzení §56: over-skilly`) — kontrola se přeskočí, čítač klesne a verdikt
zůstane zelený. Je to táž třída jako „brána, která čeká na vstup, jenž nikdy
nepřijde“ (`AGENTS.md`). P28 má totéž jako **CHYBU** (`chyb_claim`).

**P28-G — ŽIVÝ STAV SE POSUNUL, ALE STROP `B4` NIC NEBLOKUJE.** Proti §58:
`/health` `ready=1` → **2**, `/roadmap` 21 granul → **22** a 0 → **1 blokovaná**
(`stavy: done 19, queued 2, blocked 1`). **Maximální počet pokusů na granulích
je ale 5**, tedy **pod stropem 8** — blokace má jinou příčinu a **acceptance B4
(„strop opravdu zastaví“) pořád není splněna**. `validate-all` proto dnes hlásí
**2 problémy** (cache hry 22 řádků vs soubor 21 granul, 5 osiřelých řádků) —
oba o **stavu HRY/D1**, ne o orchestra; `g3` tím má 1 nedeklarovaný exit.

**P28-H — VLASTNÍ OMYLY P28 (čtyři, všechny o MĚŘENÍ — proto jsou zapsané).**
(1) Měřidlo si **přepsalo živý doklad** měřidla P27 (dílčí běhy `--jen A4/A5/A6`
bez `--vystup`) — poznáno podle času zápisu, ne podle výstupu; (2) **kotva
diferenciálu ležela mimo §56** (`83/83` je v dokumentu 15×) → první pokus vyrobil
**falešný nález o měřidle**; správně se mutuje v **izolovaném §56**;
(3) `re.search(r"^--- A%s")` s etapou `A4` hledalo `--- AA4` → `None`
(a měřidlo to naštěstí vypsalo jako NEZMĚŘENO, ne jako zelenou);
(4) `python -c` s „→“ přes PowerShell vrátil **0 výskytů** místo 4 — past
`dsh-prostredi` (české znaky v `-c`), měřeno až **souborem**.
"""


def nacti():
    return KRONIKA.read_text(encoding="utf-8")


def radky_sessions(text):
    return [l for l in text.splitlines() if RADEK_ID.match(l)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kontrola", action="store_true")
    args = ap.parse_args()
    chyb = 0
    kontrol = 0

    def k(popis, ok, detail=""):
        nonlocal chyb, kontrol
        kontrol += 1
        if ok:
            print("  OK    %s" % popis)
        else:
            chyb += 1
            print("  CHYBA %s%s" % (popis, (" — " + detail) if detail else ""))

    text = nacti()
    k("kronika je LF", text.count("\r\n") == 0)
    ma43 = bool(re.search(r"^\|\s*\*\*43\*\*\s*\|", text, re.M))
    ma221 = "### 2.21 Nálezy z P28" in text

    if ma43 and ma221:
        k("řádek 43 i §2.21 už jsou (idempotentní běh)", True)
        radky = radky_sessions(text)
        ids = [int(RADEK_ID.match(l).group(1)) for l in radky]
        k("id jsou 1..43 bez děr",
          [i for i in range(1, max(ids) + 1) if i not in ids] == [], str(sorted(ids)[-5:]))
        return 0 if chyb == 0 else 1

    radky = radky_sessions(text)
    kotva42 = [l for l in radky if RADEK_ID.match(l).group(1) == "42"]
    k("kotva (řádek 42) je v souboru právě 1×", len(kotva42) == 1 and
      text.count(kotva42[0]) == 1 if kotva42 else False)
    if not kotva42:
        return 1
    kotva42 = kotva42[0]

    kotva3 = "\n## 3. Počty omylů"
    k("kotva §3 je v souboru právě 1×", text.count(kotva3) == 1, "výskytů: %d" % text.count(kotva3))
    if text.count(kotva3) != 1:
        return 1

    novy = text
    if not ma43:
        novy = novy.replace(kotva42, kotva42 + "\n" + RADEK_43, 1)
    if not ma221:
        novy = novy.replace(kotva3, "\n" + SEKCE_221.rstrip() + kotva3, 1)

    if args.kontrola:
        print("      (--kontrola: nic se nezapsalo)")
        print("\nVÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
        return 0 if chyb == 0 else 1

    KRONIKA.write_bytes(novy.encode("utf-8"))
    zpet = nacti()
    k("řádek 43 je v souboru", bool(re.search(r"^\|\s*\*\*43\*\*\s*\|", zpet, re.M)))
    k("§2.21 je v souboru", "### 2.21 Nálezy z P28" in zpet)
    k("řádek 43 je VLOŽEN CELÝ (sha256 shodný)",
      RADEK_43 in zpet, "řádek se nenašel celý")
    k("řádek 42 zůstal BAJT NA BAJT", kotva42 in zpet)
    stare = set(radky)
    nove = set(radky_sessions(zpet))
    # ⚠ POZOR NA OBRÁCENÝ PREDIKÁT: prázdný rozdíl je ÚSPĚCH, ale prázdný seznam
    # je `False` — `k(..., sorted(...), [])` proto hlásilo CHYBU na SPRÁVNÉM zápisu.
    k("žádný řádek session nezmizel", sorted(stare - nove) == [], str(sorted(stare - nove)))
    k("a přibyl PRÁVĚ JEDEN (43)", sorted(nove - stare) == [RADEK_43], str(sorted(nove - stare))[:120])
    ids = [int(RADEK_ID.match(l).group(1)) for l in radky_sessions(zpet)]
    k("id jsou po zápisu 1..43 bez děr",
      [i for i in range(1, max(ids) + 1) if i not in ids] == [],
      str([i for i in range(1, max(ids) + 1) if i not in ids]))

    r = subprocess.run([sys.executable, str(WS / "_analyza" / "kronika-kontrola.py")],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(WS), timeout=1800)
    v = (r.stdout or "") + (r.stderr or "")
    k("kronika-kontrola.py → exit 0 a SEDÍ", (r.returncode, "SEDÍ" in v.upper()) == (0, True),
      v[-300:])
    r = subprocess.run([sys.executable, str(WS / "_analyza" / "handoff-kontrola-uplnost.py")],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(WS), timeout=1800)
    v = (r.stdout or "") + (r.stderr or "")
    m = re.search(r"(\d+)\s*/\s*(\d+)", v)
    print("      úplnost handoffu: %s (exit %d)" % (m.group(0) if m else "?", r.returncode))
    k("handoff-kontrola-uplnost.py → exit 0", r.returncode == 0, v[-300:])

    print("\nVÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
    return 0 if chyb == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
