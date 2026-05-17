from __future__ import annotations

import argparse
import sys
import traceback


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Simulador Radar UNEFA")
    p.add_argument("--headless", action="store_true")
    p.add_argument("--scenario", default="Protección de zona estratégica")
    p.add_argument("--duration", type=float, default=120.0)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--time-scale", type=int, default=1)
    p.add_argument("--out", default="run_output")
    return p.parse_args(argv)


def _run_headless(args: argparse.Namespace) -> int:
    from app.runtime.headless import run_headless
    paths = run_headless(args.scenario, args.duration, args.out,
                         seed=args.seed, time_scale=args.time_scale)
    print(f"Informe exportado: {paths['timeseries']}, {paths['summary']}")
    return 0


def _run_gui() -> int:
    from PySide6.QtWidgets import QApplication
    from app.config import settings
    from app.simulation.simulation_engine import SimulationEngine
    from app.ui.control_window import ControlWindow
    from app.ui.main_window import RadarOperationalWindow

    app = QApplication(sys.argv)
    engine = SimulationEngine()
    radar_window = RadarOperationalWindow(engine)
    control_window = ControlWindow(engine)

    control_window.assign_requested.connect(radar_window.begin_waypoint_assignment)
    radar_window.waypoint_requested.connect(control_window.assign_waypoint_from_radar)
    control_window.statusBar().messageChanged.connect(radar_window.show_feedback)

    screen_geometry = app.primaryScreen().availableGeometry()
    radar_window.setGeometry(
        screen_geometry.x() + 20, screen_geometry.y() + 20,
        min(settings.RADAR_WINDOW_WIDTH, screen_geometry.width() - settings.CONTROL_WINDOW_WIDTH - 60),
        min(settings.RADAR_WINDOW_HEIGHT, screen_geometry.height() - 40))
    control_window.setGeometry(
        radar_window.geometry().right() + 20, screen_geometry.y() + 20,
        min(settings.CONTROL_WINDOW_WIDTH, max(420, screen_geometry.width() - radar_window.width() - 60)),
        min(settings.CONTROL_WINDOW_HEIGHT, screen_geometry.height() - 40))

    radar_window.show()
    control_window.show()
    return app.exec()


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    if args.headless:
        return _run_headless(args)
    return _run_gui()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover - startup safeguard
        traceback.print_exc()
        from PySide6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "Error de inicio", f"No fue posible iniciar la aplicación:\n{exc}")
        raise
