from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit
from app.domain.waypoint import Waypoint
from app.simulation.control import move_toward_waypoint


def _unit() -> AutonomousUnit:
    return AutonomousUnit(identifier="U01", x=0.0, y=0.0, speed=50.0, nominal_speed=50.0)


def test_reaches_waypoint_within_tolerance():
    unit = _unit()
    wp = Waypoint(identifier="W", x=settings.TARGET_TOLERANCE / 2, y=0.0)
    reached = move_toward_waypoint(unit, wp, dt=0.1, max_speed=80.0,
                                   tolerance=settings.TARGET_TOLERANCE, kp=0.85)
    assert reached is True
    assert unit.distance_to_target == 0.0
    assert (unit.x, unit.y) == (wp.x, wp.y)


def test_moves_toward_far_waypoint_without_reaching():
    unit = _unit()
    wp = Waypoint(identifier="W", x=500.0, y=0.0)
    reached = move_toward_waypoint(unit, wp, dt=0.1, max_speed=80.0,
                                   tolerance=settings.TARGET_TOLERANCE, kp=0.85)
    assert reached is False
    assert unit.x > 0.0
    assert unit.direction_x == 1.0
