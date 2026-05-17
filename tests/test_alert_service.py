from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit
from app.services.alert_service import AlertService


def test_low_battery_emits_warn_once():
    svc = AlertService()
    unit = AutonomousUnit(identifier="U01", x=0.0, y=0.0, battery=10.0)
    _, new = svc.evaluate_unit(unit, zone_radius=320.0, low_battery_threshold=20.0)
    assert any(a.alert_type == settings.ALERT_BATTERY_LOW for a in new)
    _, again = svc.evaluate_unit(unit, zone_radius=320.0, low_battery_threshold=20.0)
    assert again == []


def test_out_of_zone_is_critical():
    svc = AlertService()
    unit = AutonomousUnit(identifier="U01", x=999.0, y=0.0, battery=100.0)
    _, new = svc.evaluate_unit(unit, zone_radius=320.0, low_battery_threshold=20.0)
    assert any(a.severity == settings.SEVERITY_CRIT for a in new)
