from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QVBoxLayout,
)

from app.config import settings


@dataclass
class ScenarioDialogResult:
    scenario_name: str
    unit_count: int
    swarm_count: int
    distribution: str
    use_existing_units: bool
    max_speed: float
    target_altitude: float
    zone_radius: float
    min_separation: float
    low_battery_threshold: float
    auto_start: bool


class ScenarioConfigDialog(QDialog):
    def __init__(
        self,
        scenario_name: str,
        has_existing_units: bool,
        current_values: dict[str, float | int | str],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Configurar escenario")
        self.setModal(True)
        self.resize(420, 520)
        self._scenario_name = scenario_name

        description = settings.SCENARIO_CONFIG.get(scenario_name, {}).get("description", "")
        self.description_label = QLabel(description)
        self.description_label.setWordWrap(True)
        self.description_label.setProperty("role", "field")

        self.unit_count_spin = QSpinBox()
        self.unit_count_spin.setRange(1, 20)
        self.unit_count_spin.setValue(int(current_values.get("unit_count", settings.DEFAULT_ACTIVE_UNITS)))

        self.swarm_count_combo = QComboBox()
        self.swarm_count_combo.addItems(["1", "2"])
        self.swarm_count_combo.setCurrentText(str(current_values.get("swarm_count", 1)))

        self.distribution_combo = QComboBox()
        self.distribution_combo.addItems(["Automática", "Mitad y mitad"])
        self.distribution_combo.setCurrentText(str(current_values.get("distribution", "Automática")))

        self.units_mode_combo = QComboBox()
        self.units_mode_combo.addItem("Usar unidades existentes")
        self.units_mode_combo.addItem("Reemplazar unidades")
        if not has_existing_units:
            self.units_mode_combo.setCurrentText("Reemplazar unidades")
            self.units_mode_combo.setEnabled(False)

        self.max_speed_spin = QDoubleSpinBox()
        self.max_speed_spin.setRange(20.0, 120.0)
        self.max_speed_spin.setSuffix(" u/s")
        self.max_speed_spin.setDecimals(1)
        self.max_speed_spin.setValue(float(current_values.get("max_speed", settings.MAX_SPEED)))

        self.altitude_spin = QDoubleSpinBox()
        self.altitude_spin.setRange(settings.MIN_ALTITUDE, settings.MAX_ALTITUDE)
        self.altitude_spin.setSuffix(" m")
        self.altitude_spin.setDecimals(1)
        self.altitude_spin.setValue(float(current_values.get("target_altitude", settings.DEFAULT_ALTITUDE)))

        self.zone_radius_spin = QDoubleSpinBox()
        self.zone_radius_spin.setRange(180.0, 420.0)
        self.zone_radius_spin.setSuffix(" u")
        self.zone_radius_spin.setDecimals(1)
        self.zone_radius_spin.setValue(float(current_values.get("zone_radius", settings.DEFAULT_ZONE_RADIUS)))

        self.min_separation_spin = QDoubleSpinBox()
        self.min_separation_spin.setRange(10.0, settings.MAX_MIN_SEPARATION)
        self.min_separation_spin.setSuffix(" u")
        self.min_separation_spin.setDecimals(1)
        self.min_separation_spin.setValue(float(current_values.get("min_separation", settings.DEFAULT_MIN_SEPARATION)))

        self.low_battery_spin = QDoubleSpinBox()
        self.low_battery_spin.setRange(5.0, 60.0)
        self.low_battery_spin.setSuffix(" %")
        self.low_battery_spin.setDecimals(1)
        self.low_battery_spin.setValue(float(current_values.get("low_battery_threshold", settings.DEFAULT_LOW_BATTERY_THRESHOLD)))

        self.auto_start_checkbox = QCheckBox("Iniciar simulación automáticamente")
        self.auto_start_checkbox.setChecked(bool(current_values.get("auto_start", False)))

        summary_group = QGroupBox("Escenario seleccionado")
        summary_layout = QVBoxLayout()
        summary_layout.addWidget(QLabel(scenario_name))
        summary_layout.addWidget(self.description_label)
        summary_group.setLayout(summary_layout)

        config_group = QGroupBox("Configuración básica")
        config_form = QFormLayout()
        config_form.addRow("Cantidad de unidades:", self.unit_count_spin)
        config_form.addRow("Número de enjambres:", self.swarm_count_combo)
        config_form.addRow("Distribución:", self.distribution_combo)
        config_form.addRow("Unidades:", self.units_mode_combo)
        config_group.setLayout(config_form)

        params_group = QGroupBox("Parámetros principales")
        params_form = QFormLayout()
        params_form.addRow("Velocidad máxima:", self.max_speed_spin)
        params_form.addRow("Altitud objetivo:", self.altitude_spin)
        params_form.addRow("Radio de vigilancia:", self.zone_radius_spin)
        params_form.addRow("Separación mínima:", self.min_separation_spin)
        params_form.addRow("Batería baja:", self.low_battery_spin)
        params_group.setLayout(params_form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Aplicar escenario")
        buttons.button(QDialogButtonBox.Cancel).setText("Cancelar")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(summary_group)
        layout.addWidget(config_group)
        layout.addWidget(params_group)
        layout.addWidget(self.auto_start_checkbox)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_result(self) -> ScenarioDialogResult:
        return ScenarioDialogResult(
            scenario_name=self._scenario_name,
            unit_count=self.unit_count_spin.value(),
            swarm_count=int(self.swarm_count_combo.currentText()),
            distribution=self.distribution_combo.currentText(),
            use_existing_units=self.units_mode_combo.currentText() == "Usar unidades existentes",
            max_speed=self.max_speed_spin.value(),
            target_altitude=self.altitude_spin.value(),
            zone_radius=self.zone_radius_spin.value(),
            min_separation=self.min_separation_spin.value(),
            low_battery_threshold=self.low_battery_spin.value(),
            auto_start=self.auto_start_checkbox.isChecked(),
        )
