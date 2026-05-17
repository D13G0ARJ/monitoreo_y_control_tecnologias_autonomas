from __future__ import annotations

from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit
from app.domain.waypoint import Waypoint


class BatteryService:
    """Stateless RTB + recharge decisions. Engine owns mutation/signals."""

    def evaluate(self, unit: AutonomousUnit, low_battery_threshold: float, dt: float) -> str | None:
        if unit.task_label == settings.TASK_MANUAL:
            return None

        if unit.is_charging:
            unit.battery = min(settings.RECHARGE_FULL, unit.battery + settings.RECHARGE_RATE * dt)
            unit.speed = 0.0
            unit.state = settings.STATUS_RECARGANDO
            if unit.battery >= settings.RECHARGE_FULL:
                unit.is_charging = False
                unit.is_returning = False
                return "recharge_done"
            return None

        if unit.is_returning:
            return None

        if unit.battery > 0.0 and unit.battery < low_battery_threshold:
            self._begin_return(unit)
            return "rtb_start"
        return None

    def notify_base_reached(self, unit: AutonomousUnit) -> None:
        if not unit.is_returning:
            return
        unit.is_charging = True
        unit.waypoint = None
        unit.distance_to_target = None
        unit.state = settings.STATUS_RECARGANDO

    @staticmethod
    def _begin_return(unit: AutonomousUnit) -> None:
        base_x, base_y = settings.BASE_POSITION
        unit.is_returning = True
        unit.waypoint = Waypoint(
            identifier="BASE",
            x=base_x,
            y=base_y,
            altitude=unit.altitude,
            kind="base",
        )
        unit.state = settings.STATUS_REGRESANDO
