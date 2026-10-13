# -*- coding: utf-8 -*-
"""K4 — zápis KLÍČE POSKYTOVATELE do SECRETU kteréhokoli repa hry (sealed box).

PROČ: GitHub hodnoty secretů NEVRACÍ, takže jediná cesta k zápisu je zašifrovat
je veřejným klíčem repa (`crypto_box_seal`). Hodnoty se NIKDY nevypisují —
jen jméno, stav a datum změny (datum změny je důkaz, že zápis proběhl).

Používá se, když uživatel zregeneruje klíč: klíč žije ve DVOU místech — ve
stanici (`.secrets/<nazev>_key.txt`, odkud ho bere `probe-provider.mjs`) a
v secretech HRY (odkud ho bere běh agenta). Vyměnit jen jedno z nich znamená,
že jedna strana mluví o jiném klíči než druhá.

Použití:
  .tmp\\otukani\\venv\\Scripts\\python.exe .tmp\\k4-secret-do-repa.py <repo> [jmeno ...]
Příklad:
  ... .tmp\\k4-secret-do-repa.py uo-shadows CEREBRAS_API_KEY
  (bez jmen zapíše všechny, které v .secrets/<...>_key.txt existují)
"""
import base64
import json
import pathlib
import sys
import urllib.error
import urllib.request

from nacl import encoding, public

ORCH = pathlib.Path(r"E:\Workspaces\forge-orchestra")
OWNER = "ssevcikm-spec"
PAT = (ORCH / ".secrets" / "github_pat.txt").read_text(encoding="utf-8").strip()

# Co se dá zapsat: jméno secretu -> soubor na stanici.
MAPOVANI = {
    "MISTRAL_API_KEY": "mistral_key.txt",
    "CEREBRAS_API_KEY": "cerebras_key.txt",
    "GROQ_API_KEY": "groq_key.txt",
    "OPENROUTER_API_KEY": "openrouter_key.txt",
}

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(2)
REPO = sys.argv[1]
chcene = sys.argv[2:] or list(MAPOVANI)


def api(cesta, metoda="GET", telo=None):
    data = json.dumps(telo).encode() if telo is not None else None
    req = urllib.request.Request(
        "https://api.github.com" + cesta, data=data, method=metoda,
        headers={"authorization": f"Bearer {PAT}", "accept": "application/vnd.github+json",
                 "user-agent": "forge-k4", "x-github-api-version": "2022-11-28",
                 **({"content-type": "application/json"} if data else {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, {"chyba": e.read().decode("utf-8", "replace")[:200]}


def vypis(paticka):
    stav, s = api(f"/repos/{OWNER}/{REPO}/actions/secrets")
    if stav != 200:
        print(f"  secrety nejdou přečíst ({stav}): {s}")
        return
    print(f"  {paticka}:")
    for x in sorted(s.get("secrets", []), key=lambda y: y["name"]):
        print(f"    {x['name']:<22} změněno {x['updated_at']}")


print(f"=== {OWNER}/{REPO} ===")
vypis("PŘED")

stav, klic = api(f"/repos/{OWNER}/{REPO}/actions/secrets/public-key")
if stav != 200:
    print(f"CHYBA: veřejný klíč repa nejde přečíst ({stav})")
    sys.exit(2)
box = public.SealedBox(public.PublicKey(klic["key"].encode(), encoding.Base64Encoder))

print()
for jmeno in chcene:
    soubor = ORCH / ".secrets" / MAPOVANI.get(jmeno, "")
    if not jmeno in MAPOVANI or not soubor.is_file():
        print(f"  {jmeno}: PŘESKOČENO — nevím, odkud vzít hodnotu ({soubor})")
        continue
    hodnota = soubor.read_text(encoding="utf-8").strip()
    if len(hodnota) < 20:
        print(f"  {jmeno}: PŘESKOČENO — hodnota je podezřele krátká ({len(hodnota)} znaků)")
        continue
    zasifrovane = base64.b64encode(box.encrypt(hodnota.encode())).decode()
    stav, odp = api(f"/repos/{OWNER}/{REPO}/actions/secrets/{jmeno}", "PUT",
                    {"encrypted_value": zasifrovane, "key_id": klic["key_id"]})
    print(f"  {jmeno}: PUT → {stav} {'(zapsáno)' if stav in (201, 204) else odp} (délka {len(hodnota)})")

print()
vypis("PO")
