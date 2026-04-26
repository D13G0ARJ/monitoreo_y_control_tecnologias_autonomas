@echo off
setlocal
cd /d %~dp0

set "REINSTALL=0"
if /I "%~1"=="--reinstall" set "REINSTALL=1"

if not exist .venv\Scripts\python.exe (
  echo Creando entorno virtual .venv...
  py -m venv .venv 2>nul || python -m venv .venv || (
    echo ERROR: No se pudo crear el entorno virtual.
    echo Verifica que Python este instalado y en PATH.
    exit /b 1
  )
)

if "%REINSTALL%"=="1" (
  echo Reinstalando dependencias...
  .\.venv\Scripts\python.exe -m pip install --upgrade pip || exit /b 1
  .\.venv\Scripts\python.exe -m pip install --force-reinstall -r requirements.txt || exit /b 1
) else (
  .\.venv\Scripts\python.exe -c "import PySide6" >nul 2>nul
  if errorlevel 1 (
    echo Instalando dependencias iniciales...
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt || exit /b 1
  ) else (
    echo Entorno listo. Omitiendo instalacion de dependencias.
  )
)

echo Ejecutando app...
.\.venv\Scripts\python.exe main.py
