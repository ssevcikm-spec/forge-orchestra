# -*- coding: utf-8 -*-
r"""P20 — Úkol B: BOM v `.py` — VADA, NEBO NE? (nález H99, měření oběma směry)

CO SE MĚŘÍ (a proč to nejde odhadnout):
  * `python soubor.py` — co udělá INTERPRET s BOM na začátku (spuštění),
  * `compile(text)`      — co udělá KOMPILÁTOR, když mu text dáš jako ŘETĚZEC,
  * `ast.parse(text)`    — co udělá PARSER (a proč se to liší od `compile()`),
  * `utf-8-sig` vs `utf-8` — kde se BOM ztratí a kde zůstane,
  * a CO UDĚLAJÍ OBĚ BRÁNY (NA32 i H79) nad TÝMŽ souborem s BOM.

⚠ P19 zapsala (H99), že „jde spustit?" a „jde zkompilovat?" jsou DVĚ RŮZNÉ
OTÁZKY. Tenhle skript to měří na JEDNOM souboru, aby se to nedalo zaměnit.

⚠ Fixtura se NEDÁVÁ do živého stromu jako `.py` „naoko": kdyby zůstala, byla by
to VADA, kterou by brány správně nahlásily. Proto se zakládá v kategorii
`*-scratch` (tu obě brány vylučují a VYKAZUJÍ) a po měření se UKLIDÍ.
Kdyby se neuklidila, pozná to následný běh NA32/H79 — ne ticho.

Použití: python _analyza/p20-b-bom-mereni.py
Návratový kód: 0 = změřeno (ať vyšlo co chce), 1 = měření se nepovedlo.
"""

import ast
import os
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
FIX = ANALYZA / "p20-scratch" / "bom-fixtura"
SOUBOR = FIX / "bom-fixtura.py"

kontroly = []


def zk(ok: bool, popis: str, detail: str = "") -> None:
    kontroly.append((ok, popis, detail))
    print(f"  {'OK  ' if ok else 'CHYBA'} {popis}" + (f"\n      {detail}" if detail else ""))


print("=" * 78)
print("P20/B — BOM v `.py`: spustit vs. zkompilovat (H99)")
print("=" * 78)

FIX.mkdir(parents=True, exist_ok=True)
# ── 1) Fixtura S BOM: přesně to, co vznikne, když někdo zapíše .py přes
#      `Set-Content -Encoding utf8` (omyl 189 P19).
TELO = 'x = 1\nprint("fixtura s BOM: spusteno")\n'
SOUBOR.write_bytes(b"\xef\xbb\xbf" + TELO.encode("utf-8"))

bajty = SOUBOR.read_bytes()
print(f"\n--- 1) fixtura: {SOUBOR.relative_to(WS)}")
print(f"    první tři bajty: {bajty[:3].hex(' ')}   (EF BB BF = UTF-8 BOM)")
zk(bajty[:3] == b"\xef\xbb\xbf", "fixtura SKUTEČNĚ začíná BOM (bez toho by měření nic neříkalo)")

# ── 2) SPUSTIT: co udělá interpret s BOM na začátku souboru
r = subprocess.run([sys.executable, str(SOUBOR)], capture_output=True,
                   text=True, encoding="utf-8", errors="replace", cwd=str(WS), timeout=120)
print(f"\n--- 2) SPUŠTĚNÍ (`python {SOUBOR.name}`)")
print(f"    exit={r.returncode}  stdout={r.stdout.strip()!r}")
zk(r.returncode == 0, "soubor s BOM SE SPUSTÍ (exit 0)", f"exit={r.returncode}")
zk("spusteno" in (r.stdout or ""), "a dokonce i něco vypíše (není to tichý pád)")

# ── 3) ZKOMPILOVAT: `compile()` nad ŘETĚZCEM
print("\n--- 3) `compile(text)` — dvě čtení TÉHOŽ souboru")
text_utf8 = bajty.decode("utf-8")            # BOM ZŮSTANE jako znak U+FEFF
text_sig = bajty.decode("utf-8-sig")         # BOM se ODSTRANÍ
print(f"    utf-8:     první znak = U+{ord(text_utf8[0]):04X}  (délka {len(text_utf8)})")
print(f"    utf-8-sig: první znak = {text_utf8[0]!r} -> {text_sig[0]!r}  (délka {len(text_sig)})")

chyba_compile = None
try:
    compile(text_utf8, str(SOUBOR), "exec")
except Exception as e:                                        # noqa: BLE001
    chyba_compile = e
zk(chyba_compile is not None,
   "`compile()` nad textem S BOM SPADNE (to je to, co hlásí NA32)",
   f"{type(chyba_compile).__name__}: {chyba_compile}")
compile(text_sig, str(SOUBOR), "exec")
zk(True, "`compile()` nad TÝMŽ textem po `utf-8-sig` projde (BOM byl jediná příčina)")

# ── 4) `ast.parse()` — PROČ SE LIŠÍ (a proč to NENÍ totéž co `compile()`)
chyba_ast = None
try:
    ast.parse(text_utf8, filename=str(SOUBOR))
except Exception as e:                                        # noqa: BLE001
    chyba_ast = e
print("\n--- 4) `ast.parse(text)` nad TÝMŽ textem S BOM")
print(f"    výsledek: {'SPADL: ' + repr(chyba_ast) if chyba_ast else 'PROŠEL'}")
# ⚠ OMyl 195 (naměřeno tady, 6. 10. 2026): první verze tohohle skriptu tvrdila
# OPAK — že `ast.parse()` BOM PŘIJME a `compile()` ne. Byl to PŘEDPOKLAD, ne
# měření: obě funkce volají TÝŽ tokenizér, takže obě BOM odmítnou.
# (`ast.parse` = `compile(..., PyCF_ONLY_AST)`.) Rozdíl mezi bránami NA32 a H79
# tedy NENÍ v `compile` vs. `ast.parse` — je ve ČTENÍ souboru (viz sekce 5).
zk(chyba_ast is not None,
   "`ast.parse()` BOM ODMÍTNE stejně jako `compile()` (obě jdou přes tokenizér)",
   f"{type(chyba_ast).__name__}: {chyba_ast}")
zk(chyba_compile is not None and chyba_ast is not None
   and type(chyba_compile) is type(chyba_ast),
   "…a je to TÁŽ chyba — rozdíl mezi bránami tedy vzniká JINDE než tady")

# ── 5) KDE VZNIKÁ ROZDÍL: ve ČTENÍ SOUBORU
# `h79-escape-sken.py` má fallback `utf-8` → `utf-8-sig`, který BOM ODSTRANÍ.
# `n32-kompilovatelnost.py` čte jen `utf-8`, takže BOM zůstane v textu.
print("\n--- 5) čtení souboru: `utf-8` vs. fallback `utf-8-sig` (tady je rozdíl)")
sig_proslo = None
try:
    ast.parse(text_sig, filename=str(SOUBOR))
    sig_proslo = True
except Exception as e:                                        # noqa: BLE001
    sig_proslo = e
zk(sig_proslo is True,
   "po fallbacku `utf-8-sig` je text ČISTÝ a `ast.parse` projde → H79 nic nehlásí",
   "H79 se k BOM vůbec nedostane, protože ho při čtení odstraní")

# ── 6) CO UDĚLAJÍ OBĚ BRÁNY nad TÍMŽ souborem (fixtura v `*-scratch`)
print("\n--- 6) obě brány nad živým stromem (fixtura je v `*-scratch`)")
for nazev, skript in (("NA32 (kompilovatelnost)", ANALYZA / "n32-kompilovatelnost.py"),
                      ("H79  (escape sekvence)", ANALYZA / "h79-escape-sken.py")):
    if not skript.is_file():
        zk(False, f"{nazev}: skript existuje", str(skript))
        continue
    rr = subprocess.run([sys.executable, "-B", str(skript)], capture_output=True,
                        text=True, encoding="utf-8", errors="replace",
                        cwd=str(WS), timeout=600)
    v = (rr.stdout or "") + (rr.stderr or "")
    radky = [l for l in v.splitlines() if l.startswith("ZMĚŘENO")]
    souhrn = radky[-1] if radky else "(souhrn nenalezen)"
    print(f"    {nazev}: exit={rr.returncode}")
    print(f"      {souhrn}")
    # Fixtura je ve `*-scratch`, takže se NESMÍ počítat do živých — a musí
    # být VIDĚT ve vlastním čítači (jinak je vyloučení tiché).
    # ⚠ OMyl 196 (naměřeno tady): první verze psala `"*-scratch" in souhrn`,
    # ale `souhrn` je ŘÁDEK — a `in` nad řetězcem je substring, což projde.
    # Původně tam ale byl SEZNAM (`... in radky`) = test na PRVEK seznamu,
    # který NEMŮŽE projít. Kontrola, která nemá jak projít, je stejná vada
    # jako kontrola, která nemá jak selhat.
    zk("*-scratch" in souhrn,
       f"{nazev}: fixtura je VYKÁZANÁ v kategorii `*-scratch` (vyloučení není tiché)")

# ── 7) ROZHODUJÍCÍ MĚŘENÍ: TÝŽ soubor v ŽIVÉM STROMĚ HRY
# Do P19 se tvrdilo, že „NA32 i H79 takový soubor hlásí jako vadu živého
# stromu". Fixtura v `*-scratch` to ZMĚŘIT NEMŮŽE — obě brány ji vylučují.
# Fixtura se proto na dobu měření položí do ŽIVÉHO stromu hry a hned se uklidí.
# (Není to „špinění repa": hra je v tom okamžiku čistá, soubor je netrackovaný
# a po měření se maže — a `git status` se měří PŘED i PO.)
HRA = WS.parent / "uo-shadows"
ZIVY = HRA / "scripts" / "_p20_bom_fixtura.py"
GIT = str(WS / "tools" / "git.cmd")

print("\n--- 7) ROZHODUJÍCÍ: tentýž soubor v ŽIVÉM stromě hry")
if not HRA.is_dir():
    zk(False, "živý strom hry existuje", str(HRA))
else:
    pred = subprocess.run([GIT, "-C", str(HRA), "status", "--porcelain"],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", shell=True, timeout=120).stdout
    ZIVY.write_bytes(b"\xef\xbb\xbf" + TELO.encode("utf-8"))
    zk(ZIVY.read_bytes()[:3] == b"\xef\xbb\xbf", "fixtura v živém stromě MÁ BOM")
    vystup = {}
    for nazev, skript in (("NA32", ANALYZA / "n32-kompilovatelnost.py"),
                          ("H79", ANALYZA / "h79-escape-sken.py")):
        rr = subprocess.run([sys.executable, "-B", str(skript)], capture_output=True,
                            text=True, encoding="utf-8", errors="replace",
                            cwd=str(WS), timeout=600)
        v = (rr.stdout or "") + (rr.stderr or "")
        vystup[nazev] = (rr.returncode, v)
        radky = [l for l in v.splitlines() if l.startswith("ZMĚŘENO")]
        print(f"    {nazev}: exit={rr.returncode}")
        print(f"      {radky[-1] if radky else '(souhrn nenalezen)'}")
        for l in v.splitlines():
            if "_p20_bom_fixtura" in l or "U+FEFF" in l:
                print(f"      nález: {l.strip()}")
    ZIVY.unlink(missing_ok=True)
    po = subprocess.run([GIT, "-C", str(HRA), "status", "--porcelain"],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", shell=True, timeout=120).stdout
    zk(not ZIVY.exists(), "fixtura z živého stromu SMAZÁNA")
    zk(pred == po, "`git status` hry je PŘED i PO stejný (strom vrácen)",
       f"pred={pred!r} po={po!r}")
    # ⚠ TOHLE je odpověď na otázku zadání: hlásí BOM OBĚ brány, nebo jen jedna?
    n32_bom = "U+FEFF" in vystup["NA32"][1]
    h79_bom = "U+FEFF" in vystup["H79"][1]
    print(f"\n    NA32 hlásí BOM: {n32_bom}   |   H79 hlásí BOM: {h79_bom}")
    zk(n32_bom, "NA32 soubor s BOM v živém stromě VYKÁŽE jako nekompilovatelný")
    zk(h79_bom,
       "H79 soubor s BOM v živém stromě VYKÁŽE (jinak se brány ROZCHÁZEJÍ — H99)",
       "když je `True`, H99 tvrdilo pravdu; když `False`, H99 bylo nepřesné")

# ── 8) UKLID
print("\n--- 8) úklid fixtury")
SOUBOR.unlink(missing_ok=True)
zk(not SOUBOR.exists(), "fixtura je smazaná (nezůstává ve stromě jako falešná vada)")
try:
    FIX.rmdir()
    (FIX.parent).rmdir()
except OSError:
    pass

chyb = sum(1 for ok, _, _ in kontroly if not ok)
print("\n" + "=" * 78)
print(f"VÝSLEDEK: {len(kontroly)} kontrol, {chyb} chyb")
for ok, popis, d in kontroly:
    if not ok:
        print(f"   CHYBA {popis}  [{d}]")
print("=" * 78)
sys.exit(1 if chyb else 0)
