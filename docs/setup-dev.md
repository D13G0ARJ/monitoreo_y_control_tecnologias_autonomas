# Setup del entorno de desarrollo

Este documento describe cómo preparar el entorno local para ejecutar el proyecto en **Linux** y **Windows**.

El proyecto es una aplicación de escritorio en Python con interfaz gráfica, simulación local y entrada principal en:

```text
main.py
```

---

## 1. Objetivo del setup

El objetivo del setup es preparar el proyecto para que pueda ejecutarse localmente sin instalar dependencias en el Python global del sistema.

Se busca:

- usar una versión controlada de Python;
- crear un entorno virtual local `.venv`;
- instalar las dependencias desde `requirements.txt`;
- ejecutar la aplicación desde `main.py`;
- evitar que archivos locales se suban al repositorio.

---

## 2. Herramientas recomendadas

```text
Python 3.12
uv
PySide6
```

`uv` permite manejar versiones de Python, entornos virtuales y dependencias de forma rápida y aislada.

No se recomienda instalar dependencias directamente en el Python global del sistema operativo.

---

## 3. Instalación y ejecución en Linux

### 3.1. Scripts Actuales del proyecto

Scripts disponibles: `setup.sh` (instala dependencias), `run.sh` (ejecuta la app) y `env.sh` (activa el entorno).

Desde la raíz del proyecto, dar permisos de ejecución:

```bash
chmod +x setup.sh run.sh env.sh
```

Primera instalación:

```bash
./setup.sh
```

Ejecutar la aplicación:

```bash
./run.sh
```

Ejecutar pruebas:

```bash
./test.sh
```

Ejecutar una corrida headless reproducible:

```bash
uv run python main.py --headless --scenario "Protección de zona estratégica" --duration 30 --seed 1 --out run_output
```

Activar el entorno para desarrollo manual:

```bash
source ./env.sh
```

Nota: `env.sh` solo activa el entorno virtual existente. No instala dependencias ni ejecuta la aplicación.

---

### 3.2. Instalación manual en Linux

Desde la raíz del proyecto:

```bash
uv python pin 3.12
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
python main.py
```

Ejecución sin activar manualmente el entorno:

```bash
uv run python main.py
```

Corrida headless con exportación:

```bash
uv run python main.py --headless --scenario "Protección de zona estratégica" --duration 30 --seed 1 --time-scale 1 --out run_output
```

---

## 4. Instalación y ejecución en Windows

### 4.1. Instalación manual en PowerShell

Desde la raíz del proyecto:

```powershell
uv python pin 3.12
uv venv --python 3.12
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
python main.py
```

Ejecución sin activar manualmente el entorno:

```powershell
uv run python main.py
```

---

### 4.2. Nota sobre políticas de ejecución en PowerShell

Si PowerShell bloquea la activación del entorno virtual, habilita la ejecución solo en la sesión actual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Luego activa el entorno:

```powershell
\.venv\Scripts\Activate.ps1
```

---

## 5. Flujo recomendado

### Linux

Primera vez:

```bash
./setup.sh
./run.sh
```

Uso diario:

```bash
./run.sh
```

Cuando cambie `requirements.txt`:

```bash
./setup.sh
```

Para trabajar manualmente dentro del entorno:

```bash
source ./env.sh
```

Para salir del entorno:

```bash
deactivate
```

---

### Windows

Primera vez:

```powershell
uv python pin 3.12
uv venv --python 3.12
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
python main.py
```

Uso diario:

```powershell
uv run python main.py
```

Pruebas:

```powershell
uv run --group dev pytest
```

Cuando cambie `requirements.txt`:

```powershell
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

Para salir del entorno:

```powershell
deactivate
```

---

## 6. Verificación del entorno

### Linux

```bash
source ./env.sh
which python
python --version
```

Resultado esperado:

```text
.../.venv/bin/python
Python 3.12.x
```

### Verificación del proyecto

Desde la raíz del proyecto:

```bash
./test.sh
uv run --group dev ruff check app tests
uv run python main.py --headless --scenario "Protección de zona estratégica" --duration 5 --seed 1 --out /tmp/radar_check
```

La corrida headless debe crear:

- `timeseries.csv`;
- `summary.json`.

---

### Windows

```powershell
.\.venv\Scripts\Activate.ps1
where python
python --version
```

Resultado esperado:

```text
...\monitoreo_y_control_tecnologias_autonomas\.venv\Scripts\python.exe
Python 3.12.x
```

---
