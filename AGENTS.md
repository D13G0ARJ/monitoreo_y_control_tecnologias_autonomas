# Repository Guidelines

## Project Structure & Module Organization

This is a Python 3.12 desktop simulator using PySide6. `main.py` wires the GUI and runtime entry points. Application code lives under `app/`: `domain/` contains plain data models, `simulation/` owns the shared `SimulationEngine` and movement control, `services/` contains scenario, mode, swarm, battery, alert, and metrics logic, `ui/` contains Qt windows and panels, `io/` handles scenario/report import and export, `runtime/` supports GUI and headless execution, and `config/settings.py` centralizes constants. Tests live in `tests/`; documentation lives in `docs/`.

## Build, Test, and Development Commands

- `./setup.sh`: pin Python 3.12 with `uv`, create `.venv`, and install `requirements.txt`.
- `./run.sh`: run the desktop app with `uv run python main.py`.
- `uv run python main.py --headless --scenario "Protección de zona estratégica" --duration 30 --seed 1 --out run_output`: run deterministic headless simulation and export CSV/JSON reports.
- `./test.sh`: run the pytest suite through `uv` with dev dependencies.
- `uv run --group dev ruff check app tests`: lint source and tests.

Windows launchers are available as `run.bat` and `run.ps1`.

## Coding Style & Naming Conventions

Use 4-space indentation, Python type hints, and `from __future__ import annotations` in modules. Ruff targets Python 3.12 with a 120-character line length. Keep scenario and mode names in `app/config/settings.py` constants instead of hardcoding user-facing strings. UI code should read engine state and call engine/service methods; avoid direct mutation of engine internals from widgets.

## Testing Guidelines

Tests use `pytest` and are named `tests/test_*.py`. Prefer deterministic tests for services, exporters, scenario I/O, and headless runtime. For GUI-adjacent logic, test the service or engine behavior where possible before relying on manual Qt checks. Run `./test.sh` before submitting changes; run `ruff` when editing Python source.

## Commit & Pull Request Guidelines

Git history uses short Conventional Commit-style messages such as `feat: export report button` and `perf: incremental radar redraw, persistent unit items`. Keep commits scoped to one behavior change. Pull requests should describe the user-visible change, list verification commands, mention affected scenarios or modes, and include screenshots or short recordings for UI changes.

## Domain & Configuration Notes

This is an academic simulation-only project. Do not add real hardware, GPS, maps, weapons, live communications, database, or advanced AI integrations unless explicitly requested. Existing docs and UI strings are primarily Spanish; keep new user-facing text consistent with that language.
