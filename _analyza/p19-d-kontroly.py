# -*- coding: utf-8 -*-
r"""P19 — Úkol D: DŮKAZ, ŽE `g3` UMÍ SPADNOUT (jinak je to brána bez chyby).

ZADÁNÍ: „Když zavedeš `sys.exit`, MUSÍŠ doložit, že umí spadnout — jinak je to
‚brána, která nemá jak selhat‘.“

CO SE ZAVEDLO (rozhodnutí P19): `g3` spadne jen za to, co **sám tvrdí**:
  * některá brána VŮBEC NEZAČALA,
  * některá brána BĚŽELA bez čítače a není v deklarovaném `OCEKAVANE_BEZ_CITACE`,
  * neproběhla ANI JEDNA brána (`exit 2`).
O červených branách NEROZHODUJE (to by potřebovalo seznam očekávaně nenulových
exitů — nález NA23b) a tenhle test to ověřuje taky.

JAK: ze ŽIVÉHO `g3-brany.py` se staví kopie s VLASTNÍMI fixturami (do kopie se
vkládá absolutní root — jinak by se cesty odvodily z umístění kopie, což je
past, na kterou P19 dvakrát narazila). Živý soubor se NEMUTUJE.
Použití: python _analyza/p19-d-kontroly.py
"""

import ast
import hashlib
import os
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
G3 = ANALYZA / "g3-brany.py"
SCRATCH = ANALYZA / "p19-scratch"
FIX = SCRATCH / "d-fixtury"
HARNESS = SCRATCH / "p19-d-harness.py"

kontroly = []


def zk(ok: bool, popis: str, detail: str = "") -> None:
    kontroly.append((ok, popis, detail))
    print(f"  {'OK  ' if ok else 'CHYBA'} {popis}" + (f"\n      {detail}" if detail else ""))


print("=" * 78)
print("P19/D — umí `g3` spadnout? (a nezačne padat za cizí červenou?)")
print("=" * 78)

zdroj = G3.read_text(encoding="utf-8")
hash_pred = hashlib.sha256(G3.read_bytes()).hexdigest()
FIX.mkdir(parents=True, exist_ok=True)

# Fixtury (skutečné skripty — exit se NEPÍŠE natvrdo do seznamu bran).
(FIX / "d-zdrava.py").write_text(
    'print("VYSLEDEK: 3 kontrol, 0 chyb")\n', encoding="utf-8", newline="\n")
(FIX / "d-bez-citace.py").write_text(
    'print("D: hotovo, vse na svem miste")\nraise SystemExit(2)\n',
    encoding="utf-8", newline="\n")
(FIX / "d-cervena.py").write_text(
    'print("VYSLEDEK: 3 kontrol, 1 chyb")\nraise SystemExit(1)\n',
    encoding="utf-8", newline="\n")

m = re.search(r"^BRANY = \[.*?^\]\n", zdroj, re.M | re.S)
zk(m is not None, "v živém g3 se našel blok `BRANY`")


def postav(fixtury: str, deklarace: str = "OCEKAVANE_NENULOVE = {}") -> str:
    h = zdroj[:m.start()] + fixtury + zdroj[m.end():]
    h = h.replace('VYSTUP = ANALYZA / "g3-brany-vystup.txt"',
                  'VYSTUP = ANALYZA / "p19-scratch" / "p19-d-harness-vystup.txt"')
    h = h.replace("WS = pathlib.Path(__file__).resolve().parent.parent",
                  f'WS = pathlib.Path(r"{WS}")')
    # ⚠ DOPLNĚNO V P20 (6. 10. 2026) — a je to PŘÍMÝ DŮSLEDEK rozhodnutí
    # Úkolu A: `g3` od P20 soudí i červené, takže deklarace `OCEKAVANE_NENULOVE`
    # (`{"zadání kontrola": 1}`) by v kopii byla **VISUTÁ** — fixtury nahrazují
    # celý blok `BRANY`, takže v kopii žádná `zadání kontrola` není. `g3` by
    # správně skončil `exit 1`, ale **z jiného důvodu, než tenhle test měří**
    # (`overovani` §10.1). Deklarace se proto v kopii vyprazdňuje — test tím
    # měří přesně to, co tvrdí. Explicitní hodnotu dostávají jen ty případy,
    # které deklaraci ZÁMĚRNĚ zkoumají.
    h = h.replace('OCEKAVANE_NENULOVE = {"zadání kontrola": 1}', deklarace)
    ast.parse(h)
    return h


def brana(popis: str, soubor: str) -> str:
    """Záznam brány pro KOPII `g3`.

    ⚠ OMyl 193 (naměřeno tady): `r"(\\\\\\\\d+) kontrol"` v NORMALNÍM řetězci
    generátoru vyrobí v kopii `r"(\\\\d+) kontrol"`, což je regex na LITERÁLNÍ
    zpětné lomítko — čítač se pak „nenajde" a zdravá brána vypadá jako brána
    bez čítače (a `g3` kvůli tomu správně spadne). Proto se vzor skládá
    z RAW řetězce, kde je vidět, kolik lomítek opravdu vznikne.
    """
    vzor = r'r"(\d+) kontrol"'
    return (f'    ("{popis}", ["python", "<ANALYZA>/p19-scratch/d-fixtury/{soubor}"],\n'
            f'     {vzor}),\n')


def spust(text: str) -> dict:
    HARNESS.write_text(text, encoding="utf-8", newline="\n")
    # ⚠ POJISTKA PROTI PŘEPSÁNÍ ŽIVÉHO REGISTRU (nález P24, 7. 10. 2026):
    # tenhle harness je KOPIE `g3` s VLASTNÍMI fixturami a běží **bez
    # `--soubor`** — takže si `g3` na konci **zapsal registr živých bran**.
    # Naměřeno: po dávce `p20-d-doklady.py` měl `_analyza/_registr-bran.json`
    # **`bran_celkem: 1`** a jedinou bránu **`A1: zdravá`** (fixtura), přitom
    # živých bran je **48** — a `validate-all` kvůli tomu čte lež
    # („bran v registru = 48“). Je to přesně vada z `AGENTS.md`/§6.14
    # („kdo si staví harness z `g3`, musí dát `FORGE_REGISTR` / `FORGE_BEZ_REGISTRU`“),
    # kterou `p20-d-doklady.py` sice OHLÁSÍ, ale neopraví.
    env = dict(os.environ)
    env["FORGE_BEZ_REGISTRU"] = "1"
    r = subprocess.run([sys.executable, "-B", str(HARNESS)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       cwd=str(WS), timeout=900, env=env)
    out = (r.stdout or "") + (r.stderr or "")
    # ⚠ DOPLNĚNO V P20: `exit` SÁM NEŘEKNE, KTERÝ ze stavů nastal — a přesně
    # na tomhle spadl tenhle doklad po rozhodnutí Úkolu A (`exit 1` ze čtyř
    # různých důvodů; `overovani` §10.1). Každý neúspěch se proto dá dohledat
    # podle výpisu harnessu, ne hádáním.
    if r.returncode != 0:
        print("      --- výpis harnessu (exit=%d) ---" % r.returncode)
        for l in out.splitlines()[-18:]:
            print("      " + l)
    return {"exit": r.returncode, "vystup": out}


print("\n--- 1) ZDRAVÝ stav: jedna brána s čítačem → exit 0 -----------------")
h_zdravy = postav("BRANY = [\n" + brana("D1: zdravá brána", "d-zdrava.py") + "]\n")
r = spust(h_zdravy)
zk(r["exit"] == 0, "g3 s jednou zdravou bránou → exit 0", f"exit={r['exit']}")
zk("PŘEHLED JE ÚPLNÝ" in r["vystup"], "výslovně to řekne",
   "hledám 'PŘEHLED JE ÚPLNÝ'")

print("\n--- 2) BRÁNA, KTERÁ VŮBEC NEZAČALA → MUSÍ SPADNOUT ------------------")
h_mrtva = postav("BRANY = [\n" + brana("D2: neexistující soubor", "d-neexistuje.py") + "]\n")
r = spust(h_mrtva)
zk(r["exit"] == 1, "g3 → exit 1 (vada MĚŘENÍ, ne výsledek brány)", f"exit={r['exit']}")
zk("BRÁNY, KTERÉ VŮBEC NEZAČALY" in r["vystup"], "důvod je pojmenovaný",
   "hledám sekci 'BRÁNY, KTERÉ VŮBEC NEZAČALY'")

print("\n--- 3) BRÁNA BEZ ČÍTAČE (a není deklarovaná) → MUSÍ SPADNOUT ---------")
h_bez = postav("BRANY = [\n" + brana("D3: běžela bez čítače", "d-bez-citace.py") + "]\n")
r = spust(h_bez)
zk(r["exit"] == 1, "g3 → exit 1", f"exit={r['exit']}")
zk("mimo deklarovaný stav: 1" in r["vystup"], "počet bran bez čítače je vykázaný",
   "hledám 'mimo deklarovaný stav: 1'")

print("\n--- 4) TÁŽ BRÁNA, ALE DEKLAROVANÁ v baseline → exit 0 ---------------")
h_dek = postav("BRANY = [\n" + brana("D3: běžela bez čítače", "d-bez-citace.py") + "]\n")
h_dek = h_dek.replace('OCEKAVANE_BEZ_CITACE = {"C2: mutace N1 (5 běhů)"}',
                      'OCEKAVANE_BEZ_CITACE = {"D3: běžela bez čítače"}')
zk('OCEKAVANE_BEZ_CITACE = {"D3' in h_dek, "baseline se v kopii SKUTEČNĚ změnil")
r = spust(h_dek)
zk(r["exit"] == 0, "deklarovaný stav → exit 0 (baseline funguje)", f"exit={r['exit']}")
zk("mimo deklarovaný stav: 0" in r["vystup"], "vykáže, že mimo baseline nic není")

print("\n--- 5) ČERVENÁ brána S ČÍTAČEM → P20: MUSÍ SPADNOUT (NA23b vyřešen) ---")
# ⚠ PŘEPSÁNO V P20 (6. 10. 2026) — a JE TO ZÁMĚR, ne oprava omylu.
# Tenhle případ tvrdil P19's rozhodnutí: „červenou NEposuzuje (exit 0), jen ji
# pojmenuje jako k rozhodnutí“ (nález NA23b zůstal otevřený, protože neexistoval
# seznam očekávaně nenulových exitů). **P20 ten seznam zavedla**
# (`OCEKAVANE_NENULOVE`), takže NEDEKLAROVANÁ červená brána už `g3` SHODÍ —
# a to je přesně ta polovina, která do P20 chyběla: `exit 0` vypadal stejně pro
# „vše v pořádku“ i pro „brána tiše odešla“.
# Doklad se NEMAŽE: mění se jen to, co má měřit, protože se změnila smlouva.
h_cerv = postav("BRANY = [\n" + brana("D4: červená, ale s čítačem", "d-cervena.py") + "]\n")
r = spust(h_cerv)
zk(r["exit"] == 1, "g3 → exit 1: NEDEKLAROVANOU červenou od P20 posuzuje",
   f"exit={r['exit']}")
zk("NENULOVÉ EXITY: 1" in r["vystup"] and "NEOČEKÁVANÝ: D4" in r["vystup"],
   "a pojmenuje ji jako NEOČEKÁVANOU (ne už jako „k rozhodnutí“)",
   "hledám 'NENULOVÉ EXITY: 1' a 'NEOČEKÁVANÝ: D4'")
zk("NENULOVÉ EXITY: 1" in r["vystup"] and "D4" in r["vystup"],
   "je vidět KTERÁ brána to je", "hledám jméno brány ve výpisu")
# A DRUHÁ POLOVINA TÉHOŽ (to je jádro Úkolu A): TÁŽ červená, ale DEKLAROVANÁ,
# `g3` shodit NESMÍ — jinak by padal po každém commitu.
h_cerv_dek = postav("BRANY = [\n" + brana("D4: červená, ale s čítačem", "d-cervena.py") + "]\n",
                    'OCEKAVANE_NENULOVE = {"D4: červená, ale s čítačem": 1}')
r = spust(h_cerv_dek)
zk(r["exit"] == 0, "TÁŽ červená DEKLAROVANÁ → exit 0 (g3 nepadá po commitu)",
   f"exit={r['exit']}")
zk("očekávaný:   D4" in r["vystup"], "a je vidět, že je očekávaná",
   "hledám 'očekávaný:   D4'")

print("\n--- 6) PRÁZDNÉ BRANY → exit 2 (neměřilo se) ------------------------")
h_prazdne = postav("BRANY = []\n")
r = spust(h_prazdne)
zk(r["exit"] == 2, "g3 bez bran → exit 2 (ne 0!)", f"exit={r['exit']}")
zk("NEMĚŘILO SE VŮBEC" in r["vystup"], "řekne to slovy",
   "hledám 'NEMĚŘILO SE VŮBEC'")

print("\n--- 7) ŽIVÝ g3 SE NESMÍ ZMĚNIT -------------------------------------")
hash_po = hashlib.sha256(G3.read_bytes()).hexdigest()
zk(hash_po == hash_pred, "živý `g3-brany.py` je bajt na bajt nezměněný", hash_po[:16])
HARNESS.unlink(missing_ok=True)

chyb = sum(1 for ok, _, _ in kontroly if not ok)
print("\n" + "=" * 78)
print(f"VÝSLEDEK: {len(kontroly)} kontrol, {chyb} chyb")
for ok, popis, d in kontroly:
    if not ok:
        print(f"   CHYBA {popis}  [{d}]")
print("=" * 78)
sys.exit(1 if chyb else 0)
