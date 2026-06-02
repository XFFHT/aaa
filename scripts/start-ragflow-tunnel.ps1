$ErrorActionPreference = "Stop"

$Root = "D:\HermesRAG"
$LogDir = Join-Path $Root "logs"
$OutLog = Join-Path $LogDir "ragflow-tunnel.out.log"
$ErrLog = Join-Path $LogDir "ragflow-tunnel.err.log"
$ReceiverOutLog = Join-Path $LogDir "teacher-file-receiver.out.log"
$ReceiverErrLog = Join-Path $LogDir "teacher-file-receiver.err.log"
$ReceiverScript = Join-Path $Root "scripts\teacher_file_receiver.py"
$TeacherFilesRoot = Join-Path $Root "teacher-files"
$PaperWorkerScript = Join-Path $Root "scripts\start-paper-asset-worker.ps1"
$Key = if ($env:HERMES_TUNNEL_KEY) { $env:HERMES_TUNNEL_KEY } else { "D:\path\to\server_tunnel_rsa" }
$Server = if ($env:HERMES_SERVER) { $env:HERMES_SERVER } else { "root@YOUR_SERVER_IP" }
$ServerHost = ($Server -split "@")[-1]
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
New-Item -ItemType Directory -Force -Path $TeacherFilesRoot | Out-Null

& $PaperWorkerScript

$receiver = Get-CimInstance Win32_Process |
  Where-Object {
    $_.Name -eq "python.exe" -and
    $_.CommandLine -like "*teacher_file_receiver.py*"
  }

if (-not $receiver) {
  Start-Process `
    -FilePath "python.exe" `
    -ArgumentList @($ReceiverScript, "--host", "127.0.0.1", "--port", "18765", "--root", $TeacherFilesRoot) `
    -WindowStyle Hidden `
    -RedirectStandardOutput $ReceiverOutLog `
    -RedirectStandardError $ReceiverErrLog
  Start-Sleep -Seconds 1
  Write-Host "Teacher file receiver started: http://127.0.0.1:18765"
} else {
  Write-Host "Teacher file receiver is already running."
}

$existing = Get-CimInstance Win32_Process |
  Where-Object {
    $_.Name -eq "ssh.exe" -and
    $_.CommandLine -like "*19380:127.0.0.1:9380*" -and
    $_.CommandLine -like "*$ServerHost*"
  }

if ($existing) {
  $hasArchiveForward = $existing | Where-Object { $_.CommandLine -like "*18765:127.0.0.1:18765*" }
  $hasTeacherResourceForward = $existing | Where-Object { $_.CommandLine -like "*15128:127.0.0.1:5128*" }
  $hasPaperAssetForward = $existing | Where-Object { $_.CommandLine -like "*18766:127.0.0.1:18766*" }
  if ($hasArchiveForward -and $hasTeacherResourceForward -and $hasPaperAssetForward) {
    Write-Host "RAGFlow tunnel is already running."
    exit 0
  }

  Write-Host "Restarting old RAGFlow tunnel to add archive, teacher-resource and paper-asset forwarding..."
  $existing | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
  Start-Sleep -Seconds 2
}

Start-Process `
  -FilePath "ssh.exe" `
  -ArgumentList @(
    "-N",
    "-T",
    "-o", "ExitOnForwardFailure=yes",
    "-o", "ServerAliveInterval=30",
    "-o", "ServerAliveCountMax=3",
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=NUL",
    "-i", $Key,
    "-R", "127.0.0.1:18080:127.0.0.1:8080",
    "-R", "127.0.0.1:19380:127.0.0.1:9380",
    "-R", "127.0.0.1:19382:127.0.0.1:9382",
    "-R", "127.0.0.1:18765:127.0.0.1:18765",
    "-R", "127.0.0.1:18766:127.0.0.1:18766",
    "-R", "127.0.0.1:15128:127.0.0.1:5128",
    $Server
  ) `
  -WindowStyle Hidden `
  -RedirectStandardOutput $OutLog `
  -RedirectStandardError $ErrLog

Write-Host "RAGFlow tunnel started."
Write-Host "Server API: http://127.0.0.1:19380"
Write-Host "Server archive receiver: http://127.0.0.1:18765/store"
Write-Host "Server paper asset worker: http://127.0.0.1:18766"
Write-Host "Server teacher-resource API: http://127.0.0.1:15128/api"
