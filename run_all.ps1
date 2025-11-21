
param(
  [int[]] $Ns        = @(200, 500, 1000),
  [string[]] $Ds     = @("0.01","0.05","0.10","0.20"),
  [int] $Repeat      = 3,
  [int] $Seed        = 1,
  [string] $OutRoot  = "results"
)
New-Item -ItemType Directory -Path $OutRoot -Force | Out-Null

function Run-One($n, $ds, $repeat, $seed) {
  $dtag = ($ds -replace '\.','p')
  $dir  = Join-Path $OutRoot ("n{0}\d{1}" -f $n, $dtag)
  New-Item -ItemType Directory -Path $dir -Force | Out-Null
  $outCsv = Join-Path $dir "bench.csv"
  Write-Host ("[bench] n={0} d={1} -> {2}" -f $n, $ds, $outCsv)
  python bench.py --n $n --density $ds --repeat $repeat --out $outCsv --seed $seed
}

foreach ($n in $Ns)   { foreach ($ds in $Ds)   { Run-One $n $ds $Repeat $Seed } }

$summary = Join-Path $OutRoot "summary.csv"
"n,density,case,ms" | Set-Content $summary -Encoding ASCII
Get-ChildItem -Path $OutRoot -Recurse -Filter bench.csv | ForEach-Object {
  $rel = $_.FullName.Substring((Resolve-Path $OutRoot).Path.Length+1)
  if ($rel -match 'n(\d+)\\d([0-9p]+)\\bench\.csv') {
    $n = $matches[1]
    $d = ($matches[2] -replace 'p','.') ; $d = ("0{0}" -f $d)
    Get-Content $_.FullName | Select-Object -Skip 1 | ForEach-Object {
      if ($_ -ne "") { Add-Content -Path $summary -Value ("{0},{1},{2}" -f $n,$d,$_ ) }
    }
  }
}
Write-Host ("[done] summary -> {0}" -f $summary)
