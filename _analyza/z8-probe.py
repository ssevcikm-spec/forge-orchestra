# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
"""Z8: kde je krok s FORGE_ATTEMPT a co na to říká dnešní kritérium."""
import pathlib
import sys

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

for lbl, p in [
    ("šablona", _REPO / 'repo' / '.github' / 'workflows' / 'agent.yml'),
    ("hra", _HRA / '.github' / 'workflows' / 'agent.yml'),
]:
    d = yaml.safe_load(pathlib.Path(p).read_text(encoding="utf-8"))
    kroky = d["jobs"]["agent"]["steps"]
    podle_jmena = [s for s in kroky if s.get("name") == "Spusť agenta"]
    podle_env = [s for s in kroky if "FORGE_ATTEMPT" in (s.get("env") or {})]
    print(f"--- {lbl}")
    print(f"    kroků jménem 'Spusť agenta' : {len(podle_jmena)}")
    print(f"    kroků s FORGE_ATTEMPT v env: {len(podle_env)}  -> {[s.get('name') for s in podle_env]}")
    print(f"    DNEŠNÍ kritérium env_ok = {bool(podle_jmena) and 'FORGE_ATTEMPT' in podle_jmena[0].get('env', {})}")
    print(f"    SPRÁVNÉ kritérium env_ok = {bool(podle_env)}")
