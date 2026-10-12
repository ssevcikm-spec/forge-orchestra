# p40-f-tail-rozbor.py — rozbor ŽIVÉHO tailu conductora po zlevnění tiku (P40).
#
# PROČ VLASTNÍ (H166/H191): rozbor s pevným jménem výstupu přepíše cizí doklad
# (P39 si pustila cizí sondu a přepsala doklad P38). Tenhle má VLASTNÍ jméno
# (`p40-f-tail-rozbor-vystup.txt`) a bere vstup argumentem.
#
# CO MĚŘÍ (a proč právě to):
#   1. OKNO Z DOKLADU, ne z hodinek (H188) — první a poslední `eventTimestamp`.
#   2. `cpuTime` cron eventů proti UČENÉMU CÍLI (10 ms = limit free plánu,
#      H185/H192) a proti BASELINE P39 (16–20 ms, medián 18) — to je celý důkaz
#      zlevnění. Zabitá invokace hlásí LIMIT, ne cenu (L27).
#   3. `scriptVersion.id` — musí být JEDINÁ a musí se rovnat `Current Version ID`
#      z logu deploye (krok 3 ověření nasazení).
#   4. Rozestupy cron eventů (tik má jít každou minutu; díra = neměřilo se).
#   5. Zpráva tiku — co tik hlásí (a jestli doběhl).
#
# Použití: $env:PYTHONIOENCODING='utf-8'; python _analyza\p40-f-tail-rozbor.py <raw.json>
# Exit 0 = změřeno; 2 = soubor/prázdný doklad.

import json
import pathlib
import re
import sys

WS = pathlib.Path(__file__).resolve().parents[1]
OUT = WS / "_analyza" / "p40-f-tail-rozbor-vystup.txt"
BASELINE_P39 = 18      # medián cpuTime cronu před zlevněním (H193)
LIMIT = 10             # CPU limit free plánu (dokumentace, H185)

if len(sys.argv) < 2:
    print("použití: python _analyza/p40-f-tail-rozbor.py <raw.json>")
    sys.exit(2)
raw_path = pathlib.Path(sys.argv[1])
if not raw_path.is_file():
    print(f"CHYBA: {raw_path} neexistuje")
    sys.exit(2)
raw = raw_path.read_text(encoding="utf-8", errors="replace")

# `wrangler tail --format json` píše pretty JSON: události se čtou VYVAŽOVÁNÍM
# závorek (řádkování je jen formalita a v P39 se osvědčilo).
udalosti = []
hloubka = 0
zacatek = -1
for i, c in enumerate(raw):
    if c == "{":
        if hloubka == 0:
            zacatek = i
        hloubka += 1
    elif c == "}":
        hloubka -= 1
        if hloubka == 0 and zacatek >= 0:
            try:
                udalosti.append(json.loads(raw[zacatek:i + 1]))
            except json.JSONDecodeError:
                pass
            zacatek = -1

radky = []
p = lambda x="": (radky.append(x), print(x))
p(f"# p40-f — rozbor živého tailu conductora — {raw_path.name} ({len(raw)} B)")
p(f"# cíl: cpuTime cronu POD {LIMIT} ms (baseline P39: medián {BASELINE_P39} ms)")
p("")

if not udalosti:
    p("CHYBA: v dokladu nejsou žádné JSON události.")
    OUT.write_text("\n".join(radky) + "\n", encoding="utf-8")
    sys.exit(2)

# ── 1b) PER-EVENT DETAIL (aby byl vidět každý tik jednotlivě) ───────────────
import datetime as _dt  # noqa: E402

p("## PER-EVENT DETAIL (čas UTC | druh | cpuTime | wallTime | outcome | zpráva tiku)")
for u in sorted(udalosti, key=lambda x: x.get("eventTimestamp", 0)):
    ev = u.get("event") or {}
    ts = _dt.datetime.utcfromtimestamp(u["eventTimestamp"] / 1000).strftime("%H:%M:%S")
    if ev.get("cron"):
        druh = "cron * * * * *"
    else:
        druh = "HTTP " + str((ev.get("request") or {}).get("url", "?")).split("workers.dev")[-1][:26]
    zprava = ""
    for log in u.get("logs") or []:
        text = " ".join(str(x) for x in (log.get("message") or []))
        if text.startswith("tick:"):
            zprava = text[:120]
    p(f"   {ts} | {druh:24} | {u.get('cpuTime', '?'):>4} | {u.get('wallTime', '?'):>5} "
      f"| {str(u.get('outcome')):4} | {zprava}")
p("")

# ── 1) OKNO Z DOKLADU (H188) ────────────────────────────────────────────────
casu = sorted(u.get("eventTimestamp") for u in udalosti if u.get("eventTimestamp"))
okno_min = (casu[-1] - casu[0]) / 60000.0 if casu else 0
p("## OKNO DOKLADU (z eventTimestamp, ne z hodinek — H188)")
p(f"   {len(udalosti)} eventů · {okno_min:.1f} min")
verze = sorted({(u.get("scriptVersion") or {}).get("id") for u in udalosti if (u.get("scriptVersion") or {}).get("id")})
p(f"   scriptVersion.id: {', '.join(verze) if verze else '(žádná)'}  ({len(verze)} různých)")
p("")

# ── 2) PODLE outcome ────────────────────────────────────────────────────────
podle = {}
for u in udalosti:
    k = u.get("outcome") or "?"
    podle[k] = podle.get(k, 0) + 1
p("## PODLE `outcome`")
for k, v in sorted(podle.items(), key=lambda x: -x[1]):
    p(f"   {v:4}×  {k}")
neok = sum(v for k, v in podle.items() if k != "ok")
p(f"   → NE-`ok` eventů: {neok} z {len(udalosti)}")
p("")

# ── 3) CRON EVENTY (to je tik) ──────────────────────────────────────────────
crony = [u for u in udalosti if (u.get("event") or {}).get("cron")]
http = [u for u in udalosti if not (u.get("event") or {}).get("cron")]
p("## CRON EVENTY (tik)")
if crony:
    cpu = [u.get("cpuTime", 0) for u in crony]
    cpu_s = sorted(cpu)
    med = cpu_s[len(cpu_s) // 2]
    p(f"   n={len(crony)}  cpuTime medián {med} ms (rozsah {min(cpu)}..{max(cpu)})"
      f"  · P39 baseline {BASELINE_P39} ms · limit {LIMIT} ms")
    p(f"   POD LIMITEM ({LIMIT} ms): {sum(1 for c in cpu if c < LIMIT)}/{len(cpu)}"
      f"  · na limitu a výš: {sum(1 for c in cpu if c >= LIMIT)}/{len(cpu)}")
    p(f"   změna proti P39: {med - BASELINE_P39:+d} ms (medián)")
    ok = sum(1 for u in crony if u.get("outcome") == "ok")
    p(f"   outcome ok: {ok}/{len(crony)}")
    # rozestupy
    tc = sorted(u["eventTimestamp"] for u in crony if u.get("eventTimestamp"))
    mez = [(tc[i + 1] - tc[i]) / 1000.0 for i in range(len(tc) - 1)]
    if mez:
        p(f"   rozestupy: medián {sorted(mez)[len(mez)//2]:.1f} s · max {max(mez):.1f} s"
          f" · přes 90 s: {sum(1 for m in mez if m > 90)}×")
    # zprávy tiku
    zpravy = 0
    for u in crony:
        for log in u.get("logs") or []:
            text = " ".join(str(x) for x in (log.get("message") or []))
            if text.startswith("tick:"):
                zpravy += 1
    p(f"   zpráv tiku v logu: {zpravy} z {len(crony)} cron eventů")
    if crony:
        for log in crony[-1].get("logs") or []:
            text = " ".join(str(x) for x in (log.get("message") or []))
            if text.startswith("tick:"):
                p(f"   poslední zpráva: {text[:240]}")
else:
    p("   ⚠ ŽÁDNÉ cron eventy v dokladu — okno nepokrývá tik (měření je nepoužitelné)")
p("")

# ── 4) CPU PODLE ENDPOINTU ──────────────────────────────────────────────────
p("## CPU PODLE DRUHU INVOKACE")
skup = {}
for u in udalosti:
    ev = u.get("event") or {}
    if ev.get("cron"):
        k = "cron * * * * *"
    else:
        req = ev.get("request") or {}
        k = f"HTTP {req.get('method', '?')} {req.get('url', '').split('?')[0].split('workers.dev')[-1] or '/'}"
    skup.setdefault(k, []).append(u.get("cpuTime", 0))
for k, v in sorted(skup.items(), key=lambda x: -len(x[1])):
    s = sorted(v)
    p(f"   {k[:40]:40} n={len(v):3}  medián {s[len(s)//2]:>4}  rozsah {min(v)}..{max(v)}")
p("")

# ── 5) SOUHRN PRO ZÁZNAM ────────────────────────────────────────────────────
p("## SOUHRN (to, co jde do záznamu)")
if crony:
    cpu = sorted(u.get("cpuTime", 0) for u in crony)
    med = cpu[len(cpu) // 2]
    verdikt = "POD LIMITEM" if med < LIMIT else "NAD LIMITEM"
    p(f"   tik: medián {med} ms → {verdikt} ({LIMIT} ms); P39 měla {BASELINE_P39} ms")
    p(f"   okno {okno_min:.1f} min · {len(udalosti)} eventů · ne-ok {neok}")
    p(f"   verze: {'JEDINÁ ' + verze[0] if len(verze) == 1 else '⚠ RŮZNÉ: ' + ', '.join(verze)}")

OUT.write_text("\n".join(radky) + "\n", encoding="utf-8")
print(f"\n[zapsano] {OUT}")
sys.exit(0 if crony else 1)
