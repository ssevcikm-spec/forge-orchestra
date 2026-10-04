# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
r"""Ověření, že v HANDOFF.md/AGENTS.md nic nezmizelo kvůli souběhu dvou session.

Metoda: z logů obou session vytáhni KAŽDOU verzi obsahu, kterou zapsaly
(u `write` celý obsah, u `edit` `new_string`), a hledej KLÍČOVÉ BODY
z dřívějších handoffů. Když je bod v některé zapsané verzi a v POSLEDNÍ
verzi souboru chybí, je to důkaz ztráty.

Spuštění: $env:PYTHONIOENCODING='utf-8'; python _analyza\hl2-nic-nezmizelo.py
"""
import json
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(_STANICE)

# Klíčové body, které MUSÍ v handoffu zůstat (z 1. i 2. kola)
BODY = [
    "O3", "O5", "O6", "O7", "O8", "O10", "N0.2", "N0.3", "N5", "N6", "N8",
    "N10", "N11", "N12", "Z8", "Z9", "LGTM", "pc-domaci", "sprites.json",
    "main.json", "FORGE_CMD", "kontaktni-arch", "B1", "B2", "B3", "B4", "B5",
    "C2", "C3", "C4", "C5", "D2", "D3", "D4", "D5", "G0", "G5", "R15",
    "ohlášeno", "cíl mrtev", "vezmiPrepínac", "IMPLEMENTACE-HRANICE-JAZYKA",
    "hl-neanglicky-v-kodu", "test-neanglicky-skener", "2 014", "S31", "S37",
    "IMPLEMENTACE-UKOTVENI", "MAX_ATTEMPTS", "migrace-schema.py",
    "verify-setup.py", "sjednot-sablonu.py", "styl.zmenšování",
    "validate-all.mjs", "install-into-repo", "ASSETY",
]


def zapisane_verze(log: pathlib.Path, cil: str):
    """Vrátí [(cas, session, nazev, obsah)] pro zápisy daného souboru."""
    out = []
    sid = log.stem.replace("tmp-session-", "")
    for l in log.read_text(encoding="utf-8", errors="replace").split("\n"):
        if not l.strip():
            continue
        try:
            o = json.loads(l)
        except Exception:
            continue
        if o.get("type") != "tool/call":
            continue
        d = o.get("data") or {}
        nazev = d.get("name") or d.get("tool")
        if nazev not in ("write", "edit"):
            continue
        a = d.get("arguments") or d.get("input") or {}
        if isinstance(a, str):
            try:
                a = json.loads(a)
            except Exception:
                continue
        if not isinstance(a, dict):
            continue
        cesta = str(a.get("file_path") or a.get("path") or "")
        if cil not in cesta.replace("\\", "/"):
            continue
        obsah = a.get("content") or a.get("new_string") or ""
        out.append((d.get("time") or o.get("time") or 0, sid, nazev, obsah))
    return out


for cil in ("HANDOFF.md", "AGENTS.md"):
    soubor = WS / cil
    if not soubor.exists():
        print(f"CHYBI {soubor}")
        continue
    nyni = soubor.read_text(encoding="utf-8", errors="replace")

    print(f"=== {cil} ===")
    print(f"  nyni: {len(nyni)} znaku")

    # Posbírej všechny zapsané obsahy z obou session
    logy = sorted((WS / "_analyza").glob("tmp-session-*.jsonl"))
    vsechny = []
    for lg in logy:
        vsechny += zapisane_verze(lg, cil)
    vsechny.sort()
    print(f"  zapisu v logach: {len(vsechny)}")

    # Které body byly NĚKDY zapsány a teď chybí?
    chybi = []
    for bod in BODY:
        bylo = any(bod in obs for _, _, _, obs in vsechny)
        je = bod in nyni
        if bylo and not je:
            chybi.append(bod)
    if chybi:
        print(f"  !! BODY ZAPSANE A NYNI CHYBEJICI: {chybi}")
    else:
        print("  OK — zadny bod, ktery byl zapsan, ted nechybi")

    # Kolik bodu vubec je
    pritomno = [b for b in BODY if b in nyni]
    print(f"  klicovych bodu pritomno: {len(pritomno)}/{len(BODY)}")
    if len(pritomno) < len(BODY):
        print(f"    chybi: {[b for b in BODY if b not in nyni]}")
    print()

print("Pozn.: 'bylo zapsano' = objevilo se v nekterem write/edit te session.")
print("       Kdyz bod nikdy zapsan nebyl, nemuze chybet vinou soubehu.")
