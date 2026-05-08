# ============================================================
# Pacman Arcade - PowerShell Script
# ============================================================
param(
    [switch]$NoInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "[setup] Creating virtual environment..."

    if (Get-Command py -ErrorAction SilentlyContinue) {
        py -3 -m venv .venv
    }
    elseif (Get-Command python -ErrorAction SilentlyContinue) {
        python -m venv .venv
    }
    else {
        throw "Python was not found in PATH. Install Python 3 and try again."
    }
}

if (-not $NoInstall) {
    Write-Host "[setup] Installing requirements..."
    & $venvPython -m pip install -r requirements.txt
}

Write-Host "[run] Starting Pacman Arcade..."
& $venvPython main.py

