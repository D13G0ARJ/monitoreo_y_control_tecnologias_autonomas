from __future__ import annotations

from math import hypot

from app.config import settings
from app.domain.alert import Alert
from app.domain.autonomous_unit import AutonomousUnit


class AlertService:
    def evaluate_unit(
        self,
        unit: AutonomousUnit,
        zone_radius: float,
        low_battery_threshold: float,
    ) -> tuple[list[str], list[Alert]]:
        current_alerts: list[str] = []

        if unit.battery <= 0.0:
            current_alerts.append(settings.ALERT_NO_BATTERY)
        elif unit.battery <= settings.CRITICAL_BATTERY_THRESHOLD:
            current_alerts.append(settings.ALERT_BATTERY_CRITICAL)
        elif unit.battery < low_battery_threshold:
            current_alerts.append(settings.ALERT_BATTERY_LOW)

        if hypot(unit.x, unit.y) > zone_radius:
            current_alerts.append(settings.ALERT_OUT_OF_ZONE)

        if (
            unit.waypoint is not None
            and unit.waypoint.kind in {"objetivo", "manual"}
            and unit.distance_to_target is not None
            and unit.distance_to_target <= settings.TARGET_TOLERANCE
        ):
            current_alerts.append(settings.ALERT_TARGET_REACHED)

        previous = set(unit.active_alerts)
        current = set(current_alerts)

        new_alerts: list[Alert] = []
        for alert_type in current - previous:
            severity = self._resolve_severity(alert_type)
            new_alerts.append(
                Alert(
                    alert_type=alert_type,
                    unit_id=unit.identifier,
                    swarm_id=unit.swarm_id,
                    message=self._build_message(alert_type, unit.identifier),
                    severity=severity,
                    prefix=self._resolve_prefix(severity),
                    key=f"{unit.identifier}:{alert_type}",
                )
            )

        unit.active_alerts = list(current_alerts)
        return current_alerts, new_alerts

    @staticmethod
    def _build_message(alert_type: str, unit_id: str) -> str:
        if alert_type == settings.ALERT_BATTERY_LOW:
            return f"La unidad {unit_id} presenta batería baja."
        if alert_type == settings.ALERT_BATTERY_CRITICAL:
            return f"La unidad {unit_id} presenta nivel crítico de batería."
        if alert_type == settings.ALERT_NO_BATTERY:
            return f"La unidad {unit_id} quedó fuera de operación por falta de batería."
        if alert_type == settings.ALERT_OUT_OF_ZONE:
            return f"La unidad {unit_id} se encuentra fuera de la zona de vigilancia."
        return f"La unidad {unit_id} alcanzó su objetivo asignado."

    @staticmethod
    def _resolve_severity(alert_type: str) -> str:
        if alert_type in {settings.ALERT_BATTERY_CRITICAL, settings.ALERT_NO_BATTERY, settings.ALERT_OUT_OF_ZONE}:
            return settings.SEVERITY_CRIT
        if alert_type == settings.ALERT_BATTERY_LOW:
            return settings.SEVERITY_WARN
        if alert_type == settings.ALERT_PROXIMITY:
            return settings.SEVERITY_WARN
        return settings.SEVERITY_INFO

    @staticmethod
    def _resolve_prefix(severity: str) -> str:
        if severity == settings.SEVERITY_CRIT:
            return "CRIT"
        if severity == settings.SEVERITY_WARN:
            return "WARN"
        return "INFO"
