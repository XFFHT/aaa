param(
  [string]$TargetRoot = "D:\HermesRAG",
  [switch]$InstallPythonDeps
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$PaperAssetSource = Join-Path $RepoRoot "src\paper-asset"
$ScriptsSource = Join-Path $RepoRoot "scripts"
$SkillsSource = Join-Path $RepoRoot "skills"

$PaperAssetTarget = Join-Path $TargetRoot "paper-asset"
$ScriptsTarget = Join-Path $TargetRoot "scripts"
$SkillsTarget = Join-Path $TargetRoot "skills"

New-Item -ItemType Directory -Force -Path `
  $TargetRoot, `
  $PaperAssetTarget, `
  $ScriptsTarget, `
  $SkillsTarget, `
  (Join-Path $TargetRoot "logs"), `
  (Join-Path $TargetRoot "downloads"), `
  (Join-Path $TargetRoot "teacher-files") | Out-Null

Copy-Item -Recurse -Force (Join-Path $PaperAssetSource "*") $PaperAssetTarget
Copy-Item -Recurse -Force (Join-Path $ScriptsSource "*") $ScriptsTarget
Copy-Item -Recurse -Force (Join-Path $SkillsSource "*") $SkillsTarget

$EnvExample = Join-Path $PaperAssetTarget ".env.example"
$EnvFile = Join-Path $PaperAssetTarget ".env"
if ((Test-Path $EnvExample) -and -not (Test-Path $EnvFile)) {
  Copy-Item $EnvExample $EnvFile
  Write-Host "Created env template: $EnvFile"
  Write-Host "Edit it before starting the worker."
}

if ($InstallPythonDeps) {
  $Requirements = Join-Path $PaperAssetTarget "requirements.txt"
  python -m pip install -r $Requirements
}

Write-Host ""
Write-Host "Installed to $TargetRoot"
Write-Host "Next:"
Write-Host "1. Edit $EnvFile"
Write-Host "2. Run: & $ScriptsTarget\start-paper-asset-worker.ps1"
