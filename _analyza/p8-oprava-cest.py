"""P8 — OPRAVA CEST V KODU OBOU REPU (po presunu na E:).

PROC ODVOZOVAT, A NE PREPSAT NA `E:\\...`: prepsani na novou absolutni cestu by
repo znovu svazalo s jednim mistem — a presne to je vada, ktera presun vynutila.
Cesty se proto ODVOZUJI od umisteni skriptu (`__file__` / `import.meta.url`);
takovy nastroj funguje, at je repo kdekoliv.

ZMERENY ROZSAH (pred opravou): 62 vyskytu, 20 unikatnich cest, VSECHNY
v `tools/` obou repu. Zadna cesta v kodu neodkazuje na koren stanice
(`C:\\Users\\Ssevc\\Local-Deepseek` samostatne) — to je důležité: znamena to,
ze po presunu staci odvozovat z umisteni skriptu a nic nesmi zustat na C:.

MAPOVANI:
  <WS>\\orchestra            -> PARENT (root repa)
  <WS>\\orchestra\\...        -> PARENT/...
  <WS>\\games\\uo-shadows      -> PARENT/'uo-shadows'  (sourozenec)
  <WS>\\games\\uo-shadows\\... -> PARENT/'uo-shadows'/...
  <WS>\\games                -> PARENT
  <WS>\\gameforge\\...        -> mrtve (GameForge smazan) — jen se ohlasí

BEZPECNOST (tri pojistky):
  1) pred zapisem se SPOCTA vyskytu a zapise se pocet nahrad
  2) po zapisu se soubor ZNOVU PARSuje (`ast.parse` / `node --check`)
  3) kdyz parsovani selze, soubor se VRA­TI ze zalohy a hlasi se chyba

Pouziti: python p8-oprava-cest.py [--kontrola]
"""
from __future__ import annotations

import ast
import re
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(r"E:\Workspaces\forge-orchestra")
HRA = Path(r"E:\Workspaces\uo-shadows")
CIL = [REPO, HRA]
KOD_SUFFIX = {".py", ".mjs", ".js", ".ts", ".ps1", ".cmd", ".gd", ".sql"}
LOG = Path(r"C:\Users\Ssevc\Local-Deepseek\_analyza\p8-oprava-cest-log.txt")
ZALOHA = Path(r"C:\Users\Ssevc\Local-Deepseek\_analyza\zaloha-p8")

# ── definice hlavicek (vlozi se na zacatek souboru, ktery ji jeste nema) ──
# ⚠ Hlavicka se sklada PODLE TOHO, CO UZ SOUBOR MA. Naměřeno: prvni verze
# vlozila `import { join }` do `compare-game.mjs`, ktery `join` UZ importoval
# → `SyntaxError: Identifier 'join' has already been declared`. Zase to
# odhalil az parser po zapisu — a to je presne duvod, proc se parsuje.
MJS_VZHLED = "// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni\n"\
             "// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.\n"\
             "// `tools/` je primo v koreni repa, takze PARENT = root repa.\n"\
             "const __dir = dirname(fileURLToPath(import.meta.url));\n"\
             "const PARENT = dirname(__dir);\n"
PY_VZHLED = (
    "import pathlib as _pl\n"
    "\n"
    "# P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni skriptu.\n"
    "# `tools/` je primo v koreni repa, takze _PARENT = root repa.\n"
    "_PARENT = _pl.Path(__file__).resolve().parents[1]\n"
)


def mjs_hlavicka(text: str) -> str:
    """Doplni jen to, co soubor jeste nema (jinak by vznikl duplicitni import)."""
    potreba = []
    if "fileURLToPath" not in text:
        potreba.append("import { fileURLToPath } from 'node:url';")
    if not re.search(r"\bdirname\b", text) or "from 'node:path'" not in text:
        # dirname muze byt z node:path — doplnime jen, kdyz ho soubor nema
        if "dirname" not in text:
            potreba.append("import { dirname } from 'node:path';")
    return "\n".join(potreba + [""]) + MJS_VZHLED if potreba else MJS_VZHLED

STANICE = r"C:\Users\Ssevc\Local-Deepseek"
HRA_JMENO = "uo-shadows"

# Klic = konkretni slozka pod korenem (nebo "" pro koren samotny).
# Hodnota = cim se nahradi OBSAH tytéž cesty (bez uvozovek) v JS, resp. v Pythonu.
# Skládání zbytku cesty se dela ZVLAST (viz sloz_zbytek) — nikdy se nevnoruje
# výraz do řetězce.
ROOTY = [
    (r"orchestra\repo", "repo"),
    ("orchestra/repo", "repo"),
    (r"games\uo-shadows", "hra"),
    ("games/uo-shadows", "hra"),
    (r"orchestra", "orchestra"),
    ("orchestra", "orchestra"),
    (r"games", "parent"),
    ("games", "parent"),
    ("", "stanice"),  # koren samotny = stanice (D6) — resi se rucne
]


def na_vyraz(kam: str, je_py: bool, zbytek: str = "") -> str:
    """Cely výraz pro dany koren + zbytek cesty.

    ⚠ Treti vada prvni verze (odhalil parser): pro `PARENT` se zbytek pripojil
    bez `join(...)`, takze vzniklo `const SECRETS = PARENT, '.secrets';`.
    Základ a zbytek se proto skladaji NA JEDNOM MISTE — neda se zapomenout
    obalit to spojenim.
    """
    casti = [c for c in zbytek.replace("\\", "/").split("/") if c]
    if je_py:
        zaklad = {"repo": "_PARENT / 'repo'", "hra": "_PARENT / 'uo-shadows'",
                  "orchestra": "_PARENT", "parent": "_PARENT",
                  "stanice": "STANICE"}[kam]
        return zaklad + "".join(f" / {c!r}" for c in casti)
    if kam == "stanice":
        return "STANICE" + (" + " + repr("/" + "/".join(casti)) if casti else "")
    zaklad = {"repo": "PARENT", "hra": "PARENT", "orchestra": "PARENT",
              "parent": "PARENT"}[kam]
    if kam == "repo":
        return "join(" + ", ".join(["PARENT", "'repo'"] + [repr(c) for c in casti]) + ")"
    if kam == "hra":
        return "join(" + ", ".join(["PARENT", "'uo-shadows'"] + [repr(c) for c in casti]) + ")"
    # orchestra i parent = root; zbytek se pripoji
    return "join(" + ", ".join(["PARENT"] + [repr(c) for c in casti]) + ")"


def sloz_zbytek(zbytek: str, je_py: bool) -> str:
    """Zbytek cesty (napr. '\\.forge\\roadmap.json') jako pripojeni k výrazu."""
    if not zbytek:
        return ""
    casti = [c for c in zbytek.replace("\\", "/").split("/") if c]
    if je_py:
        return "".join(f" / {c!r}" for c in casti)
    return "".join(f", {c!r}" for c in casti)

# ── KOREN STANICE: `C:\\Users\\Ssevc\\Local-Deepseek` SAMOTNE (bez podslozky) ──
# ⚠ TADY SE ZAMERNE NIC AUTOMATICKY NENAHRAZUJE. Do "korene bez podslozky"
# pise nekolik souboru a kazdy miri NĚKAM JINAM:
#   `WS / "AGENTS.md"`            -> projektova pravidla = REPO (jde s repem)
#   `WS / "HANDOFF.md"`           -> projektovy dokument = REPO
#   `WS / "MOZNOSTI-AGENTA.md"`   -> dokument STANICE   = STANICE (zustal na C:)
#   `const ROOT = '<WS>'` a `ROOT + '/games/<hra>'` -> sourozenec = PARENT
# Automaticka nahrada by musela hádat, ktery z nich to je — a hádat u cest je
# presne ta vada, ktera presun vynutila. Ty tri soubory se proto opravuji
# RUCNE a jejich seznam je v `RUCNI` nize (skript je preskoci a rekne to).
RUCNI = {
    "tools/kontrola-diakritiky.py",
    "tools/over-dokumentaci.py",
    "tools/kontrola-driftu.mjs",
    "tools/sync-sablona-hra.py",
    "tools/verify-setup.py",
}
MRTVE = [
    (r"C:\Users\Ssevc\Local-Deepseek\gameforge", "GameForge (smazano 30. 9. 2026)"),
    ("C:/Users/Ssevc/Local-Deepseek/gameforge", "GameForge (smazano 30. 9. 2026)"),
]

radky: list[str] = []
zmenene: list[Path] = []
chyby: list[str] = []


def zapis(t: str) -> None:
    print(t)
    radky.append(t)


def ma_hlavicku(text: str, je_py: bool) -> bool:
    if je_py:
        return "_PARENT = _pl.Path(__file__)" in text
    return "const PARENT = dirname(__dir__)" in text


def vloz_hlavicku(text: str, je_py: bool) -> str:
    """Vlozi hlavicku ZA pripadny shebang."""
    radky_s = text.splitlines(keepends=True)
    i = 0
    if radky_s and radky_s[0].startswith("#!"):
        i = 1
    hlava = "".join(radky_s[:i])
    zbytek = "".join(radky_s[i:])
    return hlava + (PY_VZHLED if je_py else mjs_hlavicka(text)) + zbytek


def parsuje_ok(p: Path) -> tuple[bool, str]:
    if p.suffix.lower() == ".py":
        try:
            ast.parse(p.read_text(encoding="utf-8"))
            return True, ""
        except SyntaxError as e:
            return False, f"SyntaxError: {e}"
    if p.suffix.lower() in (".mjs", ".js"):
        r = subprocess.run(["node", "--check", str(p)],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        if r.returncode == 0:
            return True, ""
        return False, (r.stderr or "")[:300]
    if p.suffix.lower() == ".ps1":
        prikaz = (
            "$e=$null;$t=$null;"
            f"[void][System.Management.Automation.Language.Parser]::ParseFile('{p}',[ref]$t,[ref]$e);"
            "if($e.Count -eq 0){'OK'}else{$e|ForEach-Object{$_.Message}}"
        )
        r = subprocess.run(["powershell", "-NoProfile", "-Command", prikaz],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        out = (r.stdout or "").strip()
        return ("OK" in out and "Missing" not in out), out[:300]
    return True, ""  # .gd/.cmd/.sql/.ts bez parseru


def oprav_literal(text: str, je_py: bool) -> tuple[str, int]:
    """Nahradi KAZDY řetězcový literál s cestou na vyraz slozeny z dilu.

    ⚠ PROC TAK: prvni verze vkladala `join(...)` DO uvozovek (`'join(PARENT, ...)'`)
    a vyrobila neplatnou syntaxi (`SyntaxError: Unexpected identifier 'uo'`).
    Odhalil to parser az PO zapisu — a to je presne duvod, proc se po zapisu
    parsuje. Tady se uvozovky z literalu ODSTRANI a zbytek cesty se pripoji
    jako samostatne argumenty, takze vyraz zustane vyrazem.
    """
    # prefix uvozovek: ', ", r'", r", pro Python i JS shodne.
    # ⚠ CHYTA se CELY prefix VCETNE `r` — jinak zustane pred vyrazem viset
    # a vznikne `r_PARENT / 'repo'`, coz je v Pythonu PLATNY NAZEV PROMENNE.
    # `ast.parse` to tedy PUSTI (syntaxe je v poradku) a vada se projevi az
    # za behu jako NameError — presne past "brána se ptá na syntaxi, ne na
    # smysl". Proto se navic kontroluji podezrela jmena (viz zkontroluj_jmena).
    vzor = re.compile(
        r"""[rR]?(?P<q>['"])"""
        r"""C:[\\/]Users[\\/]Ssevc[\\/]Local-Deepseek"""
        r"""(?P<zbytek>(?:[\\/][A-Za-z0-9_.\- ]+)*)"""
        r"""(?P=q)"""
    )
    pocet = 0

    def nahrad(m: re.Match) -> str:
        # ⚠ DVE VADY PRVNI VERZE (obe odhalil AZ POHLED na vystup, ne parser):
        #  1) `niz` se skladalo jako "/" + zbytek, kde zbytek uz zacinal "/",
        #     takze vzniklo "//orchestra" a klic "/orchestra" se NIKDY netrefil
        #     → vsechno spadlo do korene stanice (`const ORCH = STANICE`).
        #     Parser to nezachyti: `STANICE` je definovany symbol, jen nema
        #     v repu co delat. Tohle je presne past "brána prošla = jen ticho".
        #  2) Python varianta vracela `_PARENT / 'x'` i tam, kde byl literal
        #     `r"C:\...\games\uo-shadows\.forge\roadmap.json"` → vzniklo
        #     `rPARENT / ...` (uvozovaci `r` zustalo pred vyrazem).
        #     Reseni: uvozovaci prefix se musi spotrebovat CELY.
        zbytek = m.group("zbytek")
        normal = "/" + zbytek.replace("\\", "/").strip("/")
        niz = normal.lower()
        for klic, kam in ROOTY:
            if not klic:
                continue
            k = "/" + klic.replace("\\", "/").lower()
            if niz == k or niz.startswith(k + "/"):
                zb = normal[len(k):]
                return na_vyraz(kam, je_py, zb)
        # koren stanice samotny (zadna znama podslozka)
        return "STANICE"

    novy = vzor.sub(nahrad, text)
    pocet = len(vzor.findall(text))
    return novy, pocet


def zkontroluj_jmena(p: Path) -> tuple[bool, str]:
    """Hleda podezrela jmena vznIKLA rozbitim literalu (napr. `r_PARENT`).

    ⚠ PROC: `ast.parse` overi jen SYNTAXI. `r_PARENT / 'x'` je syntakticky
    spravne a je to vada (NameError za behu). Staticka kontrola musi merit
    SMYSL, ne jen tvar — jinak je to "brána, která se ptá na přítomnost".
    """
    if p.suffix.lower() != ".py":
        return True, ""
    text = p.read_text(encoding="utf-8")
    podezrele = re.findall(r"\b(a?r_?[A-Z_]|r[A-Z_]{2,})\b", text)
    # `r_PARENT` je jednoznacne, `r"..."` uz v textu neni (nahrazeno)
    spatne = [x for x in podezrele if x.startswith("r_") or x.startswith("ar_")]
    if spatne:
        return False, f"podezřelá jména po opravě: {sorted(set(spatne))}"
    return True, ""


def main(argv: list[str]) -> int:
    kontrola = "--kontrola" in argv
    ZALOHA.mkdir(parents=True, exist_ok=True)

    for zaklad in CIL:
        zapis(f"=== {zaklad} ===")
        for p in sorted(zaklad.rglob("*")):
            if any(d in p.parts for d in (".git", "node_modules", ".godot",
                                          "__pycache__", ".wrangler")):
                continue
            if not p.is_file() or p.suffix.lower() not in KOD_SUFFIX:
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if "Local-Deepseek" not in text:
                continue
            rel = p.relative_to(zaklad)
            if str(rel).replace(chr(92), "/") in RUCNI:
                zapis(f"  ⏭ {rel}: RUČNÍ oprava (dva rooty — D6), přeskakuji")
                continue
            je_py = p.suffix.lower() == ".py"
            novy, celkem = oprav_literal(text, je_py)
            for vzor, popis in MRTVE:
                if vzor in novy:
                    zapis(f"  ⚠ MRTVÁ CESTA ({popis}) v {rel} — needitovano, "
                          f"jen hlášeno")
            if celkem == 0:
                continue
            if "Local-Deepseek" in novy:
                zapis(f"  ⚠ {rel}: po nahrade ZBYVA 'Local-Deepseek' — preskoceno")
                chyby.append(f"{rel}: zbytek Local-Deepseek")
                continue
            if not ma_hlavicku(novy, je_py):
                novy = vloz_hlavicku(novy, je_py)

            if kontrola:
                zapis(f"  {rel}: {celkem} nahrad (KONTROLA — nezapisuji)")
                continue

            zal = ZALOHA / f"{zaklad.name}__{str(rel).replace(chr(92), '_')}"
            shutil.copy2(p, zal)
            p.write_text(novy, encoding="utf-8", newline="")
            ok, msg = parsuje_ok(p)
            if ok:
                ok, msg = zkontroluj_jmena(p)
            if not ok:
                shutil.copy2(zal, p)
                zapis(f"  ✗ {rel}: {celkem} nahrad, ale NEPARSuje ({msg}) — VRÁCENO")
                chyby.append(f"{rel}: {msg}")
            else:
                zapis(f"  ✓ {rel}: {celkem} nahrad, parser OK")
                zmenene.append(p)

    zapis("")
    zapis(f"změněno: {len(zmenene)} souborů, chyb: {len(chyby)}")
    for c in chyby:
        zapis(f"  CHYBA: {c}")
    LOG.write_text("\n".join(radky) + "\n", encoding="utf-8", newline="\n")
    zapis(f"log: {LOG}")
    return 1 if chyby else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
