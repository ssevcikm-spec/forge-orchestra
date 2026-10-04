r"""Oprava N3 v herním repu: přesun `FORGE_ATTEMPT` na krok spouštějící agenta.

CO JE VADA (naměřeno 2. 10. 2026, `_analyza\n3-tok-attempt.py`):
  `FORGE_ATTEMPT` je v `games/uo-shadows/.github/workflows/agent.yml` na kroku
  „Vyber bezplatného poskytovatele LLM" (ř. 119), ale hodnotu čte
  `.forge/pick-provider.mjs` ř. 129 a 132 (`rotateByAttempt(..., FORGE_ATTEMPT)`).
  Krok „Spusť agenta" ji v env NEMÁ, a protože `env:` na úrovni kroku platí jen
  pro ten krok, skript ji nedostane → rotace modelů podle čísla pokusu je mrtvá.
  V šabloně (`orchestra/repo/...`) je na správném kroku.

PROČ TO TAKHLE A NE KOPIÍ CELÉHO SOUBORU:
  kopie šablony → hra by přepsala i herní odchylky, které jsou v pořádku
  (krok parsování má hra NAVÍC kontrolu stínění `class_name` a navíc tip na
  konstanty Godotu 3; jména kroků se liší). Mění se proto JEDEN řádek.

Bezpečnost: soubor se čte i zapisuje jako BAJTY (žádný přepis konců řádků),
po zápisu se ověří YAML, počet výskytů a že zůstal jen jeden.
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

WS = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
CIL = WS / "games/uo-shadows/.github/workflows/agent.yml"
ZALOHA = WS / "_analyza" / ("zaloha-agent-yml-" + CIL.name)

RADEK_ATTEMPT = "          FORGE_ATTEMPT: ${{ inputs.attempt }}\n"
KOTVA = "          FORGE_GRAIN: ${{ inputs.grain }}\n"

puvodni = CIL.read_bytes()
ZALOHA.write_bytes(puvodni)
print(f"záloha: {ZALOHA.name}  ({len(puvodni)} B)")

text = puvodni.decode("utf-8")
print(f"před: {CIL.name}  {len(text.splitlines())} řádků, "
      f"FORGE_ATTEMPT {text.count('FORGE_ATTEMPT')}x, "
      f"CRLF {text.count(chr(13) + chr(10))}x")

# --- kontrola vstupního stavu (ať se neopravuje něco jiného, než se měřilo) ---
if text.count("FORGE_ATTEMPT") != 1:
    print(f"CHYBA: čekán 1 výskyt FORGE_ATTEMPT, je jich {text.count('FORGE_ATTEMPT')}")
    sys.exit(2)
if KOTVA not in text:
    print("CHYBA: kotevní řádek FORGE_GRAIN v kroku „Spusť agenta“ nenalezen")
    sys.exit(2)
if ("Krok_spust_agenta" in text) or (text.count(KOTVA) != 1):
    print(f"CHYBA: řádek FORGE_GRAIN je v souboru {text.count(KOTVA)}x, čekán 1x")
    sys.exit(2)

# --- 1) vložit FORGE_ATTEMPT do kroku „Spusť agenta“ (za FORGE_GRAIN) ---
text = text.replace(KOTVA, KOTVA + RADEK_ATTEMPT, 1)

# --- 2) odebrat starý výskyt u kroku „Vyber bezplatného poskytovatele LLM“ ---
#     (včetně jeho komentáře — ten patří k hodnotě, ne k provideru)
STARY_KOMENTAR = """          # Číslo pokusu: pick-provider podle něj posune pořadí modelů, aby
          # opakovaný pokus nezkoušel stejný model jako ten, co právě selhal.
          # Naměřeno 30. 9. 2026: task #128 i #131 zkoušely 5× po sobě
          # mistral/codestral a selhaly pokaždé stejně.
"""
blok_stary = STARY_KOMENTAR + RADEK_ATTEMPT
if blok_stary in text:
    text = text.replace(blok_stary, "", 1)
    print("odebrán i starý komentář (patřil k hodnotě, ne k provideru)")
elif RADEK_ATTEMPT in text:
    # druhá polovina: řádek je tam 2x → odeber ten první (u provideru)
    prvni = text.index(RADEK_ATTEMPT)
    text = text[:prvni] + text[prvni + len(RADEK_ATTEMPT):]
    print("odebrán jen řádek (komentář měl jiný tvar)")
else:
    print("CHYBA: starý výskyt se nepodařilo odstranit")
    sys.exit(2)

if text.count("FORGE_ATTEMPT") != 1:
    print(f"CHYBA: po přesunu je výskytů {text.count('FORGE_ATTEMPT')}, čekán 1")
    sys.exit(2)

# --- 3) ověření přes YAML: kde hodnota JE a kde NENÍ ---
data = yaml.safe_load(text)
kroky = data["jobs"]["agent"]["steps"]
s_att = [s.get("name") for s in kroky if "FORGE_ATTEMPT" in (s.get("env") or {})]
print(f"\npo zápisu: kroků s FORGE_ATTEMPT v env = {s_att}")
ocekavany = "Spusť agenta"
if s_att != [ocekavany]:
    print(f"CHYBA: očekáván právě krok {ocekavany!r}")
    sys.exit(2)
if "FORGE_GRAIN" not in (kroky[[s.get('name') for s in kroky].index(ocekavany)].get("env") or {}):
    print("CHYBA: krok „Spusť agenta“ nemá FORGE_GRAIN – vloženo na špatné místo?")
    sys.exit(2)

CIL.write_bytes(text.encode("utf-8"))
print(f"zapsáno: {len(text.splitlines())} řádků, "
      f"CRLF {text.count(chr(13) + chr(10))}x  (beze změny konců řádků)")

# --- 4) YAML znovu ze disku (ne z paměti) ---
znovu = yaml.safe_load(CIL.read_text(encoding="utf-8"))
kroky = znovu["jobs"]["agent"]["steps"]
print("YAML z disku je platný; kroků v jobu 'agent':", len(kroky))
print("OK: FORGE_ATTEMPT je nyní na kroku spouštějícím agenta.")
