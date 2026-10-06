# -*- coding: utf-8 -*-
r"""P23k — řádek session do kroniky §1 za schválené práce (6. 10. 2026).

PROČ SKRIPTEM: řádky tabulky §1 mají **přes 2000 znaků**, takže kotva z načteného
řádku by ho NAHRADILA zkráceným textem (omyl **194**, **206**). Bere se proto
z disku a vkládá ZA poslední řádek.

⚠ Počet omylů v řádku je **`—`**: uživatel 6. 10. 2026 rozhodl **„omyly nepiš“**.
Není to nula — je to **vědomě nevedený sloupec**, a proto se **nepřičítá** do
souhrnu §3 (kdyby tam nula byla, tvrdilo by to „žádný omyl“, což je taky tvrzení).

Idempotentní, zapisuje bajty (LF).
"""
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
K = WS / "KRONIKA-PROJEKTU.md"

RADEK_37 = (
    "| **37** | **6. 10. 2026** (17:0x–20:0x +02:00 = 15:0x–18:0x UTC) | "
    "**rozhodovací (schválené práce)** | **P23k: SCHVÁLENÉ PRÁCE** — uživatel rozhodl: "
    "„omyly nepiš, zbytek KB souhlasím, **body revize rituálu schvaluji**, drobnosti "
    "rozhodni sám“. Provedeno: **revize rituálu** (body **1, 3, 5, 6** aplikovány do "
    "`PREDAVANI-SESSION.md` §2.4–§2.7 + checklist §7), **tři drobnosti** rozhodnuty, "
    "**§6.14** (jedna autorita seznamu živých) a **§6.10** (buňka kroniky) | "
    "`PREDAVANI-SESSION.md` má **4 nové sekce** a **4 nové povinné položky** checklistu · "
    "`ag-over-cisla.py` **zařazen do `validate-all.mjs`** (mez přiznaná: **5 měřených "
    "čísel**, zbytek nehlídá) · `lint-roadmapa.py` rozlišuje **blokující 3** od "
    "**poradních 13** (závisí na nespolehlivém `done`, nález H105) — `exit 0` · "
    "kronika §3: buňka `1–13` = **`neurčeno`** (hodnota se **nedomýšlí**) · "
    "`_registr-bran.json` **generuje `g3`** (37 bran s `exit`, čítačem, příkazem; "
    "v režimu `--soubor` se nezapisuje) · **dvě vady nástroje** "
    "`_tools\\over-souhrn-kroniky.mjs` opraveny (dvouznakový blok `8za` → součet "
    "**192 → 208**; slovo `neurčeno` místo `—`) a **mutačně ověřeny**: "
    "`_tools\\test-over-souhrn-kroniky.mjs` **7/0** | **—** | "
    "**NÁLEZ (týž vzorec potřetí): měřidlo přehlíželo DVOUZNAKOVÝ blok omylů** — "
    "`[a-z]?` bere jedno písmeno, takže `8za` (vznikl, protože `8a`–`8z` jsou "
    "obsazené) se do součtu **nepočítal** a součet vypadal jako nález o datech. "
    "**A druhá polovina téhož:** buňka `—` se četla jako nevyplněná, ale po "
    "rozhodnutí je v ní slovo `neurčeno` → `NaN` a **řádek by tiše zmizel**. "
    "Obě vady odhalilo **přeměření**, ne čtení · **Co zůstává:** §6.4+6.8 (přesun "
    "znalosti z `orchestra` skillu do hry), §6.5+6.6 (PŘESUN trvalých pravidel), "
    "§6.11 (569 tis. znaků historie z `HANDOFF.md`), §6.9 — **schválené, ale patří "
    "session s nezávislým ověřením** (`ZADANI-OPTIMALIZACE-KB.md`) |"
)

kontrol = 0
chyb = []


def k(ok: bool, popis: str) -> None:
    global kontrol
    kontrol += 1
    print(f"  {'OK  ' if ok else 'CHYBA'}  {popis}")
    if not ok:
        chyb.append(popis)


print("=" * 78)
print("Kronika §1 — řádek session 37 (schválené práce P23k)")
print("=" * 78)

puvodni = K.read_bytes()
text = puvodni.decode("utf-8")
radky = text.splitlines(keepends=True)
k("\r" not in text, "kronika má LF (zapisuje se bajty)")

if any(r.startswith("| **37** |") for r in radky):
    print("  OK    řádek 37 už v kronice je — nevkládám")
    kontrol += 1
else:
    i36 = next((n for n, r in enumerate(radky) if r.startswith("| **36** |")), None)
    k(i36 is not None, "kotva: řádek session 36")
    if i36 is not None:
        konec = "\n" if radky[i36].endswith("\n") else ""
        radky.insert(i36 + 1, RADEK_37 + konec)
        k(any(r.startswith("| **37** |") for r in radky), "řádek 37 vložen ZA řádek 36")

nove = "".join(radky).encode("utf-8")
if nove != puvodni:
    K.write_bytes(nove)
    print(f"  ZAPSÁNO: KRONIKA-PROJEKTU.md ({len(puvodni)} → {len(nove)} B)")
else:
    print("  beze změny")

zpet = K.read_bytes()
k(zpet == nove, "soubor na disku odpovídá zapsanému")
k(not zpet.startswith(b"\xef\xbb\xbf"), "kronika nemá BOM")
k(zpet.count(b"\r\n") == 0, "v kronize nejsou CRLF")
t2 = zpet.decode("utf-8")
k("| **37** |" in t2, "dokument obsahuje řádek 37")
k("body **1, 3, 5, 6**" in t2, "řádek jmenuje schválené body revize")

# Souhrn §3 se NESMÍ přepočítat: řádek 37 nemá omyly (uživatel je nechce vést).
k("| **celkem** | **27 bloků, 35 sessions** | **208** | **181 = 87 %** | **54** |" in t2,
  "souhrn §3 zůstal 27 bloků / 35 sessions / 208 (řádek 37 omyly nevede)")

print()
print("=" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {len(chyb)} chyb")
print("=" * 78)
for c in chyb:
    print(f"  CHYBA: {c}")

sys.exit(1 if chyb else 0)
