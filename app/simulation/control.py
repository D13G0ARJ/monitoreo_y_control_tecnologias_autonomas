from __future__ import annotations

from math import hypot

from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit
from app.domain.waypoint import Waypoint


def move_toward_waypoint(
    unit: AutonomousUnit,
    waypoint: Waypoint,
    dt: float,
    max_speed: float,
    tolerance: float,
    kp: float,
) -> bool:
    dx = waypoint.x - unit.x
    dy = waypoint.y - unit.y
    distance = hypot(dx, dy)
    unit.distance_to_target = distance

    if distance <= tolerance:
        unit.x = waypoint.x
        unit.y = waypoint.y
        unit.direction_x = 0.0
        unit.direction_y = 0.0
        unit.distance_to_target = 0.0
        return True

    norm_x = dx / distance
    norm_y = dy / distance
    commanded_speed = min(max_speed, unit.speed, max(settings.MIN_SPEED, kp * distance))

    unit.direction_x = norm_x
    unit.direction_y = norm_y
    unit.x += norm_x * commanded_speed * dt
    unit.y += norm_y * commanded_speed * dt
    unit.distance_to_target = hypot(waypoint.x - unit.x, waypoint.y - unit.y)
    return unit.distance_to_target <= settings.TARGET_TOLERANCE
