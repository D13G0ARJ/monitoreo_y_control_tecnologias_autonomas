# Reusable Scenario Fixtures

These JSON files use the same shape as `ScenarioApplicationConfig` and can be loaded from the GUI with `Cargar configuración`.

- `zone_protection_baseline.json`: defensive patrol around the protected zone.
- `recon_area_baseline.json`: reconnaissance route through observation points.
- `combined_swarm_demo.json`: two-swarm patrol/reconnaissance demonstration.
- `rtb_low_battery_demo.json`: low-battery threshold tuned to exercise return-to-base behavior quickly.
- `proximity_alert_demo.json`: small two-unit setup for proximity alert checks.

The automated coverage for these fixtures lives in `tests/test_reusable_scenarios.py`.
