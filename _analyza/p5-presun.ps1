# P5 — PRESUN NA E: (Godot -> E:\Tools\godot, oba stromy -> E:\Workspaces)
#
# ⚠ ZAMERNE NE /MOVE: pouziva se KOPIE -> OVERENI -> SMAZANI ZDROJE.
# Duvod: /MOVE maze prubezne, takze selhani uprostred necha strom na OBOU
# mistech a neda se rict, co je kde. Takhle je zdroj nedotceny, dokud cil
# nesedi na pocet souboru A na bajty (dva nezavisle pohledy).
#
# Postup:
#   0) predpoklad: E: cile existuji a jsou prazdne
#   1) E:\Tools\godot   <- orchestra\tools\godot          (D7)
#   2) E:\Workspaces\forge-orchestra <- orchestra
#   3) E:\Workspaces\uo-shadows     <- games\uo-shadows
#   4) overeni kazdeho kroku: pocet souboru + bajty
#
# Zapisuje UTF-8 BOM + CRLF (viz skill dsh-prostredi) — ale pousti se inline
# pres `pwsh -Command` s teckovanim, proto BOM neni kriticky; parser se overi.

$ErrorActionPreference = 'Stop'
$WS = 'C:\Users\Ssevc\Local-Deepseek'
$log = @()

function Zapis($text) {
    Write-Host $text
    $script:log += $text
}

function MěřStrom($cesta) {
    if (-not (Test-Path -LiteralPath $cesta)) { return $null }
    $f = Get-ChildItem -LiteralPath $cesta -Recurse -File -Force -ErrorAction SilentlyContinue
    $b = ($f | Measure-Object -Property Length -Sum).Sum
    if ($null -eq $b) { $b = 0 }
    return [pscustomobject]@{ Souboru = $f.Count; Bajtu = [int64]$b }
}

function Presun($zdroj, $cil, $jmeno) {
    Zapis "=== $jmeno ==="
    Zapis "  zdroj: $zdroj"
    Zapis "  cil:   $cil"

    if (-not (Test-Path -LiteralPath $zdroj)) { throw "ZDROJ NEEXISTUJE: $zdroj" }
    if (Test-Path -LiteralPath $cil) {
        $stav = (Get-ChildItem -LiteralPath $cil -Force -ErrorAction SilentlyContinue).Count
        if ($stav -gt 0) { throw "CIL NENI PRAZDNY ($stav polozek): $cil" }
    } else {
        New-Item -ItemType Directory -Path $cil -Force | Out-Null
        Zapis "  (cil vytvoren)"
    }

    $pred = MěřStrom $zdroj
    Zapis "  PRED: $($pred.Souboru) souboru, $([math]::Round($pred.Bajtu/1MB,1)) MB"

    # /E vc. podadresaru, /XJ preskoc junctiony, /R:1 /W:1 at to nevisi
    $r = robocopy $zdroj $cil /E /XJ /R:1 /W:1 /NFL /NDL /NJH /NJS /NP
    $kod = $LASTEXITCODE
    Zapis "  robocopy exit: $kod  (<8 = uspech)"

    $pocitadlo = MěřStrom $cil
    Zapis "  PO:   $($pocitadlo.Souboru) souboru, $([math]::Round($pocitadlo.Bajtu/1MB,1)) MB"

    if ($pocitadlo.Souboru -ne $pred.Souboru) {
        throw "NESEDI POCET SOUBORU: zdroj=$($pred.Souboru) cil=$($pocitadlo.Souboru) — ZDROJ SE NEMAZE"
    }
    if ($pocitadlo.Bajtu -ne $pred.Bajtu) {
        throw "NESEDI BAJTY: zdroj=$($pred.Bajtu) cil=$($pocitadlo.Bajtu) — ZDROJ SE NEMAZE"
    }
    Zapis "  OVERENO: pocet souboru I bajty sedi -> zdroj se maze"

    Remove-Item -LiteralPath $zdroj -Recurse -Force
    if (Test-Path -LiteralPath $zdroj) { throw "ZDROJ SE NEPODARILO SMAZAT: $zdroj" }
    Zapis "  zdroj smazan: $zdroj"
    Zapis ""

    return [pscustomobject]@{ Jmeno = $jmeno; Souboru = $pocitadlo.Souboru; MB = [math]::Round($pocitadlo.Bajtu/1MB,1) }
}

$vysledky = @()

# 1) Godot jako obecny nastroj stanice (D7)
New-Item -ItemType Directory -Path 'E:\Tools' -Force | Out-Null
$vysledky += Presun "$WS\orchestra\tools\godot" 'E:\Tools\godot' 'godot'

# 2) orchestra
$vysledky += Presun "$WS\orchestra" 'E:\Workspaces\forge-orchestra' 'orchestra'

# 3) hra
$vysledky += Presun "$WS\games\uo-shadows" 'E:\Workspaces\uo-shadows' 'hra'

Zapis "=== SOUHRN ==="
foreach ($v in $vysledky) { Zapis ("  {0,-10} {1,6} souboru  {2,9} MB" -f $v.Jmeno, $v.Souboru, $v.MB) }

$log | Set-Content -LiteralPath "$WS\_analyza\p5-presun-log.txt" -Encoding utf8
Zapis ""
Zapis "HOTOVO — log: $WS\_analyza\p5-presun-log.txt"
