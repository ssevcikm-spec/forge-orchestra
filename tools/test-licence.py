#!/usr/bin/env python
r"""Testy brány na licence a původ assetů (`check-licence.py`).

PROČ: brána, která umí jen projít, je k ničemu – stejně jako test, který se
nikdy nezapne. Tenhle soubor staví záměrně vadné projekty a čeká, že je brána
ODMÍTNE. Každý scénář odpovídá konkrétní vadě, na kterou se už někde narazilo:

  1) bez locku              – hra bez stažených assetů (nesmí blokovat)
  2) v pořádku             – lock + soubory + CREDITS sedí
  3) soubor bez záznamu    – asset „přitekl" bez původu
  4) zakázaná licence      – cc-by-sa (vynucuje stejnou licenci na hru)
  5) cc-by bez autora      – chybí podmínka licence
  6) přepsaný soubor       – hash nesouhlasí
  7) změněný CREDITS.md    – atribuce se rozešla s lockem

Použití:  python orchestra/tools/test-licence.py
Návratový kód: 0 = všechny scénáře podle očekávání.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TADY = Path(__file__).resolve().parent
BRANA = TADY / "check-licence.py"

POVOLENE = ["cc0", "cc-by", "ofl", "mit", "public-domain"]


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _zapis(projekt: Path, relativni: str, data: bytes) -> dict:
    cesta = projekt / relativni
    cesta.parent.mkdir(parents=True, exist_ok=True)
    cesta.write_bytes(data)
    return {
        "soubor": relativni,
        "zdroj": "kenney",
        "licence": "cc0",
        "autor": "Kenney",
        "web": "https://kenney.nl",
        "url": "https://kenney.nl/media/pages/assets/interface-sounds/fa43c1dd4d-1677589452/kenney_interface-sounds.zip",
        "algoritmus": "sha256",
        "hash": _hash(data),
        "velikost": len(data),
        "overeno": True,
    }


def _lock(projekt: Path, zaznamy: list[dict], licence_seznam: list[str] | None = None) -> None:
    (projekt / "assets").mkdir(parents=True, exist_ok=True)
    obsah = {
        "_generated": "tools/asset-fetch.mjs – needituj ručně, přepíše se",
        "verze": 1,
        "povolene_licence": licence_seznam or POVOLENE,
        "soubory": zaznamy,
    }
    (projekt / "assets" / "asset-lock.json").write_text(
        json.dumps(obsah, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _spust(projekt: Path) -> tuple[int, str]:
    vysledek = subprocess.run(
        [sys.executable, str(BRANA), str(projekt)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return vysledek.returncode, (vysledek.stdout or "") + (vysledek.stderr or "")


def _ocekavane_credits(zaznamy: list[dict]) -> str:
    """Opsané z generátoru jen pro účely testu (aby test nezávisel na bráně)."""
    podle: dict[str, list[dict]] = {}
    for s in zaznamy:
        klic = f"{s.get('zdroj', '?')}|{s.get('licence', '?')}|{s.get('autor') or 'neuveden'}"
        podle.setdefault(klic, []).append(s)
    radky = [
        "<!-- GENEROVÁNO: orchestra/tools/asset-fetch.mjs – needituj ručně -->",
        "# Poděkování a licence assetů",
        "",
        "Assety třetích stran použité v tomto projektu. U licencí CC-BY je uvedení",
        "autora PODMÍNKOU použití, proto tenhle soubor není dobrovolný.",
        "",
    ]
    for klic in sorted(podle):
        zdroj, licence, autor = klic.split("|")
        soubory = podle[klic]
        radky += [f"## {zdroj} — {licence.upper()}", "", f"- Autor: {autor}"]
        if soubory[0].get("url"):
            radky.append(f"- Zdroj: {soubory[0]['url']}")
        if soubory[0].get("web"):
            radky.append(f"- Web: {soubory[0]['web']}")
        radky.append(f"- Soubory ({len(soubory)}):")
        for jmeno in sorted(s.get("soubor", "?") for s in soubory):
            radky.append(f"  - `{jmeno}`")
        radky.append("")
    radky += [
        "## Vlastní a vygenerované assety",
        "",
        "Assety vzniklé v projektu (Blender, SDXL/ComfyUI, Gemini) jsou uvedené",
        "v `asset-lock.json` se zdrojem `vlastni` a licencí projektu.",
        "",
    ]
    return "\n".join(radky)


def _dokonceny(projekt: Path, zaznamy: list[dict]) -> None:
    """Projekt, který MÁ projít: lock + soubory + CREDITS ve shodě."""
    _lock(projekt, zaznamy)
    (projekt / "assets" / "CREDITS.md").write_text(
        _ocekavane_credits(zaznamy), encoding="utf-8"
    )


# ------------------------------------------------------------------ scénáře ----
def scenar_bez_locku(koren: Path) -> tuple[bool, str]:
    projekt = koren / "bez-locku"
    (projekt / "assets").mkdir(parents=True)
    (projekt / "assets" / "player.png").write_bytes(b"PNG")
    kod, vystup = _spust(projekt)
    ok = kod == 0 and "lock" in vystup
    return ok, f"exit={kod} (čekáno 0, poznámka o chybějícím locku)"


def scenar_v_poradku(koren: Path) -> tuple[bool, str]:
    projekt = koren / "v-poradku"
    zaznamy = [_zapis(projekt, "assets/audio/ui/click.ogg", b"OggS-fake-audio")]
    _dokonceny(projekt, zaznamy)
    kod, vystup = _spust(projekt)
    ok = kod == 0 and "v pořádku" in vystup
    return ok, f"exit={kod}: {vystup.strip().splitlines()[-1] if vystup.strip() else '(prázdno)'}"


def scenar_soubor_bez_zaznamu(koren: Path) -> tuple[bool, str]:
    projekt = koren / "bez-zaznamu"
    zaznamy = [_zapis(projekt, "assets/audio/ui/click.ogg", b"OggS-fake-audio")]
    _dokonceny(projekt, zaznamy)
    (projekt / "assets" / "audio" / "ui" / "tajny.ogg").write_bytes(b"OggS-odnikud")
    kod, vystup = _spust(projekt)
    ok = kod == 1 and "tajny.ogg" in vystup and "chybí" in vystup
    return ok, f"exit={kod} (čekáno 1 a jméno souboru)"


def scenar_zakazana_licence(koren: Path) -> tuple[bool, str]:
    projekt = koren / "zakazana-licence"
    zaznam = _zapis(projekt, "assets/sprites/lpc.png", b"PNG")
    zaznam["licence"] = "cc-by-sa"
    zaznam["autor"] = "Někdo"
    _dokonceny(projekt, [zaznam])
    kod, vystup = _spust(projekt)
    ok = kod == 1 and "cc-by-sa" in vystup
    return ok, f"exit={kod} (čekáno 1, zmínka o cc-by-sa)"


def scenar_ccby_bez_autora(koren: Path) -> tuple[bool, str]:
    projekt = koren / "ccby-bez-autora"
    zaznam = _zapis(projekt, "assets/music/theme.ogg", b"OggS")
    zaznam["licence"] = "cc-by"
    zaznam["autor"] = "neuveden"
    _dokonceny(projekt, [zaznam])
    kod, vystup = _spust(projekt)
    ok = kod == 1 and "CC-BY" in vystup
    return ok, f"exit={kod} (čekáno 1, zmínka o autorovi)"


def scenar_prepisany_soubor(koren: Path) -> tuple[bool, str]:
    projekt = koren / "prepisany"
    zaznamy = [_zapis(projekt, "assets/sprites/coin.png", b"PNG-puvodni")]
    _dokonceny(projekt, zaznamy)
    # Někdo soubor přepsal (regenerace, ruční zásah) – lock zůstal starý.
    (projekt / "assets" / "sprites" / "coin.png").write_bytes(b"PNG-jiny-obsah")
    kod, vystup = _spust(projekt)
    ok = kod == 1 and "hash nesouhlasí" in vystup
    return ok, f"exit={kod} (čekáno 1, neshoda hashe)"


def scenar_zmeneny_credits(koren: Path) -> tuple[bool, str]:
    projekt = koren / "zmeneny-credits"
    zaznamy = [_zapis(projekt, "assets/audio/ui/click.ogg", b"OggS")]
    _dokonceny(projekt, zaznamy)
    (projekt / "assets" / "CREDITS.md").write_text("# Ručně přepsané\n", encoding="utf-8")
    kod, vystup = _spust(projekt)
    ok = kod == 1 and "CREDITS.md" in vystup
    return ok, f"exit={kod} (čekáno 1, neshoda CREDITS)"  # noqa: RUF001


# --- ověření proti SKUTEČNÝM datům (ne proti vyrobeným scénářům) --------------
# Tyhle dva scénáře jsou důkaz, že P0 nic nerozbíjí: brána se pouští na opravdový
# klon hry a na živý fetch z P1. Kdyby P0 mělo na hru dopad, je to vidět tady.
def scenar_zivy_fixture(koren: Path) -> tuple[bool, str]:
    fixture = TADY.parent / ".tmp" / "p1-test"
    if not (fixture / "assets" / "asset-lock.json").is_file():
        return True, "SKIP – živý fixture z P1 tu není (spusť nejdřív asset-fetch.mjs)"
    kod, vystup = _spust(fixture)
    ok = kod == 0
    return ok, f"exit={kod} na {fixture.relative_to(TADY.parent.parent)}"


def scenar_hra(koren: Path) -> tuple[bool, str]:
    hra = TADY.parent.parent / "games" / "uo-shadows"
    if not (hra / "assets").is_dir():
        return True, "SKIP – klon hry games/uo-shadows tu není"
    ma_lock = (hra / "assets" / "asset-lock.json").is_file()
    kod, vystup = _spust(hra)
    if not ma_lock:
        ok = kod == 0 and "lock" in vystup
        return ok, f"exit={kod} (čekáno 0 – hra lock nemá, brána se nesmí ozvat)"
    # Jakmile hra lock MÁ, musí být v pořádku – jinak by P0 rozbilo její CI.
    ok = kod == 0
    return ok, f"exit={kod} (hra už lock má – musí projít)"


SCENARE = [
    ("bez locku → projde s poznámkou", scenar_bez_locku),
    ("v pořádku → projde", scenar_v_poradku),
    ("soubor bez záznamu → odmitne", scenar_soubor_bez_zaznamu),
    ("zakázaná licence cc-by-sa → odmitne", scenar_zakazana_licence),
    ("cc-by bez autora → odmitne", scenar_ccby_bez_autora),
    ("přepsaný soubor (hash) → odmitne", scenar_prepisany_soubor),
    ("změněný CREDITS.md → odmitne", scenar_zmeneny_credits),
    ("živý P1 fixture → projde", scenar_zivy_fixture),
    ("skutečný klon hry → beze změny chování", scenar_hra),
]


def _pracovni_slozka() -> Path:
    """Zkušební projekty patří do orchestra/.tmp, NE do systémového tempu.

    PROČ: `tempfile` na téhle stanici míří mimo pracovní prostor a sandbox DSH
    tam zápis nepustí (`PermissionError: Access is denied`). Naměřeno 30. 9. 2026
    při prvním spuštění tohohle testu – spadl dřív, než ověřil cokoli.
    `.tmp/` je v .gitignore, takže se nic nedostane do repa.
    """
    slozka = TADY.parent / ".tmp" / "test-licence"
    shutil.rmtree(slozka, ignore_errors=True)
    slozka.mkdir(parents=True, exist_ok=True)
    return slozka


def main() -> int:
    if not BRANA.is_file():
        print(f"CHYBA: brána není: {BRANA}")
        return 1
    chyb = 0
    koren = _pracovni_slozka()
    for nazev, funkce in SCENARE:
        try:
            ok, detail = funkce(koren)
        except Exception as e:  # noqa: BLE001
            ok, detail = False, f"výjimka: {e!r}"
        print(f"  {'OK  ' if ok else 'CHYBA'} {nazev}")
        print(f"        {detail}")
        if not ok:
            chyb += 1
        # Každý scénář má vlastní složku, ale pro jistotu uklidíme.
        for dite in list(koren.iterdir()):
            if dite.is_dir():
                shutil.rmtree(dite, ignore_errors=True)
    print()
    if chyb:
        print(f"{chyb} z {len(SCENARE)} scénářů NEPROŠLO")
        return 1
    print(f"všech {len(SCENARE)} scénářů prošlo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
