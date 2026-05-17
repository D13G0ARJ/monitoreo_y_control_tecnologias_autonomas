from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QApplication, QMainWindow

from app.config import settings
from app.domain.alert import Alert
from app.simulation.simulation_engine import SimulationEngine
from app.ui.panels import ControlTabsWidget
from app.ui.scenario_dialog import ScenarioConfigDialog


class ControlWindow(QMainWindow):
    assign_requested = Signal()

    def __init__(self, engine: SimulationEngine) -> None:
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Centro de Control")
        self.resize(settings.CONTROL_WINDOW_WIDTH, settings.CONTROL_WINDOW_HEIGHT)
        self.setStyleSheet(settings.GLOBAL_STYLE_SHEET)

        self.panels = ControlTabsWidget()
        self.setCentralWidget(self.panels)

        self._connect_signals()
        self._sync_parameters_from_engine()
        self._refresh_ui()
        self.statusBar().showMessage("Centro de control listo.")

        from PySide6.QtGui import QKeySequence, QShortcut
        QShortcut(QKeySequence("Space"), self, activated=self._toggle_run)
        QShortcut(QKeySequence("R"), self, activated=self._reset_simulation)
        QShortcut(QKeySequence("A"), self, activated=self._request_assign_mode)

    def _connect_signals(self) -> None:
        controls = self.panels.controls
        controls.create_button.clicked.connect(self._create_unit)
        controls.assign_button.clicked.connect(self._request_assign_mode)
        controls.start_button.clicked.connect(self._start_simulation)
        controls.pause_button.clicked.connect(self._pause_simulation)
        controls.reset_button.clicked.connect(self._reset_simulation)
        controls.mode_selector.currentTextChanged.connect(self._change_mode)

        scenario_panel = self.panels.scenario
        scenario_panel.scenario_selector.activated.connect(self._handle_scenario_selection)

        params = self.panels.parameters
        params.max_speed_spin.valueChanged.connect(self.engine.update_max_speed)
        params.altitude_spin.valueChanged.connect(self.engine.update_target_altitude)
        params.separation_spin.valueChanged.connect(self.engine.update_min_separation)
        params.zone_radius_spin.valueChanged.connect(self.engine.update_zone_radius)
        params.low_battery_spin.valueChanged.connect(self.engine.update_low_battery_threshold)
        params.active_units_spin.valueChanged.connect(self.engine.update_active_unit_target)
        params.time_scale_combo.currentTextChanged.connect(
            lambda text: self.engine.set_time_scale(int(text.rstrip("x")))
        )

        self.panels.alerts.clear_button.clicked.connect(self.engine.clear_alert_history)
        controls.export_button.clicked.connect(self._export_report)
        self.panels.unit_list_panel.unit_list.itemClicked.connect(
            lambda item: self.engine.set_selected_unit(item.data(Qt.UserRole))
        )

        self.engine.updated.connect(self._refresh_ui)
        self.engine.selection_changed.connect(self._handle_selection_change)
        self.engine.alerts_updated.connect(self._handle_alerts_updated)

    def assign_waypoint_from_radar(self, x: float, y: float) -> None:
        if self.engine.selected_unit_id is None:
            self.statusBar().showMessage("Seleccione una unidad antes de asignar un objetivo.")
            return

        temporary = self.panels.scenario.assignment_mode_selector.currentText() == settings.TASK_TEMPORARY
        self.engine.set_waypoint_for_unit(self.engine.selected_unit_id, x, y, temporary=temporary)
        action = "tarea temporal" if temporary else "control manual"
        self.statusBar().showMessage(
            f"Objetivo asignado a {self.engine.selected_unit_id} en ({x:0.1f}, {y:0.1f}) como {action}."
        )

    def _create_unit(self) -> None:
        unit = self.engine.create_unit()
        self.engine.set_selected_unit(unit.identifier)
        self.panels.parameters.active_units_spin.blockSignals(True)
        self.panels.parameters.active_units_spin.setValue(len(self.engine.units))
        self.panels.parameters.active_units_spin.blockSignals(False)
        self.statusBar().showMessage(f"Unidad {unit.identifier} creada.")

    def _request_assign_mode(self) -> None:
        if self.engine.selected_unit_id is None:
            self.statusBar().showMessage("Seleccione una unidad antes de asignar un objetivo.")
            return
        self.assign_requested.emit()
        mode_label = self.panels.scenario.assignment_mode_selector.currentText()
        self.statusBar().showMessage(f"Asignación preparada en modo: {mode_label}.")

    def _start_simulation(self) -> None:
        if self.engine.is_running:
            self.statusBar().showMessage("La simulación ya se encuentra en ejecución.")
            return
        self.engine.start()
        self.statusBar().showMessage("Simulación iniciada.")

    def _pause_simulation(self) -> None:
        if not self.engine.is_running:
            self.statusBar().showMessage("La simulación ya se encuentra en pausa.")
            return
        self.engine.pause()
        self.statusBar().showMessage("Simulación en pausa.")

    def _reset_simulation(self) -> None:
        self.engine.reset()
        self.statusBar().showMessage("Simulación reiniciada.")

    def _toggle_run(self) -> None:
        if self.engine.is_running:
            self._pause_simulation()
        else:
            self._start_simulation()

    def _change_mode(self, mode: str) -> None:
        if not self.engine.units:
            self._sync_mode_selector()
            self.statusBar().showMessage("No hay unidades activas. Cree unidades o cargue un escenario.")
            return
        self.engine.set_mode(mode)
        self.statusBar().showMessage(f"Modo operativo cambiado a: {mode}.")

    def _handle_scenario_selection(self, index: int) -> None:
        scenario_name = self.panels.scenario.scenario_selector.itemText(index)
        self._open_scenario_configuration(scenario_name)

    def _open_scenario_configuration(self, scenario_name: str) -> None:
        if not scenario_name:
            return

        defaults = self.engine.get_scenario_dialog_defaults(scenario_name)
        dialog = ScenarioConfigDialog(
            scenario_name=scenario_name,
            has_existing_units=bool(self.engine.units),
            current_values=defaults,
            parent=self,
        )
        if dialog.exec() == 0:
            self._restore_scenario_selector()
            self.statusBar().showMessage("Configuración de escenario cancelada.")
            return

        message = self.engine.configure_scenario_from_dialog(dialog.get_result())
        self._sync_parameters_from_engine()
        self._sync_mode_selector()
        self._refresh_ui()
        self.statusBar().showMessage(message)

    def _handle_selection_change(self, unit_id: str | None) -> None:
        if unit_id:
            self.statusBar().showMessage(f"Unidad seleccionada: {unit_id}.")
        self._refresh_ui()

    def _refresh_ui(self) -> None:
        selected_unit = self.engine.units.get(self.engine.selected_unit_id) if self.engine.selected_unit_id else None
        self.panels.unit_info.update_unit(selected_unit)
        self.panels.unit_list_panel.update_units(list(self.engine.units.values()), self.engine.selected_unit_id)
        self.panels.global_status.update_status(self.engine.get_global_status())
        self.panels.swarm_status.update_summaries(self.engine.get_swarm_summaries())
        self.panels.scenario.set_description(self.engine.current_scenario_description)
        self._refresh_alerts()
        self._update_control_states()

    def _refresh_alerts(self) -> None:
        def _to_dict(alert):
            return {
                "timestamp": alert.timestamp,
                "unit_id": alert.unit_id,
                "swarm_id": alert.swarm_id,
                "message": alert.message,
                "severity": alert.severity,
                "prefix": alert.prefix,
            }

        alert_items = [_to_dict(a) for a in self.engine.recent_alerts[:10]]
        self.panels.alerts.update_alerts(alert_items, self.engine.active_alert_count)
        history_items = [_to_dict(a) for a in self.engine.recent_alerts]
        self.panels.alerts.update_history(history_items)

    def _update_control_states(self) -> None:
        controls = self.panels.controls
        has_units = bool(self.engine.units)
        has_selection = self.engine.selected_unit_id is not None and self.engine.selected_unit_id in self.engine.units

        controls.assign_button.setEnabled(has_selection)
        controls.start_button.setEnabled(has_units and not self.engine.is_running)
        controls.pause_button.setEnabled(has_units and self.engine.is_running)
        controls.reset_button.setEnabled(has_units)
        controls.export_button.setEnabled(has_units)

    def _handle_alerts_updated(self, new_alerts: list[Alert]) -> None:
        self._refresh_alerts()
        if not new_alerts:
            return

        if not self.panels.parameters.alert_sound_checkbox.isChecked():
            return

        for alert in new_alerts:
            self._emit_alert_sound(alert)

    def _emit_alert_sound(self, alert: Alert) -> None:
        QApplication.beep()
        if alert.severity == settings.SEVERITY_CRIT:
            QTimer.singleShot(150, QApplication.beep)
            QTimer.singleShot(300, QApplication.beep)

    def _sync_parameters_from_engine(self) -> None:
        params = self.panels.parameters
        widgets = (
            params.max_speed_spin,
            params.altitude_spin,
            params.separation_spin,
            params.zone_radius_spin,
            params.low_battery_spin,
            params.active_units_spin,
        )
        for widget in widgets:
            widget.blockSignals(True)

        params.max_speed_spin.setValue(self.engine.max_speed)
        params.altitude_spin.setValue(self.engine.target_altitude)
        params.separation_spin.setValue(self.engine.min_separation)
        params.zone_radius_spin.setValue(self.engine.zone_radius)
        params.low_battery_spin.setValue(self.engine.low_battery_threshold)
        params.active_units_spin.setValue(self.engine.active_unit_target)

        for widget in widgets:
            widget.blockSignals(False)

        params.time_scale_combo.blockSignals(True)
        params.time_scale_combo.setCurrentText(f"{self.engine.time_scale}x")
        params.time_scale_combo.blockSignals(False)

        self.panels.scenario.scenario_selector.blockSignals(True)
        self.panels.scenario.scenario_selector.setCurrentText(self.engine.current_scenario_name)
        self.panels.scenario.scenario_selector.blockSignals(False)
        self._sync_mode_selector()

    def _restore_scenario_selector(self) -> None:
        self.panels.scenario.scenario_selector.blockSignals(True)
        self.panels.scenario.scenario_selector.setCurrentText(self.engine.current_scenario_name)
        self.panels.scenario.scenario_selector.blockSignals(False)

    def _export_report(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        from app.io.exporter import export_run
        directory = QFileDialog.getExistingDirectory(self, "Carpeta de destino")
        if not directory:
            return
        summary = self.engine.metrics.build_summary(self.engine.get_global_status())
        paths = export_run(directory, self.engine.metrics.timeseries_rows(), summary)
        self.statusBar().showMessage(f"Informe exportado en {paths['timeseries']}")

    def _sync_mode_selector(self) -> None:
        self.panels.controls.mode_selector.blockSignals(True)
        self.panels.controls.mode_selector.setCurrentText(self.engine.mode)
        self.panels.controls.mode_selector.blockSignals(False)
