from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit
from app.services.mode_service import ModeService


def _units(n):
    return [AutonomousUnit(identifier=f"U{i:02d}", x=0.0, y=0.0) for i in range(n)]


def test_defensive_assigns_patrol_loop_route():
    units = _units(4)
    ModeService().apply_mode(settings.MODE_DEFENSIVE, units, zone_radius=320.0)
    for u in units:
        assert u.role == settings.ROLE_PATROL
        assert u.route_loop is True
        assert len(u.route) >= 8
        assert u.waypoint is not None
        assert u.distance_to_target is not None
        assert u.distance_to_target > 0.0


def test_recon_assigns_non_loop_route():
    units = _units(3)
    ModeService().apply_mode(settings.MODE_RECON, units, zone_radius=320.0)
    for u in units:
        assert u.role == settings.ROLE_RECON
        assert u.route_loop is False
        assert len(u.route) == 4


def test_advance_route_loop_wraps():
    svc = ModeService()
    units = _units(2)
    svc.apply_mode(settings.MODE_DEFENSIVE, units, zone_radius=320.0)
    u = units[0]
    u.current_waypoint_index = len(u.route) - 1
    svc.advance_unit_route(u)
    assert u.current_waypoint_index == 0
    assert u.distance_to_target is not None
