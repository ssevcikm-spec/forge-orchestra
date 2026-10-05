#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""G — ZÁLOHA `_analyza/_archiv` (a `_analyza/_zaloha*`) MIMO REPO.

PROČ TO EXISTUJE (otevřený bod z §29.7 a §30.18, P13c ani P14 ho neuzavřely)
--------------------------------------------------------------------------
`_analyza/_archiv/` je **jediná cesta zpět** k 344 jednorázovým nástrojům
(D5, přesun na `E:`) — a je **gitignorovaný** (`.gitignore:72`), takže **v gitu
není**. Když se smaže, není odkud ho vzít.

ROZHODNUTÍ (AKČNÍ session P15, 5. 10. 2026)
------------------------------------------
**Kam:** `C:\Users\Ssevc\Local-Deepseek\_zalohy\forge-orchestra\` — tedy na
**JINÝ DISK** než repa (ta jsou na `E:`). Důvod: záloha na témž disku chrání
jen proti smazání, ne proti výpadku disku; kdyby padl `E:`, přežije kořen
stanice na `C:` **i s touhle zálohou**.
**Čím:** tenhle skript — kopíruje **bajty**, vede **SHA-256 manifest** a po
zápisu **ověří kopii čtením z disku** (ne z paměti). `exit 0` = záloha sedí.

Přepínače:
  `--jen-kontrola`  nic nekopíruje, jen ověří, že záloha odpovídá zdroji.
  `--cil <cesta>`   jiný cíl (nebo proměnná `FORGE_ZALOHA`).

Nic v repu se nemění a nic se **nemaže** (ani ze zálohy) — mazání do zálohy
nepatří; co v záloze přebývá, se jen **vypíše**.

Použití:  python _analyza\zalohuj-archiv.py
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(os.environ.get("FORGE_WS") or pathlib.Path(__file__).resolve().parents[1])
ANALYZA = WS / "_analyza"
VYCHOZI_CIL = pathlib.Path(
    os.environ.get("FORGE_ZALOHA") or r"C:\Users\Ssevc\Local-Deepseek\_zalohy\forge-orchestra")
CIL = VYCHOZI_CIL
JEN_KONTROLA = "--jen-kontrola" in sys.argv
if "--cil" in sys.argv:
    CIL = pathlib.Path(sys.argv[sys.argv.index("--cil") + 1])

# Co se zálohuje: archiv + případné `_zaloha*` adresáře vedle něj.
ZDROJE = [ANALYZA / "_archiv"] + sorted(
    p for p in ANALYZA.glob("_zaloha*") if p.is_dir())


def sha256(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def sesbirej(koren: pathlib.Path, zaklad: pathlib.Path) -> dict[str, str]:
    return {str(p.relative_to(zaklad)).replace("\\", "/"): sha256(p)
            for p in sorted(koren.rglob("*")) if p.is_file()}


kontrol = 0
chyb = 0


def zkontroluj(popis: str, ok: bool, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    if not ok:
        chyb += 1
    print(f"  {'OK   ' if ok else 'CHYBA'} {popis}")
    if not ok and detail:
        for r in str(detail).splitlines()[:12]:
            print(f"        {r}")


print("=" * 88)
print("G — ZÁLOHA `_analyza/_archiv` MIMO REPO (bajty + SHA-256 manifest)")
print("=" * 88)
print(f"  zdroj(e) = {', '.join(str(z) for z in ZDROJE)}")
print(f"  cíl      = {CIL}")
print(f"  režim    = {'JEN KONTROLA' if JEN_KONTROLA else 'kopírovat + ověřit'}")
print()

zdroje_ok = [z for z in ZDROJE if z.is_dir()]
zkontroluj(f"zdrojové adresáře existují ({len(zdroje_ok)} z {len(ZDROJE)})",
           bool(zdroje_ok), "\n".join(str(z) for z in ZDROJE))

manifest: dict = {"verze": 1, "zdroje": {}, "soubory": {}}
celkem = 0
bajtu = 0

for zdroj in zdroje_ok:
    jmeno = zdroj.name
    obsah = sesbirej(zdroj, zdroj)
    manifest["zdroje"][jmeno] = {"souboru": len(obsah)}
    celkem += len(obsah)
    bajtu += sum((zdroj / k).stat().st_size for k in obsah)
    print(f"  {jmeno}: {len(obsah)} souborů, "
          f"{sum((zdroj / k).stat().st_size for k in obsah) / 1e6:.2f} MB")
    for rel, h in obsah.items():
        cil_rel = f"{jmeno}/{rel}"
        if cil_rel in manifest["soubory"]:
            print(f"  POZN  stejné relativní jméno ve dvou zdrojích: {cil_rel}")
        manifest["soubory"][cil_rel] = h
        if not JEN_KONTROLA:
            c = CIL / cil_rel
            c.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(zdroj / rel, c)

print()
zkontroluj(f"zdroje mají aspoň 300 souborů (archiv byl 344 v P13c) — je {celkem}",
           celkem >= 300, str(celkem))

# ── OVĚŘENÍ KOPIE: čte se Z DISKU, ne z paměti ─────────────────────────────
print("── OVĚŘENÍ ZÁLOHY (čtení z disku) ──────────────────────────────────────")
chybejici: list[str] = []
rozdilne: list[str] = []
for cil_rel, h in manifest["soubory"].items():
    c = CIL / cil_rel
    if not c.is_file():
        chybejici.append(cil_rel)
        continue
    if sha256(c) != h:
        rozdilne.append(cil_rel)
zkontroluj(f"v záloze je všech {len(manifest['soubory'])} souborů",
           not chybejici, "\n".join(chybejici[:12]))
zkontroluj("a všechny mají SHODNÝ SHA-256 se zdrojem", not rozdilne,
           "\n".join(rozdilne[:12]))

# Co v záloze přebývá — jen se VYPÍŠE, nemaže se.
prebyva = [str(p.relative_to(CIL)).replace("\\", "/")
           for p in CIL.rglob("*") if p.is_file()
           and str(p.relative_to(CIL)).replace("\\", "/") not in manifest["soubory"]
           and p.name not in ("MANIFEST.json", "MANIFEST.txt")]
if prebyva:
    print(f"  POZN  v záloze přebývá {len(prebyva)} souborů (NEMAŽE se): "
          f"{', '.join(prebyva[:6])}{' …' if len(prebyva) > 6 else ''}")

# ── MANIFEST ───────────────────────────────────────────────────────────────
CIL.mkdir(parents=True, exist_ok=True)
import datetime as _dt                                            # noqa: E402

cas = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
manifest["cas_utc"] = cas
manifest["souboru_celkem"] = len(manifest["soubory"])
manifest["bajtu_celkem"] = bajtu
(CIL / "MANIFEST.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8", newline="")
radky = [f"# ZÁLOHA _analyza (mimo repo) — {cas}",
         f"# souborů: {len(manifest['soubory'])}, bajtů: {bajtu}",
         "# sha256  cesta_v_zaloze"]
radky += [f"{h}  {k}" for k, h in sorted(manifest["soubory"].items())]
(CIL / "MANIFEST.txt").write_text("\n".join(radky) + "\n", encoding="utf-8", newline="")
zkontroluj("manifest (JSON i TXT) je v cíli",
           (CIL / "MANIFEST.json").is_file() and (CIL / "MANIFEST.txt").is_file())

print()
print("=" * 88)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb   |   "
      f"zálohováno {len(manifest['soubory'])} souborů, {bajtu / 1e6:.2f} MB → {CIL}")
if chyb:
    print(f"CHYBA: {chyb} — záloha NENÍ v pořádku")
    sys.exit(1)
print("ZÁLOHA SEDÍ: každý soubor je v cíli a má shodný SHA-256 se zdrojem.")
sys.exit(0)
