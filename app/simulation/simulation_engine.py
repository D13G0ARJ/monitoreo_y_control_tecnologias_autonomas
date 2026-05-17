from __future__ import annotations

import random
from math import cos, hypot, pi, sin

from PySide6.QtCore import QObject, QTimer, Signal

from app.config import settings
from app.domain.alert import Alert
from app.domain.autonomous_unit import AutonomousUnit
from app.domain.waypoint import Waypoint
from app.services.alert_service import AlertService
from app.services.battery_service import BatteryService
from app.services.mode_service import ModeService
from app.services.scenario_service import ScenarioApplicationConfig, ScenarioService
from app.services.swarm_service import SwarmService, SwarmSummary
from app.simulation.control import move_toward_waypoint


class SimulationEngine(QObject):
    updated = Signal()
    alerts_updated = Signal(object)
    selection_changed = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.units: dict[str, AutonomousUnit] = {}
        self.mode: str = settings.MODE_DEFENSIVE
        self.zone_radius: float = settings.DEFAULT_ZONE_RADIUS
        self.max_speed: float = settings.MAX_SPEED
        self.target_altitude: float = settings.DEFAULT_ALTITUDE
        self.min_separation: float = settings.DEFAULT_MIN_SEPARATION
        self.low_battery_threshold: float = settings.DEFAULT_LOW_BATTERY_THRESHOLD
        self.active_unit_target: int = settings.DEFAULT_ACTIVE_UNITS
        self.recent_alerts: list[Alert] = []
        self.active_pair_alerts: set[tuple[str, str]] = set()
        self.is_running = False
        self.simulation_time = 0.0
        self.simulation_status = "Detenida"
        self.selected_unit_id: str | None = None
        self.current_scenario_name = settings.SCENARIO_ZONE_PROTECTION
        self.current_scenario_description = settings.SCENARIO_CONFIG[self.current_scenario_name]["description"]
        self.current_scenario_visuals = dict(settings.SCENARIO_CONFIG[self.current_scenario_name])
        self.current_swarm_count = 1
        self.current_distribution = "Automática"
        self.configured_unit_count = settings.DEFAULT_ACTIVE_UNITS
        self._next_unit_number = 1
        self._next_waypoint_number = 1

        self._alert_service = AlertService()
        self._mode_service = ModeService()
        self._swarm_service = SwarmService()
        self._scenario_service = ScenarioService(self._swarm_service)
        self._battery_service = BatteryService()
        self._timer = QTimer(self)
        self._timer.setInterval(settings.SIMULATION_INTERVAL_MS)
        self._timer.timeout.connect(self.update_simulation)

    def create_unit(self) -> AutonomousUnit:
        identifier = f"U{self._next_unit_number:02d}"
        self._next_unit_number += 1

        x, y = self._generate_spawn_position()
        speed = random.uniform(settings.MIN_SPEED + 10.0, max(settings.MIN_SPEED + 12.0, self.max_speed - 5.0))

        unit = AutonomousUnit(
            identifier=identifier,
            x=x,
            y=y,
            altitude=self.target_altitude,
            speed=speed,
            nominal_speed=speed,
            battery=100.0,
        )
        self.units[identifier] = unit
        self.updated.emit()
        return unit

    def set_waypoint_for_unit(self, unit_id: str, x: float, y: float, temporary: bool = True) -> None:
        unit = self.units.get(unit_id)
        if unit is None:
            return

        waypoint = Waypoint(
            identifier=f"WP-{self._next_waypoint_number:02d}",
            x=x,
            y=y,
            altitude=self.target_altitude,
            kind="manual",
        )
        self._next_waypoint_number += 1

        if temporary:
            unit.mission_snapshot = self._build_mission_snapshot(unit)
            unit.task_label = settings.TASK_TEMPORARY
        else:
            unit.mission_snapshot = None
            unit.role = settings.ROLE_MANUAL
            unit.route = []
            unit.current_waypoint_index = None
            unit.route_loop = False
            unit.route_forward = True
            unit.patrol_points = []
            unit.task_label = settings.TASK_MANUAL

        unit.waypoint = waypoint
        unit.state = settings.STATUS_EN_RUTA
        unit.distance_to_target = hypot(waypoint.x - unit.x, waypoint.y - unit.y)
        self.updated.emit()

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        self._mode_service.apply_mode(mode, list(self.units.values()), self.zone_radius)
        for unit in self.units.values():
            unit.altitude = self.target_altitude
            for waypoint in unit.route:
                waypoint.altitude = self.target_altitude
            if unit.waypoint is not None:
                unit.waypoint.altitude = self.target_altitude
        self.updated.emit()

    def ensure_unit_count(self, target_count: int) -> None:
        target_count = max(0, target_count)
        current_count = len(self.units)

        while current_count < target_count:
            self.create_unit()
            current_count += 1

        if current_count > target_count:
            identifiers = sorted(self.units.keys(), reverse=True)
            for identifier in identifiers[: current_count - target_count]:
                self.units.pop(identifier, None)
                if self.selected_unit_id == identifier:
                    self.selected_unit_id = None

        self.active_unit_target = target_count
        self.selection_changed.emit(self.selected_unit_id)
        self.updated.emit()

    def replace_units(self, target_count: int) -> None:
        self.units.clear()
        self.selected_unit_id = None
        self._next_unit_number = 1
        self.active_pair_alerts.clear()
        self.ensure_unit_count(target_count)

    def prepare_units_for_scenario(self) -> None:
        for unit in self.units.values():
            unit.mission_snapshot = None
            unit.task_label = settings.TASK_AUTOMATIC
            unit.route = []
            unit.current_waypoint_index = None
            unit.route_loop = False
            unit.route_forward = True
            unit.waypoint = None
            unit.distance_to_target = None
            unit.altitude = self.target_altitude
            unit.nominal_speed = min(unit.nominal_speed, self.max_speed)
            unit.speed = unit.nominal_speed

    def apply_mode_configuration(self, scenario_name: str | None = None) -> None:
        if scenario_name:
            scenario = settings.SCENARIO_CONFIG.get(scenario_name, {})
            self.mode = str(scenario.get("mode", self.mode))
        self.prepare_units_for_scenario()
        self._mode_service.apply_mode(self.mode, list(self.units.values()), self.zone_radius)
        self.updated.emit()

    def configure_scenario_from_dialog(self, dialog_result) -> str:
        config = self._scenario_service.from_dialog(dialog_result)
        self.current_swarm_count = config.swarm_count
        self.current_distribution = config.distribution
        self.configured_unit_count = config.unit_count
        return self._scenario_service.apply(self, config)

    def start(self) -> None:
        self.is_running = True
        self.simulation_status = "En ejecución"
        if not self._timer.isActive():
            self._timer.start()
        for unit in self.units.values():
            if unit.state_before_pause is not None:
                unit.state = unit.state_before_pause
                unit.state_before_pause = None
        self.updated.emit()

    def pause(self) -> None:
        self.is_running = False
        self.simulation_status = "Pausada"
        self._timer.stop()
        for unit in self.units.values():
            if unit.state in {
                settings.STATUS_ACTIVO,
                settings.STATUS_EN_RUTA,
                settings.STATUS_PATRULLANDO,
                settings.STATUS_RECONOCIMIENTO,
            }:
                unit.state_before_pause = unit.state
                unit.state = settings.STATUS_DETENIDO
        self.updated.emit()

    def reset(self) -> None:
        self.is_running = False
        self.simulation_status = "Detenida"
        self._timer.stop()
        self.simulation_time = 0.0
        for unit in self.units.values():
            unit.reset()
        self.recent_alerts.clear()
        self.active_pair_alerts.clear()
        self.alerts_updated.emit([])
        if self.units:
            self._swarm_service.assign_swarms(
                units=list(self.units.values()),
                scenario_name=self.current_scenario_name,
                swarm_count=self.current_swarm_count,
                distribution=self.current_distribution,
            )
            self.apply_mode_configuration(self.current_scenario_name)
        self.updated.emit()

    def clear_alert_history(self) -> None:
        self.recent_alerts.clear()
        self.alerts_updated.emit([])
        self.updated.emit()

    def set_selected_unit(self, unit_id: str | None) -> None:
        self.selected_unit_id = unit_id if unit_id in self.units else None
        self.selection_changed.emit(self.selected_unit_id)
        self.updated.emit()

    def update_max_speed(self, value: float) -> None:
        self.max_speed = value
        for unit in self.units.values():
            unit.nominal_speed = min(unit.nominal_speed, self.max_speed)
            unit.speed = min(unit.speed, self.max_speed)
        self.updated.emit()

    def update_target_altitude(self, value: float) -> None:
        self.target_altitude = value
        for unit in self.units.values():
            unit.altitude = value
            if unit.waypoint is not None:
                unit.waypoint.altitude = value
            for waypoint in unit.route:
                waypoint.altitude = value
        self.updated.emit()

    def update_min_separation(self, value: float) -> None:
        self.min_separation = value
        self.updated.emit()

    def update_zone_radius(self, value: float) -> None:
        self.zone_radius = value
        self.current_scenario_visuals["zone_radius"] = value
        self.updated.emit()

    def update_low_battery_threshold(self, value: float) -> None:
        self.low_battery_threshold = value
        self.updated.emit()

    def update_active_unit_target(self, value: int) -> None:
        self.ensure_unit_count(value)
        self.configured_unit_count = value
        if self.units:
            self._swarm_service.assign_swarms(
                units=list(self.units.values()),
                scenario_name=self.current_scenario_name,
                swarm_count=self.current_swarm_count,
                distribution=self.current_distribution,
            )
            self.apply_mode_configuration(self.current_scenario_name)

    def get_global_status(self) -> dict[str, str]:
        return {
            "scenario": self.current_scenario_name,
            "description": self.current_scenario_description,
            "mode": self.mode,
            "units": str(len(self.units)),
            "configured_units": str(self.configured_unit_count),
            "swarms": str(len(self.get_swarm_summaries())),
            "alerts": str(self.active_alert_count),
            "simulation": self.simulation_status,
            "time": self.format_simulation_time(),
            "max_speed": f"{self.max_speed:0.1f} u/s",
            "zone_radius": f"{self.zone_radius:0.1f} u",
            "min_separation": f"{self.min_separation:0.1f} u",
            "low_battery_threshold": f"{self.low_battery_threshold:0.1f} %",
            "swarm_overview": self._swarm_service.build_swarm_overview(list(self.units.values())),
        }

    def get_swarm_summaries(self) -> list[SwarmSummary]:
        return self._swarm_service.summarize(list(self.units.values()))

    def get_scenario_dialog_defaults(self, scenario_name: str) -> dict[str, float | int | str | bool]:
        return self._scenario_service.build_dialog_defaults(self, scenario_name)

    def apply_scenario_configuration(self, config: ScenarioApplicationConfig) -> str:
        return self._scenario_service.apply(self, config)

    @property
    def active_alert_count(self) -> int:
        unit_alerts = sum(len(unit.active_alerts) for unit in self.units.values())
        return unit_alerts + len(self.active_pair_alerts)

    def format_simulation_time(self) -> str:
        total_seconds = int(self.simulation_time)
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def update_simulation(self) -> None:
        dt = settings.SIMULATION_INTERVAL_MS / 1000.0
        self.simulation_time += dt

        for unit in self.units.values():
            reached_target = False
            if not unit.is_charging:
                self._apply_battery_speed_policy(unit)

            rtb_action = self._battery_service.evaluate(unit, self.low_battery_threshold, dt)
            if rtb_action == "rtb_start":
                if unit.task_label != settings.TASK_TEMPORARY:
                    unit.mission_snapshot = self._build_mission_snapshot(unit)
                self._register_alerts([
                    Alert(
                        alert_type=settings.ALERT_RTB_START,
                        unit_id=unit.identifier,
                        swarm_id=unit.swarm_id,
                        message=f"La unidad {unit.identifier} inició retorno a base por batería baja.",
                        severity=settings.SEVERITY_INFO,
                        prefix="INFO",
                        key=f"{unit.identifier}:{settings.ALERT_RTB_START}",
                    )
                ])
            elif rtb_action == "recharge_done":
                self._restore_mission(unit)
                self._register_alerts([
                    Alert(
                        alert_type=settings.ALERT_RECHARGE_DONE,
                        unit_id=unit.identifier,
                        swarm_id=unit.swarm_id,
                        message=f"La unidad {unit.identifier} completó recarga y reanudó su misión.",
                        severity=settings.SEVERITY_INFO,
                        prefix="INFO",
                        key=f"{unit.identifier}:{settings.ALERT_RECHARGE_DONE}",
                    )
                ])

            if unit.is_charging:
                unit.active_alerts = [
                    alert for alert in unit.active_alerts
                    if alert not in {
                        settings.ALERT_BATTERY_LOW,
                        settings.ALERT_BATTERY_CRITICAL,
                        settings.ALERT_NO_BATTERY,
                    }
                ]
                unit.direction_x = 0.0
                unit.direction_y = 0.0
                unit.append_trajectory()
                continue

            if unit.battery <= 0.0:
                unit.direction_x = 0.0
                unit.direction_y = 0.0
                unit.speed = 0.0
                if unit.distance_to_target is None and unit.waypoint is not None:
                    unit.distance_to_target = hypot(unit.waypoint.x - unit.x, unit.waypoint.y - unit.y)
                self._apply_state_overrides(unit)
                unit.append_trajectory()
                _, new_alerts = self._alert_service.evaluate_unit(
                    unit,
                    self.zone_radius,
                    self.low_battery_threshold,
                )
                if new_alerts:
                    self._register_alerts(new_alerts)
                continue

            if unit.waypoint is not None:
                reached_target = move_toward_waypoint(
                    unit=unit,
                    waypoint=unit.waypoint,
                    dt=dt,
                    max_speed=self.max_speed,
                    tolerance=settings.TARGET_TOLERANCE,
                    kp=settings.CONTROL_KP,
                )

            if unit.waypoint is not None and reached_target and unit.is_returning and unit.waypoint.kind == "base":
                self._battery_service.notify_base_reached(unit)
            elif unit.waypoint is not None and reached_target and unit.task_label == settings.TASK_TEMPORARY:
                self._restore_mission(unit)
            elif unit.waypoint is not None and reached_target and unit.route:
                self._mode_service.advance_unit_route(unit)
                unit.state = self._resolve_route_state(unit)
            elif unit.waypoint is not None and reached_target:
                unit.state = settings.STATUS_OBJETIVO_ALCANZADO
            elif unit.waypoint is not None:
                unit.state = self._resolve_route_state(unit)
            else:
                unit.distance_to_target = None
                unit.direction_x = 0.0
                unit.direction_y = 0.0
                unit.state = settings.STATUS_ACTIVO if self.is_running else settings.STATUS_DETENIDO

            self._drain_battery(unit, dt)
            self._apply_state_overrides(unit)
            unit.append_trajectory()

            _, new_alerts = self._alert_service.evaluate_unit(
                unit,
                self.zone_radius,
                self.low_battery_threshold,
            )
            if new_alerts:
                self._register_alerts(new_alerts)

        proximity_alerts = self._handle_proximity_monitoring()
        if proximity_alerts:
            self._register_alerts(proximity_alerts)

        self.updated.emit()

    def _handle_proximity_monitoring(self) -> list[Alert]:
        new_alerts: list[Alert] = []
        active_pairs_now: set[tuple[str, str]] = set()
        identifiers = sorted(self.units.keys())

        for left_index, left_id in enumerate(identifiers):
            left_unit = self.units[left_id]
            for right_id in identifiers[left_index + 1 :]:
                right_unit = self.units[right_id]
                distance = hypot(left_unit.x - right_unit.x, left_unit.y - right_unit.y)
                pair_key = tuple(sorted((left_id, right_id)))

                if distance < self.min_separation:
                    active_pairs_now.add(pair_key)
                    self._apply_separation_correction(left_unit, right_unit, distance)
                    if pair_key not in self.active_pair_alerts:
                        new_alerts.append(
                            Alert(
                                alert_type=settings.ALERT_PROXIMITY,
                                unit_id=f"{left_id}/{right_id}",
                                swarm_id=f"{left_unit.swarm_id}/{right_unit.swarm_id}",
                                message=f"Las unidades {left_id} y {right_id} se aproximaron por debajo de la separación mínima.",
                                severity=settings.SEVERITY_WARN,
                                prefix="WARN",
                                key=f"{left_id}:{right_id}:{settings.ALERT_PROXIMITY}",
                            )
                        )

        self.active_pair_alerts = active_pairs_now
        return new_alerts

    def _apply_separation_correction(self, left_unit: AutonomousUnit, right_unit: AutonomousUnit, distance: float) -> None:
        if distance == 0:
            return

        overlap = (self.min_separation - distance) / 2.0
        dx = (left_unit.x - right_unit.x) / distance
        dy = (left_unit.y - right_unit.y) / distance

        left_unit.x += dx * overlap * settings.SEPARATION_CORRECTION_GAIN
        left_unit.y += dy * overlap * settings.SEPARATION_CORRECTION_GAIN
        right_unit.x -= dx * overlap * settings.SEPARATION_CORRECTION_GAIN
        right_unit.y -= dy * overlap * settings.SEPARATION_CORRECTION_GAIN

    def _register_alerts(self, alerts: list[Alert]) -> None:
        self.recent_alerts = (alerts + self.recent_alerts)[:100]
        self.alerts_updated.emit(alerts)

    def _restore_mission(self, unit: AutonomousUnit) -> None:
        unit.is_returning = False
        unit.is_charging = False
        if not unit.mission_snapshot:
            unit.task_label = settings.TASK_AUTOMATIC
            unit.state = settings.STATUS_OBJETIVO_ALCANZADO
            return

        snapshot = unit.mission_snapshot
        unit.role = str(snapshot["role"])
        unit.route = list(snapshot["route"])
        unit.current_waypoint_index = snapshot["current_waypoint_index"]
        unit.route_loop = bool(snapshot["route_loop"])
        unit.route_forward = bool(snapshot["route_forward"])
        unit.patrol_points = list(snapshot["patrol_points"])
        unit.task_label = settings.TASK_AUTOMATIC
        unit.mission_snapshot = None

        if unit.route and unit.current_waypoint_index is not None:
            unit.waypoint = unit.route[unit.current_waypoint_index]
            unit.distance_to_target = hypot(unit.waypoint.x - unit.x, unit.waypoint.y - unit.y)
        else:
            unit.waypoint = None
            unit.distance_to_target = None

        unit.state = self._resolve_route_state(unit)

    @staticmethod
    def _build_mission_snapshot(unit: AutonomousUnit) -> dict[str, object] | None:
        if not unit.route and unit.role not in {settings.ROLE_PATROL, settings.ROLE_RECON}:
            return None

        return {
            "role": unit.role,
            "route": list(unit.route),
            "current_waypoint_index": unit.current_waypoint_index,
            "route_loop": unit.route_loop,
            "route_forward": unit.route_forward,
            "patrol_points": list(unit.patrol_points),
        }

    def _drain_battery(self, unit: AutonomousUnit, dt: float) -> None:
        moving_factor = max(abs(unit.direction_x), abs(unit.direction_y))
        drain = settings.BATTERY_DRAIN_IDLE + (unit.speed * moving_factor * settings.BATTERY_DRAIN_MOVING_FACTOR)
        unit.battery = max(0.0, unit.battery - drain * (dt * settings.BATTERY_DRAIN_DT_SCALE))

    def _apply_state_overrides(self, unit: AutonomousUnit) -> None:
        if unit.is_charging:
            unit.state = settings.STATUS_RECARGANDO
            return
        if unit.is_returning:
            unit.state = settings.STATUS_REGRESANDO
            return
        if unit.battery <= 0.0:
            unit.state = settings.STATUS_SIN_BATERIA
        elif hypot(unit.x, unit.y) > self.zone_radius:
            unit.state = settings.STATUS_FUERA_DE_ZONA
        elif unit.battery <= settings.CRITICAL_BATTERY_THRESHOLD:
            unit.state = settings.STATUS_CRITICO
        elif unit.battery < self.low_battery_threshold:
            unit.state = settings.STATUS_BATERIA_BAJA
        elif unit.distance_to_target == 0.0 and not unit.route and unit.task_label != settings.TASK_TEMPORARY:
            unit.state = settings.STATUS_OBJETIVO_ALCANZADO

    def _apply_battery_speed_policy(self, unit: AutonomousUnit) -> None:
        nominal_speed = min(unit.nominal_speed, self.max_speed)
        if unit.battery <= 0.0:
            unit.speed = 0.0
            return
        if unit.battery <= settings.CRITICAL_BATTERY_THRESHOLD:
            unit.speed = max(0.0, nominal_speed * 0.3)
            return
        unit.speed = nominal_speed

    @staticmethod
    def _resolve_route_state(unit: AutonomousUnit) -> str:
        if unit.task_label == settings.TASK_TEMPORARY:
            return settings.STATUS_EN_RUTA
        if unit.role == settings.ROLE_PATROL:
            return settings.STATUS_PATRULLANDO
        if unit.role == settings.ROLE_RECON:
            return settings.STATUS_RECONOCIMIENTO
        if unit.role == settings.ROLE_MANUAL:
            return settings.STATUS_EN_RUTA if unit.distance_to_target not in {0.0, None} else settings.STATUS_OBJETIVO_ALCANZADO
        return settings.STATUS_EN_RUTA

    def _generate_spawn_position(self) -> tuple[float, float]:
        for _ in range(50):
            angle = random.uniform(0.0, 2 * pi)
            radius = random.uniform(settings.SPAWN_MIN_RADIUS, self.zone_radius * settings.SPAWN_MAX_RADIUS_FACTOR)
            x = radius * cos(angle)
            y = radius * sin(angle)
            if self._is_position_available(x, y):
                return x, y
        return 0.0, 0.0

    def _is_position_available(self, x: float, y: float) -> bool:
        for unit in self.units.values():
            if hypot(unit.x - x, unit.y - y) < settings.SPAWN_MIN_DISTANCE:
                return False
        return True
