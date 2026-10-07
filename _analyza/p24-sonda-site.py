# -*- coding: utf-8 -*-
r"""P24 — SONDA: umí Python na téhle stanici sáhnout na síť (GitHub API + živá služba)?

PROČ: zadání P24 §2.1 žádá **vlastní měřidlo** (`_analyza/p24-*`). Než se podle
něj začne stavět, musí být změřeno, jestli jde měřit **jedním skriptem** — nebo
jestli se síť musí rozdělit do Node (`dsh-prostredi` §5: „TLS z PowerShellu
nefunguje → na síť jdi Node fetch"). Sonda odpovídá měřením, ne odhadem.

Nic nezapisuje, jen vypisuje. Použití: python _analyza/p24-sonda-site.py
"""

import json
import pathlib
import sys
import urllib.error
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]


def env_soubor(p):
    out = {}
    try:
        for radek in p.read_text(encoding="utf-8-sig").splitlines():
            radek = radek.strip()
            if not radek or radek.startswith("#") or "=" not in radek:
                continue
            k, v = radek.split("=", 1)
            out[k.strip()] = v.strip()
    except OSError as e:
        print("  CHYBA čtení %s: %s" % (p, e))
    return out


def zkus(popis, url, hlavicky=None, timeout=25):
    req = urllib.request.Request(url, headers=hlavicky or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            telo = r.read()
            print("  OK   %-34s HTTP %s  %d B" % (popis, r.status, len(telo)))
            return r.status, telo
    except urllib.error.HTTPError as e:
        print("  HTTP %-30s %s  %s" % (popis, e.code, e.read()[:120]))
        return e.code, b""
    except Exception as e:                                   # noqa: BLE001
        print("  PAD  %-34s %s: %s" % (popis, type(e).__name__, e))
        return None, b""


print("=" * 78)
print("P24 — SONDA: síť z Pythonu")
print("=" * 78)

env = env_soubor(WS / ".env")
url = env.get("FORGE_URL", "")
print("FORGE_URL: %s" % (url or "(v .env není)"))
print()

print("1) GitHub API (PAT ze souboru, nikdy se nevypisuje):")
pat_cesta = WS / ".secrets" / "github_pat.txt"
pat = ""
try:
    pat = pat_cesta.read_text(encoding="utf-8").strip()
    print("   PAT načten: %d znaků" % len(pat))
except OSError as e:
    print("   CHYBA: PAT nejde přečíst: %s" % e)

H = {"Authorization": "Bearer %s" % pat,
     "Accept": "application/vnd.github+json",
     "User-Agent": "forge-p24-sonda"}
kod, telo = zkus("deploy.yml runs",
                 "https://api.github.com/repos/ssevcikm-spec/forge-orchestra"
                 "/actions/workflows/deploy.yml/runs?per_page=3", H)
if kod == 200 and telo:
    d = json.loads(telo)
    for r in d.get("workflow_runs", []):
        print("     #%s %s/%s head=%s" % (r["run_number"], r["status"],
                                          r.get("conclusion"), r["head_sha"][:7]))

print()
print("2) Živá služba conductora:")
# ⚠ Cloudflare vrací `error code: 1010` (HTTP 403) na `Python-urllib/3.x` —
# to je BLOKACE PODLE User-Agenta, ne vada služby ani sítě. Node `fetch` má
# vlastní UA, proto v Node cestě nikdy nevyskočila. Sonda to měří OBĚMA cestami,
# aby se „403“ nepletlo s „nedostupné“.
if url:
    zkus("GET /health (bez UA)", url.rstrip("/") + "/health")
    zkus("GET /health (s UA prohlížeče)", url.rstrip("/") + "/health",
         {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) forge-p24"})

print()
print("SONDA HOTOVA — výše je naměřeno, co kterou cestou jde.")
