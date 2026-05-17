from __future__ import annotations

from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit
from app.services.metrics_service import MetricsService


def test_accumulates_distance_and_samples():
    m = MetricsService()
    u = AutonomousUnit(identifier="U01", x=0.0, y=0.0, battery=100.0)
    m.record_tick(sim_time=0.0, units=[u])
    u.x, u.y = 3.0, 4.0
    m.record_tick(sim_time=0.1, units=[u])
    summary = m.build_summary({"scenario": "X"})
    assert summary["units"]["U01"]["distance"] == 5.0
    assert summary["scenario"]["scenario"] == "X"
    assert len(m.timeseries_rows()) == 2


def test_counts_objective_reached():
    m = MetricsService()
    u = AutonomousUnit(identifier="U01", x=0.0, y=0.0, battery=100.0)
    u.state = settings.STATUS_OBJETIVO_ALCANZADO
    m.record_tick(0.0, [u])
    s = m.build_summary({})
    assert s["units"]["U01"]["objectives_reached"] == 1
