"""Offline test zámku souborů v dispatch smyčce conductora (invariant 17).

PROČ TENHLE TEST EXISTUJE
-------------------------
Zámek `owns` v dispatch smyčce NEBLOKOVAL NIC. `locked` se plnilo holými jmény
souborů, ale porovnávalo se proti `lockKeys()`, což jsou klíče `{repo}/{soubor}`
– množiny se tedy nikdy nemohly protnout. Naměřeno 1. 10. 2026 replikou obou
funkcí: `locked = ['scripts/player.gd']` vs. klíč
`'ssevcikm-spec/uo-shadows/scripts/player.gd'`.

Dnes to nemělo následek (roadmapa hry kolizi `owns` nemá), ale při
`MAX_CONCURRENT = 5` je to tikající bomba: dvě granule se stejnými `owns` se
rozjedou paralelně a auto-merge to slije jako cizí práci.

JAK TO TESTOVÁ (a proč je to důvěryhodné)
-----------------------------------------
`lockKeys()` se NEOPISUJE – vytáhne se **ze zdrojáku conductora** (zevřením
závorek) a spustí se skutečný text funkce. Když se v conductoru změní, test
použije novou verzi. Jediné, co se replikuje, je **jednořádkové porovnání**
z dispatch smyčky (`index.ts:806`), a to je výslovně označené.

Test má assert i nenulový exit kód. Bez toho by „zelený" nic neznamenal –
naměřeno: `test-cooldown.py` v témž adresáři vypisoval `CHYBA` a končil
s exit 0.
"""

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KONDUKTOR = pathlib.Path(__file__).resolve().parents[1] / "conductor" / "src" / "index.ts"
REPO = "ssevcikm-spec/uo-shadows"

kontrol = 0
chyb = 0


def bez_komentaru(zdroj: str) -> str:
    """Odstraní // a /* */ komentáře i řetězce – aby kontrola četla KÓD.

    PROČ: první verze tohohle testu hledala v celém zdrojáku řetězec
    `for (const k of lockKeys(...)) locked.add(k);` – a našla ho V KOMENTÁŘI,
    který vadu popisuje. Test pak prošel i s vrácenou vadou (ověřeno mutačním
    testem). `game-developer`: „statická kontrola musí číst KÓD, ne komentáře."
    """
    v = re.sub(r"/\*.*?\*/", " ", zdroj, flags=re.S)
    v = re.sub(r"//[^\n]*", " ", v)
    return v


def vytahni_funkci(zdroj: str, jmeno: str) -> str:
    """Vytáhne CELÝ text funkce ze zdrojáku (po vyvážené závorce)."""
    m = re.search(rf"function\s+{re.escape(jmeno)}\s*\(", zdroj)
    if not m:
        raise SystemExit(f"CHYBA: funkce `{jmeno}` v {KONDUKTOR} nenalezena")
    start = zdroj.index("{", m.end() - 1)
    hloubka = 0
    for i in range(start, len(zdroj)):
        if zdroj[i] == "{":
            hloubka += 1
        elif zdroj[i] == "}":
            hloubka -= 1
            if hloubka == 0:
                return zdroj[m.start():i + 1]
    raise SystemExit(f"CHYBA: nevyvážené závorky u funkce `{jmeno}`")


def spust_lock_keys(ts_text: str, payloady: list[str]) -> list[list[str]]:
    """Spustí SKUTEČNÝ text `lockKeys` v Node a vraží klíče pro každý payload."""
    skript = ts_text + """
const env = { GITHUB_REPO: process.env.TEST_REPO };
const payloady = JSON.parse(process.env.TEST_PAYLOADY);
const out = payloady.map((p) => lockKeys(p, env));
console.log(JSON.stringify(out));
"""
    r = subprocess.run(
        ["node", "-e", skript],
        capture_output=True,
        text=True,
        env={
            "TEST_REPO": REPO,
            "TEST_PAYLOADY": __import__("json").dumps(payloady),
            "PATH": __import__("os").environ.get("PATH", ""),
            "SYSTEMROOT": __import__("os").environ.get("SYSTEMROOT", ""),
        },
    )
    if r.returncode != 0:
        raise SystemExit(f"CHYBA: node spadl:\n{r.stderr[:800]}")
    return __import__("json").loads(r.stdout.strip().splitlines()[-1])


def zkontroluj(popis: str, skutecne, ocekavane) -> None:
    global kontrol, chyb
    kontrol += 1
    if skutecne == ocekavane:
        print(f"  OK    {popis}")
    else:
        chyb += 1
        print(f"  CHYBA {popis}\n        čekáno: {ocekavane!r}\n        dáno:   {skutecne!r}")


def main() -> int:
    global chyb
    print(f"=== zdroj: {KONDUKTOR} ===")
    if not KONDUKTOR.is_file():
        print(f"CHYBA: soubor neexistuje ({KONDUKTOR})")
        return 1
    zdroj = KONDUKTOR.read_text(encoding="utf-8")

    # 1) Funkce se vytáhne ze zdrojáku – když ji někdo přejmenuje, test to řekne.
    ts = vytahni_funkci(zdroj, "lockKeys")
    print(f"=== lockKeys vytažena ze zdrojáku ({len(ts.splitlines())} řádků) ===")
    zkontroluj("klíč má tvar '{repo}/{soubor}'",
               spust_lock_keys(ts, ['{"repo":"%s","owns":["scripts/player.gd"]}' % REPO]),
               [[f"{REPO}/scripts/player.gd"]])
    zkontroluj("dvě hry se stejným souborem se NEblokují",
               spust_lock_keys(ts, [
                   '{"repo":"a/hra","owns":["scripts/game.gd"]}',
                   '{"repo":"b/hra","owns":["scripts/game.gd"]}',
               ]),
               [["a/hra/scripts/game.gd"], ["b/hra/scripts/game.gd"]])
    zkontroluj("rozbitý JSON nespadne, vrátí []",
               spust_lock_keys(ts, ["tohle-není-json"]), [[]])
    zkontroluj("prázdné owns vrátí []",
               spust_lock_keys(ts, ['{"repo":"%s","owns":[]}' % REPO]), [[]])
    zkontroluj("chybějící repo spadne na GITHUB_REPO z env",
               spust_lock_keys(ts, ['{"owns":["scripts/x.gd"]}']),
               [[f"{REPO}/scripts/x.gd"]])

    # 2) Volající místo: dispatch smyčka musí plnit `locked` TÍMŽ zdrojem.
    #    Čte se KÓD BEZ KOMENTÁŘŮ – komentář, který vadu popisuje, nesmí
    #    vypadat jako oprava (naměřeno: první verze testu se na tom spálila).
    #
    #    Hledá se VOLÁNÍ `lockKeys(` v části, která plní `locked`. Nezáleží na
    #    tom, jestli je volání přímo v `.add()` nebo v mezivé proměnné – obojí
    #    je správně. Rozbitá verze `lockKeys` v té části nemá vůbec (sahá na
    #    `JSON.parse(...).owns`), takže ji to musí chytit.
    kod = bez_komentaru(zdroj)
    m = re.search(r"const\s+locked\s*=\s*new\s+Set<string>\(\)\s*;(.{0,700}?)\n\s*\n", kod, re.S)
    usek = m.group(1) if m else ""
    if not usek:
        chyb += 1
        print("  CHYBA nenašel jsem místo, kde dispatch smyčka plní `locked` --")
        print("        test je slepý; zkontroluj index.ts ručně.")
    elif "lockKeys(" in usek:
        print("  OK    dispatch smyčka plní `locked` přes lockKeys() (index.ts)")
    else:
        chyb += 1
        print("  CHYBA dispatch smyčka NEplní `locked` přes lockKeys() --")
        print("        zámek `owns` v dispatch smyčce je znovu rozbitý (invariant 17).")

    # 3) SROVNÁNÍ: co dělala ROZBITÁ verze a co dělá opravená.
    #    Replikuje se jen jednořádkové porovnání z index.ts:806:
    #        !lockKeys(t.payload, env).some((k) => locked.has(k))
    #    `projde` = kandidát se SMÍ vydat (tedy zámek ho NEZablokoval).
    import json as _json
    bezici = '{"repo":"%s","owns":["scripts/player.gd"]}' % REPO
    kandidat_kolize = '{"repo":"%s","owns":["scripts/player.gd"]}' % REPO
    kandidat_volny = '{"repo":"%s","owns":["scripts/npc.gd"]}' % REPO

    klicu = spust_lock_keys(ts, [bezici, kandidat_kolize, kandidat_volny])
    zamcene_opraveno = set(klicu[0])

    def projde_opraveno(kandidat_klice):
        return not any(k in zamcene_opraveno for k in kandidat_klice)

    # Rozbitá verze: `locked` se plnilo HOLÝMI jmény, porovnání ale klíči ->
    # klíč se nikdy netrefí, takže projde VŠECHNO.
    zamcene_rozbite = set(_json.loads(bezici)["owns"])
    projde_rozbite = not any(k in zamcene_rozbite for k in klicu[1])

    zkontroluj("OPRAVENÁ verze: kolidující owns se NEVYDÁ",
               projde_opraveno(klicu[1]), False)
    zkontroluj("OPRAVENÁ verze: nekolidující owns se VYDÁ",
               projde_opraveno(klicu[2]), True)
    zkontroluj("ROZBITÁ verze (holá jména): kolidující owns PROJDE – důkaz vady",
               projde_rozbite, True)

    print()
    if chyb:
        print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} CHYB")
        return 1
    print(f"VÝSLEDEK: {kontrol} kontrol, 0 chyb")
    return 0


if __name__ == "__main__":
    sys.exit(main())
