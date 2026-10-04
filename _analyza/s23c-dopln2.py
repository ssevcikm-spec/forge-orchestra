r"""Druhý doplněk k zápisu session 19 — omyly 95 a 96 (našly je až BRÁNY).

CO SE DOPLŇUJE A PROČ (oba jsou naměřené, ne odhadnuté)
  **95 — DOKUMENTOVAT VADU V `AGENTS.md` ROZBILO MUTAČNÍ TEST, KTERÝ TU VADU VRACÍ.**
      Do `AGENTS.md` přibyl odstavec, který vadu R1 **popisuje** — a v něm je
      **citovaný** řetězec `**„32 sloupců"**`. Tím se kotva mutačního testu
      `audit2a-mutace.py` (M2) stala **dvojznačnou** (`kotva 2x`), test správně
      odmítl mutovat a spadl. Naměřeno: `CHYBA: M2 se neprovedla (kotva 2x)`.
      **Je to přesně past `overovani` §9.8** — a tu jsem si do skillu zapsal
      **v téže session**.
  **96 — KONTROLA, KTERÁ ŽÁDALA SHODNÝ HASH U APPEND-ONLY DOKUMENTU.**
      `audit2b-over.py` ověřoval, že `HANDOFF.md` je „nedotčený", **rovností
      SHA-256 se snapshotem Úkolu 0**. Jenže **toutéž session do něj bylo
      legitimně připsáno** (§8j a §23 — přímý požadavek zadání, Úkol 6c).
      Kontrola tedy **nemohla projít, jakmile se udělalo to, co zadání žádá**.
      Naměřeno: `CHYBA: HANDOFF.md se od Úkolu 0 ZMĚNIL` a `HANDOFF.md:1143
      granulí NENÍ v ZÁZNAMECH` (kotva se posunula na **1174**).
      **Správné kritérium u append-only dokumentu je „je původní stav pořád
      celý uvnitř?" — a to je přesně A2.**

Skript nic neodebere; na konci spustí `kronika-kontrola.py`
i `handoff-kontrola-uplnost.py` a skončí `exit 1`, když některá nesedí.

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\s23c-dopln2.py
"""
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
K = WS / "KRONIKA-PROJEKTU.md"

OMYLY = (
    "| **95** | **Dokumentovat vadu v `AGENTS.md` ROZBILO mutační test, který tu "
    "vadu vrací** | přidal jsem do `AGENTS.md` odstavec, který vadu R1 "
    "**popisuje** — a v něm je `„32 sloupců\"` **citované podruhé**. Tím se kotva "
    "testu `audit2a-mutace.py` (M2) stala **dvojznačnou** | "
    "`CHYBA: M2 se neprovedla (kotva 2x)` — test to **správně odmítl** a spadl. "
    "Odhalil to až **společný běh všech bran na konci session**, ne čtení | "
    "Kotvu **zúžit na jednoznačné okolí** (`**„32 sloupců\"**, správně je`) — "
    "a **po každé editaci dokumentu, který je kotvou někde jinde, spustit "
    "i testy, které na něj míří**. Je to `overovani` **§9.8**, kterou jsem si "
    "do skillu zapsal **v téže session** — a přesto jsem do ní spadl |\n"
    "| **96** | **Kontrola, která žádala SHODNÝ HASH u APPEND-ONLY dokumentu** | "
    "`audit2b-over.py` ověřoval „`HANDOFF.md` je nedotčený\" **rovností SHA-256** "
    "se snapshotem Úkolu 0. Jenže **toutéž session do něj bylo legitimně "
    "připsáno** (§8j a §23 — přímý požadavek zadání, Úkol 6c) | "
    "`CHYBA: HANDOFF.md se od Úkolu 0 ZMĚNIL — nález R3 se nemá opravovat "
    "v datech!` a `HANDOFF.md:1143 granulí NENÍ v ZÁZNAMECH` — **druhá chyba "
    "byla jen posun řádků** (kotva se připsáním posunula na **1174**) | "
    "U **append-only** dokumentu se neptej „je stejný?\", ale **„je původní stav "
    "pořád celý uvnitř?\"** — to je A2. A **kotvu hledej podle OBSAHU, ne podle "
    "čísla řádku**: číslo se posune vždy, když se dokument doplní. "
    "*(Obě pravidla zapsána do `overovani` — viz návrh NA24)* |\n"
)

PRECOUNTS = [
    ("akční (dokončení auditu) 2. 10. 18:1x | **8** | **8** | **0** |",
     "akční (dokončení auditu) 2. 10. 18:1x | **10** | **10** | **0** |"),
    ("| **celkem** | **10 bloků, 19 sessions** | **89** | **73 = 82 %** | **37** |",
     "| **celkem** | **10 bloků, 19 sessions** | **91** | **75 = 82 %** | **37** |"),
    ("| **z toho vad MĚŘIDLA** | **73 = 82 %** |",
     "| **z toho vad MĚŘIDLA** | **75 = 82 %** |"),
    ("| **omylů celkem v `HANDOFF.md` (unikátní id)** | **94** |",
     "| **omylů celkem v `HANDOFF.md` (unikátní id)** | **96** |"),
    ("**§23** (výsledky dokončení auditu) · **§8j** (vlastní\nomyly **87–94**)",
     "**§23** (výsledky dokončení auditu) · **§8j** (vlastní\nomyly **87–96**)"),
]


def spust(skript):
    r = subprocess.run([sys.executable, str(WS / "_analyza" / skript)], cwd=str(WS),
                       capture_output=True, timeout=300)
    return r.returncode, r.stdout.decode("utf-8", "replace")


def main() -> int:
    h_pred, k_pred = HANDOFF.read_bytes(), K.read_bytes()
    h, k = h_pred.decode("utf-8"), k_pred.decode("utf-8")
    a = WS / "ZADANI-PO-AUDITU.md"
    z_pred = a.read_bytes()
    z = z_pred.decode("utf-8")

    print("=" * 88)
    print("DOPLNĚK 2 — omyly 95 a 96 (našly je brány) + přepočet")
    print("=" * 88)

    kotva = ("**A jeden údaj, který tomu nasvědčuje:** omyl **88** je **třetí "
             "výskyt téže")
    if "| **95** |" not in h:
        assert h.count(kotva) == 1, "kotva pro omyly 95/96 není 1×"
        h = h.replace(kotva, OMYLY + "\n" + kotva, 1)
    assert "| **95** |" in h and "| **96** |" in h, "omyly 95/96 se nevložily"
    stara = "— **87–94**"
    if stara in h:
        h = h.replace(stara, "— **87–96**", 1)
    h = h.replace("**Osm, všechny v měřidlech**", "**Deset, všechny v měřidlech**")
    assert "— **87–96**" in h, "hlavička 8j se neopravila"
    print("  omyly 95 a 96 v §8j: OK")

    for stary, novy in PRECOUNTS:
        for cil, nazev in ((h, "HANDOFF.md"), (k, "KRONIKA"), (z, "ZADANI")):
            pass
        if novy in k:
            continue
        if stary in k:
            k = k.replace(stary, novy, 1)
    # text v zadání pro další session
    z = z.replace("**§8j** (vlastní\nomyly **87–94**)", "**§8j** (vlastní\nomyly **87–96**)")
    z = z.replace("**89 omylů v 10 blocích**", "**91 omylů v 10 blocích**")
    z = z.replace("**73 = 82 %**", "**75 = 82 %**")
    print("  přepočet kroniky a zadání: OK")

    HANDOFF.write_bytes(h.encode("utf-8"))
    K.write_bytes(k.encode("utf-8"))
    a.write_bytes(z.encode("utf-8"))

    # ── Ověření: nic nezmizelo (záměrné změny = nahrazené CELÉ ŘÁDKY) ──────
    zamerne = set()
    for stary, novy in PRECOUNTS:
        if stary != novy:
            zamerne.update(l for l in k_pred.decode("utf-8").splitlines() if stary in l)
    zamerne.update(l for l in h_pred.decode("utf-8").splitlines() if "— **87–94**" in l)
    zamerne.update(l for l in h_pred.decode("utf-8").splitlines()
                   if "**Osm, všechny v měřidlech**" in l)
    zamerne.update(l for l in z_pred.decode("utf-8").splitlines()
                   if "**89 omylů v 10 blocích**" in l or "**73 = 82 %**" in l
                   or "omyly **87–94**" in l)
    for jmeno, pred, po in (("HANDOFF.md", h_pred, HANDOFF.read_bytes()),
                            ("KRONIKA-PROJEKTU.md", k_pred, K.read_bytes()),
                            ("ZADANI-PO-AUDITU.md", z_pred, a.read_bytes())):
        t_po = po.decode("utf-8")
        chybejici = [l for l in pred.decode("utf-8").splitlines()
                     if l.strip() and l not in t_po and l not in zamerne]
        print("  %-22s neobjasněně chybějících řádků: %d" % (jmeno, len(chybejici)))
        for l in chybejici[:3]:
            print("      CHYBI: %s" % l[:100])
        if chybejici:
            print("\nVYSLEDEK: něco zmizelo → exit 1")
            return 1

    kod_k, v_k = spust("kronika-kontrola.py")
    for l in v_k.splitlines():
        if l.strip().startswith(("omylů celkem", "nálezů H", "KRONIKA SEDÍ", "CHYBA", "NALEZENO")):
            print("  kronika: %s" % l.strip())
    kod_h, v_h = spust("handoff-kontrola-uplnost.py")
    for l in v_h.splitlines():
        if "kontrolovaných klíčů" in l or "CHYBÍ" in l or "VŠE OK" in l:
            print("  handoff: %s" % l.strip())
    print("\n  kronika-kontrola.py exit=%d | handoff-kontrola-uplnost.py exit=%d"
          % (kod_k, kod_h))
    if kod_k or kod_h:
        print("\nVYSLEDEK: některá brána nesedí → exit 1")
        return 1
    print("\nVYSLEDEK: omyly 95/96 zapsány, počty přepočteny, obě brány sedí. exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
