from __future__ import annotations

from dataclasses import dataclass, replace
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
    mode: str
    max_speed: float
    target_altitude: float
    zone_radius: float
    min_separation: float
    low_battery_threshold: float
    protected_radius: float
    observation_points: list[tuple[float, float]]
    auto_start: bool


class ScenarioService:
    def __init__(self, swarm_service: SwarmService) -> None:
        self._swarm_service = swarm_service

    def build_dialog_defaults(self, engine: "SimulationEngine", scenario_name: str) -> dict[str, float | int | str | bool]:
        profile = self.profile_for(scenario_name)

        return {
            "unit_count": profile.unit_count,
            "swarm_count": profile.swarm_count,
            "distribution": profile.distribution,
            "mode": profile.mode,
            "max_speed": profile.max_speed,
            "target_altitude": profile.target_altitude,
            "zone_radius": profile.zone_radius,
            "min_separation": profile.min_separation,
            "low_battery_threshold": profile.low_battery_threshold,
            "protected_radius": profile.protected_radius,
            "auto_start": False,
        }

    def profile_for(
        self,
        scenario_name: str,
        *,
        use_existing_units: bool = False,
        auto_start: bool = False,
    ) -> ScenarioApplicationConfig:
        scenario = settings.SCENARIO_CONFIG.get(scenario_name, {})
        return ScenarioApplicationConfig(
            scenario_name=scenario_name,
            unit_count=int(scenario.get("units", settings.DEFAULT_ACTIVE_UNITS)),
            swarm_count=int(scenario.get("swarms", 2 if scenario_name == settings.SCENARIO_COMBINED else 1)),
            distribution=str(
                scenario.get(
                    "distribution",
                    settings.DISTRIBUTION_HALF
                    if scenario_name == settings.SCENARIO_COMBINED
                    else settings.DISTRIBUTION_AUTO,
                )
            ),
            use_existing_units=use_existing_units,
            mode=str(scenario.get("mode", settings.MODE_DEFENSIVE)),
            max_speed=float(scenario.get("max_speed", settings.MAX_SPEED)),
            target_altitude=float(scenario.get("target_altitude", settings.DEFAULT_ALTITUDE)),
            zone_radius=float(scenario.get("zone_radius", settings.DEFAULT_ZONE_RADIUS)),
            min_separation=float(scenario.get("min_separation", settings.DEFAULT_MIN_SEPARATION)),
            low_battery_threshold=float(
                scenario.get("low_battery_threshold", settings.DEFAULT_LOW_BATTERY_THRESHOLD)
            ),
            protected_radius=float(scenario.get("protected_radius", 0.0)),
            observation_points=[
                (float(x), float(y))
                for x, y in scenario.get("observation_points", [])
            ],
            auto_start=auto_start,
        )

    def from_dialog(self, dialog_result: "ScenarioDialogResult") -> ScenarioApplicationConfig:
        profile = self.profile_for(dialog_result.scenario_name)
        return ScenarioApplicationConfig(
            scenario_name=dialog_result.scenario_name,
            unit_count=dialog_result.unit_count,
            swarm_count=dialog_result.swarm_count,
            distribution=dialog_result.distribution,
            use_existing_units=dialog_result.use_existing_units,
            mode=profile.mode,
            max_speed=dialog_result.max_speed,
            target_altitude=dialog_result.target_altitude,
            zone_radius=dialog_result.zone_radius,
            min_separation=dialog_result.min_separation,
            low_battery_threshold=dialog_result.low_battery_threshold,
            protected_radius=profile.protected_radius,
            observation_points=profile.observation_points,
            auto_start=dialog_result.auto_start,
        )

    def apply(self, engine: "SimulationEngine", config: ScenarioApplicationConfig) -> str:
        normalized = self.normalize_config(config)

        engine.mode = normalized.mode
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
        engine.current_scenario_visuals["protected_radius"] = normalized.protected_radius
        engine.current_scenario_visuals["observation_points"] = list(normalized.observation_points)
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

        engine.apply_mode_configuration()

        if normalized.auto_start:
            engine.start()
            return "Escenario aplicado e iniciado automáticamente."
        engine.updated.emit()
        return "Escenario aplicado correctamente."

    def normalize_config(self, config: ScenarioApplicationConfig) -> ScenarioApplicationConfig:
        if config.scenario_name == settings.SCENARIO_COMBINED and config.swarm_count < 2:
            config = replace(config, swarm_count=2)
        return replace(
            config,
            unit_count=max(1, config.unit_count),
            swarm_count=max(1, config.swarm_count),
            mode=config.mode if config.mode in settings.AVAILABLE_MODES else settings.MODE_DEFENSIVE,
            observation_points=[(float(x), float(y)) for x, y in config.observation_points],
        )
