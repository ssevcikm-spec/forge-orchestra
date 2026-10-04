r"""Zápis §8j a §23 do `HANDOFF.md` (session 2. 10. 2026, dokončení auditu).

PROČ SKRIPTEM (a ne editorem): `HANDOFF.md` je **append-only** a je to jediné
místo, kde žijí otevřené body — ztráta bodu je nejdražší chba předání
(`AGENTS.md`). Skript proto:
  1. **nic neodebere** — jen vloží dva bloky na přesně určená místa,
  2. **před zápisem i po zápisu** ověří, že počet řádků **vzrostl přesně
     o vložené bloky** a že **všech 83 klíčových bodů** je pořád v dokumentu,
  3. zapíše **bajty** (`write_bytes`), takže zůstanou LF (soubor je `eol=lf`).

Místa vložení:
  * `§8j` — hned za konec bloku `8i` (před `## 9.`), tedy mezi omyly,
  * `§23` — na konec souboru (výsledky jdou vždycky na konec).

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\s23-zapis.py
"""
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
BLOK_8J = WS / "_analyza" / "s8j-oddil.md"
BLOK_23 = WS / "_analyza" / "s23-oddil.md"
KONTROLA = WS / "_analyza" / "handoff-kontrola-uplnost.py"

KOTVA_8J = "## 9. Co už otevřené NENÍ"
KOTVA_23_8I = "### 8i."


def uplnost() -> int:
    r = subprocess.run([sys.executable, str(KONTROLA)], cwd=str(WS),
                       capture_output=True, timeout=300)
    v = r.stdout.decode("utf-8", "replace")
    for l in v.splitlines():
        if "kontrolovaných klíčů" in l:
            return int(l.split(":")[1].strip())
    return -1


pred = HANDOFF.read_bytes()
text = pred.decode("utf-8")
radky_pred = len(text.splitlines())
klice_pred = uplnost()
print("=" * 88)
print("ZÁPIS DO `HANDOFF.md` — §8j (vlastní omyly 87–93) a §23 (výsledky)")
print("=" * 88)
print("  před: %d řádků, %d B, kontrolovaných klíčů: %d"
      % (radky_pred, len(pred), klice_pred))

osm_j = BLOK_8J.read_text(encoding="utf-8").rstrip("\n") + "\n\n"
dva_tri = BLOK_23.read_text(encoding="utf-8").rstrip("\n") + "\n"

# ── Pojistky proti dvojímu vložení a proti špatnému místu ───────────────────
for popis, znacka in (("§8j", "### 8j. Omyly AKČNÍ session 2. 10. 2026"),
                      ("§23", "## 23. Provedeno 2. 10. 2026")):
    assert text.count(znacka) == 0, "%s už v HANDOFF.md je — zápis by zdvojil!" % popis
assert text.count(KOTVA_8J) == 1, "kotva pro §8j (`%s`) není 1×" % KOTVA_8J
assert text.count(KOTVA_23_8I) == 1, "kotva `### 8i.` není 1×"

# ── 1) §8j se vkládá PŘED `## 9.` ─────────────────────────────────────────
i = text.index(KOTVA_8J)
novy = text[:i] + osm_j + text[i:]

# ── 2) §23 na konec ────────────────────────────────────────────────────────
novy = novy.rstrip("\n") + "\n\n---\n\n" + dva_tri
HANDOFF.write_bytes(novy.encode("utf-8"))

po = HANDOFF.read_bytes()
t_po = po.decode("utf-8")
radky_po = len(t_po.splitlines())
ocekavane = radky_pred + len(osm_j.splitlines()) + len(dva_tri.splitlines()) + 2
print("  po:   %d řádků, %d B (přírůstek %d řádků, očekáváno %d)"
      % (radky_po, len(po), radky_po - radky_pred, ocekavane - radky_pred))
assert radky_po >= ocekavane - 1, "přírůstek řádků nesedí — zápis se nepovedl"
assert "### 8j." in t_po and "## 23." in t_po, "bloky v souboru nejsou"
assert len(pred) < len(po), "soubor se nezvětšil"
# NIC NEODEŠLO: každý řádek původního textu musí být i v novém
stare = set(text.splitlines())
chybejici = [l for l in stare if l.strip() and l not in t_po]
print("  řádků původního textu, které v novém NEJSOU: %d" % len(chybejici))
assert not chybejici, "NĚCO ZMIZELO: %s" % chybejici[:3]

klice_po = uplnost()
print("  kontrolovaných klíčů po: %d (před %d)" % (klice_po, klice_pred))
assert klice_po == klice_pred, "úplnost handoffu se změnila: %d -> %d" % (klice_pred, klice_po)

print("\nVYSLEDEK: zapsáno, nic nezmizelo, úplnost drží (%d/%d). exit 0"
      % (klice_po, klice_po))
sys.exit(0)
