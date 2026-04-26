from __future__ import annotations

import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox

from app.config import settings
from app.simulation.simulation_engine import SimulationEngine
from app.ui.control_window import ControlWindow
from app.ui.main_window import RadarOperationalWindow


def main() -> int:
    app = QApplication(sys.argv)
    engine = SimulationEngine()
    radar_window = RadarOperationalWindow(engine)
    control_window = ControlWindow(engine)

    control_window.assign_requested.connect(radar_window.begin_waypoint_assignment)
    radar_window.waypoint_requested.connect(control_window.assign_waypoint_from_radar)
    control_window.statusBar().messageChanged.connect(radar_window.show_feedback)

    screen_geometry = app.primaryScreen().availableGeometry()
    radar_window.setGeometry(
        screen_geometry.x() + 20,
        screen_geometry.y() + 20,
        min(settings.RADAR_WINDOW_WIDTH, screen_geometry.width() - settings.CONTROL_WINDOW_WIDTH - 60),
        min(settings.RADAR_WINDOW_HEIGHT, screen_geometry.height() - 40),
    )
    control_window.setGeometry(
        radar_window.geometry().right() + 20,
        screen_geometry.y() + 20,
        min(settings.CONTROL_WINDOW_WIDTH, max(420, screen_geometry.width() - radar_window.width() - 60)),
        min(settings.CONTROL_WINDOW_HEIGHT, screen_geometry.height() - 40),
    )

    radar_window.show()
    control_window.show()
    return app.exec()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - startup safeguard
        traceback.print_exc()
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "Error de inicio", f"No fue posible iniciar la aplicación:\n{exc}")
        raise
