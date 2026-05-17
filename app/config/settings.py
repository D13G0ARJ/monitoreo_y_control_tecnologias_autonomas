from __future__ import annotations

APP_NAME = "Simulador Radar UNEFA"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
RADAR_WINDOW_WIDTH = 1280
RADAR_WINDOW_HEIGHT = 860
CONTROL_WINDOW_WIDTH = 460
CONTROL_WINDOW_HEIGHT = 860

RADAR_RADIUS = 320.0
RADAR_CONCENTRIC_RINGS = 4
RADAR_MARGIN = 60.0
RADAR_SWEEP_ENABLED = True
RADAR_SWEEP_STEP_DEGREES = 3.0
RADAR_SWEEP_INTERVAL_MS = 35
RADAR_SWEEP_WIDTH_DEGREES = 28.0
RADAR_UNIT_RADIUS = 9.5
RADAR_SELECTED_RING_RADIUS = 17.0

SIMULATION_INTERVAL_MS = 100
DEFAULT_ZONE_RADIUS = RADAR_RADIUS
DEFAULT_ALTITUDE = 150.0
MIN_ALTITUDE = 100.0
MAX_ALTITUDE = 450.0
DEFAULT_SPEED = 55.0
MIN_SPEED = 20.0
MAX_SPEED = 80.0
DEFAULT_MIN_SEPARATION = 38.0
MAX_MIN_SEPARATION = 120.0
CONTROL_KP = 0.85
TARGET_TOLERANCE = 10.0
DEFAULT_LOW_BATTERY_THRESHOLD = 20.0
CRITICAL_BATTERY_THRESHOLD = 5.0
BATTERY_DRAIN_IDLE = 0.02
BATTERY_DRAIN_MOVING_FACTOR = 0.0009
MAX_TRAJECTORY_POINTS = 80
SPAWN_MIN_DISTANCE = 35.0
DEFAULT_ACTIVE_UNITS = 6

# Movement / behavior tunables (extracted from inline literals)
BATTERY_DRAIN_DT_SCALE = 10.0
SEPARATION_CORRECTION_GAIN = 0.12
PATROL_ORBIT_FACTOR = 0.68
RECON_X_FACTOR = 0.68
RECON_TOP_FACTOR = 0.52
RECON_BOTTOM_FACTOR = 0.48
RECON_STEP_FACTOR = 0.23
SPAWN_MIN_RADIUS = 25.0
SPAWN_MAX_RADIUS_FACTOR = 0.45

# Return-to-base / recharge (Fase 2)
BASE_POSITION = (0.0, 0.0)
RECHARGE_RATE = 6.0  # % por segundo de simulación
RECHARGE_FULL = 100.0
RTB_TRIGGER_MARGIN = 0.0  # se dispara al cruzar low_battery_threshold

# Control de tiempo (Fase 4)
DEFAULT_TIME_SCALE = 1
AVAILABLE_TIME_SCALES = (1, 2, 4, 8)
METRICS_CHART_WINDOW = 240

DISTRIBUTION_AUTO = "Automática"
DISTRIBUTION_HALF = "Mitad y mitad"

MODE_DEFENSIVE = "Defensivo"
MODE_RECON = "Reconocimiento"
MODE_MIXED = "Mixto"
AVAILABLE_MODES = (MODE_DEFENSIVE, MODE_RECON, MODE_MIXED)

ROLE_NONE = "sin rol"
ROLE_PATROL = "patrullaje defensivo"
ROLE_RECON = "reconocimiento"
ROLE_RESERVE = "reserva"
ROLE_MANUAL = "objetivo manual"
TASK_AUTOMATIC = "Misión automática"
TASK_TEMPORARY = "Tarea temporal"
TASK_MANUAL = "Control manual"

STATUS_DETENIDO = "detenido"
STATUS_ACTIVO = "activo"
STATUS_EN_RUTA = "en ruta"
STATUS_PATRULLANDO = "patrullando"
STATUS_RECONOCIMIENTO = "reconocimiento"
STATUS_CRITICO = "crítico"
STATUS_SIN_BATERIA = "sin batería"
STATUS_OBJETIVO_ALCANZADO = "objetivo alcanzado"
STATUS_FUERA_DE_ZONA = "fuera de zona"
STATUS_BATERIA_BAJA = "batería baja"
STATUS_REGRESANDO = "regresando a base"
STATUS_RECARGANDO = "recargando"

ALERT_BATTERY_LOW = "batería baja"
ALERT_BATTERY_CRITICAL = "batería crítica"
ALERT_NO_BATTERY = "sin batería"
ALERT_OUT_OF_ZONE = "fuera de zona"
ALERT_TARGET_REACHED = "objetivo alcanzado"
ALERT_PROXIMITY = "proximidad entre unidades"
ALERT_RTB_START = "retorno a base iniciado"
ALERT_RECHARGE_DONE = "recarga completada"

SEVERITY_INFO = "informativa"
SEVERITY_WARN = "advertencia"
SEVERITY_CRIT = "crítica"

COLOR_BACKGROUND = "#071419"
COLOR_BACKGROUND_ALT = "#0b1c24"
COLOR_PANEL = "#10222b"
COLOR_PANEL_ALT = "#0c1b22"
COLOR_BORDER = "#1f4f57"
COLOR_TEXT = "#d7f7f2"
COLOR_MUTED = "#7ab4ae"
COLOR_GRID = "#1d5a50"
COLOR_ZONE = "#1bb58d"
COLOR_SWEEP = "#7af7d0"
COLOR_SWEEP_GLOW = "#32c39c"
COLOR_TRAJECTORY = "#57d6c2"
COLOR_WAYPOINT = "#ffc857"
COLOR_SELECTED = "#f4f1bb"
COLOR_ALERT = "#ff6b6b"
COLOR_OK = "#47d17c"
COLOR_WARNING = "#ffd166"
COLOR_UNIT = "#2ec4b6"
COLOR_UNIT_IDLE = "#7ab4ae"
COLOR_ROLE_PATROL = "#43d9bd"
COLOR_ROLE_RECON = "#67b7ff"
COLOR_ROUTE_PATROL = "#32c39c"
COLOR_ROUTE_RECON = "#ffd166"
COLOR_STATUS_ACTIVE = "#47d17c"
COLOR_STATUS_ROUTE = "#ffd166"
COLOR_STATUS_RECON = "#67b7ff"
COLOR_STATUS_ALERT = "#ff6b6b"
COLOR_STATUS_IDLE = "#9aa6b2"
COLOR_STATUS_CRITICAL = "#ff7b2c"
COLOR_STATUS_OFFLINE = "#ff4d4f"
COLOR_ALERT_BG_HIGH = "#3a1516"
COLOR_ALERT_BG_MEDIUM = "#3b3116"
COLOR_ALERT_BORDER = "#7c3f3f"
COLOR_ALERT_BORDER_MEDIUM = "#7a6b2f"
COLOR_ALERT_BG_INFO = "#14303a"
COLOR_ALERT_BORDER_INFO = "#2d6f87"
COLOR_ZONE_PROTECTED = "#1e7f6d"
COLOR_OBSERVATION = "#9ac1ff"
COLOR_STATUS_RTB = "#ffb454"
COLOR_STATUS_CHARGING = "#43d9bd"

SCENARIO_ZONE_PROTECTION = "Protección de zona estratégica"
SCENARIO_RECON_AREA = "Reconocimiento de área de interés"
SCENARIO_COMBINED = "Vigilancia y reconocimiento combinado"
AVAILABLE_SCENARIOS = (
    SCENARIO_ZONE_PROTECTION,
    SCENARIO_RECON_AREA,
    SCENARIO_COMBINED,
)

SCENARIO_CONFIG = {
    SCENARIO_ZONE_PROTECTION: {
        "description": "Escenario centrado en supervisión perimetral continua alrededor de una zona estratégica protegida.",
        "mode": MODE_DEFENSIVE,
        "units": 6,
        "zone_radius": 320.0,
        "protected_radius": 95.0,
        "observation_points": [(-120.0, -140.0), (120.0, -140.0), (0.0, 180.0)],
    },
    SCENARIO_RECON_AREA: {
        "description": "Escenario orientado al reconocimiento secuencial de puntos de observación sobre un área de interés.",
        "mode": MODE_RECON,
        "units": 5,
        "zone_radius": 320.0,
        "protected_radius": 70.0,
        "observation_points": [(-180.0, -120.0), (180.0, -40.0), (-150.0, 70.0), (150.0, 160.0)],
    },
    SCENARIO_COMBINED: {
        "description": "Escenario combinado donde un grupo mantiene vigilancia perimetral mientras otro ejecuta reconocimiento secuencial.",
        "mode": MODE_MIXED,
        "units": 7,
        "zone_radius": 320.0,
        "protected_radius": 85.0,
        "observation_points": [(-180.0, -120.0), (180.0, -30.0), (-170.0, 85.0), (170.0, 160.0)],
    },
}

GLOBAL_STYLE_SHEET = f"""
QMainWindow {{
    background-color: {COLOR_BACKGROUND};
}}
QWidget {{
    background-color: {COLOR_BACKGROUND};
    color: {COLOR_TEXT};
    font-family: "Segoe UI";
    font-size: 12px;
}}
QGroupBox {{
    border: 1px solid {COLOR_BORDER};
    border-radius: 10px;
    margin-top: 12px;
    padding: 12px;
    background-color: {COLOR_PANEL};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {COLOR_TEXT};
}}
QPushButton {{
    background-color: {COLOR_PANEL_ALT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 9px 12px;
    font-weight: 600;
}}
QPushButton:hover {{
    border-color: {COLOR_ZONE};
}}
QPushButton:pressed {{
    background-color: {COLOR_BORDER};
}}
QPushButton:disabled {{
    color: {COLOR_MUTED};
    border-color: #294049;
    background-color: #0b171c;
}}
QComboBox, QListWidget, QProgressBar {{
    background-color: {COLOR_PANEL_ALT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 6px;
}}
QTabWidget::pane {{
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    background-color: {COLOR_PANEL};
}}
QTabBar::tab {{
    background-color: {COLOR_PANEL_ALT};
    color: {COLOR_TEXT};
    padding: 8px 14px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}
QTabBar::tab:selected {{
    background-color: {COLOR_PANEL};
    border: 1px solid {COLOR_BORDER};
    border-bottom-color: {COLOR_PANEL};
}}
QScrollArea {{
    border: none;
    background-color: {COLOR_BACKGROUND};
}}
QScrollArea > QWidget > QWidget {{
    background-color: {COLOR_BACKGROUND};
}}
QSpinBox, QDoubleSpinBox, QTextEdit {{
    background-color: {COLOR_PANEL_ALT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 5px;
}}
QCheckBox {{
    spacing: 8px;
}}
QComboBox::drop-down {{
    border: none;
}}
QLabel[role="value"] {{
    color: {COLOR_OK};
    font-weight: 600;
}}
QLabel[role="field"] {{
    color: {COLOR_MUTED};
    font-weight: 600;
}}
QLabel[role="title"] {{
    color: {COLOR_TEXT};
    font-size: 13px;
    font-weight: 700;
}}
QLabel[role="empty"] {{
    color: {COLOR_MUTED};
    font-style: italic;
}}
QLabel[role="statusBadge"] {{
    border: 1px solid {COLOR_BORDER};
    border-radius: 9px;
    padding: 4px 10px;
    font-weight: 700;
}}
QProgressBar {{
    min-height: 16px;
    text-align: center;
    font-weight: 700;
}}
QProgressBar::chunk {{
    background-color: {COLOR_OK};
    border-radius: 5px;
}}
QListWidget {{
    outline: none;
    padding: 4px;
}}
QListWidget::item {{
    margin: 3px 0;
    padding: 8px;
    border-radius: 6px;
}}
QTextEdit {{
    color: {COLOR_TEXT};
}}
QStatusBar {{
    background-color: {COLOR_PANEL};
    color: {COLOR_TEXT};
}}
"""
