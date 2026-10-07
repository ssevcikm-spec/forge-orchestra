"""Brána pro B4: `listGames` fallback NESMÍ dispatchovat (invariant 18).

PROČ TENHLE TEST EXISTUJE
-------------------------
`listGames` má „zpětnou kompatibilitu“: když v registru není AKTIVNÍ hra, vrátí
jeden defaultní repo z `env.GITHUB_REPO`. Důsledek (naměřeno v analýze,
invariant 18): **vypnutí poslední registrované hry orchestra nezastaví** — cron
tikne, `roadmapTick` si vezme `GITHUB_REPO` a dispatchuje dál. Uživatel vypne
hru, a hra se přesto vyvíjí (a pálí kvótu).

Acceptance plánu (`PLAN-ROZVOJ-ORCHESTRA.md`, B4):
  `POST /game/active {active:false}` → `/health` `games=0` a **žádný dispatch**.
Plán to sám označuje jako **zamýšlené** („radši nemakat“).

CO SE NEOPISUJE
---------------
  * SQL dotazu se vytáhne **ze zdrojáku** a spustí se ve **skutečném SQLite**
    nad fixturou (takže filtr `active = 1` se měří chováním, ne čtením),
  * funkce `listGames` se vytáhne ze zdrojáku a **zavolá se** v Node
    (`--experimental-strip-types`) s falešnou D1, do které se vloží právě ty
    řádky, které vrátil SQLite.

CO TVRDÍ:
  A) registr s jednou aktivní hrou → vrátí JI (a `repo` bere z registru,
     ne z `env.GITHUB_REPO` — invariant 4),
  B) registr, kde je hra jen VYPNUTÁ → SQL nevrátí nic a `listGames` musí vrátit
     **prázdný seznam** (žádný dispatch) — dnes vrací fallback,
  C) prázdný registr (nikdy nic registrovaného) → taky prázdný seznam,
  D) ve KÓDU (bez komentářů) nesmí zůstat fallback na `env.GITHUB_REPO`,
  E) **guardy v `tick`** (dispatch smyčka čte úlohy z D1, takže samotný
     `listGames` k „žádnému dispatchi“ nestačí): smyčka se hned na začátku ptá
     na `aktivniHry`, `tick` si je načítá z registru a `roadmapTick` se pouští
     jen s aktivní hrou.

Test má assert i nenulový exit kód.
"""

import json
import pathlib
import re
import sqlite3
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
CONDUCTOR = WS / "conductor" / "src" / "index.ts"
SCRATCH = WS / "_analyza" / "b4-scratch"

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
    v = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    return re.sub(r"//[^\n]*", " ", v)


def extract_function(src: str, name: str) -> str:
    m = re.search(rf"async\s+function\s+{re.escape(name)}\s*\(", src)
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
    raise SystemExit(f"CHYBA: nevyvážené závorky u `{name}`")


def extract_games_sql(src: str) -> str:
    """SQL z `listGames` (řetězec obsahující `FROM games`)."""
    for m in re.finditer(r'"([^"\n]*FROM games[^"\n]*)"', src):
        return m.group(1)
    raise SystemExit("CHYBA: v `listGames` není dotaz na `games`")


def prepare_db(sql: str):
    db = sqlite3.connect(":memory:")
    db.executescript(
        """
        CREATE TABLE games (game_id TEXT PRIMARY KEY, repo TEXT NOT NULL,
                            roadmap_file TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1,
                            created_at TEXT);
        """
    )
    return db


def run_listgames(ts_text: str, rows: list) -> list:
    """Zavolá SKUTEČNÝ text `listGames` s falešnou D1, která vrátí `rows`."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    driver = SCRATCH / "listgames.mts"
    driver.write_text(
        "const rows: any[] = JSON.parse(process.env.TEST_ROWS || '[]');\n"
        "const env: any = {\n"
        '  GITHUB_REPO: "fallback/nesmi-se-pouzit",\n'
        '  ROADMAP_FILE: ".forge/roadmap.json",\n'
        "  DB: { prepare: (_sql: string) => ({ all: async () => ({ results: rows }) }) },\n"
        "};\n"
        + ts_text + "\n"
        "console.log(JSON.stringify(await listGames(env)));\n",
        encoding="utf-8",
    )
    r = subprocess.run(
        ["node", "--experimental-strip-types", str(driver)],
        cwd=str(WS), capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={"TEST_ROWS": json.dumps(rows),
             "PATH": __import__("os").environ.get("PATH", ""),
             "SYSTEMROOT": __import__("os").environ.get("SYSTEMROOT", "")},
    )
    if r.returncode != 0:
        raise SystemExit(f"CHYBA: node spadl:\n{(r.stderr or '')[:900]}")
    return json.loads((r.stdout or "").strip().splitlines()[-1])


def main() -> int:
    global checks, errors
    print(f"=== zdroj: {CONDUCTOR.name} ===")
    if not CONDUCTOR.is_file():
        print(f"CHYBA: chybí {CONDUCTOR}")
        return 1
    src = CONDUCTOR.read_text(encoding="utf-8")
    sql = extract_games_sql(src)
    ts = extract_function(src, "listGames")
    print(f"=== dotaz na hry: {sql[:70]}… ===")

    # ── SQL: filtr `active = 1` se měří CHOVÁNÍM (skutečný SQLite) ────────────
    db = prepare_db(sql)
    db.execute("INSERT INTO games VALUES ('hra-on', 'a/hra-on', '.forge/roadmap.json', 1, datetime('now'))")
    db.execute("INSERT INTO games VALUES ('hra-off', 'a/hra-off', '.forge/roadmap.json', 0, datetime('now'))")
    db.commit()
    aktivni = [dict(zip(("game_id", "repo", "roadmap_file", "active"), r))
               for r in db.execute(sql).fetchall()]
    check("SQL: vratí jen AKTIVNÍ hru", [g["game_id"] for g in aktivni], ["hra-on"])

    db2 = prepare_db(sql)
    db2.execute("INSERT INTO games VALUES ('hra-off', 'a/hra-off', '.forge/roadmap.json', 0, datetime('now'))")
    db2.commit()
    vypnuta = db2.execute(sql).fetchall()
    check("SQL: vypnutá hra se nevrací", vypnuta, [])

    # ── JS: co udělá `listGames`, když SQL nic nevrátí ────────────────────────
    vysledek_on = run_listgames(ts, aktivni)
    check("A: s aktivní hrou vrací právě ji", [g.get("game_id") for g in vysledek_on], ["hra-on"])
    check("A: repo bere z REGISTRU, ne z env.GITHUB_REPO",
          [g.get("repo") for g in vysledek_on], ["a/hra-on"])

    vysledek_off = run_listgames(ts, [])
    check("B: vypnutá hra (SQL nic nevrátí) → PRÁZDNÝ seznam = žádný dispatch",
          vysledek_off, [])
    check("B: fallback na env.GITHUB_REPO se NEPOUŽIL",
          any("nesmi-se-pouzit" in str(g.get("repo")) for g in vysledek_off), False)

    # ── D) staticky: fallback nesmí být v KÓDU (komentář, který ho popisuje, nevadí) ──
    kod = strip_comments(src)
    telo = extract_function(kod, "listGames")
    check("D: v KÓDU `listGames` není `env.GITHUB_REPO`", "env.GITHUB_REPO" in telo, False)

    # ── E) GUARDY v `tick`: acceptance zní „ŽÁDNÝ DISPATCH“, a ten se neděje
    #      jen v `listGames` — dispatch smyčka čte úlohy z D1. Měří se KÓD
    #      (komentáře odstraněné), ne text, který vadu popisuje.
    m = re.search(r"const\s+started\s*:\s*number\[\]\s*=\s*\[\]\s*;\s*while\s*\(true\)\s*\{"
                  r"(.{0,300})", kod, re.S)
    usek = m.group(1) if m else ""
    if not usek:
        errors += 1
        checks += 1
        print("  CHYBA nenašel jsem dispatch smyčku (`const started … while (true) {`) —")
        print("        test je slepý; zkontroluj index.ts ručně.")
    else:
        check("E: dispatch smyčka hned na začátku kontroluje aktivní hry",
              "aktivniHry.length" in usek and "break" in usek, True)
    check("E: `tick` si aktivní hry načítá z registru (ne z env)",
          bool(re.search(r"const\s+aktivniHry\s*=\s*await\s+listGames\(env\)", kod)), True)
    check("E: `roadmapTick` se volá jen když je aktivní hra",
          bool(re.search(r"aktivniHry\.length\s*\?\s*await\s+roadmapTick", kod)), True)

    print()
    if errors:
        print(f"VYSLEDEK: {checks} kontrol, {errors} CHYB")
        return 1
    print(f"VYSLEDEK: {checks} kontrol, 0 chyb")
    return 0


if __name__ == "__main__":
    sys.exit(main())
