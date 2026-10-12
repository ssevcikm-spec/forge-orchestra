"""Rozbor ŽIVÉHO `wrangler tail` conductora pro P41 (H197/H201).

CO MĚŘÍ (a co z toho plyne):
  · `cpuTime`/`wallTime` per invokace (runtime je hlásí JEN za celou invokaci),
  · `iso=` z řádku `tick-prof:` → které invokace šly v TÉMŽ izolátu,
  · `faze=` + ceny fází → wall time po fázích a u měřicích tiků i to, po které
    fázi se zastavilo (z rozdílu `cpuTime` mezi `faze=N` a `faze=N+1` v TÉMŽ
    izolátu je cena fáze N+1),
  · `event.cron` vs `event.request.url` → cron (čerstvý izolát) vs ruční tik.

⚠ OKNO SE POČÍTÁ Z DOKLADU, ne z hodinek (H188) — proto se vypisuje první
a poslední event včetně délky okna. Doklad s pevným jménem nese jen POSLEDNÍ běh
(H191), proto má tenhle rozbor vlastní výstupní jméno.

Použití: python _analyza/p41-c-tail-rozbor.py <doklad.txt> [--vystup <cesta>] [--json <vystup.json>]

Výchozí výstup = `<doklad-bez-přípony>-rozbor.txt`, tedy VLASTNÍ jméno pro každé
okno. Pevné jméno by znamenalo, že druhé okno přepíše doklad prvního (H191).
"""

import json
import pathlib
import statistics
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]

radky = []


def zapis(x=""):
    radky.append(x)
    print(x)


def objekty(text):
    """Vytáhne z textu VŠECHNY vyvážené JSON objekty (tail píše pretty-print).

    Proč ne `splitlines()`: `wrangler tail --format json` sází každý event jako
    pretty-printed objekt; řádkový parser by se rozbil na vnořených objektech.
    """
    out = []
    hloubka = 0
    zacatek = None
    v_ret = False
    escapovano = False
    for i, ch in enumerate(text):
        if v_ret:
            if escapovano:
                escapovano = False
            elif ch == "\\":
                escapovano = True
            elif ch == '"':
                v_ret = False
            continue
        if ch == '"':
            v_ret = True
        elif ch == "{":
            if hloubka == 0:
                zacatek = i
            hloubka += 1
        elif ch == "}":
            hloubka -= 1
            if hloubka == 0 and zacatek is not None:
                try:
                    out.append(json.loads(text[zacatek:i + 1]))
                except json.JSONDecodeError:
                    pass
                zacatek = None
    return out


def iso_cas(ms):
    import datetime
    return datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).strftime("%H:%M:%S")


def main() -> int:
    if len(sys.argv) < 2:
        print("pouziti: p41-c-tail-rozbor.py <doklad.txt> [--vystup <cesta>] [--json <vystup.json>]")
        return 2
    doklad = pathlib.Path(sys.argv[1])
    if not doklad.is_absolute():
        doklad = WS / doklad
    # VLASTNÍ jméno výstupu pro každý doklad (H191): pevné jméno by znamenalo,
    # že druhé okno přepíše doklad prvního.
    out = doklad.with_name(doklad.stem + "-rozbor.txt")
    if "--vystup" in sys.argv:
        out = pathlib.Path(sys.argv[sys.argv.index("--vystup") + 1])
        if not out.is_absolute():
            out = WS / out
    json_out = None
    if "--json" in sys.argv:
        json_out = pathlib.Path(sys.argv[sys.argv.index("--json") + 1])

    text = doklad.read_text(encoding="utf-8", errors="replace")
    eventy = objekty(text)

    zapis(f"# p41-c — rozbor živého tailu: {doklad.name}")
    zapis(f"# objektů v dokladu: {len(eventy)}")
    zapis()

    con = [e for e in eventy if e.get("scriptName") == "forge-conductor"]
    if not con:
        zapis("CHYBA: v dokladu není ANI JEDEN event conductora — měření neproběhlo.")
        out.write_text("\n".join(radky) + "\n", encoding="utf-8", newline="\n")
        return 1

    verze = sorted({(e.get("scriptVersion") or {}).get("id") for e in con})
    casy = [e.get("eventTimestamp") for e in con if e.get("eventTimestamp")]
    okno_min = (max(casy) - min(casy)) / 60000 if len(casy) > 1 else 0.0
    zapis(f"okno Z DOKLADU: {iso_cas(min(casy))} .. {iso_cas(max(casy))} = {okno_min:.1f} min"
          f" ({len(con)} eventů conductora z {len(eventy)} objektů)")
    zapis(f"scriptVersion.id: {', '.join(str(v) for v in verze)}"
          + ("  (JEDINÁ verze)" if len(verze) == 1 else "  ⚠ VÍC VERSION!"))
    zapis()

    zaznamy = []
    for e in con:
        ev = e.get("event") or {}
        cron = ev.get("cron")
        url = ((ev.get("request") or {}).get("url") or "")
        if cron:
            src = "cron"
        elif "/tick" in url:
            src = "manual" + ("+faze" if "faze=" in url else "")
        elif url:
            src = "http:" + url.split("/")[-1][:14]
        else:
            src = "?"
        prof = ""
        for lg in e.get("logs") or []:
            m = " ".join(str(x) for x in (lg.get("message") or []))
            if m.startswith("tick-prof:"):
                prof = m
        iso = ""
        faze = ""
        ceny = {}
        if prof:
            casti = prof.split()
            for c in casti:
                if c.startswith("iso="):
                    iso = c[4:]
                elif c.startswith("faze="):
                    faze = c[5:]
                elif "=" in c and c.split("=")[0] in (
                        "start", "zaklad", "poll", "watchdog", "stale", "hry",
                        "roadmap", "zombie", "dispatch"):
                    k, v = c.split("=", 1)
                    try:
                        ceny[k] = int(v)
                    except ValueError:
                        pass
        zaznamy.append({
            "cas": iso_cas(e.get("eventTimestamp") or 0),
            "ts": e.get("eventTimestamp") or 0,
            "src": src, "iso": iso, "faze": faze,
            "cpu": e.get("cpuTime"), "wall": e.get("wallTime"),
            "outcome": e.get("outcome"), "ceny": ceny,
        })

    # ── tabulka eventů ──────────────────────────────────────────────────────
    zapis("## Eventy v pořadí (cpu/wall z tailu; fáze z logu `tick-prof:`)")
    zapis(f"{'#':>3} {'cas':>8} {'zdroj':<16} {'iso':<9} {'faze':<18} {'cpu':>4} {'wall':>6}  faze ms")
    for i, r in enumerate(zaznamy, 1):
        ceny = " ".join(f"{k}={v}" for k, v in r["ceny"].items())
        zapis(f"{i:>3} {r['cas']:>8} {r['src']:<16} {r['iso']:<9} {r['faze']:<18}"
              f" {str(r['cpu']):>4} {str(r['wall']):>6}  {ceny}")
    zapis()

    # ── izoláty ─────────────────────────────────────────────────────────────
    zapis("## Izoláty (`iso=` je modulová konstanta → přežije jen v jednom izolátu)")
    podle_iso = {}
    for r in zaznamy:
        if r["iso"]:
            podle_iso.setdefault(r["iso"], []).append(r)
    for iso, rs in sorted(podle_iso.items(), key=lambda kv: kv[1][0]["ts"]):
        cpu = [x["cpu"] for x in rs if isinstance(x["cpu"], int)]
        zapis(f"  iso={iso:<9} eventů={len(rs):>2}  první={rs[0]['cas']} ({rs[0]['src']})"
              f"  cpu první={rs[0]['cpu']}  cpu medián={statistics.median(cpu) if cpu else '-'}"
              f"  cpu rozsah={min(cpu) if cpu else '-'}–{max(cpu) if cpu else '-'}")
        for x in rs:
            zapis(f"      {x['cas']} {x['src']:<18} faze={x['faze']:<18} cpu={x['cpu']} wall={x['wall']}")
    zapis()

    # ── agregace cron vs manual ─────────────────────────────────────────────
    def stat(pred, nazev):
        cpu = [r["cpu"] for r in zaznamy if pred(r) and isinstance(r["cpu"], int)]
        wall = [r["wall"] for r in zaznamy if pred(r) and isinstance(r["wall"], int)]
        if not cpu:
            zapis(f"  {nazev:<28} n=0  ⚠ NEMĚŘENO")
            return None
        zapis(f"  {nazev:<28} n={len(cpu):<3} cpu min/med/max = {min(cpu)}/{statistics.median(cpu)}/{max(cpu)}"
              f"   wall min/med/max = {min(wall)}/{statistics.median(wall)}/{max(wall)}")
        return {"n": len(cpu), "cpu_min": min(cpu), "cpu_med": statistics.median(cpu), "cpu_max": max(cpu)}

    zapis("## Agregace")
    cron_stat = stat(lambda r: r["src"] == "cron", "cron (čerstvý izolát)")
    man_stat = stat(lambda r: r["src"].startswith("manual"), "ruční /tick (teplý izolát?)")
    neok = [r for r in zaznamy if r["outcome"] != "ok"]
    zapis(f"  outcome ne-`ok`: {len(neok)}"
          + ("" if not neok else " → " + ", ".join(f"{r['cas']} {r['src']} {r['outcome']}" for r in neok)))
    zapis()

    # ── cena fází: rozdíl cpuTime mezi faze=N a faze=N+1 v TÉMŽ izolátu ────
    zapis("## Cena fáze z ROZDÍLU `cpuTime` mezi `?faze=N` a `?faze=N+1` (jen TÝŽ izolát)")
    for iso, rs in sorted(podle_iso.items(), key=lambda kv: kv[1][0]["ts"]):
        podle_f = {r["faze"]: r for r in rs if r["src"].startswith("manual") and r["faze"].startswith("stop-po-")}
        if len(podle_f) < 2:
            continue
        zapis(f"  iso={iso}:")
        for f in range(0, 9):
            r = podle_f.get(f"stop-po-{['start', 'zaklad', 'poll', 'watchdog', 'stale', 'hry', 'roadmap', 'zombie', 'dispatch'][f]}")
            if r:
                zapis(f"      faze={f} cpu={r['cpu']} wall={r['wall']}  {r['faze']}")
    zapis()

    # ── wall time po fázích z PLNÝCH tiků ──────────────────────────────────
    zapis("## Wall time po fázích (plné tiky s `faze=celkem`)")
    plne = [r for r in zaznamy if r["faze"] == "celkem" and r["ceny"]]
    if not plne:
        zapis("  ⚠ ŽÁDNÝ plný tik s `faze=celkem` v dokladu — profil se nezalogoval.")
    for r in plne:
        soucet = sum(r["ceny"].values())
        zapis(f"  {r['cas']} {r['src']:<10} iso={r['iso']:<9} cpu={r['cpu']} wall={r['wall']}"
              f"  soucet fazi={soucet}  " + " ".join(f"{k}={v}" for k, v in r["ceny"].items()))
    zapis()

    out.write_text("\n".join(radky) + "\n", encoding="utf-8", newline="\n")
    print(f"\n[doklad: {out}]")

    if json_out:
        json_out.write_text(json.dumps({"okno_min": okno_min, "verze": verze,
                                        "cron": cron_stat, "manual": man_stat,
                                        "zaznamy": zaznamy}, ensure_ascii=False, indent=2),
                            encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
