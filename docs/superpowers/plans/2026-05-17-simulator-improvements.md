# Simulator Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add bug fixes, test tooling, return-to-base battery behavior, metrics/headless export, time-scale control, incremental radar rendering, and UI extras to the radar monitoring simulator.

**Architecture:** `SimulationEngine` stays the single source of truth; new behavior added as stateless services (`BatteryService`, `MetricsService`) composed by the engine. A new `app/runtime` package builds an engine without Qt so a headless CLI can reuse it. UI stays read-only over engine signals.

**Tech Stack:** Python 3.12, `uv`, PySide6 (incl. PySide6.QtCharts, no new runtime dep), pytest + ruff (dev only). UI/docs Spanish.

Spec: `docs/superpowers/specs/2026-05-17-simulator-improvements-design.md`

---

## File Structure

- Modify `app/config/settings.py` — all new constants (P0, P2, P3, P4, P6).
- Modify `app/services/alert_service.py` — remove dead branch (P0).
- Modify `app/services/mode_service.py`, `app/simulation/simulation_engine.py` — use new constants (P0); RTB integration (P2); metrics + time_scale hooks (P3/P4).
- Modify `app/domain/autonomous_unit.py` — RTB flags (P2).
- Create `app/services/battery_service.py` — RTB/recharge logic (P2).
- Create `app/services/metrics_service.py` — run metrics (P3).
- Create `app/io/__init__.py`, `app/io/exporter.py` — CSV/JSON export (P3).
- Create `app/runtime/__init__.py`, `app/runtime/engine_builder.py`, `app/runtime/headless.py` — Qt-free engine build + headless loop (P3).
- Modify `main.py` — arg parsing, headless branch (P3).
- Modify `app/ui/radar_view.py` — incremental redraw (P5).
- Modify `app/ui/panels.py`, `app/ui/control_window.py` — unit list, charts, time-scale, full log, save/load, shortcuts (P4/P6).
- Create `pyproject.toml`, `test.sh`; modify `setup.sh` (P1).
- Create `tests/` modules (P1+).

---

## Phase 0 — Correctness fixes

### Task 0.1: Add named constants, remove redundant alias

**Files:**
- Modify: `app/config/settings.py`

- [ ] **Step 1: Edit `settings.py`** — replace the line `LOW_BATTERY_THRESHOLD = 20.0` / `DEFAULT_LOW_BATTERY_THRESHOLD = LOW_BATTERY_THRESHOLD` block so only the default remains, and append new constants.

Replace:
```python
LOW_BATTERY_THRESHOLD = 20.0
DEFAULT_LOW_BATTERY_THRESHOLD = LOW_BATTERY_THRESHOLD
```
with:
```python
DEFAULT_LOW_BATTERY_THRESHOLD = 20.0
```

Append after `DEFAULT_ACTIVE_UNITS = 6`:
```python
# Movement / behavior tunables (extracted from inline literals)
BATTERY_DRAIN_DT_SCALE = 10.0
SEPARATION_CORRECTION_GAIN = 0.12
PATROL_ORBIT_FACTOR = 0.68
RECON_X_FACTOR = 0.68
RECON_TOP_FACTOR = 0.52
RECON_BOTTOM_FACTOR = 0.48
RECON_STEP_FACTOR = 0.23
SPAWN_MIN_RADIUS = 25.0
SPAWN_MAX_RADIUS_FACTOR = 0.45

# Return-to-base / recharge (Fase 2)
BASE_POSITION = (0.0, 0.0)
RECHARGE_RATE = 6.0  # % por segundo de simulación
RECHARGE_FULL = 100.0
RTB_TRIGGER_MARGIN = 0.0  # se dispara al cruzar low_battery_threshold

# Control de tiempo (Fase 4)
DEFAULT_TIME_SCALE = 1
AVAILABLE_TIME_SCALES = (1, 2, 4, 8)
```

Append after `STATUS_BATERIA_BAJA = "batería baja"`:
```python
STATUS_REGRESANDO = "regresando a base"
STATUS_RECARGANDO = "recargando"
```

Append after `ALERT_PROXIMITY = "proximidad entre unidades"`:
```python
ALERT_RTB_START = "retorno a base iniciado"
ALERT_RECHARGE_DONE = "recarga completada"
```

Append after `COLOR_OBSERVATION = "#9ac1ff"`:
```python
COLOR_STATUS_RTB = "#ffb454"
COLOR_STATUS_CHARGING = "#43d9bd"
```

- [ ] **Step 2: Verify import still works**

Run: `uv run python -c "from app.config import settings; print(settings.DEFAULT_LOW_BATTERY_THRESHOLD, settings.RECHARGE_RATE)"`
Expected: `20.0 6.0`

- [ ] **Step 3: Replace remaining `LOW_BATTERY_THRESHOLD` references**

Run: `grep -rn "settings.LOW_BATTERY_THRESHOLD\|LOW_BATTERY_THRESHOLD" app/ main.py`
Expected: no matches (only `DEFAULT_LOW_BATTERY_THRESHOLD` remains). If any match, change it to `settings.DEFAULT_LOW_BATTERY_THRESHOLD`.

- [ ] **Step 4: Commit**

```bash
git add app/config/settings.py
git commit -m "refactor: name magic numbers, drop redundant battery alias"
```

### Task 0.2: Use the new constants at call sites

**Files:**
- Modify: `app/simulation/simulation_engine.py` (`_drain_battery`, `_apply_separation_correction`, `_generate_spawn_position`)
- Modify: `app/services/mode_service.py` (`_assign_defensive_patrol`, `_build_recon_route`)

- [ ] **Step 1: `simulation_engine.py` `_drain_battery`** — replace `* (dt * 10.0)` with `* (dt * settings.BATTERY_DRAIN_DT_SCALE)`.

- [ ] **Step 2: `simulation_engine.py` `_apply_separation_correction`** — replace the four `* 0.12` with `* settings.SEPARATION_CORRECTION_GAIN`.

- [ ] **Step 3: `simulation_engine.py` `_generate_spawn_position`** — replace `random.uniform(25.0, self.zone_radius * 0.45)` with `random.uniform(settings.SPAWN_MIN_RADIUS, self.zone_radius * settings.SPAWN_MAX_RADIUS_FACTOR)`.

- [ ] **Step 4: `mode_service.py` `_assign_defensive_patrol`** — replace `zone_radius * 0.68` with `zone_radius * settings.PATROL_ORBIT_FACTOR`.

- [ ] **Step 5: `mode_service.py` `_build_recon_route`** — replace `-(zone_radius * 0.68)`/`zone_radius * 0.68` with `settings.RECON_X_FACTOR`, `-(zone_radius * 0.52)` with `settings.RECON_TOP_FACTOR`, `zone_radius * 0.48` with `settings.RECON_BOTTOM_FACTOR`, `zone_radius * 0.23` with `settings.RECON_STEP_FACTOR`.

- [ ] **Step 6: Smoke run**

Run: `uv run python -c "from app.simulation.simulation_engine import SimulationEngine; e=SimulationEngine(); e.create_unit(); e.update_simulation(); print('ok')"`
Expected: `ok`

- [ ] **Step 7: Commit**

```bash
git add app/simulation/simulation_engine.py app/services/mode_service.py
git commit -m "refactor: replace inline literals with named settings constants"
```

### Task 0.3: Remove dead alert-severity branch

**Files:**
- Modify: `app/services/alert_service.py:70-80`

- [ ] **Step 1: Edit `_resolve_severity`** — delete the unreachable second `ALERT_OUT_OF_ZONE` check.

Replace:
```python
        if alert_type in {settings.ALERT_BATTERY_CRITICAL, settings.ALERT_NO_BATTERY, settings.ALERT_OUT_OF_ZONE}:
            return settings.SEVERITY_CRIT
        if alert_type == settings.ALERT_OUT_OF_ZONE:
            return settings.SEVERITY_CRIT
        if alert_type == settings.ALERT_BATTERY_LOW:
```
with:
```python
        if alert_type in {settings.ALERT_BATTERY_CRITICAL, settings.ALERT_NO_BATTERY, settings.ALERT_OUT_OF_ZONE}:
            return settings.SEVERITY_CRIT
        if alert_type == settings.ALERT_BATTERY_LOW:
```

- [ ] **Step 2: Commit**

```bash
git add app/services/alert_service.py
git commit -m "refactor: remove unreachable alert-severity branch"
```

### Task 0.4: Remove unused `apply_scenario`

**Files:**
- Modify: `app/simulation/simulation_engine.py:120-135`

- [ ] **Step 1: Confirm unused**

Run: `grep -rn "\.apply_scenario(" app/ main.py`
Expected: no matches.

- [ ] **Step 2: Delete the `apply_scenario` method** (the `def apply_scenario(self, scenario_name: str) -> None:` block, lines ~120-135, ending before `def ensure_unit_count`).

- [ ] **Step 3: Smoke run**

Run: `uv run python -c "from app.simulation.simulation_engine import SimulationEngine; SimulationEngine(); print('ok')"`
Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add app/simulation/simulation_engine.py
git commit -m "refactor: drop unused SimulationEngine.apply_scenario"
```

### Task 0.5: Restore unit state on resume after pause

**Files:**
- Modify: `app/simulation/simulation_engine.py` (`pause`, `start`)

- [ ] **Step 1: In `pause()`** — before overwriting `unit.state` to `STATUS_DETENIDO`, store the prior state. Replace the loop body:

```python
        for unit in self.units.values():
            if unit.state in {
                settings.STATUS_ACTIVO,
                settings.STATUS_EN_RUTA,
                settings.STATUS_PATRULLANDO,
                settings.STATUS_RECONOCIMIENTO,
            }:
                unit.state = settings.STATUS_DETENIDO
```
with:
```python
        for unit in self.units.values():
            if unit.state in {
                settings.STATUS_ACTIVO,
                settings.STATUS_EN_RUTA,
                settings.STATUS_PATRULLANDO,
                settings.STATUS_RECONOCIMIENTO,
            }:
                unit.state_before_pause = unit.state
                unit.state = settings.STATUS_DETENIDO
```

- [ ] **Step 2: In `start()`** — after setting status running and before `self.updated.emit()`, restore:

```python
        for unit in self.units.values():
            if unit.state_before_pause is not None:
                unit.state = unit.state_before_pause
                unit.state_before_pause = None
```

- [ ] **Step 3: Add field to `AutonomousUnit`** — in `app/domain/autonomous_unit.py`, after `direction_y: float = 0.0` add:

```python
    state_before_pause: str | None = None
```
And in `reset()` add `self.state_before_pause = None`.

- [ ] **Step 4: Smoke run**

Run: `uv run python -c "from app.simulation.simulation_engine import SimulationEngine as E; e=E(); e.create_unit(); e.start(); e.update_simulation(); e.pause(); e.start(); print([u.state for u in e.units.values()])"`
Expected: a non-`detenido` state printed.

- [ ] **Step 5: Commit**

```bash
git add app/simulation/simulation_engine.py app/domain/autonomous_unit.py
git commit -m "fix: restore unit state on resume after pause"
```

---

## Phase 1 — Tooling + tests

### Task 1.1: pyproject + test runner

**Files:**
- Create: `pyproject.toml`, `test.sh`
- Modify: `setup.sh`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "simulador-radar-unefa"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["PySide6"]

[dependency-groups]
dev = ["pytest>=8", "ruff>=0.6"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"

[tool.ruff]
line-length = 120
target-version = "py312"
```

- [ ] **Step 2: Create `test.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail
uv run --group dev pytest "$@"
```
Then: `chmod +x test.sh`

- [ ] **Step 3: Append dev-deps note to `setup.sh`** — add at the end:

```bash
echo "Para ejecutar las pruebas: ./test.sh"
```

- [ ] **Step 4: Create `tests/__init__.py`** (empty file) and `tests/conftest.py`:

```python
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
```

- [ ] **Step 5: Verify pytest runs (no tests yet)**

Run: `./test.sh`
Expected: exit 0, "no tests ran".

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml test.sh setup.sh tests/
git commit -m "chore: add pyproject, ruff/pytest config, test runner"
```

### Task 1.2: Tests for `control.move_toward_waypoint`

**Files:**
- Create: `tests/test_control.py`

- [ ] **Step 1: Write failing tests**

```python
from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit
from app.domain.waypoint import Waypoint
from app.simulation.control import move_toward_waypoint


def _unit() -> AutonomousUnit:
    return AutonomousUnit(identifier="U01", x=0.0, y=0.0, speed=50.0, nominal_speed=50.0)


def test_reaches_waypoint_within_tolerance():
    unit = _unit()
    wp = Waypoint(identifier="W", x=settings.TARGET_TOLERANCE / 2, y=0.0)
    reached = move_toward_waypoint(unit, wp, dt=0.1, max_speed=80.0,
                                   tolerance=settings.TARGET_TOLERANCE, kp=0.85)
    assert reached is True
    assert unit.distance_to_target == 0.0
    assert (unit.x, unit.y) == (wp.x, wp.y)


def test_moves_toward_far_waypoint_without_reaching():
    unit = _unit()
    wp = Waypoint(identifier="W", x=500.0, y=0.0)
    reached = move_toward_waypoint(unit, wp, dt=0.1, max_speed=80.0,
                                   tolerance=settings.TARGET_TOLERANCE, kp=0.85)
    assert reached is False
    assert unit.x > 0.0
    assert unit.direction_x == 1.0
```

- [ ] **Step 2: Run, expect PASS** (function already exists)

Run: `./test.sh tests/test_control.py`
Expected: 2 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/test_control.py
git commit -m "test: cover move_toward_waypoint"
```

### Task 1.3: Tests for mode/alert/swarm services

**Files:**
- Create: `tests/test_mode_service.py`, `tests/test_alert_service.py`, `tests/test_swarm_service.py`

- [ ] **Step 1: `tests/test_mode_service.py`**

```python
from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit
from app.services.mode_service import ModeService


def _units(n):
    return [AutonomousUnit(identifier=f"U{i:02d}", x=0.0, y=0.0) for i in range(n)]


def test_defensive_assigns_patrol_loop_route():
    units = _units(4)
    ModeService().apply_mode(settings.MODE_DEFENSIVE, units, zone_radius=320.0)
    for u in units:
        assert u.role == settings.ROLE_PATROL
        assert u.route_loop is True
        assert len(u.route) >= 8


def test_recon_assigns_non_loop_route():
    units = _units(3)
    ModeService().apply_mode(settings.MODE_RECON, units, zone_radius=320.0)
    for u in units:
        assert u.role == settings.ROLE_RECON
        assert u.route_loop is False
        assert len(u.route) == 4


def test_advance_route_loop_wraps():
    svc = ModeService()
    units = _units(2)
    svc.apply_mode(settings.MODE_DEFENSIVE, units, zone_radius=320.0)
    u = units[0]
    u.current_waypoint_index = len(u.route) - 1
    svc.advance_unit_route(u)
    assert u.current_waypoint_index == 0
```

- [ ] **Step 2: `tests/test_alert_service.py`**

```python
from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit
from app.services.alert_service import AlertService


def test_low_battery_emits_warn_once():
    svc = AlertService()
    unit = AutonomousUnit(identifier="U01", x=0.0, y=0.0, battery=10.0)
    _, new = svc.evaluate_unit(unit, zone_radius=320.0, low_battery_threshold=20.0)
    assert any(a.alert_type == settings.ALERT_BATTERY_LOW for a in new)
    _, again = svc.evaluate_unit(unit, zone_radius=320.0, low_battery_threshold=20.0)
    assert again == []


def test_out_of_zone_is_critical():
    svc = AlertService()
    unit = AutonomousUnit(identifier="U01", x=999.0, y=0.0, battery=100.0)
    _, new = svc.evaluate_unit(unit, zone_radius=320.0, low_battery_threshold=20.0)
    assert any(a.severity == settings.SEVERITY_CRIT for a in new)
```

- [ ] **Step 3: `tests/test_swarm_service.py`**

```python
from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit
from app.services.swarm_service import SwarmService


def _units(n):
    return [AutonomousUnit(identifier=f"U{i:02d}", x=0.0, y=0.0) for i in range(n)]


def test_combined_splits_two_swarms():
    units = _units(6)
    SwarmService().assign_swarms(units, settings.SCENARIO_COMBINED, swarm_count=2,
                                 distribution="Mitad y mitad")
    ids = {u.swarm_id for u in units}
    assert ids == {"E1", "E2"}


def test_zone_protection_single_swarm_patrol():
    units = _units(5)
    SwarmService().assign_swarms(units, settings.SCENARIO_ZONE_PROTECTION, swarm_count=1,
                                 distribution="Automática")
    assert all(u.swarm_id == "E1" and u.swarm_role == settings.ROLE_PATROL for u in units)
```

- [ ] **Step 4: Run all**

Run: `./test.sh`
Expected: all passed.

- [ ] **Step 5: Commit**

```bash
git add tests/
git commit -m "test: cover mode, alert, swarm services"
```

---

## Phase 2 — Return-to-base + recharge

### Task 2.1: RTB flags on the domain model

**Files:**
- Modify: `app/domain/autonomous_unit.py`

- [ ] **Step 1: Add fields** after `state_before_pause: str | None = None`:

```python
    is_returning: bool = False
    is_charging: bool = False
```

- [ ] **Step 2: In `reset()`** add:

```python
        self.is_returning = False
        self.is_charging = False
```

- [ ] **Step 3: Commit**

```bash
git add app/domain/autonomous_unit.py
git commit -m "feat: add RTB/charging flags to AutonomousUnit"
```

### Task 2.2: BatteryService (TDD)

**Files:**
- Create: `app/services/battery_service.py`
- Create: `tests/test_battery_service.py`

- [ ] **Step 1: Write failing tests** `tests/test_battery_service.py`

```python
from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit
from app.services.battery_service import BatteryService


def _unit(battery):
    u = AutonomousUnit(identifier="U01", x=100.0, y=0.0, battery=battery)
    u.task_label = settings.TASK_AUTOMATIC
    return u


def test_triggers_rtb_when_below_threshold():
    svc = BatteryService()
    u = _unit(15.0)
    action = svc.evaluate(u, low_battery_threshold=20.0, dt=0.1)
    assert u.is_returning is True
    assert u.waypoint is not None
    assert (u.waypoint.x, u.waypoint.y) == settings.BASE_POSITION
    assert u.state == settings.STATUS_REGRESANDO
    assert action == "rtb_start"


def test_does_not_rtb_manual_units():
    svc = BatteryService()
    u = _unit(10.0)
    u.task_label = settings.TASK_MANUAL
    action = svc.evaluate(u, low_battery_threshold=20.0, dt=0.1)
    assert u.is_returning is False
    assert action is None


def test_charges_at_base_then_restores():
    svc = BatteryService()
    u = _unit(15.0)
    svc.evaluate(u, 20.0, 0.1)              # start RTB
    u.x, u.y = settings.BASE_POSITION       # simulate arrival
    svc.notify_base_reached(u)
    assert u.is_charging is True
    assert u.state == settings.STATUS_RECARGANDO
    for _ in range(1000):
        done = svc.evaluate(u, 20.0, 1.0)
        if done == "recharge_done":
            break
    assert u.battery == settings.RECHARGE_FULL
    assert u.is_charging is False
    assert u.is_returning is False
```

- [ ] **Step 2: Run, expect FAIL** (`No module named 'app.services.battery_service'`)

Run: `./test.sh tests/test_battery_service.py`
Expected: collection error / FAIL.

- [ ] **Step 3: Implement `app/services/battery_service.py`**

```python
from __future__ import annotations

from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit
from app.domain.waypoint import Waypoint


class BatteryService:
    """Stateless RTB + recharge decisions. Engine owns mutation/signals."""

    def evaluate(self, unit: AutonomousUnit, low_battery_threshold: float, dt: float) -> str | None:
        if unit.task_label == settings.TASK_MANUAL:
            return None

        if unit.is_charging:
            unit.battery = min(settings.RECHARGE_FULL, unit.battery + settings.RECHARGE_RATE * dt)
            unit.speed = 0.0
            unit.state = settings.STATUS_RECARGANDO
            if unit.battery >= settings.RECHARGE_FULL:
                unit.is_charging = False
                unit.is_returning = False
                return "recharge_done"
            return None

        if unit.is_returning:
            return None

        if unit.battery > 0.0 and unit.battery < low_battery_threshold:
            self._begin_return(unit)
            return "rtb_start"
        return None

    def notify_base_reached(self, unit: AutonomousUnit) -> None:
        if not unit.is_returning:
            return
        unit.is_charging = True
        unit.waypoint = None
        unit.distance_to_target = None
        unit.state = settings.STATUS_RECARGANDO

    @staticmethod
    def _begin_return(unit: AutonomousUnit) -> None:
        base_x, base_y = settings.BASE_POSITION
        unit.is_returning = True
        unit.waypoint = Waypoint(
            identifier="BASE",
            x=base_x,
            y=base_y,
            altitude=unit.altitude,
            kind="base",
        )
        unit.state = settings.STATUS_REGRESANDO
```

- [ ] **Step 4: Run, expect PASS**

Run: `./test.sh tests/test_battery_service.py`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add app/services/battery_service.py tests/test_battery_service.py
git commit -m "feat: BatteryService RTB + recharge logic"
```

### Task 2.3: Wire BatteryService + mission snapshot into the engine

**Files:**
- Modify: `app/simulation/simulation_engine.py`

- [ ] **Step 1: Import + instantiate** — add `from app.services.battery_service import BatteryService` with the other service imports, and in `__init__` after `self._scenario_service = ...` add `self._battery_service = BatteryService()`.

- [ ] **Step 2: In `update_simulation`**, inside the per-unit loop, immediately after `self._apply_battery_speed_policy(unit)` and before the `if unit.battery <= 0.0:` block, insert RTB handling:

```python
            rtb_action = self._battery_service.evaluate(unit, self.low_battery_threshold, dt)
            if rtb_action == "rtb_start":
                if unit.task_label != settings.TASK_TEMPORARY:
                    unit.mission_snapshot = self._build_mission_snapshot(unit)
                self._register_alerts([
                    Alert(
                        alert_type=settings.ALERT_RTB_START,
                        unit_id=unit.identifier,
                        swarm_id=unit.swarm_id,
                        message=f"La unidad {unit.identifier} inició retorno a base por batería baja.",
                        severity=settings.SEVERITY_INFO,
                        prefix="INFO",
                        key=f"{unit.identifier}:{settings.ALERT_RTB_START}",
                    )
                ])
            elif rtb_action == "recharge_done":
                self._restore_mission(unit)
                self._register_alerts([
                    Alert(
                        alert_type=settings.ALERT_RECHARGE_DONE,
                        unit_id=unit.identifier,
                        swarm_id=unit.swarm_id,
                        message=f"La unidad {unit.identifier} completó recarga y reanudó su misión.",
                        severity=settings.SEVERITY_INFO,
                        prefix="INFO",
                        key=f"{unit.identifier}:{settings.ALERT_RECHARGE_DONE}",
                    )
                ])

            if unit.is_charging:
                unit.direction_x = 0.0
                unit.direction_y = 0.0
                unit.append_trajectory()
                continue
```

- [ ] **Step 2b:** In the same loop, replace the temporary-task restore branch so base arrival hands off to BatteryService. Find:

```python
            if unit.waypoint is not None and reached_target and unit.task_label == settings.TASK_TEMPORARY:
                self._restore_mission(unit)
```
Replace with:
```python
            if unit.waypoint is not None and reached_target and unit.is_returning:
                self._battery_service.notify_base_reached(unit)
            elif unit.waypoint is not None and reached_target and unit.task_label == settings.TASK_TEMPORARY:
                self._restore_mission(unit)
```

- [ ] **Step 3: `_apply_state_overrides`** — do not let battery-low/critical override the RTB/charging states. At the top of `_apply_state_overrides`, add:

```python
        if unit.is_charging:
            unit.state = settings.STATUS_RECARGANDO
            return
        if unit.is_returning:
            unit.state = settings.STATUS_REGRESANDO
            return
```

- [ ] **Step 4: `_restore_mission`** — at the end, ensure flags clear. After `unit.mission_snapshot = None` (the success path) and in the no-snapshot early return, add `unit.is_returning = False` / `unit.is_charging = False` to both branches.

- [ ] **Step 5: Integration smoke**

Run:
```bash
uv run python -c "
from app.simulation.simulation_engine import SimulationEngine as E
e=E(); u=e.create_unit(); u.battery=12.0; e.start()
for _ in range(50): e.update_simulation()
print(u.is_returning, u.state)"
```
Expected: `True regresando a base` (or already `recargando`).

- [ ] **Step 6: Commit**

```bash
git add app/simulation/simulation_engine.py
git commit -m "feat: integrate RTB + recharge into simulation loop"
```

### Task 2.4: Radar color for RTB/charging states

**Files:**
- Modify: `app/ui/radar_view.py` (`_resolve_unit_color`)

- [ ] **Step 1: In `_resolve_unit_color`**, add before the `STATUS_DETENIDO` check:

```python
        if unit.state == settings.STATUS_REGRESANDO:
            return settings.COLOR_STATUS_RTB
        if unit.state == settings.STATUS_RECARGANDO:
            return settings.COLOR_STATUS_CHARGING
```

- [ ] **Step 2: Commit**

```bash
git add app/ui/radar_view.py
git commit -m "feat: radar colors for RTB and charging states"
```

---

## Phase 3 — Metrics + export + headless

### Task 3.1: MetricsService (TDD)

**Files:**
- Create: `app/services/metrics_service.py`
- Create: `tests/test_metrics_service.py`

- [ ] **Step 1: Write failing tests** `tests/test_metrics_service.py`

```python
from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit
from app.services.metrics_service import MetricsService


def test_accumulates_distance_and_samples():
    m = MetricsService()
    u = AutonomousUnit(identifier="U01", x=0.0, y=0.0, battery=100.0)
    m.record_tick(sim_time=0.0, units=[u])
    u.x, u.y = 3.0, 4.0
    m.record_tick(sim_time=0.1, units=[u])
    summary = m.build_summary({"scenario": "X"})
    assert summary["units"]["U01"]["distance"] == 5.0
    assert summary["scenario"]["scenario"] == "X"
    assert len(m.timeseries_rows()) == 2


def test_counts_objective_reached():
    m = MetricsService()
    u = AutonomousUnit(identifier="U01", x=0.0, y=0.0, battery=100.0)
    u.state = settings.STATUS_OBJETIVO_ALCANZADO
    m.record_tick(0.0, [u])
    s = m.build_summary({})
    assert s["units"]["U01"]["objectives_reached"] >= 1
```

- [ ] **Step 2: Run, expect FAIL.** Run: `./test.sh tests/test_metrics_service.py`

- [ ] **Step 3: Implement `app/services/metrics_service.py`**

```python
from __future__ import annotations

from collections import deque
from math import hypot

from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit

CHART_WINDOW = 240


class MetricsService:
    def __init__(self) -> None:
        self._last_pos: dict[str, tuple[float, float]] = {}
        self._distance: dict[str, float] = {}
        self._objectives: dict[str, int] = {}
        self._prev_state: dict[str, str] = {}
        self._first_objective_time: dict[str, float] = {}
        self._rows: list[dict[str, object]] = []
        self.battery_window: deque[tuple[float, float]] = deque(maxlen=CHART_WINDOW)
        self.alert_window: deque[tuple[float, int]] = deque(maxlen=CHART_WINDOW)

    def reset(self) -> None:
        self.__init__()

    def record_tick(self, sim_time: float, units: list[AutonomousUnit],
                    active_alert_count: int = 0) -> None:
        batteries: list[float] = []
        for u in units:
            prev = self._last_pos.get(u.identifier)
            if prev is not None:
                self._distance[u.identifier] = self._distance.get(u.identifier, 0.0) + hypot(
                    u.x - prev[0], u.y - prev[1])
            else:
                self._distance.setdefault(u.identifier, 0.0)
            self._last_pos[u.identifier] = (u.x, u.y)

            if (u.state == settings.STATUS_OBJETIVO_ALCANZADO
                    and self._prev_state.get(u.identifier) != settings.STATUS_OBJETIVO_ALCANZADO):
                self._objectives[u.identifier] = self._objectives.get(u.identifier, 0) + 1
                self._first_objective_time.setdefault(u.identifier, sim_time)
            self._objectives.setdefault(u.identifier, 0)
            self._prev_state[u.identifier] = u.state

            batteries.append(u.battery)
            self._rows.append({
                "sim_time": round(sim_time, 2),
                "unit_id": u.identifier,
                "x": round(u.x, 3),
                "y": round(u.y, 3),
                "battery": round(u.battery, 2),
                "state": u.state,
            })

        avg_batt = sum(batteries) / len(batteries) if batteries else 0.0
        self.battery_window.append((round(sim_time, 2), round(avg_batt, 2)))
        self.alert_window.append((round(sim_time, 2), active_alert_count))

    def timeseries_rows(self) -> list[dict[str, object]]:
        return self._rows

    def build_summary(self, scenario_info: dict[str, object]) -> dict[str, object]:
        return {
            "scenario": scenario_info,
            "units": {
                uid: {
                    "distance": round(self._distance.get(uid, 0.0), 3),
                    "objectives_reached": self._objectives.get(uid, 0),
                    "time_to_first_objective": self._first_objective_time.get(uid),
                }
                for uid in self._distance
            },
        }
```

- [ ] **Step 4: Run, expect PASS.** Run: `./test.sh tests/test_metrics_service.py` → 2 passed.

- [ ] **Step 5: Commit**

```bash
git add app/services/metrics_service.py tests/test_metrics_service.py
git commit -m "feat: MetricsService for run accumulation"
```

### Task 3.2: Engine records metrics each tick

**Files:**
- Modify: `app/simulation/simulation_engine.py`

- [ ] **Step 1: Import + instantiate** — add `from app.services.metrics_service import MetricsService`; in `__init__` add `self.metrics = MetricsService()`; in `reset()` add `self.metrics.reset()`.

- [ ] **Step 2: End of `update_simulation`** — just before the final `self.updated.emit()`:

```python
        self.metrics.record_tick(self.simulation_time, list(self.units.values()),
                                 self.active_alert_count)
```

- [ ] **Step 3: Smoke**

Run: `uv run python -c "from app.simulation.simulation_engine import SimulationEngine as E; e=E(); e.create_unit(); [e.update_simulation() for _ in range(5)]; print(len(e.metrics.timeseries_rows()))"`
Expected: `5`

- [ ] **Step 4: Commit**

```bash
git add app/simulation/simulation_engine.py
git commit -m "feat: engine records metrics each tick"
```

### Task 3.3: Exporter (TDD)

**Files:**
- Create: `app/io/__init__.py` (empty), `app/io/exporter.py`
- Create: `tests/test_exporter.py`

- [ ] **Step 1: Failing test** `tests/test_exporter.py`

```python
import csv
import json
from pathlib import Path

from app.io.exporter import export_run


def test_export_writes_csv_and_json(tmp_path: Path):
    rows = [{"sim_time": 0.0, "unit_id": "U01", "x": 1.0, "y": 2.0,
             "battery": 99.0, "state": "activo"}]
    summary = {"scenario": {"scenario": "X"}, "units": {"U01": {"distance": 0.0}}}
    paths = export_run(tmp_path, rows, summary)
    csv_rows = list(csv.DictReader(open(paths["timeseries"])))
    assert csv_rows[0]["unit_id"] == "U01"
    assert json.load(open(paths["summary"]))["scenario"]["scenario"] == "X"


def test_export_empty_rows_ok(tmp_path: Path):
    paths = export_run(tmp_path, [], {"scenario": {}, "units": {}})
    assert Path(paths["timeseries"]).exists()
```

- [ ] **Step 2: Run, expect FAIL.** `./test.sh tests/test_exporter.py`

- [ ] **Step 3: Implement `app/io/exporter.py`**

```python
from __future__ import annotations

import csv
import json
from pathlib import Path

_CSV_FIELDS = ["sim_time", "unit_id", "x", "y", "battery", "state"]


def export_run(out_dir: str | Path, timeseries_rows: list[dict[str, object]],
                summary: dict[str, object]) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ts_path = out / "timeseries.csv"
    sum_path = out / "summary.json"

    with ts_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        for row in timeseries_rows:
            writer.writerow({k: row.get(k, "") for k in _CSV_FIELDS})

    sum_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"timeseries": str(ts_path), "summary": str(sum_path)}
```

- [ ] **Step 4: Run, expect PASS.** `./test.sh tests/test_exporter.py` → 2 passed.

- [ ] **Step 5: Commit**

```bash
git add app/io/ tests/test_exporter.py
git commit -m "feat: CSV/JSON run exporter"
```

### Task 3.4: Qt-free engine builder + headless loop

**Files:**
- Create: `app/runtime/__init__.py` (empty), `app/runtime/engine_builder.py`, `app/runtime/headless.py`
- Create: `tests/test_headless.py`

- [ ] **Step 1: `app/runtime/engine_builder.py`**

```python
from __future__ import annotations

import random

from app.config import settings
from app.services.scenario_service import ScenarioApplicationConfig
from app.simulation.simulation_engine import SimulationEngine


def build_engine(scenario_name: str, seed: int | None = None) -> SimulationEngine:
    if seed is not None:
        random.seed(seed)
    engine = SimulationEngine()
    scenario = settings.SCENARIO_CONFIG.get(scenario_name, {})
    config = ScenarioApplicationConfig(
        scenario_name=scenario_name,
        unit_count=int(scenario.get("units", settings.DEFAULT_ACTIVE_UNITS)),
        swarm_count=2 if scenario_name == settings.SCENARIO_COMBINED else 1,
        distribution="Mitad y mitad" if scenario_name == settings.SCENARIO_COMBINED else "Automática",
        use_existing_units=False,
        max_speed=settings.MAX_SPEED,
        target_altitude=settings.DEFAULT_ALTITUDE,
        zone_radius=float(scenario.get("zone_radius", settings.DEFAULT_ZONE_RADIUS)),
        min_separation=settings.DEFAULT_MIN_SEPARATION,
        low_battery_threshold=settings.DEFAULT_LOW_BATTERY_THRESHOLD,
        auto_start=False,
    )
    engine.apply_scenario_configuration(config)
    return engine
```

- [ ] **Step 2: `app/runtime/headless.py`**

```python
from __future__ import annotations

from app.config import settings
from app.io.exporter import export_run
from app.runtime.engine_builder import build_engine


def run_headless(scenario_name: str, duration_s: float, out_dir: str,
                 seed: int | None = None, time_scale: int = 1) -> dict[str, str]:
    engine = build_engine(scenario_name, seed=seed)
    dt = settings.SIMULATION_INTERVAL_MS / 1000.0
    steps = int((duration_s / dt) / max(1, time_scale))
    engine.is_running = True
    for _ in range(steps):
        engine.simulation_time += dt * time_scale
        engine._tick_units(dt * time_scale)  # see Task 4.1 for extracted tick
    summary = engine.metrics.build_summary(engine.get_global_status())
    return export_run(out_dir, engine.metrics.timeseries_rows(), summary)
```

> NOTE: `_tick_units` is introduced in Task 4.1 (extracted from `update_simulation`). Implement Task 4.1 before running headless. Until then this module imports fine but `run_headless` is not called.

- [ ] **Step 3: `tests/test_headless.py`**

```python
from pathlib import Path

from app.runtime.headless import run_headless


def test_headless_run_is_deterministic(tmp_path: Path):
    a = run_headless("Protección de zona estratégica", duration_s=5.0,
                     out_dir=str(tmp_path / "a"), seed=42)
    b = run_headless("Protección de zona estratégica", duration_s=5.0,
                     out_dir=str(tmp_path / "b"), seed=42)
    assert Path(a["summary"]).read_text() == Path(b["summary"]).read_text()
```

- [ ] **Step 4: Commit (tests run after Task 4.1)**

```bash
git add app/runtime/ tests/test_headless.py
git commit -m "feat: Qt-free engine builder + headless loop (tick extracted in P4)"
```

### Task 3.5: CLI args + headless branch in main.py

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Rewrite `main.py`** to parse args and branch:

```python
from __future__ import annotations

import argparse
import sys
import traceback


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Simulador Radar UNEFA")
    p.add_argument("--headless", action="store_true")
    p.add_argument("--scenario", default="Protección de zona estratégica")
    p.add_argument("--duration", type=float, default=120.0)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--time-scale", type=int, default=1)
    p.add_argument("--out", default="run_output")
    return p.parse_args(argv)


def _run_headless(args: argparse.Namespace) -> int:
    from app.runtime.headless import run_headless
    paths = run_headless(args.scenario, args.duration, args.out,
                         seed=args.seed, time_scale=args.time_scale)
    print(f"Informe exportado: {paths['timeseries']}, {paths['summary']}")
    return 0


def _run_gui() -> int:
    from PySide6.QtWidgets import QApplication
    from app.config import settings
    from app.simulation.simulation_engine import SimulationEngine
    from app.ui.control_window import ControlWindow
    from app.ui.main_window import RadarOperationalWindow

    app = QApplication(sys.argv)
    engine = SimulationEngine()
    radar_window = RadarOperationalWindow(engine)
    control_window = ControlWindow(engine)

    control_window.assign_requested.connect(radar_window.begin_waypoint_assignment)
    radar_window.waypoint_requested.connect(control_window.assign_waypoint_from_radar)
    control_window.statusBar().messageChanged.connect(radar_window.show_feedback)

    screen_geometry = app.primaryScreen().availableGeometry()
    radar_window.setGeometry(
        screen_geometry.x() + 20, screen_geometry.y() + 20,
        min(settings.RADAR_WINDOW_WIDTH, screen_geometry.width() - settings.CONTROL_WINDOW_WIDTH - 60),
        min(settings.RADAR_WINDOW_HEIGHT, screen_geometry.height() - 40))
    control_window.setGeometry(
        radar_window.geometry().right() + 20, screen_geometry.y() + 20,
        min(settings.CONTROL_WINDOW_WIDTH, max(420, screen_geometry.width() - radar_window.width() - 60)),
        min(settings.CONTROL_WINDOW_HEIGHT, screen_geometry.height() - 40))

    radar_window.show()
    control_window.show()
    return app.exec()


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    if args.headless:
        return _run_headless(args)
    return _run_gui()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover - startup safeguard
        traceback.print_exc()
        from PySide6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "Error de inicio", f"No fue posible iniciar la aplicación:\n{exc}")
        raise
```

- [ ] **Step 2: Commit**

```bash
git add main.py
git commit -m "feat: CLI args + headless entrypoint"
```

---

## Phase 4 — Time scale

### Task 4.1: Extract `_tick_units` and apply `time_scale`

**Files:**
- Modify: `app/simulation/simulation_engine.py`

- [ ] **Step 1: Add field** — in `__init__` add `self.time_scale: int = settings.DEFAULT_TIME_SCALE`.

- [ ] **Step 2: Refactor `update_simulation`** — split into the timer-facing method and a reusable tick. Replace the current `update_simulation` body so the loop body moves into `_tick_units(self, dt)`:

```python
    def update_simulation(self) -> None:
        base_dt = settings.SIMULATION_INTERVAL_MS / 1000.0
        dt = base_dt * self.time_scale
        self.simulation_time += dt
        self._tick_units(dt)
        self.updated.emit()

    def _tick_units(self, dt: float) -> None:
        # (everything that was previously between
        #  `self.simulation_time += dt` and the final `self.updated.emit()`)
```

Move the existing per-unit loop, `_handle_proximity_monitoring`, and `_register_alerts(proximity_alerts)` into `_tick_units`. Move the `self.metrics.record_tick(...)` call (Task 3.2) into `_tick_units` just before it returns. Do NOT emit `updated` inside `_tick_units` (headless has no Qt loop; emitting is harmless but keep it in `update_simulation` only).

- [ ] **Step 3: Add setter**

```python
    def set_time_scale(self, value: int) -> None:
        if value in settings.AVAILABLE_TIME_SCALES:
            self.time_scale = value
            self.updated.emit()
```

- [ ] **Step 4: Run headless tests (now `_tick_units` exists)**

Run: `./test.sh tests/test_headless.py`
Expected: 1 passed (deterministic).

- [ ] **Step 5: Full suite**

Run: `./test.sh`
Expected: all passed.

- [ ] **Step 6: Commit**

```bash
git add app/simulation/simulation_engine.py
git commit -m "feat: extract _tick_units, add time_scale"
```

### Task 4.2: Time-scale selector in Control UI

**Files:**
- Modify: `app/ui/panels.py` (parameters panel), `app/ui/control_window.py`

- [ ] **Step 1: In `panels.py`** locate the parameters panel class (the one exposing `max_speed_spin`, `active_units_spin`). Add a `QComboBox` `time_scale_combo` with items `["1x","2x","4x","8x"]`, added to the same form layout with label `"Escala de tiempo:"`. Follow the existing widget-construction pattern in that class.

- [ ] **Step 2: In `control_window.py` `_connect_signals`** add:

```python
        params.time_scale_combo.currentTextChanged.connect(
            lambda t: self.engine.set_time_scale(int(t.rstrip("x")))
        )
```

- [ ] **Step 3: In `_sync_parameters_from_engine`** add to the blocked widgets and set value:

```python
        params.time_scale_combo.blockSignals(True)
        params.time_scale_combo.setCurrentText(f"{self.engine.time_scale}x")
        params.time_scale_combo.blockSignals(False)
```

- [ ] **Step 4: Manual smoke** — `./run.sh`, change selector, confirm units move faster. (Document as manual check; no automated UI test.)

- [ ] **Step 5: Commit**

```bash
git add app/ui/panels.py app/ui/control_window.py
git commit -m "feat: time-scale selector in control panel"
```

---

## Phase 5 — Incremental radar redraw

### Task 5.1: Persistent graphics items keyed by unit id

**Files:**
- Modify: `app/ui/radar_view.py`

- [ ] **Step 1:** In `RadarView.__init__` add registries:

```python
        self._unit_items: dict[str, dict[str, object]] = {}
        self._dynamic_items: list[object] = []
        self._last_scenario_visuals: dict[str, object] | None = None
```

- [ ] **Step 2:** Rewrite `refresh()` to avoid `scene.clear()`:

```python
    def refresh(self, units, selected_unit_id, scenario_visuals=None):
        self._selected_unit_id = selected_unit_id
        self._scenario_visuals = scenario_visuals or {}
        self._display_zone_radius = float(self._scenario_visuals.get("zone_radius", settings.RADAR_RADIUS))

        if self._scenario_visuals != self._last_scenario_visuals:
            for item in self._static_items():
                self._scene.removeItem(item)
            self._static_registry = []
            self._draw_scenario_visuals()
            self._last_scenario_visuals = dict(self._scenario_visuals)

        for item in self._dynamic_items:
            self._scene.removeItem(item)
        self._dynamic_items = []

        present = set()
        for unit in units:
            present.add(unit.identifier)
            self._draw_route(unit)
            self._draw_trajectory(unit)
            if unit.waypoint is not None:
                self._draw_waypoint(unit)
            self._sync_unit_item(unit)

        for uid in list(self._unit_items):
            if uid not in present:
                for it in self._unit_items.pop(uid).values():
                    self._scene.removeItem(it)
```

> Implementation notes for the worker:
> - Add `self._static_registry: list = []` in `__init__`; `_static_items()` returns it.
> - In `_draw_scenario_visuals`, `_draw_hud`, `_draw_compact_legend`: append every created item to `self._static_registry` instead of relying on `scene.clear()`.
> - In `_draw_route`, `_draw_trajectory`, `_draw_waypoint`: append every created item to `self._dynamic_items` (these change every tick — cheapest to recreate just these).
> - Add `_sync_unit_item(unit)`: if `unit.identifier` not in `self._unit_items`, create ellipse + label (+ selection ring) once, store them in the dict, and add to scene; otherwise update `setRect`/pen/brush/pos and label text/color in place. Selection ring visibility toggled by `setVisible`.

- [ ] **Step 3: Manual smoke** — `./run.sh`, load a scenario, start. Confirm no flicker, units update smoothly, deleting units (lower active-units spin) removes them from radar.

- [ ] **Step 4: Headless regression** — `./test.sh` (ensure nothing engine-side broke).

- [ ] **Step 5: Commit**

```bash
git add app/ui/radar_view.py
git commit -m "perf: incremental radar redraw, persistent unit items"
```

---

## Phase 6 — UI extras

### Task 6.1: Unit list panel with selection sync

**Files:**
- Modify: `app/ui/panels.py`, `app/ui/control_window.py`

- [ ] **Step 1:** In `panels.py` add a `QListWidget`-based panel class `UnitListPanel` exposing `unit_list` and a method `update_units(units: list, selected_id)` that rebuilds items (text `f"{u.identifier} [{u.swarm_id}] {u.state}"`, `setData(Qt.UserRole, u.identifier)`), preserving/highlighting selection. Add it to `ControlTabsWidget` next to `unit_info` following existing composition.

- [ ] **Step 2:** In `control_window.py`:
  - `_connect_signals`: `self.panels.unit_list_panel.unit_list.itemClicked.connect(lambda it: self.engine.set_selected_unit(it.data(Qt.UserRole)))` (import `Qt` from `PySide6.QtCore`).
  - `_refresh_ui`: call `self.panels.unit_list_panel.update_units(list(self.engine.units.values()), self.engine.selected_unit_id)`.

- [ ] **Step 3: Manual smoke** — click list item selects unit in radar and vice-versa.

- [ ] **Step 4: Commit**

```bash
git add app/ui/panels.py app/ui/control_window.py
git commit -m "feat: unit list panel with selection sync"
```

### Task 6.2: Full scrollable event log

**Files:**
- Modify: `app/ui/panels.py` (alerts panel), `app/ui/control_window.py`

- [ ] **Step 1:** In the alerts panel class add a second `QListWidget` `history_list` (scrollable) under the existing last-alerts widget, labelled `"Historial completo"`. Add method `update_history(alert_items: list)` rendering `f"[{a['timestamp']}] {a['prefix']} {a['unit_id']}: {a['message']}"`.

- [ ] **Step 2:** In `control_window.py` `_refresh_alerts`, after the existing `update_alerts(...)` call, build the full list from `self.engine.recent_alerts` (all, not `[:10]`) and call `self.panels.alerts.update_history(...)`.

- [ ] **Step 3: Manual smoke** — alerts accumulate in history beyond 10.

- [ ] **Step 4: Commit**

```bash
git add app/ui/panels.py app/ui/control_window.py
git commit -m "feat: full scrollable event log"
```

### Task 6.3: Keyboard shortcuts

**Files:**
- Modify: `app/ui/control_window.py`, `app/ui/main_window.py`

- [ ] **Step 1:** In `ControlWindow.__init__` (after signals wired) add `QShortcut`s (import `from PySide6.QtGui import QKeySequence, QShortcut`):

```python
        QShortcut(QKeySequence("Space"), self, activated=self._toggle_run)
        QShortcut(QKeySequence("R"), self, activated=self._reset_simulation)
        QShortcut(QKeySequence("A"), self, activated=self._request_assign_mode)
```
Add `_toggle_run`:
```python
    def _toggle_run(self) -> None:
        if self.engine.is_running:
            self._pause_simulation()
        else:
            self._start_simulation()
```

- [ ] **Step 2:** In `RadarOperationalWindow.__init__` add `QShortcut(QKeySequence("Escape"), self, activated=lambda: self.radar_view.set_waypoint_assignment_enabled(False))`.

- [ ] **Step 3: Manual smoke** — Space toggles run, R resets, Esc cancels assign-cursor.

- [ ] **Step 4: Commit**

```bash
git add app/ui/control_window.py app/ui/main_window.py
git commit -m "feat: keyboard shortcuts"
```

### Task 6.4: Export report button

**Files:**
- Modify: `app/ui/panels.py` (controls panel), `app/ui/control_window.py`

- [ ] **Step 1:** Add `export_button` (`QPushButton("Exportar informe")`) to the controls panel class next to reset.

- [ ] **Step 2:** In `control_window.py`:

```python
        controls.export_button.clicked.connect(self._export_report)
```
```python
    def _export_report(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        from app.io.exporter import export_run
        directory = QFileDialog.getExistingDirectory(self, "Carpeta de destino")
        if not directory:
            return
        summary = self.engine.metrics.build_summary(self.engine.get_global_status())
        paths = export_run(directory, self.engine.metrics.timeseries_rows(), summary)
        self.statusBar().showMessage(f"Informe exportado en {paths['timeseries']}")
```

- [ ] **Step 3: Manual smoke** — run sim, export, verify CSV+JSON written.

- [ ] **Step 4: Commit**

```bash
git add app/ui/panels.py app/ui/control_window.py
git commit -m "feat: export report button"
```

### Task 6.5: Save/Load scenario config (JSON)

**Files:**
- Create: `app/io/scenario_io.py`
- Create: `tests/test_scenario_io.py`
- Modify: `app/ui/panels.py` (scenario panel), `app/ui/control_window.py`

- [ ] **Step 1: Failing test** `tests/test_scenario_io.py`

```python
from pathlib import Path

from app.io.scenario_io import load_scenario_config, save_scenario_config
from app.services.scenario_service import ScenarioApplicationConfig


def _cfg():
    return ScenarioApplicationConfig(
        scenario_name="Protección de zona estratégica", unit_count=6, swarm_count=1,
        distribution="Automática", use_existing_units=False, max_speed=80.0,
        target_altitude=150.0, zone_radius=320.0, min_separation=38.0,
        low_battery_threshold=20.0, auto_start=False)


def test_roundtrip(tmp_path: Path):
    path = tmp_path / "cfg.json"
    save_scenario_config(path, _cfg())
    loaded = load_scenario_config(path)
    assert loaded == _cfg()
```

- [ ] **Step 2: Run, expect FAIL.** `./test.sh tests/test_scenario_io.py`

- [ ] **Step 3: Implement `app/io/scenario_io.py`**

```python
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from app.services.scenario_service import ScenarioApplicationConfig


def save_scenario_config(path: str | Path, config: ScenarioApplicationConfig) -> None:
    Path(path).write_text(json.dumps(asdict(config), indent=2, ensure_ascii=False),
                          encoding="utf-8")


def load_scenario_config(path: str | Path) -> ScenarioApplicationConfig:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return ScenarioApplicationConfig(**data)
```

- [ ] **Step 4: Run, expect PASS.** `./test.sh tests/test_scenario_io.py` → 1 passed.

- [ ] **Step 5:** In scenario panel (`panels.py`) add `save_config_button` / `load_config_button`. In `control_window.py`:

```python
    def _save_config(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        from app.io.scenario_io import save_scenario_config
        path, _ = QFileDialog.getSaveFileName(self, "Guardar configuración", "escenario.json", "JSON (*.json)")
        if not path:
            return
        defaults = self.engine.get_scenario_dialog_defaults(self.engine.current_scenario_name)
        from app.services.scenario_service import ScenarioApplicationConfig
        cfg = ScenarioApplicationConfig(
            scenario_name=self.engine.current_scenario_name,
            unit_count=self.engine.configured_unit_count,
            swarm_count=self.engine.current_swarm_count,
            distribution=self.engine.current_distribution,
            use_existing_units=False,
            max_speed=self.engine.max_speed,
            target_altitude=self.engine.target_altitude,
            zone_radius=self.engine.zone_radius,
            min_separation=self.engine.min_separation,
            low_battery_threshold=self.engine.low_battery_threshold,
            auto_start=False)
        save_scenario_config(path, cfg)
        self.statusBar().showMessage(f"Configuración guardada: {path}")

    def _load_config(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        from app.io.scenario_io import load_scenario_config
        path, _ = QFileDialog.getOpenFileName(self, "Cargar configuración", "", "JSON (*.json)")
        if not path:
            return
        cfg = load_scenario_config(path)
        message = self.engine.apply_scenario_configuration(cfg)
        self._sync_parameters_from_engine()
        self._sync_mode_selector()
        self._refresh_ui()
        self.statusBar().showMessage(message)
```
Wire both buttons in `_connect_signals`.

- [ ] **Step 6: Commit**

```bash
git add app/io/scenario_io.py tests/test_scenario_io.py app/ui/panels.py app/ui/control_window.py
git commit -m "feat: save/load scenario config JSON"
```

### Task 6.6: Live charts panel (QtCharts, graceful fallback)

**Files:**
- Create: `app/ui/charts_panel.py`
- Modify: `app/ui/panels.py`, `app/ui/control_window.py`

- [ ] **Step 1: Verify QtCharts importable**

Run: `uv run python -c "from PySide6.QtCharts import QChart; print('ok')"`
Expected: `ok`. If ImportError → the fallback path (Step 3) keeps the app working; note in commit.

- [ ] **Step 2: Create `app/ui/charts_panel.py`**

```python
from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

try:
    from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
    CHARTS_AVAILABLE = True
except ImportError:  # pragma: no cover - environment dependent
    CHARTS_AVAILABLE = False


class ChartsPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        if not CHARTS_AVAILABLE:
            layout.addWidget(QLabel("Gráficos no disponibles (QtCharts ausente)."))
            self._ok = False
            return
        self._ok = True
        self._batt = QLineSeries()
        self._batt.setName("Batería promedio")
        self._alerts = QLineSeries()
        self._alerts.setName("Alertas activas")
        chart = QChart()
        chart.addSeries(self._batt)
        chart.addSeries(self._alerts)
        chart.createDefaultAxes()
        view = QChartView(chart)
        layout.addWidget(view)

    def update_charts(self, battery_window, alert_window) -> None:
        if not self._ok:
            return
        self._batt.clear()
        for t, v in battery_window:
            self._batt.append(t, v)
        self._alerts.clear()
        for t, v in alert_window:
            self._alerts.append(t, v)
```

- [ ] **Step 3:** In `panels.py` add `ChartsPanel` to `ControlTabsWidget` as a tab `"Gráficos"`. In `control_window.py` `_refresh_ui` add:

```python
        self.panels.charts_panel.update_charts(
            self.engine.metrics.battery_window, self.engine.metrics.alert_window)
```

- [ ] **Step 4: Manual smoke** — run sim, watch battery line drop, alert line move.

- [ ] **Step 5: Full suite + headless**

Run: `./test.sh`
Expected: all passed.

- [ ] **Step 6: Commit**

```bash
git add app/ui/charts_panel.py app/ui/panels.py app/ui/control_window.py
git commit -m "feat: live charts panel with QtCharts fallback"
```

---

## Final verification

- [ ] Run full suite: `./test.sh` — all green.
- [ ] Headless determinism: `uv run python main.py --headless --scenario "Protección de zona estratégica" --duration 30 --seed 1 --out /tmp/run1` then again `/tmp/run2`; `diff /tmp/run1/summary.json /tmp/run2/summary.json` → no diff.
- [ ] GUI smoke: `./run.sh` — load each scenario, start, pause/resume, RTB observed, export report, save/load config, charts update, shortcuts work.
- [ ] `uv run --group dev ruff check app tests` — clean (fix or justify).
- [ ] Update `README.md` + `CLAUDE.md` Commands section: headless usage, `./test.sh`. Commit `docs: document headless mode and tests`.

---

## Self-review notes (author)

- Spec coverage: P0–P6 each mapped to tasks; RTB-vs-manual priority enforced in `BatteryService.evaluate` (manual returns None) + `_apply_state_overrides`. Charts fallback per spec risk. Headless avoids `app/ui` imports (lazy import in `main._run_gui`). Time-scale in headless via `run_headless(time_scale=...)`.
- Type consistency: `MetricsService` exposes `battery_window`, `alert_window`, `timeseries_rows()`, `build_summary()` — used identically in exporter, headless, charts, export button. `export_run(out_dir, rows, summary)->dict` signature consistent across callers. `_tick_units(dt)` defined Task 4.1, referenced by Task 3.2/3.4 (note flags the ordering dependency).
- Ordering dependency: Task 3.4 headless test deferred to run at Task 4.1 Step 4 (documented inline).
