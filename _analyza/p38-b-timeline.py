r"""p38-b-timeline.py — ČASOVÁ OSA zdraví CRON TIKU ze všech žijících dokladů `tail` (P38).

PROČ: P37 zapsala „rozdíl je v CESTĚ (scheduled vs. fetch)". Jenže P35 naměřila
cron eventy s `outcome=ok` a `cpuTime` 24–36 ms — tedy TÁŽ cesta, která později
umírala. Otázka „kdy a na které VERZI cron umíral" se z jednoho dokladu
nezodpoví; potřebuje časovou osu přes VŠECHNY doklady, které v `_analyza/` jsou.

Skript nic nemění — jen čte `*tail*` doklady a vypíše pro každý:
  okno, verzi (`scriptVersion.id`), počet cron eventů, rozpad `outcome`,
  cpuTime cronu (n/medián/rozsah) a wallTime cronu (medián).

Použití:
  python _analyza/p38-b-timeline.py [--json vystup.json]
Exit 0 = měřeno; 2 = žádný doklad nenalezen (měření NEPROBĚHLO).
"""

import datetime
import glob
import json
import pathlib
import statistics
import sys

WS = pathlib.Path(__file__).resolve().parent.parent
ANALYZA = WS / "_analyza"


def nacti_json_za_sebou(cesta: pathlib.Path):
    text = cesta.read_text(encoding="utf-8", errors="replace")
    dek = json.JSONDecoder()
    i, ven = 0, []
    while i < len(text):
        while i < len(text) and text[i] in " \t\r\n":
            i += 1
        if i >= len(text):
            break
        try:
            obj, i = dek.raw_decode(text, i)
        except ValueError:
            break
        ven.append(obj)
    return ven


def je_cron(ev):
    return "cron" in ev.get("event", {})


def cas(ev):
    t = ev.get("eventTimestamp")
    return datetime.datetime.fromtimestamp(t / 1000, datetime.timezone.utc) if t else None


def popis(doklad: pathlib.Path):
    eventy = nacti_json_za_sebou(doklad)
    if not eventy:
        return None
    cron = [e for e in eventy if je_cron(e)]
    casy = [c for c in (cas(e) for e in eventy) if c]
    cc = sorted([c for c in (cas(e) for e in cron) if c])
    cpu = [e.get("cpuTime") for e in cron if isinstance(e.get("cpuTime"), (int, float))]
    wall = [e.get("wallTime") for e in cron if isinstance(e.get("wallTime"), (int, float))]
    podle = {}
    for e in cron:
        podle[e.get("outcome", "?")] = podle.get(e.get("outcome", "?"), 0) + 1
    verze = sorted({e.get("scriptVersion", {}).get("id", "")[:8] for e in eventy if e.get("scriptVersion", {}).get("id")})
    return {
        "doklad": doklad.name,
        "bajtu": doklad.stat().st_size,
        "od": min(casy).isoformat() if casy else None,
        "do": max(casy).isoformat() if casy else None,
        "eventu": len(eventy),
        "verze": verze,
        "cron_n": len(cron),
        "cron_outcome": podle,
        "cron_cpu_median": statistics.median(cpu) if cpu else None,
        "cron_cpu_min": min(cpu) if cpu else None,
        "cron_cpu_max": max(cpu) if cpu else None,
        "cron_wall_median": statistics.median(wall) if wall else None,
        "cron_prvni": cc[0].strftime("%H:%M:%S") if cc else None,
        "cron_posledni": cc[-1].strftime("%H:%M:%S") if cc else None,
    }


def main():
    doklady = sorted(set(
        [pathlib.Path(p) for p in glob.glob(str(ANALYZA / "*tail*vystup.txt"))]
        + [pathlib.Path(p) for p in glob.glob(str(ANALYZA / "*tail*-raw-vystup.txt"))]
    ))
    if not doklady:
        print("CHYBA: v _analyza/ není ŽÁDNÝ doklad tailu — měření NEPROBĚHLO")
        return 2

    print("# p38-b — časová osa zdraví cron tiku z dokladů `wrangler tail`")
    print("")
    print("doklad                              | okno (UTC)              | verze    | cron | outcome (cron)            | cpuTime med/min/max | wall med")
    vysledky = []
    for d in doklady:
        try:
            p = popis(d)
        except Exception as e:  # poškozený doklad se musí POJMENOVAT, ne zmizet
            print("%-35s | CHYBA PARSOVÁNÍ: %s" % (d.name[:35], str(e)[:60]))
            continue
        if not p:
            print("%-35s | (žádný čitelný objekt)" % d.name[:35])
            continue
        vysledky.append(p)
        okno = "%s..%s" % (p["od"][11:19] if p["od"] else "?", p["do"][11:19] if p["do"] else "?")
        out = ", ".join("%s=%d" % (k, v) for k, v in sorted(p["cron_outcome"].items()))
        print("%-35s | %-23s | %-8s | %4d | %-25s | %s/%s/%s | %s" % (
            p["doklad"][:35], okno, ",".join(p["verze"])[:8], p["cron_n"], out[:25],
            p["cron_cpu_median"], p["cron_cpu_min"], p["cron_cpu_max"], p["cron_wall_median"]))

    # kontrola, že osa NENÍ prázdná
    s_cronem = [v for v in vysledky if v["cron_n"]]
    print("")
    print("dokladů: %d, z toho s cron eventy: %d" % (len(vysledky), len(s_cronem)))
    if not s_cronem:
        print("CHYBA: ANI JEDEN doklad neobsahuje cron event — o zdraví tiku NENÍ změřeno nic")
        return 1

    if "--json" in sys.argv:
        cesta = pathlib.Path(sys.argv[sys.argv.index("--json") + 1])
        cesta.write_text(json.dumps(vysledky, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("[zapsáno] %s" % cesta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
