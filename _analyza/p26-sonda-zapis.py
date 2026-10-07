"""P26 sonda: kam umi PODPROCES zapsat ve workspace (stav sandboxu, ne vada skriptu).

Vzor: skill dsh-prostredi 4e.  Nemuze selhat na kodovani - vse ASCII.
"""
import os
import sys
import tempfile

WS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = [
    ("koren workspace", WS),
    ("_analyza", os.path.join(WS, "_analyza")),
    ("tools", os.path.join(WS, "tools")),
    ("conductor", os.path.join(WS, "conductor")),
    ("conductor/src", os.path.join(WS, "conductor", "src")),
]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("python:", sys.version.split()[0])
    print("workspace:", WS)
    print("cwd:", os.getcwd())
    ok, bad = 0, 0
    for jmeno, cil in TARGETS:
        if not os.path.isdir(cil):
            print("  %-18s NEEXISTUJE" % jmeno)
            continue
        # a) mkstemp (to, co dela _mutace.py)
        try:
            fd, cesta = tempfile.mkstemp(prefix=".p26-sonda-", dir=cil)
            os.write(fd, b"x")
            os.close(fd)
            os.remove(cesta)
            a = "ZAPSANO"
            ok += 1
        except OSError as e:
            a = "%s: %s" % (type(e).__name__, e.errno)
            bad += 1
        # b) primy open() na jmeno souboru
        primy = os.path.join(cil, ".p26-sonda-open.txt")
        try:
            with open(primy, "wb") as f:
                f.write(b"x")
            os.remove(primy)
            b = "ZAPSANO"
        except OSError as e:
            b = "%s: %s" % (type(e).__name__, e.errno)
        print("  %-18s mkstemp=%-22s open=%-22s" % (jmeno, a, b))
    print("SOUHRN: zapsano=%d odmitnuto=%d" % (ok, bad))
    return 0


if __name__ == "__main__":
    sys.exit(main())
