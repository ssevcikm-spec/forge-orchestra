# P28 — SONDA (jednorázová): KTERÉ CESTY BRÁNA `over-skilly.py` NEVIDÍ?
#
# PROČ: §51.3 tvrdí, že brána měří JEN tvar `` `tools\...` `` / `` `_analyza\...` ``
# (backtick + cesta HNED na začátku), a že „0 mrtvých cest“ proto NENÍ důkaz.
# Tenhle skript to měří: porovná, co najde VZOR BRÁNY a co najde ŠIROKÝ vzor
# (cesta kdekoliv na řádku — v backticích, v code fence, za `python `, s `.\`),
# a u každého nálezu řekne, jestli cesta na disku existuje.
#
# ⚠ JE TO JEDNORÁZOVÁ DIAGNOSTIKA (odpovídá na jednu otázku) — patří do
# `PRESKOCIT` dávky `p20-d-doklady.py`. Měří SE ROZSAH, ne výsledek brány.
#
# Použití: python _analyza/p28-sonda-cesty.py
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = pathlib.Path(r"E:\Workspaces\forge-orchestra")
DSH = pathlib.Path(r"C:\Users\Ssevc\.dsh")

SOUBORY = []
for d in sorted((DSH / "skills").iterdir()):
    if d.is_dir() and (d / "SKILL.md").is_file():
        SOUBORY.append(d / "SKILL.md")
SOUBORY += [REPO / "PROVOZ-ORCHESTRA.md", REPO.parent / "uo-shadows" / "docs" / "BRANY-HRY.md"]

VZOR_BRANY = re.compile(r"`((?:_analyza|tools)[\\/][^\s`\"']+)`")
# ŠIROKÝ vzor: cesta začínající `_analyza`/`tools` kdekoliv (i za `python `, v ``` bloku)
VZOR_SIROKY = re.compile(r"(?<![\w\\./-])((?:_analyza|tools)[\\/][A-Za-z0-9_\-\\/.]+)")

KORENY = [REPO, REPO.parent / "uo-shadows"]
KORENY += [d for d in sorted(REPO.parent.iterdir())
           if d.is_dir() and (d / ".git").exists() and d not in KORENY]


def existuje(cesta):
    for k in KORENY:
        if (k / cesta).exists():
            return k.name
    return None


souhrn = []
for p in SOUBORY:
    if not p.is_file():
        print("  CHYBI: %s" % p)
        continue
    text = p.read_text(encoding="utf-8", errors="replace")
    videno = {m.group(1).rstrip(".,;:)") for m in VZOR_BRANY.finditer(text)}
    vse = {m.group(1).rstrip(".,;:)") for m in VZOR_SIROKY.finditer(text)}
    nevidene = sorted(vse - videno)
    mrtve_nevidene = [c for c in nevidene if not existuje(c)]
    mrtve_videne = [c for c in sorted(videno) if not existuje(c)]
    souhrn.append((p.name, len(videno), len(vse), len(nevidene), len(mrtve_nevidene),
                   len(mrtve_videne)))
    if nevidene:
        print("\n%s" % p.name)
        print("   vidí brána: %d   široký vzor: %d   NEVIDÍ: %d   z toho MRTVÝCH: %d"
              % (len(videno), len(vse), len(nevidene), len(mrtve_nevidene)))
        for c in nevidene[:14]:
            kam = existuje(c)
            print("      %-58s %s" % (c, ("→ " + kam) if kam else "!! NEEXISTUJE"))
        if len(nevidene) > 14:
            print("      … a dalších %d" % (len(nevidene) - 14))

print("\n" + "=" * 78)
print("SOUHRN: soubor | vidí brána | široký vzor | nevidí | z toho mrtvých | mrtvých viděných")
for jm, a, b, c, d, e in souhrn:
    print("  %-28s %4d %4d %4d %4d %4d" % (jm, a, b, c, d, e))
print("=" * 78)
print("CELKEM: brána vidí %d zmínek, široký vzor %d, NEVIDÍ %d (z toho mrtvých %d)"
      % (sum(x[1] for x in souhrn), sum(x[2] for x in souhrn),
         sum(x[3] for x in souhrn), sum(x[4] for x in souhrn)))
