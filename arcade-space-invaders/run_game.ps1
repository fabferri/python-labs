$ErrorActionPreference = 'Stop'

if (-not (Test-Path .venv)) {
    Write-Host 'Virtual environment not found. Run .\\setup_venv.ps1 first.'
    exit 1
}

. .\.venv\Scripts\Activate.ps1
python main.py
