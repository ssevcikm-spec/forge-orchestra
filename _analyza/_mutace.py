# -*- coding: utf-8 -*-
r"""Jedna funkce pro MUTACE v měřidlech — aby se táž vada neopakovala pětkrát.

PROČ TO EXISTUJE (naměřeno 6. 10. 2026, klasifikace **205 omylů** projektu):
**15 omylů** má vzorec „**mutace se tiše neprovedla / nezměnila měřenou
podmínku — a prošla**". Dva z nich (omyly **#18** a **#106**) jsou **tentýž omyl
dvakrát**: nové jméno obsahovalo staré jako **podřetězec**. Další čtyři
(**#138**, **#173**, **#190**, **#198**) jsou čtyři různé způsoby, jak mutace
„prošla" bez provedení. Dnes má **každé měřidlo vlastní opis mutace** — proto se
vada opakuje. (Zdroj: `KRONIKA-PROJEKTU.md` §3–§4, `HANDOFF.md` §8.)

CO FUNKCE HLÍDÁ (a co bez ní poznat nelze):

1. **kotva je v souboru právě JEDNOU** — jinak `replace()` zmutuje i to, co nemá;
2. **text se SKUTEČNĚ změnil** — `replace()` bez nálezu vrátí tentýž řetězec
   a měřidlo pak měří **nezměněný** soubor (a tvrdí, že brána je slepá);
3. **nový text NEOBSAHUJE starý vzor** jako podřetězec — jinak „mutace" nezmění
   to, co kontrola hledá (přesně omyly #18 a #106);
4. **soubor se VŽDY vrátí** — i když test spadne (`try/finally` bez výjimky);
5. **návrat je bajt na bajt** — porovná se `sha256` před a po.

⚠ CO FUNKCE NEUMÍ: ověřit, že mutace **změnila to, co brána měří** — to je na
volajícím (a je to smysl testu). Funkce hlídá jen to, že **v souboru nastala
změna, kterou jsi popsal**.

Použití:

    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from _mutace import mutuj

    with mutuj(SOUBOR, "starý text", "nový text") as m:
        # ... spustit bránu a ověřit, že spadla ...
        pass
    # tady je soubor UŽ vrácený (i kdyby uvnitř vznikla výjimka)

Když kotva v souboru není nebo je víckrát, funkce **vyhodí `ValueError`** a nic
nezapíše — tichá mutace je horší než žádná.
"""

import contextlib
import hashlib
import pathlib


def _sha(bajty: bytes) -> str:
    return hashlib.sha256(bajty).hexdigest()


@contextlib.contextmanager
def mutuj(soubor, stary: str, novy: str, *, encoding: str = "utf-8"):
    """Zmutuje `soubor` (záměna `stary` → `novy`) a po skončení bloku ho VRÁTÍ.

    Vrací objekt s atributy:
        .pocet_vyskytu  – kolikrát byla kotva v souboru (musí být 1)
        .hash_pred      – sha256 souboru před mutací
        .hash_po_mutaci – sha256 zmutovaného souboru
        .hash_po_navratu– sha256 po vrácení (musí se rovnat `.hash_pred`)

    Vyhodí `ValueError`, když:
        * soubor neexistuje,
        * kotva `stary` v souboru NENÍ,
        * kotva je tam VÍCKRÁT (pak by mutace zasáhla i místo, které nemá),
        * `novy` OBSAHUJE `stary` jako podřetězec (mutace by nic nezměnila).
    """
    p = pathlib.Path(soubor)
    if not p.is_file():
        raise ValueError(f"mutuj: soubor neexistuje: {p}")

    puvodni = p.read_bytes()
    text = puvodni.decode(encoding)

    pocet = text.count(stary)
    if pocet == 0:
        raise ValueError(f"mutuj: kotva v souboru NENÍ (mutace by se tiše neprovedla): {stary!r}")
    if pocet > 1:
        raise ValueError(
            f"mutuj: kotva je v souboru {pocet}× — mutace by zasáhla i místo, které nemá "
            f"(spočítej výskyty a zvol delší kotvu): {stary!r}")
    if stary and stary in novy:
        raise ValueError(
            f"mutuj: nový text OBSAHUJE starý jako podřetězec — kontrola by hledala totéž "
            f"(přesně omyly #18/#106): {stary!r} ⊂ {novy!r}")

    zmutovany = text.replace(stary, novy, 1)
    if zmutovany == text:
        raise ValueError("mutuj: text se NEZMĚNIL (tohle by nemělo nastat — hlas to jako vadu nástroje)")

    hash_pred = _sha(puvodni)
    p.write_bytes(zmutovany.encode(encoding))
    hash_po_mutaci = _sha(p.read_bytes())
    if hash_po_mutaci == hash_pred:
        p.write_bytes(puvodni)
        raise ValueError("mutuj: hash se po mutaci NEZMĚNIL — zápis neproběhl")

    class _Vysledek:
        pocet_vyskytu = pocet
        hash_pred = None
        hash_po_mutaci = None
        hash_po_navratu = None

    v = _Vysledek()
    v.pocet_vyskytu = pocet
    v.hash_pred = hash_pred
    v.hash_po_mutaci = hash_po_mutaci

    try:
        yield v
    finally:
        p.write_bytes(puvodni)
        v.hash_po_navratu = _sha(p.read_bytes())
        if v.hash_po_navratu != v.hash_pred:
            raise ValueError(
                f"mutuj: NÁVRAT SELHAL — soubor není bajt na bajt původní "
                f"({v.hash_pred[:12]} vs {v.hash_po_navratu[:12]}): {p}")
