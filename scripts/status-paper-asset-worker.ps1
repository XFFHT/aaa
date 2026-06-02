$ErrorActionPreference = "Continue"

Write-Host "Windows paper asset worker process:"
$procs = Get-CimInstance Win32_Process |
  Where-Object {
    $_.Name -eq "python.exe" -and
    $_.CommandLine -like "*uvicorn*" -and
    $_.CommandLine -like "*worker:app*" -and
    $_.CommandLine -like "*18766*"
  }
if ($procs) {
  $procs | Select-Object ProcessId, CommandLine | Format-Table -AutoSize
} else {
  Write-Host "(none)"
}

Write-Host ""
Write-Host "Local worker health:"
curl.exe -sS --max-time 8 http://127.0.0.1:18766/health 2>&1
