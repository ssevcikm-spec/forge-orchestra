# -*- coding: utf-8 -*-
r"""OPRAVA MĚŘIDLA: `f3-over-deploy.mjs` kontrolovalo deploy na HEADu `main`,
ale `deploy.yml` má filtr `paths: conductor/**`.

NAMĚŘENO 2. 10. 2026 (po pushi obou repů):
    GitHub main = 1e3925e2c  (kontrola diakritiky: doplnit dalsich 14 souboru)
    CHYBA GitHub main = očekávaný commit  — 1e3925e2c vs 7c11b2d
    CHYBA deploy běžel na tomto commitu  — na 1e3925e2c žádný deploy

**Obě hlášky jsou falešné poplachy na SPRÁVNÉM stavu:** commit `1e3925e` mění
jen `tools/kontrola-diakritiky.py`, takže deploy **správně neběžel** — a
nasazený kód conductora je `7c11b2d` (deploy #32), což je pořád pravda.

**Správné kritérium** (a tak to dělá `a3-kontrola.mjs:43–52`): ptát se na
**poslední změnu `conductor/**`**, ne na HEAD `main`. Když je na ní úspěšný
deploy, kód conductora z `main` JE nasazený — ať je HEAD kde chce.

Použití:  python _analyza\s19f-oprav-deploy.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
SOUBOR = WS / "_analyza" / "f3-over-deploy.mjs"
ZAPIS = "--zapis" in sys.argv

t = SOUBOR.read_text(encoding="utf-8")

# ── 1) nahradit kontrolu „main == očekávaný commit" za „HEAD je na main" ────
STARE1 = """if (cekanyNorm) test('GitHub main = očekávaný commit', shaMain?.toLowerCase().startsWith(cekanyNorm), `${shaMain?.slice(0, 9)} vs ${cekany}`);"""
NOVE1 = """// POZOR (opraveno 2. 10. 2026): `cekany` NENÍ „aktuální HEAD main" — je to
// **commit, na kterém má běžet deploy**, tedy poslední změna `conductor/**`.
// Původní verze porovnávala `cekany` s HEADem main, a když pozdější push změnil
// jen `tools/`, hlásila `CHYBA GitHub main = očekávaný commit` — **falešný
// poplach na správném stavu** (naměřeno: `1e3925e2c vs 7c11b2d`).
// Nově se ptáme na **poslední změnu conductor/**, stejně jako `a3-kontrola.mjs`.
const zmenaConductoru = await gh(`/repos/${REPO}/commits?path=conductor/src/index.ts&per_page=1`);
const shaConductoru = zmenaConductoru[0]?.sha;
console.log(`  poslední změna conductor/src/index.ts = ${shaConductoru?.slice(0, 9)}`);
// `messageHead` se používá níž v hlášce; drží se, aby výpis zůstal čitelný.
const messageHead = hlavni.commit?.message?.split('\\n')[0];
void messageHead;"""

# ── 2) nahradit kontrolu „deploy běžel na HEADu main" za „na poslední změně conductor/" ──
STARE2 = """const naCommitu = nas.find((r) => r.head_sha === shaMain);
if (naCommitu) {
  test('deploy běžel na TOMTO commitu', true, `#${naCommitu.run_number}`);
  test('deploy skončil success', naCommitu.conclusion === 'success',
    `#${naCommitu.run_number} ${naCommitu.conclusion}`);
} else {
  test('deploy běžel na tomto commitu', false,
    `na ${shaMain?.slice(0, 9)} žádný deploy — push nezměnil conductor/**?`);
}"""
NOVE2 = """// Hledá se deploy na **poslední změně conductor/** — ne na HEADu main.
const naCommitu = nas.find((r) => r.head_sha === shaConductoru);
test('kód conductora z main JE nasazený (deploy na poslední změně conductor/)',
  !!naCommitu && naCommitu.conclusion === 'success',
  naCommitu ? `#${naCommitu.run_number} success head:${naCommitu.head_sha.slice(0, 9)}`
            : `na ${shaConductoru?.slice(0, 9)} žádný deploy`);
// A když uživatel zadal konkrétní sha, ověří se, že na NĚM deploy opravdu byl
// (to je původní smysl parametru — „B1 musí být nasazené").
if (cekanyNorm) {
  const naZadanem = nas.find((r) => r.head_sha.toLowerCase().startsWith(cekanyNorm));
  test(`deploy běžel na zadaném commitu ${cekany.slice(0, 9)}`,
    !!naZadanem && naZadanem.conclusion === 'success',
    naZadanem ? `#${naZadanem.run_number} ${naZadanem.conclusion}` : 'žádný deploy na tom commitu');
}"""

print("=" * 78)
print("OPRAVA MĚŘIDLA f3-over-deploy.mjs — deploy se ptá na conductor/, ne na HEAD")
print("=" * 78)
for i, (stary, novy) in enumerate(((STARE1, NOVE1), (STARE2, NOVE2)), 1):
    pocet = t.count(stary)
    print("  %d) kotva %dx (očekáváno 1)" % (i, pocet))
    if pocet != 1:
        print("     → CHYBA: kotvu nejde nahradit jednoznačně")
        sys.exit(1)

novy_text = t.replace(STARE1, NOVE1, 1).replace(STARE2, NOVE2, 1)
assert novy_text != t, "MUTACE NEPROBĚHLA"
assert "shaConductoru" in novy_text, "nová proměnná se nevepsala"
assert "deploy běžel na tomto commitu" not in novy_text, "stará kontrola tam zůstala"
# POJISTKA proti rekurzi: `shaMain` se už NESMÍ použít pro rozhodnutí o deployi.
assert "r.head_sha === shaMain" not in novy_text, "staré kritérium tam zůstalo"

if ZAPIS:
    SOUBOR.write_bytes(novy_text.encode("utf-8"))
    print()
    print("  ZAPSÁNO: %d -> %d B"
          % (len(t.encode("utf-8")), len(novy_text.encode("utf-8"))))
else:
    print()
    print("  (dry-run — spusť s --zapis)")
