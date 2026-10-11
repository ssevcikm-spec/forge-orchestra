r"""p37-tail-rozbor.py — VLASTNÍ parser živého `wrangler tail` (P37, Úkol A4 + B).

Proč vlastní parser: doklad `p37-tail-raw-vystup.txt` je syrový výstup
`wrangler tail --format json`, který píše pretty-printed objekty **ZA SEBOU**
(ne JSONL). P35 měl vlastní rozbor (`p35-tail-rozbor.py`), ale ten čte SVŮJ
doklad a jiné otázky; P37 potřebuje navíc **rozpad cron eventů podle `outcome`**
— protože živý stav je `exceededCpu` (tik umírá), a to je jiná otázka než
„jak drahý je tik, když žije“.

Měří:
  * počet eventů, rozpad podle `outcome`, podle endpointu (`request.url` / `cron`);
  * pro `cron` eventy: `cpuTime` (n, medián, rozsah, kolik× NENÍ `ok`);
  * pro `request` eventy: `cpuTime` podle cesty (medián);
  * verzi (`scriptVersion.id`) — křížová kontrola proti logu nasazení;
  * časové okno dokladu (`eventTimestamp`).

Použití:
  python _analyza/p37-tail-rozbor.py [doklad] [--json vystup.txt]
Výchozí doklad: _analyza/p37-tail-raw-vystup.txt
"""

import json
import pathlib
import statistics
import sys

WS = pathlib.Path(__file__).resolve().parent.parent
ANALYZA = WS / "_analyza"


def nacti_json_za_sebou(cesta: pathlib.Path):
    """`wrangler tail --format json` píše objekty ZA SEBOU (pretty-printed)."""
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
            # Poškozený/neúplný objekt (tail se ukončil uprostřed zápisu) — končíme.
            break
        ven.append(obj)
    return ven


def cesta_eventu(ev):
    req = ev.get("event", {}).get("request")
    if req:
        return "HTTP %s %s" % (req.get("method"), str(req.get("url", "")).split("?")[0]
                               .replace("https://forge-conductor.ssevcikm.workers.dev", ""))
    if "cron" in ev.get("event", {}):
        return "cron %s" % ev["event"]["cron"]
    return "?"


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    doklad = pathlib.Path(argv[0]) if argv else (ANALYZA / "p37-tail-raw-vystup.txt")
    vystup_json = None
    if "--json" in sys.argv:
        vystup_json = ANALYZA / sys.argv[sys.argv.index("--json") + 1]

    if not doklad.is_file():
        print("CHYBA: doklad %s NENÍ — měření neproběhlo" % doklad.name)
        return 1

    eventy = nacti_json_za_sebou(doklad)
    print("doklad: %s (%d B)" % (doklad.name, doklad.stat().st_size))
    if not eventy:
        print("CHYBA: v dokladu není ANI JEDEN čitelný objekt — měření neproběhlo")
        return 1

    podle_vysledku = {}
    podle_cesty = {}
    cron_casy = []
    verze = set()
    casy = []
    for ev in eventy:
        v = ev.get("outcome", "?")
        podle_vysledku[v] = podle_vysledku.get(v, 0) + 1
        c = cesta_eventu(ev)
        podle_cesty.setdefault(c, []).append(ev.get("cpuTime"))
        if c.startswith("cron"):
            cron_casy.append(ev.get("cpuTime"))
        if ev.get("scriptVersion", {}).get("id"):
            verze.add(ev["scriptVersion"]["id"])
        if ev.get("eventTimestamp"):
            casy.append(ev["eventTimestamp"])

    print("")
    print("## OKNO DOKLADU")
    if casy:
        import datetime
        a = datetime.datetime.fromtimestamp(min(casy) / 1000, datetime.timezone.utc)
        b = datetime.datetime.fromtimestamp(max(casy) / 1000, datetime.timezone.utc)
        print("   %s .. %s  (%.1f min)" % (a.isoformat(), b.isoformat(), (max(casy) - min(casy)) / 60000))
    print("   eventů: %d" % len(eventy))
    print("   scriptVersion.id: %s" % (", ".join(sorted(verze)) or "(žádná)"))

    print("")
    print("## PODLE `outcome`")
    for v, n in sorted(podle_vysledku.items(), key=lambda x: -x[1]):
        print("   %4d×  %s" % (n, v))
    nenulove = sum(n for v, n in podle_vysledku.items() if v != "ok")
    print("   → NE-`ok` eventů: %d z %d" % (nenulove, len(eventy)))

    print("")
    print("## CPU PODLE ENDPOINTU (cpuTime ms, medián / rozsah / n)")
    for c, t in sorted(podle_cesty.items(), key=lambda x: -len(x[1])):
        tt = [x for x in t if isinstance(x, (int, float))]
        if not tt:
            print("   %-34s n=%d  (bez cpuTime)" % (c[:34], len(t)))
            continue
        print("   %-34s n=%3d  medián %5s  rozsah %s..%s" % (
            c[:34], len(tt), statistics.median(tt), min(tt), max(tt)))

    print("")
    print("## CRON EVENTY ZVLÁŠŤ (to je tik)")
    if not cron_casy:
        print("   ⚠ ŽÁDNÝ cron event v dokladu — o tiku NENÍ změřeno nic")
    else:
        tt = [x for x in cron_casy if isinstance(x, (int, float))]
        print("   n=%d  medián %s ms  rozsah %s..%s ms" % (
            len(tt), statistics.median(tt), min(tt), max(tt)))
        # outcome zvlášť pro cron
        cron_vys = {}
        for ev in eventy:
            if cesta_eventu(ev).startswith("cron"):
                cron_vys[ev.get("outcome", "?")] = cron_vys.get(ev.get("outcome", "?"), 0) + 1
        for v, n in sorted(cron_vys.items(), key=lambda x: -x[1]):
            print("   %4d×  outcome=%s" % (n, v))
        if len(tt) < 5:
            print("   ⚠ POZOR: n=%d je málo na medián — číslo se musí číst jako předběžné" % len(tt))

    if vystup_json:
        vystup_json.write_text(json.dumps({
            "doklad": doklad.name, "eventu": len(eventy),
            "podle_outcome": podle_vysledku,
            "cron_casy": cron_casy,
            "verze": sorted(verze),
        }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("\n[zapsáno] %s" % vystup_json.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
