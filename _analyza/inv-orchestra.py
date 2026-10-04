#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hloubkova analýza orchestra - inventura stromu (Python walk, včetně skrytých složek).
Vzor: _analyza/sken-vazeb.py. Vypisuje strojově čitelné řádky ZMERENO:.
Nic nemění, jen čte.
"""
import os, sys, json, hashlib, re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\Ssevc\Local-Deepseek"
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".npm-cache", ".wrangler"}

def walk(root, skip=SKIP_DIRS):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for fn in filenames:
            yield os.path.join(dirpath, fn)

def rel(p, base=WS):
    return os.path.relpath(p, base).replace("\\", "/")

def tree(root, label):
    files = list(walk(os.path.join(WS, root)))
    total = sum(os.path.getsize(f) for f in files)
    ext = {}
    for f in files:
        e = os.path.splitext(f)[1].lower() or "(bez pripony)"
        ext[e] = ext.get(e, 0) + 1
    top = sorted(ext.items(), key=lambda kv: -kv[1])[:12]
    print(f"ZMERENO: strom={label} souboru={len(files)} bajtu={total}")
    print(f"  prirpony: " + ", ".join(f"{k}={v}" for k, v in top))
    return files

print("=== SOUPIS STROMU (bez .git, node_modules, __pycache__, cache) ===")
orchestra = tree("orchestra", "orchestra")
game = tree("games/uo-shadows", "games/uo-shadows")
ws = tree(".", "workspace-cely")

# orchestra bez assetu godot
godot = [f for f in orchestra if "tools/godot" in rel(f)]
print(f"ZMERENO: orchestra-tools-godot souboru={len(godot)} bajtu={sum(os.path.getsize(f) for f in godot)}")

# kolik z orchestra je sablona vs conductor vs tools
for sub in ["conductor", "repo", "tools", "bin", "assets"]:
    fl = [f for f in orchestra if rel(f).startswith("orchestra/" + sub + "/")]
    if fl:
        print(f"ZMERENO: orchestra/{sub} souboru={len(fl)} bajtu={sum(os.path.getsize(f) for f in fl)}")

# --- git ls-files vs disk (drift orchestra repa) ---
print("\n=== ZDROJ PRAVDY: git ls-files vs disk ===")

def git_ls(repo):
    import subprocess
    out = subprocess.run([os.path.join(WS, "orchestra", "tools", "git.cmd"), "-C", repo, "ls-files"],
                         capture_output=True)
    return set(l.strip() for l in out.stdout.decode("utf-8", "replace").splitlines() if l.strip())

GEN_PREFIX = (".godot/", ".test/", ".state/", ".tmp/", ".wrangler/", ".npm-cache/")

for repo, root, label in [("orchestra", "orchestra", "orchestra"),
                          (r"games\uo-shadows", "games/uo-shadows", "hra")]:
    tracked = git_ls(os.path.join(WS, repo))
    allfiles = set(os.path.relpath(f, os.path.join(WS, root)).replace("\\", "/")
                   for f in walk(os.path.join(WS, root)))
    on_disk = set(f for f in allfiles if not f.startswith(GEN_PREFIX))
    untracked = sorted(on_disk - tracked)
    missing = sorted(tracked - on_disk)
    gen = len(allfiles) - len(on_disk)
    print(f"ZMERENO: {label} git-ls-files={len(tracked)} na-disku-bez-generovanych={len(on_disk)} "
          f"generovanych={gen} netrackovano={len(untracked)} chybi-na-disku={len(missing)}")
    for f in untracked[:60]:
        print(f"  NETRACKOVANO: {f}")
    if len(untracked) > 60:
        print(f"  ... a dalsich {len(untracked)-60}")
    for f in missing[:20]:
        print(f"  CHYBI-NA-DISKU: {f}")

# --- zdrojak: radky ---
print("\n=== VELIKOST ZDROJAKU ===")
for p in ["orchestra/conductor/src/index.ts", "orchestra/conductor/schema.sql",
          "orchestra/conductor/wrangler.toml", "orchestra/repo/.forge/roadmap.json"]:
    fp = os.path.join(WS, p)
    if os.path.exists(fp):
        b = open(fp, "rb").read()
        nl = b.count(10)
        radku = nl if b.endswith(b"\n") else nl + 1
        print(f"ZMERENO: {p} radku={radku} bajtu={len(b)} sha256={hashlib.sha256(b).hexdigest()[:12]}")
    else:
        print(f"ZMERENO: {p} NEEXISTUJE")
