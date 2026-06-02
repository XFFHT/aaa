$ErrorActionPreference = "Stop"

$Root = "D:\HermesRAG"
$WorkerDir = Join-Path $Root "paper-asset"
$LogDir = Join-Path $Root "logs"
$OutLog = Join-Path $LogDir "paper-asset-worker.out.log"
$ErrLog = Join-Path $LogDir "paper-asset-worker.err.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$existing = Get-CimInstance Win32_Process |
  Where-Object {
    $_.Name -eq "python.exe" -and
    $_.CommandLine -like "*uvicorn*" -and
    $_.CommandLine -like "*worker:app*" -and
    $_.CommandLine -like "*18766*"
  }

if ($existing) {
  Write-Host "Paper asset worker is already running."
  exit 0
}

Start-Process `
  -FilePath "python.exe" `
  -ArgumentList @("-m", "uvicorn", "worker:app", "--host", "127.0.0.1", "--port", "18766", "--timeout-keep-alive", "30") `
  -WorkingDirectory $WorkerDir `
  -WindowStyle Hidden `
  -RedirectStandardOutput $OutLog `
  -RedirectStandardError $ErrLog

Start-Sleep -Seconds 2
Write-Host "Paper asset worker started: http://127.0.0.1:18766"
curl.exe -sS --max-time 8 http://127.0.0.1:18766/health
