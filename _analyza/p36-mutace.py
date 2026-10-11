# -*- coding: utf-8 -*-
r"""P36 — MUTAČNÍ DŮKAZ: umí měřidlo `p36-a-overeni.py` SPADNOUT — a umí i PROJÍT?

PROČ (`AGENTS.md`): „Napsal jsi test? Vrať do kódu vadu a podívej se, že spadne.“
Bez toho je i „18/0“ jen ticho. A druhá polovina téhož: **kontrola, která spadne
VŽDY, není o nic lepší než ta, která projde vždy** — proto se každá mutace měří
i ve ZDRAVÉM stavu (tam musí PROJÍT).

CO SE MUTUJE (vždy KOPIE přes seam — živé soubory se NESMÍ změnit):
  M1  TVRZENÍ v §66 (seam `P36_HANDOFF`): vypuštěný čítač `74/0 plně` → A3 MUSÍ
      hlásit „TVRZENÍ NENALEZENO“. Dokazuje, že se tvrzení OPRAVDU ČTE
      Z DOKUMENTU (H155), nebere z hlavy.
  M2  DOKLAD CIZÍHO MĚŘIDLA (seam `P36_P35A`): čítač přepsán na 99/0 → A3 MUSÍ
      hlásit ROZDÍL proti §66.
  M3  ŽIVÝ TAIL (seam `P36_TAIL`): jiné `scriptVersion.id` → A1 krok 3 (křížová
      kontrola verze) MUSÍ spadnout. To je jádro „HTTP 200 není důkaz“.
  M4  ŽIVÝ STAV (seam `P36_HEALTH`): `/health` BEZ `last_cron_pokus` → A5 MUSÍ
      spadnout na „NEPOSÍLÁ last_cron_pokus“.
  M5  KÓD CONDUCTORA (seam `P36_CONDUCTOR`): do KOPIE se vrátí DRAHÝ dekodér
      (`Uint8Array.from(atob(…), mapFn)`) → A2 MUSÍ spadnout na kontrole kódu.
  M6  TEST, KTERÝ OPRAVU VOLÁ (seam `P36_TEST`): v KOPII zmizí vícebajtová
      čeština scénáře AF → A2 MUSÍ spadnout na „test NEMÁ scénář AF“.

⚠ Mutuje se do KOPIÍ v `_analyza/p36-mutace-scratch/` (živé soubory se nechávají
  být) — a na konci se hash VŠECH živých souborů porovná s hodnotou před testem.

Použití: python _analyza\p36-mutace.py
"""

import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
MERIDLO = ANALYZA / "p36-a-overeni.py"
SCRATCH = ANALYZA / "p36-mutace-scratch"

ZIVE = [
    WS / "HANDOFF.md",
    WS / "NEXT-SESSION-INSTRUKCE.md",
    WS / "KRONIKA-PROJEKTU.md",
    WS / "conductor" / "src" / "index.ts",
    WS / "tools" / "test-tick-offline.mjs",
    ANALYZA / "p36-p35a-plne-vystup.txt",
    ANALYZA / "p36-tail-raw-vystup.txt",
    ANALYZA / "p36-a-overeni.py",
]

kontrol = 0
chyb = []


def zk(ok, popis):
    global kontrol
    kontrol += 1
    print("  %s %s" % ("OK   " if ok else "CHYBA", popis))
    if not ok:
        chyb.append(popis)


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def kopie(orig, jmeno):
    SCRATCH.mkdir(parents=True, exist_ok=True)
    cil = SCRATCH / jmeno
    shutil.copyfile(orig, cil)
    return cil


def zmutuj_text(cesta, stary, novy, vsechny=False):
    """Vrátí (pocet_vyskytu, zmeneno) — a zapíše kopii, jen když je to bezpečné.

    `vsechny=False` vyžaduje PRÁVĚ 1 výskyt (past omylů #18/#106: kotva, která
    je v souboru víckrát, znamená, že mutace netrefila to, co si myslíš).
    `vsechny=True` je pro případ, kdy je kotva ZÁMĚRNĚ na mnoha místech
    (např. `scriptVersion.id` v každém eventu tailu) — mění se PAK VŠECHNY.
    """
    t = pathlib.Path(cesta).read_text(encoding="utf-8").replace("\r\n", "\n")
    n = t.count(stary)
    if n == 0 or (not vsechny and n != 1):
        return n, False
    novy_text = t.replace(stary, novy) if vsechny else t.replace(stary, novy, 1)
    if novy_text == t or stary in novy:
        return n, False
    pathlib.Path(cesta).write_text(novy_text, encoding="utf-8", newline="\n")
    return n, True


def spust(args, env=None, timeout=2700):
    t0 = time.time()
    e = {**os.environ, "PYTHONIOENCODING": "utf-8", **(env or {})}
    r = subprocess.run([str(a) for a in args], cwd=str(WS), env=e,
                       capture_output=True, timeout=timeout)
    out = ((r.stdout or b"") + (r.stderr or b"")).decode("utf-8", "replace")
    return r.returncode, out, time.time() - t0


def otisk(out):
    """Otisk POJMENOVANÝCH verdiktů (ROZDÍL/CHYBA/NÁLEZ) — bez něj se mutace,
    která změní TEXT verdiktu, ale ne POČTY, jeví jako „nic se nezměnilo“."""
    radky = [r.strip() for r in out.splitlines()
             if re.match(r"^\s*(ROZDÍL|CHYBA|NÁLEZ)\s+\S", r)]
    return hashlib.sha256("\n".join(sorted(radky)).encode("utf-8")).hexdigest()[:12]


def verdikt(out):
    """(kontrol, chyb, ROZDÍLŮ, NEZMĚŘENO, otisk pojmenovaných verdiktů)."""
    m = re.findall(r"V[ÝY]SLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb"
                   r"(?:\s*\(z toho (\d+) ROZDÍLŮ, (\d+) NEZMĚŘENO)?", out)
    if not m:
        return None
    k, c, r, n = m[-1]
    return (int(k), int(c), int(r or 0), int(n or 0), otisk(out))


def bez_vystupu(out, vzory):
    v = []
    for v2 in vzory:
        for r in out.splitlines():
            if re.search(v2, r):
                v.append(r.strip()[:150])
    return v


def bez(mut, popis, sekce, env, ocekavany_vzor, zdrave_env=None):
    """Mutant MUSÍ změnit VERDIKT (a pojmenovat to) · zdravý stav MUSÍ projít.

    ⚠ „Spadnout“ NENÍ totéž co „exit 1“: měřidlo rozlišuje CHYBU (vada měření)
    a ROZDÍL (stav se posunul). Mutace KONTROLY tvrzení se projeví jako ROZDÍL —
    proto se porovnává CELÝ verdikt (kontrol/chyb/ROZDÍLŮ/NEZMĚŘENO), ne exit kód.
    """
    print("\n%s — %s" % (mut, popis))
    zdrave = None
    if zdrave_env is not None:
        _, out, _ = spust(["python", str(MERIDLO), "--jen", sekce, "--levne",
                           "--vystup", "_analyza/p36-mut-zdrave-vystup.txt"], env=zdrave_env)
        zdrave = verdikt(out)
        # ⚠ Zdravý stav MUSÍ projít BEZ CHYB měření. ROZDÍLY dovoleny jsou:
        # v A3 jsou to SKUTEČNÁ pojmenovaná zjištění (§66 tvrdí 74/0, naměřeno
        # 73/0; zadání tvrdí 71/0) — „zdravý“ tu neznamená „nulový“, ale
        # „změřený a bez vady měřidla“.
        zk(zdrave is not None and zdrave[1] == 0,
           "%s: ZDRAVÝ stav MUSÍ projít bez CHYB → %s (kontrol, chyb, ROZDÍLŮ, NEZMĚŘENO, otisk)"
           % (mut, zdrave))
        if zdrave and (zdrave[2] or zdrave[3]):
            print("        (zdravý běh má %d ROZDÍLŮ a %d NEZMĚŘENO — pojmenované, ne tiché)"
                  % (zdrave[2], zdrave[3]))
    rc, out, _ = spust(["python", str(MERIDLO), "--jen", sekce, "--levne",
                        "--vystup", "_analyza/p36-mut-%s-vystup.txt" % mut.lower()], env=env)
    v = verdikt(out)
    zk(v is not None and v != zdrave,
       "%s: MUTANT MUSÍ ZMĚNIT VERDIKT → %s (zdravý %s, exit %d)" % (mut, v, zdrave, rc))
    zk(v is not None and (v[1] > 0 or v[2] > 0 or v[3] > 0),
       "%s: a mutant NESMÍ zůstat zelený (chyb/ROZDÍLŮ/NEZMĚŘENO > 0)" % mut)
    nalezene = bez_vystupu(out, ocekavany_vzor)
    zk(bool(nalezene), "%s: a musí to POJMENOVAT (%s)" % (mut, " / ".join(ocekavany_vzor)))
    for n in nalezene[:3]:
        print("        %s" % n)


def main():
    print("=" * 96)
    print("P36 — MUTAČNÍ DŮKAZ MĚŘIDLA p36-a-overeni.py")
    print("=" * 96)
    if not (ANALYZA / "p36-p35a-plne-vystup.txt").is_file():
        print("CHYBA: chybí doklad `_analyza/p36-p35a-plne-vystup.txt` (spusť nejdřív A3)")
        return 2

    pred = {str(p): sha(p) for p in ZIVE if p.is_file()}
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)

    # ── M1: tvrzení v dokumentu ─────────────────────────────────────────────
    kop = kopie(WS / "HANDOFF.md", "handoff-mutant.md")
    n, zm = zmutuj_text(kop, "vlastní měřidlo P35 74/0 plně", "vlastní měřidlo P35 plně")
    zk(n == 1 and zm, "M1: kotva v KOPII HANDOFFu je PRÁVĚ 1× a text se ZMĚNIL")
    bez("M1", "TVRZENÍ V DOKUMENTU (74/0 vypuštěno)",
        "A3", {"P36_HANDOFF": str(kop), "P36_P35A": str(ANALYZA / "p36-p35a-plne-vystup.txt")},
        [r"TVRZENÍ NENALEZENO"],
        zdrave_env={"P36_P35A": str(ANALYZA / "p36-p35a-plne-vystup.txt")})

    # ── M2: čítač v dokladu cizího měřidla ──────────────────────────────────
    kop2 = kopie(ANALYZA / "p36-p35a-plne-vystup.txt", "p35a-mutant.txt")
    n, zm = zmutuj_text(kop2, "VÝSLEDEK: 73 kontrol, 0 chyb", "VÝSLEDEK: 99 kontrol, 0 chyb")
    zk(n == 1 and zm, "M2: kotva čítače v KOPII dokladu je PRÁVĚ 1× a text se ZMĚNIL")
    bez("M2", "ČÍTAČ CIZÍHO MĚŘIDLA (73 → 99)",
        "A3", {"P36_P35A": str(kop2)}, [r"naměřeno 99/0"],
        zdrave_env={"P36_P35A": str(ANALYZA / "p36-p35a-plne-vystup.txt")})

    # ── M3: verze v živém tailu ─────────────────────────────────────────────
    kop3 = kopie(ANALYZA / "p36-tail-raw-vystup.txt", "tail-mutant.txt")
    n, zm = zmutuj_text(kop3, "3985379c-4f45-424c-8400-2e26b54cae23",
                        "deadbeef-0000-1111-2222-333344445555", vsechny=True)
    zk(n >= 1 and zm, "M3: v KOPII tailu je verze na %d místech a VŠECHNA se změnila" % n)
    bez("M3", "KŘÍŽOVÁ KONTROLA VERZE (živý tail běží jinou verzi)",
        "A1", {"P36_TAIL": str(kop3)}, [r"živý tail běží JINOU verzi"],
        zdrave_env={})

    # ── M4: /health bez POKUSU ──────────────────────────────────────────────
    kop4 = kopie(ANALYZA / "p35-health-vystup.txt", "health-mutant.json")
    telo = json.loads(kop4.read_text(encoding="utf-8"))
    for k in ("last_cron_pokus", "last_cron_pokus_min"):
        telo.pop(k, None)
    kop4.write_text(json.dumps(telo, ensure_ascii=False, indent=1), encoding="utf-8")
    zk("last_cron_pokus" not in kop4.read_text(encoding="utf-8"),
       "M4: v KOPII /health NENÍ last_cron_pokus (a zbytek zůstal)")
    bez("M4", "/health BEZ POKUSU o tik",
        "A5", {"P36_HEALTH": str(kop4), "P36_BEZ_SITE": "1"}, [r"NEPOSÍLÁ last_cron_pokus"],
        zdrave_env={"P36_HEALTH": str(ANALYZA / "p35-health-vystup.txt"), "P36_BEZ_SITE": "1"})

    # ── M5: drahý dekodér v KOPII conductora ────────────────────────────────
    kop5 = kopie(WS / "conductor" / "src" / "index.ts", "conductor-mutant.ts")
    n, zm = zmutuj_text(
        kop5,
        'const bytes = new Uint8Array(bin.length);\n'
        '      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);',
        'const bytes = Uint8Array.from(atob(String(data.content || "").replace(/\\n/g, "")), '
        '(c) => c.charCodeAt(0));')
    zk(n == 1 and zm, "M5: kotva dekodéru v KOPII conductora je PRÁVĚ 1× a text se ZMĚNIL")
    bez("M5", "DRAHÝ DEKODÉR V KÓDU (vrácena vada H165)",
        "A2", {"P36_CONDUCTOR": str(kop5)}, [r"DRAHÝ přepis"],
        zdrave_env={})

    # ── M6: test bez scénáře AF ─────────────────────────────────────────────
    # ⚠ KOPIE MUSÍ LEŽET VEDLE ORIGINÁLU: test si hledá vstupní soubory relativně
    # ke svému umístění, takže kopie ve scratchi spadne na CESTY — a to by
    # vypadalo jako „mutace zabrala“, i kdyby nemutovala nic (nález z běhu M6).
    kop6 = WS / "tools" / "test-tick-offline.p36mut.mjs"
    shutil.copyfile(WS / "tools" / "test-tick-offline.mjs", kop6)
    n, zm = zmutuj_text(kop6, "žluťoučký", "zlutoucky", vsechny=True)
    zk(n >= 1 and zm, "M6: vícebajtová čeština v KOPII testu zmizela (%d×)" % n)
    bez("M6", "TEST BEZ SCÉNÁŘE AF",
        "A2", {"P36_TEST": str(kop6)}, [r"NEMÁ scénář AF"],
        zdrave_env={})

    # ── M7: fakeDb bez modelu tabulky `state` (vrácení slepého místa) ───────
    # ⚠ TOHLE JE MUTACE ÚKOLU B: `test-tick-offline.mjs` se v P36 rozšířil
    # o model tabulky `state` (+13 kontrol, scénář AG). Bez vrácení té vady by
    # „231/0“ nebylo doložené — muselo by se věřit, že nové kontroly umí spadnout.
    print("\nM7 — FAKEDB BEZ TABULKY `state` (tep se nezapíše, /health čte `catch`)")
    kop7 = WS / "tools" / "test-tick-offline.p36mut.mjs"
    shutil.copyfile(WS / "tools" / "test-tick-offline.mjs", kop7)
    n, zm = zmutuj_text(kop7, "sql.includes('SELECT k, v FROM state')",
                        "sql.includes('SELECT k, v FROM state NIKDY')")
    zk(n == 1 and zm, "M7: kotva větve pro `state` v KOPII testu je PRÁVĚ 1× a změnila se")
    _, zdrave_t, _ = spust(["node", str(WS / "tools" / "test-tick-offline.mjs")], timeout=900)
    mz = re.findall(r"VYSLEDEK:\s*(\d+) kontrol, (\d+) [Cc][Hh][Yy][Bb]", zdrave_t)
    zk(bool(mz) and int(mz[-1][1]) == 0,
       "M7: ŽIVÝ test MUSÍ projít → %s kontrol, %s chyb" % (mz[-1] if mz else ("?", "?")))
    rc7, out7, _ = spust(["node", str(kop7)], timeout=900)
    mm = re.findall(r"VYSLEDEK:\s*(\d+) kontrol, (\d+) [Cc][Hh][Yy][Bb]", out7)
    if mm:
        zk(rc7 != 0 and int(mm[-1][1]) > 0,
           "M7: MUTANT testu MUSÍ spadnout → %s kontrol, %s chyb (exit %d)"
           % (mm[-1][0], mm[-1][1], rc7))
    else:
        zk(False, "M7: mutant testu nevrátil čítač (exit %d)" % rc7)
    ag = [l.strip()[:120] for l in out7.splitlines() if "CHYBA" in l and "AG:" in l]
    zk(bool(ag), "M7: a musí spadnout KONTROLY SCÉNÁŘE AG (ne něco jiného) — %d z nich" % len(ag))
    for l in ag[:4]:
        print("        %s" % l)
    if kop7.exists():
        kop7.unlink()
    zk(not kop7.exists(), "M7: dočasná kopie testu je UKLIZENÁ")

    # ── NÁVRAT: živé soubory BAJT NA BAJT a žádný scratch ───────────────────
    print("\nNÁVRAT")
    if kop6.exists():
        kop6.unlink()
    zk(not kop6.exists(), "dočasná kopie testu `tools/test-tick-offline.p36mut.mjs` je UKLIZENÁ")
    for p, h in pred.items():
        zk(sha(p) == h, "živý %s je BAJT NA BAJT původní" % pathlib.Path(p).name)
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    zk(not SCRATCH.exists(), "scratch `_analyza/p36-mutace-scratch` je UKLIZENÝ")

    print("\n" + "=" * 96)
    print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
    for c in chyb:
        print("   CHYBA %s" % c)
    print("=" * 96)
    (ANALYZA / "p36-mutace-vystup.txt").write_text(
        "P36 mutace — %s\nVÝSLEDEK: %d kontrol, %d chyb\n" % (time.strftime("%Y-%m-%dT%H:%M:%S%z"), kontrol, len(chyb)) +
        "\n".join("CHYBA " + c for c in chyb) + "\n", encoding="utf-8")
    return 1 if chyb else 0


if __name__ == "__main__":
    sys.exit(main())
