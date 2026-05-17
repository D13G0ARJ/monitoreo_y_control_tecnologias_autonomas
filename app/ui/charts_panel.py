from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

try:
    from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
    CHARTS_AVAILABLE = True
except ImportError:  # pragma: no cover - environment dependent
    CHARTS_AVAILABLE = False

from app.config import settings


class ChartsPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        if not CHARTS_AVAILABLE:
            layout.addWidget(QLabel("Gráficos no disponibles (QtCharts ausente)."))
            self._ok = False
            return
        self._ok = True
        self._batt = QLineSeries()
        self._batt.setName("Batería promedio")
        self._batt.setPen(QPen(QColor(settings.COLOR_STATUS_ACTIVE), 2))
        self._alerts = QLineSeries()
        self._alerts.setName("Alertas activas")
        self._alerts.setPen(QPen(QColor(settings.COLOR_WARNING), 2))

        self._axis_x = QValueAxis()
        self._axis_x.setTitleText("Tiempo de simulación (s)")
        self._axis_x.setLabelFormat("%.1f")
        self._axis_x.setTickCount(5)

        self._axis_battery = QValueAxis()
        self._axis_battery.setTitleText("Batería promedio (%)")
        self._axis_battery.setRange(0, 100)
        self._axis_battery.setLabelFormat("%.0f")

        self._axis_alerts = QValueAxis()
        self._axis_alerts.setTitleText("Alertas activas")
        self._axis_alerts.setRange(0, 1)
        self._axis_alerts.setLabelFormat("%.0f")
        self._axis_alerts.setTickCount(3)

        self._chart = QChart()
        self._chart.addSeries(self._batt)
        self._chart.addSeries(self._alerts)
        self._chart.addAxis(self._axis_x, Qt.AlignBottom)
        self._chart.addAxis(self._axis_battery, Qt.AlignLeft)
        self._chart.addAxis(self._axis_alerts, Qt.AlignRight)
        self._batt.attachAxis(self._axis_x)
        self._batt.attachAxis(self._axis_battery)
        self._alerts.attachAxis(self._axis_x)
        self._alerts.attachAxis(self._axis_alerts)
        self._style_chart()

        view = QChartView(self._chart)
        view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(view)

    def update_charts(self, battery_window, alert_window) -> None:
        if not self._ok:
            return
        self._batt.clear()
        for t, v in battery_window:
            self._batt.append(t, v)
        self._alerts.clear()
        for t, v in alert_window:
            self._alerts.append(t, v)
        self._update_axes(list(battery_window), list(alert_window))

    def _style_chart(self) -> None:
        self._chart.setTitle("Métricas en vivo")
        self._chart.setTitleBrush(QColor(settings.COLOR_TEXT))
        self._chart.setBackgroundBrush(QColor(settings.COLOR_PANEL))
        self._chart.setPlotAreaBackgroundBrush(QColor(settings.COLOR_BACKGROUND_ALT))
        self._chart.setPlotAreaBackgroundVisible(True)
        self._chart.legend().setLabelColor(QColor(settings.COLOR_TEXT))

        for axis in (self._axis_x, self._axis_battery, self._axis_alerts):
            axis.setLabelsColor(QColor(settings.COLOR_MUTED))
            axis.setTitleBrush(QColor(settings.COLOR_TEXT))
            axis.setGridLineColor(QColor(settings.COLOR_BORDER))
            axis.setLinePenColor(QColor(settings.COLOR_BORDER))

    def _update_axes(self, battery_points: list[tuple[float, float]], alert_points: list[tuple[float, int]]) -> None:
        all_times = [time for time, _ in battery_points] + [time for time, _ in alert_points]
        if not all_times:
            self._axis_x.setRange(0, 1)
            self._axis_battery.setRange(0, 100)
            self._axis_alerts.setRange(0, 1)
            return

        min_time = min(all_times)
        max_time = max(all_times)
        if min_time == max_time:
            max_time = min_time + 1.0
        self._axis_x.setRange(min_time, max_time)

        self._axis_battery.setRange(0, 100)
        max_alerts = max((count for _, count in alert_points), default=0)
        self._axis_alerts.setRange(0, max(1, max_alerts + 1))
