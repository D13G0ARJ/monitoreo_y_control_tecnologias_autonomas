from __future__ import annotations

from dataclasses import dataclass

from app.config import settings
from app.domain.autonomous_unit import AutonomousUnit


@dataclass
class SwarmSummary:
    swarm_id: str
    swarm_name: str
    swarm_role: str
    unit_count: int
    general_status: str


class SwarmService:
    def assign_swarms(
        self,
        units: list[AutonomousUnit],
        scenario_name: str,
        swarm_count: int,
        distribution: str,
    ) -> None:
        if not units:
            return

        normalized_distribution = distribution.lower()

        if scenario_name == settings.SCENARIO_ZONE_PROTECTION:
            self._assign_uniform(units, "E1", "Enjambre 1", settings.ROLE_PATROL)
            return

        if scenario_name == settings.SCENARIO_RECON_AREA:
            self._assign_uniform(units, "E1", "Enjambre 1", settings.ROLE_RECON)
            return

        if swarm_count <= 1:
            split_index = len(units)
        elif normalized_distribution == "mitad y mitad":
            split_index = max(1, len(units) // 2)
        else:
            split_index = max(1, round(len(units) * 0.5))

        self._assign_uniform(units[:split_index], "E1", "Enjambre 1", settings.ROLE_PATROL)
        self._assign_uniform(units[split_index:], "E2", "Enjambre 2", settings.ROLE_RECON)

    def summarize(self, units: list[AutonomousUnit]) -> list[SwarmSummary]:
        grouped: dict[str, list[AutonomousUnit]] = {}
        for unit in units:
            grouped.setdefault(unit.swarm_id, []).append(unit)

        summaries: list[SwarmSummary] = []
        for swarm_id in sorted(grouped.keys()):
            swarm_units = grouped[swarm_id]
            first_unit = swarm_units[0]
            summaries.append(
                SwarmSummary(
                    swarm_id=swarm_id,
                    swarm_name=first_unit.swarm_name,
                    swarm_role=first_unit.swarm_role,
                    unit_count=len(swarm_units),
                    general_status=self._resolve_general_status(swarm_units),
                )
            )
        return summaries

    def build_swarm_overview(self, units: list[AutonomousUnit]) -> str:
        summaries = self.summarize(units)
        if not summaries:
            return "Sin enjambres activos"
        return " | ".join(
            f"{summary.swarm_id}: {summary.swarm_role.title()}"
            for summary in summaries
        )

    @staticmethod
    def _assign_uniform(units: list[AutonomousUnit], swarm_id: str, swarm_name: str, swarm_role: str) -> None:
        for unit in units:
            unit.swarm_id = swarm_id
            unit.swarm_name = swarm_name
            unit.swarm_role = swarm_role
            if unit.task_label == settings.TASK_AUTOMATIC:
                unit.role = swarm_role

    @staticmethod
    def _resolve_general_status(units: list[AutonomousUnit]) -> str:
        if any(unit.state == settings.STATUS_SIN_BATERIA for unit in units):
            return "fuera de operación"
        if any(unit.state == settings.STATUS_CRITICO for unit in units):
            return "crítico"
        if any(unit.state == settings.STATUS_BATERIA_BAJA for unit in units):
            return "advertencia"
        if any(unit.state in {settings.STATUS_PATRULLANDO, settings.STATUS_RECONOCIMIENTO, settings.STATUS_EN_RUTA} for unit in units):
            return "activo"
        return "estable"
