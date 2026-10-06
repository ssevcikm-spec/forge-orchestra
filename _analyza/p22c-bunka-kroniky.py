# -*- coding: utf-8 -*-
r"""Doplnění chybějící buňky v kronice §3 (blok `1–13`, sloupec „nálezů o cizím kódu").

PROČ: součet sloupce je **51**, ale souhrn tvrdí **54** — a rozdíl **3** dělá
**jediná nevyplněná buňka** (`—`) v bloku `1–13`. Není to zastaralý souhrn:
omylů i vad měřidla sedí na puntík (**205 = 205**, **178 = 178**). Rozhodnutí
(6. 10. 2026): buňka se **nedomýšlí** — označí se jako **nedoložená**, protože
u bloku `1–13` (30. 9. – 1. 10. 2026) se ten sloupec **nikdy nevedl**.

⚠ Historická čísla se NEPŘEPISUJÍ (`dokumentace` §1.8): řádek bloku se mění
jen v tom, že `—` dostane **význam**; souhrn `54` zůstává, ale přestane být
bez vysvětlení.

Idempotentní, zapisuje bajty (LF).
"""
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
K = WS / "KRONIKA-PROJEKTU.md"

STARY_RADEK = "| **1–13** | 30. 9. – 1. 10. | **13** | **9** | — |"
NOVY_RADEK = "| **1–13** | 30. 9. – 1. 10. | **13** | **9** | **neurčeno** |"

VYSVETLENI = """> **⚠ DOPLNĚNO 6. 10. 2026 — CO ZNAMENÁ `neurčeno` V BLOKU `1–13`:**
> Sloupec „nálezů o cizím kódu“ se u bloku `1–13` (30. 9. – 1. 10. 2026)
> **nikdy nevedl**, takže součet řádků je **51**, kdežto souhrn tvrdí **54**.
> **Není to zastaralý souhrn** — omylů i vad měřidla sedí na puntík
> (**205 = 205**, **178 = 178**, naměřeno `_tools\\over-souhrn-kroniky.mjs`).
> **Hodnota se NEDOMÝŠLÍ** (doplnit „3“ by znamenalo zapsat nezměřené jako
> změřené); `neurčeno` je **přiznaná mez**, ne nula. Historický řádek se
> **nepřepisuje** — dostal jen **význam**.
"""

kontrol = 0
chyb = []


def k(ok: bool, popis: str) -> None:
    global kontrol
    kontrol += 1
    print(f"  {'OK  ' if ok else 'CHYBA'}  {popis}")
    if not ok:
        chyb.append(popis)


print("=" * 78)
print("Kronika §3 — doplnění významu chybějící buňky (blok 1–13)")
print("=" * 78)

puvodni = K.read_bytes()
text = puvodni.decode("utf-8")
radky = text.splitlines(keepends=True)

k("\r" not in text, "kronika má LF (zapisuje se bajty)")

uz = any(r.startswith("| **1–13** | 30. 9. – 1. 10. | **13** | **9** | **neurčeno** |") for r in radky)
if uz:
    print("  OK    buňka už je označená `neurčeno` — neměním")
    kontrol += 1
else:
    i = next((n for n, r in enumerate(radky) if r.startswith(STARY_RADEK)), None)
    k(i is not None, "kotva: řádek bloku `1–13` s nevyplněným sloupcem")
    if i is not None:
        radky[i] = radky[i].replace(STARY_RADEK, NOVY_RADEK)
        k("**neurčeno**" in radky[i], "sloupec `—` nahrazen za `neurčeno`")

uz_v = "CO ZNAMENÁ `neurčeno`" in text
if uz_v:
    print("  OK    vysvětlení už v dokumentu je — nevkládám")
    kontrol += 1
else:
    # Vysvětlení patří POD tabulku bloků a NAD poznámky o souhrnu — kotva je
    # první z těch poznámek („SOUHRNNÝ ŘÁDEK BYL DO 5. 10. 2026 ZASTARALÝ“).
    kotva = "> **⚠ SOUHRNNÝ ŘÁDEK BYL DO 5. 10. 2026 ZASTARALÝ"
    j = next((n for n, r in enumerate(radky) if r.startswith(kotva)), None)
    k(j is not None, "kotva: poznámka o souhrnném řádku")
    if j is not None:
        radky.insert(j, VYSVETLENI + "\n")
        k(any("CO ZNAMENÁ `neurčeno`" in r for r in radky), "vysvětlení vloženo pod tabulku")

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
k("| **1–13** | 30. 9. – 1. 10. | **13** | **9** | **neurčeno** |" in t2, "řádek má `neurčeno`")
k("CO ZNAMENÁ `neurčeno`" in t2, "vysvětlení je v dokumentu")
k("| **celkem** | **27 bloků, 35 sessions** | **208** | **181 = 87 %** | **54** |" in t2,
  "souhrn §3 zůstal (54 se nevydává za změřené, jen je vysvětlené)")

print()
print("=" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {len(chyb)} chyb")
print("=" * 78)
for c in chyb:
    print(f"  CHYBA: {c}")

sys.exit(1 if chyb else 0)
