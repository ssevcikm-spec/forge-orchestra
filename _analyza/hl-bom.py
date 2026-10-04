#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Overi stav BOM a koncu radku u souboru, ktere jsem editoval.

POZOR (past, na kterou jsem u toho narazil): `git show` pres PowerShell
(`> soubor`) zapise UTF-16LE a zmeni i prvni bajty - BOM se pak "nemeni"
jen zdanlive. Proto se vsechno cte v Pythonu s `shell=True` (git.cmd je
batch, ktery se bez shellu nespusti) a vyhodnocuje jako bajty.

Spusteni: $env:PYTHONIOENCODING='utf-8'; python _analyza\hl-bom.py
"""
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

GIT = r"C:\Users\Ssevc\Local-Deepseek\orchestra\tools\git.cmd"
BOM = bytes([0xEF, 0xBB, 0xBF])

SOUBORY = [
    ("games", r"C:\Users\Ssevc\Local-Deepseek\games\uo-shadows", "scripts/level.gd"),
    ("games", r"C:\Users\Ssevc\Local-Deepseek\games\uo-shadows", ".forge/check-schema.py"),
    ("orchestra", r"C:\Users\Ssevc\Local-Deepseek\orchestra", "repo/.forge/check-schema.py"),
    ("orchestra", r"C:\Users\Ssevc\Local-Deepseek\orchestra", "tools/validate-all.mjs"),
    ("orchestra", r"C:\Users\Ssevc\Local-Deepseek\orchestra", "tools/test-cooldown.py"),
]


def z_gitu(repo, rev, cesta):
    r = subprocess.run([GIT, "-C", repo, "show", f"{rev}:{cesta}"],
                       capture_output=True, shell=True)
    return r.stdout if r.returncode == 0 else b""


for reponame, repo, cesta in SOUBORY:
    print(f"\n== {reponame}/{cesta} ==")
    for rev in ("HEAD", ":0"):
        b = z_gitu(repo, rev, cesta)
        popis = "HEAD " if rev == "HEAD" else "index"
        if not b:
            print(f"   {popis}: (v gitu není)")
            continue
        crlf = b.count(b"\r\n")
        print(f"   {popis}: BOM={'ANO' if b[:3] == BOM else 'ne ':3s}  "
              f"CRLF={crlf:5d}  LF={b.count(chr(10).encode()) - crlf:5d}  {len(b):7d} B")
    try:
        with open(rf"{repo}\{cesta.replace('/', chr(92))}", "rb") as f:
            b = f.read()
        crlf = b.count(b"\r\n")
        print(f"   disk : BOM={'ANO' if b[:3] == BOM else 'ne ':3s}  "
              f"CRLF={crlf:5d}  LF={b.count(chr(10).encode()) - crlf:5d}  {len(b):7d} B")
    except FileNotFoundError:
        print("   disk : (soubor není)")
