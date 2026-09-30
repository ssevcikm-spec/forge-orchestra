"""Sjednotí šablonu orchestra s herními vylepšeními (idempotentně).

Co se doplňuje a proč:
  1) KVÓTNÍ GUARD – když první pokus spadl na vyčerpané kvótě, druhý
     poskytovatel se nezkouší. Naměřeno 30. 9. 2026: 9 z 13 běhů skončilo na
     rate-limitu a 11 z 13 zkoušelo druhého poskytovatele – žádný neuspěl.
     Hra tuhle úpravu měla, šablona ne (drift opačným směrem).
  2) VSTUP `attempt` – číslo pokusu, podle kterého pick-provider posouvá pořadí
     modelů, aby opakovaný pokus nezkoušel stejný model. Naměřeno: task #128
     i #131 zkoušely 5× po sobě mistral/codestral a selhaly pokaždé stejně.

Poznámka: textové zásahy do souborů s diakritikou se dělají Pythonem
s encoding='utf-8'. PowerShell (Get-Content -Raw + Set-Content) soubor
poškodil – YAML pak nešel načíst („unacceptable character #x009d").
"""

import pathlib
import sys
import yaml

SABLONA = pathlib.Path(
    r"C:\Users\Ssevc\Local-Deepseek\orchestra\repo\.github\workflows\agent.yml")

# --- 1) kvótní guard ------------------------------------------------------
STARY_GUARD = """          if ! zmenil_neco; then
            echo "::notice::model nezměnil žádný kód – zkouším jiného bezplatného poskytovatele"
            if node .forge/pick-provider.mjs --next; then
              nacti_poskytovatele
              spust_agenta
            fi
          fi"""

NOVY_GUARD = """          if ! zmenil_neco; then
            # KVÓTA vs. SCHOPNOST (od 30. 9. 2026). Druhý pokus s jiným
            # poskytovatelem má smysl jen tehdy, když je co zkoušet — tedy když
            # model odpověděl, ale kód nezměnil (jiný model to může trefit).
            # Když ale běh spadl na vyčerpané kvótě (rate-limit / denní strop),
            # druhý pokus je jen další spálený pokus: naměřeno 30. 9. — 9 z 13
            # běhů skončilo na rate-limitu a 11 z 13 zkoušelo druhého
            # poskytovatele — žádný z nich neuspěl. Kvóta je vzácnější než čas.
            if grep -qE 'RateLimitError|rate limit reached|exceeded your current quota' agent.log; then
              echo "::warning::první pokus spadl na vyčerpané kvótě – druhý poskytovatel se nezkouší (šetřím kvótu)"
            else
              echo "::notice::model nezměnil žádný kód – zkouším jiného bezplatného poskytovatele"
              if node .forge/pick-provider.mjs --next; then
                nacti_poskytovatele
                spust_agenta
              fi
            fi
          fi"""

# --- 2) vstup attempt -----------------------------------------------------
STARY_VSTUP = """      grain:
        description: 'ID granule v roadmapě (např. core.skills) – podle něj se bere owns, tedy soubory k editaci'
        required: false
        default: ''"""

NOVY_VSTUP = STARY_VSTUP + """
      attempt:
        description: 'Číslo pokusu (1 = první). Podle něj se posouvá pořadí modelů, aby opakovaný pokus nezkoušel stejný model.'
        required: false
        default: '1'"""

STARY_ENV = "          FORGE_GRAIN: ${{ inputs.grain }}"

NOVY_ENV = """          FORGE_GRAIN: ${{ inputs.grain }}
          # Číslo pokusu: pick-provider podle něj posune pořadí modelů, aby
          # opakovaný pokus nezkoušel stejný model jako ten, co právě selhal.
          # Naměřeno 30. 9. 2026: task #128 i #131 zkoušely 5× po sobě
          # mistral/codestral a selhaly pokaždé stejně.
          FORGE_ATTEMPT: ${{ inputs.attempt }}"""


def main() -> int:
    text = SABLONA.read_text(encoding="utf-8")
    zmeny = []

    if "RateLimitError" not in text:
        if STARY_GUARD not in text:
            print("CHYBA: blok druhého pokusu nenalezen – kvótní guard nelze vložit.")
            return 1
        text = text.replace(STARY_GUARD, NOVY_GUARD, 1)
        zmeny.append("kvótní guard (druhý pokus se nezkouší po rate-limitu)")
    else:
        print("kvótní guard: už tam je")

    if "FORGE_ATTEMPT" not in text:
        if STARY_ENV not in text:
            print("CHYBA: řádek FORGE_GRAIN nenalezen – nelze vložit FORGE_ATTEMPT.")
            return 1
        text = text.replace(STARY_ENV, NOVY_ENV, 1)
        zmeny.append("FORGE_ATTEMPT do prostředí kroku")
    else:
        print("FORGE_ATTEMPT: už tam je")

    if "attempt:" not in text:
        if STARY_VSTUP not in text:
            print("CHYBA: blok vstupu 'grain' nenalezen – nelze vložit 'attempt'.")
            return 1
        text = text.replace(STARY_VSTUP, NOVY_VSTUP, 1)
        zmeny.append("vstup 'attempt'")
    else:
        print("vstup 'attempt': už tam je")

    SABLONA.write_text(text, encoding="utf-8")

    # Ověření: YAML musí zůstat platný a vstupy vidět.
    data = yaml.safe_load(SABLONA.read_text(encoding="utf-8"))
    klic = True if True in data else "on"
    vstupy = list(data[klic]["workflow_dispatch"]["inputs"].keys())
    kroky = [s for s in data["jobs"]["agent"]["steps"] if s.get("name") == "Spusť agenta"]
    env_ok = bool(kroky) and "FORGE_ATTEMPT" in kroky[0].get("env", {})

    print("\nZměny:", ", ".join(zmeny) if zmeny else "(žádné)")
    print("YAML platný, vstupy:", ", ".join(vstupy))
    print("FORGE_ATTEMPT v env kroku:", env_ok)
    return 0


if __name__ == "__main__":
    sys.exit(main())
