from __future__ import annotations

from dataclasses import dataclass, field

from app.config import settings
from app.domain.waypoint import Waypoint


@dataclass
class AutonomousUnit:
    identifier: str
    x: float
    y: float
    altitude: float = settings.DEFAULT_ALTITUDE
    speed: float = settings.DEFAULT_SPEED
    nominal_speed: float = settings.DEFAULT_SPEED
    battery: float = 100.0
    state: str = settings.STATUS_DETENIDO
    role: str = settings.ROLE_NONE
    swarm_id: str = "E1"
    swarm_name: str = "Enjambre 1"
    swarm_role: str = settings.ROLE_NONE
    task_label: str = settings.TASK_AUTOMATIC
    waypoint: Waypoint | None = None
    route: list[Waypoint] = field(default_factory=list)
    current_waypoint_index: int | None = None
    route_loop: bool = False
    route_forward: bool = True
    patrol_points: list[tuple[float, float]] = field(default_factory=list)
    mission_snapshot: dict[str, object] | None = None
    trajectory: list[tuple[float, float]] = field(default_factory=list)
    active_alerts: list[str] = field(default_factory=list)
    distance_to_target: float | None = None
    signal_ok: bool = True
    direction_x: float = 0.0
    direction_y: float = 0.0
    state_before_pause: str | None = None
    is_returning: bool = False
    is_charging: bool = False

    _initial_x: float = field(init=False, repr=False)
    _initial_y: float = field(init=False, repr=False)
    _initial_altitude: float = field(init=False, repr=False)
    _initial_speed: float = field(init=False, repr=False)
    _initial_battery: float = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._initial_x = self.x
        self._initial_y = self.y
        self._initial_altitude = self.altitude
        self._initial_speed = self.speed
        self._initial_battery = self.battery
        if self.nominal_speed <= 0:
            self.nominal_speed = self.speed
        self.trajectory.append((self.x, self.y))

    def append_trajectory(self) -> None:
        point = (self.x, self.y)
        if not self.trajectory or self.trajectory[-1] != point:
            self.trajectory.append(point)
        if len(self.trajectory) > settings.MAX_TRAJECTORY_POINTS:
            self.trajectory = self.trajectory[-settings.MAX_TRAJECTORY_POINTS :]

    def reset(self) -> None:
        self.x = self._initial_x
        self.y = self._initial_y
        self.altitude = self._initial_altitude
        self.speed = self._initial_speed
        self.nominal_speed = self._initial_speed
        self.battery = self._initial_battery
        self.state = settings.STATUS_DETENIDO
        self.role = settings.ROLE_NONE
        self.swarm_id = "E1"
        self.swarm_name = "Enjambre 1"
        self.swarm_role = settings.ROLE_NONE
        self.task_label = settings.TASK_AUTOMATIC
        self.waypoint = None
        self.route = []
        self.current_waypoint_index = None
        self.route_loop = False
        self.route_forward = True
        self.patrol_points = []
        self.mission_snapshot = None
        self.trajectory = [(self.x, self.y)]
        self.active_alerts.clear()
        self.distance_to_target = None
        self.signal_ok = True
        self.direction_x = 0.0
        self.direction_y = 0.0
        self.state_before_pause = None
        self.is_returning = False
        self.is_charging = False
