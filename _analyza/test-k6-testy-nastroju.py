# -*- coding: utf-8 -*-
"""TEST brány K6 (`k6-over-testy-nastroju.py`) — umí vůbec spadnout?

PROČ: `AGENTS.md` — „Napsal jsi test? Vrať do kódu vadu a podívej se, že spadne."
Brána, která nikdy nic nenajde, není brána. Tahle brána má dvě strany, které se
musí prokázat OBĚ:

  1) KONTROLNÍ stav: nad zdravou falešnou hrou (test, který projde) → `exit 0`
     a čítač `1/1` — a hlavně SE ZAZNAMENALO, ŽE TEST OPRAVDU BĚŽEL (test při
     spuštění zapíše značku; bez ní by brána mohla jen tvrdit, že ho spustila).
  2) VADNÝ stav: nad falešnou hrou, jejíž test čte soubor, který v ní NENÍ
     (přesně vada naměřená 14. 10. 2026 v `coin-picker`) → `exit 1`, nález
     pojmenovaný souborem testu i chybějícím souborem.
  3) NEMĚŘENÝ stav: `--hry` na adresář bez testů → `exit 1` („nula není zelená").
  4) SMÍŠENÝ stav: zdravá + vadná hra v jednom běhu → `exit 1`, čítač `1/2`.
  5) TICHÉ PŘESKOČENÍ: test si chybějící vstup přeskočí, vypíše „0/0 kontrol"
     a skončí `exit 0` → `exit 1` s pojmenovaným důvodem (K7, 14. 10. 2026 —
     naměřeno na falešné hře, že to brána DŘÍV brala jako zelenou).
  6) VNOŘENÝ test (`.forge/node/sub/`) → `exit 1` a nález jmenuje ten soubor
     (dřív ho nerekurzivní `glob` vůbec neviděl).
  7) SOUHRN BEZ PROVEDENÉ KONTROLY S CHYBAMI: „VYSLEDEK: 0/5 kontrol, 5 chyb"
     a `exit 0` → `exit 1` (K8, 15. 10. 2026 — naměřeno vlastním A/B proti
     verzi brány z gitu, že to pravidlo K7 „aspoň jedno NENULOVÉ číslo" bralo
     jako zelenou: číslo selhání není důkaz provedené kontroly).
  8) SOUHRN S KLADNÝM POČTEM SELHÁNÍ: „VYSLEDEK: 5 kontrol, 2 selhání" a
     `exit 0` → `exit 1` (K8).
  9) PROTIZKOUŠKA: reálný formát souhrnu „Testů OK: 36, chyb: 0" (tak ho píše
     `vision.test.mjs` v obou hrách) musí zůstat ZELENÝ — jinak by zpevnění
     vyrobilo falešný nález o správném testu (K8).
 10) PROTIZKOUŠKA na TŘETÍ reálný formát: „14 kontrol, 0 selhání" (tak ho píše
     `provider-choice.test.mjs` v obou hrách) musí zůstat ZELENÝ. Tenhle formát
     v kalibraci K8 NEBYL — naměřil ho vlastním skenem až K9.
 11) NASTRAŽENÁ BRÁNA (H213, K9): zelený test se souhrnem
     „kontrol: 14, chybí: 2 volitelné fixtury" a `exit 0` musí zůstat ZELENÝ.
     Vzor K8 bral české sloveso „chybí" jako počet chyb → falešný nález
     o správném testu. Naměřeno vlastním A/B (K9): brána K7 zeleně, K8 červeně.
 12) OCHRANA PROTI PŘEOPRAVĚ: „14/14 kontrol, 2 chyby" a `exit 0` musí být
     ČERVENĚ — oprava vzoru nesmí oslepit pravidlo na skutečné chyby
     (podstatné jméno „chyby" se počítá dál). Bez tohohle případu by šlo
     „opravit" H213 tak, že by brána přestala vidět chyby vůbec.
 13) PROTIZKOUŠKA na obrácené pořadí: „0 chyb, 14/14 kontrol" → ZELENÁ.

Falešné hry se stavějí do `.tmp/` UVNITŘ repa (ne do systémového tempu) a po
testu se uklidí. Do žádné skutečné hry se nezasahuje.

Použití: python _analyza/test-k6-testy-nastroju.py
"""

import pathlib
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
BRANA = WS / "_analyza" / "k6-over-testy-nastroju.py"
KALIBR = WS / ".tmp" / "k6-kalibrace-testy-nastroju"
ZNACKA = KALIBR / "bezelo.txt"

TEST_OK = """// Falesna hra: test, ktery probehne a zapise, ze opravdu bezel.
import { writeFileSync } from 'node:fs';
writeFileSync(process.env.K6_ZNACKA || 'bezelo.txt', 'ano', 'utf8');
console.log('VYSLEDEK: 1/1 kontrol, 0 chyb');
"""

TEST_VADNY = """// Falesna hra: test existuje, ale jeho fixtura v hre NENI (vada coin-picker).
import { readFileSync } from 'node:fs';
readFileSync('.forge/roadmap.pilot.json', 'utf8');
console.log('VYSLEDEK: 1/1 kontrol, 0 chyb');
"""

# K7: test si chybejici vstup TISE preskoci a tvari se zeleny ("0/0 kontrol").
TEST_TICHE_PRESKOCENO = """// Falesna hra: test se chybejici fixture vyhne a skonci exit 0.
import { existsSync } from 'node:fs';
if (!existsSync('.forge/roadmap.pilot.json')) {
  console.log('PRESKOCENO: fixtura neni, 0/0 kontrol');
  process.exit(0);
}
console.log('VYSLEDEK: 5/5 kontrol, 0 chyb');
"""

# K8 (15. 10. 2026): zbývající díra v pravidle K7 — "aspoň jedno NENULOVÉ číslo"
# bere i ČÍSLO SELHÁNÍ. Naměřeno vlastním A/B K8: test, který vypíše
# "VYSLEDEK: 0/5 kontrol, 5 chyb" a skončí `exit 0`, hlasila brána jako zelený.
TEST_NULA_S_CHYBAMI = """// Falesna hra: nula provedenych kontrol, pet chyb, ale exit 0.
console.log('VYSLEDEK: 0/5 kontrol, 5 chyb');
process.exit(0);
"""

TEST_SELHANI_BEZ_SLASH = """// Falesna hra: pet kontrol, dve selhani, ale exit 0.
console.log('VYSLEDEK: 5 kontrol, 2 selhání');
process.exit(0);
"""

# PROTIZKOUŠKA: třetí reálný formát souhrnu nesmí nové pravidlo shodit.
# Naměřeno 15. 10. 2026 v `coin-picker`/`uo-shadows`: "Testů OK: 36, chyb: 0".
TEST_FORMAT3 = """// Falesna hra: format souhrnu, ktery pisou realne testy ve hrach.
console.log('Testů OK: 36, chyb: 0');
"""

# K9 (15. 10. 2026): TŘETÍ reálný formát — `provider-choice.test.mjs` v obou
# hrách píše `${checks} kontrol, 0 selhání`. V kalibraci K8 NEBYL.
TEST_FORMAT_R1 = """// Falesna hra: format souhrnu z provider-choice.test.mjs.
console.log('14 kontrol, 0 selhání');
"""

# K9 (H213): NASTRAŽENÁ BRÁNA. Zelený test, který u ZELENÉHO běhu hlásí, kolik
# VOLITELNÝCH věcí chybí. Vzor K8 (`chyb\w*`) v tom viděl počet chyb, protože
# `\w` zahrne i „í" — a brána vyrobila falešný nález o správném testu.
TEST_CHYBI_VOLITELNE = """// Falesna hra: zeleny test hlasi, kolik VOLITELNYCH fixtur chybi.
console.log('kontrol: 14, chybí: 2 volitelné fixtury');
process.exit(0);
"""

# K9: OCHRANA PROTI PŘEOPRAVĚ. Oprava H213 nesmí oslepit pravidlo na skutečné
# chyby — podstatné jméno „chyby" se musí počítat dál.
TEST_CHYBY_PODSTATNE = """// Falesna hra: dve skutecne chyby, ale exit 0.
console.log('14/14 kontrol, 2 chyby');
process.exit(0);
"""

# K9: PROTIZKOUŠKA na obrácené pořadí — nula chyb se nesmí splést s chybějícím.
TEST_OBRACENE_PORADI = """// Falesna hra: nula chyb, obracene poradi.
console.log('0 chyb, 14/14 kontrol');
"""

kontroly = []


def zk(ok: bool, popis: str, detail: str = "") -> None:
    kontroly.append((ok, popis, detail))
    print(f"  {'OK  ' if ok else 'CHYBA'} {popis}{f'  [{detail}]' if detail else ''}")


def postav_hru(jmeno: str, obsah_testu: str, soubor: str = "ukazka.test.mjs") -> pathlib.Path:
    hra = KALIBR / jmeno
    cesta = hra / ".forge" / "node" / soubor
    cesta.parent.mkdir(parents=True, exist_ok=True)
    cesta.write_text(obsah_testu, encoding="utf-8")
    return hra


def spust_branu(hry: list[pathlib.Path]):
    prikaz = [sys.executable, str(BRANA), "--hry", ";".join(str(h) for h in hry)]
    r = subprocess.run(prikaz, capture_output=True, cwd=str(WS), timeout=600,
                       env=None)
    return r.returncode, (r.stdout + r.stderr).decode("utf-8", "replace")


print("=" * 78)
print("TEST K6 — umí brána 'testy nástrojů ve hrách' spadnout?")
print("=" * 78)

try:
    if KALIBR.exists():
        shutil.rmtree(KALIBR)
    if ZNACKA.exists():
        ZNACKA.unlink()
    zdrava = postav_hru("zdrava", TEST_OK)
    vadna = postav_hru("vadna", TEST_VADNY)
    prazdna = KALIBR / "prazdna"
    prazdna.mkdir(parents=True, exist_ok=True)

    # ── 1) kontrolní stav ────────────────────────────────────────────────
    print("\n--- 1) zdravá falešná hra -------------------------------------------------")
    # Značku píše test do svého cwd (= kořen hry); nastavíme ji tam, kde ji čekáme.
    kod0, v0 = spust_branu([zdrava])
    zk(kod0 == 0, "zdravá hra → exit 0", f"exit={kod0}")
    zk("1/1 testů zelených" in v0, "čítač hlásí 1/1 testů zelených",
       [l for l in v0.splitlines() if "ZMĚŘENO" in l][:1])
    zk((zdrava / "bezelo.txt").exists(),
       "TEST OPRAVDU BĚŽEL (zapsal značku do kořene hry)",
       "bezelo.txt")

    # ── 2) vadný stav: test existuje, fixtura ne ─────────────────────────
    print("\n--- 2) vadná falešná hra (chybějící fixtura) -------------------------------")
    kod1, v1 = spust_branu([vadna])
    zk(kod1 == 1, "vadná hra → exit 1", f"exit={kod1}")
    zk("CHYBA" in v1, "výstup má pojmenovaný nález (CHYBA)")
    zk("ukazka.test.mjs" in v1, "nález jmenuje SOUBOR testu")
    zk("roadmap.pilot.json" in v1, "nález jmenuje CHYBĚJÍCÍ soubor")
    zk("0/1 testů zelených" in v1, "čítač hlásí 0/1 (ne tichou nulu)")

    # ── 3) neměřený stav ────────────────────────────────────────────────
    print("\n--- 3) adresář bez testů (nula není zelená) --------------------------------")
    kod2, v2 = spust_branu([prazdna])
    zk(kod2 == 1, "bez testů → exit 1", f"exit={kod2}")
    zk("neměřený stav" in v2, "výstup řekne, že se NEMĚŘILO")

    # ── 4) smíšený stav ─────────────────────────────────────────────────
    print("\n--- 4) zdravá + vadná hra v jednom běhu ------------------------------------")
    kod3, v3 = spust_branu([zdrava, vadna])
    zk(kod3 == 1, "smíšený běh → exit 1", f"exit={kod3}")
    zk("1/2 testů zelených" in v3, "čítač hlásí 1/2",
       [l for l in v3.splitlines() if "ZMĚŘENO" in l][:1])
    zk(len(re.findall(r"CHYBA", v3)) >= 2, "vadná hra je v souhrnu i u sebe")

    # ── 5) tiché přeskočení (K7) ────────────────────────────────────────
    print("\n--- 5) test si vstup TISE preskoci a hlasi 0/0 kontrol ---------------------")
    ticha = postav_hru("ticha-nula", TEST_TICHE_PRESKOCENO)
    kod4, v4 = spust_branu([ticha])
    zk(kod4 == 1, "0/0 kontrol → exit 1 (neměřeno není zelená)", f"exit={kod4}")
    zk("ANI JEDNU" in v4, "nález pojmenuje důvod (souhrn nehlásí ani jednu kontrolu)")
    zk("0/1 testů zelených" in v4, "čítač hlásí 0/1",
       [l for l in v4.splitlines() if "ZMĚŘENO" in l][:1])

    # ── 6) vnořený test (K7) ────────────────────────────────────────────
    print("\n--- 6) test ve VNORENE slozce .forge/node/sub/ -----------------------------")
    vnor = postav_hru("vnoreny", TEST_OK, soubor="sub/vnoreny.test.mjs")
    kod5, v5 = spust_branu([vnor])
    zk(kod5 == 1, "vnořený test → exit 1", f"exit={kod5}")
    zk("vnoreny.test.mjs" in v5, "nález jmenuje VNOŘENÝ soubor")
    zk("VNORENE" in v5, "nález řekne, že leží ve vnořené složce")

    # ── 7) souhrn hlásí NULU provedených kontrol a 5 chyb, ale exit 0 (K8) ─
    print("\n--- 7) souhrn '0/5 kontrol, 5 chyb' a přesto exit 0 ----------------------")
    nula = postav_hru("nula-provedenych", TEST_NULA_S_CHYBAMI)
    kod6, v6 = spust_branu([nula])
    zk(kod6 == 1, "0 provedených kontrol, 5 chyb → exit 1", f"exit={kod6}")
    zk("0/1 testů zelených" in v6, "čítač hlásí 0/1 (ne tichou zelenou)",
       [l for l in v6.splitlines() if "ZMĚŘENO" in l][:1])
    zk("ANI JEDNU" in v6, "nález pojmenuje důvod (souhrn nehlásí ani jednu kontrolu)")

    # ── 8) souhrn hlásí KLADNÝ počet selhání, ale exit 0 (K8) ───────────
    print("\n--- 8) souhrn '5 kontrol, 2 selhání' a přesto exit 0 --------------------")
    selh = postav_hru("selhani-bez-slash", TEST_SELHANI_BEZ_SLASH)
    kod7, v7 = spust_branu([selh])
    zk(kod7 == 1, "2 selhání → exit 1", f"exit={kod7}")
    zk("0/1 testů zelených" in v7, "čítač hlásí 0/1",
       [l for l in v7.splitlines() if "ZMĚŘENO" in l][:1])

    # ── 9) PROTIZKOUŠKA: reálný formát 3 musí zůstat zelený ─────────────
    # Bez tohohle případu by šlo "zpevnit" bránu tak, že vyrobí FALEŠNÝ nález
    # o správném testu (AGENTS.md: nastražená brána je horší než slepá).
    print("\n--- 9) protizkouška: reálný formát 'Testů OK: 36, chyb: 0' ----------------")
    f3 = postav_hru("format3", TEST_FORMAT3)
    kod8, v8 = spust_branu([f3])
    zk(kod8 == 0, "reálný formát souhrnu → exit 0 (žádný falešný nález)", f"exit={kod8}")
    zk("1/1 testů zelených" in v8, "čítač hlásí 1/1",
       [l for l in v8.splitlines() if "ZMĚŘENO" in l][:1])

    # ── 10) PROTIZKOUŠKA na TŘETÍ reálný formát (K9) ────────────────────
    print("\n--- 10) protizkouška: reálný formát '14 kontrol, 0 selhání' --------------")
    r1 = postav_hru("format-r1", TEST_FORMAT_R1)
    kod9, v9 = spust_branu([r1])
    zk(kod9 == 0, "formát z provider-choice.test.mjs → exit 0", f"exit={kod9}")
    zk("1/1 testů zelených" in v9, "čítač hlásí 1/1",
       [l for l in v9.splitlines() if "ZMĚŘENO" in l][:1])

    # ── 11) NASTRAŽENÁ BRÁNA: „chybí" není počet chyb (H213, K9) ────────
    print("\n--- 11) 'kontrol: 14, chybí: 2 volitelné fixtury' musí být ZELENÁ ------")
    chybi = postav_hru("chybi-volitelne", TEST_CHYBI_VOLITELNE)
    kod10, v10 = spust_branu([chybi])
    zk(kod10 == 0, "české 'chybí' (is missing) → exit 0, žádný falešný nález",
       f"exit={kod10}")
    zk("1/1 testů zelených" in v10, "čítač hlásí 1/1",
       [l for l in v10.splitlines() if "ZMĚŘENO" in l][:1])

    # ── 12) OCHRANA PROTI PŘEOPRAVĚ: skutečné chyby se počítají dál ─────
    print("\n--- 12) '14/14 kontrol, 2 chyby' musí být ČERVENÁ (proti přeopravě) ---")
    chyby = postav_hru("chyby-podstatne", TEST_CHYBY_PODSTATNE)
    kod11, v11 = spust_branu([chyby])
    zk(kod11 == 1, "2 skutečné chyby → exit 1", f"exit={kod11}")
    zk("0/1 testů zelených" in v11, "čítač hlásí 0/1",
       [l for l in v11.splitlines() if "ZMĚŘENO" in l][:1])

    # ── 13) PROTIZKOUŠKA: obrácené pořadí ──────────────────────────────
    print("\n--- 13) protizkouška: '0 chyb, 14/14 kontrol' → ZELENÁ ------------------")
    obr = postav_hru("obracene-poradi", TEST_OBRACENE_PORADI)
    kod12, v12 = spust_branu([obr])
    zk(kod12 == 0, "obrácené pořadí → exit 0", f"exit={kod12}")
    zk("1/1 testů zelených" in v12, "čítač hlásí 1/1",
       [l for l in v12.splitlines() if "ZMĚŘENO" in l][:1])
finally:
    if KALIBR.exists():
        shutil.rmtree(KALIBR, ignore_errors=True)

chyb = sum(1 for ok, _, _ in kontroly if not ok)
print("\n" + "=" * 78)
print(f"VÝSLEDEK: {len(kontroly)} kontrol, {chyb} chyb")
for ok, popis, d in kontroly:
    if not ok:
        print(f"   CHYBA {popis}  [{d}]")
print("=" * 78)
sys.exit(1 if chyb else 0)
