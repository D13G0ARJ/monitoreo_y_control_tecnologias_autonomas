from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Waypoint:
    identifier: str
    x: float
    y: float
    altitude: float = 0.0
    kind: str = "objetivo"
