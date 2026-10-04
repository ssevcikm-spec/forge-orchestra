# List entries of an Electron .asar archive header (no extraction).
# Usage: pwsh -File asar-list.ps1 <path-to-asar> [regex-filter]
param(
  [Parameter(Mandatory=$true)][string]$Asar,
  [string]$Filter = '.'
)
$fs = [System.IO.File]::OpenRead($Asar)
$br = New-Object System.IO.BinaryReader($fs)
# asar = Pickle: [u32 size=4][u32 headerSize][u32 headerStringSize(+pad?)][u32 jsonLen][json bytes]
$null = $br.ReadUInt32()      # 4
$headerSize = $br.ReadUInt32()  # pickle payload size
$null = $br.ReadUInt32()      # header string size field
$jsonLen = $br.ReadUInt32()   # actual json byte length
$hdr = New-Object byte[] $jsonLen
$read = 0
while ($read -lt $jsonLen) {
  $n = $br.Read($hdr, $read, $jsonLen - $read)
  if ($n -le 0) { break }
  $read += $n
}
$fs.Close()
Write-Output "headerSize=$headerSize jsonLen=$jsonLen read=$read"
$json = [System.Text.Encoding]::UTF8.GetString($hdr)
$obj = $json | ConvertFrom-Json

$script:results = New-Object System.Collections.ArrayList
function Walk($node, $prefix) {
  foreach ($p in $node.PSObject.Properties) {
    $v = $p.Value
    if ($null -ne $v.files) { Walk $v.files ("$prefix" + $p.Name + "/") }
    else { [void]$script:results.Add( ("{0}{1}|off={2}|size={3}" -f $prefix, $p.Name, $v.offset, $v.size) ) }
  }
}
Walk $obj.files ""
Write-Output "TOTAL ENTRIES: $($script:results.Count)"
$script:results | Where-Object { $_ -match $Filter } | ForEach-Object { Write-Output $_ }
