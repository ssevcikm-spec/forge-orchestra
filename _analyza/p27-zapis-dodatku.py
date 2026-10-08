# -*- coding: utf-8 -*-
r"""P27 (dodatek) — HANDOFF §58 + KRONIKA řádky P27-T/U/V (rozhodnutí a nasazení).

Použití: python _analyza/p27-zapis-dodatku.py
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
H = WS / "HANDOFF.md"
K = WS / "KRONIKA-PROJEKTU.md"

kontrol = 0
chyb = []


def k(ok, popis):
    global kontrol
    kontrol += 1
    print("  %s  %s" % ("OK  " if ok else "CHYBA", popis))
    if not ok:
        chyb.append(popis)


ODDIL_58 = r"""## 58. P27 — DODATEK: ROZHODNUTÍ UŽIVATELE, NASAZENÍ STROPU A ROZSAH BRÁNY (8. 10. 2026)

**Co tenhle oddíl JE:** **dodatek k §57** — uživatel 8. 10. 2026 rozhodl o otevřených
otázkách, **strop granulí se ZAPNUL a NASAZIL** a opravil se **rozsah brány**
`over-skilly` (rozhodnutí **B5**, které uživatel delegoval na agenta).
**Co NENÍ:** stav před rozhodnutím (to je §57), historie (kronika — řádek **42**,
nálezy **§2.20**), plán (ten je `PLAN-ROZVOJ-ORCHESTRA.md` §6 a **§6.1**).

> **⚠ DATUM SPOTŘEBY:** měřeno a nasazeno **8. 10. 2026, ~14:30–15:30 +02:00**.
> Živá služba se od té doby může změnit — kdo to čte později, **přeměří**
> (`node _analyza\p27-over-nasazeni.mjs`).

### 58.1 Co se udělalo

| # | Co | Doklad |
|---|---|---|
| **B4** | **STROP NA GRANULI ZAPNUT na `"8"`** (byl `"0"` = vypnuto) a **NASAZEN** | `conductor/wrangler.toml` + push **`07169c7`** → Actions `deploy.yml` **#34 `completed/success`** na témž commitu; **živě:** `/health` `ok=true`, `/roadmap` 21 granul, **0 blokovaných** |
| **B5** | **ROZSAH BRÁNY `over-skilly`** — skilly jsou STANIČNÍ, takže cesta smí patřit jinému projektu | `tools/over-skilly.py` → **0 mrtvých cest** (3 cesty se našly v `game-clone` a vypisují se jako **poznámka**); mutační dvojče **8/0** |
| **—** | Mut. dvojče `test-over-skilly-delegovane.py` **odpojeno od cizích skillů** (přepis `FORGE_SKILLS`) | dřív padalo kvůli **cizímu** rozbitému skillu; dnes **8/0** |
| **O9** | Ověřeno, že oprava `NAZEV-REPA` **drží** (hotová už 1. 10. 2026) | šablona `repo/.github/workflows/release.yml`: **0×** `NAZEV-REPA`, **5×** `github.repository`; `termux-setup.sh` 2× **záměrně** (návod pro člověka) |
| **—** | **Rozhodnutí uživatele zapsána** do `PLAN-ROZVOJ-ORCHESTRA.md` §6 (+ nový **§6.1** = rozhodnutí B5 s důvodem) | `O5`, `O6`, `O10` = souhlas; `O7` odloženo s pravidlem; `O8` = celek, ale postupně; `O9` hotovo; `O3` zodpovězeno |

### 58.2 Nálezy P27 (dodatek — každý doložený měřením)

19. **CIZÍ SKILL MÁ NEPLATNÝ YAML — A SHODÍ NAŠE BRÁNY.** Během session vznikl
    (jinou session, **mtime 14:26**) skill `dialog-s-uzivatelem` s **neplatným
    frontmatterem** (neescapované uvozovky v `description`). `over-skilly` kvůli
    němu hlásí 1 chybu a `g3` má nedeklarovaný exit — **přitom s orchestrou ten
    soubor nemá nic společného**. **NEOPRAVOVAL jsem ho** (cizí rozdělaná práce);
    patří té session. Naměřeno: `Skillů: 14, chyb: 1`, `Cesty k nástrojům: 71
    zmínek, 0 mrtvých`.
20. **MUTAČNÍ TEST BYL SVÁZANÝ S CIZÍMI SKILLY.** `_analyza/test-over-skilly-delegovane.py`
    testuje část o **delegovaných dokumentech**, ale jeho „zdravá fixtura →
    exit 0" padalo kvůli cizímu rozbitému skillu (2 chyby). Opraveno přepisem
    **`FORGE_SKILLS`** (stejný vzor jako `FORGE_NAVAZANE`/`FORGE_KORENY`) → test
    měří **svou věc**: **8/0**.
21. **STROP GRANULÍ: PROČ PRÁVĚ 8.** Musí být **víc než `MAX_ATTEMPTS` (5)** —
    jinak jen opisuje pokusový strop a nic dalšího nebrzdí (granule s jedním
    úkolem spálí 5 běhů a stejně padne). `ESCALATE_AFTER` (3) musí zůstat **pod**
    ním. 8 = 3 (ohlášení) + 5 (jeden plný rozpočet) → druhá šance ano, třetí ne.
    **Mez acceptance:** že strop opravdu **zastaví**, se na živé službě projeví až
    u granule s **≥ 8 běhy** (stejná mez jako u B3/B4) — dnes je blokovaných **0**.

### 58.3 Stav po dodatku

```
orchestra: HEAD 07169c7 (PUSHNUTO, origin/main = HEAD)
hra:       HEAD bc51e46 (cizí session, nepushnuté) — P27 do hry nezapsala
živá služba: /health ok=true ready=1 running=0 games=1 · /roadmap 21 granul,
           0 blokovaných · strop granulí ZAPNUTÝ na 8 (deploy.yml #34 success)
brány (P27, poslední běh): test-tick-offline 205/0 · p27-a --plne 133/0 ·
           p27-b 27/0 · b3b-mutace 11/0 · tick-mutace 20 vrat / 41/0 ·
           over-skilly: 0 mrtvých cest, 1 CHYBA = CIZÍ skill (nález 19)
```

### 58.4 Co čeká na tebe

- **Cizí skill `dialog-s-uzivatelem`** — neplatný YAML; dokud ho ta session
  neopraví, bude `over-skilly` (a tím `g3`) červené. **Neopravoval jsem ho.**
- **B2 `.gitattributes`** — nerozhodnuto (`git checkout` nad `conductor/src/index.ts`
  ho přepíše na CRLF a rozbije vícřádkové kotvy mutací).
- **B5 slepé místo z `§51.3`** (brána měří jiný **tvar** cest, než dokumenty
  používají) — **zůstává otevřené**; dnešní oprava řešila jen **rozsah**.
- **O7** — až vznikne druhá hra, bere se jako **testovací** (free kvóta se sdílí).
"""

RADKY = r"""| **P27-T** | „Rozbitý skill mimo repo se nás netýká.“ | Během P27 vznikl (jinou session, **mtime 14:26**) skill `dialog-s-uzivatelem` s **neplatným YAML** frontmatterem (neescapované uvozovky v `description`) → `over-skilly` hlásí `Skillů: 14, chyb: 1` a `g3` má nedeklarovaný exit | **NEOPRAVOVÁNO** (cizí rozdělaná práce) — **zapsáno a nahlášeno**; patří té session. Není to vada orchestra: `Cesty k nástrojům: 71 zmínek, 0 mrtvých` |
| **P27-U** | „Mutační test měří svou věc.“ | `_analyza/test-over-skilly-delegovane.py` (test DELEGOVANÝCH dokumentů) padal na **cizím** rozbitém skillu: „zdravá fixtura → exit 0“ dalo `exit 1` | **OPRAVENO** přepisem **`FORGE_SKILLS`** (vzor `FORGE_NAVAZANE`/`FORGE_KORENY`) → **8/0**. Falešný poplach se hledá hůř než slepé místo |
| **P27-V** | „Strop granulí stačí zapnout na 5.“ | Musí být **víc než `MAX_ATTEMPTS` (5)**, jinak jen opisuje pokusový strop (granule s jedním úkolem spálí 5 běhů a stejně padne); `ESCALATE_AFTER` (3) musí zůstat pod ním | **ZAPNUTO NA 8** (3 + 5) a **NASAZENO** (`07169c7` → `deploy.yml` #34 `success`); ověřeno živě: `/health` ok, `/roadmap` 21 granul, **0 blokovaných**. **Mez acceptance:** zastavení se projeví až u granule s ≥ 8 běhy |
| **P27-W** | „Brána má měřit jen orchestra a hru.“ | **ROZHODNUTÍ B5 (agent, uživatel delegoval):** skilly jsou **STANIČNÍ** — cesta v nich smí patřit jinému projektu (naměřeno: skill `game-developer` odkazuje na `tools/plan-status.py` a `tools/roadmap-gen.py`, které žijí v sourozenci `game-clone`), a brána je hlásila jako **3 mrtvé cesty** (falešný poplach shazující `g3`) | **OPRAVENO:** cesta se uzná v orchestře, ve hře **nebo v sourozeneckém projektu** (`.git`); **skutečně mrtvá cesta bránu dál SHODÍ** a nález mimo orchestra/hru se **vypíše jako poznámka** (rozsah musí být vidět). Zapsáno v `PLAN-ROZVOJ-ORCHESTRA.md` **§6.1** |
"""

t = H.read_text(encoding="utf-8")
if "## 58. P27 — DODATEK" in t:
    k(True, "HANDOFF už §58 má")
else:
    H.write_bytes((t.rstrip("\n") + "\n\n" + ODDIL_58).encode("utf-8"))
    k(True, "HANDOFF: §58 vložen na konec")

t2 = K.read_text(encoding="utf-8")
if "| **P27-T** |" in t2:
    k(True, "kronika už řádky P27-T…W má")
else:
    import re
    m = re.search(r"^\| \*\*P27-S\*\* \|.*$", t2, re.M)
    if not m:
        k(False, "kotva P27-S v kronice nenalezena")
    else:
        t2 = t2[:m.end()] + "\n" + RADKY.strip("\n") + t2[m.end():]
        K.write_bytes(t2.encode("utf-8"))
        k(True, "kronika: řádky P27-T…W doplněny do §2.20")

# ── dodatek k řádku 42 (append, nic se nemaže) ─────────────────────────────
t2 = K.read_text(encoding="utf-8")
if "**Dodatek 8. 10.:**" not in t2:
    import re
    m = re.search(r"^\| \*\*42\*\* \|.*$", t2, re.M)
    if m:
        novy = (m.group(0)[:-1] +
                " **Dodatek 8. 10.:** strop granulí **ZAPNUT na 8** a **NASAZEN** "
                "(`deploy.yml` #34 `success`), **rozsah brány `over-skilly` opraven** "
                "(rozhodnutí **B5**), rozhodnutí **O5/O6/O8/O9/O10** zapsána a ověřena; "
                "`g3` zůstává červené kvůli **cizímu** skillu s neplatným YAML |")
        t2 = t2.replace(m.group(0), novy, 1)
        K.write_bytes(t2.encode("utf-8"))
        k(True, "kronika: řádek 42 má dodatek")
    else:
        k(False, "řádek 42 nenalezen")

t_h = H.read_text(encoding="utf-8")
t_k = K.read_text(encoding="utf-8")
k("## 58. P27 — DODATEK" in t_h, "HANDOFF má §58")
k("## 57. P27 —" in t_h and "## 56. P26 —" in t_h, "§56 i §57 zůstaly")
k("| **P27-W** |" in t_k, "kronika má P27-W")
k("| **P27-T** |" in t_k, "kronika má P27-T")
k("| **42** |" in t_k and "| **41** |" in t_k, "řádky 41 a 42 zůstaly")
k("| **celkem** | **27 bloků, 35 sessions** | **208** |" in t_k,
  "souhrn §3 zůstal NEPŘEPOČÍTÁN")
for p, popis in ((H, "HANDOFF"), (K, "KRONIKA")):
    b = p.read_bytes()
    k(b.count(b"\r\n") == 0 and not b.startswith(b"\xef\xbb\xbf"),
      "%s: LF a bez BOM" % popis)

print()
print("=" * 78)
print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
for c in chyb:
    print("  CHYBA: %s" % c)
sys.exit(1 if chyb else 0)
