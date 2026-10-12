# p40-i-sonda2-rozbor.py — rozbor DRUHÉHO kola sondy (P40): baseline cron
# invokace, režie jednoho `fetch()` a režie D1 round-tripu.
#
# PROČ VZNIKL: první kolo změřilo režii D1 (0,42–0,90 ms/round-trip) a podle
# toho se tik zlevnil — ale živý tik zůstal na 18 ms. Rozklad tedy nesedí a je
# potřeba změřit, KDE cena je: kolik stojí PRÁZDNÁ cron invokace (baseline),
# kolik jeden `fetch()` a kolik D1 (kontrola opakovatelnosti).
#
# Použití: python _analyza\p40-i-sonda2-rozbor.py <raw.json>

import json
import pathlib
import sys

WS = pathlib.Path(__file__).resolve().parents[1]
OUT = WS / "_analyza" / "p40-i-sonda2-vystup.txt"

if len(sys.argv) < 2:
    print("použití: python _analyza/p40-i-sonda2-rozbor.py <raw.json>")
    sys.exit(2)
raw = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")

ud = []
h = 0
z = -1
for i, c in enumerate(raw):
    if c == "{":
        if h == 0:
            z = i
        h += 1
    elif c == "}":
        h -= 1
        if h == 0 and z >= 0:
            try:
                ud.append(json.loads(raw[z:i + 1]))
            except json.JSONDecodeError:
                pass
            z = -1

radky = []
p = lambda x="": (radky.append(x), print(x))
p(f"# p40-i — druhé kolo sondy ({pathlib.Path(sys.argv[1]).name}, {len(raw)} B)")

crony = [u for u in ud if (u.get("event") or {}).get("cron")]
http = [u for u in ud if not (u.get("event") or {}).get("cron")]

p("")
p("## CRON: PRÁZDNÁ INVAKACE (baseline — kolik stojí tik, i kdyby nic nedělal)")
if crony:
    cpu = sorted(u.get("cpuTime", 0) for u in crony)
    p(f"   n={len(crony)}  cpuTime: {cpu}  → medián {cpu[len(cpu)//2]} ms")
    p(f"   wallTime: {[u.get('wallTime') for u in crony]}")
    p(f"   outcome: {sorted({u.get('outcome') for u in crony})}")
else:
    p("   ⚠ ŽÁDNÉ cron eventy — baseline NEMĚŘEN (okno nepokrylo tik sondy)")

p("")
p("## HTTP POŽADAVKY (podle query)")
p("   query                     | cpuTime | wallTime | outcome")
for u in sorted(http, key=lambda x: x.get("eventTimestamp", 0)):
    q = str(((u.get("event") or {}).get("request") or {}).get("url", "")).split("?")[-1]
    p(f"   {q[:24]:25} | {u.get('cpuTime', '?'):>7} | {u.get('wallTime', '?'):>8} | {u.get('outcome')}")

p("")
p("## ODVOZENÉ HODNOTY (režie na JEDNU operaci)")
def cpu_of(pred):
    return [u.get("cpuTime", 0) for u in http
            if pred(str(((u.get("event") or {}).get("request") or {}).get("url", "")))]

def med(a):
    s = sorted(a)
    return s[len(s) // 2] if s else None

zaklad = cpu_of(lambda q: "/?token" in q and "f=" not in q and "d1=" not in q and "batch=" not in q)
for n, popis in ((1, "f=1"), (5, "f=5"), (10, "f=10")):
    v = cpu_of(lambda q, n=n: f"f={n}" in q)
    if v and zaklad:
        p(f"   {popis:8}: cpuTime {v} → režie na JEDEN fetch ≈ "
          f"{((med(v) - med(zaklad)) / n):.2f} ms")
for n in (20, 50):
    v = cpu_of(lambda q, n=n: f"d1={n}" in q)
    if v and zaklad:
        p(f"   d1={n:<6}: cpuTime {v} → režie na JEDEN D1 round-trip ≈ "
          f"{((med(v) - med(zaklad)) / n):.2f} ms")
for n in (20, 50):
    v = cpu_of(lambda q, n=n: f"batch={n}" in q)
    if v:
        p(f"   batch={n:<4}: cpuTime {v}  (N příkazů JEDNÍM voláním)")

p("")
p("## SOUVISLOST S ŽIVÝM TIKEM (18–19 ms, verze db95d2d3)")
p("   Tik dělá ~13 D1 round-tripů a 3 fetche. Když baseline cronu + 13×D1 + 3×fetch")
p("   nedá ~18 ms, je cena jinde než v počtu operací — a to je nález, ne detail.")

OUT.write_text("\n".join(radky) + "\n", encoding="utf-8")
print(f"\n[zapsano] {OUT}")
sys.exit(0)
