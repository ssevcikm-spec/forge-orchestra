# -*- coding: utf-8 -*-
r"""P20 — OPRAVA KRONIKY: vrátí řádek 33 (P19) BAJT NA BAJT a přidá řádek 34 (P20).

CO SE STALO (omyl 206, naměřeno): do kroniky jsem vkládal nový řádek session
a jako kotvu použil **řádek 33** — jenže ten se mi do kontextu načetl
**ZKRÁCENÝ** (2000 znaků). Nahradil jsem tedy **celý** řádek zkráceným textem
a pak ho „vrátil“, čímž do NĚJ vznikl **druhý výskyt téhož textu** (řádek
narostl z 4286 na 6149 znaků). Je to **tatáž třída jako omyl P19 194**
(editace kroniky nahradila řádek místo vložení) — a proto se to opravuje
**programově**, ne dalším ručním zápisem.

POSTUP: zdrojem pravdy je **blob v `HEAD`** (P19 je commitnutá a pushnutá).
Řádek 33 se z něj vezme DOSLOVA; nový řádek 34 se přidá ZA něj. Tím nemůže
vzniknout duplikát ani ztráta textu — a obojí se vzápětí KONTROLUJE.

Použití: python _analyza/p20-oprav-kroniku.py
"""

import hashlib
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
KR = WS / "KRONIKA-PROJEKTU.md"
GIT = str(WS / "tools" / "git.cmd")

RADEK_33 = 33          # 1-based index řádku P19 v tabulce sessions
NOVY = (
    "| **34** | **6. 10. 2026** (10:2x–13:2x UTC = 12:2x–15:2x +02:00) | "
    "**rozhodovací** | **P20: `g3` SOUDÍ ČERVENÉ, BOM V `.py` ZAKÁZÁN, TICHÁ "
    "DÍRA V H79** (`NEXT-SESSION-INSTRUKCE.md` z 6. 10., Úkoly **A–E**): "
    "**A** verdikt `g3` nad červenými (NA23b) — `OCEKAVANE_NENULOVE`, "
    "**B** BOM v `.py`: vada, nebo ne? (H99), **C** mají opakovatelné ověřovací "
    "skripty vstoupit do `g3`?, **D** záznamy a ověření stavu, **E** návrat "
    "k věcné práci | **A — NA23b VYŘEŠEN: `g3` JE NYNÍ ÚPLNÁ BRÁNA.** Do P20 "
    "soudil jen sebe a červené pouze vypsal. Nově je deklarace "
    "**`OCEKAVANE_NENULOVE = {\"zadání kontrola\": 1}`** — a **KÓD v ní je "
    "proto, že se to naměřilo** (`p20-a-kody-bran.py` **7/0**): brána `zadání "
    "kontrola` umí **`0` i `1`** (0 = kotva na živý `HEAD`, 1 = zastaralé "
    "zadání, což je její SPRÁVNÁ práce), takže deklarace nesoucí jen JMÉNO by "
    "nerozlišila „tatáž brána, jiný důvod“. Doklad **`p20-a-kontroly.py` 18/0**: "
    "nedeklarovaná červená → **`exit 1`**, táž deklarovaná → **`exit 0`**, "
    "stejné jméno s jiným kódem → **`exit 1`**, deklarace bez brány (visutá) → "
    "**`exit 1`**, deklarovaná a dnes zelená → **poznámka, ne pád** (zadání se "
    "na dnešek neopravuje, §37.5). **B — BOM V `.py` JE ZAKÁZÁN** (pravidlo "
    "v `AGENTS.md`): naměřeno **9/0**, že `python soubor.py` s BOM **funguje** "
    "(`exit 0`), ale `compile()` ho **odmítne** — „jde spustit?“ a „jde "
    "zkompilovat?“ jsou DVĚ otázky (H99). **A P19 měla v POPISU nepřesnost, ne "
    "ve výsledku:** `ast.parse()` BOM **taky odmítne** (týž tokenizér), takže "
    "rozdíl mezi NA32 a H79 nevzniká tam; vznikl by v **`utf-8-sig` fallbacku** "
    "H79, který je ale **mrtvá větev** (BOM se v `utf-8` dekóduje na U+FEFF, "
    "nepadá). Fixtura s BOM vložená do ŽIVÉHO stromu hry: **NA32 i H79 ji "
    "vykázaly** (`exit 1`) — obě brány se tedy **nerozcházejí**, ověřeno, ne "
    "odvozeno. **Navíc H101 (NOVÝ NÁLEZ): H79 měla TICHOU DÍRU** — nečitelný "
    "`.py` **tiše vynechala** (`continue`) a skončila `exit 0`, kdežto NA32 "
    "tentýž soubor vykázal (`1 nepřečteno`) a skončil `exit 1`. Dvě brány, dva "
    "verdikty o témž stromě. Opraveno: nečitelné se **počítají i pojmenovávají** "
    "(pole `nečitelných` na KONCI souhrnu, takže starší doklady P19 na týž "
    "řádek pořád sedí — ověřeno jejich vlastním vzorem), `exit` se nemění "
    "a mrtvý fallback je pryč. Doklady **`p20-b2-kontroly.py` 12/0** "
    "a **`p20-b2-necitelne.py` 12/0**. **C — 8 KANDIDÁTŮ ROZHODNUTO** "
    "(`p20-c-kandidati.py`, měřeno: exit, doba, čítač, zápis). Do `g3` se "
    "**NEPŘIDAL ANI JEDEN** a je to podložené: dva (`ov-b1` 1,1 s, "
    "`ov-g-neovereno` 1,2 s) **nevykazují čítač** → `g3` by na nich podle "
    "vlastního pravidla spadl; tři (`ov-e` 9,7 s, `p19-c` 14,0 s, `p19-d` "
    "8,6 s) **zapisují do stromu** (mutují) — nejsou to měřidla STAVU, ale "
    "doklady; `ov-g-h92-sken` (0,8 s) je **diagnostický sken**; `p19-b` "
    "a `p19-b2` (10,8 s / 10,4 s) jsou **doklady k jednorázovým opravám** "
    "H93/H98. **`g3` zůstává na 37 branách.** Součástí rozhodnutí ale je, že "
    "**každý z 8 kandidátů musí být opakovatelný a zelený** — a to se měřilo: "
    "**19 dokladů, 17 zelených, 4 opravené, 1 doložený falešný poplach** "
    "(`p20-d-doklady.py`). **D — ZÁZNAMY SEDÍ:** `g3` **37 bran, 1 nenulový "
    "(deklarovaný: `zadání kontrola`), 0 nezačatých, 0 bez čítače mimo "
    "deklaraci, exit 0**; `validate-all` **✓ VŠE V POŘÁDKU**; `KRONIKA SEDÍ`; "
    "handoff **83/83**; **`NEOVĚŘENO` = 0** vlastním skriptem; inventář "
    "přegenerován **jako POSLEDNÍ krok** | 195–206 |"
)

print("=" * 78)
print("P20 — oprava kroniky: řádek 33 z HEAD (bajt na bajt) + nový řádek 34")
print("=" * 78)

blob = subprocess.run([GIT, "-C", str(WS), "show", "HEAD:KRONIKA-PROJEKTU.md"],
                      capture_output=True, shell=True).stdout
head_lines = blob.decode("utf-8").splitlines()
# ⚠ OMyl 207 (naměřeno tady): ČÍSLO SESSION NENÍ ČÍSLO ŘÁDKU. První verze
# tohohle skriptu sahala na `head_lines[32]` podle „řádek 33 = session 33“ —
# a trefila session **2**. Je to táž třída jako „různé čítače nesou stejné
# jméno“ (`dsh-prostredi` §5): hledá se proto **podle OBSAHU**, ne podle pozice.
_idx = [i for i, l in enumerate(head_lines) if l.startswith("| **33** |")]
assert len(_idx) == 1, f"řádek session 33 v HEAD není právě jednou: {_idx}"
RADEK_33 = _idx[0] + 1
radek_head = head_lines[RADEK_33 - 1]
print(f"\n  řádek session 33 je v HEAD na pozici {RADEK_33}: "
      f"{len(radek_head)} znaků")
print(f"  začíná: {radek_head[:90]}…")
assert radek_head.startswith("| **33**"), "řádek 33 v HEAD není řádek P19!"
assert "P19" in radek_head, "řádek 33 v HEAD není session P19!"

soucasne = KR.read_text(encoding="utf-8").splitlines()
radek_ted = soucasne[RADEK_33 - 1]
print(f"  řádek 33 teď:    {len(radek_ted)} znaků")
print(f"  je poškozený:    {radek_ted != radek_head}")

# ⚠ IDEMPOTENCE: skript se nesmí dát spustit dvakrát a vložit řádek 34 dvakrát
# (to je táž třída jako omyl 194/206 — „editace přidala, co už tam bylo“).
# Když je řádek 34 na místě a 33 je zdravý, není co dělat.
if radek_ted == radek_head and soucasne[RADEK_33].startswith("| **34**"):
    print("\n  STAV JE JIŽ OPRAVENÝ (33 shodný s HEAD, 34 na místě) — končím "
          "bez zápisu.")
    sys.exit(0)

nove = list(soucasne)
nove[RADEK_33 - 1] = radek_head          # obnov P19 DOSLOVA z HEAD
nove.insert(RADEK_33, NOVY)              # a vlož nový řádek ZA něj
KR.write_text("\n".join(nove) + "\n", encoding="utf-8", newline="\n")

# ── KONTROLY: obojí se ověřuje, ne předpokládá ────────────────────────────
po = KR.read_text(encoding="utf-8").splitlines()
chyb = 0


def kont(ok, popis, detail=""):
    global chyb
    if not ok:
        chyb += 1
    print(f"  {'OK  ' if ok else 'CHYBA'} {popis}" + (f"\n      {detail}" if detail else ""))


print()
kont(len(po) == len(soucasne) + 1, "přibyl PRÁVĚ JEDEN řádek",
     f"{len(soucasne)} → {len(po)}")
kont(po[RADEK_33 - 1] == radek_head, "řádek 33 (P19) je SHODNÝ s blobem v HEAD",
     f"{len(po[RADEK_33 - 1])} znaků")
kont(po[RADEK_33].startswith("| **34**"), "řádek 34 je nový řádek P20")
# Duplikát, který vznikl omylem 206, se nesmí vrátit:
kont(po[RADEK_33 - 1].count("H93 PŘEMĚŘENO SOUBOR PO SOUBORU") == 1,
     "v řádku 33 není DRUHÝ výskyt téhož textu (omyl 206)",
     f"výskytů: {po[RADEK_33 - 1].count('H93 PŘEMĚŘENO SOUBOR PO SOUBORU')}")
kont(sum(1 for l in po if l.startswith("| **33**")) == 1
     and sum(1 for l in po if l.startswith("| **34**")) == 1,
     "řádek 33 i 34 je v tabulce právě JEDNOU")
# Ostatní řádky se nesmí změnit (kronika je append-only ZÁZNAM):
# ⚠ OMyl 208 (naměřeno tady): první verze porovnávala `soucasne[i]` s `po[i]`
# a hlásila, že se změnilo 650 řádků. Nebyly změněné — byly **POSUNUTÉ**
# o vložený řádek. Indexové srovnání po vložení je mimo o jeden řádek, a to
# vypadá jako hromadné poškození dokumentu. Porovnává se proto se SPRÁVNÝM
# posunem: řádky PŘED vložením na stejné pozici, řádky ZA vložením o jedna dál.
pred = [i + 1 for i in range(RADEK_33 - 1) if soucasne[i] != po[i]]
kont(pred == [], "řádky PŘED vloženým jsou beze změny", f"odlišné: {pred}")
posunute = [i + 1 for i in range(RADEK_33 - 1, len(soucasne))
            if soucasne[i] != po[i + 1]]
kont(posunute == [], "řádky ZA vloženým se jen POSUNULY, obsah zůstal",
     f"odlišné: {posunute[:10]}")

print(f"\n  KRONIKA: {len(po)} řádků, {KR.stat().st_size} B, "
      f"sha {hashlib.sha256(KR.read_bytes()).hexdigest()[:16]}")
print(f"\nVÝSLEDEK: {7 - chyb} kontrol, {chyb} chyb")
sys.exit(1 if chyb else 0)
