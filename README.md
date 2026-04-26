# Simulador Radar UNEFA

Aplicación de escritorio desarrollada en Python y PySide6 para simular el monitoreo y control básico de múltiples tecnologías autónomas dentro de una interfaz gráfica tipo radar.

## Características de esta primera versión
- Interfaz oscura tipo centro de monitoreo.
- Radar 2D con círculos concéntricos y zona de vigilancia.
- Creación de unidades autónomas simuladas.
- Selección de unidades desde el radar.
- Asignación de objetivos mediante clic sobre el radar.
- Movimiento en tiempo real con control proporcional simple.
- Trayectoria histórica visible.
- Panel lateral con variables básicas de la unidad seleccionada.
- Alertas por batería baja, fuera de zona y objetivo alcanzado.
- Modos operativos iniciales: defensivo, reconocimiento y mixto.

## Requisitos
- Python 3.11 o superior recomendado.
- PySide6.

## Instalación
```bash
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecución
```bash
python main.py
```

### Ejecución fácil (recomendado)

Sin activar el entorno (ideal para PowerShell/VS Code):

```bash
.\run.bat
```

Si quieres forzar reinstalación de dependencias:

```bash
.\run.bat --reinstall
```

O con PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

## Uso básico
1. Ejecutar la aplicación.
2. Pulsar `Crear unidad` una o más veces.
3. Seleccionar una unidad en el radar.
4. Pulsar `Asignar objetivo`.
5. Hacer clic dentro del radar para fijar el waypoint.
6. Pulsar `Iniciar` para comenzar la simulación.
7. Usar `Pausar` o `Reiniciar` según sea necesario.
8. Cambiar el modo operativo desde el selector lateral para distribuir objetivos automáticos.

## Estructura del proyecto
```text
tesis_simulador/
├─ main.py
├─ app/
│  ├─ ui/
│  ├─ domain/
│  ├─ simulation/
│  ├─ services/
│  └─ config/
├─ requirements.txt
└─ README.md
```

## Alcance actual
Esta versión no incluye base de datos, exportación de reportes, mapas reales, GPS real, hardware físico, PID ni simulación 3D. El objetivo es ofrecer una base funcional, modular y defendible para la tesis.
