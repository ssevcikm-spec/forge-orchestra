# -*- coding: utf-8 -*-
"""P16/E — jsou ZÁZNAMY opravdu jen PŘIDANÉ? (měřeno proti COMMITU, ne proti stromu)

⚠ ZADÁNÍ TVRDÍ: „Historie se od P15 posunula, takže `git diff HEAD` je dnes
PRÁZDNÝ.“ **Naměřeno není** — pracovní strom orchestry má **3 změněné soubory**
(`HANDOFF.md`, `KRONIKA-PROJEKTU.md`, `NEXT-SESSION-INSTRUKCE.md`). Proto se měří
proti **commitu `ce49234`**, ne proti pracovnímu stromu — a stav stromu se
zapisuje jako nález, ne jako předpoklad.

Co se měří:
  1. `git show ce49234 -- KRONIKA-PROJEKTU.md` → jediná smazaná řádka musí být
     souhrn `| **celkem** |` (to je STAV, ne záznam); zbytek = přidání,
  2. `git show ce49234 -- HANDOFF.md` → 0 smazaných řádků,
  3. řádky §31.7, §31.9 a řádku 27 kroniky z blobu PŘED → musí být pořád na místě
     (H75/H76/H77 se měly DOPLNIT, ne přepsat),
  4. tři brány záznamů spuštěné zvlášť,
  5. stav pracovního stromu (a co v něm je necommitnuté).
"""

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
GIT = str(WS / "tools" / "git.cmd")
PRE = "ce49234~1"

kontrol = 0
chyb = 0


def zk(ok, popis, detail=""):
    global kontrol, chyb
    kontrol += 1
    if ok:
        print(f"  OK   {popis}" + (f"  [{detail}]" if detail else ""))
    else:
        chyb += 1
        print(f"  CHYBA {popis}" + (f"  [{detail}]" if detail else ""))


def git(*args):
    r = subprocess.run([GIT, "-C", str(WS), *args], capture_output=True, shell=True)
    return (r.returncode, (r.stdout or b"").decode("utf-8", "replace"))


def diff_pocty(rel):
    _, d = git("show", "--unified=0", "--format=", "ce49234", "--", rel)
    pridane = [l for l in d.splitlines() if l.startswith("+") and not l.startswith("+++")]
    smazane = [l for l in d.splitlines() if l.startswith("-") and not l.startswith("---")]
    return pridane, smazane


print("=" * 78)
print("P16/E — záznamy: jen PŘIDANÉ? (proti commitu ce49234)")
print("=" * 78)

# ── 1) KRONIKA ─────────────────────────────────────────────────────────────
print("\n--- 1) `git show ce49234 -- KRONIKA-PROJEKTU.md` ----------------------")
prid, smaz = diff_pocty("KRONIKA-PROJEKTU.md")
print(f"  přidaných řádků: {len(prid)}, smazaných: {len(smaz)}")
for l in smaz:
    print(f"      SMAZÁNO: {l[:100]}")
zk(len(smaz) == 1, "v kronize je smazaná PRÁVĚ JEDNA řádka", f"{len(smaz)}")
zk(bool(smaz) and "celkem" in smaz[0],
   "a je to souhrnný řádek `celkem` — tedy STAV, ne záznam", smaz[0][:70] if smaz else "—")
zk(len(prid) >= 20, "zbytek je PŘIDÁNÍ (ne přepis)", f"{len(prid)} řádků")

# ── 2) HANDOFF ─────────────────────────────────────────────────────────────
print("\n--- 2) `git show ce49234 -- HANDOFF.md` ------------------------------")
prid_h, smaz_h = diff_pocty("HANDOFF.md")
print(f"  přidaných řádků: {len(prid_h)}, smazaných: {len(smaz_h)}")
zk(len(smaz_h) == 0, "v `HANDOFF.md` není ANI JEDNA smazaná řádka", f"{len(smaz_h)}")

# ── 3) původní věty na místě (H75/H76/H77) ────────────────────────────────
print("\n--- 3) původní věty §31.7 / §31.9 / řádku 27 pořád na místě ----------")
_, pre_handoff = git("show", f"{PRE}:HANDOFF.md")
_, pre_kronika = git("show", f"{PRE}:KRONIKA-PROJEKTU.md")
dnes_handoff = (WS / "HANDOFF.md").read_text(encoding="utf-8")
dnes_kronika = (WS / "KRONIKA-PROJEKTU.md").read_text(encoding="utf-8")


def usek(text, nadpis):
    radky = text.splitlines()
    i = next((k for k, l in enumerate(radky) if l.startswith(nadpis)), None)
    if i is None:
        return None
    j = next((k for k in range(i + 1, len(radky)) if radky[k].startswith("### ")), len(radky))
    return radky[i:j]


for nadpis in ("### 31.7", "### 31.9"):
    u = usek(dnes_handoff, nadpis)
    if u is None:
        zk(False, f"{nadpis} v `HANDOFF.md` NENÍ")
        continue
    text = "\n".join(u)
    print(f"  {nadpis}: {len(u)} řádků dnes")
    zk("⚠ OPRAVA 5. 10. 2026" in text or "OPRAVA 5. 10. 2026" in text,
       f"{nadpis}: obsahuje DODATEČNÝ odstavec s datem opravy (doplnění, ne přepis)")
    zk(len(u) > 20, f"{nadpis}: původní text je pořád na místě (řádků {len(u)})")
    for klic in ("V tabulce §31.7 vs. uložený běh", "8 nenulových exitů",
                 "dnes **0**", "uložený běh"):
        if klic in text:
            print(f"      obsahuje: {klic!r}")

# ⚠ MEZ MĚŘENÍ, která se musí přiznat: `### 31.7` ani `### 31.9` v `ce49234~1`
# NEJSOU — §31 vznikl v P13c, a ta se commitla SPOLU s P14 a P15 v `ce49234`.
# „Stav před P15" tedy v gitu neexistuje ani pro ně (táž mez jako u H80).
zk("### 31.7" not in pre_handoff and "### 31.9" not in pre_handoff,
   "PŘIZNANÁ MEZ: §31 v `ce49234~1` není → H75/H76 se z gitu OVĚŘIT NEDÁ, "
   "jen že `ce49234` v HANDOFFu nesmazal ani řádek")

# řádek 27 kroniky — měřeno na DNEŠNÍM stavu (v `ce49234~1` taky není: je z P13c)
r27_dnes = [l for l in dnes_kronika.splitlines() if re.match(r"^\|\s*\*{0,2}27\*{0,2}\s*\|", l)]
print(f"  řádek 27 kroniky dnes: {len(r27_dnes)}×")
for l in r27_dnes:
    print(f"      {l[:100]}")
zk(bool(r27_dnes), "řádek 27 v kronize existuje")
# H77: přidán odstavec s odkazem na H68/H69 — najdi ho v okolí řádku 27
obsah = dnes_kronika
idx = obsah.find(r27_dnes[0]) if r27_dnes else -1
text_kolem = obsah[idx:idx + 2500] if idx >= 0 else ""
zk("H68" in text_kolem or "H69" in text_kolem,
   "H77: v okolí řádku 27 je DOPLNĚNÝ odkaz na H68/H69 (původní text zůstal)",
   "nalezeno" if ("H68" in text_kolem or "H69" in text_kolem) else "NENALEZENO")

# ── 4) brány záznamů ──────────────────────────────────────────────────────
print("\n--- 4) brány záznamů (spuštěné zvlášť) ------------------------------")
for popis, skript, vzor in (
        ("handoff úplnost", ANALYZA / "handoff-kontrola-uplnost.py", r"kontrolovaných klíčů:\s+(\d+)"),
        ("kronika úplnost", ANALYZA / "kronika-kontrola.py", r"omylů celkem \(skutečnost\):\s+(\d+)"),
        ("zadání kontrola", ANALYZA / "zadani-kontrola.py", r"(\d+) řádků")):
    r = subprocess.run([sys.executable, str(skript)], capture_output=True, cwd=str(WS))
    v = (r.stdout or b"").decode("utf-8", "replace") \
        + (r.stderr or b"").decode("utf-8", "replace")
    m = None
    for m in re.finditer(vzor, v):
        pass
    print(f"  {popis:<18} exit={r.returncode}   čítač={m.group(1) if m else '—'}")
    zk(r.returncode == 0, f"{popis}: `exit 0`", f"exit={r.returncode}")
    if popis == "handoff úplnost":
        zk(m is not None and m.group(1) == "83", "handoff úplnost hlásí 83/83",
           m.group(1) if m else "—")

# ── 5) stav pracovního stromu (nález, ne předpoklad) ─────────────────────
print("\n--- 5) pracovní strom orchestry: NENÍ čistý --------------------------")
_, stav = git("status", "--porcelain")
radky = [l for l in stav.splitlines() if l.strip()]
for l in radky[:12]:
    print(f"      {l}")
print(f"  změněných/untracked řádků: {len(radky)}")
_, stat = git("diff", "--stat", "HEAD")
for l in stat.splitlines()[-4:]:
    print(f"      {l.strip()}")
zk(len(radky) > 0,
   "NAMĚŘENO: strom orchestra NENÍ čistý (tvrzení v hlavičce zadání je "
   "v rozporu s měřením)")
print("  ⚠ Co z toho plyne: záznamy, které P15 zapsala PO commitu (blok "
      "„PUSH PROVEDEN“, §33.9c/§33.9d a přepsané zadání), v gitu NEJSOU.")
print("     `HANDOFF.md` i `KRONIKA-PROJEKTU.md` jsou přitom APPEND-ONLY "
      "záznamy — visí jen ve stromě.")

print("\n" + "=" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
print("=" * 78)
sys.exit(1 if chyb else 0)
