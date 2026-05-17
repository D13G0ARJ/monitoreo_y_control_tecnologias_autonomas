# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Academic thesis project (UNEFA): desktop simulator for monitoring and control of autonomous units via a radar-style GUI. Defense/surveillance domain, **simulation only** — no real hardware, GPS, maps, weapons, AI, or database. Scope is intentionally limited; do not add real-world integrations. Project docs and UI strings are in Spanish — keep new user-facing text and docs in Spanish.

## Commands

Tooling: `uv` + Python 3.12. Runtime dependency is PySide6; development tools are pytest and ruff.

```bash
./setup.sh              # create .venv, install requirements (run on first setup or when requirements.txt changes)
./run.sh                # run app (uv run python main.py)
./test.sh               # run pytest through uv with dev dependencies
source ./env.sh         # activate existing .venv for manual work
uv run python main.py   # run without script
uv run python main.py --headless --scenario "Protección de zona estratégica" --duration 30 --seed 1 --out run_output
uv run --group dev ruff check app tests
```

Windows: `run.bat` / `run.ps1`. Manual steps in `docs/setup-dev.md`. Headless mode writes `timeseries.csv` and `summary.json` to the directory passed with `--out`.

## Architecture

Two-window Qt app sharing **one** `SimulationEngine`. `main.py` wires both windows to the same engine instance and connects cross-window signals.

- **`app/simulation/simulation_engine.py`** — core. `SimulationEngine(QObject)` holds all state (units dict, mode, scenario, alerts, sim time) and the `QTimer` tick. Emits `updated`, `alerts_updated`, `selection_changed` signals that the UI subscribes to. Largest/most central file (~530 lines) — most behavior changes start here.
- **`app/simulation/control.py`** — `move_toward_waypoint`: proportional (`CONTROL_KP`) movement toward a waypoint with speed clamping and tolerance. Pure function, no Qt.
- **`app/services/`** — stateless-ish helpers the engine composes: `ScenarioService` (builds `ScenarioApplicationConfig` from dialog, applies scenarios), `ModeService` (Defensivo/Reconocimiento/Mixto behavior), `SwarmService` (swarm grouping + labels like `U01 [E1-P]`), `AlertService` (severity INFO/WARN/CRIT, low-battery/separation rules).
- **`app/domain/`** — plain data: `AutonomousUnit`, `Waypoint`, `Alert`.
- **`app/ui/`** — `RadarOperationalWindow` (radar view, unit selection, waypoint picking) and `ControlWindow` (scenario config, manual control). `radar_view.py` and `panels.py` are the heavy widgets. UI is read-only over engine state + signals; it must not mutate engine internals directly — go through engine/service methods.
- **`app/config/settings.py`** — all tunables: window sizes, radar geometry, speeds, battery drain, thresholds, scenario/mode name constants, `SCENARIO_CONFIG`, stylesheet. Use these constants; do not hardcode magic numbers elsewhere.

### Data flow

`ScenarioDialog` → `ScenarioApplicationConfig` → `ScenarioService.apply` mutates `SimulationEngine` → timer tick advances units via `control.move_toward_waypoint`, runs mode/swarm/alert services → `updated` signal → both windows refresh. User clicks radar → `waypoint_requested` signal → assigned as a temporary task without losing the original mission.

### Conventions

- All modules use `from __future__ import annotations`; keep type hints.
- Scenario/mode identifiers are string constants in `settings.py` (e.g. `SCENARIO_*`, `MODE_*`) — reference them, never literal strings.
- Engine is the single source of truth; services take/return data and the engine owns mutation and signal emission.
