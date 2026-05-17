from __future__ import annotations

from app.config import settings
from app.domain.alert import Alert
from app.domain.autonomous_unit import AutonomousUnit
from app.services.metrics_service import MetricsService


def test_accumulates_distance_and_samples():
    m = MetricsService()
    u = AutonomousUnit(identifier="U01", x=0.0, y=0.0, battery=100.0)
    m.record_tick(sim_time=0.0, units=[u], dt=0.1)
    u.x, u.y = 3.0, 4.0
    u.speed = 44.0
    u.active_alerts = [settings.ALERT_BATTERY_LOW]
    m.record_tick(sim_time=0.1, units=[u], dt=0.1)
    summary = m.build_summary({"scenario": "X"})
    assert summary["units"]["U01"]["distance"] == 5.0
    assert summary["scenario"]["scenario"] == "X"
    assert summary["units"]["U01"]["battery"]["min"] == 100.0
    assert summary["units"]["U01"]["state_durations"][settings.STATUS_DETENIDO] == 0.2
    assert len(m.timeseries_rows()) == 2
    row = m.timeseries_rows()[-1]
    assert row["speed"] == 44.0
    assert row["active_alerts"] == settings.ALERT_BATTERY_LOW


def test_counts_objective_reached():
    m = MetricsService()
    u = AutonomousUnit(identifier="U01", x=0.0, y=0.0, battery=100.0)
    u.state = settings.STATUS_OBJETIVO_ALCANZADO
    m.record_tick(0.0, [u])
    s = m.build_summary({})
    assert s["units"]["U01"]["objectives_reached"] == 1


def test_counts_alert_events_by_type_and_severity():
    m = MetricsService()
    m.record_alerts([
        Alert(
            alert_type=settings.ALERT_PROXIMITY,
            unit_id="U01/U02",
            swarm_id="E1",
            message="Proximidad",
            severity=settings.SEVERITY_WARN,
            prefix="WARN",
        )
    ])

    summary = m.build_summary({})

    assert summary["alerts"]["by_type"][settings.ALERT_PROXIMITY] == 1
    assert summary["alerts"]["by_severity"][settings.SEVERITY_WARN] == 1
