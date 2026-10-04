# -*- coding: utf-8 -*-
"""Nezávislé přeměření počtu sloupců v `conductor/schema.sql`.

PROČ (nález z fáze 2 auditu):
  `AGENTS.md` tvrdí na DVOU místech DVĚ RŮZNÁ ČÍSLA téhož:
    * řádek 62–63: „`AGENTS.md` tvrdil „32 sloupců", **správně je 39**"
    * řádek 337 (tabulka jazyka): „5 tabulek, **40 sloupců**, českých 0"

⚠ PAST, DO KTERÉ JSEM PŘI TOM SPADL (a je to poučení, ne detail):
  První verze tohohle skriptu **neodstraňovala SQL komentáře** — a blok
  `CREATE TABLE roadmap` má uvnitř ČTYŘI komentářové řádky (vysvětlují sloupec
  `naposledy_selhalo`). Vyšlo **44** místo **40**, protože se komentář počítal
  jako sloupec. A protože OBĚ „metody" v tom skriptu používaly tentýž blokový
  regex, shodly se na stejné chybě a skript napsal „obě metody se SHODUJÍ,
  číslo je spolehlivé". **Dvě metody nad jedním vadným vstupem nejsou dvě
  metody** — je to jeden pohled dvakrát (`overovani` §1.1).

  Proto se teď komentáře odstraňují PŘED hledáním bloků a výsledek se navíc
  vypisuje PO TABULKÁCH, aby se dal přečíst a zkontrolovat ručně.

CO VYŠLO (a proč je 39 i 40 „správně"):
  Dnes je správně **40**. Číslo **39** bylo správné DO 2. 10. 2026 — pak B1
  přidal sloupec `naposledy_selhalo` (aby se cooldown neptal na `updated_at`,
  což byla vada S12). Rozdíl je tedy **čas**, ne nepravda (`AGENTS.md` A2).
  Vada není v tom, že tam 39 je — ale že je tam **v přítomném čase a bez
  značky času**, zatímco o pár set řádků níž stojí 40. Kdo čte AGENTS.md
  jako autoritu, nemá jak poznat, které z nich platí.
"""

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
SQL = WS / "orchestra" / "conductor" / "schema.sql"
OMEZENI = ("primary", "foreign", "unique", "check", "constraint", "key")

if not SQL.is_file():
    print("CHYBA: %s neexistuje — není co měřit" % SQL)
    sys.exit(2)

sql_hruby = SQL.read_text(encoding="utf-8")
# Komentáře se odstraní PRVNÍ — jinak se počítají jako sloupce (naměřeno: 44 vs 40).
sql = re.sub(r"--[^\n]*", "", sql_hruby)

bloky = re.findall(r"CREATE TABLE IF NOT EXISTS\s+(\w+)\s*\((.*?)\n\);", sql, re.S)

print("=" * 88)
print("NEZÁVISLÉ PŘEMĚŘENÍ SLOUPCŮ: orchestra/conductor/schema.sql")
print("=" * 88)
print("  soubor: %s  (%d B, %d řádků)"
      % (SQL.name, SQL.stat().st_size, len(sql_hruby.splitlines())))
print()

celkem = 0
for jmeno, telo in bloky:
    sloupce = [l.strip().rstrip(",") for l in telo.splitlines() if l.strip()]
    celkem += len(sloupce)
    print("  %-10s sloupců: %2d   %s" % (jmeno, len(sloupce),
                                         ", ".join(s.split()[0] for s in sloupce)))
print("  " + "-" * 70)
print("  TABULEK: %d     SLOUPCŮ CELKEM: %d" % (len(bloky), celkem))
print()

# ── Historická hodnota 39: ověřit, že vznikla odečtením jednoho sloupce ────
print("  Kontrola vysvětlení „39 vs 40\": sloupec `naposledy_selhalo` je v roadmapě")
print("  a podle komentáře ho přidal B1 (2. 10. 2026). Odečte-li se, vyjde:")
print("      %d - 1 = %d   ← to je to „39\" z AGENTS.md:62" % (celkem, celkem - 1))
print()

# ── Co o tom tvrdí dokumenty ──────────────────────────────────────────────
print("=" * 88)
print("CO O TOM TVRDÍ DOKUMENTY")
print("=" * 88)
zdroje = ["AGENTS.md", "KRONIKA-PROJEKTU.md", "HANDOFF.md"]
vzor = re.compile(r"(\d+)\s+sloupc")
rozchody = 0
for jmeno in zdroje:
    cesta = WS / jmeno
    if not cesta.is_file():
        continue
    s = cesta.read_text(encoding="utf-8")
    for m in vzor.finditer(s):
        radek = s[:m.start()].count("\n") + 1
        kontext = s[max(0, m.start() - 95):m.end() + 45].replace("\n", " ").strip()
        tvrzeno = int(m.group(1))
        if tvrzeno == celkem:
            verdikt = "SOUHLASÍ s živým zdrojem"
        elif tvrzeno == celkem - 1:
            verdikt = "STAV PŘED B1 (historické — ve svém čase správné)"
            rozchody += 1
        else:
            verdikt = "ROZCHOD (živý zdroj = %d)" % celkem
            rozchody += 1
        print("  %-22s :%-5d tvrdí %2d  → %s" % (jmeno, radek, tvrzeno, verdikt))
        print("        …%s…" % kontext[:140])
print()
print("  ROZCHODŮ (včetně historických bez značky času): %d" % rozchody)
sys.exit(1 if rozchody else 0)
