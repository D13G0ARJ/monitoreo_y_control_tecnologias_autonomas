from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit


class ProgressBarMixin:
    @staticmethod
    def build_battery_bar() -> QProgressBar:
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(0)
        bar.setFormat("--")
        bar.setTextVisible(True)
        return bar

class UnitInfoPanel(QGroupBox):
    def __init__(self) -> None:
        super().__init__("Unidad seleccionada")
        self._values: dict[str, QLabel] = {}

        self.header_label = QLabel("Supervisión de unidad")
        self.header_label.setProperty("role", "title")
        self.status_badge = QLabel("Sin selección")
        self.status_badge.setProperty("role", "statusBadge")
        self.status_badge.setStyleSheet(f"color: {settings.COLOR_STATUS_IDLE};")
        self.battery_bar = ProgressBarMixin.build_battery_bar()
        self.empty_message = QLabel("Seleccione una unidad en el radar")
        self.empty_message.setProperty("role", "empty")

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)

        for key, label in (
            ("identifier", "ID"),
            ("swarm", "Enjambre"),
            ("swarm_role", "Rol de enjambre"),
            ("role", "Rol actual"),
            ("task", "Tarea"),
            ("position", "Posición X/Y"),
            ("speed", "Velocidad"),
            ("altitude", "Altitud"),
            ("distance", "Distancia al objetivo"),
            ("alerts", "Alertas activas"),
        ):
            field_label = QLabel(f"{label}:")
            field_label.setProperty("role", "field")
            value_label = QLabel("--")
            value_label.setProperty("role", "value")
            value_label.setWordWrap(True)
            self._values[key] = value_label
            form.addRow(field_label, value_label)

        status_row = QHBoxLayout()
        status_label = QLabel("Estado:")
        status_label.setProperty("role", "field")
        status_row.addWidget(status_label)
        status_row.addWidget(self.status_badge, 1)

        battery_layout = QVBoxLayout()
        battery_label = QLabel("Batería:")
        battery_label.setProperty("role", "field")
        battery_layout.addWidget(battery_label)
        battery_layout.addWidget(self.battery_bar)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(
            f"color: {settings.COLOR_BORDER}; background-color: {settings.COLOR_BORDER}; max-height: 1px;"
        )

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.addWidget(self.header_label)
        layout.addWidget(self.empty_message)
        layout.addLayout(status_row)
        layout.addLayout(battery_layout)
        layout.addWidget(separator)
        layout.addLayout(form)
        self.setLayout(layout)

    def update_unit(self, unit: AutonomousUnit | None) -> None:
        if unit is None:
            for value in self._values.values():
                value.setText("--")
            self.empty_message.show()
            self.status_badge.setText("Sin selección")
            self.status_badge.setStyleSheet(f"color: {settings.COLOR_STATUS_IDLE};")
            self.battery_bar.setValue(0)
            self.battery_bar.setFormat("--")
            self.battery_bar.setStyleSheet("")
            return

        self.empty_message.hide()
        self._values["identifier"].setText(unit.identifier)
        self._values["swarm"].setText(f"{unit.swarm_id} ({unit.swarm_name})")
        self._values["swarm_role"].setText(unit.swarm_role.title())
        self._values["role"].setText(unit.role.title())
        self._values["task"].setText(unit.task_label)
        self._values["position"].setText(f"{unit.x:0.1f}, {unit.y:0.1f}")
        self._values["speed"].setText(f"{unit.speed:0.1f} u/s")
        self._values["altitude"].setText(f"{unit.altitude:0.1f} m")
        self.status_badge.setText(unit.state.title())
        self.status_badge.setStyleSheet(f"color: {self._resolve_state_color(unit.state)};")
        self.battery_bar.setValue(int(unit.battery))
        self.battery_bar.setFormat(f"{unit.battery:0.1f}%")
        self.battery_bar.setStyleSheet(
            "QProgressBar::chunk {"
            f"background-color: {self._resolve_battery_color(unit.battery)};"
            "border-radius: 5px;}"
        )

        if unit.distance_to_target is None:
            self._values["distance"].setText("--")
        else:
            self._values["distance"].setText(f"{unit.distance_to_target:0.1f} u")

        self._values["alerts"].setText(", ".join(unit.active_alerts) if unit.active_alerts else "ninguna")

    @staticmethod
    def _resolve_state_color(state: str) -> str:
        if state == settings.STATUS_SIN_BATERIA:
            return settings.COLOR_STATUS_OFFLINE
        if state == settings.STATUS_CRITICO:
            return settings.COLOR_STATUS_CRITICAL
        if state == settings.STATUS_BATERIA_BAJA:
            return settings.COLOR_STATUS_ROUTE
        if state == settings.STATUS_FUERA_DE_ZONA:
            return settings.COLOR_STATUS_ALERT
        if state == settings.STATUS_RECONOCIMIENTO:
            return settings.COLOR_STATUS_RECON
        if state in {settings.STATUS_EN_RUTA, settings.STATUS_OBJETIVO_ALCANZADO}:
            return settings.COLOR_STATUS_ROUTE
        if state == settings.STATUS_DETENIDO:
            return settings.COLOR_STATUS_IDLE
        return settings.COLOR_STATUS_ACTIVE

    @staticmethod
    def _resolve_battery_color(level: float) -> str:
        if level <= 0.0:
            return settings.COLOR_STATUS_OFFLINE
        if level <= settings.CRITICAL_BATTERY_THRESHOLD:
            return settings.COLOR_STATUS_CRITICAL
        if level < settings.DEFAULT_LOW_BATTERY_THRESHOLD:
            return settings.COLOR_STATUS_ROUTE
        if level < 45.0:
            return settings.COLOR_STATUS_ROUTE
        return settings.COLOR_STATUS_ACTIVE


class GlobalStatusPanel(QGroupBox):
    def __init__(self) -> None:
        super().__init__("Estado global")
        self._values: dict[str, QLabel] = {}
        self.description_label = QLabel("--")
        self.description_label.setWordWrap(True)
        self.description_label.setProperty("role", "field")

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        for row, (key, label) in enumerate(
            (
                ("scenario", "Escenario"),
                ("mode", "Modo"),
                ("units", "Unidades activas"),
                ("configured_units", "Unidades configuradas"),
                ("swarms", "Enjambres"),
                ("alerts", "Alertas activas"),
                ("simulation", "Simulación"),
                ("time", "Tiempo"),
                ("max_speed", "Velocidad máxima"),
                ("zone_radius", "Radio de vigilancia"),
                ("min_separation", "Separación mínima"),
                ("low_battery_threshold", "Batería baja"),
            )
        ):
            card = QGroupBox(label)
            card_layout = QVBoxLayout()
            value = QLabel("--")
            value.setProperty("role", "value")
            value.setWordWrap(True)
            card_layout.addWidget(value)
            card.setLayout(card_layout)
            self._values[key] = value
            grid.addWidget(card, row // 2, row % 2)

        layout = QVBoxLayout()
        layout.addLayout(grid)
        overview_title = QLabel("Resumen de enjambres:")
        overview_title.setProperty("role", "field")
        self.swarm_overview_label = QLabel("--")
        self.swarm_overview_label.setWordWrap(True)
        self.swarm_overview_label.setProperty("role", "value")
        layout.addWidget(overview_title)
        layout.addWidget(self.swarm_overview_label)
        description_title = QLabel("Descripción del escenario:")
        description_title.setProperty("role", "field")
        layout.addWidget(description_title)
        layout.addWidget(self.description_label)
        self.setLayout(layout)

    def update_status(self, status: dict[str, str]) -> None:
        for key, value in self._values.items():
            value.setText(status.get(key, "--"))
        self.swarm_overview_label.setText(status.get("swarm_overview", "--"))
        self.description_label.setText(status.get("description", "--"))


class SwarmStatusPanel(QGroupBox):
    def __init__(self) -> None:
        super().__init__("Enjambres operativos")
        self.overview_label = QLabel("Sin enjambres activos")
        self.overview_label.setWordWrap(True)
        self.overview_label.setProperty("role", "field")
        self._rows: list[dict[str, QLabel]] = []

        layout = QVBoxLayout()
        layout.addWidget(self.overview_label)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)
        for index in range(2):
            card = QGroupBox(f"Enjambre {index + 1}")
            card_layout = QFormLayout()
            count_value = QLabel("--")
            role_value = QLabel("--")
            status_value = QLabel("--")
            for value in (count_value, role_value, status_value):
                value.setProperty("role", "value")
                value.setWordWrap(True)
            card_layout.addRow("Unidades:", count_value)
            card_layout.addRow("Rol:", role_value)
            card_layout.addRow("Estado:", status_value)
            card.setLayout(card_layout)
            grid.addWidget(card, 0, index)
            self._rows.append(
                {
                    "count": count_value,
                    "role": role_value,
                    "status": status_value,
                }
            )

        layout.addLayout(grid)
        self.setLayout(layout)

    def update_summaries(self, summaries) -> None:
        if not summaries:
            self.overview_label.setText("Sin enjambres activos")
        else:
            self.overview_label.setText(
                " | ".join(f"{summary.swarm_id}: {summary.swarm_role.title()}" for summary in summaries)
            )

        for row in self._rows:
            row["count"].setText("--")
            row["role"].setText("--")
            row["status"].setText("--")

        for index, summary in enumerate(summaries[:2]):
            row = self._rows[index]
            row["count"].setText(str(summary.unit_count))
            row["role"].setText(summary.swarm_role.title())
            row["status"].setText(summary.general_status.title())


class ParametersPanel(QGroupBox):
    def __init__(self) -> None:
        super().__init__("Parámetros operativos")

        self.max_speed_spin = QDoubleSpinBox()
        self.max_speed_spin.setRange(20.0, 120.0)
        self.max_speed_spin.setSuffix(" u/s")
        self.max_speed_spin.setDecimals(1)
        self.max_speed_spin.setValue(settings.MAX_SPEED)

        self.altitude_spin = QDoubleSpinBox()
        self.altitude_spin.setRange(settings.MIN_ALTITUDE, settings.MAX_ALTITUDE)
        self.altitude_spin.setSuffix(" m")
        self.altitude_spin.setDecimals(1)
        self.altitude_spin.setValue(settings.DEFAULT_ALTITUDE)

        self.separation_spin = QDoubleSpinBox()
        self.separation_spin.setRange(10.0, settings.MAX_MIN_SEPARATION)
        self.separation_spin.setSuffix(" u")
        self.separation_spin.setDecimals(1)
        self.separation_spin.setValue(settings.DEFAULT_MIN_SEPARATION)

        self.zone_radius_spin = QDoubleSpinBox()
        self.zone_radius_spin.setRange(180.0, 420.0)
        self.zone_radius_spin.setSuffix(" u")
        self.zone_radius_spin.setDecimals(1)
        self.zone_radius_spin.setValue(settings.DEFAULT_ZONE_RADIUS)

        self.low_battery_spin = QDoubleSpinBox()
        self.low_battery_spin.setRange(5.0, 60.0)
        self.low_battery_spin.setSuffix(" %")
        self.low_battery_spin.setDecimals(1)
        self.low_battery_spin.setValue(settings.DEFAULT_LOW_BATTERY_THRESHOLD)

        self.active_units_spin = QSpinBox()
        self.active_units_spin.setRange(0, 20)
        self.active_units_spin.setValue(settings.DEFAULT_ACTIVE_UNITS)

        self.alert_sound_checkbox = QCheckBox("Sonido de alertas")
        self.alert_sound_checkbox.setChecked(True)

        self.time_scale_combo = QComboBox()
        for scale in settings.AVAILABLE_TIME_SCALES:
            self.time_scale_combo.addItem(f"{scale}x")
        self.time_scale_combo.setMaximumWidth(150)

        for widget in (
            self.max_speed_spin,
            self.altitude_spin,
            self.separation_spin,
            self.zone_radius_spin,
            self.low_battery_spin,
            self.active_units_spin,
        ):
            widget.setMaximumWidth(150)

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(10)
        parameter_rows = (
            ("Velocidad máxima:", self.max_speed_spin),
            ("Altitud objetivo:", self.altitude_spin),
            ("Separación mínima:", self.separation_spin),
            ("Radio de vigilancia:", self.zone_radius_spin),
            ("Batería baja:", self.low_battery_spin),
            ("Unidades activas:", self.active_units_spin),
        )
        for index, (label, widget) in enumerate(parameter_rows):
            row = index // 2
            column = (index % 2) * 2
            title = QLabel(label)
            title.setProperty("role", "field")
            grid.addWidget(title, row, column)
            grid.addWidget(widget, row, column + 1)

        time_scale_row = len(parameter_rows) // 2
        time_scale_label = QLabel("Escala de tiempo:")
        time_scale_label.setProperty("role", "field")
        grid.addWidget(time_scale_label, time_scale_row, 0)
        grid.addWidget(self.time_scale_combo, time_scale_row, 1)

        layout = QVBoxLayout()
        layout.addLayout(grid)
        layout.addWidget(self.alert_sound_checkbox)
        self.setLayout(layout)


class ScenarioPanel(QGroupBox):
    def __init__(self) -> None:
        super().__init__("Escenarios y misión")
        self.scenario_selector = QComboBox()
        self.scenario_selector.addItems(settings.AVAILABLE_SCENARIOS)

        self.assignment_mode_selector = QComboBox()
        self.assignment_mode_selector.addItems([settings.TASK_TEMPORARY, settings.TASK_MANUAL])
        self.scenario_selector.setMaximumWidth(220)
        self.assignment_mode_selector.setMaximumWidth(220)

        self.scenario_description = QLabel(settings.SCENARIO_CONFIG[settings.SCENARIO_ZONE_PROTECTION]["description"])
        self.scenario_description.setWordWrap(True)
        self.scenario_description.setProperty("role", "field")
        self.help_label = QLabel("Cambiar escenario abre la configuración operativa antes de aplicar cambios.")
        self.help_label.setWordWrap(True)
        self.help_label.setProperty("role", "empty")

        form = QFormLayout()
        form.addRow("Escenario:", self.scenario_selector)
        form.addRow("Asignación manual:", self.assignment_mode_selector)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.scenario_description)
        layout.addWidget(self.help_label)
        self.setLayout(layout)

    def set_description(self, text: str) -> None:
        self.scenario_description.setText(text)


class ControlPanel(QGroupBox):
    def __init__(self) -> None:
        super().__init__("Control de simulación")

        self.create_button = QPushButton("Crear unidad")
        self.assign_button = QPushButton("Asignar objetivo")
        self.start_button = QPushButton("Iniciar")
        self.pause_button = QPushButton("Pausar")
        self.reset_button = QPushButton("Reiniciar")
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(settings.AVAILABLE_MODES)
        self.mode_selector.setMaximumWidth(220)
        self.instructions_label = QLabel("Seleccione una unidad en el radar para asignar una tarea manual o temporal.")
        self.instructions_label.setWordWrap(True)
        self.instructions_label.setProperty("role", "field")

        mode_row = QHBoxLayout()
        mode_label = QLabel("Modo operativo:")
        mode_label.setProperty("role", "field")
        mode_row.addWidget(mode_label)
        mode_row.addWidget(self.mode_selector)
        mode_row.addStretch(1)

        self.export_button = QPushButton("Exportar informe")

        button_grid = QGridLayout()
        button_grid.setHorizontalSpacing(10)
        button_grid.setVerticalSpacing(10)
        button_grid.addWidget(self.create_button, 0, 0)
        button_grid.addWidget(self.assign_button, 0, 1)
        button_grid.addWidget(self.start_button, 1, 0)
        button_grid.addWidget(self.pause_button, 1, 1)
        button_grid.addWidget(self.reset_button, 2, 0, 1, 2)
        button_grid.addWidget(self.export_button, 3, 0, 1, 2)

        layout = QVBoxLayout()
        layout.addLayout(mode_row)
        layout.addWidget(self.instructions_label)
        layout.addLayout(button_grid)
        layout.addStretch(1)
        self.setLayout(layout)


class AlertsPanel(QGroupBox):
    def __init__(self) -> None:
        super().__init__("Alertas del sistema")
        self.counter_label = QLabel("0 alertas activas")
        self.counter_label.setProperty("role", "value")
        self.clear_button = QPushButton("Limpiar alertas")
        self.list_widget = QListWidget()
        self.list_widget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.list_widget.setAlternatingRowColors(True)

        header = QHBoxLayout()
        header.addWidget(self.counter_label)
        header.addStretch(1)
        header.addWidget(self.clear_button)

        history_title = QLabel("Historial completo")
        history_title.setProperty("role", "title")
        self.history_list = QListWidget()
        self.history_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.history_list.setAlternatingRowColors(True)

        layout = QVBoxLayout()
        layout.addLayout(header)
        layout.addWidget(self.list_widget)
        layout.addWidget(history_title)
        layout.addWidget(self.history_list, 1)
        self.setLayout(layout)

    def update_alerts(self, alerts: list[dict[str, str]], active_count: int) -> None:
        self.counter_label.setText(f"{active_count} alertas activas")
        self.list_widget.clear()
        if not alerts:
            self.list_widget.addItem("Sin alertas registradas.")
            return

        for alert in alerts[:10]:
            unit_scope = alert["unit_id"]
            if alert.get("swarm_id"):
                unit_scope = f"{unit_scope} / {alert['swarm_id']}"
            item = QListWidgetItem(
                f"{alert['prefix']} [{alert['timestamp']}] {unit_scope}: {alert['message']}"
            )
            severity = alert["severity"]
            if severity == settings.SEVERITY_CRIT:
                item.setForeground(QColor(settings.COLOR_ALERT))
                item.setBackground(QColor(settings.COLOR_ALERT_BG_HIGH))
            elif severity == settings.SEVERITY_WARN:
                item.setForeground(QColor(settings.COLOR_WARNING))
                item.setBackground(QColor(settings.COLOR_ALERT_BG_MEDIUM))
            else:
                item.setForeground(QColor(settings.COLOR_OBSERVATION))
                item.setBackground(QColor(settings.COLOR_ALERT_BG_INFO))
            self.list_widget.addItem(item)

    def update_history(self, alert_items: list) -> None:
        self.history_list.clear()
        for a in alert_items:
            self.history_list.addItem(
                f"[{a['timestamp']}] {a['prefix']} {a['unit_id']}: {a['message']}"
            )


class UnitListPanel(QGroupBox):
    def __init__(self) -> None:
        super().__init__("Lista de unidades")
        title_label = QLabel("Unidades activas")
        title_label.setProperty("role", "title")

        self.unit_list = QListWidget()
        self.unit_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.unit_list.setAlternatingRowColors(True)

        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(self.unit_list)
        self.setLayout(layout)

    def update_units(self, units: list, selected_id: str | None) -> None:
        self.unit_list.blockSignals(True)
        self.unit_list.clear()
        for u in units:
            text = f"{u.identifier} [{u.swarm_id}] {u.state}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, u.identifier)
            self.unit_list.addItem(item)
            if u.identifier == selected_id:
                self.unit_list.setCurrentItem(item)
        self.unit_list.blockSignals(False)


class LegendPanel(QGroupBox):
    def __init__(self) -> None:
        super().__init__("Leyenda")
        layout = QVBoxLayout()
        for text, color in (
            ("Patrullaje defensivo", settings.COLOR_ROLE_PATROL),
            ("Reconocimiento", settings.COLOR_ROLE_RECON),
            ("Control manual", settings.COLOR_WAYPOINT),
            ("Alerta crítica", settings.COLOR_ALERT),
        ):
            label = QLabel(f"■ {text}")
            label.setStyleSheet(f"color: {color}; font-weight: 600;")
            layout.addWidget(label)
        layout.addStretch(1)
        self.setLayout(layout)


class SidePanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.global_status = GlobalStatusPanel()
        self.scenario = ScenarioPanel()
        self.parameters = ParametersPanel()
        self.unit_info = UnitInfoPanel()
        self.controls = ControlPanel()
        self.legend = LegendPanel()
        self.alerts = AlertsPanel()

        layout = QVBoxLayout()
        layout.addWidget(self.global_status)
        layout.addWidget(self.scenario)
        layout.addWidget(self.parameters)
        layout.addWidget(self.unit_info)
        layout.addWidget(self.controls)
        layout.addWidget(self.legend)
        layout.addWidget(self.alerts, 1)
        self.setLayout(layout)


class ControlTabsWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.global_status = GlobalStatusPanel()
        self.swarm_status = SwarmStatusPanel()
        self.scenario = ScenarioPanel()
        self.parameters = ParametersPanel()
        self.unit_info = UnitInfoPanel()
        self.unit_list_panel = UnitListPanel()
        self.controls = ControlPanel()
        self.legend = LegendPanel()
        self.alerts = AlertsPanel()

        self.tabs = QTabWidget()
        self.tabs.addTab(
            self._wrap_scroll([self.global_status, self.swarm_status, self.unit_list_panel, self.unit_info]),
            "Estado",
        )
        self.tabs.addTab(
            self._wrap_scroll([self.scenario, self.controls]),
            "Control",
        )
        self.tabs.addTab(
            self._wrap_scroll([self.parameters, self.legend]),
            "Parámetros",
        )
        self.tabs.addTab(
            self._wrap_scroll([self.alerts]),
            "Alertas",
        )

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    @staticmethod
    def _wrap_scroll(widgets: list[QWidget]) -> QScrollArea:
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(10)
        for widget in widgets:
            layout.addWidget(widget)
        layout.addStretch(1)
        container.setLayout(layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(container)
        return scroll
