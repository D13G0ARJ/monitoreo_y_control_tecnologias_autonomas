# Diseño — Mejoras del Simulador Radar (UNEFA)

Fecha: 2026-05-17
Estado: aprobado
Alcance: una sola especificación, ejecución por fases. Fases independientes y commit-eables por separado.

## Principios invariables

- El `SimulationEngine` es la única fuente de verdad; los servicios son stateless-ish; la UI es de solo lectura sobre señales.
- Toda constante nueva va en `app/config/settings.py`. No hay números mágicos fuera de allí.
- Todos los módulos usan `from __future__ import annotations` y type hints.
- Dependencia de runtime: solo PySide6 (QtCharts forma parte del wheel de PySide6, no es dependencia nueva). Dependencias de desarrollo (ruff, pytest) separadas.
- Todo texto de UI y documentación en español.

## Fase 0 — Correcciones (sin cambio de comportamiento)

- `app/services/alert_service.py`: eliminar la rama inalcanzable de `ALERT_OUT_OF_ZONE` (segundo `if` muerto en `_resolve_severity`).
- `app/config/settings.py`: eliminar el alias redundante `LOW_BATTERY_THRESHOLD`; conservar `DEFAULT_LOW_BATTERY_THRESHOLD` (actualizar referencias).
- Extraer números mágicos a constantes nombradas en `settings.py`:
  - `BATTERY_DRAIN_DT_SCALE = 10.0` (usado en `_drain_battery`).
  - `SEPARATION_CORRECTION_GAIN = 0.12` (usado en `_apply_separation_correction`).
  - `PATROL_ORBIT_FACTOR = 0.68` (usado en `_assign_defensive_patrol`).
  - Factores recon: `RECON_X_FACTOR = 0.68`, `RECON_TOP_FACTOR = 0.52`, `RECON_BOTTOM_FACTOR = 0.48`, `RECON_STEP_FACTOR = 0.23`.
  - Spawn: `SPAWN_MIN_RADIUS = 25.0`, `SPAWN_MAX_RADIUS_FACTOR = 0.45`.
- Eliminar `SimulationEngine.apply_scenario()` (no referenciado; la ruta de UI usa `configure_scenario_from_dialog`). Verificar ausencia de referencias antes de borrar.
- `pause()` / `start()`: tomar snapshot del estado por unidad antes de pausar y restaurarlo al iniciar, para que los paneles no queden con estado obsoleto.

## Fase 1 — Tooling + pruebas

- `pyproject.toml`: configuración de `ruff` y `pytest` (dependencias de desarrollo). Runtime sigue solo-PySide6.
- `tests/`: pruebas de lógica pura sin Qt:
  - `control.move_toward_waypoint`
  - `mode_service` (generación de rutas patrulla/recon, `advance_unit_route`)
  - `alert_service`
  - `swarm_service`
  - lógica RTB (Fase 2)
- `setup.sh`: paso opcional para instalar dependencias de desarrollo. `run.sh` sin cambios. Nuevo `test.sh` (`uv run pytest`).

## Fase 2 — Retorno a base + recarga (RTB)

- Nuevo `app/services/battery_service.py` (`BatteryService`, stateless): decide disparo de RTB, ruteo a base y recarga.
- `AutonomousUnit` gana flags `is_returning: bool`, `is_charging: bool`; reutiliza `mission_snapshot`. `reset()` los limpia.
- Lógica:
  1. `battery < low_battery_threshold` y la unidad no está ya en RTB ni en control manual → snapshot de misión (vía `_build_mission_snapshot`), ruta a `BASE_POSITION` (0,0), estado `STATUS_REGRESANDO`.
  2. Al alcanzar base (tolerancia existente) → estado `STATUS_RECARGANDO`, `is_charging = True`, velocidad 0.
  3. Recargar a razón `RECHARGE_RATE` por segundo hasta 100% → restaurar misión vía `_restore_mission`, limpiar flags.
- Interacción con `_apply_battery_speed_policy`: en RTB la política de velocidad crítica no aplica freno adicional (la unidad debe poder volver). RTB tiene prioridad sobre la asignación de modo automático; no interrumpe `TASK_MANUAL`.
- Nuevas constantes: `BASE_POSITION = (0.0, 0.0)`, `RECHARGE_RATE` (%/s), umbral de salida de recarga `RECHARGE_FULL = 100.0`.
- Nuevos estados: `STATUS_REGRESANDO = "regresando a base"`, `STATUS_RECARGANDO = "recargando"`; colores asociados en `settings.py`.
- Nuevas alertas severidad INFO: inicio RTB, recarga completa.
- Pruebas unitarias del `BatteryService` (Fase 1 cubre el archivo de tests).

## Fase 3 — Métricas + exportación + modo headless

- Nuevo `app/services/metrics_service.py` (`MetricsService`): acumula por unidad distancia recorrida, número de objetivos/misiones completadas, tiempo al primer objetivo, conteo de alertas por severidad, muestras de batería. El engine lo invoca cada tick (sin acoplar UI).
- Nuevo `app/io/exporter.py`: escribe `timeseries.csv` (por tick: tiempo sim, id unidad, x, y, batería, estado) y `summary.json` (distancias, % de completitud de misión, conteos de alerta, tiempo al primer objetivo, parámetros del escenario).
- UI: botón "Exportar informe" en la ventana de control → diálogo de carpeta → escribe ambos archivos.
- Headless: reestructurar entrypoints. Nuevo `app/runtime/engine_builder.py` que construye y configura un `SimulationEngine` sin Qt-UI. `main.py` parsea args:
  - `--headless --scenario <nombre> --duration <segundos> [--seed N] --out <carpeta>`
  - Ejecuta un bucle de paso fijo (no `QTimer`) llamando a `update_simulation()` con `dt` constante; `--seed` fija `random.seed` para reproducibilidad; escribe CSV+JSON al final.
  - Sin `--headless`: comportamiento actual (ventanas Qt).
- Restricción: los módulos `app/ui/*` no deben importarse en la ruta headless.

## Fase 4 — Control de tiempo

- `SimulationEngine.time_scale` (1, 2, 4, 8). El intervalo del `QTimer` queda fijo; el `dt` lógico se multiplica por `time_scale` en `update_simulation`.
- Selector (QComboBox) en el panel de parámetros de control; sincronizado vía señal `updated`.
- En headless, `--time-scale` opcional (default 1) afecta el `dt` del bucle.

## Fase 5 — Rendimiento del radar (redibujado incremental)

- `RadarView`: mantener `QGraphicsItem`s persistentes indexados por `unit.identifier` (elipse, anillo selección, etiqueta, waypoint, ruta, trayectoria). Por tick actualizar posición/pluma/pincel en lugar de `scene.clear()`.
- Elementos de escenario estáticos (zona protegida, puntos de observación, HUD, leyenda) se reconstruyen solo cuando cambia `scenario_visuals` (comparación por dict). El barrido (sweep) sigue en `drawForeground`.
- Manejo de unidades eliminadas: quitar sus items del scene.

## Fase 6 — Extras de UI

- Panel de lista de unidades en la ventana de control: click → `engine.set_selected_unit`; sincronizado con `selection_changed`.
- Panel QtCharts: gráficos en vivo de batería (promedio + unidad seleccionada) y conteo de alertas activas, alimentados por un buffer circular en `MetricsService`. Si la importación de `PySide6.QtCharts` falla en runtime, ocultar el panel y registrar aviso (degradación elegante; el resto sigue).
- Atajos de teclado: Espacio = iniciar/pausar, R = reiniciar, A = preparar asignación, Esc = cancelar asignación.
- Registro de eventos/alertas completo y desplazable con marca de tiempo de simulación (más allá de las últimas 10 actuales).
- Guardar/Cargar configuración de escenario en JSON (reutiliza los campos de `ScenarioApplicationConfig`).

## Pruebas

- Lógica pura → pytest (Fase 1 + RTB en Fase 2 + MetricsService en Fase 3).
- Qt/UI → smoke manual + corrida headless como verificación de integración.
- La corrida headless con `--seed` actúa como arnés de regresión determinista.

## Riesgos / notas

- Verificar import de `PySide6.QtCharts` al inicio de Fase 6; fallback documentado: ocultar panel, conservar CSV.
- La ruta headless no debe importar `app/ui/*` a nivel de módulo → la reestructuración de entrypoints (Fase 3) es prerrequisito de un headless limpio.
- Orden de ejecución = orden de fases. Dependencias: Fase 6 (charts) depende de Fase 3 (MetricsService); Fase 1 (tests) cubre incrementalmente fases posteriores.
- Todo texto de UI y documentación en español; dominio sigue siendo solo-simulación (sin hardware/GPS/mapas/BD real).
