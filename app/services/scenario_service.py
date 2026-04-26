from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.config import settings
from app.services.swarm_service import SwarmService

if TYPE_CHECKING:
    from app.simulation.simulation_engine import SimulationEngine
    from app.ui.scenario_dialog import ScenarioDialogResult


@dataclass
class ScenarioApplicationConfig:
    scenario_name: str
    unit_count: int
    swarm_count: int
    distribution: str
    use_existing_units: bool
    max_speed: float
    target_altitude: float
    zone_radius: float
    min_separation: float
    low_battery_threshold: float
    auto_start: bool


class ScenarioService:
    def __init__(self, swarm_service: SwarmService) -> None:
        self._swarm_service = swarm_service

    def build_dialog_defaults(self, engine: "SimulationEngine", scenario_name: str) -> dict[str, float | int | str | bool]:
        scenario = settings.SCENARIO_CONFIG.get(scenario_name, {})
        recommended_units = int(scenario.get("units", max(1, len(engine.units) or settings.DEFAULT_ACTIVE_UNITS)))
        recommended_swarms = 2 if scenario_name == settings.SCENARIO_COMBINED else 1

        return {
            "unit_count": len(engine.units) or recommended_units,
            "swarm_count": recommended_swarms,
            "distribution": "Mitad y mitad" if scenario_name == settings.SCENARIO_COMBINED else "Automática",
            "max_speed": engine.max_speed,
            "target_altitude": engine.target_altitude,
            "zone_radius": float(scenario.get("zone_radius", engine.zone_radius)),
            "min_separation": engine.min_separation,
            "low_battery_threshold": engine.low_battery_threshold,
            "auto_start": False,
        }

    def from_dialog(self, dialog_result: "ScenarioDialogResult") -> ScenarioApplicationConfig:
        return ScenarioApplicationConfig(
            scenario_name=dialog_result.scenario_name,
            unit_count=dialog_result.unit_count,
            swarm_count=dialog_result.swarm_count,
            distribution=dialog_result.distribution,
            use_existing_units=dialog_result.use_existing_units,
            max_speed=dialog_result.max_speed,
            target_altitude=dialog_result.target_altitude,
            zone_radius=dialog_result.zone_radius,
            min_separation=dialog_result.min_separation,
            low_battery_threshold=dialog_result.low_battery_threshold,
            auto_start=dialog_result.auto_start,
        )

    def apply(self, engine: "SimulationEngine", config: ScenarioApplicationConfig) -> str:
        normalized = self._normalize_config(config)

        engine.max_speed = normalized.max_speed
        engine.target_altitude = normalized.target_altitude
        engine.zone_radius = normalized.zone_radius
        engine.min_separation = normalized.min_separation
        engine.low_battery_threshold = normalized.low_battery_threshold
        engine.active_unit_target = normalized.unit_count
        engine.current_swarm_count = normalized.swarm_count
        engine.current_distribution = normalized.distribution
        engine.configured_unit_count = normalized.unit_count

        scenario = settings.SCENARIO_CONFIG.get(normalized.scenario_name, {})
        engine.current_scenario_name = normalized.scenario_name
        engine.current_scenario_description = str(scenario.get("description", ""))
        engine.current_scenario_visuals = dict(scenario)
        engine.current_scenario_visuals["zone_radius"] = normalized.zone_radius
        engine.current_scenario_visuals["configured_units"] = normalized.unit_count
        engine.current_scenario_visuals["configured_swarms"] = normalized.swarm_count

        if not engine.units or not normalized.use_existing_units:
            engine.replace_units(normalized.unit_count)
        elif normalized.unit_count > len(engine.units):
            engine.ensure_unit_count(normalized.unit_count)

        units = list(engine.units.values())
        self._swarm_service.assign_swarms(
            units=units,
            scenario_name=normalized.scenario_name,
            swarm_count=normalized.swarm_count,
            distribution=normalized.distribution,
        )

        engine.apply_mode_configuration(normalized.scenario_name)

        if normalized.auto_start:
            engine.start()
            return "Escenario aplicado e iniciado automáticamente."
        engine.updated.emit()
        return "Escenario aplicado correctamente."

    def _normalize_config(self, config: ScenarioApplicationConfig) -> ScenarioApplicationConfig:
        if config.scenario_name == settings.SCENARIO_COMBINED and config.swarm_count < 2:
            return ScenarioApplicationConfig(
                scenario_name=config.scenario_name,
                unit_count=config.unit_count,
                swarm_count=2,
                distribution=config.distribution,
                use_existing_units=config.use_existing_units,
                max_speed=config.max_speed,
                target_altitude=config.target_altitude,
                zone_radius=config.zone_radius,
                min_separation=config.min_separation,
                low_battery_threshold=config.low_battery_threshold,
                auto_start=config.auto_start,
            )
        return config
