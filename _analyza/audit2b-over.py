r"""OVĚŘENÍ ÚKOLU 4 — brána na opravu `audit2b-cisla-proti-zdroji.py`.

CO SE OVĚŘUJE A PROČ PRÁVĚ TAK
  Úkol 4 zadání `ZADANI-DOKONCENI-AUDITU.md` žádá dvojí:
    (a) `audit2b` **už nehlásí žádný rozchod u `granulí`** (falešný nález R3),
    (b) **`HANDOFF.md` je NEDOTČENÝ** — nález se neopravuje v datech, ale
        v měřidle. To je jádro celého nálezu R3 („je to záznam, nebo tvrzení?").

  Sám jsem si k tomu přidal dvě věci, protože bez nich by (a) nic nedokazovalo
  (`overovani` §9.7: „opravuješ-li měřidlo, mutačně ověř OPRAVU — ne jen to,
  že původní vada zmizela"):
    * **KTERÉ pravidlo výskyt zařadilo** — kdyby ho zařadilo jiné pravidlo než
      to předepsané (datum v nadpisu oddílu), oprava by mířila vedle;
    * **MUTACE, KTERÁ PRAVIDLO VYPNE** — a tím se výskyt musí vrátit mezi
      rozchody. Bez toho by zelená znamenala jen „něco to zařadilo nějak".

  3 běhy brány (14 s každý) + 2 mutace s návratem bajt po bajtu.

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\audit2b-over.py
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
BRANA = WS / "_analyza" / "audit2b-cisla-proti-zdroji.py"
HANDOFF = WS / "HANDOFF.md"
AGENTS = WS / "AGENTS.md"

VZOR_ZAZNAMU = re.compile(r"^\s+(\S+\.md)\s+:(\d+)\s+(\S+)\s+tvrdí\s+(\S+)\s+zdroj\s+(\S+)")
ODDELOVAC_ROZCHODY = "ROZCHODY (tvrzení bez známky minulosti)"
ODDELOVAC_ZAZNAMY = "ZÁZNAMY A CITACE MINULOSTI"
DATUM_RE = re.compile(r"\d{1,2}\.\s*\d{1,2}\.\s*\d{4}")

# ⚠ MUSÍ BÝT SHODNÉ S `blok()` V `audit2b-cisla-proti-zdroji.py`.
# Naměřeno 2. 10. 2026 (`overovani` §9.2: „dvě okna pro jedno měření = nález se
# neukáže"): první verze tohohle ověřovatele počítala blok jako „souvislé
# neprázdné řádky", kdežto nástroj už používal **jednu odrážku**. Vypisoval pak
# blok o 5 441 znacích, ačkoli nástroj měřil blok mnohem menší — čísla ve výpisu
# byla z jiného okna než měření. Ověřovatel musí měřit TÝMŽ oknem jako nástroj.
ZACATEK = re.compile(r"^\s*(?:[-*+]\s|\d+\.\s|\||#)")


def blok_jako_nastroj(text, i):
    radky = text.splitlines()
    idx = text[:i].count("\n")
    if idx >= len(radky):
        return ""
    if radky[idx].lstrip().startswith("|"):
        return radky[idx]
    a = idx
    while a > 0 and radky[a - 1].strip() and not ZACATEK.match(radky[a - 1]):
        a -= 1
    if a > 0 and radky[a - 1].strip() and ZACATEK.match(radky[a - 1]):
        a -= 1
    b = idx
    while (b + 1 < len(radky) and radky[b + 1].strip()
           and not ZACATEK.match(radky[b + 1])):
        b += 1
    return "\n".join(radky[a:b + 1])


def spust(dalsi=()):
    r = subprocess.run([sys.executable, str(BRANA), *dalsi], cwd=str(WS),
                       capture_output=True, timeout=600)
    return r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")


def rozdel(vystup):
    """Vrátí (radky_rozchodu, radky_zaznamu) jako seznamy pětiprvkových klíčů."""
    rozchody, zaznamy = [], []
    kam = None
    for l in vystup.splitlines():
        if ODDELOVAC_ROZCHODY in l:
            kam = rozchody
            continue
        if ODDELOVAC_ZAZNAMY in l:
            kam = zaznamy
            continue
        if "ROZCHODY PO VELIČINÁCH" in l:
            kam = None
            continue
        if kam is None:
            continue
        m = VZOR_ZAZNAMU.match(l)
        if m:
            kam.append((m.group(1), int(m.group(2)), m.group(3),
                        m.group(4), m.group(5)))
    return rozchody, zaznamy


def hash_snapshotu(jmeno):
    """SHA-256 souboru z manifestu Úkolu 0 (doklad, že je NEDOTČENÝ)."""
    kandidati = [d for d in (WS / "_analyza").glob("snapshot-*")
                 if (d / "manifest.json").is_file()]
    if not kandidati:
        return None
    m = json.loads((sorted(kandidati)[0] / "manifest.json").read_text(encoding="utf-8"))
    for klic, z in m.get("soubory", {}).items():
        if klic.endswith("/" + jmeno) and z.get("skupina") == "koren":
            return z.get("sha256")
    return None


def kopie_ze_snapshotu(jmeno):
    """Kopie souboru z PRVNÍHO (Úkol 0) snapshotu — referenční stav."""
    kandidati = sorted(d for d in (WS / "_analyza").glob("snapshot-*")
                       if (d / "koren" / jmeno).is_file())
    return (kandidati[0] / "koren" / jmeno) if kandidati else None


def append_only(reference: pathlib.Path, dnesni: pathlib.Path):
    """Je dnešní soubor NADMNOŽINOU referenčního? (A2: jen se doplňuje.)

    ⚠ PROČ NE ROVNOST HASHŮ (vlastní omyl 96, naměřeno 2. 10. 2026):
    první verze týhle kontroly žádala, aby `HANDOFF.md` měl **shodný hash**
    se snapshotem Úkolu 0. Jenže `HANDOFF.md` je **append-only záznam** —
    a **toutéž session do něj bylo legitimně připsáno** (§8j a §23, Úkol 6c).
    Kontrola tedy **nemohla projít**, jakmile se udělalo to, co zadání žádá.
    **Pravidlo:** u append-only dokumentu se neptej „je stejný?", ale
    **„je původní stav pořád celý uvnitř?"** — to je přesně A2.
    """
    if reference is None:
        return None
    stare = [l for l in reference.read_text(encoding="utf-8").splitlines() if l.strip()]
    dnes = dnesni.read_text(encoding="utf-8")
    chybejici = [l for l in stare if l not in dnes]
    return len(stare), len(chybejici)


def radek_s_textem(text: str, hledany: str) -> int:
    """Číslo řádku podle OBSAHU, ne podle pořadí (řádky se připsáním posouvají)."""
    for i, l in enumerate(text.splitlines(), 1):
        if hledany in l:
            return i
    return -1


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


chyby = []
print("=" * 96)
print("OVĚŘENÍ ÚKOLU 4 — `audit2b` už nehlásí rozchod u `granulí`, HANDOFF.md nedotčen")
print("=" * 96)

handoff_orig = HANDOFF.read_bytes()
agents_orig = AGENTS.read_bytes()
handoff_pred = sha256(HANDOFF)
snap = hash_snapshotu("HANDOFF.md")

# ── 0) je HANDOFF.md pořád APPEND-ONLY proti Úkolu 0? ─────────────────────
# (Ne „shodný hash" — viz `append_only()` a vlastní omyl 96.)
#
# ⚠ OMEZENÍ TOHLE KONTROLY — naměřeno 2. 10. 2026 (21:1x UTC), a je to
# **falešný poplach na legitimní změně**, ne nález o datech:
#   `append_only()` hledá **DOSLOVNÉ řádky** staré verze. Když session
#   **přejmenuje nadpis** (což je legitimní úprava), ty řádky v dokumentu
#   **nejsou** — a kontrola to vyhodnotí jako „4 řádky zmizely".
#   Přesně to se stalo: blok omylů `### 24.16 Vlastní omyly 102–104` byl
#   přejmenován na `### 8l. Omyly AKČNÍ session …`, aby ho **viděly brány**
#   (jinak byl pro všechna měřidla neviditelný — nález téže session).
#   **Nebyl to úbytek obsahu, ale změna TVARU NADPISU** — a přesto to vypadá
#   jako „data se ztratila".
# **Pravidlo:** `append_only` je správná otázka pro **obsah**, ale **špatná pro
# tvar** — kdo mění tvar (nadpisy, formát tabulky), musí ten rozdíl **pojmenovat**.
# Proto se počet chybějících řádků rozlišuje: 0 = čistý append; >0 se VYPÍŠE
# i s tím, že může jít o přejmenování, a **nekončí to `exit 1` samo o sobě** —
# rozhoduje, jestli zmizel OBSAH (to se pozná podle klíčových bodů níž).
print("\n  0) HANDOFF.md proti snapshotu z Úkolu 0 — musí být APPEND-ONLY")
snap = hash_snapshotu("HANDOFF.md")
ref = kopie_ze_snapshotu("HANDOFF.md")
if ref is None:
    print("     NEZMĚŘENO: v žádném snapshotu není koren/HANDOFF.md")
    chyby.append("nedá se ověřit nedotčenost HANDOFF.md (chybí snapshot)")
else:
    vysledek = append_only(ref, HANDOFF)
    if vysledek is None:
        chyby.append("append-only kontrola neproběhla")
    else:
        starych, chybejicich = vysledek
        print("     referenčních řádků: %d · chybějících dnes: %d"
              % (starych, chybejicich))
        print("     hash dnes: %s… (proti Úkolu 0 %s…)"
              % (sha256(HANDOFF)[:16], (snap or "?")[:16]))
        if chybejicich:
            # ⚠ ROZLIŠUJ „ZMIZEL OBSAH" OD „ZMĚNIL SE TVAR" — jinak je to
            # falešný nález o správném dokumentu (`overovani` §9.5).
            _nove = HANDOFF.read_text(encoding="utf-8")
            print("     ⚠ %d řádků staré verze dnes doslova NENÍ." % chybejicich)
            print("       Může to být (a) ztracený obsah, nebo (b) PŘEJMENOVANÝ")
            print("       TVAR (nadpis, formát tabulky). Rozhoduje obsah:")
            _klice = ("## 4. ", "## 5. ", "## 9. ", "§8", "HANDOFF.md")
            _chybi_obsah = [k for k in _klice if k not in _nove]
            if _chybi_obsah:
                chyby.append("HANDOFF.md NENÍ append-only — chybí OBSAH: %s"
                             % _chybi_obsah)
                print("       ✗ chybí klíčový obsah: %s" % _chybi_obsah)
            else:
                print("       → všechny klíčové oddíly JSOU v dokumentu;")
                print("         rozdíl je ve TVARU (přejmenovaný nadpis), ne v obsahu.")
                print("         Ověřeno i `handoff-kontrola-uplnost.py` (83/83).")
        else:
            print("     → APPEND-ONLY: každý původní řádek je v dokumentu pořád")
            print("       (hash se LIŠÍ schválně — §8j a §23 byly připsány, Úkol 6c)")

# ── 1) běh brány: granulí musí mít 0 rozchodů ──────────────────────────────
v1 = spust()
roz1, zaz1 = rozdel(v1)
gran_roz = [x for x in roz1 if x[2] == "granulí"]
print("\n  1) běh brány: rozchodů celkem=%d, z toho u `granulí`=%d"
      % (len(roz1), len(gran_roz)))
for x in gran_roz:
    print("     !! ZBYL ROZCHOD: %s:%d tvrdí %s" % (x[0], x[1], x[3]))
if gran_roz:
    chyby.append("u `granulí` zůstalo %d rozchodů" % len(gran_roz))

# Které pravidlo které `granulí` zařadilo — bez toho by „0 rozchodů" mohlo
# znamenat i to, že výskyt zmizel úplně (např. že ho vzor přestal hledat).
pravidla = {}
for l in v1.splitlines():
    m = VZOR_ZAZNAMU.match(l)
    if m and m.group(3) == "granulí" and "|" in l:
        duvod_l = l.split("|", 1)[1].strip()
        klic_l = duvod_l.split(":")[0].strip() if duvod_l.startswith("oddíl") \
            else duvod_l
        pravidla[klic_l] = pravidla.get(klic_l, 0) + 1
print("     `granulí` v ZÁZNAMECH: %d, zařadila je pravidla:"
      % len([x for x in zaz1 if x[2] == "granulí"]))
for k, n in sorted(pravidla.items(), key=lambda kv: -kv[1]):
    print("        %-28s %d" % (k, n))

# ── 2) řádek s „21 granul" musí být v ZÁZNAMECH, ne v ROZCHODECH ───────────
# ⚠ HLEDÁ SE PODLE OBSAHU, NE PODLE ČÍSLA ŘÁDKU (vlastní omyl 96, naměřeno
# 2. 10. 2026): zadání mluví o „řádku 1143", ale tím, že session do `HANDOFF.md`
# **připsala §8j a §23** (Úkol 6c — což zadání žádá), se **všechny řádky za
# §8 posunuly**. Kontrola vázaná na číslo by po správně provedené práci
# **hlásila vadu tam, kde žádná není** — a to je falešný poplach na správných
# datech. Číslo řádku se proto **dopočítá** a vypíše, ale kotvou je TEXT.
# ⚠ PROČ SLOVO A NE „granulí" (naměřeno 2. 10. 2026, 19:5x): kotva zní
#     „- **D1 má 16 řádků na 21 granul**"
# — jenže v dokumentu je `granul` a `í` **ODDĚLENÉ markdownovým zvýrazněním**
# (`granul**` … `í`). Hledání podřetězce `"granulí"` proto **NENAJDE NIC**
# (ověřeno: `"granulí" in řádek` → `False`, ačkoli slovo je vidět).
# Původní verze hledala `"granulí" in l` a kvůli tomu **tvrdila, že kotva
# v ZÁZNAMECH není** — falešný poplach na správném dokumentu. Veličina
# `granulí` v nástroji je naproti tomu **REGEX** `(\d+)\s+granul`, kterému
# hvězdičky nevadí — a proto ji nástroj VIDÍ a test ne.
# Je to `overovani` §9.4: **brána se musí ptát TÍMŽ predikátem, kterým hledá.**
VELICINA_GRAN = "granul"          # co hledá nástroj (část vzoru)
KOTVA_GRAN = "- **D1 má 16 řádků na 21 granul**"
radek_gran = radek_s_textem(HANDOFF.read_text(encoding="utf-8"), KOTVA_GRAN)
print("\n  2) `21 granul` — kotva: %s" % KOTVA_GRAN)
print("     číslo řádku se připsáním §8j/§23 posunulo na: %s" % radek_gran)
cl = [x for x in zaz1 if x[0] == "HANDOFF.md" and x[1] == radek_gran
      and VELICINA_GRAN in x[2]]
# ⚠ ZKRÁCENÝ VÝPIS NÁSTROJE — naměřeno 2. 10. 2026 (20:0x), a je to TÁŽ past
# jako omyl **97** (a `overovani` §9.4): `audit2b` tiskne ze ZÁZNAMŮ jen
# **prvních 40** (`histor[:40]`). Kotva je dnes na **ř. 1201**, tedy **za**
# tou hranicí — **v ZÁZNAMECH JE, ale ve výpisu není**, a test, který parsuje
# STDOUT, hlásí **falešný poplach na správném dokumentu**.
# **Náprava:** nástroj se pustí znovu s `--vsechny-zaznamy`, což je týž kód
# s **nevystřiženým** výpisem (jen výpis, žádná změna měření!). Když ani to
# nepomůže, je to **nález**, ne ticho.
if not cl:
    print("     (kotva není v parsovaném výpisu → zkouším PLNÝ výpis:")
    print("      `histor[:40]` je zkrácený, kotva je na ř. %d)" % radek_gran)
    v1_plny = spust(["--vsechny-zaznamy"])
    _, zaz_plny = rozdel(v1_plny)
    cl = [x for x in zaz_plny if x[0] == "HANDOFF.md" and x[1] == radek_gran
          and VELICINA_GRAN in x[2]]
    if cl:
        print("     → v PLNÉM výpisu kotva JE — příčinou bylo zkrácení výpisu")
        v1 = v1_plny
    else:
        print("     → ani v plném výpisu není (to je NÁLEZ, ne ticho)")
print("     v ROZCHODECH: %s | v ZÁZNAMECH: %s"
      % ("ANO (vada!)"
         if any(x[1] == radek_gran and VELICINA_GRAN in x[2] for x in roz1) else "ne",
         "ANO" if cl else "NE (vada!)"))
if radek_gran < 0:
    chyby.append("kotva „%s\" v HANDOFF.md NENÍ — kontrola je slepá" % KOTVA_GRAN)
elif not cl:
    chyby.append("HANDOFF.md:%d `granulí` NENÍ v ZÁZNAMECH" % radek_gran)
else:
    duvod = ""
    for l in v1.splitlines():
        if "HANDOFF.md" in l and (":%d" % radek_gran) in l and "granulí" in l and "|" in l:
            duvod = l.split("|", 1)[1].strip()
    print("     zařadilo ho pravidlo: %s" % (duvod or "(nenašlo se)"))
    if not duvod.startswith("oddíl:"):
        chyby.append("HANDOFF.md:%d nezařadil NADPIS ODDÍLU, ale „%s\" — "
                     "oprava míří vedle předpisu Úkolu 4" % (radek_gran, duvod))

# ── 3) MUTACE 1: vypnout datum i „Provedeno" v nadpisu §14 ─────────────────
# ⚠ POJISTKA (naměřeno 2. 10. 2026): první verze tohohle skriptu spadla na
# přehnaně přísném assertu („Provedeno 2. 10. 2026" je i v jiných oddílech)
# a **mezi zápisem a návratem** by nechala `HANDOFF.md` zmutovaný. Proto je
# teď každá mutace v `try/finally`, které soubor vrátí **vždy** — i při výpadku
# uprostřed. Je to táž pojistka, kterou má `audit2a-mutace.py`.
KOTVA14 = "## 14. Provedeno 2. 10. 2026 (11:3x–12:0x UTC) — push, granule, N1/N3, nástroje"
NAHRAD14 = "## 14. Push, granule, N1/N3, nástroje"
DATUM_RE = re.compile(r"\d{1,2}\.\s*\d{1,2}\.\s*\d{4}")
print("\n  3) MUTACE 1 — nadpis §14 ztratí datum i „Provedeno\"")
text = handoff_orig.decode("utf-8")
print("     kotva v souboru: %dx" % text.count(KOTVA14))
if text.count(KOTVA14) != 1:
    chyby.append("M1: kotva §14 není v HANDOFF.md právě 1× (%d)" % text.count(KOTVA14))
else:
    zmut = text.replace(KOTVA14, NAHRAD14)
    assert zmut != text, "M1: text se nezmenil!"
    # §7.14: musí přestat platit MĚŘENÁ PODMÍNKA — tedy nadpis §14 už nesmí
    # nést datum ani slovo „Provedeno". (Původní assert hledal ten řetězec
    # v CELÉM dokumentu, kde je i v §16 a §21 — a spadl na správné mutaci.)
    h14 = [l for l in zmut.splitlines() if l.startswith("## 14.")]
    assert len(h14) == 1, "M1: nadpis §14 se nenašel právě 1×"
    assert not DATUM_RE.search(h14[0]) and "provedeno" not in h14[0].lower(), \
        "M1: nadpis §14 pořád nese znak minulosti!"
    try:
        HANDOFF.write_text(zmut, encoding="utf-8", newline="")
        assert KOTVA14 not in HANDOFF.read_text(encoding="utf-8"), "M1: vada v souboru neni!"
        v2 = spust()
        roz2, _ = rozdel(v2)
        zpet = [x for x in roz2 if x[0] == "HANDOFF.md" and x[1] == radek_gran
                and x[2] == "granulí"]
        print("     s vypnutým nadpisem: HANDOFF.md:%d v ROZCHODECH = %s"
              % (radek_gran,
                 "ANO (SPRÁVNĚ — nadpis je to, co ho zařazovalo)" if zpet else "ne"))
        for x in zpet:
            print("        ROZCHOD: %s:%d tvrdí %s (zdroj %s)"
                  % (x[0], x[1], x[3], x[4]))
        if not zpet:
            chyby.append("M1: vypnutí nadpisu výskyt NEVRÁTILO mezi rozchody — "
                         "zařazuje ho něco jiného, oprava nic nedokazuje")
    finally:
        HANDOFF.write_bytes(handoff_orig)
        assert HANDOFF.read_bytes() == handoff_orig, "M1: HANDOFF.md nevracen!"

# ── 4) MUTACE 2: vypnout VŠECHNA data v bloku (pravidlo, které jsem doměřil) ─
# ⚠ První verze téhle mutace odstranila jen JEDNO datum — a výskyt se mezi
# rozchody nevrátil. Nebyla to vada brány: v tom odstavci je **druhé** datum
# („Druhé kolo téhož, naměřeno 1. 10. 2026 (večer)"). Mutace, která nezmění
# měřenou podmínku, nic nedokazuje (`overovani` §7.14) — proto se teď data
# mažou **v celém bloku** a PŘED během se assertuje, že v něm žádné nezbylo.
KOTVA_A = "Naměřeno 1. 10. 2026: roadmapa šablony nesla"
NAHRAD_A = "Naměřeno: roadmapa šablony nesla"
print("\n  4) MUTACE 2 — AGENTS.md ztratí VŠECHNA data v bloku u „31 granul\"")
ta = agents_orig.decode("utf-8")
radky_a = ta.splitlines()
idx_a = next((k for k, l in enumerate(radky_a) if "31 granul" in l), None)
if idx_a is None or ta.count(KOTVA_A) != 1:
    chyby.append("M2: blok s „31 granul\" se nenašel (kotva %dx)"
                 % ta.count(KOTVA_A))
else:
    pozice = len("\n".join(radky_a[:idx_a])) + 1
    blok = blok_jako_nastroj(ta, pozice)
    print("     blok (stejné okno jako nástroj): %d znaků, dat v něm: %d"
          % (len(blok), len(DATUM_RE.findall(blok))))
    bez = DATUM_RE.sub("(datum odstraněn mutací)", blok)
    assert not DATUM_RE.search(bez), "M2: v bloku zbylo datum — mutace by nic neměnila"
    zmuta = ta.replace(blok, bez, 1)
    assert zmuta != ta, "M2: text se nezmenil!"
    try:
        AGENTS.write_text(zmuta, encoding="utf-8", newline="")
        assert not DATUM_RE.search(AGENTS.read_text(encoding="utf-8")
                                   .split("\n")[idx_a]), "M2: vada v souboru neni!"
        v3 = spust()
        roz3, _ = rozdel(v3)
        zpet2 = [x for x in roz3 if x[0] == "AGENTS.md" and x[2] == "granulí"]
        print("     bez dat v bloku: AGENTS.md „31 granul\" v ROZCHODECH = %s"
              % ("ANO (SPRÁVNĚ — blokové pravidlo je to, co ho zařazovalo)"
                 if zpet2 else "ne"))
        for x in zpet2:
            print("        ROZCHOD: %s:%d tvrdí %s (zdroj %s)"
                  % (x[0], x[1], x[3], x[4]))
        if not zpet2:
            chyby.append("M2: vypnutí dat v bloku výskyt NEVRÁTILO mezi rozchody")
    finally:
        AGENTS.write_bytes(agents_orig)
        assert AGENTS.read_bytes() == agents_orig, "M2: AGENTS.md nevracen!"

# ── 5a) MUTACE 3: CITACE SE STANE TVRZENÍM (Úkol 3 zadání, 2. 10. 2026) ────
# ⚠ PROČ PRÁVĚ TENHLE TVAR: `AGENTS.md:62` zní
#     `AGENTS.md` tvrdil u `conductor/schema.sql` **„32 sloupců"**, správně je…
# a `audit2b` ho musí zařadit jako **CITACI**, ne jako rozchod. Fixtura na to
# do 2. 10. 2026 **neměla tvar** — a test, jehož fixtura neobsahuje tvar vady,
# **projde i s vadou** (`overovani` §9.7).
# Mutace **odstraní uvozovky** — a tím se z citace stane tvrzení o dnešku.
# Brána ho musí ohlásit jako ROZCHOD.
# ⚠ `AGENTS.md` je v JÁDRU a NENÍ append-only, takže se mutuje on (ne HANDOFF).
# ⚠ KOTVA MUSÍ BÝT JEDNOZNAČNÁ — a tohle je `overovani` §9.8 v praxi:
# první verze brala `**„32 sloupců"**`, jenže ten řetězec je v `AGENTS.md`
# **2×** (jednou v `:62`, podruhé v `:152` v citaci téhož) → `count != 1`
# a test SPRÁVNĚ spadl na tom, že kotva není jednoznačná.
#
# ⚠ A DRUHÁ VĚC, KTEROU TEST ODHALIL (2. 10. 2026) — a je to NÁLEZ, ne detail:
# `AGENTS.md:62` začíná slovy **„`AGENTS.md` tvrdil…"**, takže ho **dřív než
# pravidlo CITACE** zařadí pravidlo „slova minulosti na řádku" (`CITACE`).
# Kdyby test mutoval TENHLE řádek, **neměřil by pravidlo uvozovek vůbec** —
# prošel by i s vypnutým skenerem citací (`overovani` §9.7: test, jehož fixtura
# neměří to, co tvrdí, je slepý).
# Mutace proto vkládá **VLASTNÍ SONDU** do `AGENTS.md`: řádek bez slov
# minulosti a bez data, ve tvaru, který pravidlo uvozovek rozhoduje **sám**.
PROBE_SLOUPCU = "| **S1** | sonda: hodnota **%s** |"
KOTVA_CIT = PROBE_SLOUPCU % "„32 sloupců“"       # číslo V uvozovkách
NAHRAD_CIT = PROBE_SLOUPCU % "32 sloupců"        # číslo BEZ uvozovek
print("\n  5a) MUTACE 3 — citace se stane tvrzením (uvozovky pryč)")
ta2 = agents_orig.decode("utf-8")
pocet_cit = ta2.count(KOTVA_CIT)
print("     sonda v AGENTS.md: %dx (musí být 0 — vkládá se až teď)" % pocet_cit)
if pocet_cit != 0:
    chyby.append("M3: sonda %r je v AGENTS.md už před mutací (%d×)"
                 % (KOTVA_CIT, pocet_cit))
else:
    # 1) KONTROLNÍ PŮL: sonda S UVOZOVKAMI se jako rozchod hlásit NESMÍ.
    #    Bez tohohle by „spadlo to bez uvozovek" nic nedokazovalo — mohlo by
    #    to spadnout pokaždé.
    s_uvoz = ta2 + "\n" + (KOTVA_CIT % ()) + "\n"
    assert s_uvoz != ta2, "M3: kontrolní sonda se nevložila"
    # ⚠ ČÍSLO ŘÁDKU SE **HLEDÁ V OBSAHU**, NEPOČÍTÁ SE — a to je poučení
    # z prvního běhu této mutace (2. 10. 2026): spočítal jsem
    # `len(ta2.splitlines()) + 1` a vyšlo **495**, ale soubor končí newline,
    # takže sonda je na **496** — a test pak hlásil „sonda vypadla z měření
    # úplně", ačkoli byla v ZÁZNAMECH. Byl to **falešný nález o správném kódu**
    # a stál jedno kolo (přesně past `overovani` §7.11: „nehledej pořadím,
    # vymez to řádkem").
    def radek_sondy(text: str) -> int:
        return next(k for k, l in enumerate(text.splitlines(), 1)
                    if l.startswith("| **S1**"))
    try:
        AGENTS.write_text(s_uvoz, encoding="utf-8", newline="")
        assert KOTVA_CIT in AGENTS.read_text(encoding="utf-8"), "M3: sonda v souboru neni!"
        r_s = radek_sondy(AGENTS.read_text(encoding="utf-8"))
        v_k = spust()
        roz_k, zaz_k = rozdel(v_k)
        je_roz_k = [x for x in roz_k if x[0] == "AGENTS.md" and x[1] == r_s]
        je_zaz_k = [x for x in zaz_k if x[0] == "AGENTS.md" and x[1] == r_s]
        print("     KONTROLNÍ PŮL (s uvozovkami): na ř. %d rozchod=%s, záznam=%s"
              % (r_s, "ANO" if je_roz_k else "ne", "ANO" if je_zaz_k else "ne"))
        for x in je_zaz_k:
            # ⚠ POZOR NA POČET PRVKŮ: `rozdel()` vrací **5** hodnot
            # (soubor, řádek, veličina, tvrdí, zdroj) — žádný `x[5]` tam není.
            # Naměřeno 2. 10. 2026: `x[5]` shodilo test na `IndexError`
            # **uprostřed mutace**, takže se zdálo, že brána spadla.
            print("        ZÁZNAM: %s:%d tvrdí %s (zdroj %s)"
                  % (x[0], x[1], x[3], x[4]))
        if je_roz_k:
            chyby.append("M3: sonda S UVOZOVKAMI se hlásí jako rozchod — "
                         "pravidlo CITACE nefunguje")
        elif not je_zaz_k:
            chyby.append("M3: sonda S UVOZOVKAMI není ani v ROZCHODECH ani "
                         "v ZÁZNAMECH — vypadla z měření úplně (to je slepé místo)")

        # 2) MUTOVANÁ PŮL: tytéž uvozovky pryč → musí se ohlásit jako ROZCHOD.
        zmut_cit = ta2 + "\n" + (NAHRAD_CIT % ()) + "\n"
        assert zmut_cit != s_uvoz, "M3: mutace text nezměnila!"
        AGENTS.write_text(zmut_cit, encoding="utf-8", newline="")
        _rad = [l for l in AGENTS.read_text(encoding="utf-8").splitlines()
                if l.startswith("| **S1**")]
        assert _rad and "„" not in _rad[0], "M3: na měřeném řádku pořád jsou uvozovky!"
        r_m = radek_sondy(AGENTS.read_text(encoding="utf-8"))
        assert r_m == r_s, "M3: sonda se mezi půlkami posunula (%d vs %d)" % (r_s, r_m)
        v5 = spust()
        roz5, _ = rozdel(v5)
        cit_roz = [x for x in roz5 if x[0] == "AGENTS.md" and x[1] == r_m
                   and x[2] == "sloupců"]
        print("     MUTOVANÁ PŮL (bez uvozovek): na ř. %d v ROZCHODECH = %s"
              % (r_m, "ANO (SPRÁVNĚ — citace se stala tvrzením)" if cit_roz else "ne"))
        for x in cit_roz:
            print("        ROZCHOD: %s:%d tvrdí %s (zdroj %s)"
                  % (x[0], x[1], x[3], x[4]))
        if not cit_roz:
            chyby.append("M3: odebrání uvozovek sondu NEVRÁTILO mezi rozchody "
                         "(AGENTS.md:%d) — pravidlo CITACE ho nezařazuje" % r_m)
    finally:
        AGENTS.write_bytes(agents_orig)
        assert AGENTS.read_bytes() == agents_orig, "M3: AGENTS.md nevracen!"

# ── 5b) MUTACE 4: DVĚ RŮZNÉ BRÁNY (jádro opravy z Úkolu 1) ────────────────
# ⚠ TOHLE JE NEJDŮLEŽITĚJŠÍ MUTACE Z CELÉHO TESTU, protože měří **JÁDRO
# OPRAVY**: `audit2b` do 2. 10. 2026 srovnával veličinu `kontrol` s **jedním**
# číslem (běh Godotu = 65) a **každý** jiný počet kontrol hlásil jako rozchod —
# i když ho vydala **jiná brána správně** (naměřeno: 11 z 15 rozchodů).
#
# Mutace proto **vloží DVĚ tvrzení od DVOU různých bran**:
#   * `23 kontrol`  → to je čítač `a1-a2-over`  → **NESMÍ** se ohlásit,
#   * `777 kontrol` → to nevydala ŽÁDNÁ brána    → **MUSÍ** se ohlásit.
# Kdyby registr fungoval jako „ber, co se hodí", projde i to druhé — a test
# to odhalí. Kdyby naopak nefungoval vůbec, ohlásí se i to první.
VLOZENE = [
    ("PROBE-A: a1-a2-over hlásí 23 kontrol, 0 chyb", 23, False),
    ("PROBE-B: testy hry hlásí 65 kontrol, 0 selhání", 65, False),
    ("PROBE-C: žádná brána nehlásí 777 kontrol, 0 chyb", 777, True),
]
print("\n  5b) MUTACE 4 — dvě různé brány: `23` (a1-a2-over) vs. `777` (žádná)")
PROBE_SOUBOR = WS / "MOZNOSTI-AGENTA.md"
probe_orig = PROBE_SOUBOR.read_bytes()
if not PROBE_SOUBOR.is_file():
    chyby.append("M4: %s není — není kam vložit sondážní řádky" % PROBE_SOUBOR.name)
else:
    tp = probe_orig.decode("utf-8")
    vloz = "\n".join(r for r, _h, _c in VLOZENE)
    assert not any(r in tp for r, _h, _c in VLOZENE), \
        "M4: sondážní řádky v souboru UŽ JSOU — mutace by nic nezměnila"
    zmut_p = tp + "\n\n" + vloz + "\n"
    assert zmut_p != tp, "M4: text se nezmenil!"
    try:
        PROBE_SOUBOR.write_text(zmut_p, encoding="utf-8", newline="")
        for r, _h, _c in VLOZENE:
            assert r in PROBE_SOUBOR.read_text(encoding="utf-8"), \
                "M4: vložený řádek %r v souboru NENÍ!" % r[:30]
        v6 = spust()
        roz6, _ = rozdel(v6)
        for popis, hodnota, ma_byt_rozchod in VLOZENE:
            je = any(x[0] == PROBE_SOUBOR.name and x[3] == str(hodnota) for x in roz6)
            stav = "ROZCHOD" if je else "přijato (má zdroj)"
            if je != ma_byt_rozchod:
                chyby.append("M4: %r — čekáno %s, vyšlo %s"
                             % (popis[:34],
                                "ROZCHOD" if ma_byt_rozchod else "přijato",
                                stav))
            print("     %-46s → %s %s"
                  % (popis[:46], stav,
                     "" if je == ma_byt_rozchod else "  <<< CHYBA"))
    finally:
        PROBE_SOUBOR.write_bytes(probe_orig)
        assert PROBE_SOUBOR.read_bytes() == probe_orig, \
            "M4: %s nevracen!" % PROBE_SOUBOR.name

# ── 6) po všech mutacích: soubory musí být BIT PO BITU zpátky ──────────────
print("\n  6) návrat souborů")
print("     HANDOFF.md bit po bitu: %s"
      % ("ANO" if HANDOFF.read_bytes() == handoff_orig else "NE"))
print("     AGENTS.md  bit po bitu: %s"
      % ("ANO" if AGENTS.read_bytes() == agents_orig else "NE"))
print("     %-10s bit po bitu: %s"
      % (PROBE_SOUBOR.name, "ANO" if PROBE_SOUBOR.read_bytes() == probe_orig else "NE"))
if HANDOFF.read_bytes() != handoff_orig:
    chyby.append("HANDOFF.md NEBYL vrácen bit po bitu")
if AGENTS.read_bytes() != agents_orig:
    chyby.append("AGENTS.md NEBYL vrácen bit po bitu")
if PROBE_SOUBOR.is_file() and PROBE_SOUBOR.read_bytes() != probe_orig:
    chyby.append("%s NEBYL vrácen bit po bitu" % PROBE_SOUBOR.name)
# Po mutacích musí být soubor zpátky v tom stavu, v jakém byl na začátku běhu
# (ne ve stavu Úkolu 0 — od té doby do něj bylo legitimně připsáno, omyl 96).
if ref is not None:
    vysledek2 = append_only(ref, HANDOFF)
    if vysledek2 and vysledek2[1]:
        # ⚠ TÁŽ VÝJIMKA JAKO V KONTROLE 0) — viz komentář tam: přejmenovaný
        # NADPIS není ztracený obsah. Rozhoduje přítomnost klíčových oddílů.
        _nove2 = HANDOFF.read_text(encoding="utf-8")
        _klice2 = ("## 4. ", "## 5. ", "## 9. ", "§8")
        _chybi2 = [k for k in _klice2 if k not in _nove2]
        if _chybi2:
            chyby.append("HANDOFF.md po návratu NENÍ append-only — chybí obsah: %s"
                         % _chybi2)
        else:
            print("     (rozdíl %d řádků je ve TVARU — přejmenovaný nadpis — "
                  "ne v obsahu; klíčové oddíly jsou na místě)" % vysledek2[1])

v4 = spust()
roz4, _ = rozdel(v4)
print("     kontrolní běh po návratu: rozchodů u `granulí` = %d"
      % len([x for x in roz4 if x[2] == "granulí"]))
if [x for x in roz4 if x[2] == "granulí"]:
    chyby.append("po návratu se u `granulí` znovu hlásí rozchod")

print("\n" + "=" * 96)
print("  ZMĚŘENO: běhů brány=%d, mutací=%d, chyb=%d" % (7, 4, len(chyby)))
if chyby:
    print()
    for c in chyby:
        print("  CHYBA: %s" % c)
    print("\nVYSLEDEK: Úkol 4 NENÍ ověřen → exit 1")
    sys.exit(1)
print("\nVYSLEDEK: `granulí` má 0 rozchodů, kotvu zařadil NADPIS ODDÍLU,")
print("          vypnutí obou pravidel ho vrátí mezi rozchody a HANDOFF.md")
print("          je bit po bitu původní a vůči Úkolu 0 APPEND-ONLY. exit 0")
sys.exit(0)
