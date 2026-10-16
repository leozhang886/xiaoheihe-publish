$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$dataDir = Join-Path $projectRoot 'data'
$processFile = Join-Path $dataDir 'comment-watch-processes.json'

function Get-RunnerProcess([object]$runnerId, [string]$scriptName) {
  if (-not $runnerId) { return $null }
  $processInfo = Get-CimInstance Win32_Process -Filter "ProcessId=$runnerId" -ErrorAction SilentlyContinue
  if ($processInfo -and $processInfo.Name -eq 'node.exe' -and
      $processInfo.CommandLine -match [regex]::Escape($scriptName)) {
    return Get-Process -Id $runnerId -ErrorAction SilentlyContinue
  }
  return $null
}

New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
$saved = if (Test-Path -LiteralPath $processFile) {
  Get-Content -LiteralPath $processFile -Raw -Encoding UTF8 | ConvertFrom-Json
} else { $null }
$session = Get-RunnerProcess $saved.sessionPid 'session.mjs'
$watch = Get-RunnerProcess $saved.watchPid 'comments.mjs'
if ($session -and $watch) {
  Write-Host 'Auto replies are already running.'
  exit 0
}

$nodePath = (Get-Command node -ErrorAction Stop).Source
if (-not $session) {
  if (Get-NetTCPConnection -LocalPort 9222 -State Listen -ErrorAction SilentlyContinue) {
    throw 'Port 9222 is in use by another browser session.'
  }
  $session = Start-Process -FilePath $nodePath -ArgumentList @('session.mjs') `
    -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $dataDir 'comment-session.out.log') `
    -RedirectStandardError (Join-Path $dataDir 'comment-session.err.log')
  $ready = $false
  for ($attempt = 0; $attempt -lt 60; $attempt++) {
    if (Get-NetTCPConnection -LocalPort 9222 -State Listen -ErrorAction SilentlyContinue) {
      $ready = $true
      break
    }
    if ($session.HasExited) { break }
    Start-Sleep -Milliseconds 500
  }
  if (-not $ready) { throw 'Browser session did not start.' }
}

if (-not $watch) {
  $watch = Start-Process -FilePath $nodePath -ArgumentList @('comments.mjs', '--send', '--watch') `
    -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $dataDir 'comment-watch.out.log') `
    -RedirectStandardError (Join-Path $dataDir 'comment-watch.err.log')
}
@{ sessionPid = $session.Id; watchPid = $watch.Id; startedAt = (Get-Date).ToString('o') } |
  ConvertTo-Json | Set-Content -LiteralPath $processFile -Encoding UTF8
Start-Sleep -Seconds 10
if (-not (Get-RunnerProcess $watch.Id 'comments.mjs')) {
  throw 'Auto reply process stopped. Check data/comment-watch.err.log.'
}
Write-Host 'Auto replies are running.'
