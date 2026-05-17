from __future__ import annotations

from pathlib import Path

from app.runtime.headless import run_headless
from app.simulation.simulation_engine import SimulationEngine


def test_headless_run_is_deterministic(tmp_path: Path):
    a = run_headless("Protección de zona estratégica", duration_s=5.0,
                     out_dir=str(tmp_path / "a"), seed=42)
    b = run_headless("Protección de zona estratégica", duration_s=5.0,
                     out_dir=str(tmp_path / "b"), seed=42)
    assert Path(a["summary"]).read_text() == Path(b["summary"]).read_text()


def test_public_step_advances_time_and_records_metrics():
    engine = SimulationEngine()
    engine.create_unit()

    engine.step(0.25)

    assert engine.simulation_time == 0.25
    assert len(engine.metrics.timeseries_rows()) == 1


def test_format_simulation_time_ignores_tiny_float_drift():
    engine = SimulationEngine()
    engine.simulation_time = 4.999999999999998

    assert engine.format_simulation_time() == "00:05"
