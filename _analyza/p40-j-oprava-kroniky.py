# p40-j-oprava-kroniky.py — OPRAVA VLASTNÍHO OMYLU P40 v KRONICE.
#
# CO SE STALO: při vkládání řádku session 55 jsem jako `old_string` použil
# ZAČÁTEK řádku 54 — takže řádek 54 přišel o hlavičku a jeho ZBYTEK zůstal
# nalepený za řádkem 55 (jeden řádek = [55][zbytek 54]).
#
# OPRAVA (nic se nemaže, všechno se ověřuje):
#   1. řádek 54 se vezme CELÝ z HEAD (`git show HEAD:KRONIKA-PROJEKTU.md`),
#   2. z pracovního řádku se najde NEJDELŠÍ SUFIX, který je zároveň koncem
#      řádku 54 z HEAD (= ten nalepený zbytek) a ověří se, že jím řádek KONČÍ,
#   3. zapíše se DVOJICE: [řádek 54 z HEAD, řádek 55 bez zbytku].
# Předchozí verze skriptu hledala zbytek podle PEVNÉHO prefixu (88 znaků) —
# a ten nesedl (nahrazené bylo víc); tahle verze hledá podle SOULADU textů,
# takže na konkrétní délce prefixu nezávisí.
#
# Použití: python _analyza/p40-j-oprava-kroniky.py
# Exit 0 = opraveno; 1 = nesouhlasí (nic se nezapisuje).

import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = pathlib.Path(__file__).resolve().parents[1]
KRONIKA = WS / "KRONIKA-PROJEKTU.md"

head = subprocess.run([str(WS / "tools" / "git.cmd"), "-C", str(WS),
                       "show", "HEAD:KRONIKA-PROJEKTU.md"],
                      capture_output=True, shell=True)
hr = (head.stdout or b"").decode("utf-8", "replace").splitlines()
p = KRONIKA.read_text(encoding="utf-8").splitlines()

i55 = next((i for i, l in enumerate(p) if l.startswith("| **55** | **12. 10. 2026**")), None)
i54 = next((i for i, l in enumerate(hr) if l.startswith("| **54** | **11. 10. 2026**")), None)
if i55 is None or i54 is None:
    print(f"CHYBA: řádek 55 v pracovním souboru: {i55}, řádek 54 v HEAD: {i54} — nic se nemění.")
    sys.exit(1)

prac = p[i55]
radek54 = hr[i54]

# 2) Rozdělovač: KONEC mého řádku 55 je přesně text, který jsem psal
#    (`**Brány** měřeny po posledním commitu (§4 zadání). |`). Zbytek za ním
#    musí být SUFIX řádku 54 z HEAD — to je ten nalepený zbytek.
KONEC55 = "**Brány** měřeny po posledním commitu (§4 zadání). |"
i = prac.find(KONEC55)
if i < 0:
    print(f"CHYBA: konec mého řádku 55 ({KONEC55!r}) v pracovním řádku NENÍ — nic se nemění.")
    print("  konec pracovního řádku:", repr(prac[-120:]))
    sys.exit(1)
radek55 = prac[:i + len(KONEC55)]
najity = prac[i + len(KONEC55):]
if not radek54.endswith(najity):
    print(f"CHYBA: zbytek za mým řádkem 55 NENÍ sufixem řádku 54 z HEAD — nic se nemění.")
    print(f"  zbytek ({len(najity)} znaků): {najity[:80]!r} … {najity[-40:]!r}")
    sys.exit(1)
print(f"řádek 54 z HEAD: {len(radek54)} znaků · nalepený zbytek: {len(najity)} znaků")
print(f"nový řádek 55:   {len(radek55)} znaků (končí {radek55[-30:]!r})")
print(f"dvojice dá délku {len(radek54) + len(radek55) + 1} vs. dnešní řádek {len(prac)}")

p[i55:i55 + 1] = [radek54, radek55]
KRONIKA.write_text("\n".join(p) + "\n", encoding="utf-8")
print(f"OPRAVENO: řádek {i55 + 1} = session 54, řádek {i55 + 2} = session 55")
sys.exit(0)
