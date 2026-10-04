# -*- coding: utf-8 -*-
"""Změří, KOLIK ČASU zabere každá brána projektu (audit dokumentace, fáze 5).

PROČ TENHLE SKRIPT EXISTUJE:
  Podnětem k auditu je, že práce agenta trvá půl hodiny místo pár minut.
  Jedna z hypotéz je „povinná metodika je drahá" — a ta se MUSÍ změřit, ne
  odhadnout (`AGENTS.md`: „mně to přijde zdlouhavé" není měření).
  Tenhle skript změří wall time KAŽDÉ brány z `g3-brany.py`.

JAK (a proč zrovna takhle):
  `g3-brany.py` se NEUPRAVUJE. Je to živá brána a audit do ní nesmí sahat
  (pravidlo A3: audit navrhuje, provádí jiná session). Místo úpravy se jeho
  zdroj NAČTE a spustí s podstrčeným `subprocess.run`, které každé volání
  změří. Díky tomu se měří TOTÉŽ, co měří `g3-brany.py` — ne jeho kopie,
  která by mohla tiše zestárnout (to je přesně vada S27).

  Výstupní soubor `g3-brany-vystup.txt` se přesměruje na `audit5-cas-vystup.txt`,
  aby se NEPŘEPSAL důkaz z posledního běhu.

CO SE VYPÍŠE:
  * tabulka „brána → sekundy → co otevřela → exit",
  * součet a podíl na celku,
  * **brány, které neotevřely nic** (`otevřela: —`) — to je nález fáze 5,
  * brány s nenulovým exit, ROZLIŠENÉ na „vada" a „neproběhlo (prostředí)".

Použití:  python _analyza/audit5-cas-bran.py [--json _analyza/audit5-cas.json]
Návrat:   0 vždy (je to měřidlo, ne brána) — nálezy jsou ve výstupu a v JSONu.
"""

import contextlib
import io
import json
import pathlib
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
G3 = WS / "_analyza" / "g3-brany.py"

# ── 1. Podstrčené měření ────────────────────────────────────────────────────
ZAZNAM = []
_ORIG_RUN = subprocess.run


def _mereny_run(prikaz, *a, **k):
    t0 = time.perf_counter()
    try:
        r = _ORIG_RUN(prikaz, *a, **k)
    except Exception:                                            # noqa: BLE001
        ZAZNAM.append({"prikaz": prikaz, "sekundy": time.perf_counter() - t0,
                       "exit": None})
        raise
    ZAZNAM.append({"prikaz": prikaz, "sekundy": time.perf_counter() - t0,
                   "exit": r.returncode})
    return r


# ── 2. Přesměrování výstupního souboru (aby se nepřepsal důkaz) ─────────────
_ORIG_WRITE_BYTES = pathlib.Path.write_bytes
PRESMEROVANO = []


def _patched_write_bytes(self, data):
    if self.name == "g3-brany-vystup.txt":
        PRESMEROVANO.append(str(self))
        self = self.with_name("audit5-cas-vystup.txt")
    return _ORIG_WRITE_BYTES(self, data)


# ── 3. Spuštění g3 se šavlí ────────────────────────────────────────────────
def main() -> int:
    json_cesta = WS / "_analyza" / "audit5-cas.json"
    argv = sys.argv[1:]
    if "--json" in argv:
        json_cesta = pathlib.Path(argv[argv.index("--json") + 1])

    if not G3.is_file():
        print("CHYBA: %s neexistuje — není co měřit" % G3)
        return 0

    zdroj = G3.read_text(encoding="utf-8")
    buf = io.StringIO()
    subprocess.run = _mereny_run
    pathlib.Path.write_bytes = _patched_write_bytes
    t0 = time.perf_counter()
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(zdroj, str(G3), "exec"), {"__name__": "__main__",
                                                   "__file__": str(G3)})
    finally:
        subprocess.run = _ORIG_RUN
        pathlib.Path.write_bytes = _ORIG_WRITE_BYTES

    vystup = buf.getvalue()

    # ── 4. Spojení: g3 vypsal jména a „otevřela" v témže pořadí, v jakém
    #       volal subprocess.run. Nic se neparsuje „odhadem" — páruje se pořadím
    #       a počet se KONTROLUJE (když nesedí, je to vidět, ne ticho).
    radky = []
    for L in vystup.splitlines():
        m = re.match(r"^  (OK  |exit=\S+)\s+(.+?)\s+otevřela: (.*)$", L)
        if m:
            radky.append((m.group(1).strip(), m.group(2).strip(), m.group(3).strip()))

    if len(radky) != len(ZAZNAM):
        print("VAROVÁNÍ: g3 vypsal %d bran, ale změřeno %d volání subprocess.run"
              % (len(radky), len(ZAZNAM)))
        print("         (párování pořadím by bylo nejisté — níž se páruje jen"
              " to, co sedí)")

    zaznamy = []
    for i, z in enumerate(ZAZNAM):
        popis = radky[i][1] if i < len(radky) else "(nepářováno)"
        otevrela = radky[i][2] if i < len(radky) else "?"
        exit_kod = radky[i][0] if i < len(radky) else "?"
        prikaz = z["prikaz"]
        zaznamy.append({
            "poradi": i + 1,
            "brana": popis,
            "prikaz": " ".join(str(x) for x in prikaz)[:200],
            "sekundy": round(z["sekundy"], 2),
            "exit": exit_kod,
            "otevrela": otevrela,
        })

    celkem = time.perf_counter() - t0
    soucet = sum(z["sekundy"] for z in zaznamy)

    print("=" * 90)
    print("AUDIT 5 — KOLIK ČASU ZABEROU POVINNÉ BRÁNY")
    print("=" * 90)
    print()
    print("  %-32s %9s  %9s  %s" % ("brána", "sekundy", "% celku", "co otevřela"))
    print("  " + "-" * 86)
    for z in sorted(zaznamy, key=lambda x: -x["sekundy"]):
        podil = (100.0 * z["sekundy"] / soucet) if soucet else 0.0
        print("  %-32s %9.1f  %8.1f%%  %s"
              % (z["brana"][:32], z["sekundy"], podil, z["otevrela"][:36]))
    print("  " + "-" * 86)
    print("  %-32s %9.1f" % ("SOUČET BRAN", soucet))
    print("  %-32s %9.1f  (včetně režie skriptu)" % ("CELKOVÝ WALL TIME", celkem))
    print()

    # ── 5. Nálezy fáze 5 ────────────────────────────────────────────────────
    nic = [z for z in zaznamy if z["otevrela"] in ("—", "", "?")]
    if nic:
        print("  BRÁNY, KTERÉ NEOTEVŘELY NIC (vzor, který usnul / neměřila):")
        for z in nic:
            print("      %-32s exit=%s" % (z["brana"][:32], z["exit"]))
    else:
        print("  Každá brána vykázala, co otevřela (0 bran s '—').")
    print()

    zle = [z for z in zaznamy if z["exit"] not in ("OK",)]
    if zle:
        print("  BRÁNY S NENULOVÝM EXITEM:")
        for z in zle:
            print("      %-32s exit=%-8s %s" % (z["brana"][:32], z["exit"],
                                                z["otevrela"][:30]))
    print()

    if PRESMEROVANO:
        print("  (výstup g3 přesměrován, původní důkaz nedotčen: %s)"
              % PRESMEROVANO[0])

    json_cesta.write_text(json.dumps({
        "wall_time_celkem_s": round(celkem, 2),
        "soucet_bran_s": round(soucet, 2),
        "bran": zaznamy,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("  JSON: %s" % json_cesta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
