r"""p37-tail-logy.py — co conductor v živém tailu SKUTEČNĚ zalogoval (P37, Úkol B).

Proč: `exceededCpu` event má `logs: []` — izolát umřel dřív, než stihl logy
vyflusnout. Kdežto event, který projde (`outcome: ok`, např. ruční `POST /tick`),
své `console.log` NESE. Tenhle skript je vypíše — je to jediné místo, kde je
vidět, co tik v produkci dělal, a kolik ho to stálo.

Použití: python _analyza/p37-tail-logy.py [doklad]
"""

import json
import pathlib
import sys

WS = pathlib.Path(__file__).resolve().parent.parent
ANALYZA = WS / "_analyza"


def nacti(cesta):
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


def popis(ev):
    req = ev.get("event", {}).get("request")
    if req:
        return "HTTP %s %s" % (req.get("method"), str(req.get("url", "")).split("?")[0]
                               .replace("https://forge-conductor.ssevcikm.workers.dev", ""))
    if "cron" in ev.get("event", {}):
        return "cron %s" % ev["event"]["cron"]
    return "?"


cesty = [a for a in sys.argv[1:] if not a.startswith("--")]
doklad = pathlib.Path(cesty[0]) if cesty else (ANALYZA / "p37-tail-raw-vystup.txt")
if not doklad.is_file():
    print("CHYBA: doklad %s NENÍ" % doklad.name)
    sys.exit(1)

eventy = nacti(doklad)
print("doklad %s: %d eventů" % (doklad.name, len(eventy)))
print("")
print("endpoint                          | outcome      | cpu ms | logs")
for ev in eventy:
    logy = ev.get("logs") or []
    texty = [str(l.get("message", l)) for l in logy]
    print("%-33s | %-12s | %6s | %s" % (popis(ev)[:33], ev.get("outcome"), ev.get("cpuTime"),
                                        (" || ".join(texty)[:150] if texty else "(žádné)")))
    if ev.get("exceptions"):
        print("    VÝJIMKY: %s" % json.dumps(ev["exceptions"])[:300])

print("")
print("## PLNÉ LOGY (kde nějaké jsou)")
for ev in eventy:
    logy = ev.get("logs") or []
    if not logy:
        continue
    print("")
    print("### %s  [%s, cpuTime=%s]" % (popis(ev), ev.get("outcome"), ev.get("cpuTime")))
    for l in logy:
        print("    %s" % json.dumps(l, ensure_ascii=False)[:400])
