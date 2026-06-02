$ErrorActionPreference = "Continue"

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

Write-Host "Paper asset worker stopped."
