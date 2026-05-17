from __future__ import annotations

from collections import deque
from math import hypot

from app.config import settings
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
        # _rows grows unbounded by design: full-fidelity timeseries for CSV export.
        # Acceptable for thesis-scale runs; a long headless run trades memory for completeness.
        self._rows: list[dict[str, object]] = []
        self.battery_window: deque[tuple[float, float]] = deque(maxlen=settings.METRICS_CHART_WINDOW)
        self.alert_window: deque[tuple[float, int]] = deque(maxlen=settings.METRICS_CHART_WINDOW)

    def reset(self) -> None:
        self._init_state()

    def record_tick(self, sim_time: float, units: list[AutonomousUnit],
                    active_alert_count: int = 0) -> None:
        batteries: list[float] = []
        for u in units:
            prev = self._last_pos.get(u.identifier)
            if prev is not None:
                self._distance[u.identifier] = self._distance.get(u.identifier, 0.0) + hypot(
                    u.x - prev[0], u.y - prev[1])
            else:
                self._distance.setdefault(u.identifier, 0.0)
            self._last_pos[u.identifier] = (u.x, u.y)

            if (u.state == settings.STATUS_OBJETIVO_ALCANZADO
                    and self._prev_state.get(u.identifier) != settings.STATUS_OBJETIVO_ALCANZADO):
                self._objectives[u.identifier] = self._objectives.get(u.identifier, 0) + 1
                self._first_objective_time.setdefault(u.identifier, sim_time)
            self._objectives.setdefault(u.identifier, 0)
            self._prev_state[u.identifier] = u.state

            batteries.append(u.battery)
            self._rows.append({
                "sim_time": round(sim_time, 2),
                "unit_id": u.identifier,
                "x": round(u.x, 3),
                "y": round(u.y, 3),
                "battery": round(u.battery, 2),
                "state": u.state,
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
                }
                for uid in self._distance
            },
        }
