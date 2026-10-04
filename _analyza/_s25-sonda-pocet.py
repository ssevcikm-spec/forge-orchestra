# -*- coding: utf-8 -*-
"""SONDA 9 — volá `je_pocet()` a `je_citace()` VYŘÍZNUTÉ ZE ZDROJE nástroje.

Měří **týž kód**, který běží v bráně (`overovani` §10.5) — ne jeho opis.
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
zdroj = (WS / "_analyza" / "audit2b-cisla-proti-zdroji.py").read_text(encoding="utf-8")
print("  řádků zdroje: %d" % len(zdroj.splitlines()))
print("  'JINA_JEDNOTKA = ' na řádku: %d"
      % next(k for k, l in enumerate(zdroj.splitlines(), 1) if "JINA_JEDNOTKA = " in l))
print("  'def je_pocet' na řádku:     %d"
      % next(k for k, l in enumerate(zdroj.splitlines(), 1) if "def je_pocet" in l))

# Vyřízneme blok od `NENI_POCET = ` po konec `je_pocet` (před `# ── REGISTR`).
# ⚠ POZOR NA HRANICE VÝŘEZU — vlastní omyl sondy (2. 10. 2026): první verze
# začínala na `NENI_POCET = re.compile`, jenže to je odkaz **uvnitř komentáře
# o `je_citace`** (ř. 189), ne definice predikátu (ř. 192) — výřez pak
# neobsahoval `je_pocet` vůbec a `exec` tiše nedefinoval nic.
# Kotvou je proto JEDNOZNAČNÝ název funkce, ne jméno sdílené s komentářem.
i = zdroj.index("    JINA_JEDNOTKA = re.compile")
# Konec bloku: jednoznačná kotva ZA funkcí (`je_pocet` je poslední věc před
# návratem k datovým konstantám). Bere se text od `i` a hledá se v NĚM.
_zbytek = zdroj[i:]
j = i + _zbytek.index("    # ⚠ DATUM JE NEJSILNĚJŠÍ")
blok = zdroj[i:j]
blok = "\n".join(l[4:] if l.startswith("    ") else l for l in blok.splitlines())
# Odřízneme případný zbytek (main už tam není, ale pro jistotu)
ns = {"re": re}
try:
    exec(blok, ns)
except Exception as e:                                            # noqa: BLE001
    print("  CHYBA při exec: %s: %s" % (type(e).__name__, e))
    print("  --- prvních 1200 znaků bloku ---")
    print(blok[:1200])
    print("  --- posledních 400 znaků ---")
    print(blok[-400:])
    raise
je_pocet = ns["je_pocet"]
print("  funkce načteny: %s" % [k for k in ns if k.startswith("je_")])

# Text, na kterém se to rozchází — z reálného dokumentu
t = (WS / "AGENTS.md").read_text(encoding="utf-8")
print()
print("=" * 96)
print("  AGENTS.md — výskyty „N kontrol“ a co řekne `je_pocet`")
print("=" * 96)
for m in re.finditer(r"(\d+)\s+kontrol", t):
    r = t[:m.start()].count("\n") + 1
    v = je_pocet(t, m.end())
    print("  ř.%-5d tvrdí %-4s je_pocet=%-5s | %s"
          % (r, m.group(1), v, t[m.start():m.start() + 42].replace("\n", " ")))

print()
print("=" * 96)
print("  TOTÉŽ pro HANDOFF.md:583 (`dokumentů`)")
print("=" * 96)
h = (WS / "HANDOFF.md").read_text(encoding="utf-8")
for m in re.finditer(r"(\d+)\s+dokument", h):
    r = h[:m.start()].count("\n") + 1
    if r == 583:
        print("  ř.%d tvrdí %s je_pocet=%s" % (r, m.group(1), je_pocet(h, m.end())))
        print("  u: %r" % h[m.start():m.start() + 50])
