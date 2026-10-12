# p40-b-profil.py — rozbor V8 CPU profilu z `p40-a-faze-tiku.mjs` (zadání P40, krok 1).
#
# PROČ: bucketové měření (`p40-a`) umí přiřadit jen fáze, které jde obalit.
# Zbytek („logika + JIT“) je pak černá skříňka — a přesně v ní může být ta
# chybějící polovina ceny tiku. V8 CPU profil přiřadí KAŽDÝ vzorek konkrétní
# funkci, takže je vidět i to, co by člověka nenapadlo měřit.
#
# VSTUP:  _analyza/p40-prof/CPU.*.cpuprofile (vzniká `node --cpu-prof …`)
# VÝSTUP: _analyza/p40-b-profil-vystup.txt
#
# ⚠ Profil je SAMPLOVACÍ: 1 vzorek = 100 µs (interval nastaven při běhu).
#   „ms“ níž je počet vzorků × interval, tedy odhad self-time, ne přesné CPU.
#
# Použití: $env:PYTHONIOENCODING='utf-8'; python _analyza\p40-b-profil.py <soubor.cpuprofile>
# Exit 0 = rozebráno; 2 = soubor nenalezen.

import json
import pathlib
import sys

WS = pathlib.Path(__file__).resolve().parents[1]
OUT = WS / "_analyza" / "p40-b-profil-vystup.txt"
INTERVAL_US = 100.0

if len(sys.argv) < 2:
    print("použití: python _analyza/p40-b-profil.py <soubor.cpuprofile>")
    sys.exit(2)
cesta = pathlib.Path(sys.argv[1])
if not cesta.is_file():
    print(f"CHYBA: {cesta} neexistuje")
    sys.exit(2)

profil = json.loads(cesta.read_text(encoding="utf-8"))
uzly = {n["id"]: n for n in profil["nodes"]}
interval = profil.get("timeDeltas") and (sum(profil["timeDeltas"]) / len(profil["timeDeltas"]) / 1000.0) or INTERVAL_US
interval = INTERVAL_US   # držíme se nastaveného intervalu (timeDeltas míchá i pauzy)

# self-time: hitCount uzlu × interval
self = {}
for n in profil["nodes"]:
    cf = n["callFrame"]
    klic = (cf.get("functionName") or "(anonym)", cf.get("url") or "")
    h = n.get("hitCount", 0)
    if h:
        self[klic] = self.get(klic, 0) + h

celkem_vzorku = sum(self.values())
radky = []
p = lambda x="": (radky.append(x), print(x))

p(f"# p40-b — V8 CPU profil tiku (rozbor) — {cesta.name}")
p(f"# interval vzorkování: {interval:.0f} µs · vzorků s přiřazením: {celkem_vzorku}"
  f" · celkem {celkem_vzorku * interval / 1000:.1f} ms self-time")
p("")

p("## SELF-TIME PODLE FUNKCE (top 30)")
p("     ms  | podíl | funkce @ soubor")
for (fn, url), h in sorted(self.items(), key=lambda x: -x[1])[:30]:
    ms = h * interval / 1000.0
    podil = 100.0 * h / celkem_vzorku if celkem_vzorku else 0
    kratky = url.split("/")[-1].split("?")[0] if url else ""
    p(f"  {ms:6.1f} | {podil:5.1f}% | {fn[:52]:52} @ {kratky[:40]}")

# Souhrn po „druhu práce“ — klíčová slova z názvů funkcí a URL.
def druh(fn, url):
    f = fn.lower()
    if "garbage" in f or "gc" == f:
        return "GC (úklid paměti)"
    if "(compile" in f or "parse" in f and "json" not in f:
        return "kompilace/parse skriptu"
    if "json" in f or "parse" in f:
        return "JSON.parse"
    if "decode" in f or "utf8" in f or "utf-8" in f:
        return "TextDecoder/UTF-8"
    if "atob" in f or "base64" in f:
        return "base64"
    if "stringify" in f:
        return "JSON.stringify"
    if "d1" in f or "prepare" in f or "sql" in f:
        return "D1 klient"
    if "fetch" in f or "response" in f or "headers" in f:
        return "fetch/Response"
    if url.endswith("index.js"):
        return "logika conductora"
    return "runtime Node"

souhrn = {}
for (fn, url), h in self.items():
    k = druh(fn, url)
    souhrn[k] = souhrn.get(k, 0) + h
p("")
p("## SOUHRN PO DRUHU PRÁCE")
for k, h in sorted(souhrn.items(), key=lambda x: -x[1]):
    p(f"  {h * interval / 1000:7.1f} ms | {100.0 * h / celkem_vzorku:5.1f}% | {k}")

p("")
p("## LOGIKA CONDUCTORA — nejsilnější vlastní funkce (top 15)")
p("     ms  | funkce")
for (fn, url), h in sorted(self.items(), key=lambda x: -x[1]):
    if not url.endswith("index.js"):
        continue
    p(f"  {h * interval / 1000:6.1f} | {fn[:70]}")
    if sum(1 for (f2, u2), _ in self.items() if u2.endswith("index.js") and self[(f2, u2)] >= h) > 15:
        break

OUT.write_text("\n".join(radky) + "\n", encoding="utf-8")
print(f"\n[zapsano] {OUT}")
sys.exit(0)
