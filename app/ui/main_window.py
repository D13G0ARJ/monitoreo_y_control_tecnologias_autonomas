from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMainWindow

from app.config import settings
from app.simulation.simulation_engine import SimulationEngine
from app.ui.radar_view import RadarView


class RadarOperationalWindow(QMainWindow):
    waypoint_requested = Signal(float, float)

    def __init__(self, engine: SimulationEngine) -> None:
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Radar Operativo")
        self.resize(settings.RADAR_WINDOW_WIDTH, settings.RADAR_WINDOW_HEIGHT)
        self.setStyleSheet(settings.GLOBAL_STYLE_SHEET)

        self.radar_view = RadarView()
        self.setCentralWidget(self.radar_view)

        self.radar_view.unit_selected.connect(self.engine.set_selected_unit)
        self.radar_view.waypoint_requested.connect(self.waypoint_requested.emit)
        self.engine.updated.connect(self._refresh_ui)
        self.engine.selection_changed.connect(self._sync_selection)

        QShortcut(QKeySequence("Escape"), self, activated=lambda: self.radar_view.set_waypoint_assignment_enabled(False))

        self.statusBar().showMessage("Radar operativo listo.")
        self._refresh_ui()

    def begin_waypoint_assignment(self) -> None:
        self.radar_view.set_waypoint_assignment_enabled(True)
        self.statusBar().showMessage("Seleccione un punto en el radar para asignar el objetivo.")

    def show_feedback(self, message: str) -> None:
        self.statusBar().showMessage(message)

    def _sync_selection(self, unit_id: str | None) -> None:
        self.radar_view.set_selected_unit(unit_id)
        self._refresh_ui()

    def _refresh_ui(self) -> None:
        units = list(self.engine.units.values())
        scenario_visuals = dict(self.engine.current_scenario_visuals)
        scenario_visuals["name"] = self.engine.current_scenario_name
        scenario_visuals["mode"] = self.engine.mode
        scenario_visuals["units_count"] = len(units)
        scenario_visuals["alerts_count"] = self.engine.active_alert_count
        self.radar_view.refresh(units, self.engine.selected_unit_id, scenario_visuals)
