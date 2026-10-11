# -*- coding: utf-8 -*-
r"""P35 — ROZBOR ŽIVÉHO `wrangler tail` (cpuTime podle endpointu + zpráva tiku).

PROČ VLASTNÍ PARSER: tail se ukládá přes `cmd /c "… > soubor"` (H161: PowerShell
pipeline u wrangleru NEDODÁ data). Soubor ale není JSONL — wrangler do něj píše
**pretty-printed objekty za sebou**, takže `splitlines()` + `json.loads` na řádek
nefunguje. Tenhle skript je čte přes `JSONDecoder.raw_decode` (zvládne objekty
za sebou i s mezerami mezi nimi) a NIKDY netvrdí nic o tom, co nenašel:
když soubor nemá `cpuTime`, vypíše to jako NEMĚŘENO, ne jako nulu.

CO MĚŘÍ (a co z toho plyne):
  * `cpuTime` / `wallTime` / `outcome` u KAŽDÉ invokace — a seskupí je podle
    `event.request.url` (HTTP) nebo `event.cron` (plánovaný tik),
  * `scriptVersion.id` — pro křížovou kontrolu s verzí z logu nasazení (A1),
  * `logs[].message` — zprávu tiku a chybové řádky (např. „duplicate column
    name“, které P34 chtěla dělat JEN JEDNOU NA ISOLATE),
  * „kolik eventů mělo `exceededCpu`“ — to je původní vada (H156/H157).

Použití:
    python _analyza/p35-tail-rozbor.py _analyza/p35-tail-raw-vystup.txt
    python _analyza/p35-tail-rozbor.py <soubor> --json <vystup.json>
Exit 0 = parser proběhl (i když jsou to špatné zprávy o službě); exit 1 = soubor
chybí / se nedá přečíst (měření neproběhlo — to se NESMÍ tvářit jako nula).
"""

import argparse
import json
import pathlib
import statistics
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def nacti(path):
    """Přečte concatenated JSON objekty (wrangler je píše pretty-printed)."""
    text = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    dec = json.JSONDecoder()
    i = 0
    eventy = []
    while i < len(text):
        while i < len(text) and text[i] in " \r\n\t":
            i += 1
        if i >= len(text):
            break
        try:
            obj, i = dec.raw_decode(text, i)
        except ValueError:
            # Poškozený/nekompletní objekt (tail se mohl ukončit uprostřed) —
            # zbytek se zahodí a POČET se vypíše, aby to nebylo tiché.
            return eventy, len(text) - i
        eventy.append(obj)
    return eventy, 0


def popis_logu(e):
    """Zprávy z logu jako jeden text (a seznam chybových)."""
    zpravy = []
    chyby = []
    for l in e.get("logs") or []:
        m = l.get("message")
        text = " ".join(str(x) for x in (m if isinstance(m, list) else [m])) if m is not None else ""
        if not text:
            continue
        zpravy.append(text)
        if "duplicate column" in text or "selhal" in text or "Error" in text:
            chyby.append(text)
    return zpravy, chyby


def klic(e):
    ev = e.get("event") or {}
    if ev.get("cron") is not None:
        return "cron(" + str(ev.get("cron")) + ")"
    req = ev.get("request") or {}
    url = str(req.get("url") or req.get("path") or "?")
    # Cesta stačí (host je pořád týž) — a vejde se do sloupce tabulky.
    if "://" in url:
        url = url.split("://", 1)[1]
        url = url[url.find("/"):] if "/" in url else "/"
    return str(req.get("method") or "GET") + " " + url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tail")
    ap.add_argument("--json", default=None, help="kam uložit rozbor jako JSON")
    args = ap.parse_args()

    p = pathlib.Path(args.tail)
    if not p.is_file():
        print("CHYBA: tail soubor %s NEEXISTUJE — měření neproběhlo (není to nula)" % p)
        return 1
    eventy, zbytek = nacti(p)
    if not eventy:
        print("CHYBA: v %s není ani jeden JSON objekt — měření neproběhlo" % p)
        return 1

    print("=" * 96)
    print("P35 — ROZBOR ŽIVÉHO TAILU: %s (%d B)" % (p.name, p.stat().st_size))
    print("=" * 96)
    if zbytek:
        print("  ⚠ na konci zůstalo %d znaků nedokončeného objektu (tail ukončen uprostřed)" % zbytek)

    verze = {}
    podle = {}
    cron_cpu = []
    ex_cpu = 0
    for e in eventy:
        v = (e.get("scriptVersion") or {}).get("id")
        if v:
            verze[v] = verze.get(v, 0) + 1
        k = klic(e)
        cpu = e.get("cpuTime")
        wall = e.get("wallTime")
        d = podle.setdefault(k, {"n": 0, "cpu": [], "wall": [], "outcome": {}})
        d["n"] += 1
        if isinstance(cpu, (int, float)):
            d["cpu"].append(cpu)
        if isinstance(wall, (int, float)):
            d["wall"].append(wall)
        o = str(e.get("outcome"))
        d["outcome"][o] = d["outcome"].get(o, 0) + 1
        if o == "exceededCpu":
            ex_cpu += 1
        if k.startswith("cron(") and isinstance(cpu, (int, float)):
            cron_cpu.append(cpu)

    print("\n## VERZE SKRIPTU V ŽIVÝCH EVENTECH (křížová kontrola s logem nasazení)")
    for v, n in sorted(verze.items(), key=lambda kv: -kv[1]):
        print("  %-40s %d eventů" % (v, n))
    if not verze:
        print("  NEZMĚŘENO: ani jeden event neměl `scriptVersion.id`")

    print("\n## CPU PODLE ENDPOINTU / TIKU")
    print("  %-46s %4s %8s %8s %8s  %s" % ("endpoint", "n", "cpu min", "cpu med", "cpu max", "outcome"))
    for k in sorted(podle):
        d = podle[k]
        c = d["cpu"]
        med = statistics.median(c) if c else None
        print("  %-46s %4d %8s %8s %8s  %s" % (
            k[:46], d["n"],
            min(c) if c else "—", med if med is not None else "—", max(c) if c else "—",
            ",".join("%s:%d" % kv for kv in sorted(d["outcome"].items()))))
    if not podle:
        print("  NEZMĚŘENO: žádné eventy")

    print("\n## ZPRÁVA TIKU (poslední cron event)")
    crony = [e for e in eventy if ((e.get("event") or {}).get("cron") is not None)]
    if crony:
        zpravy, chyby = popis_logu(crony[-1])
        for z in zpravy:
            print("  · " + z[:300])
        if chyby:
            print("  ⚠ chybové řádky v POSLEDNÍM cron eventu: %d" % len(chyby))
        else:
            print("  (v posledním cron eventu nejsou chybové řádky)")
    else:
        print("  NEZMĚŘENO: v tailu není ani jeden cron event")

    print("\n## SOUHRN")
    print("  invokací celkem: %d · z toho s outcome=exceededCpu: %d" % (len(eventy), ex_cpu))
    if cron_cpu:
        print("  cron cpuTime: min=%s med=%s max=%s (n=%d)"
              % (min(cron_cpu), statistics.median(cron_cpu), max(cron_cpu), len(cron_cpu)))
    else:
        print("  cron cpuTime: NEZMĚŘENO")

    if args.json:
        pathlib.Path(args.json).write_text(json.dumps({
            "soubor": str(p), "eventu": len(eventy),
            "verze": verze,
            "podle": {k: {"n": v["n"], "cpu": v["cpu"], "wall": v["wall"], "outcome": v["outcome"]}
                      for k, v in podle.items()},
            "exceededCpu": ex_cpu,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("\n  [json] %s" % args.json)
    print("=" * 96)
    return 0


if __name__ == "__main__":
    sys.exit(main())
