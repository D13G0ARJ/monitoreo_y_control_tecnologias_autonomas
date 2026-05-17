from __future__ import annotations

import csv
import json
from pathlib import Path

_CSV_FIELDS = ["sim_time", "unit_id", "x", "y", "battery", "state"]


def export_run(out_dir: str | Path, timeseries_rows: list[dict[str, object]],
               summary: dict[str, object]) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ts_path = out / "timeseries.csv"
    sum_path = out / "summary.json"

    with ts_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        for row in timeseries_rows:
            writer.writerow({k: row.get(k, "") for k in _CSV_FIELDS})

    sum_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"timeseries": str(ts_path), "summary": str(sum_path)}
