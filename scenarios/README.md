# Reusable Scenario Fixtures

These JSON files use the same shape as `ScenarioApplicationConfig` and can be loaded from the GUI with `Cargar configuración`.

- `zone_protection_baseline.json`: defensive patrol around the protected zone with 8 units.
- `recon_area_baseline.json`: reconnaissance route through observation points with 7 units.
- `combined_swarm_demo.json`: two-swarm patrol/reconnaissance demonstration with 10 units.
- `rtb_low_battery_demo.json`: low-battery threshold tuned to exercise return-to-base behavior quickly with 5 units.
- `proximity_alert_demo.json`: small two-unit setup for proximity alert checks.

The automated coverage for these fixtures lives in `tests/test_reusable_scenarios.py`.

When one of these configurations is loaded, target distance is not read from the JSON file. The simulator calculates it from each unit's current position and assigned waypoint, then updates it as the unit moves.

The same configurations can also be used from headless mode:

```bash
uv run python main.py --headless --scenario "Protección de zona estratégica" --duration 30 --seed 1 --out run_output
```

The generated report contains:

- `timeseries.csv`: per-tick unit state, position, role, target and alerts.
- `summary.json`: scenario summary, distances, battery statistics, state durations and alert counts.
