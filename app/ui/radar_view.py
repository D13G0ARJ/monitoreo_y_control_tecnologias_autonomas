from __future__ import annotations

from math import cos, radians, sin

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QBrush, QPolygonF, QRadialGradient
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsScene, QGraphicsTextItem, QGraphicsView

from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit


class RadarView(QGraphicsView):
    unit_selected = Signal(str)
    waypoint_requested = Signal(float, float)

    def __init__(self) -> None:
        super().__init__()
        scene_size = (settings.RADAR_RADIUS + settings.RADAR_MARGIN) * 2
        self._scene = QGraphicsScene(
            -scene_size / 2,
            -scene_size / 2,
            scene_size,
            scene_size,
            self,
        )
        self.setScene(self._scene)
        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setBackgroundBrush(QColor(settings.COLOR_BACKGROUND))
        self.setFrameShape(QGraphicsView.NoFrame)

        self._selected_unit_id: str | None = None
        self._assigning_waypoint = False
        self._sweep_angle = 0.0
        self._scenario_visuals: dict[str, object] = {}
        self._display_zone_radius = settings.RADAR_RADIUS

        # Incremental redraw state
        self._unit_items: dict[str, dict[str, object]] = {}
        self._dynamic_items: list = []
        self._static_items: list = []
        self._last_scenario_visuals: dict | None = None

        self._sweep_timer = QTimer(self)
        self._sweep_timer.setInterval(settings.RADAR_SWEEP_INTERVAL_MS)
        self._sweep_timer.timeout.connect(self._advance_sweep)
        if settings.RADAR_SWEEP_ENABLED:
            self._sweep_timer.start()

    def set_selected_unit(self, unit_id: str | None) -> None:
        self._selected_unit_id = unit_id

    def set_waypoint_assignment_enabled(self, enabled: bool) -> None:
        self._assigning_waypoint = enabled
        self.setCursor(Qt.CrossCursor if enabled else Qt.ArrowCursor)

    def refresh(
        self,
        units: list[AutonomousUnit],
        selected_unit_id: str | None,
        scenario_visuals: dict[str, object] | None = None,
    ) -> None:
        self._selected_unit_id = selected_unit_id
        self._scenario_visuals = scenario_visuals or {}
        self._display_zone_radius = float(self._scenario_visuals.get("zone_radius", settings.RADAR_RADIUS))

        # HUD counters change every tick, so treat them as dynamic; rebuild HUD each tick.
        # Structural scenario visuals (zone, obs points, legend) are rebuilt only when they change.
        _HUD_KEYS = {"alerts_count", "units_count", "mode", "name"}
        static_snapshot = {k: v for k, v in self._scenario_visuals.items() if k not in _HUD_KEYS}
        last_static = (
            {k: v for k, v in self._last_scenario_visuals.items() if k not in _HUD_KEYS}
            if self._last_scenario_visuals is not None
            else None
        )
        if static_snapshot != last_static:
            self._remove_items(self._static_items)
            self._static_items = []
            self._draw_scenario_visuals()
        self._last_scenario_visuals = dict(self._scenario_visuals)

        # Remove all dynamic items (routes, trajectories, waypoints, HUD) from previous tick
        self._remove_items(self._dynamic_items)
        self._dynamic_items = []
        # HUD changes every tick (alerts_count, units_count, mode) — always rebuild as dynamic
        self._draw_hud()

        # Draw dynamic per-unit elements and sync persistent unit items
        for unit in units:
            self._draw_route(unit)
            self._draw_trajectory(unit)
            if unit.waypoint is not None:
                self._draw_waypoint(unit)
            self._sync_unit_item(unit)

        # Remove items for units that are no longer present
        present = {unit.identifier for unit in units}
        for uid in list(self._unit_items):
            if uid not in present:
                stored = self._unit_items.pop(uid)
                self._remove_items(list(stored.values()))

    def _remove_items(self, items: list) -> None:
        for item in items:
            if item.scene() is self._scene:
                self._scene.removeItem(item)

    def _add_overlay_rect(self, x: float, y: float, width: float, height: float, radius: float):
        bg_color = QColor(settings.COLOR_PANEL_ALT)
        bg_color.setAlpha(210)
        border_color = QColor(settings.COLOR_BORDER)
        border_color.setAlpha(155)
        path = QPainterPath()
        path.addRoundedRect(QRectF(x, y, width, height), radius, radius)
        item = QGraphicsPathItem(path)
        item.setPen(QPen(border_color))
        item.setBrush(QBrush(bg_color))
        item.setZValue(19)
        self._scene.addItem(item)
        return item

    def _sync_unit_item(self, unit: AutonomousUnit) -> None:
        radius = settings.RADAR_UNIT_RADIUS
        selected = unit.identifier == self._selected_unit_id
        brush_color = self._resolve_unit_color(unit)

        if unit.identifier not in self._unit_items:
            # Create all items for this unit
            pen = QPen(QColor(settings.COLOR_SELECTED if selected else brush_color))
            pen.setWidth(2 if selected else 1)
            body = self._scene.addEllipse(
                unit.x - radius, unit.y - radius, radius * 2, radius * 2,
                pen, QBrush(QColor(brush_color)),
            )
            body.setData(0, unit.identifier)
            body.setZValue(10)

            ring_pen = QPen(QColor(settings.COLOR_SELECTED))
            ring_pen.setWidth(2)
            ring = self._scene.addEllipse(
                unit.x - settings.RADAR_SELECTED_RING_RADIUS,
                unit.y - settings.RADAR_SELECTED_RING_RADIUS,
                settings.RADAR_SELECTED_RING_RADIUS * 2,
                settings.RADAR_SELECTED_RING_RADIUS * 2,
                ring_pen,
            )
            ring.setZValue(9)
            ring.setVisible(selected)

            label = QGraphicsTextItem(self._unit_label_text(unit, selected))
            label.setDefaultTextColor(QColor(settings.COLOR_SELECTED if selected else settings.COLOR_MUTED))
            label.setOpacity(1.0 if selected else 0.82)
            label.setScale(1.08 if selected else 0.92)
            label.setPos(unit.x + 12, unit.y - 28)
            label.setData(0, unit.identifier)
            label.setZValue(11)
            self._scene.addItem(label)

            self._unit_items[unit.identifier] = {"body": body, "label": label, "ring": ring}
        else:
            # Update existing items in place
            stored = self._unit_items[unit.identifier]
            body = stored["body"]
            label = stored["label"]
            ring = stored["ring"]

            body.setRect(unit.x - radius, unit.y - radius, radius * 2, radius * 2)
            pen = QPen(QColor(settings.COLOR_SELECTED if selected else brush_color))
            pen.setWidth(2 if selected else 1)
            body.setPen(pen)
            body.setBrush(QBrush(QColor(brush_color)))

            ring.setRect(
                unit.x - settings.RADAR_SELECTED_RING_RADIUS,
                unit.y - settings.RADAR_SELECTED_RING_RADIUS,
                settings.RADAR_SELECTED_RING_RADIUS * 2,
                settings.RADAR_SELECTED_RING_RADIUS * 2,
            )
            ring.setVisible(selected)

            label.setPlainText(self._unit_label_text(unit, selected))
            label.setDefaultTextColor(QColor(settings.COLOR_SELECTED if selected else settings.COLOR_MUTED))
            label.setOpacity(1.0 if selected else 0.82)
            label.setScale(1.08 if selected else 0.92)
            label.setPos(unit.x + 12, unit.y - 28)

    def drawBackground(self, painter: QPainter, rect) -> None:  # type: ignore[override]
        painter.fillRect(rect, QColor(settings.COLOR_BACKGROUND))
        painter.setRenderHint(QPainter.Antialiasing, True)

        center = QPointF(0.0, 0.0)
        gradient = QRadialGradient(center, self._display_zone_radius + 120)
        gradient.setColorAt(0.0, QColor("#0d252a"))
        gradient.setColorAt(0.62, QColor(settings.COLOR_BACKGROUND))
        gradient.setColorAt(1.0, QColor("#030b0d"))
        painter.fillRect(rect, QBrush(gradient))

        grid_pen = QPen(QColor(settings.COLOR_GRID))
        grid_pen.setWidth(1)

        for ring_index in range(1, settings.RADAR_CONCENTRIC_RINGS + 1):
            radius = (self._display_zone_radius / settings.RADAR_CONCENTRIC_RINGS) * ring_index
            grid_color = QColor(settings.COLOR_GRID)
            grid_color.setAlpha(88 if ring_index < settings.RADAR_CONCENTRIC_RINGS else 132)
            grid_pen.setColor(grid_color)
            painter.setPen(grid_pen)
            painter.drawEllipse(center, radius, radius)

        axis_color = QColor(settings.COLOR_GRID)
        axis_color.setAlpha(118)
        grid_pen.setColor(axis_color)
        painter.setPen(grid_pen)
        painter.drawLine(-self._display_zone_radius, 0, self._display_zone_radius, 0)
        painter.drawLine(0, -self._display_zone_radius, 0, self._display_zone_radius)

        glow_color = QColor(settings.COLOR_SWEEP_GLOW)
        glow_color.setAlpha(70)
        glow_pen = QPen(glow_color)
        glow_pen.setWidth(6)
        painter.setPen(glow_pen)
        painter.drawEllipse(center, self._display_zone_radius, self._display_zone_radius)

        zone_pen = QPen(QColor(settings.COLOR_ZONE))
        zone_pen.setWidth(2)
        painter.setPen(zone_pen)
        painter.drawEllipse(center, self._display_zone_radius, self._display_zone_radius)

    def drawForeground(self, painter: QPainter, rect) -> None:  # type: ignore[override]
        if not settings.RADAR_SWEEP_ENABLED:
            return

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        current_angle = radians(self._sweep_angle)
        tail_angle = radians(self._sweep_angle - settings.RADAR_SWEEP_WIDTH_DEGREES)

        end_x = self._display_zone_radius * cos(current_angle)
        end_y = self._display_zone_radius * sin(current_angle)
        tail_x = self._display_zone_radius * cos(tail_angle)
        tail_y = self._display_zone_radius * sin(tail_angle)

        sweep_polygon = QPolygonF(
            [
                QPointF(0.0, 0.0),
                QPointF(tail_x, tail_y),
                QPointF(end_x, end_y),
            ]
        )
        sweep_glow = QColor(settings.COLOR_SWEEP_GLOW)
        sweep_glow.setAlpha(45)
        painter.setPen(Qt.NoPen)
        painter.setBrush(sweep_glow)
        painter.drawPolygon(sweep_polygon)

        pen = QPen(QColor(settings.COLOR_SWEEP))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(QPointF(0.0, 0.0), QPointF(end_x, end_y))
        painter.restore()

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        scene_pos = self.mapToScene(event.position().toPoint())

        if self._assigning_waypoint and self._selected_unit_id is not None:
            self._assigning_waypoint = False
            self.setCursor(Qt.ArrowCursor)
            self.waypoint_requested.emit(scene_pos.x(), scene_pos.y())
            event.accept()
            return

        item = self.itemAt(event.position().toPoint())
        if item is not None:
            unit_id = item.data(0)
            if unit_id:
                self.unit_selected.emit(str(unit_id))
                event.accept()
                return

        super().mousePressEvent(event)

    def _draw_waypoint(self, unit: AutonomousUnit) -> None:
        waypoint = unit.waypoint
        if waypoint is None:
            return

        color = self._resolve_role_color(unit)
        pen = QPen(QColor(color))
        pen.setWidth(2)
        size = 7.0
        link_pen = QPen(QColor(color))
        link_pen.setStyle(Qt.DashLine)
        link_pen.setWidth(1)
        link_pen.setColor(QColor(color))
        link_item = self._scene.addLine(unit.x, unit.y, waypoint.x, waypoint.y, link_pen)
        cross_h = self._scene.addLine(waypoint.x - size, waypoint.y, waypoint.x + size, waypoint.y, pen)
        cross_v = self._scene.addLine(waypoint.x, waypoint.y - size, waypoint.x, waypoint.y + size, pen)

        label = QGraphicsTextItem(waypoint.identifier)
        label.setDefaultTextColor(QColor(color))
        label.setPos(waypoint.x + 8, waypoint.y + 4)
        label.setZValue(5)
        self._scene.addItem(label)

        self._dynamic_items.extend([link_item, cross_h, cross_v, label])

    def _draw_scenario_visuals(self) -> None:
        if not self._scenario_visuals:
            return

        protected_radius = float(self._scenario_visuals.get("protected_radius", 0.0))
        if protected_radius > 0:
            protected_pen = QPen(QColor(settings.COLOR_ZONE_PROTECTED))
            protected_pen.setWidth(2)
            protected_pen.setStyle(Qt.DashLine)
            zone_item = self._scene.addEllipse(
                -protected_radius,
                -protected_radius,
                protected_radius * 2,
                protected_radius * 2,
                protected_pen,
            )
            zone_item.setZValue(-1)
            self._static_items.append(zone_item)

            protected_label = QGraphicsTextItem("Zona estratégica")
            protected_label.setDefaultTextColor(QColor(settings.COLOR_ZONE_PROTECTED))
            protected_label.setOpacity(0.82)
            protected_label.setPos(-56, protected_radius + 8)
            protected_label.setZValue(3)
            self._scene.addItem(protected_label)
            self._static_items.append(protected_label)

        for index, point in enumerate(self._scenario_visuals.get("observation_points", []), start=1):
            x, y = point
            pen = QPen(QColor(settings.COLOR_OBSERVATION))
            pen.setWidth(2)
            brush = QBrush(QColor(settings.COLOR_OBSERVATION))
            item = self._scene.addEllipse(x - 4.5, y - 4.5, 9.0, 9.0, pen, brush)
            item.setZValue(2)
            self._static_items.append(item)
            label = QGraphicsTextItem(f"Obs {index}")
            label.setDefaultTextColor(QColor(settings.COLOR_OBSERVATION))
            label.setPos(x + 7, y - 16)
            label.setZValue(3)
            self._scene.addItem(label)
            self._static_items.append(label)

        self._draw_compact_legend()

    def _draw_route(self, unit: AutonomousUnit) -> None:
        if not unit.route or unit.current_waypoint_index is None:
            return

        current_index = unit.current_waypoint_index
        active_points = [unit.route[current_index]]
        if len(unit.route) > 1:
            next_index = (current_index + 1) % len(unit.route) if unit.route_loop else min(current_index + 1, len(unit.route) - 1)
            if next_index != current_index:
                active_points.append(unit.route[next_index])

        path = QPainterPath(QPointF(unit.x, unit.y))
        for waypoint in active_points:
            path.lineTo(waypoint.x, waypoint.y)

        route_item = QGraphicsPathItem(path)
        route_pen = QPen(QColor(self._resolve_role_color(unit)))
        route_pen.setStyle(Qt.DotLine if unit.role != settings.ROLE_PATROL else Qt.DashLine)
        route_pen.setWidth(1)
        route_item.setPen(route_pen)
        route_item.setOpacity(0.28 if unit.identifier != self._selected_unit_id else 0.45)
        route_item.setZValue(0)
        self._scene.addItem(route_item)
        self._dynamic_items.append(route_item)

        for index, waypoint in enumerate(active_points):
            point_radius = 4.0 if index == 0 else 2.8
            point_item = self._scene.addEllipse(
                waypoint.x - point_radius,
                waypoint.y - point_radius,
                point_radius * 2,
                point_radius * 2,
                QPen(QColor(self._resolve_role_color(unit))),
                QBrush(QColor(self._resolve_role_color(unit))),
            )
            point_item.setOpacity(0.85 if index == 0 else 0.45)
            point_item.setZValue(2)
            self._dynamic_items.append(point_item)

    def _draw_trajectory(self, unit: AutonomousUnit) -> None:
        if len(unit.trajectory) < 2:
            return

        path = QPainterPath(QPointF(*unit.trajectory[0]))
        for x, y in unit.trajectory[1:]:
            path.lineTo(x, y)

        trajectory_item = QGraphicsPathItem(path)
        pen = QPen(QColor(self._resolve_role_color(unit)))
        pen.setWidth(2 if unit.identifier == self._selected_unit_id else 1)
        trajectory_item.setPen(pen)
        trajectory_item.setOpacity(0.38 if unit.identifier != self._selected_unit_id else 0.62)
        trajectory_item.setZValue(1)
        self._scene.addItem(trajectory_item)
        self._dynamic_items.append(trajectory_item)

    @staticmethod
    def _resolve_unit_color(unit: AutonomousUnit) -> str:
        if unit.state == settings.STATUS_SIN_BATERIA:
            return settings.COLOR_STATUS_OFFLINE
        if unit.state == settings.STATUS_CRITICO:
            return settings.COLOR_STATUS_CRITICAL
        if unit.state == settings.STATUS_BATERIA_BAJA:
            return settings.COLOR_STATUS_ROUTE
        if unit.state == settings.STATUS_FUERA_DE_ZONA:
            return settings.COLOR_STATUS_ALERT
        if unit.state == settings.STATUS_REGRESANDO:
            return settings.COLOR_STATUS_RTB
        if unit.state == settings.STATUS_RECARGANDO:
            return settings.COLOR_STATUS_CHARGING
        if unit.state == settings.STATUS_DETENIDO:
            return settings.COLOR_UNIT_IDLE
        if unit.role == settings.ROLE_RECON:
            return settings.COLOR_ROLE_RECON
        if unit.role == settings.ROLE_PATROL:
            return settings.COLOR_ROLE_PATROL
        if unit.state == settings.STATUS_EN_RUTA:
            return settings.COLOR_WARNING
        return settings.COLOR_STATUS_ACTIVE

    @staticmethod
    def _resolve_role_color(unit: AutonomousUnit) -> str:
        if unit.role == settings.ROLE_PATROL:
            return settings.COLOR_ROUTE_PATROL
        if unit.role == settings.ROLE_RECON:
            return settings.COLOR_ROLE_RECON
        if unit.role == settings.ROLE_MANUAL:
            return settings.COLOR_WAYPOINT
        return settings.COLOR_TRAJECTORY

    @staticmethod
    def _role_suffix(unit: AutonomousUnit) -> str:
        swarm_tag = unit.swarm_id or "E1"
        if unit.task_label == settings.TASK_TEMPORARY:
            return f"[{swarm_tag}-T]"
        if unit.role == settings.ROLE_PATROL:
            return f"[{swarm_tag}-P]"
        if unit.role == settings.ROLE_RECON:
            return f"[{swarm_tag}-R]"
        if unit.role == settings.ROLE_MANUAL:
            return f"[{swarm_tag}-M]"
        return ""

    def _unit_label_text(self, unit: AutonomousUnit, selected: bool) -> str:
        if selected:
            return f"{unit.identifier} {self._role_suffix(unit)}"
        return unit.identifier

    def _advance_sweep(self) -> None:
        self._sweep_angle = (self._sweep_angle + settings.RADAR_SWEEP_STEP_DEGREES) % 360.0
        self.viewport().update()

    def _draw_compact_legend(self) -> None:
        legend_items = [
            ("Patrulla", settings.COLOR_ROLE_PATROL),
            ("Reconocimiento", settings.COLOR_ROLE_RECON),
            ("Manual", settings.COLOR_WAYPOINT),
        ]
        origin_x = self._display_zone_radius - 135
        origin_y = self._display_zone_radius - 72
        background = self._add_overlay_rect(
            origin_x - 12,
            origin_y - 12,
            132,
            70,
            8,
        )
        self._static_items.append(background)

        for index, (label, color) in enumerate(legend_items):
            y = origin_y + (index * 18)
            marker = self._scene.addEllipse(origin_x, y, 8, 8, QPen(QColor(color)), QBrush(QColor(color)))
            marker.setZValue(20)
            self._static_items.append(marker)
            text = QGraphicsTextItem(label)
            text.setDefaultTextColor(QColor(settings.COLOR_TEXT))
            text.setPos(origin_x + 14, y - 6)
            text.setZValue(20)
            self._scene.addItem(text)
            self._static_items.append(text)

    def _draw_hud(self) -> None:
        hud_items = [
            str(self._scenario_visuals.get("name", "")),
            f"Modo: {self._scenario_visuals.get('mode', '--')}",
            f"Unidades: {self._scenario_visuals.get('units_count', '--')}",
            f"Alertas: {self._scenario_visuals.get('alerts_count', '--')}",
        ]
        origin_x = -self._display_zone_radius + 12
        origin_y = -self._display_zone_radius + 8
        background = self._add_overlay_rect(
            origin_x - 12,
            origin_y - 8,
            225,
            86,
            9,
        )
        self._dynamic_items.append(background)

        for index, text_value in enumerate(hud_items):
            label = QGraphicsTextItem(text_value)
            label.setDefaultTextColor(QColor(settings.COLOR_TEXT if index == 0 else settings.COLOR_MUTED))
            label.setScale(1.02 if index == 0 else 0.94)
            label.setPos(origin_x, origin_y + (index * 19))
            label.setZValue(20)
            self._scene.addItem(label)
            self._dynamic_items.append(label)
