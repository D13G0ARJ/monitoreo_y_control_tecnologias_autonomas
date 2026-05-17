from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit
from app.services.battery_service import BatteryService


def _unit(battery):
    u = AutonomousUnit(identifier="U01", x=100.0, y=0.0, battery=battery)
    u.task_label = settings.TASK_AUTOMATIC
    return u


def test_triggers_rtb_when_below_threshold():
    svc = BatteryService()
    u = _unit(15.0)
    action = svc.evaluate(u, low_battery_threshold=20.0, dt=0.1)
    assert u.is_returning is True
    assert u.waypoint is not None
    assert (u.waypoint.x, u.waypoint.y) == settings.BASE_POSITION
    assert u.state == settings.STATUS_REGRESANDO
    assert action == "rtb_start"


def test_does_not_rtb_manual_units():
    svc = BatteryService()
    u = _unit(10.0)
    u.task_label = settings.TASK_MANUAL
    action = svc.evaluate(u, low_battery_threshold=20.0, dt=0.1)
    assert u.is_returning is False
    assert action is None


def test_charges_at_base_then_restores():
    svc = BatteryService()
    u = _unit(15.0)
    svc.evaluate(u, 20.0, 0.1)
    u.x, u.y = settings.BASE_POSITION
    svc.notify_base_reached(u)
    assert u.is_charging is True
    assert u.state == settings.STATUS_RECARGANDO
    for _ in range(1000):
        done = svc.evaluate(u, 20.0, 1.0)
        if done == "recharge_done":
            break
    assert u.battery == settings.RECHARGE_FULL
    assert u.is_charging is False
    assert u.is_returning is False
