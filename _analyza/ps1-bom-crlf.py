"""Prepis .ps1 na UTF-8 BOM + jednotne CRLF (bajty, ne text) a over parserem.

PROC: skill `dsh-prostredi` §3 — bez BOM cte PowerShell .ps1 jako cp1252 a
ceske znaky se rozsypou (parser pak hlasi chybu na radku, ktery v souboru
neni). `write_text()` navic umi vyrobit dvojite \\r. Zapisuje se proto BAJTY.

Pouziti: python _analyza\ps1-bom-crlf.py <soubor.ps1> [<dalsi.ps1> ...]
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if not argv:
        print("pouziti: ps1-bom-crlf.py <soubor.ps1> ...")
        return 2
    chyba = False
    for cesta in argv:
        p = Path(cesta)
        if not p.exists():
            print(f"CHYBI: {p}")
            chyba = True
            continue
        surovy = p.read_bytes()
        text = surovy.decode("utf-8-sig")
        # sjednotit vsechny konce radku na CRLF
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        nove = "\ufeff" + text.replace("\n", "\r\n")
        p.write_bytes(nove.encode("utf-8"))
        # overeni: kolik CRLF a kolik osamocenych CR/LF
        zpet = p.read_bytes()
        crlf = zpet.count(b"\r\n")
        lf_sam = zpet.count(b"\n") - crlf
        cr_sam = zpet.count(b"\r") - crlf
        bom = zpet[:3] == b"\xef\xbb\xbf"
        print(f"{p.name}: BOM={bom} CRLF={crlf} osamocenych_LF={lf_sam} "
              f"osamocenych_CR={cr_sam} ({len(zpet)} B)")
        if not bom or lf_sam or cr_sam:
            print("  ⚠ KODOVANI/KONCE RADKU NEJSOU V PORADKU")
            chyba = True

    # over parserem (Windows PowerShell)
    for cesta in argv:
        p = Path(cesta)
        if not p.exists():
            continue
        prikaz = (
            "$e=$null; $t=$null; "
            f"[void][System.Management.Automation.Language.Parser]::ParseFile("
            f"'{p}',[ref]$t,[ref]$e); "
            "if($e.Count -eq 0){'PARSER OK: ' + [IO.Path]::GetFileName('" + str(p) + "')}"
            "else{ $e | ForEach-Object { 'CHYBA: ' + $_.Message + ' @ ' + $_.Extent.StartLineNumber } }"
        )
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", prikaz],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        vystup = (r.stdout or "").strip()
        if (r.stderr or "").strip():
            vystup += " | STDERR: " + r.stderr.strip()[:400]
        print(vystup)
        if "CHYBA" in vystup:
            chyba = True
    return 1 if chyba else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
