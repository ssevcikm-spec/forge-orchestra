"""Brána watchdogu na GRANULI (B3a) — SQL i prah se ČTOU ZE ZDROJÁKU.

PROČ TENHLE TEST EXISTUJE
-------------------------
Naměřeno na ŽIVÉ službě 6. 10. 2026:
  * `entity.npc` spálil **8 pokusů** (5 v úkolu #228 + 3 v #234) a conductor ho
    vydával dál; `entity.enemy` **5**.
  * Watchdog se **nikdy nespustil**: počítal běhy JEDNOHO úkolu (`r.task_id = t.id`)
    a měl prah **8** > strop `MAX_ATTEMPTS=5` → nedosažitelný stav. Ověřeno:
    v `payload` žádné úlohy není `eskalovano`.
  * Fronta se plnila osiřelými duplikáty: **49 úloh** na tutéž granuli.

CO SE NEOPISUJE (a proč je to jinak než dřív)
--------------------------------------------
Starý `test-eskalace.py` měl `PRAH = 8` **natvrdo** a `watchdog()` byl **opis**
logiky — testoval tedy stav, který conductor nemůže vyrobit (`ANALYZA-ARCHITEKTURY`
ř. 500). Tahle brána **vytahuje ze zdrojáku**:
  1. `GRAIN_KEY_SQL` — klíč granule `{game}/{grain}` (skládá se na jednom místě),
  2. `SQL_GRANULE_RUNS` — počítadlo spálených běhů na granuli,
  3. SQL kandidátů z `escalateStuckTasks` (řádek `roadmap`, ještě neohlášený),
  4. výchozí prah z `env.ESCALATE_AFTER || "3"`,
a k tomu **konfiguraci** z `wrangler.toml` (`MAX_ATTEMPTS`, `ESCALATE_AFTER`).

Test má assert i nenulový exit kód. Když se SQL v conductoru změní, test použije
novou verzi — a když se změní tak, že přestane platit některý ze slibů, spadne.

CO TVRDÍ:
  A) počítadlo je NA GRANULI: dva úkoly jedné granule (5+3) → **8** (starý dotaz
     na jednom úkolu dá max 5 → dokumentovaná vada, „známý chybný případ"),
  B) běhy PŘED založením řádku se nepočítají → `roadmap-reset` je cesta zpět,
  C) granule bez řádku v roadmapě se nepočítá vůbec,
  D) ohlášená granule (`eskalovano`) se už nevrací mezi kandidáty → žádný spam,
  E) pod prahem se nehlásí nic,
  F) **prah je POD stropem** (v kódu i ve `wrangler.toml`) — prah nad stropem je
     prah, který nikdy nepřijde (přesně vada, která watchdog zabila),
  G) značka se ukládá do `roadmap` (ne do payloadu úkolu, který retry zahodí).
"""

import json
import os
import pathlib
import re
import sqlite3
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
CONDUCTOR = WS / "conductor" / "src" / "index.ts"
WRANGLER = WS / "conductor" / "wrangler.toml"

checks = 0
errors = 0


def check(desc: str, actual, expected) -> None:
    global checks, errors
    checks += 1
    if actual == expected:
        print(f"  OK    {desc}")
    else:
        errors += 1
        print(f"  CHYBA {desc}\n        cekano: {expected!r}\n        dáno:   {actual!r}")


def strip_comments(src: str) -> str:
    """Odstraní komentáře — kontrola musí číst KÓD, ne komentář, který vadu popisuje."""
    v = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    return re.sub(r"//[^\n]*", " ", v)


def extract_template(src: str, name: str) -> str:
    """Vytáhne obsah template literalu `const NAME = \\`...\\`;` (i víceřádkového)."""
    m = re.search(rf"const\s+{re.escape(name)}\s*=\s*`", src)
    if not m:
        raise SystemExit(f"CHYBA: `const {name} = ...` (template literal) ve zdroji není")
    start = m.end()
    end = src.index("`", start)
    text = src[start:end]
    # Nahrazení vložených konstant tím, co je opravdu ve zdroji. POZOR: u samotné
    # `GRAIN_KEY_SQL` se nahrazovat nesmí — rekurze by se zavolala sama na sebe
    # (naměřeno 6. 10. 2026: `RecursionError` z prvního běhu téhle brány).
    if name != "GRAIN_KEY_SQL" and "${GRAIN_KEY_SQL}" in text:
        text = re.sub(r"\$\{GRAIN_KEY_SQL\}", extract_template(src, "GRAIN_KEY_SQL"), text)
    return text


def extract_candidate_sql(src: str) -> str:
    """Vytáhne SQL kandidátů z `escalateStuckTasks` (SELECT ... FROM roadmap ...)."""
    body = src[src.index("async function escalateStuckTasks"):]
    for m in re.finditer(r"`([^`]*)`", body, flags=re.S):
        if "FROM roadmap" in m.group(1):
            return m.group(1)
    raise SystemExit("CHYBA: SQL kandidátů (`FROM roadmap`) v escalateStuckTasks není")


def extract_default_threshold(src: str) -> int:
    m = re.search(r'env\.ESCALATE_AFTER\s*\|\|\s*"(\d+)"', src)
    if not m:
        raise SystemExit("CHYBA: výchozí prah `env.ESCALATE_AFTER || \"N\"` ve zdroji není")
    return int(m.group(1))


def extract_function(src: str, name: str) -> str:
    """Vytáhne CELÝ text funkce ze zdrojáku (po vyvážené závorce)."""
    m = re.search(rf"function\s+{re.escape(name)}\s*\(", src)
    if not m:
        raise SystemExit(f"CHYBA: funkce `{name}` ve zdroji není")
    start = src.index("{", m.end() - 1)
    depth = 0
    for i in range(start, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[m.start():i + 1]
    raise SystemExit(f"CHYBA: nevyvážené závorky u funkce `{name}`")


def run_should_escalate(ts_text: str, cases: list) -> list:
    """Spustí SKUTEČNÝ text `shouldEscalate` v Node (rozhodnutí se NEOPISUJE)."""
    skript = ts_text + """
const cases = JSON.parse(process.env.TEST_CASES);
const out = cases.map((c) => shouldEscalate(c[0] === null ? undefined : c[0], c[1]));
console.log(JSON.stringify(out));
"""
    r = subprocess.run(
        ["node", "-e", skript],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={"TEST_CASES": json.dumps(cases),
             "PATH": os.environ.get("PATH", ""),
             "SYSTEMROOT": os.environ.get("SYSTEMROOT", "")},
    )
    if r.returncode != 0:
        raise SystemExit(f"CHYBA: node spadl při volání shouldEscalate:\n{(r.stderr or '')[:800]}")
    return json.loads((r.stdout or "").strip().splitlines()[-1])


def toml_var(text: str, name: str) -> str:
    m = re.search(rf'^{name}\s*=\s*"([^"]*)"', text, flags=re.M)
    return m.group(1) if m else ""


# SQL STAÉ (odstraněné) verze: počítalo běhy JEDNOHO úkolu. Drží se tu jako
# „známý chybný případ" — bez něj by tvrzení „starý watchdog se nemohl spustit"
# nebylo změřené, jen odvozené.
OLD_PER_TASK_SQL = """
  SELECT t.id, (SELECT COUNT(*) FROM runs r WHERE r.task_id = t.id) AS pokusu
    FROM tasks t WHERE t.status IN ('ready','failed') ORDER BY t.id DESC LIMIT 50
"""


def prepare_db(sql_granule: str, sql_candidates: str):
    db = sqlite3.connect(":memory:")
    db.executescript(
        """
        CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT, status TEXT, payload TEXT);
        CREATE TABLE runs (id INTEGER PRIMARY KEY, task_id INTEGER, status TEXT, started_at TEXT);
        CREATE TABLE roadmap (item_id TEXT PRIMARY KEY, task_id INTEGER, status TEXT,
                              created_at TEXT, updated_at TEXT, naposledy_selhalo TEXT,
                              eskalovano TEXT);
        """
    )

    def task(tid, game, grain, status="failed"):
        db.execute("INSERT INTO tasks (id, title, status, payload) VALUES (?,?,?,?)",
                   (tid, grain, status, json.dumps({"game": game, "grain": grain,
                                                    "repo": "ssevcikm-spec/uo-shadows"})))

    def runs(tid, count, started="2026-10-05T02:00:00"):
        for _ in range(count):
            db.execute("INSERT INTO runs (task_id, status, started_at) VALUES (?,?,?)",
                       (tid, "failure", started))

    def row(item_id, created, eskalovano=None, status="failed"):
        db.execute("INSERT INTO roadmap (item_id, status, created_at, updated_at, eskalovano)"
                   " VALUES (?,?,?,?,?)", (item_id, status, created, created, eskalovano))

    # A) jedna granule, DVA úkoly: 5 + 3 běhů
    row("test/npc", "2026-09-30T16:00:00")
    task(1, "test", "npc"); runs(1, 5)
    task(2, "test", "npc"); runs(2, 3)
    # B) nepřítel: jeden úkol, 5 běhů
    row("test/enemy", "2026-09-30T10:00:00")
    task(3, "test", "enemy"); runs(3, 5)
    # C) po resetu: řádek založený 6. 10., 4 běhy jsou STARŠÍ (stará kampaň)
    row("test/po-resetu", "2026-10-06T20:00:00")
    task(4, "test", "po-resetu")
    runs(4, 4, "2026-10-01T02:00:00")
    runs(4, 1, "2026-10-06T21:00:00")
    # D) granule bez řádku v roadmapě
    task(5, "test", "bez-radku"); runs(5, 3)
    # E) už ohlášená granule (6 běhů)
    row("test/uz-ohlaseno", "2026-09-30T10:00:00", eskalovano="2026-10-06 20:00:00")
    task(6, "test", "uz-ohlaseno"); runs(6, 6)
    # F) pod prahem (2 běhy)
    row("test/pod-prahem", "2026-09-30T10:00:00")
    task(7, "test", "pod-prahem"); runs(7, 2)
    db.commit()

    granule = {r[0]: r[1] for r in db.execute(sql_granule).fetchall()}
    kandidati = [r[0] for r in db.execute(sql_candidates).fetchall()]
    stary = db.execute(OLD_PER_TASK_SQL).fetchall()
    return granule, kandidati, stary


def main() -> int:
    global checks, errors
    print(f"=== zdroj: {CONDUCTOR.name} + {WRANGLER.name} ===")
    if not CONDUCTOR.is_file():
        print(f"CHYBA: chybí {CONDUCTOR}")
        return 1
    src = CONDUCTOR.read_text(encoding="utf-8")
    kod = strip_comments(src)

    sql_granule = extract_template(src, "SQL_GRANULE_RUNS")
    sql_candidates = extract_candidate_sql(src)
    prah_default = extract_default_threshold(src)
    wtext = WRANGLER.read_text(encoding="utf-8") if WRANGLER.is_file() else ""
    prah_cfg = toml_var(wtext, "ESCALATE_AFTER")
    strop_cfg = toml_var(wtext, "MAX_ATTEMPTS")
    print(f"=== prah: default v kodu {prah_default}, ve wrangler.toml {prah_cfg!r}; "
          f"strop {strop_cfg!r} ===")

    try:
        granule, kandidati, stary = prepare_db(sql_granule, sql_candidates)
    except sqlite3.OperationalError as e:
        print(f"CHYBA: SQL ze zdrojáku nejde spustit ({e}) — sqlite bez JSON1?")
        return 1

    # A) počítá se NA GRANULI (přes všechny úkoly)
    check("A: dva úkoly jedné granule (5+3) = 8 spálených běhů", granule.get("test/npc"), 8)
    check("A: jeden úkol s 5 běhy = 5", granule.get("test/enemy"), 5)
    # známý chybný případ: starý dotaz na JEDEN úkol vidí u téže granule nejvýš 5
    stare_npc = [r[1] for r in stary if r[0] in (1, 2)]
    check("A: STARY dotaz na jeden ukol vidi u teze granule nejvyse 5"
          " (proto se watchdog se prahem 8 nikdy nespustil)",
          max(stare_npc) if stare_npc else None, 5)

    # B) běhy před založením řádku se nepočítají (roadmap-reset je cesta zpět)
    check("B: po resetu se počítá jen běh po založení řádku", granule.get("test/po-resetu"), 1)
    # C) granule bez řádku v roadmapě se nepočítá
    check("C: granule bez řádku v roadmapě v počítadle není", "test/bez-radku" in granule, False)

    # D) už ohlášená granule se nevrací mezi kandidáty (žádný spam)
    check("D: ohlášená granule není kandidát", "test/uz-ohlaseno" in kandidati, False)
    check("D: neohlášená nad prahem kandidát JE", "test/npc" in kandidati, True)
    check("D: druhá neohlášená nad prahem je taky kandidát", "test/enemy" in kandidati, True)

    # E) PRAH SE APLIKUJE ROZHODNUTÍM, ne SQL — a to se volá (neopisuje)
    ts_funkce = extract_function(src, "shouldEscalate")
    print(f"=== shouldEscalate vytažena ze zdrojáku ({len(ts_funkce.splitlines())} řádků) ===")
    vysledky = run_should_escalate(ts_funkce, [[2, prah_default], [3, prah_default],
                                               [8, prah_default], [0, prah_default],
                                               [None, prah_default]])
    check("E: 2 běhy < prah 3 → NEhlásit", vysledky[0], False)
    check("E: 3 běhy = prah → hlásit", vysledky[1], True)
    check("E: 8 běhů > prah → hlásit (přesně dnešní entity.npc)", vysledky[2], True)
    check("E: nula běhů → NEhlásit", vysledky[3], False)
    check("E: granule bez řádku (undefined) → NEhlásit, není to nula", vysledky[4], False)

    # F) prah musí být POD stropem — jinak je to prah, který nikdy nepřijde
    check("F: výchozí prah v kódu < MAX_ATTEMPTS", prah_default < int(strop_cfg or "0"), True)
    check("F: prah ve wrangler.toml < MAX_ATTEMPTS",
          int(prah_cfg or "0") < int(strop_cfg or "0"), True)

    # G) značka se ukládá do `roadmap` (payload úkolu retry zahodí)
    check("G: značka se zapisuje do roadmap.eskalovano",
          bool(re.search(r"UPDATE\s+roadmap\s+SET\s+eskalovano", kod, flags=re.I)), True)
    check("G: kandidáti se ptají na roadmap.eskalovano",
          "eskalovano" in sql_candidates, True)

    print()
    if errors:
        print(f"VYSLEDEK: {checks} kontrol, {errors} CHYB")
        return 1
    print(f"VYSLEDEK: {checks} kontrol, 0 chyb")
    return 0


if __name__ == "__main__":
    sys.exit(main())
