from __future__ import annotations

import csv
import json
from pathlib import Path

from app.io.exporter import export_run


def test_export_writes_csv_and_json(tmp_path: Path):
    rows = [{"sim_time": 0.0, "unit_id": "U01", "x": 1.0, "y": 2.0,
             "battery": 99.0, "state": "activo"}]
    summary = {"scenario": {"scenario": "X"}, "units": {"U01": {"distance": 0.0}}}
    paths = export_run(tmp_path, rows, summary)
    csv_rows = list(csv.DictReader(open(paths["timeseries"], encoding="utf-8")))
    assert csv_rows[0]["unit_id"] == "U01"
    assert json.load(open(paths["summary"], encoding="utf-8"))["scenario"]["scenario"] == "X"


def test_export_empty_rows_ok(tmp_path: Path):
    paths = export_run(tmp_path, [], {"scenario": {}, "units": {}})
    assert Path(paths["timeseries"]).exists()
