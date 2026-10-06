# -*- coding: utf-8 -*-
r"""P20 — Úkol A: POMOCNÉ MĚŘENÍ pro `OCEKAVANE_NENULOVE`.

OTÁZKA: jaké `exit` kódy umí brána `zadání kontrola` VŮBEC vydat?
To rozhoduje, čím se deklaruje „očekávaně nenulový" stav:
  * kdyby uměla JEN `1`, stačilo by deklarovat JMÉNO brány,
  * kdyby uměla `1` i `0` (podle stavu zadání), musí deklarace nést i KÓD —
    jinak by `g3` nerozlišil „tatáž brána, jiný důvod".

Měří se na SYNTHETICKÝCH zadáních v `_analyza/p20-scratch/`, ne na živém
dokumentu: živé zadání se NEMUTUJE a nemusí se nic commitovat, aby vznikl stav
„kotva = HEAD". Každá fixtura se před spuštěním KONTROLUJE (kdyby se nevyrobila,
měření by lhalo — omyl P20/1).

⚠ Omyl P20/1 (naměřeno tady): první verze hledala kotvu regeXem se zpětným
apostrofem v RAW řetězci. `r"\`"` ale NENÍ escape — zpětný apostrof žádnou
escape sekvenci nemá, takže vzor zůstal dva znaky a nenašel nic. Nahrazení
„prošlo" jen zdánlivě. Hledá se proto PROSTÝM PODŘETĚZCEM.

⚠ Omyl P20/2: druhá verze měnila jen PRVNÍ výskyt kotvy na řádku — ale ten řádek
nese i `origin/main` = **`19a2195`**, takže vzniklo zadání s DVĚMA ROZCHÁZEJÍCÍMI
SE TVRZENÍMI a brána správně hlásila varování. Fixtura musí být CELÁ a vlastní.

Použití: python _analyza/p20-a-kody-bran.py
"""

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
SCRATCH = ANALYZA / "p20-scratch"
GIT = str(WS / "tools" / "git.cmd")
BRANA = ANALYZA / "zadani-kontrola.py"
ZADANI = WS / "NEXT-SESSION-INSTRUKCE.md"
HRA = WS.parent / "uo-shadows"

kontroly = []


def zk(ok: bool, popis: str, detail: str = "") -> None:
    kontroly.append((ok, popis, detail))
    print(f"  {'OK  ' if ok else 'CHYBA'} {popis}" + (f"\n      {detail}" if detail else ""))


def git(repo: pathlib.Path, *args: str) -> str:
    r = subprocess.run([GIT, "-C", str(repo), *args], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       shell=True, timeout=120)
    return (r.stdout or "").strip()


def git_kod(repo: pathlib.Path, *args: str) -> int:
    """Týž git, ale vrací NÁVRATOVÝ KÓD (potřeba pro `merge-base --is-ancestor`).

    ⚠ `shell=True` zůstává (git.cmd je batka) — proto se sem NESMÍ dostat `^`:
    `cmd.exe` ho bere jako escape znak a tiše ho zahodí (skill `dsh-prostredi`
    §5c). Ověření existence commitu se proto dělá přes `cat-file -t`, ne přes
    `rev-parse <sha>^{commit}`.
    """
    r = subprocess.run([GIT, "-C", str(repo), *args], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       shell=True, timeout=120)
    return r.returncode


def spust(nad: pathlib.Path):
    r = subprocess.run([sys.executable, "-B", str(BRANA), "--soubor", str(nad)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(WS), timeout=300)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


# ⚠ OMyl P20/3 (naměřeno tady, a je to past PROSTŘEDÍ, ne logiky): fixtura se
# NESMÍ skládat v `python -c` ANI v here-stringu PowerShellu. Zpětný apostrof je
# v PowerShellu ESCAPE znak, takže z `` `forge-orchestra` `` se stane
# `orge-orchestra` — a brána pak SPRÁVNĚ hlásí „zadání netvrdí žádný commit",
# protože klíč rozbitý je. Vypadá to jako vada brány a je to vada ZÁPISU.
# Fixtura se proto staví tady, v souboru, kde jsou zpětné apostrofy obyčejné znaky.
Q = chr(96)          # zpětný apostrof — nikdy ne doslovně v okolním shellu
NOVE = "\n"


def fixtura(sha_orchestra: str, sha_hra: str, jmeno: str) -> pathlib.Path:
    """Minimální zadání s POCTIVOU hlavičkou (kotva = obojí: HEAD i origin/main)."""
    radek = (
        "**Stav obou repů při psaní:** " + Q + "forge-orchestra" + Q + " = "
        + Q + sha_orchestra + Q + ", " + Q + "origin/main" + Q + " = **"
        + Q + sha_orchestra + Q + "** · " + Q + "uo-shadows" + Q + " = "
        + Q + sha_hra + Q + ", " + Q + "origin/main" + Q + " **shodná**, "
        "strom **čistý**"
    )
    f = SCRATCH / jmeno
    f.write_text("# ZADÁNÍ (fixtura P20/A — měří se na ní chování brány)\n\n"
                 + radek + "\n\nNic se tady neprovádí.\n",
                 encoding="utf-8", newline=NOVE)
    return f


print("=" * 78)
print("P20/A — jaké `exit` umí brána `zadání kontrola`?")
print("=" * 78)

SCRATCH.mkdir(parents=True, exist_ok=True)
# Obsah živého zadání se bere JEDNOU a na konci se porovnává — kdyby ho skript
# omylem přepsal, pozná se to (a fixtury se stavějí z TOHOHLE textu).
zdroj = ZADANI.read_text(encoding="utf-8")
HEAD_WS = git(WS, "rev-parse", "--short", "HEAD")
HEAD_HRA = git(HRA, "rev-parse", "--short", "HEAD")
print(f"\n  živý HEAD orchestra: {HEAD_WS}")
print(f"  živý HEAD hry:       {HEAD_HRA}")

# Kontrola, že kotva v ŽIVÉM zadání je tam, kde ji čekáme (jinak by tvrzení
# o dnešním stavu stálo na neověřeném předpokladu).
# ⚠ OMyl 209 (naměřeno tady): první verze MĚLA KOTVU ZAPSANOU NATVRDO
# (`19a2195`) — a když se zadání přepsalo na nový živý `HEAD`, spadla NA
# SPRÁVNĚ AKTUALIZOVANÉM dokumentu. Je to **tatáž třída jako H102**: doklad
# tvrdící zastaralé číslo. Kotva se proto **VYTAHUJE Z DOKUMENTU**, neopisuje.
_m = re.search(r"Stav obou repů při psaní:.*?`forge-orchestra`\s*=\s*`([0-9a-f]{7,40})`",
               zdroj)
zk(_m is not None,
   "v ŽIVÉM zadání se našla kotva orchestry (čte se z dokumentu, ne z konstanty)",
   "hledám `forge-orchestra` = `<sha>` na řádku se stavem repů")
KOTVA_SHA = _m.group(1) if _m else ""
print(f"  kotva orchestry v zadání: {KOTVA_SHA}   (živý HEAD: {HEAD_WS})")
# ⚠ H107 (P21, 6. 10. 2026): tady stálo `KOTVA_SHA == HEAD_WS` — a ta kontrola
# byla ZELENÁ JEN PROTO, že práce P20 **NEBYLA COMMITNUTÁ**. Zadání se ale píše
# PŘED commitem, takže po každém commitu se rovnost s `HEAD` **NUTNĚ** rozbije —
# ačkoli je zadání v pořádku (kotva pořád ukazuje na commit, na kterém se měřilo).
# Správná otázka tedy není „je kotva dnešní `HEAD`?", ale **„JE KOTVA SKUTEČNÝ
# COMMIT, KTERÝ NENÍ NOVĚJŠÍ NEŽ `HEAD`?"** — přesně to potřebuje `zadani-kontrola.py`,
# aby mohla tvrdit „přibylo commitů: N".
typ = git(WS, "cat-file", "-t", KOTVA_SHA) if KOTVA_SHA else ""
zk(typ == "commit",
   "kotva zadání je SKUTEČNÝ commit v repu",
   f"git cat-file -t {KOTVA_SHA} → {typ or '(nic)'}")
_kotva_neni_novejsi = bool(KOTVA_SHA) and (
    KOTVA_SHA == HEAD_WS
    or git_kod(WS, "merge-base", "--is-ancestor", KOTVA_SHA, "HEAD") == 0)
zk(_kotva_neni_novejsi,
   "kotva zadání není NOVĚJŠÍ než živý HEAD (je to předek, nebo sám HEAD)",
   f"kotva={KOTVA_SHA} HEAD={HEAD_WS}")

pripady = [
    ("kotva = ŽIVÝ HEAD (obojí)", HEAD_WS, HEAD_HRA, 0),
    ("kotva = NEDOSTUPNÝ commit", "deadbee", HEAD_HRA, 1),
]
for popis, sha_ws, sha_hra, ocekavany in pripady:
    f = fixtura(sha_ws, sha_hra, f"fixtura-{sha_ws}.md")
    text = f.read_text(encoding="utf-8")
    # ⚠ Fixtura se KONTROLUJE: kdyby se nevyrobila, měřilo by se něco jiného.
    # (Omyl P20/3: rozbitý zápis fixtury vypadal jako vada BRÁNY.)
    zk(text.count(Q + sha_ws + Q) == 2,
       f"{popis}: fixtura tvrdí kotvu DVAKRÁT (HEAD i origin/main) — bez rozporu",
       f"výskytů {Q+sha_ws+Q}: {text.count(Q + sha_ws + Q)}")
    kod, vystup = spust(f)
    zmin = [l.strip() for l in vystup.splitlines() if "VÝSLEDEK" in l]
    varov = [l.strip() for l in vystup.splitlines() if l.strip().startswith("⚠")]
    print(f"    {popis}: exit={kod}   {zmin[-1] if zmin else ''}")
    for v in varov:
        print(f"        {v[:130]}")
    zk(kod == ocekavany, f"{popis} → exit {ocekavany}", f"naměřeno exit={kod}")

for f in SCRATCH.glob("fixtura-*.md"):
    f.unlink()
zk(not list(SCRATCH.glob("fixtura-*.md")), "fixtury uklizeny")
zk(ZADANI.read_text(encoding="utf-8") == zdroj, "ŽIVÉ zadání je bajt na bajt nezměněné")

chyb = sum(1 for ok, _, _ in kontroly if not ok)
print("\n" + "=" * 78)
print(f"VÝSLEDEK: {len(kontroly)} kontrol, {chyb} chyb")
for ok, popis, d in kontroly:
    if not ok:
        print(f"   CHYBA {popis}  [{d}]")
print("=" * 78)
sys.exit(1 if chyb else 0)
