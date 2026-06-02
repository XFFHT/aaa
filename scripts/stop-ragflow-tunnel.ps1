$ErrorActionPreference = "Continue"

$Server = if ($env:HERMES_SERVER) { $env:HERMES_SERVER } else { "root@YOUR_SERVER_IP" }
$ServerHost = ($Server -split "@")[-1]

Get-CimInstance Win32_Process |
  Where-Object {
    $_.Name -eq "ssh.exe" -and
    $_.CommandLine -like "*19380:127.0.0.1:9380*" -and
    $_.CommandLine -like "*$ServerHost*"
  } |
  ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force
  }

Get-CimInstance Win32_Process |
  Where-Object {
    $_.Name -eq "python.exe" -and
    $_.CommandLine -like "*teacher_file_receiver.py*"
  } |
  ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force
  }

Get-CimInstance Win32_Process |
  Where-Object {
    $_.Name -eq "python.exe" -and
    $_.CommandLine -like "*uvicorn*" -and
    $_.CommandLine -like "*worker:app*" -and
    $_.CommandLine -like "*18766*"
  } |
  ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force
  }

Write-Host "RAGFlow tunnel stopped."
Write-Host "Teacher file receiver stopped."
Write-Host "Paper asset worker stopped."
