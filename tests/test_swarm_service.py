from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit
from app.services.swarm_service import SwarmService


def _units(n):
    return [AutonomousUnit(identifier=f"U{i:02d}", x=0.0, y=0.0) for i in range(n)]


def test_combined_splits_two_swarms():
    units = _units(6)
    SwarmService().assign_swarms(units, settings.SCENARIO_COMBINED, swarm_count=2,
                                 distribution="Mitad y mitad")
    ids = {u.swarm_id for u in units}
    assert ids == {"E1", "E2"}


def test_zone_protection_single_swarm_patrol():
    units = _units(5)
    SwarmService().assign_swarms(units, settings.SCENARIO_ZONE_PROTECTION, swarm_count=1,
                                 distribution="Automática")
    assert all(u.swarm_id == "E1" and u.swarm_role == settings.ROLE_PATROL for u in units)
