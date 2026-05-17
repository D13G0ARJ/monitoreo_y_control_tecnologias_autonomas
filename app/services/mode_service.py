from __future__ import annotations

from math import cos, pi, sin

from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit
from app.domain.waypoint import Waypoint


class ModeService:
    def apply_mode(self, mode: str, units: list[AutonomousUnit], zone_radius: float) -> None:
        automatic_units = [unit for unit in units if unit.task_label != settings.TASK_MANUAL]
        if not automatic_units:
            return

        if mode == settings.MODE_DEFENSIVE:
            for unit in automatic_units:
                unit.swarm_role = settings.ROLE_PATROL
            self._assign_defensive_patrol(automatic_units, zone_radius)
        elif mode == settings.MODE_RECON:
            for unit in automatic_units:
                unit.swarm_role = settings.ROLE_RECON
            self._assign_recon_points(automatic_units, zone_radius)
        elif mode == settings.MODE_MIXED:
            patrol_units = [unit for unit in automatic_units if unit.swarm_role == settings.ROLE_PATROL]
            recon_units = [unit for unit in automatic_units if unit.swarm_role == settings.ROLE_RECON]

            if not patrol_units and not recon_units:
                split_index = max(1, len(automatic_units) // 2)
                patrol_units = automatic_units[:split_index]
                recon_units = automatic_units[split_index:]

            if patrol_units:
                self._assign_defensive_patrol(patrol_units, zone_radius)
            if recon_units:
                self._assign_recon_points(recon_units, zone_radius)

    def _assign_defensive_patrol(self, units: list[AutonomousUnit], zone_radius: float) -> None:
        orbit_radius = zone_radius * settings.PATROL_ORBIT_FACTOR
        route_points = max(8, len(units) * 2)
        patrol_route = [
            Waypoint(
                identifier=f"PAT-{index + 1:02d}",
                x=orbit_radius * cos((2 * pi * index) / route_points),
                y=orbit_radius * sin((2 * pi * index) / route_points),
                kind="patrullaje",
            )
            for index in range(route_points)
        ]
        total = len(units)

        for index, unit in enumerate(units):
            start_index = (index * route_points) // max(1, total)
            self._assign_route(
                unit=unit,
                role=settings.ROLE_PATROL,
                state=settings.STATUS_PATRULLANDO,
                route=[
                    Waypoint(
                        identifier=f"{point.identifier}-{unit.identifier}",
                        x=point.x,
                        y=point.y,
                        altitude=unit.altitude,
                        kind="patrullaje",
                    )
                    for point in patrol_route
                ],
                start_index=(start_index + 1) % route_points,
                route_loop=True,
                patrol_points=[(point.x, point.y) for point in patrol_route],
            )

    def _assign_recon_points(self, units: list[AutonomousUnit], zone_radius: float) -> None:
        total = len(units)
        if total == 0:
            return

        for index, unit in enumerate(units):
            route = self._build_recon_route(index, total, zone_radius, unit.altitude, unit.identifier)
            self._assign_route(
                unit=unit,
                role=settings.ROLE_RECON,
                state=settings.STATUS_RECONOCIMIENTO,
                route=route,
                start_index=0,
                route_loop=False,
                patrol_points=[],
            )

    def advance_unit_route(self, unit: AutonomousUnit) -> None:
        if not unit.route:
            return

        if unit.current_waypoint_index is None:
            unit.current_waypoint_index = 0
        elif unit.route_loop:
            unit.current_waypoint_index = (unit.current_waypoint_index + 1) % len(unit.route)
        elif unit.route_forward:
            if unit.current_waypoint_index < len(unit.route) - 1:
                unit.current_waypoint_index += 1
            else:
                unit.route_forward = False
                unit.current_waypoint_index = max(len(unit.route) - 2, 0)
        else:
            if unit.current_waypoint_index > 0:
                unit.current_waypoint_index -= 1
            else:
                unit.route_forward = True
                unit.current_waypoint_index = 1 if len(unit.route) > 1 else 0

        unit.waypoint = unit.route[unit.current_waypoint_index]
        unit.distance_to_target = None

    def _assign_route(
        self,
        unit: AutonomousUnit,
        role: str,
        state: str,
        route: list[Waypoint],
        start_index: int,
        route_loop: bool,
        patrol_points: list[tuple[float, float]],
    ) -> None:
        unit.role = role
        unit.route = route
        unit.route_loop = route_loop
        unit.route_forward = True
        unit.patrol_points = patrol_points
        unit.mission_snapshot = None
        unit.task_label = settings.TASK_AUTOMATIC
        unit.current_waypoint_index = start_index if route else None
        unit.waypoint = route[start_index] if route else None
        unit.state = state
        unit.distance_to_target = None

    def _build_recon_route(
        self,
        index: int,
        total_units: int,
        zone_radius: float,
        altitude: float,
        unit_id: str,
    ) -> list[Waypoint]:
        left_x = -(zone_radius * settings.RECON_X_FACTOR)
        right_x = zone_radius * settings.RECON_X_FACTOR
        top_y = -(zone_radius * settings.RECON_TOP_FACTOR)
        bottom_y = zone_radius * settings.RECON_BOTTOM_FACTOR
        lanes = max(3, total_units)
        lane_spacing = (bottom_y - top_y) / max(1, lanes)
        start_y = top_y + (index * lane_spacing)
        step_y = zone_radius * settings.RECON_STEP_FACTOR
        direction_left = index % 2 == 0

        route: list[Waypoint] = []
        for point_index in range(4):
            x = left_x if direction_left else right_x
            y = min(bottom_y, start_y + (point_index * step_y))
            route.append(
                Waypoint(
                    identifier=f"REC-{unit_id}-{point_index + 1:02d}",
                    x=x,
                    y=y,
                    altitude=altitude,
                    kind="reconocimiento",
                )
            )
            direction_left = not direction_left

        return route
