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
