"""Brána pro B3b: STROP NA GRANULI (`GRAIN_MAX_RUNS`) + shoda obou tvarů klíče.

PROČ TENHLE TEST EXISTUJE
-------------------------
Naměřeno na živé službě 6. 10. 2026: `entity.npc` spálil **8 běhů** napříč DVĚMA
úkoly (#228: 5, #234: 3), `entity.enemy` 5, a conductor je vydával dál — ve
frontě na to vzniklo **49 osiřelých úloh** na tutéž granuli. Watchdog (B3a) to
už HLÁSÍ, ale nic nezastaví. Strop (B3b) je ta druhá polovina.

⚠ STROP JE ZÁMĚRNĚ VYPNUTÝ (`GRAIN_MAX_RUNS = "0"`), aby se dal nasadit
po částech: první deploy přinese jen watchdog, druhý teprve zastaví vydávání.
Kdyby se zapnulo obojí naráz, nebylo by z čeho měřit, že watchdog hlásí.

CO SE NEOPISUJE
---------------
Ze zdrojáku se vytáhnou a ZAVOLAJÍ tři skutečné funkce (`grainCap`,
`grainCapped`, `grainKeyOf`) a k tomu SQL počítadla; SQL se pustí ve skutečném
SQLite a porovná se klíč z JS s klíčem, který skládá SQL.

CO TVRDÍ:
  A) `grainCap`: prázdné/`0`/nesmysl/záporné → **0 = vypnuto** (strop, který se
     nedá přečíst, nesmí tiše zastavit orchestra), `"5"` → 5,
  B) `grainCapped`: pod stropem ne, na stropě ano, `cap = 0` nikdy (vypnuto),
     `undefined` (granule bez řádku) není nula, která se zastaví,
  C) **oba tvary klíče granule SEDÍ** (`grainKeyOf` v JS × `GRAIN_KEY_SQL` v SQL) —
     dva tvary téhož klíče je vada, kterou žádný test nevidí (invariant 17),
  D) strop je OPRAVDU v cestě, kterou se granule vydává (filtr `ready`
     v `roadmapTick` i dispatch smyčka; počítadlo se měří jednou za tik),
  E) konfigurace `GRAIN_MAX_RUNS` ve `wrangler.toml` je čitelné číslo
     (a test VYPÍŠE, jestli je strop zapnutý nebo vypnutý).

Test má assert i nenulový exit kód.
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
SCRATCH = WS / "_analyza" / "b3b-scratch"

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
    raise SystemExit(f"CHYBA: nevyvážené závorky u `{name}`")


def extract_template(src: str, name: str) -> str:
    m = re.search(rf"const\s+{re.escape(name)}\s*=\s*`", src)
    if not m:
        raise SystemExit(f"CHYBA: `const {name} = ...` ve zdroji není")
    start = m.end()
    end = src.index("`", start)
    text = src[start:end]
    if name != "GRAIN_KEY_SQL" and "${GRAIN_KEY_SQL}" in text:
        text = re.sub(r"\$\{GRAIN_KEY_SQL\}", extract_template(src, "GRAIN_KEY_SQL"), text)
    return text


def toml_var(text: str, name: str) -> str:
    m = re.search(rf'^{name}\s*=\s*"([^"]*)"', text, flags=re.M)
    return m.group(1) if m else ""


def run_js(ts_text: str, payload: dict) -> dict:
    """Zavolá skutečné funkce `grainCap`, `grainCapped`, `grainKeyOf` v Node."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    driver = SCRATCH / "grain.mts"
    driver.write_text(
        "const c: any = JSON.parse(process.env.TEST_CASES || '{}');\n"
        + ts_text + "\n"
        "const out = {\n"
        "  cap: c.caps.map((e: any) => grainCap(e)),\n"
        "  capped: c.capped.map((p: any) => grainCapped(p[0] === null ? undefined : p[0], p[1])),\n"
        "  keys: c.keys.map((k: any) => grainKeyOf(k)),\n"
        "};\n"
        "console.log(JSON.stringify(out));\n",
        encoding="utf-8",
    )
    r = subprocess.run(
        ["node", "--experimental-strip-types", str(driver)],
        cwd=str(WS), capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={"TEST_CASES": json.dumps(payload),
             "PATH": os.environ.get("PATH", ""),
             "SYSTEMROOT": os.environ.get("SYSTEMROOT", "")},
    )
    if r.returncode != 0:
        raise SystemExit(f"CHYBA: node spadl:\n{(r.stderr or '')[:900]}")
    return json.loads((r.stdout or "").strip().splitlines()[-1])


def main() -> int:
    global checks, errors
    print(f"=== zdroj: {CONDUCTOR.name} + {WRANGLER.name} ===")
    for p in (CONDUCTOR, WRANGLER):
        if not p.is_file():
            print(f"CHYBA: chybí {p}")
            return 1
    src = CONDUCTOR.read_text(encoding="utf-8")
    kod = strip_comments(src)
    wtext = WRANGLER.read_text(encoding="utf-8")

    ts = "\n".join(extract_function(src, n) for n in ("grainCap", "grainCapped", "grainKeyOf"))
    payload = {
        "caps": [{}, {"GRAIN_MAX_RUNS": "5"}, {"GRAIN_MAX_RUNS": "0"},
                 {"GRAIN_MAX_RUNS": "abc"}, {"GRAIN_MAX_RUNS": "-3"}],
        "capped": [[None, 5], [4, 5], [5, 5], [9, 5], [9, 0], [0, 0]],
        "keys": ['{"game":"test","grain":"npc"}', "{}", "tohle-není-json"],
    }
    out = run_js(ts, payload)

    # A) strop: co je vypnuto a co ne
    check("A: prázdná konfigurace → 0 (strop vypnutý)", out["cap"][0], 0)
    check("A: GRAIN_MAX_RUNS=5 → 5", out["cap"][1], 5)
    check("A: GRAIN_MAX_RUNS=0 → 0 (vypnuto)", out["cap"][2], 0)
    check("A: nesmysl (abc) → 0 (nesmí tiše zastavit orchestra)", out["cap"][3], 0)
    check("A: záporné (-3) → 0", out["cap"][4], 0)

    # B) rozhodnutí
    check("B: granule bez řádku (undefined) se nezastaví", out["capped"][0], False)
    check("B: 4 běhy pod stropem 5 → jede dál", out["capped"][1], False)
    check("B: 5 běhů = strop 5 → ZASTAVIT", out["capped"][2], True)
    check("B: 9 běhů nad stropem → ZASTAVIT (přesně dnešní entity.npc)", out["capped"][3], True)
    check("B: cap = 0 (vypnuto) → nikdy nezastavovat", out["capped"][4], False)
    check("B: cap = 0 a nula běhů → nezastavovat", out["capped"][5], False)

    # C) SHODA OBOU TVARŮ KLÍČE (past invariantu 17)
    sql = extract_template(src, "SQL_GRANULE_RUNS")
    db = sqlite3.connect(":memory:")
    db.executescript(
        """
        CREATE TABLE tasks (id INTEGER PRIMARY KEY, payload TEXT);
        CREATE TABLE runs (id INTEGER PRIMARY KEY, task_id INTEGER, started_at TEXT);
        CREATE TABLE roadmap (item_id TEXT PRIMARY KEY, created_at TEXT);
        """
    )
    db.execute("INSERT INTO tasks VALUES (1, ?)",
               (json.dumps({"game": "test", "grain": "npc", "repo": "a/b"}),))
    db.execute("INSERT INTO runs VALUES (1, 1, datetime('now'))")
    db.execute("INSERT INTO roadmap VALUES ('test/npc', datetime('now', '-1 day'))")
    db.commit()
    sql_klic = [r[0] for r in db.execute(sql).fetchall()]
    check("C: SQL skládá klíč `test/npc`", sql_klic, ["test/npc"])
    check("C: JS `grainKeyOf` skládá TENTÝŽ klíč", out["keys"][0], "test/npc")
    check("C: oba tvary klíče SEDÍ (invariant 17)",
          out["keys"][0] == sql_klic[0] if sql_klic else False, True)
    check("C: payload bez game/grain → null (nezastavovat naslepo)", out["keys"][1], None)
    check("C: rozbitý JSON → null (nespadnout)", out["keys"][2], None)

    # D) strop je OPRAVDU v cestě, kterou se granule vydává (čte se KÓD)
    m = re.search(r"const\s+ready\s*=\s*items\.filter\(\(i\)\s*=>(.{0,700}?)\);", kod, re.S)
    usek_ready = m.group(1) if m else ""
    if not usek_ready:
        checks += 1
        errors += 1
        print("  CHYBA nenašel jsem filtr `ready` v roadmapTick — test je slepý")
    else:
        check("D: filtr `ready` zná strop", "grainCapped(" in usek_ready, True)
    m2 = re.search(r"const\s+task\s*=\s*\(readyAll\.results[^;]{0,400}", kod, re.S)
    usek_task = m2.group(0) if m2 else ""
    if not usek_task:
        checks += 1
        errors += 1
        print("  CHYBA nenašel jsem výběr úlohy v dispatch smyčce — test je slepý")
    else:
        check("D: dispatch smyčka zná strop", "grainCapped(" in usek_task, True)
        check("D: dispatch smyčka počítá klíč přes `grainKeyOf`", "grainKeyOf(" in usek_task, True)
    check("D: počítadlo se měří JEDNOU za tik a jde do watchdogu",
          bool(re.search(r"escalateStuckTasks\(env,\s*grainRunsMap\)", kod)), True)
    check("D: týž map se předává do roadmapTick (jedno číslo pro všechny)",
          bool(re.search(r"roadmapTick\(env,\s*retryH,\s*grainRunsMap,\s*cap\)", kod)), True)

    # E) konfigurace: strop musí být čitelné číslo; test VYPÍŠE, jak je nastaven
    hodnota = toml_var(wtext, "GRAIN_MAX_RUNS")
    platne = hodnota == "" or (hodnota.lstrip("-").isdigit() and int(hodnota) >= 0)
    check(f"E: GRAIN_MAX_RUNS je čitelné číslo ({hodnota!r})", platne, True)
    stav = "VYPNUTÝ" if (hodnota == "" or int(hodnota or 0) == 0) else f"ZAPNUTÝ na {hodnota}"
    print(f"  INFO  strop na granuli je dnes {stav}")

    print()
    if errors:
        print(f"VYSLEDEK: {checks} kontrol, {errors} CHYB")
        return 1
    print(f"VYSLEDEK: {checks} kontrol, 0 chyb")
    return 0


if __name__ == "__main__":
    sys.exit(main())
