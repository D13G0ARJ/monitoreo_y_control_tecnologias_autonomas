from __future__ import annotations

import json
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from app.config import settings
from app.io.exporter import export_run
from app.io.scenario_io import load_scenario_config, save_scenario_config
from app.services.scenario_service import ScenarioApplicationConfig, ScenarioService
from app.services.swarm_service import SwarmService
from app.simulation.simulation_engine import SimulationEngine
from app.ui.control_window import ControlWindow


SCENARIO_DIR = Path(__file__).resolve().parents[1] / "scenarios"
SCENARIO_FILES = sorted(
    path for path in SCENARIO_DIR.glob("*.json")
    if path.name not in {"summary.json"}
)


def _load(name: str):
    return load_scenario_config(SCENARIO_DIR / name)


def _apply(name: str) -> SimulationEngine:
    engine = SimulationEngine()
    message = engine.apply_scenario_configuration(_load(name))
    assert "Escenario aplicado" in message
    return engine


@pytest.mark.parametrize("scenario_name", settings.AVAILABLE_SCENARIOS)
def test_builtin_scenario_profile_is_complete(scenario_name: str):
    profile = ScenarioService(SwarmService()).profile_for(scenario_name)

    assert profile.scenario_name == scenario_name
    assert profile.unit_count >= 1
    assert profile.swarm_count >= 1
    assert profile.distribution in {settings.DISTRIBUTION_AUTO, settings.DISTRIBUTION_HALF}
    assert profile.mode in settings.AVAILABLE_MODES
    assert settings.MIN_SPEED <= profile.max_speed <= 120.0
    assert settings.MIN_ALTITUDE <= profile.target_altitude <= settings.MAX_ALTITUDE
    assert profile.zone_radius > 0.0
    assert profile.min_separation > 0.0
    assert profile.low_battery_threshold > 0.0
    assert profile.protected_radius > 0.0
    assert profile.observation_points


@pytest.mark.parametrize("path", SCENARIO_FILES, ids=lambda p: p.name)
def test_reusable_scenario_fixture_is_valid_and_roundtrips(path: Path, tmp_path: Path):
    config = load_scenario_config(path)
    copy_path = tmp_path / path.name
    save_scenario_config(copy_path, config)
    assert load_scenario_config(copy_path) == config


@pytest.mark.parametrize("path", SCENARIO_FILES, ids=lambda p: p.name)
def test_reusable_scenario_applies_to_engine(path: Path):
    config = load_scenario_config(path)
    engine = SimulationEngine()
    engine.apply_scenario_configuration(config)

    assert engine.current_scenario_name == config.scenario_name
    assert len(engine.units) == config.unit_count
    assert engine.configured_unit_count == config.unit_count
    assert engine.zone_radius == config.zone_radius
    assert engine.min_separation == config.min_separation
    assert engine.low_battery_threshold == config.low_battery_threshold
    assert engine.max_speed == config.max_speed
    assert engine.target_altitude == config.target_altitude
    assert engine.current_scenario_visuals["configured_units"] == config.unit_count
    assert engine.current_scenario_visuals["configured_swarms"] >= config.swarm_count
    assert engine.mode == config.mode
    assert engine.scenario_config_source == settings.SCENARIO_SOURCE_FILE
    assert not engine.scenario_config_dirty


def test_zone_fixture_exercises_defensive_patrol_routes():
    engine = _apply("zone_protection_baseline.json")

    assert engine.mode == settings.MODE_DEFENSIVE
    assert {unit.swarm_id for unit in engine.units.values()} == {"E1"}
    assert all(unit.role == settings.ROLE_PATROL for unit in engine.units.values())
    assert all(unit.route_loop for unit in engine.units.values())
    assert all(unit.waypoint is not None for unit in engine.units.values())


def test_recon_fixture_exercises_non_loop_recon_routes():
    engine = _apply("recon_area_baseline.json")

    assert engine.mode == settings.MODE_RECON
    assert all(unit.role == settings.ROLE_RECON for unit in engine.units.values())
    assert all(not unit.route_loop for unit in engine.units.values())
    assert all(len(unit.route) == 4 for unit in engine.units.values())


def test_combined_fixture_exercises_swarm_split_and_export(tmp_path: Path):
    engine = _apply("combined_swarm_demo.json")

    swarms = engine.get_swarm_summaries()
    assert {summary.swarm_id for summary in swarms} == {"E1", "E2"}
    assert {summary.swarm_role for summary in swarms} == {settings.ROLE_PATROL, settings.ROLE_RECON}

    engine.set_time_scale(4)
    engine.start()
    for _ in range(8):
        engine.update_simulation()

    paths = export_run(tmp_path, engine.metrics.timeseries_rows(), engine.metrics.build_summary(engine.get_global_status()))
    assert Path(paths["timeseries"]).exists()
    assert Path(paths["summary"]).exists()
    summary = json.loads(Path(paths["summary"]).read_text(encoding="utf-8"))
    assert summary["scenario"]["scenario"] == settings.SCENARIO_COMBINED
    assert set(summary["units"]) == set(engine.units)


def test_builtin_profile_application_marks_predefined_source():
    engine = SimulationEngine()
    engine.apply_scenario_profile(settings.SCENARIO_RECON_AREA)

    profile = engine.active_scenario_profile
    assert profile is not None
    assert engine.current_scenario_name == settings.SCENARIO_RECON_AREA
    assert engine.scenario_config_source == settings.SCENARIO_SOURCE_PREDEFINED
    assert engine.get_scenario_source_label() == settings.SCENARIO_SOURCE_PREDEFINED
    assert len(engine.units) == profile.unit_count
    assert engine.current_swarm_count == profile.swarm_count
    assert engine.current_distribution == profile.distribution
    assert engine.mode == profile.mode
    assert engine.max_speed == profile.max_speed
    assert engine.target_altitude == profile.target_altitude
    assert engine.current_scenario_visuals["protected_radius"] == profile.protected_radius
    assert engine.current_scenario_visuals["observation_points"] == profile.observation_points


def test_loaded_json_config_marks_file_source():
    config = ScenarioApplicationConfig(
        scenario_name=settings.SCENARIO_ZONE_PROTECTION,
        unit_count=3,
        swarm_count=1,
        distribution=settings.DISTRIBUTION_AUTO,
        use_existing_units=False,
        mode=settings.MODE_DEFENSIVE,
        max_speed=66.0,
        target_altitude=155.0,
        zone_radius=300.0,
        min_separation=36.0,
        low_battery_threshold=18.0,
        protected_radius=80.0,
        observation_points=[(1.0, 2.0)],
        auto_start=False,
    )
    engine = SimulationEngine()
    engine.apply_loaded_scenario_configuration(config)

    assert engine.scenario_config_source == settings.SCENARIO_SOURCE_FILE
    assert engine.get_scenario_source_label() == settings.SCENARIO_SOURCE_FILE
    assert engine.active_scenario_profile == config


def test_manual_parameter_change_marks_config_modified_and_restore_clears_it():
    engine = SimulationEngine()
    engine.apply_scenario_profile(settings.SCENARIO_RECON_AREA)
    original_speed = engine.max_speed

    engine.update_max_speed(original_speed - 5.0)

    assert engine.scenario_config_dirty
    assert engine.get_scenario_source_label() == settings.SCENARIO_SOURCE_MANUAL

    engine.restore_active_scenario_profile()

    assert not engine.scenario_config_dirty
    assert engine.get_scenario_source_label() == settings.SCENARIO_SOURCE_PREDEFINED
    assert engine.max_speed == original_speed


def test_zone_radius_change_recalculates_routes():
    engine = SimulationEngine()
    engine.apply_scenario_profile(settings.SCENARIO_ZONE_PROTECTION)
    unit = next(iter(engine.units.values()))
    before = [(point.x, point.y) for point in unit.route]

    engine.update_zone_radius(260.0)

    after = [(point.x, point.y) for point in unit.route]
    assert engine.scenario_config_dirty
    assert before != after
    assert after[0][0] == pytest.approx(260.0 * settings.PATROL_ORBIT_FACTOR)


def test_control_center_reflects_config_source_and_restore_state():
    app = QApplication.instance() or QApplication([])
    engine = SimulationEngine()
    engine.apply_scenario_profile(settings.SCENARIO_ZONE_PROTECTION)
    window = ControlWindow(engine)
    try:
        engine.update_low_battery_threshold(25.0)
        app.processEvents()
        window._sync_parameters_from_engine()
        window._refresh_ui()

        assert settings.SCENARIO_SOURCE_MANUAL in window.panels.scenario.source_label.text()
        assert "Configuración activa:" in window.panels.scenario.active_config_label.text()

        window._restore_scenario_defaults()

        assert settings.SCENARIO_SOURCE_PREDEFINED in window.panels.scenario.source_label.text()
        assert engine.low_battery_threshold == settings.DEFAULT_LOW_BATTERY_THRESHOLD
    finally:
        window.close()


def test_temporary_and_manual_assignment_paths_restore_or_override_mission():
    engine = _apply("zone_protection_baseline.json")
    unit = next(iter(engine.units.values()))
    engine.set_selected_unit(unit.identifier)

    original_route = list(unit.route)
    engine.set_waypoint_for_unit(unit.identifier, unit.x + 1.0, unit.y, temporary=True)
    assert unit.task_label == settings.TASK_TEMPORARY
    engine.start()
    for _ in range(10):
        engine.update_simulation()
        if unit.task_label == settings.TASK_AUTOMATIC:
            break
    assert unit.task_label == settings.TASK_AUTOMATIC
    assert unit.route == original_route

    engine.set_waypoint_for_unit(unit.identifier, unit.x + 1.0, unit.y, temporary=False)
    assert unit.task_label == settings.TASK_MANUAL
    assert unit.role == settings.ROLE_MANUAL
    assert unit.route == []


def test_rtb_fixture_exercises_low_battery_return_to_base_and_recharge():
    engine = _apply("rtb_low_battery_demo.json")
    unit = next(iter(engine.units.values()))
    unit.battery = 90.0
    engine.start()

    saw_rtb = False
    saw_charging = False
    for _ in range(1200):
        engine.update_simulation()
        saw_rtb = saw_rtb or unit.is_returning
        saw_charging = saw_charging or unit.is_charging
        if saw_charging:
            break

    assert saw_rtb
    assert saw_charging
    assert any(alert.alert_type == settings.ALERT_RTB_START for alert in engine.recent_alerts)


def test_proximity_fixture_exercises_pair_alerts_and_separation_correction():
    engine = _apply("proximity_alert_demo.json")
    left, right = list(engine.units.values())
    left.x = 0.0
    left.y = 0.0
    right.x = 10.0
    right.y = 0.0

    engine.start()
    engine.update_simulation()

    assert engine.active_pair_alerts == {(left.identifier, right.identifier)}
    assert any(alert.alert_type == settings.ALERT_PROXIMITY for alert in engine.recent_alerts)
    assert left.x < 0.0
    assert right.x > 10.0
