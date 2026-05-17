from __future__ import annotations

from app.config import settings
from app.io.exporter import export_run
from app.runtime.engine_builder import build_engine


def run_headless(scenario_name: str, duration_s: float, out_dir: str,
                 seed: int | None = None, time_scale: int = 1) -> dict[str, str]:
    engine = build_engine(scenario_name, seed=seed)
    dt = settings.SIMULATION_INTERVAL_MS / 1000.0
    steps = int((duration_s / dt) / max(1, time_scale))
    # headless drives ticks manually; QTimer is never started, so set the flag directly
    engine.is_running = True
    for _ in range(steps):
        engine.step(dt * time_scale)
    summary = engine.metrics.build_summary(engine.get_global_status())
    return export_run(out_dir, engine.metrics.timeseries_rows(), summary)
