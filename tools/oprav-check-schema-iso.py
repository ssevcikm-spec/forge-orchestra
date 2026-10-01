"""Naučí kontrolu schématu poznat IZOMETRICKÝ renderer podle skutečného kódu.

PROČ: `check-schema.py` vznikl tak, že hledal konkrétní podezřelý vzorec
(`Vector2(x*cell, y*cell)` + `scale` 1:1) a hlásil izometrii jako chybějící.
Jenže `level.gd` se pak PŘEPSAL na izometrii – a kontrola pokračovala ve
hlášení vady, protože hledala starý text.

To je poučné: **kontrola, která zná jen „jak to vypadalo špatně", hlásí falešný
poplach i po opravě** – a falešný poplach je nebezpečný, protože nutí
„opravovat" něco, co je v pořádku, nebo odnaučí lidi kontrole věřit.

Nová logika je robustnější a je postavená na TŘECH nezávislých znacích:
  1. negativní: starý čtvercový vzorec `Vector2(x * cell, y * cell)` tam NENÍ,
  2. pozitivní: renderer čte schéma ze `spec.json` (SPEC_PATH / projekce),
  3. pozitivní: existuje `je_izometricka()` nebo `iso_position`.

A když ani jeden pozitivní znak není, vypíše se to jako POZNÁMKA („nedá se
posoudit"), ne jako vada – protože „nevím" a „je to špatně" nejsou totéž.

Použití: python orchestra/tools/oprav-check-schema-iso.py
"""
from __future__ import annotations

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOPIE = [
    pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek\orchestra\repo\.forge\check-schema.py"),
    pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek\games\uo-shadows\.forge\check-schema.py"),
    pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek\orchestra\tools\kontrole-schematu.py"),
]
# zdrojový nástroj má jiné jméno
KOPIE[2] = pathlib.Path(
    r"C:\Users\Ssevc\Local-Deepseek\orchestra\tools\kontrole-schematu.py".replace(
        "kontrole-schematu", "kontrola-schematu"))

STARE = '''            # Izometrie vzniká jen tím, že RENDERER staví dlaždice zkosené.
            # Ověřuje se strukturně: najde se v level.gd skutečný izometrický
            # vzorec (zúžení x, půlení y), NE jen jakékoli dělení číslem.
            # (První verze hledala `/ 2` a propustila i čtvercový renderer –
            # benevolentní kontrola je horší než žádná, protože budí důvěru.)
            ma_iso_skalovani = bool(re.search(
                r"scale\\s*=\\s*Vector2\\([^)]*/\\s*2|iso_position|Vector2\\(\\s*\\(?\\s*\\w+\\s*-\\s*\\w+",
                t))
            if not ma_iso_skalovani:
                vady.append(
                    "spec.json deklaruje IZOMETRICKOU projekci (dlaždice "
                    f"{tile_w}×{tile_h}), ale scripts/level.gd staví dlaždice osově "
                    "zarovnaně (s.position = offset + Vector2(x*cell, y*cell), scale "
                    "1:1) – izometrický pohled takto nemůže vzniknout, ať se sprity "
                    "ladí jakkoli")
            # A druhá polovina téže vady: kdo má izometrii na starosti, musí ji
            # mít zapojenou. Pokud level.gd neumí iso projekci a world.gd (která ji
            # má) se nikde nepoužívá, izometrie v projektu NENÍ – jen v komentáři.
            if not re.search(r"iso_position|iso_z|iso\\(", t):
                wg_txt = ""
                if wg.is_file():
                    wg_txt = wg.read_text(encoding="utf-8", errors="replace")
                pouziva_world = bool(re.search(r"world\\.gd|world\\.iso|World", t))
                if re.search(r"iso_position", wg_txt) and not pouziva_world:
                    vady.append(
                        "izometrická projekce je jen v scripts/world.gd (iso_position), "
                        "ale level.gd ji nepoužívá – izometrie tedy v projektu NENÍ, "
                        "jen v komentáři. Buď ji level.gd převezme, nebo se spec.json "
                        "přepíše na čtvercovou projekci")'''

NOVE = '''            # Izometrie se ověřuje TŘEMI nezávislými znaky, protože hledat
            # jeden konkrétní vzorec je křehké: kontrola pak hlásí vadu i po
            # opravě (přesně to se stalo – `level.gd` se přepsal na izometrii
            # a kontrola dál tvrdila, že kreslí čtvercově, protože hledala
            # starý text). Falešný poplach nutí „opravovat" správný kód.
            stary_ctverec = bool(re.search(r"Vector2\\(\\s*\\w+\\s*\\*\\s*cell\\s*,", t))
            cte_spec = bool(re.search(r"SPEC_PATH|spec\\.json|projekce", t))
            ma_iso_metodu = bool(re.search(r"je_izometricka|iso_position|iso_z", t))
            if stary_ctverec:
                vady.append(
                    "spec.json deklaruje IZOMETRICKOU projekci (dlaždice "
                    f"{tile_w}×{tile_h}), ale scripts/level.gd staví dlaždice osově "
                    "zarovnaně (Vector2(x * cell, y * cell)) – izometrický pohled "
                    "takto nemůže vzniknout, ať se sprity ladí jakkoli")
            elif not cte_spec and not ma_iso_metodu:
                # „NEDÁ SE POSOUDIT" NENÍ VADA. Když kód neumíme přečíst, řekne
                # se to jako poznámka – vymyslet z toho vadu by bylo horší.
                poznamky.append(
                    "level.gd nevypadá ani čtvercově, ani izometricky – projekci "
                    "nejde z kódu posoudit (zkontroluj to očima)")
            if not ma_iso_metodu:
                wg_txt = ""
                if wg.is_file():
                    wg_txt = wg.read_text(encoding="utf-8", errors="replace")
                if re.search(r"iso_position", wg_txt):
                    vady.append(
                        "izometrická projekce je jen v scripts/world.gd (iso_position), "
                        "ale level.gd ji nepoužívá – izometrie tedy v projektu NENÍ, "
                        "jen v komentáři")'''

upraveno = 0
for cesta in KOPIE:
    if not cesta.is_file():
        print(f"  --   {cesta.name}: neexistuje, přeskakuji")
        continue
    t = cesta.read_text(encoding="utf-8")
    if "stary_ctverec" in t:
        print(f"  --   {cesta.parent.parent.name}\\{cesta.name}: už upraveno")
        continue
    if STARE not in t:
        print(f"  CHYBA {cesta.parent.parent.name}\\{cesta.name}: nenalezen blok")
        continue
    cesta.write_text(t.replace(STARE, NOVE, 1), encoding="utf-8")
    upraveno += 1
    print(f"  OK   {cesta.parent.parent.name}\\{cesta.name}: 3 znaky + poznámka místo vady")

print()
print(f"Upraveno: {upraveno}")
