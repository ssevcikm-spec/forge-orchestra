"""Zaverecna kontrola: struktura workspace, platnost JSON a UTF-8 u dokumentace."""
import json
import os
import sys

OK = True
W = r"C:\Users\Ssevc\Local-Deepseek"

print("=== struktura workspace ===")
# `games` obsahuje klon hry, na které orchestra pracuje – dnes `uo-shadows`.
ocekavane = ["orchestra", "games", "games/uo-shadows", "research", "router",
             "_retired", "obrazky", "ollama", "session-handoff"]
for k in ocekavane:
    p = os.path.join(W, k.replace("/", os.sep))
    print(f"  {'OK ' if os.path.exists(p) else 'CHYBI'} {k}")

print("\n=== co melo zmizet ===")
# POZOR: `forge-quest` tu dřív BYL a byla to chyba. Není to smazaná složka, ale
# ŽIVÝ repozitář na GitHubu (`ssevcikm-spec/forge-quest`, push 30. 9. 2026,
# vlastní GitHub Pages a vlastní hra). Kontrola ho hledala jako lokální složku –
# nikdy tu nebyla, takže vždy hlásila „smazáno OK". Kdyby se klon někdy pořídil,
# hlásila by „STÁLE EXISTUJE" a nutila mazat živý projekt.
# Zůstává jen to, co skutečně bylo smazáno (GameForge).
for k in ["gameforge", "uo-sandbox-repo", "uo-sandbox"]:
    p = os.path.join(W, k)
    stav = "SMazano OK" if not os.path.exists(p) else "STALE EXISTUJE"
    if os.path.exists(p):
        OK = False
    print(f"  {stav} {k}")
print("  (poznámka: repo `forge-quest` na GitHubu je ŽIVÉ – viz orchestra/README.md)")

print("\n=== orchestra: klicove soubory ===")
o = os.path.join(W, "orchestra")
for f in ["README.md", "conductor/src/index.ts", "repo/.forge/providers.json",
          "repo/.forge/roadmap.json", "tools/status.mjs", "tools/roadmap-reset.mjs",
          "tools/tasks.mjs", "tools/cancel-stale-runs.mjs", "tools/git.cmd",
          "tools/godot/Godot_v4.7.2-stable_win64_console.exe",
          "repo/.forge/node/.env", ".env", ".secrets/github_pat.txt"]:
    p = os.path.join(o, f.replace("/", os.sep))
    ada = os.path.exists(p)
    if not ada:
        OK = False
    print(f"  {'OK   ' if ada else 'CHYBI'} {f}")

print("\n=== hra: klicove soubory ===")
g = os.path.join(W, "games", "uo-shadows")
for f in [".forge/roadmap.json", ".forge/pick-provider.mjs",
          ".github/workflows/agent.yml", ".github/workflows/model-check.yml",
          "docs/ARCHITEKTURA.md", "CONVENTIONS.md", "forge.json", "project.godot"]:
    p = os.path.join(g, f.replace("/", os.sep))
    ada = os.path.exists(p)
    if not ada:
        OK = False
    print(f"  {'OK   ' if ada else 'CHYBI'} {f}")

print("\n=== platnost JSON ===")
for p in [os.path.join(o, "repo", ".forge", "providers.json"),
          os.path.join(g, ".forge", "roadmap.json"),
          os.path.join(g, "forge.json")]:
    try:
        d = json.load(open(p, encoding="utf-8"))
        if "grains" in d:
            g2 = d["grains"]
            print(f"  OK  {os.path.basename(p)}: {len(g2)} granulí, "
                  f"{sum(1 for x in g2 if x.get('done'))} hotových, "
                  f"{sum(1 for x in g2 if x.get('model') == 'strong')} strong")
        else:
            print(f"  OK  {os.path.basename(p)}")
    except Exception as e:
        OK = False
        print(f"  CHYBA {p}: {e}")

print("\n=== dokumentace je platne UTF-8 ===")
dok = ["README.md", "HANDOFF.md", "research/README.md",
       "_retired/README-router.md", "orchestra/README.md",
       os.path.join(os.path.expanduser("~"), ".dsh", "skills", "orchestra", "SKILL.md")]
for f in dok:
    p = f if os.path.isabs(f) else os.path.join(W, f.replace("/", os.sep))
    try:
        open(p, encoding="utf-8").read()
        print(f"  OK  {f}")
    except Exception as e:
        OK = False
        print(f"  CHYBA {f}: {e}")

print("\n=== herni repo: git stav ===")
print(f"  .git existuje: {os.path.exists(os.path.join(g, '.git'))}")
import subprocess  # noqa: E402
r = subprocess.run(["git", "-C", g, "status", "--porcelain"], capture_output=True, text=True)
print(f"  nezapsane zmeny: {len([l for l in r.stdout.splitlines() if l.strip()])}")

print()
print("VSE OK" if OK else "NEJAKE PROBLEMY (viz vys)")
sys.exit(0 if OK else 1)
