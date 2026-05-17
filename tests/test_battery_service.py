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


def test_engine_full_rtb_cycle_restores_mission():
    from app.simulation.simulation_engine import SimulationEngine

    engine = SimulationEngine()
    unit = engine.create_unit()
    engine.set_mode(settings.MODE_DEFENSIVE)  # gives it an automatic patrol mission
    assert unit.route, "unit should have a patrol route before RTB"
    unit.battery = 12.0
    engine.start()
    saw_returning = False
    saw_charging = False
    cycle_complete = False
    for _ in range(4000):
        was_charging = unit.is_charging
        engine.update_simulation()
        saw_returning = saw_returning or unit.is_returning
        saw_charging = saw_charging or unit.is_charging
        # detect the tick on which charging completed: was_charging but now is not
        if was_charging and not unit.is_charging and not unit.is_returning:
            cycle_complete = True
            break
    assert saw_returning, "unit should have entered RTB"
    assert saw_charging, "unit should have entered charging state"
    assert cycle_complete, "recharge cycle should have completed within 4000 ticks"
    assert unit.is_returning is False
    assert unit.is_charging is False
    # battery was set to RECHARGE_FULL inside evaluate, then may drain one tick — still very high
    assert unit.battery > settings.RECHARGE_FULL * 0.95, f"expected near-full battery after recharge, got {unit.battery}"
    assert unit.route, "patrol mission should be restored after recharge"


def test_returning_unit_keeps_nominal_speed_even_when_battery_is_critical():
    from app.simulation.simulation_engine import SimulationEngine

    engine = SimulationEngine()
    unit = engine.create_unit()
    unit.battery = settings.CRITICAL_BATTERY_THRESHOLD
    unit.is_returning = True
    unit.nominal_speed = 60.0
    unit.speed = 1.0

    engine._apply_battery_speed_policy(unit)

    assert unit.speed == 60.0
