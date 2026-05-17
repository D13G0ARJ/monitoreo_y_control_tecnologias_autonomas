from __future__ import annotations

from collections import Counter
from collections import deque
from math import hypot

from app.config import settings
from app.domain.alert import Alert
from app.domain.autonomous_unit import AutonomousUnit


class MetricsService:
    def __init__(self) -> None:
        self._init_state()

    def _init_state(self) -> None:
        self._last_pos: dict[str, tuple[float, float]] = {}
        self._distance: dict[str, float] = {}
        self._objectives: dict[str, int] = {}
        self._prev_state: dict[str, str] = {}
        self._first_objective_time: dict[str, float] = {}
        self._state_durations: dict[str, Counter[str]] = {}
        self._battery_samples: dict[str, list[float]] = {}
        self._alert_type_counts: Counter[str] = Counter()
        self._alert_severity_counts: Counter[str] = Counter()
        # _rows grows unbounded by design: full-fidelity timeseries for CSV export.
        # Acceptable for thesis-scale runs; a long headless run trades memory for completeness.
        self._rows: list[dict[str, object]] = []
        self.battery_window: deque[tuple[float, float]] = deque(maxlen=settings.METRICS_CHART_WINDOW)
        self.alert_window: deque[tuple[float, int]] = deque(maxlen=settings.METRICS_CHART_WINDOW)

    def reset(self) -> None:
        self._init_state()

    def record_alerts(self, alerts: list[Alert]) -> None:
        for alert in alerts:
            self._alert_type_counts[alert.alert_type] += 1
            self._alert_severity_counts[alert.severity] += 1

    def record_tick(
        self,
        sim_time: float,
        units: list[AutonomousUnit],
        active_alert_count: int = 0,
        dt: float = 0.0,
    ) -> None:
        batteries: list[float] = []
        for u in units:
            prev = self._last_pos.get(u.identifier)
            if prev is not None:
                self._distance[u.identifier] = self._distance.get(u.identifier, 0.0) + hypot(
                    u.x - prev[0], u.y - prev[1]
                )
            else:
                self._distance.setdefault(u.identifier, 0.0)
            self._last_pos[u.identifier] = (u.x, u.y)

            if (
                u.state == settings.STATUS_OBJETIVO_ALCANZADO
                and self._prev_state.get(u.identifier) != settings.STATUS_OBJETIVO_ALCANZADO
            ):
                self._objectives[u.identifier] = self._objectives.get(u.identifier, 0) + 1
                self._first_objective_time.setdefault(u.identifier, sim_time)
            self._objectives.setdefault(u.identifier, 0)
            self._prev_state[u.identifier] = u.state
            self._state_durations.setdefault(u.identifier, Counter())[u.state] += dt

            batteries.append(u.battery)
            self._battery_samples.setdefault(u.identifier, []).append(u.battery)
            target_x = u.waypoint.x if u.waypoint is not None else ""
            target_y = u.waypoint.y if u.waypoint is not None else ""
            self._rows.append({
                "sim_time": round(sim_time, 2),
                "unit_id": u.identifier,
                "x": round(u.x, 3),
                "y": round(u.y, 3),
                "battery": round(u.battery, 2),
                "state": u.state,
                "swarm_id": u.swarm_id,
                "role": u.role,
                "task": u.task_label,
                "speed": round(u.speed, 3),
                "altitude": round(u.altitude, 3),
                "target_x": round(target_x, 3) if target_x != "" else "",
                "target_y": round(target_y, 3) if target_y != "" else "",
                "distance_to_target": (
                    round(u.distance_to_target, 3)
                    if u.distance_to_target is not None
                    else ""
                ),
                "active_alerts": "; ".join(u.active_alerts),
            })

        avg_batt = sum(batteries) / len(batteries) if batteries else 0.0
        self.battery_window.append((round(sim_time, 2), round(avg_batt, 2)))
        self.alert_window.append((round(sim_time, 2), active_alert_count))

    def timeseries_rows(self) -> list[dict[str, object]]:
        return list(self._rows)

    def build_summary(self, scenario_info: dict[str, object]) -> dict[str, object]:
        return {
            "scenario": scenario_info,
            "units": {
                uid: {
                    "distance": round(self._distance.get(uid, 0.0), 3),
                    "objectives_reached": self._objectives.get(uid, 0),
                    "time_to_first_objective": self._first_objective_time.get(uid),
                    "battery": self._build_battery_summary(uid),
                    "state_durations": {
                        state: round(duration, 2)
                        for state, duration in self._state_durations.get(uid, {}).items()
                    },
                }
                for uid in self._distance
            },
            "alerts": {
                "by_type": dict(self._alert_type_counts),
                "by_severity": dict(self._alert_severity_counts),
            },
        }

    def _build_battery_summary(self, unit_id: str) -> dict[str, float | None]:
        samples = self._battery_samples.get(unit_id, [])
        if not samples:
            return {"min": None, "avg": None, "final": None}
        return {
            "min": round(min(samples), 2),
            "avg": round(sum(samples) / len(samples), 2),
            "final": round(samples[-1], 2),
        }
