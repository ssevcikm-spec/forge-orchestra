r"""p38-b-tail-rozbor.py — VLASTNÍ rozbor živého `wrangler tail` (P38).

PROČ VLASTNÍ: P37 měl svůj rozbor (`p37-tail-rozbor.py`) a P35 taky — a každý
čte SVŮJ doklad a jinou otázku (H166: cizí sondu pouštěj s výstupem do vlastního
jména). P38 potřebuje navíc DVĚ věci, které ani jeden z nich neměl:

  1. **PER-EVENT DETAIL** — u každého eventu `cpuTime`, `outcome` a jestli v jeho
     `logs` byly slepé `ALTER TABLE` („duplicate column name"). P37 zapsala, že
     cron eventy umíraly a `/tick` prošel, ale NEZAPSALA, jestli umírající cron
     eventy obsahovaly ty tři chyby — a to je přesně to, co rozhoduje mezi
     „vadou cesty (scheduled vs. fetch)" a „vadou ceny práce".
  2. **SOUVISLOST POKRYTÍ** — cron má chodit KAŽDOU minutu; díra mezi dvěma
     cron eventy delší než ~90 s znamená, že doklad o tiku NENÍ souvislý, a
     „0× exceededCpu" by pak mohlo znamenat „neměřilo se" (nula není úspěch).

Použití:
  python _analyza/p38-b-tail-rozbor.py <doklad> [--json <vystup.json>]
Exit 0 = měřeno; 1 = doklad chybí/prázdný (měření NEPROBĚHLO).
"""

import datetime
import json
import pathlib
import statistics
import sys

WS = pathlib.Path(__file__).resolve().parent.parent
ANALYZA = WS / "_analyza"


def nacti_json_za_sebou(cesta: pathlib.Path):
    """`wrangler tail --format json` píše pretty-printed objekty ZA SEBOU (ne JSONL)."""
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


def popis_eventu(ev):
    req = ev.get("event", {}).get("request")
    if req:
        cesta = str(req.get("url", "")).split("?")[0].replace(
            "https://forge-conductor.ssevcikm.workers.dev", "")
        return "HTTP %s %s" % (req.get("method"), cesta)
    if "cron" in ev.get("event", {}):
        return "cron %s" % ev["event"]["cron"]
    return "?"


def je_cron(ev):
    return "cron" in ev.get("event", {})


def text_logu(ev):
    """Spojí `logs[].message` (může to být řetězec i pole) do jednoho textu."""
    kusy = []
    for l in ev.get("logs") or []:
        m = l.get("message")
        if isinstance(m, list):
            kusy.append(" ".join(str(x) for x in m))
        else:
            kusy.append(str(m))
    return " | ".join(kusy)


def cas(ev):
    t = ev.get("eventTimestamp")
    if not t:
        return None
    return datetime.datetime.fromtimestamp(t / 1000, datetime.timezone.utc)


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not argv:
        print("CHYBA: chybí cesta k dokladu tailu")
        return 2
    doklad = pathlib.Path(argv[0])
    vystup_json = None
    if "--json" in sys.argv:
        vystup_json = pathlib.Path(sys.argv[sys.argv.index("--json") + 1])

    if not doklad.is_file():
        print("CHYBA: doklad %s NENÍ — měření neproběhlo" % doklad)
        return 1

    eventy = nacti_json_za_sebou(doklad)
    print("doklad: %s (%d B)" % (doklad.name, doklad.stat().st_size))
    if not eventy:
        print("CHYBA: v dokladu není ANI JEDEN čitelný objekt — měření NEPROBĚHLO")
        return 1

    # ---- okno + verze -------------------------------------------------------
    casy = [c for c in (cas(e) for e in eventy) if c]
    verze = sorted({e.get("scriptVersion", {}).get("id") for e in eventy if e.get("scriptVersion", {}).get("id")})
    print("")
    print("## OKNO DOKLADU")
    if casy:
        print("   %s .. %s  (%.1f min, %d eventů)" % (
            min(casy).isoformat(), max(casy).isoformat(),
            (max(casy) - min(casy)).total_seconds() / 60, len(eventy)))
    print("   scriptVersion.id: %s" % (", ".join(verze) or "(žádná)"))

    # ---- podle outcome ------------------------------------------------------
    podle_vysledku = {}
    for e in eventy:
        podle_vysledku[e.get("outcome", "?")] = podle_vysledku.get(e.get("outcome", "?"), 0) + 1
    print("")
    print("## PODLE `outcome` (všechny eventy)")
    for v, n in sorted(podle_vysledku.items(), key=lambda x: -x[1]):
        print("   %4d×  %s" % (n, v))
    chybne = sum(n for v, n in podle_vysledku.items() if v != "ok")
    print("   → NE-`ok` eventů: %d z %d  (0 = žádná invokace nespadla)" % (chybne, len(eventy)))

    # ---- per-event detail ---------------------------------------------------
    print("")
    print("## PER-EVENT DETAIL (čas UTC | druh | cpuTime | wallTime | outcome | chyby ALTER v logu)")
    slepe_celkem = 0
    for e in eventy:
        t = cas(e)
        lg = text_logu(e)
        slepe = lg.count("duplicate column name")
        slepe_celkem += slepe
        print("   %s | %-34s | %5s | %6s | %-12s | %d" % (
            t.strftime("%H:%M:%S") if t else "?", popis_eventu(e)[:34],
            e.get("cpuTime"), e.get("wallTime"), e.get("outcome", "?"), slepe))
    print("   → slepých `ALTER TABLE` (duplicate column name) v CELÉM dokladu: %d" % slepe_celkem)

    # ---- cron zvlášť --------------------------------------------------------
    cron = [e for e in eventy if je_cron(e)]
    print("")
    print("## CRON EVENTY (to je tik)")
    if not cron:
        print("   ⚠ ŽÁDNÝ cron event v dokladu — o tiku NENÍ změřeno nic")
    else:
        cpu = [e.get("cpuTime") for e in cron if isinstance(e.get("cpuTime"), (int, float))]
        wall = [e.get("wallTime") for e in cron if isinstance(e.get("wallTime"), (int, float))]
        podle = {}
        for e in cron:
            podle[e.get("outcome", "?")] = podle.get(e.get("outcome", "?"), 0) + 1
        print("   n=%d  cpuTime medián %s ms (rozsah %s..%s)  wallTime medián %s ms" % (
            len(cron), statistics.median(cpu) if cpu else "?", min(cpu) if cpu else "?",
            max(cpu) if cpu else "?", statistics.median(wall) if wall else "?"))
        for v, n in sorted(podle.items(), key=lambda x: -x[1]):
            print("   %4d×  outcome=%s" % (n, v))
        print("   exceededCpu: %d z %d" % (podle.get("exceededCpu", 0), len(cron)))
        # souvislost: díry mezi po sobě jdoucími cron eventy
        cc = sorted([c for c in (cas(e) for e in cron) if c])
        diry = [(cc[i + 1] - cc[i]).total_seconds() for i in range(len(cc) - 1)]
        if diry:
            print("   rozestupy mezi cron eventy: medián %.1f s, max %.1f s, přes 90 s: %d×" % (
                statistics.median(diry), max(diry), sum(1 for d in diry if d > 90)))
        else:
            print("   ⚠ jediný cron event — souvislost pokrytí se měřit NEDÁ")
        # co tiky hlásily
        zpravy = [text_logu(e) for e in cron if text_logu(e)]
        print("   zpráv tiku v logu: %d z %d cron eventů" % (len(zpravy), len(cron)))
        for z in zpravy[:3]:
            print("     %s" % z[:300])

    # ---- CPU podle endpointu ------------------------------------------------
    print("")
    print("## CPU PODLE ENDPOINTU (cpuTime ms, medián / rozsah / n)")
    podle_cesty = {}
    for e in eventy:
        podle_cesty.setdefault(popis_eventu(e), []).append(e.get("cpuTime"))
    for c, t in sorted(podle_cesty.items(), key=lambda x: -len(x[1])):
        tt = [x for x in t if isinstance(x, (int, float))]
        if not tt:
            print("   %-34s n=%d  (bez cpuTime)" % (c[:34], len(t)))
            continue
        print("   %-34s n=%3d  medián %5s  rozsah %s..%s" % (
            c[:34], len(tt), statistics.median(tt), min(tt), max(tt)))

    if vystup_json:
        vystup_json.write_text(json.dumps({
            "doklad": doklad.name,
            "bajtu": doklad.stat().st_size,
            "eventu": len(eventy),
            "okno_od": min(casy).isoformat() if casy else None,
            "okno_do": max(casy).isoformat() if casy else None,
            "verze": verze,
            "podle_outcome": podle_vysledku,
            "cron_n": len(cron),
            "cron_cpu": [e.get("cpuTime") for e in cron],
            "cron_outcome": {e.get("outcome", "?"): 1 for e in cron},
            "slepe_alter_celkem": slepe_celkem,
        }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("\n[zapsáno] %s" % vystup_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
