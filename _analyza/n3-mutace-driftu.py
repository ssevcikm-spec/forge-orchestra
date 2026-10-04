r"""Mutační test opraveného `kontrola-driftu.mjs` (nález N3).

CO SE DOKAZUJE: že nástroj po opravě UMI SPADNOUT na vadu, kterou dřív viděl
jako `OK (struktura)` — tedy že `FORGE_ATTEMPT` je v JINÉM KROKU, než má být.

Postup (tři kroky, mezi nimi se pouští nástroj z PowerShellu):
  1) `--vrat`  : vrátí FORGE_ATTEMPT z kroku „Spusť agenta" na krok providera
                 (přesně vada, kterou měl herní rep do 2. 10. 2026)
  2) `--obnov` : vrátí soubor ze zálohy (bajt po bajtu)
  3) `--stav`  : vypíše, na kterém kroku hodnota je (kontrola, že se to povedlo)

PROČ VLASTNÍ SOUBOR A NE `python -c`: `${{ inputs.attempt }}` v here-stringu
rozbije parser PowerShellu (`OpenBraceNeedsToBeBacktickedInVariableName`).
Je to táž past, před kterou varuje skill `dsh-prostredi` §3c.
"""
import pathlib
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    print("CHYBA: chybí PyYAML")
    sys.exit(2)

CIL = pathlib.Path("games/uo-shadows/.github/workflows/agent.yml")
ZALOHA = pathlib.Path("_analyza/_mutace-agent.yml")

RADEK = "          FORGE_ATTEMPT: ${{ inputs.attempt }}\n"
KOTVA_AGENT = "          FORGE_GRAIN: ${{ inputs.grain }}\n"
KOTVA_PROVIDER = ("          FORGE_MIN_STRONG: ${{ inputs.model }}\n"
                  "        run: node .forge/pick-provider.mjs")


def kde_je() -> list:
    d = yaml.safe_load(CIL.read_text(encoding="utf-8"))
    return [s.get("name") for s in d["jobs"]["agent"]["steps"]
            if "FORGE_ATTEMPT" in (s.get("env") or {})]


def main() -> int:
    akce = sys.argv[1] if len(sys.argv) > 1 else "--stav"

    if akce == "--vrat":
        ZALOHA.write_bytes(CIL.read_bytes())
        t = CIL.read_text(encoding="utf-8")
        if t.count("FORGE_ATTEMPT") != 1:
            print(f"CHYBA: čekán 1 výskyt, je {t.count('FORGE_ATTEMPT')}")
            return 2
        if KOTVA_AGENT + RADEK not in t:
            print("CHYBA: hodnota není na kroku agenta – není co vracet")
            return 2
        t = t.replace(KOTVA_AGENT + RADEK, KOTVA_AGENT, 1)
        if KOTVA_PROVIDER not in t:
            print("CHYBA: kotva kroku providera nenalezena")
            return 2
        t = t.replace(KOTVA_PROVIDER, KOTVA_PROVIDER.replace(
            "        run:", RADEK + "        run:"), 1)
        CIL.write_bytes(t.encode("utf-8"))
        # OVĚŘENÍ, ŽE MUTACE PROBĚHLA (jinak testuje nezměněný soubor!)
        if t.count("FORGE_ATTEMPT") != 1:
            print("CHYBA: po mutaci není právě 1 výskyt – mutace se nepovedla")
            return 2
        print(f"  mutace zapsána; FORGE_ATTEMPT nyní na: {kde_je()}")
        return 0

    if akce == "--obnov":
        if not ZALOHA.is_file():
            print("CHYBA: záloha neexistuje")
            return 2
        shutil.copyfile(ZALOHA, CIL)
        print(f"  obnoveno ze zálohy; FORGE_ATTEMPT nyní na: {kde_je()}")
        return 0

    print(f"  FORGE_ATTEMPT je na kroku: {kde_je()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
