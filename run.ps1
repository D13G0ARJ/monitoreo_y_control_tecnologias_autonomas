Param(
    [switch]$Reinstall
)

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'

if (-not (Test-Path $venvPython)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        py -m venv .venv
    } else {
        python -m venv .venv
    }
}

if ($Reinstall) {
    Write-Host "Reinstalando dependencias..."
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install --force-reinstall -r requirements.txt
} else {
    try {
        & $venvPython -c "import PySide6" | Out-Null
        Write-Host "Entorno listo. Omitiendo instalacion de dependencias."
    } catch {
        Write-Host "Instalando dependencias iniciales..."
        & $venvPython -m pip install -r requirements.txt
    }
}

& $venvPython main.py
