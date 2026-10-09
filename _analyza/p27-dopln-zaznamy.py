# -*- coding: utf-8 -*-
r"""P27 — DOPLNĚNÍ ZÁZNAMŮ: finální čísla + nálezy P27-P/Q/R/S.

PROČ SKRIPTEM: texty mají tisíce znaků a musí se měnit JEN v MÝCH oddílech
(`HANDOFF.md` §57, `KRONIKA` řádek 42 + §2.20) — cizí historie se needituje.

Použití: python _analyza/p27-dopln-zaznamy.py
"""

import os
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
# ⚠ TEST SEAM (P32, H136): cesty jdou přepsat z PROSTŘEDÍ, aby je test mohl
# poslat na FIXTURY a měřit, jestli skript zapíše, nebo ne. Bez toho by test
# musel sáhnout na ŽIVÉ dokumenty — a to je přesně to, co H130/H136 zakazuje.
# Výchozí hodnota je živý dokument (chování se pro normální běh NEMĚNÍ).
H = pathlib.Path(os.environ.get("P27_HANDOFF") or (WS / "HANDOFF.md"))
K = pathlib.Path(os.environ.get("P27_KRONIKA") or (WS / "KRONIKA-PROJEKTU.md"))

kontrol = 0
chyb = []


def k(ok, popis):
    global kontrol
    kontrol += 1
    print("  %s  %s" % ("OK  " if ok else "CHYBA", popis))
    if not ok:
        chyb.append(popis)


def vymen(cesta, dvojice, popis):
    """Nahradí dvojice v souboru — ale ZAPÍŠE JEN, KDYŽ JSOU VŠECHNY KOTVY 1×.

    ⚠ H136 (opraveno v P32): do P32 se soubor zapsal **i když kotva nalezena
    nebyla** (`cesta.write_bytes(...)` byl bez podmínky) a `exit 1` hlásal až
    potom — „doklad, který spadl, a přesto zapsal“. Následek: dávka dokladů
    i ruční běh přepsaly ŽIVÝ dokument (a převedly konce řádků), i když skript
    sám hlásil chybu. Kotvy se proto ověří **PŘED** zápisem a při neshodě se
    **nezapisuje vůbec**.
    """
    text = cesta.read_text(encoding="utf-8")
    chyby = ["%s: kotva %d× (musí 1×): %r" % (popis, text.count(stary), stary[:60])
             for stary, _ in dvojice if text.count(stary) != 1]
    if chyby:
        for c in chyby:
            k(False, c)
        k(False, "%s: NEZAPSÁNO (kotvy nesedí) — soubor zůstal NEDOTČEN" % popis)
        return False
    for stary, novy in dvojice:
        text = text.replace(stary, novy, 1)
    cesta.write_bytes(text.encode("utf-8"))
    k(True, "%s: zapsáno (všech %d kotev 1×)" % (popis, len(dvojice)))
    return True


DOPLNENI_57 = r"""
15. **PŘEPSANÝ ŘÁDEK SESSION VYPADÁ PRO BRÁNU JAKO SMAZANÝ.** Když se v kronice
    **přepíše text** řádku (oprava data v řádku 42), `git diff` ukáže
    `-| **42** | …` **a** `+| **42** | …` se **stejným id** — a brány
    `p25-a-overeni.py` (A5) i `p24-a-overeni.py` (A5) to hlásily jako
    **„SMAZAL SE ŘÁDEK SESSION"**. Falešný poplach na **správném** dokumentu.
    **OPRAVENO v obou:** za smazaný se počítá jen id, které na `+` straně diffu
    **NENÍ**, a `p25-a` má k tomu **negativní kontrolu** (klasifikátor musí
    rozlišit přepsaný a smazaný řádek, jinak brána skončí `exit 2`).
16. **PEVNÉ OKNO `HEAD`…`HEAD~4` V `p26-b-mutace.py` SE ROZPADLO.** Důkaz P25-K
    hledal verzi brány **před opravou** v posledních pěti revizích. Po dvou
    commitech P27 (`1bdc982`, `649ca9b`) se ta verze (`ef58327`) posunula na
    **`HEAD~6`** → `p26-b` hlásilo **26/4** („verze měřidla PŘED opravou
    nalezena v historii (None)") a **důkaz se tiše ztratil**.
    **OPRAVENO:** okno je 20 revizí a nález je pojmenovaný v komentáři.
17. **CIZÍ ZMĚNA SKILLU MIMO REPO SHODÍ BRÁNY ORCHESTRA.** Soubor
    `~\.dsh\skills\game-developer\SKILL.md` **přepsala jiná session** během P27
    (**mtime 8. 10. 2026 11:22:23**) a odkazuje na 3 cesty, které v repu
    orchestra **nejsou** (`tools/plan-status.py`, `tools\roadmap-gen.py`,
    `tools\plan-status.py` — existují v sourozenci `E:\Workspaces\game-clone`).
    Naměřeno: `over-skilly` **13/0 → 13/1**, a **kaskádou** to shodilo `g3`
    (2 nedeklarované exity), `validate-all`, `p24-a` (A6), `p25-a` (A4),
    `p26-a` (`--plne` 90 → 85 kontrol) i `p26-b` (diferenciál M3a).
    **NENÍ to práce P27 a NEOPRAVOVAL jsem ji** (cizí rozdělaná práce);
    měřidlo ten stav **pojmenovává** (`cizi_skill()`) a **měří jeho mechanismus**
    (`p26-a --jen A4` padá na `over-skilly`). **Rozhodnutí je na uživateli.**
18. **I DOKLAD MIMO VYLUČOVACÍ VZOR ZNEplatní INVENTÁŘ UPROSTŘED BĚHU.**
    Výstup jsem přesměroval do `_analyza/p27-a-plne-final.txt` — název
    **neodpovídá** vzoru `*-vystup.txt`, takže soubor **je vstupem otisku**
    a během běhu se **měnil** → inventář „zastaralý" → `p26-a` spadl na
    **84–88 kontrol** a `g3`/`validate-all` hlásily nedeklarované exity.
    **Poučení (P26/10 zopakováno):** doklady a logy se pojmenovávají
    `_analyza/*-vystup.txt`; do otisku vstupů navíc vstupuje i **`__pycache__`**,
    který vzniká **importem** během běhu.
"""

RADKY_220 = r"""| **P27-P** | „Přepsaný řádek v kronice je totéž co smazaný.“ | Oprava **data** v řádku 42 (táž session, `77ade9f`) vypadá v `git diff` jako `-| **42** |` **i** `+| **42** |` se stejným id — a `p25-a` (A5) i `p24-a` (A5) to hlásily jako **„SMAZAL SE ŘÁDEK SESSION“** | **FALEŠNÝ POPLACH NA SPRÁVNÉM DOKUMENTU — OPRAVENO V OBOU.** Za smazaný se počítá jen id, které na `+` straně **NENÍ**; `p25-a` má **negativní kontrolu** klasifikátoru (jinak `exit 2`). Ověřeno na skutečných difech `77ade9f` a `649ca9b` |
| **P27-Q** | „Důkaz P25-K je trvalý, když je v repu commit.“ | `p26-b-mutace.py` hledal verzi brány **před opravou** jen v `HEAD`…`HEAD~4`; po dvou commitech P27 je ta verze na **`HEAD~6`** → **26/4** a „verze měřidla PŘED opravou nalezena v historii (None)“ — **důkaz se tiše ztratil** | **OPRAVENO:** okno 20 revizí + nález pojmenovaný v komentáři. **Pevné okno je křehké: s každým commitem se zub posouvá** |
| **P27-R** | „Brány orchestra měří jen orchestr.“ | `over-skilly` **13/0 → 13/1**: SKILL `game-developer` **mimo repo** (`~\.dsh\skills\`, mtime **8. 10. 2026 11:22:23**, změnila ho **cizí session**) odkazuje na `tools/plan-status.py`, `tools\roadmap-gen.py` — v repu orchestra **nejsou**, v sourozenci `E:\Workspaces\game-clone` **jsou** | **STAV MIMO REPO, NE VADA ORCHESTRA.** Kaskádou shodí `g3` (2 nedeklarované exity), `validate-all`, `p24-a` A6, `p25-a` A4, `p26-a` (90 → 85 kontrol) i `p26-b` (diferenciál M3a). **NEOPRAVOVAL jsem ji** (cizí rozdělaná práce) — měřidlo ji **pojmenovává** a **měří její mechanismus**; rozhodnutí patří uživateli |
| **P27-S** | „Název výstupu je detail.“ | Vlastní log jsem přesměroval do `_analyza/p27-a-plne-final.txt` — název **není** `*-vystup.txt`, takže soubor **vstupuje do otisku** a během běhu se měnil → inventář „zastaralý“ → `p26-a` **90 → 84/86/88** kontrol a `g3`/`validate-all` hlásily nedeklarované exity | **P26/10 ZOPAKOVÁNO VLASTNÍM OMylem.** Doklady patří na `_analyza/*-vystup.txt`; a do otisku vstupuje i **`__pycache__`** z importů během běhu |
"""

# ── HANDOFF §57: doplnit nálezy 15–18 před „### 57.3“ ──────────────────────
text = H.read_text(encoding="utf-8")
kotva = "### 57.3 Živý stav při zápisu"
k(kotva in text, "HANDOFF: kotva 57.3 nalezena")
if "15. **PŘEPSANÝ ŘÁDEK SESSION" not in text:
    if kotva in text:
        text = text.replace(kotva, DOPLNENI_57.strip("\n") + "\n\n" + kotva, 1)
        H.write_bytes(text.encode("utf-8"))
        k(True, "HANDOFF: nálezy 15–18 doplněny do §57.2")
    else:
        k(False, "HANDOFF: kotva 57.3 NENÍ → NEZAPISUJI (H136)")
else:
    k(True, "HANDOFF: nálezy 15–18 už tam jsou")

# ── HANDOFF §57: OPRAVA čísel (měřeno znovu, finální stav) ─────────────────
vymen(H, [
    ("`_analyza/p27-a-overeni.py --plne` → **140 kontrol, 0 chyb** (0× `NEZMĚŘENO`), uložený výstup `p27-a-plne-vystup.txt`",
     "`_analyza/p27-a-overeni.py --plne` → **133 kontrol, 0 chyb** (0× `NEZMĚŘENO`), uložený výstup `p27-a-plne-vystup.txt`; doloženo během 8. 10. 2026 12:5x–13:4x"),
    ("| **C** | Brány po sobě (**inventář → `g3` → `validate-all`**, ne současně) | `g3` → **49 bran, 1 deklarovaný nenulový exit** (`zadání kontrola`), **exit 0** · `validate-all` → **VŠE V POŘÁDKU** · `kronika-kontrola` → **SEDÍ** · `handoff-kontrola-uplnost` → **83/83** |",
     "| **C** | Brány po sobě (**inventář → `g3` → `validate-all`**, ne současně) | `g3` → **49 bran**; nenulové exity **2, oba NEDEKLAROVANÉ a oba MIMO REPO** (`over-skilly`, `over-skilly: mutace delegovaných cest`) → **exit 1** (stav mimo repo, nález **P27-R**) · `validate-all` → **NENÍ zelený, padá na `over-skilly`** (týž stav) · `kronika-kontrola` → **SEDÍ** · `handoff-kontrola-uplnost` → **83/83** |"),
], "HANDOFF §57 čísla")

vymen(H, [
    ("brány:     g3 → 49 bran, 1 deklarovaný nenulový exit (zadání kontrola), exit 0\n           validate-all → VŠE V POŘÁDKU",
     "brány:     g3 → 49 bran; 2 NEDEKLAROVANÉ exity, oba MIMO REPO (`over-skilly`\n           a její mutační dvojče) → exit 1; validate-all padá na TÝŽ stav\n           (cizí session přepsala SKILL `game-developer`, mtime 11:22)"),
    ("p27-a:     --plne → 140 kontrol, 0 chyb",
     "p27-a:     --plne → 133 kontrol, 0 chyb (sondy/klasifikátory P27)"),
], "HANDOFF §57.3 stav")

# ── KRONIKA §2.20: doplnit řádky P/Q/R/S za P27-O ─────────────────────────
text = K.read_text(encoding="utf-8")
if "| **P27-P** |" not in text:
    m = re.search(r"^\| \*\*P27-O\*\* \|.*$", text, re.M)
    k(m is not None, "KRONIKA: řádek P27-O nalezen")
    if m:
        text = text[:m.end()] + "\n" + RADKY_220.strip("\n") + text[m.end():]
        K.write_bytes(text.encode("utf-8"))
        k(True, "KRONIKA: řádky P27-P…P27-S doplněny do §2.20")
else:
    k(True, "KRONIKA: řádky P27-P…P27-S už tam jsou")

# ── kontroly ───────────────────────────────────────────────────────────────
t_h = H.read_text(encoding="utf-8")
t_k = K.read_text(encoding="utf-8")
k("15. **PŘEPSANÝ ŘÁDEK SESSION" in t_h, "HANDOFF má nález 15")
k("18. **I DOKLAD MIMO VYLUČOVACÍ VZOR" in t_h, "HANDOFF má nález 18")
k("**133 kontrol, 0 chyb**" in t_h, "HANDOFF tvrdí finální čítač 133/0")
k("205/0" in t_h and "205 kontrol" in t_h, "HANDOFF dál tvrdí 205/0 i 205 kontrol")
for kotva, popis in (("## 53.", "§53"), ("## 54.", "§54"), ("## 55.", "§55"),
                     ("## 56. P26 —", "§56")):
    k(kotva in t_h, "%s zůstal" % popis)
k("| **P27-R** |" in t_k, "KRONIKA má řádek P27-R")
k("| **42** |" in t_k and "| **41** |" in t_k, "řádky 41 i 42 zůstaly")
k("### 2.19 Nálezy z P26" in t_k and "### 2.20 Nálezy z P27" in t_k,
  "§2.19 i §2.20 zůstaly")
k("| **celkem** | **27 bloků, 35 sessions** | **208** |" in t_k,
  "souhrn §3 zůstal NEPŘEPOČÍTÁN")

print()
print("=" * 78)
print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
for c in chyb:
    print("  CHYBA: %s" % c)
sys.exit(1 if chyb else 0)
