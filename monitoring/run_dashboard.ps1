# PowerShell script to run dashboard with proper path handling
$ErrorActionPreference = "Stop"

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = (Get-Item $scriptDir).Parent.Parent.FullName

Write-Host "========================================"
Write-Host "Starting Agent Health Dashboard..."
Write-Host "========================================"
Write-Host ""

# Try to use .venv Python if it exists
$venvPython = Join-Path $workspaceRoot ".venv\Scripts\python.exe"
$scriptPath = Join-Path $scriptDir "dashboard-terminal.py"

if (Test-Path $venvPython) {
    Write-Host "Using virtual environment Python..."
    & $venvPython $scriptPath
} else {
    Write-Host "Using system Python..."
    python $scriptPath
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Dashboard failed to start"
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
