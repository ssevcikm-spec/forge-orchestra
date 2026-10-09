# -*- coding: utf-8 -*-
r"""P32 — MUTAČNÍ TEST: umí VLASTNÍ MĚŘIDLO P32 spadnout? (a měří opravy P32?)

PROČ: `AGENTS.md` — „Napsal jsi test? Vrať do kódu vadu a podívej se, že spadne."
A druhá polovina téhož: **důkaz je DIFERENCIÁL**, ne zelená. Tenhle test proto
vrací vady do KOPIÍ a porovnává verdikty:

  * **M1 — měřidlo `p32-a-overeni.py`:** tvrzení §62 se v **kopii** `HANDOFF.md`
    zmutuje (`over-skilly 92/0` → `93/0`); měřidlo nad kopií musí spadnout
    (`exit 1`) a pojmenovat ten rozchod. Živý `HANDOFF.md` se **neotvírá na
    zápis** — cesty jdou z prostředí (`P32_HANDOFF`).
  * **M2 — kontrola v `p22-test-mutace.py` (oprava H140/H141):** v kopii testu se
    `mrtve_cesty()` přepíše na „vždy (0, 0)" → test musí spadnout. Tím je
    dokázáno, že nová kontrola (parse MĚŘENÉHO řádku) umí selhat — na rozdíl od
    původní podřetězcové, kterou uspokojilo `"40 mrtvých"`.
  * **M3 — patcher `p27-dopln-zaznamy.py` (oprava H136):** ověří se, že
    `p32-test-zapis-kotvy.py` PROŠEL a že jeho výstup obsahuje diferenciál
    (oslabená kopie patcheru fixturu ZAPSALA) — jinak by „nezapsáno" nic
    nedokazovalo.

Použití: python _analyza/p32-mutace.py
"""

import os
import pathlib
import shutil
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
HANDOFF = WS / "HANDOFF.md"
MERIDLO = ANALYZA / "p32-a-overeni.py"
P22T = ANALYZA / "p22-test-mutace.py"
P32T = ANALYZA / "p32-test-zapis-kotvy.py"
SCRATCH = ANALYZA / "p32-mutace-scratch"
KOPIE_H = SCRATCH / "handoff-kopie.md"
KOPIE_P22 = ANALYZA / "_p32-mut-p22t.py"
DOKLAD = ANALYZA / "p32-mutace-vystup.txt"

sys.path.insert(0, str(ANALYZA))
from _mutace import mutuj  # noqa: E402

# ── kotvy mutací (MUSÍ se shodovat se zdrojem; ověřují se níž) ────────────────
CLAIM_STARY = "over-skilly 92/0 · over-dokumentaci 64/0 · kronika SEDÍ (45 řádků)"
CLAIM_NOVY = "over-skilly 93/0 · over-dokumentaci 64/0 · kronika SEDÍ (45 řádků)"
P22_STARY = ("    n = VZOR_CESTY.findall(v)\n"
             "    return (int(n[-1][0]), int(n[-1][1])) if n else None")
P22_NOVY = "    return (0, 0)"

kontrol = 0
chyb = []
_radky = []


class _Tee:
    """Zapisuje výstup zároveň na obrazovku i do dokladu (doklad = celý běh)."""

    def __init__(self, f):
        self.f = f

    def write(self, s):
        self.f.write(s)
        _radky.append(s)
        return len(s)

    def flush(self):
        self.f.flush()


sys.stdout = _Tee(sys.stdout)


def k(popis, zjisteno, ocekavano):
    global kontrol
    kontrol += 1
    if zjisteno == ocekavano:
        print("  OK    %s" % popis)
        return True
    chyb.append(popis)
    print("  CHYBA %s\n        čekáno:   %r\n        naměřeno: %r"
          % (popis, ocekavano, zjisteno))
    return False


def spust(args, timeout=1800, env=None):
    r = subprocess.run([str(a) for a in args], cwd=str(WS),
                       env={**os.environ, "PYTHONIOENCODING": "utf-8", **(env or {})},
                       capture_output=True, timeout=timeout)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace") + \
        (r.stderr or b"").decode("utf-8", "replace")


def main() -> int:
    print("=" * 78)
    print("P32 — MUTAČNÍ TEST MĚŘIDLA P32 A OPRAV H136/H140")
    print("datum (z hodin): %s" % time.strftime("%Y-%m-%d %H:%M:%S %z"))
    print("=" * 78)
    SCRATCH.mkdir(parents=True, exist_ok=True)

    # ── P0 pojistky ─────────────────────────────────────────────────────────
    print("\n── P0: POJISTKY ──")
    k("P0 vlastní měřidlo `p32-a-overeni.py` existuje", MERIDLO.is_file(), True)
    k("P0 test patcheru `p32-test-zapis-kotvy.py` existuje", P32T.is_file(), True)
    text = HANDOFF.read_text(encoding="utf-8")
    k("P0 kotva tvrzení §62 je v HANDOFF.md právě 1×", text.count(CLAIM_STARY), 1)
    zdroj_p22 = P22T.read_text(encoding="utf-8")
    k("P0 kotva `mrtve_cesty` je v p22-test-mutace.py právě 1×",
      zdroj_p22.count(P22_STARY), 1)
    k("P0 nový tvar NEobsahuje starý jako podřetězec (jinak by mutace nic nezměnila)",
      P22_STARY in P22_NOVY, False)
    KOPIE_H.write_bytes(text.encode("utf-8"))

    # ── M1: měřidlo nad KOPIÍ (zdravou a zmutovanou) ─────────────────────────
    print("\n── M1: `p32-a-overeni.py --jen B3` nad KOPIÍ §62 ──")
    t0 = time.time()
    kod0, v0 = spust([sys.executable, "-B", str(MERIDLO), "--jen", "B3",
                      "--vystup", "_analyza/p32-mut-b3-zdrave-vystup.txt"],
                     env={"P32_HANDOFF": str(KOPIE_H)})
    k("M1-a měřidlo nad ZDRAVOU kopií projde (exit 0, %.0f s)" % (time.time() - t0),
      kod0, 0)
    with mutuj(KOPIE_H, CLAIM_STARY, CLAIM_NOVY) as mut:
        print("      kotva %d× · %s → %s" % (mut.pocet_vyskytu, mut.hash_pred[:12],
                                             mut.hash_po_mutaci[:12]))
        kod1, v1 = spust([sys.executable, "-B", str(MERIDLO), "--jen", "B3",
                          "--vystup", "_analyza/p32-mut-b3-mutant-vystup.txt"],
                         env={"P32_HANDOFF": str(KOPIE_H)})
    k("M1-b měřidlo nad ZMUTOVANOU kopií SPADNE (exit 1)", kod1, 1)
    k("M1-b a spadne NA TÉ kontrole (over-skilly: dokument vs naměřeno)",
      ("over-skilly" in v1 and "CHYBA" in v1), True)
    roz = [l.strip() for l in v1.splitlines() if l.strip().startswith("CHYBA")]
    print("      · %s" % (roz[0][:150] if roz else "(žádná CHYBA v řádcích)"))
    k("M1-c kopie HANDOFF.md vrácena bajt na bajt", mut.hash_po_navratu, mut.hash_pred)
    k("M1-d ŽIVÝ HANDOFF.md se během testu nezměnil (seam `P32_HANDOFF`)",
      HANDOFF.read_bytes() == text.encode("utf-8"), True)

    # ── M2: kontrola v p22-test-mutace.py umí selhat ────────────────────────
    print("\n── M2: `mrtve_cesty()` v kopii testu P22 → (0, 0) ──")
    kod2, v2 = spust([sys.executable, "-B", str(P22T)], timeout=600)
    k("M2-a ŽIVÝ test P22 po opravě projde (exit 0)", kod2, 0)
    shutil.copyfile(P22T, KOPIE_P22)
    try:
        with mutuj(KOPIE_P22, P22_STARY, P22_NOVY):
            zmut = KOPIE_P22.read_bytes()
        KOPIE_P22.write_bytes(zmut)
        kod3, v3 = spust([sys.executable, "-B", str(KOPIE_P22)], timeout=600)
        red = [l.strip() for l in v3.splitlines() if l.strip().startswith("CHYBA")]
        k("M2-b oslabená kopie testu SPADNE (exit≠0)", kod3 != 0, True)
        k("M2-b a pojmenuje to na kontrole měřeného řádku",
          any("mrtvých" in l or "změřila" in l for l in red), True)
        print("      · %s" % (red[0][:150] if red else "(žádná CHYBA)"))
    except ValueError as e:
        k("M2 oslabenou kopii šlo vyrobit", False, str(e)[:120])
    finally:
        KOPIE_P22.unlink(missing_ok=True)
    k("M2-c oslabená kopie testu P22 je smazaná", KOPIE_P22.exists(), False)

    # ── M3: patcher — diferenciál je součástí důkazu ────────────────────────
    print("\n── M3: `p32-test-zapis-kotvy.py` (H136) má DIFERENCIÁL ──")
    kod4, v4 = spust([sys.executable, "-B", str(P32T)], timeout=600)
    k("M3-a test patcheru projde (exit 0)", kod4, 0)
    k("M3-b a obsahuje diferenciál (oslabená kopie fixturu ZAPSALA)",
      "ZAPSALA (bajty se změnily)" in v4, True)
    k("M3-c a živý patcher u fixtury NEZAPSAL", "NEZAPSÁNO" in v4, True)

    # ── úklid ───────────────────────────────────────────────────────────────
    shutil.rmtree(SCRATCH, ignore_errors=True)
    k("úklid: scratch je smazaný", SCRATCH.exists(), False)

    print("\n" + "=" * 78)
    print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
    print("=" * 78)
    DOKLAD.write_bytes("".join(_radky).encode("utf-8"))
    return 1 if chyb else 0


if __name__ == "__main__":
    sys.exit(main())
