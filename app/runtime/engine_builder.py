from __future__ import annotations

import random

from app.simulation.simulation_engine import SimulationEngine


def build_engine(scenario_name: str, seed: int | None = None) -> SimulationEngine:
    if seed is not None:
        random.seed(seed)
    engine = SimulationEngine()
    engine.apply_scenario_profile(scenario_name)
    return engine
