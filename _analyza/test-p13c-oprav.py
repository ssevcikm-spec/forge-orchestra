#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""P13c: MUTAČNÍ TESTY oprav měřidel (nálezy H48, H49, H50, H52).

PROČ SAMOSTATNÝ SOUBOR: zadání žádá u KAŽDÉ opravy **mutační test** — „s vrácenou
vadou brána spadne". U čtyř z pěti oprav jde právě o to, že brána **tiše
neměřila**, takže „prošlo to" bez mutace neznamená nic (`overovani` §1).

CO SE MĚŘÍ (každý test má ZNÁMÝ SPRÁVNÝ i ZNÁMÝ CHYBNÝ případ):

  A) `g3-brany.py` — cesty se ODVOZUJÍ:
       * zdravě: všech N bran se spustí, **0 nedosazených záznamníků**
       * vada:   do seznamu se vrátí STARÝ literál (`orchestra/tools/...`)
                 → `can't open file` a `nedosazene` to pojmenuje
  B) `tools/test-gitignore-tajemstvi.py` — kontrakt generátor ↔ hra:
       * zdravě: `N kontrol, 0 chyb` s N > 0
       * vada:   z generátoru se vyndá `.env` → `CHYBA` a `exit 1`
  C) `tools/verify-setup.py` — struktura:
       * zdravě: `exit 0` + čítač `ZMĚŘENO: N kontrol`
       * vada:   hra se „přesune" (proměnná prostředí) → hlásí CHYBI, `exit 1`
  E) `_analyza/hl-neanglicky-v-kodu.py` — vidí NETRACKOVANÉ soubory:
       * zdravě: soubor s českým identifikátorem **mimo git** se v inventáři OBJEVÍ
       * vada:   soubor se vyloučí vzorem artefaktů → v inventáři NENÍ
                 (a je vidět ve `vyloucene_artefakty`)

⚠ KAŽDÝ ZÁPIS JE V `try/finally` A VRACÍ SE BAJT NA BAJT (`overovani` §10.6).
⚠ U KAŽDÉ MUTACE SE OVĚŘUJE, ŽE **MĚŘENÁ PODMÍNKA PŘESTALA PLATIT** (§7.14),
  ne jen že se změnil text.

Použití: python _analyza\test-p13c-oprav.py
Návrat:  0 = všechny opravy měří | 1 = nález | 2 = test sám selhal
"""

import json
import pathlib
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
ANALYZA = WS / "_analyza"
TOOLS = WS / "tools"
HRA = WS.parent / "uo-shadows"
G3 = ANALYZA / "g3-brany.py"
GITIGNORE_TEST = TOOLS / "test-gitignore-tajemstvi.py"
VERIFY = TOOLS / "verify-setup.py"
SKENER = ANALYZA / "hl-neanglicky-v-kodu.py"
GENERATOR = WS / "install-into-repo.ps1"

kontrol = 0
chyb = 0


def zkontroluj(popis: str, ok: bool, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    if ok:
        print(f"  OK    {popis}")
    else:
        chyb += 1
        print(f"  CHYBA {popis}")
        if detail:
            for radek in detail.splitlines()[:12]:
                print(f"        {radek}")


def spust(prikaz: list, cwd: pathlib.Path = WS, env: dict | None = None) -> tuple:
    import os
    e = dict(os.environ)
    e["PYTHONIOENCODING"] = "utf-8"
    if env:
        e.update(env)
    r = subprocess.run(prikaz, capture_output=True, cwd=str(cwd), env=e, timeout=1800)
    v = (r.stdout or b"").decode("utf-8", "replace") + (r.stderr or b"").decode("utf-8", "replace")
    return r.returncode, v


def mutuj(cesta: pathlib.Path, stary: str, novy: str, funkce, pocet_cekany: int = 1):
    """Provede mutaci, zavolá `funkce()`, v `finally` vrátí soubor bajt na bajt.

    ⚠ `stary` se v `novy` ZÁMĚRNĚ NESMÍ vyskytovat: jinak by platila původní
    podmínka dál a test by měřil nezměněný stav (past `overovani` §7.14).
    """
    puvodni = cesta.read_bytes()
    # ⚠ KÓDOVÁNÍ SE MUSÍ DODRŽET: `install-into-repo.ps1` má UTF-8 **s BOM**.
    # Kdyby se mutace zapsala bez BOM, `blok_generatoru()` by ho nenašel (čte
    # `utf-8-sig`, ten BOM odřízne i když tam není) a **měřil by se jiný jev**.
    # Proto se BOM detekuje a vrací zpět — u obou souborů.
    ma_bom = puvodni.startswith(b"\xef\xbb\xbf")
    text = puvodni.decode("utf-8-sig") if ma_bom else puvodni.decode("utf-8")
    pocet = text.count(stary)
    assert pocet == pocet_cekany, f"{cesta.name}: hledaný text je {pocet}x, očekáván {pocet_cekany}x"
    zmut = text.replace(stary, novy, pocet_cekany)
    assert zmut != text, "MUTACE SE NEPROVEDLA (text se nezměnil)"
    assert stary not in zmut, "MUTACE SE NEPROVEDLA (starý text v mutaci ZŮSTAL)"
    kodovani = "utf-8-sig" if ma_bom else "utf-8"
    try:
        cesta.write_bytes(zmut.encode(kodovani))
        na_disku = cesta.read_bytes().decode(kodovani)
        assert na_disku == zmut, "mutace není na disku"
        assert (cesta.read_bytes().startswith(b"\xef\xbb\xbf")) == ma_bom, \
            "změnil se BOM souboru — to je jiná mutace, než jsme chtěli"
        assert stary not in na_disku, "MĚŘENÁ PODMÍNKA POŘÁD PLATÍ (starý text je na disku)"
        return funkce()
    finally:
        cesta.write_bytes(puvodni)
        assert cesta.read_bytes() == puvodni, f"{cesta.name} NEVRÁCEN BAJT NA BAJT!"


def zkontroluj_radek(v: str, popis: str, hledany: str, ok: bool = True) -> None:
    zkontroluj(popis, (hledany in v) == ok,
               "\n".join(l for l in v.splitlines() if hledany.split()[0] in l)[:400])


# ───────────────────────────── A) g3-brany.py ────────────────────────────────
print("=" * 78)
print("A) g3-brany.py — cesty se odvozují (nález H48)")
print("=" * 78)
print("--- A1) zdravý stav: kolik záznamníků zůstalo nedosazených? ---")
kod, v = spust([sys.executable, str(G3)])
radek = [l for l in v.splitlines() if "záznamníky cest" in l]
zkontroluj("g3 proběhl (exit 0 — je to PŘEHLED, ne blokující brána)", kod == 0, f"exit={kod}")
zkontroluj("0 nedosazených záznamníků", any("0 nedosazených" in l for l in radek),
           "\n".join(radek) or "(řádek o záznamnících chybí)")
pocet_bran = [l for l in v.splitlines() if l.startswith("brán celkem")]
zkontroluj("g3 vypsal počet bran", bool(pocet_bran), "\n".join(pocet_bran))
zkontroluj("v přehledu NEJSOU brány s „can't open file“",
           "can't open file" not in v,
           "\n".join(l for l in v.splitlines() if "can't open file" in l)[:400])

print()
print("--- A2) vrácená vada: ZÁZNAMNÍK SE NEDOSADÍ ---")
print("    (přesně to byla vada H48: cesta zůstala jako `orchestra/tools/...`)")
# ⚠ PRVNÍ VERZE TÉHLE MUTACE BYLA ŠPATNÁ a stálo za to ji popsat: měnila
# `"<TOOLS>/over-skilly.py"` na `"orchestra/tools/over-skilly.py"`. To ale není
# vada H48 — to je jen **jiná (neexistující) cesta**, a `dosad()` s ní nic dělat
# nemusí. `NEDOSAZENÉ CESTY` správně mlčelo. Měřená podmínka se proto obrací
# přímo: **vypne se substituce** a záznamník zůstane v příkazu, takže soubor
# s ostrými závorkami v cestě neexistuje.
STARY_DOSAD = '                    cast = cast.replace(znacka, str(cesta).replace("\\\\", "/"))'
VADNY_DOSAD = '                    cast = cast  # MUTACE: substituce vypnuta'


def _mer_a2():
    kod2, v2 = spust([sys.executable, str(G3)])
    zkontroluj("s vadou g3 stále doběhne (je to přehled)", kod2 == 0, f"exit={kod2}")
    zkontroluj("vada je VIDĚT: g3 pojmenuje brány, které vůbec nezačaly",
               "BRÁNY, KTERÉ VŮBEC NEZAČALY" in v2,
               "\n".join(l for l in v2.splitlines() if "over-skilly" in l)[:400])
    zkontroluj("nedosazené záznamníky jsou pojmenované",
               "NEDOSAZENÉ CESTY" in v2,
               "\n".join(l for l in v2.splitlines() if "NEDOSAZEN" in l)[:400])
    zkontroluj("brána over-skilly se s vadou nepočítá jako OK",
               any("over-skilly" in l and "exit=" in l for l in v2.splitlines()),
               "\n".join(l for l in v2.splitlines() if "over-skilly" in l)[:400])


mutuj(G3, STARY_DOSAD, VADNY_DOSAD, _mer_a2)
print("    (g3 vrácen bajt na bajt)")

# ─────────────────── B) test-gitignore-tajemstvi.py ──────────────────────────
print()
print("=" * 78)
print("B) tools/test-gitignore-tajemstvi.py — kontrakt generátor ↔ hra (H49)")
print("=" * 78)
print("--- B1) zdravý stav ---")
kod, v = spust([sys.executable, str(GITIGNORE_TEST)])
m = [l for l in v.splitlines() if l.startswith("VÝSLEDEK:")]
zkontroluj("test prošel (exit 0)", kod == 0, f"exit={kod}\n" + "\n".join(m))
zkontroluj("hlásí N kontrol, 0 chyb", any("0 chyb" in l for l in m), "\n".join(m))
# ⚠ „0 kontrol, 0 chyb" NENÍ zelená (zadání to říká výslovně) — počet se čte.
import re
mm = re.search(r"VÝSLEDEK: (\d+) kontrol", v)
zkontroluj("počet kontrol je NENULOVÝ", bool(mm) and int(mm.group(1)) > 0,
           f"nalezeno: {mm.group(1) if mm else '?'}")

print()
print("--- B2) vrácená vada: z generátoru zmizí `.env` ---")
print("    (to je přesně díra, kvůli které test existuje: tajemství by šlo do gitu)")
# Kotva je `.env` jako SAMOSTATNÝ ŘÁDEK **na začátku řádku** (v bloku `@'...'@`
# NENÍ odsazený). ⚠ KONCE ŘÁDKŮ SE MUSÍ ZJISTIT, NE HÁDAT: soubor je `.ps1`
# a **má CRLF** — naměřeno: `\n.env\n` má **0 výskytů**, správně je `\r\n.env\r\n`.
# (Kdyby se to neověřilo, mutace by se ticho neprovedla a test by hlásil
# „brána neměří" — přesně past z `overovani` §7.9.)
_B = GENERATOR.read_bytes()
NL = "\r\n" if b"\r\n" in _B else "\n"
assert (_B.count(b"\r\n") == 0) or (_B.count(b"\n") == _B.count(b"\r\n")), \
    "soubor má SMÍŠENÉ konce řádků — kotva by mohla trefit jiné místo"
KOTVA_ENV = NL + ".env" + NL
assert _B.decode("utf-8-sig").count(KOTVA_ENV) == 1, \
    "kotva `.env` není v generátoru právě jednou"


def _mer_b2():
    kod2, v2 = spust([sys.executable, str(GITIGNORE_TEST)])
    zkontroluj("s vadou test SPADNE (exit 1)", kod2 == 1, f"exit={kod2}")
    zkontroluj("vada je pojmenovaná (CHYBA u generátoru)",
               "CHYBA" in v2 and ".env" in v2,
               "\n".join(l for l in v2.splitlines() if "CHYBA" in l)[:400])
    zkontroluj("souhrn hlásí nenulový počet chyb",
               bool(re.search(r"VÝSLEDEK: \d+ kontrol, [1-9]\d* CHYB", v2)),
               "\n".join(l for l in v2.splitlines() if l.startswith("VÝSLEDEK")))


mutuj(GENERATOR, KOTVA_ENV, NL + "# .env (MUTACE: řádek vyndán)" + NL, _mer_b2)
print("    (generátor vrácen bajt na bajt)")

# ───────────────────────── C) verify-setup.py ────────────────────────────────
print()
print("=" * 78)
print("C) tools/verify-setup.py — struktura stanice a obou repů (H50)")
print("=" * 78)
print("--- C1) zdravý stav ---")
kod, v = spust([sys.executable, str(VERIFY)])
m = re.search(r"ZMĚŘENO: (\d+) kontrol, (\d+) chyb", v)
zkontroluj("verify-setup prošel (exit 0)", kod == 0, f"exit={kod}")
zkontroluj("VYPISUJE ČÍTAČ (bez něj je zelená jen ticho)", bool(m),
           "\n".join(l for l in v.splitlines() if "ZMĚŘENO" in l) or "(čítač chybí)")
zkontroluj("počet kontrol je NENULOVÝ", bool(m) and int(m.group(1)) > 0,
           f"kontrol={m.group(1) if m else '?'}")

print()
print("--- C2) vrácená vada: kořen stanice nasměrovaný jinam ---")
print("    (přesně to byla vada H50: pevná cesta na starý kořen)")
kod2, v2 = spust([sys.executable, str(VERIFY)],
                 env={"FORGE_STANICE": str(WS / "_neexistuje-stanice")})
zkontroluj("s vadou nástroj SPADNE (exit 1)", kod2 == 1, f"exit={kod2}")
zkontroluj("vada je pojmenovaná", "neexistuje" in v2.lower() or "CHYBA" in v2,
           v2.strip()[:300])

# ────────── E) hl-neanglicky-v-kodu.py — vidí NETRACKOVANÉ (H52) ─────────────
print()
print("=" * 78)
print("E) skener vidí NETRACKOVANÉ soubory (nález H52)")
print("=" * 78)
SOUBOR = WS / "_analyza" / "test-h52-untracked.py"
INV = ANALYZA / "_test-h52-inventar.json"

# Soubor se ZÁMĚRNĚ českým identifikátorem — to je to, co brána hledá.
OBSAH = (
    "# -*- coding: utf-8 -*-\n"
    "# P13c: dočasný NETRACKOVANÝ soubor pro mutační test nálezu H52.\n"
    "def změř_něco() -> int:\n"
    "    return 1\n"
)
try:
    SOUBOR.write_bytes(OBSAH.encode("utf-8"))
    # Pojistka: soubor opravdu NENÍ v gitu (jinak by test měřil trackovaný stav).
    r = subprocess.run([str(TOOLS / "git.cmd"), "-C", str(WS), "ls-files",
                        "--error-unmatch", "_analyza/test-h52-untracked.py"],
                       capture_output=True, shell=True)
    zkontroluj("testovací soubor NENÍ v gitu (jinak by test nic nedokázal)",
               r.returncode != 0, f"git ls-files vrátil {r.returncode}")

    kod, _ = spust([sys.executable, str(SKENER), "--json", str(INV)])
    data = json.loads(INV.read_text(encoding="utf-8"))
    soubory = {n["soubor"] for n in data["nalezy"]}
    zkontroluj("NETRACKOVANÝ soubor s českým identifikátorem je v inventáři",
               any("test-h52-untracked.py" in s for s in soubory),
               f"v inventáři je {len(soubory)} souborů s nálezy")
    zkontroluj("inventář ho hlásí i v `netrackovane` (je to VIDĚT v datech)",
               any("test-h52-untracked.py" in s
                   for sez in data.get("netrackovane", {}).values() for s in sez),
               json.dumps(data.get("netrackovane", {}), ensure_ascii=False)[:300])
    zkontroluj("identifikátor `změř_něco` je mezi nálezy (ne jen soubor)",
               any("změř_něco" in n["text"] for n in data["nalezy"]),
               "\n".join(f"{n['soubor']}:{n['radek']} {n['text'][:50]}"
                         for n in data["nalezy"] if "h52" in n["soubor"])[:300])
finally:
    for p in (SOUBOR, INV):
        if p.exists():
            p.unlink()

print()
print("--- E2) vrácená vada: soubor spadne do VZORU ARTEFAKTŮ ---")
# ⚠ PRVNÍ VERZE TOHOHLE TESTU BYLA ŠPATNÁ a stojí za to ji popsat: vylučovala
# soubor jen podle `_` prefixu (`_test-h52-untracked.py`). Jenže vzor artefaktů
# **záměrně** vylučuje z `_analyza/` jen `_*.json` (mezivýstupy skeneru) a
# `*-vystup.txt` — **žádný `.py`**. A to je SPRÁVNĚ: kdyby vylučoval i `.py`,
# byl by slepý právě na živý kód, kvůli kterému existuje (H52).
# Měřená podmínka se proto bere tam, kde vzor opravdu platí: na MEZIVÝSTUP.
ARTEFAKT = WS / "_analyza" / "_test-h52-artefakt.json"
ZIVY_PY = WS / "_analyza" / "_test-h52-zivy.py"
try:
    # (a) `_*.json` v `_analyza/` = mezivýstup skeneru → MUSÍ se vyloučit.
    ARTEFAKT.write_bytes(OBSAH.encode("utf-8"))
    # (b) `_*.py` v `_analyza/` = ŽIVÝ KÓD → vyloučit se NESMÍ (jinak slepá brána).
    ZIVY_PY.write_bytes(OBSAH.encode("utf-8"))
    kod, _ = spust([sys.executable, str(SKENER), "--json", str(INV)])
    data = json.loads(INV.read_text(encoding="utf-8"))
    nalezy2 = [n["soubor"] for n in data["nalezy"]]
    zkontroluj("_*.json v `_analyza/` JE VYLOUČENÝ (v nálezech není)",
               not any("_test-h52-artefakt.json" in s for s in nalezy2),
               "\n".join(s for s in nalezy2 if "artefakt" in s)[:300])
    zkontroluj("a NENÍ ani v NEPOKRYTO (to by znamenalo „skener ho zkusil a vzdal“)",
               not any("_test-h52-artefakt" in str(x) for x in data.get("nepokryto", [])),
               str(data.get("nepokryto", []))[:300])
    zkontroluj("vyloučení je PŘIZNANÉ (klíč `vyloucene_artefakty` v datech je)",
               "vyloucene_artefakty" in data,
               json.dumps(data.get("vyloucene_artefakty", {}), ensure_ascii=False))
    # ⚠ A tohle je pojistka proti PŘEhnané exkluzi — slepá brána je horší než hlučná.
    zkontroluj("_*.py v `_analyza/` vyloučený NENÍ (jinak by brána byla slepá na kód)",
               any("_test-h52-zivy.py" in s for s in nalezy2),
               f"nálezy v _analyza: {len(nalezy2)}")
finally:
    for p in (ARTEFAKT, ZIVY_PY, INV):
        if p.exists():
            p.unlink()

print()
print("=" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
print("=" * 78)
sys.exit(1 if chyb else 0)
