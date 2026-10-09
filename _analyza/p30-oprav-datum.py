# -*- coding: utf-8 -*-
r"""P30 — OPRAVA ZÁZNAMU, KTERÝ ROZBILA ZNOVU PUSTĚNÁ JEDNORÁZOVKA Z P27.

CO SE STALO (naměřeno 9. 10. 2026, ne odhadnuto):
  Dávka dokladů `_analyza/p20-d-doklady.py` spouští i **jednorázové patchery
  starých session** — mezi nimi `p27-oprav-datum.py`, který 8. 10. 2026
  **jednorázově** opravil špatné datum v záznamu P27. Jenže opravený text
  obsahuje **obě** data („zadání vzniklo 7. 10. večer… ověřeno, že v nich
  7. 10. už není“), takže **druhý běh** patcheru přepíše i to správné a záznam
  se stane **vnitřně rozporným** („zadání vzniklo 8. 10. 2026 večer“ u session,
  která měřila 8. 10. dopoledne).

  Zasažené soubory (tři, naměřeno `git diff`):
    * `HANDOFF.md` §57 (dva řádky bloku omylů P27),
    * `KRONIKA-PROJEKTU.md` řádek `P27-O` v §2.20,
    * `_analyza/p27-radek-kroniky.py` (týž text vložený ve skriptu).

CO SKRIPT DĚLÁ: vrátí **jen ta tři místa** na text z `HEAD` (`git show
HEAD:<soubor>`) — u skriptu celý soubor, v dokumentech dvě/tři cílené záměny.
**Idempotentní:** druhý běh najde správný text a jen to řekne.

Použití: python _analyza\p30-oprav-datum.py [--kontrola]
"""

import argparse
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
VECER = "večer".encode("utf-8")

# (soubor, co má být správně, co tam je teď) — každé právě 1×
OPRAVY = [
    (WS / "HANDOFF.md",
     "    **7. 10. 2026** večer — a do záznamů jsem **opsal jeho datum**, ačkoli",
     "    **8. 10. 2026** večer — a do záznamů jsem **opsal jeho datum**, ačkoli"),
    (WS / "HANDOFF.md",
     "    cizí záznamy nedotčeny) a ověřeno, že v nich `7. 10. 2026` už není.",
     "    cizí záznamy nedotčeny) a ověřeno, že v nich `8. 10. 2026` už není."),
    (WS / "KRONIKA-PROJEKTU.md",
     "Zadání P27 vzniklo **7. 10. 2026** večer — a do vlastních záznamů jsem",
     "Zadání P27 vzniklo **8. 10. 2026** večer — a do vlastních záznamů jsem"),
]

# Soubor, který se rovnou vrátí z gitu (P30 do něj nezasáhl) — bajt na bajt.
VRATIT = [(WS / "_analyza" / "p27-radek-kroniky.py", "_analyza/p27-radek-kroniky.py")]

kontrol = 0
chyby = []


def k(podminka, popis):
    global kontrol
    kontrol += 1
    print("  %s  %s" % ("OK  " if podminka else "CHYBA", popis))
    if not podminka:
        chyby.append(popis)


def blob(rel):
    r = subprocess.run(["git", "show", "HEAD:" + rel], cwd=str(WS), capture_output=True)
    return r.stdout if r.returncode == 0 else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kontrola", action="store_true")
    args = ap.parse_args()
    kdo = "KONTROLA" if args.kontrola else "ZÁPIS"

    # ── 1) soubor, který se vrací z gitu ─────────────────────────────────
    for cesta, rel in VRATIT:
        ted = cesta.read_bytes()
        head = blob(rel)
        k(head is not None, "git zná %s" % rel)
        if head is None:
            continue
        if ted == head:
            print("  --    %s je už shodný s HEAD (idempotentní běh)" % rel)
            continue
        k(b"**8. 10. 2026** " + VECER in ted and b"**7. 10. 2026** " + VECER in head,
          "%s: vada JE na disku a HEAD má správný text (oba %d B)" % (rel, len(ted)))
        if not args.kontrola and b"**8. 10. 2026** " + VECER in ted:
            cesta.write_bytes(head)
            k(cesta.read_bytes() == head, "%s vrácen bajt na bajt z HEAD" % rel)

    # ── 2) cílené záměny v dokumentech ───────────────────────────────────
    for cesta, spravne, spatne in OPRAVY:
        t = cesta.read_text(encoding="utf-8")
        rel = cesta.relative_to(WS).as_posix()
        if t.count(spravne) >= 1 and t.count(spatne) == 0:
            print("  --    %s: text je UŽ správný (idempotentní běh)" % rel)
            continue
        k(t.count(spatne) == 1, "%s: vadný text je tam právě 1× (%d×)" % (rel, t.count(spatne)))
        if not args.kontrola and t.count(spatne) == 1:
            cesta.write_bytes(t.replace(spatne, spravne, 1).encode("utf-8"))
            k(cesta.read_text(encoding="utf-8").count(spatne) == 0,
              "%s: vadný text je pryč" % rel)

    # ── 3) souhrnná kontrola rozporného data ─────────────────────────────
    for cesta, _, spatne in OPRAVY:
        t = cesta.read_text(encoding="utf-8")
        k(t.count(spatne) == 0,
          "%s: rozporné datum „%s…“ v souboru NENÍ" % (cesta.name, spatne[:38]))

    print("[%s] VÝSLEDEK: %d kontrol, %d chyb" % (kdo, kontrol, len(chyby)))
    for c in chyby:
        print("  CHYBA: %s" % c)
    return 1 if chyby else 0


if __name__ == "__main__":
    sys.exit(main())
