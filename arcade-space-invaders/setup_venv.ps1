$ErrorActionPreference = 'Stop'

if (-not (Test-Path .venv)) {
    Write-Host 'Creating virtual environment (.venv)...'
    python -m venv .venv
}

Write-Host 'Activating virtual environment...'
. .\.venv\Scripts\Activate.ps1

Write-Host 'Installing dependencies...'
pip install -r requirements.txt

Write-Host 'Done. Run the game with: .\\run_game.ps1'
