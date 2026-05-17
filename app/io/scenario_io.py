from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from app.config import settings
from app.services.scenario_service import ScenarioApplicationConfig


def save_scenario_config(path: str | Path, config: ScenarioApplicationConfig) -> None:
    Path(path).write_text(json.dumps(asdict(config), indent=2, ensure_ascii=False),
                          encoding="utf-8")


def load_scenario_config(path: str | Path) -> ScenarioApplicationConfig:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    scenario = settings.SCENARIO_CONFIG.get(data.get("scenario_name", ""), {})
    data.setdefault("mode", scenario.get("mode", settings.MODE_DEFENSIVE))
    data.setdefault("protected_radius", scenario.get("protected_radius", 0.0))
    data.setdefault("observation_points", scenario.get("observation_points", []))
    data["observation_points"] = [tuple(point) for point in data["observation_points"]]
    return ScenarioApplicationConfig(**data)
