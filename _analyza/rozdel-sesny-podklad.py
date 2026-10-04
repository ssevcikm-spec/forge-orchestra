"""Rozdel seznam session na 'orchestra' a 'jine' podle nadpisu a prvni zpravy.

Vstup: _analyza/sesny-podklad.txt (UTF-16LE, protoze PowerShell redirect).
Cil: ne 'kolik session je orchestra', ale s jakym postupem to bylo zmereno.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ZAKLAD = Path(__file__).resolve().parents[1]
VSTUP = ZAKLAD / "_analyza" / "sesny-podklad.txt"

# Klicova slova. Kazde ma vlastni vyznam - slouzi k rozdeleni, ne k souctu.
ORCHESTRA = ("orchestra", "orchestr", "conductor", "forge", "granule", "agent.yml",
             "roadmapa", "uo-shadows", "handoff", "zadani", "brán", "brana")
HRA = ("uo-shadows", "hra", "godot", "hráč", "hrác", "shadow")
STANICE = ("ollama", "litellm", "router", "dsh", "harness", "skill", "obrazky",
           "model", "api klíč", "token")

def main() -> int:
    raw = VSTUP.read_bytes()
    text = None
    for enc in ("utf-16-le", "utf-8-sig", "cp1250"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        print("CHYBA: soubor nelze dekodovat zadnym z enc")
        return 2

    # Blok session zacina radkem s casovou znackou a konci prazdnym radkem.
    # Pozor: radek vypise jako '[SESSION ]' (mezera pred zavorkou) - poprve to
    # neslo a skript tiše nahlodil 'nalezeno 0'. Vzorec musi tu mezeru prijmout.
    bloky = re.split(r"\n\s*\n", text)
    sesny: list[tuple[str, str, str]] = []  # (cas, typ, naletany text)
    for b in bloky:
        m = re.search(r"^(\d{4}-\d{2}-\d{2} [\d:]+)\s+\[(SESSION|SUBAGENT)\s*\]", b, re.M)
        if not m:
            continue
        sesny.append((m.group(1), m.group(2), b))

    if not sesny:
        print("CHYBA: v souboru neni ani jeden blok session (nalezeno 0)")
        return 2

    real = [s for s in sesny if s[1] == "SESSION"]
    sub = [s for s in sesny if s[1] == "SUBAGENT"]

    # Klasifikace: hledame klicova slova v PRVNICH dvou radcich za hlavickou
    # (titulek + zacatek). Cely blok by hledal slovo 'hra' i v odpovedi agenta.
    def text_klasifikace(b: str) -> str:
        radky = [r for r in b.splitlines() if r.strip()]
        hlava = " ".join(radky[:5]).lower()
        if any(k in hlava for k in ("orchestra", "orchestr", "conductor", "forge-",
                                    "granule", "agent.yml", "roadmapa", "uo-shadows")):
            return "orchestra"
        if any(k in hlava for k in ("ollama", "litellm", "router", "harness",
                                    "obrazky", "skill", "dsh ", "provider")):
            return "stanice/DSH"
        return "jine"

    pocet = Counter(text_klasifikace(b) for _, _, b in real)
    print(f"Pouzity postup: '{VSTUP.name}', klicova slova v prvnich 5 radcich bloku")
    print(f"Bloku celkem {len(sesny)}  (SESSION {len(real)}, SUBAGENT {len(sub)})")
    print()
    for k, v in pocet.most_common():
        print(f"  {k:<14} {v:>3}")
    print()
    # Explicitne: prazdny seznam neni vysledek. Kdyby neco nesedlo, je to vysledek.
    if len(real) == 0:
        print("VAROVANI: 0 skutecnych session - rozdeleni neni platne")
        return 1
    for cas, _, b in sorted(real, reverse=True)[:12]:
        radky = [r.strip() for r in b.splitlines() if r.strip()]
        titulek = next((r for r in radky if r.startswith("titulek")), "?")
        print(f"  {cas}  {text_klasifikace(b):<12} {titulek[:90]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())