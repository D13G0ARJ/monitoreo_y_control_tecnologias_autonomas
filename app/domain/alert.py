from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Alert:
    alert_type: str
    unit_id: str
    message: str
    swarm_id: str = ""
    severity: str = "informativa"
    prefix: str = "INFO"
    key: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
