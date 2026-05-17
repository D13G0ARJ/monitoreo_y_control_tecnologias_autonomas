from __future__ import annotations

import pytest

pytestmark = pytest.mark.skipif(
    not hasattr(__import__("app.simulation.simulation_engine", fromlist=["SimulationEngine"]).SimulationEngine, "_tick_units"),
    reason="_tick_units extracted in Phase 4")

from pathlib import Path

from app.runtime.headless import run_headless


def test_headless_run_is_deterministic(tmp_path: Path):
    a = run_headless("Protección de zona estratégica", duration_s=5.0,
                     out_dir=str(tmp_path / "a"), seed=42)
    b = run_headless("Protección de zona estratégica", duration_s=5.0,
                     out_dir=str(tmp_path / "b"), seed=42)
    assert Path(a["summary"]).read_text() == Path(b["summary"]).read_text()
