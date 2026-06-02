$ErrorActionPreference = "Continue"

$Key = if ($env:HERMES_TUNNEL_KEY) { $env:HERMES_TUNNEL_KEY } else { "D:\path\to\server_tunnel_rsa" }
$Server = if ($env:HERMES_SERVER) { $env:HERMES_SERVER } else { "root@YOUR_SERVER_IP" }
$ServerHost = ($Server -split "@")[-1]

Write-Host "Windows teacher-file receiver process:"
$receiverProcs = Get-CimInstance Win32_Process |
  Where-Object {
    $_.Name -eq "python.exe" -and
    $_.CommandLine -like "*teacher_file_receiver.py*"
  }
if ($receiverProcs) {
  $receiverProcs | Select-Object ProcessId, CommandLine | Format-Table -AutoSize
} else {
  Write-Host "(none)"
}

Write-Host ""
Write-Host "Local archive receiver health:"
curl.exe -sS --max-time 5 http://127.0.0.1:18765/healthz 2>&1

Write-Host ""
Write-Host "Local paper asset worker health:"
curl.exe -sS --max-time 8 http://127.0.0.1:18766/health 2>&1

Write-Host ""
Write-Host "Windows SSH tunnel process:"
$tunnelProcs = Get-CimInstance Win32_Process |
  Where-Object {
    $_.Name -eq "ssh.exe" -and
    $_.CommandLine -like "*19380:127.0.0.1:9380*" -and
    $_.CommandLine -like "*$ServerHost*"
  }
if ($tunnelProcs) {
  $tunnelProcs | Select-Object ProcessId, CommandLine | Format-Table -AutoSize
} else {
  Write-Host "(none)"
}

Write-Host ""
Write-Host "Server-side port check:"
ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=NUL -i $Key $Server "ss -ltnp | grep -E ':18080|:19380|:19382|:18765|:18766|:15128' || true; curl -I --max-time 10 http://127.0.0.1:18080 2>&1 || true; curl -I --max-time 10 http://127.0.0.1:19380 2>&1 || true; curl -sS --max-time 10 http://127.0.0.1:18765/healthz 2>&1 || true; curl -sS --max-time 10 http://127.0.0.1:18766/health 2>&1 || true; curl -sS --max-time 10 http://127.0.0.1:15128/api/health 2>&1 || true"
