# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
r"""Mutační test `n8-zastarala-analyza.py` — měří ten skript, nebo jen počítá vzorce?

Skript porovnává 7 tvrzení analýzy s KÓDEM. „5 zastaralých ze 7" je číslo,
které může být špatně dvěma způsoby: skript je slepý, nebo počítá špatně.

Hledají se DVĚ VADY, které tenhle typ kontroly mívá:
  (a) FALEŠNÝ POPLACH — kontroluje se PŘÍTOMNOST řetězce, ne jeho funkce.
      Tvrzení 4 (`awaiting_human`) se ptá, jestli je řetězec v kódu. Když se
      stav v zápisu do D1 přejmenuje na `pending_review`, je tvrzení LOGICKY
      DÁL ZASTARALÉ (rozhoduje `ok && merged`) — a skript to musí poznat.
  (b) FALEŠNÉ „V POŘÁDKU" — když se přejmenuje funkce, ale volání zůstane,
      kód je ROZBITÝ; skript ale hledá jen jméno, takže tvrzení 3 prohlásí
      za aktuální.

POZOR (naměřeno 2. 10. 2026, stálo to půl hodiny): vzory se MUSÍ escapovat.
`re.compile("if (ok && merged) {")` hledá `if ok && merged {` — závorky jsou
skupina, ne literál. Skripty projektu to dělají správně (`r"if\s*\(\s*ok..."`),
tenhle harness to nejdřív nedělal a hlásil „vzor 0x" u textu, který v souboru
prokazatelně byl.

Spusteni:  $env:PYTHONIOENCODING='utf-8'; python _analyza\n8-mutace.py
"""
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(_STANICE)
INDEX = WS / "conductor" / "src" / "index.ts"
SKRIPT = WS / "_analyza" / "n8-zastarala-analyza.py"


def spust():
    r = subprocess.run([sys.executable, str(SKRIPT)],
                       capture_output=True, text=True, encoding="utf-8")
    out = r.stdout or ""
    m = re.search(r"zastaralých tvrzení:\s*(\d+)\s*z\s*(\d+)", out)
    # MNOŽINA zastaralých tvrzení (ne jen počet) — počet sám je slabá metrika:
    # dvě různé změny ho mohou nechat stejný a přesto změnit, CO je zastaralé.
    # POZOR (naměřeno při psaní): klíč se bere z CELÉHO textu tvrzení, ne z §.
    # Dvě různá tvrzení totiž začínají na `§3.2` (auto-merge a size_lines) —
    # s klíčem `§3.2` by se scvrkla na jednu položku a změnilo by se tím, co
    # test měří.
    zastarale = set()
    aktualni = set()
    for l in out.splitlines():
        cil = None
        if "ZASTARALÉ:" in l:
            cil = zastarale
        elif "OK (aktuální):" in l:
            cil = aktualni
        if cil is None:
            continue
        text = l.split(":", 1)[1].strip() if ":" in l else l.strip()
        cil.add(text[:48])
    return (int(m.group(1)) if m else None), zastarale, aktualni, out


pocet0, zastarale0, aktualni0, _ = spust()
print("=== Mutační test N8 (měří skript kód, nebo počítá vzorce?) ===\n")
print(f"  0) vychozi stav: zastaralých = {pocet0}")
for z in sorted(zastarale0):
    print(f"       ZASTARALE: {z}")
if pocet0 is None:
    print("     CHYBA: nepodarilo se precist pocet z vystupu.")
    sys.exit(2)

index_orig = INDEX.read_bytes()

# (nazev, najdi, nahrad, ocekavana_zmena, co_to_dokazuje)
# `ocekavana_zmena`: "ubyde" = neco se stane AKTUALNIM |
#                    "stejne" = mnozina zastaralych se NESMI zmenit
# Porovnava se MNOZINA, ne pocet: dve různé změny mohou počet nechat stejný
# a přesto změnit, KTERÉ tvrzení je zastaralé.
MUTACE = [
    # OVERENO SPUSTENIM (zaklad: zastarale = 1,2,3,4,5 | aktualni = done_note, artifacts)
    ("vracena vada A1: `ok && merged` -> `ok`",
     r"if \(ok && merged\) \{", "if (ok) {", "ubyde",
     "tvrzeni 1 se stava AKTUALNIM (rozhodnuti je zase jen na `ok`)"),

    ("PAST (a): `awaiting_human` prejmenovan v zapisu do D1",
     r"UPDATE tasks SET status='awaiting_human'",
     "UPDATE tasks SET status='pending_review'", "ubyde",
     "stav `awaiting_human` se uz do D1 NEZAPISUJE -> tvrzeni 4 se stava "
     "AKTUALNIM. TOHLE JE OPRAVA V3: stara verze hledala SLOVO kdekoliv "
     "(komentar, roadmapa) a rozdil nevidela"),

    ("PAST (b): funkce prejmenovana I S VOLANIM (kod je konzistentni)",
     r"filesInOriginMain", "loadMainTree", "ubyde",
     "jmeno v kodu neni -> tvrzeni 3 se stava AKTUALNIM. Kontrola se ptá na "
     "DEKLARACI I VOLANI, takze konzistentni prejmenovani pozna. "
     "POZOR: nahrazuji se VŠECHNY výskyty (deklarace i volani) — jinak by "
     "vzniklo volani neexistujici funkce a testoval by se jiny jev"),
]

selhalo = []          # skript nereagoval spravne = NALEZ O SKRIPTU
nezmutovano = []      # mutaci nešlo provést = NALEZ O TESTOVACIM SKRIPTU
try:
    for i, (nazev, najdi, nahrad, ocekavana_zmena, dokazuje) in enumerate(MUTACE, start=1):
        puvodni = INDEX.read_bytes().decode("utf-8")
        vzor = re.compile(najdi, re.M)
        # `finditer` (ne `findall` — to vraci capture groupy, ne pocet shod)
        pocet_vyskytu = sum(1 for _ in vzor.finditer(puvodni))
        # Nahrazuji se VSECHNY vyskty: u jednoslovneho jmena funkce je to
        # deklarace + volani, a obe se prejmenovat MUSI (jinak je kod rozbity
        # a netestuje se to, co test tvrdi).
        if pocet_vyskytu < 1:
            print(f"  {i}) {nazev}: NEZMUTOVANO (vzor {pocet_vyskytu}x)")
            nezmutovano.append(nazev)
            continue
        novy = vzor.sub(lambda m: nahrad, puvodni)
        assert novy != puvodni, "mutace nezmenila text!"
        INDEX.write_text(novy, encoding="utf-8", newline="")
        pocet, zastarale, aktualni, out = spust()
        # Porovnava se MNOZINA, ne pocet — pocet muze zustat stejny,
        # i kdyz se zmenilo, KTERE tvrzeni je zastarale.
        if ocekavana_zmena == "ubyde":
            ok = zastarale < zastarale0        # neco se stalo AKTUALNIM
            verdikt = ("OK (mnozina se zmensila)" if ok
                       else "NESHODA (melo ubyt, nezmenilo se)")
        else:
            ok = (zastarale == zastarale0)
            verdikt = ("OK (mnozina stejna)" if ok else "NESHODA (mnozina se zmenila)")
        print(f"  {i}) {nazev}")
        print(f"       zastaralých = {pocet} (zaklad {pocet0}) -> {verdikt}")
        print(f"       {dokazuje}")
        print(f"       UBYLO: {sorted(zastarale0 - zastarale) if ok else '(nic)'}")
        print(f"       PRIBILO: {sorted(zastarale - zastarale0) if ok else '(nic)'}")
        if not ok:
            selhalo.append(nazev)
        INDEX.write_bytes(index_orig)
finally:
    INDEX.write_bytes(index_orig)
    assert INDEX.read_bytes() == index_orig, "index.ts nevracen!"

pocet_po, zastarale_po, aktualni_po, _ = spust()
print(f"\n  po vraceni originalu: zastaralých = {pocet_po} (ocekavano {pocet0})")
assert zastarale_po == zastarale0, "original se nevratil do stejneho stavu!"
assert aktualni_po == aktualni0, "original se nevratil do stejneho stavu (aktualni)!"

provedeno = len(MUTACE) - len(nezmutovano)
print()
print(f"  mutaci provedeno : {provedeno} z {len(MUTACE)}")
if selhalo:
    print(f"\nVYSLEDEK: skript nereagoval podle ocekavani v {len(selhalo)} pripadech:")
    for s in selhalo:
        print(f"          - {s}")
    sys.exit(1)
if nezmutovano:
    print(f"\nVYSLEDEK: vsech {provedeno} provedenych mutaci dopadlo podle ocekavani,")
    print(f"          ale {len(nezmutovano)} se neprovedlo — vzory zpresnit.")
    sys.exit(2)
print(f"\nVYSLEDEK: vsech {len(MUTACE)} mutaci dopadlo podle ocekavani.")
sys.exit(0)
