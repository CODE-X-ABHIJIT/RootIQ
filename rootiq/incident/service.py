from pathlib import Path

from rootiq.incident.enums import (
    IncidentStatus,
    Severity,
)
from rootiq.incident.models import Incident
from rootiq.incident.repository import IncidentRepository
from rootiq.incident.target import ClusterTarget


class IncidentService:
    """
    Service layer responsible for managing the lifecycle
    of an Incident.
    """

    def __init__(self):

        self.repository = IncidentRepository()

    # ==========================================================
    # Incident ID Generation
    # ==========================================================

    def _generate_incident_id(self) -> str:
        """
        Generates sequential IDs.

        Example:
            INC-000001
            INC-000002
        """

        counter_file = self.repository.base_path / ".counter"

        if not counter_file.exists():
            counter_file.write_text("0")

        current = int(counter_file.read_text().strip())

        current += 1

        counter_file.write_text(str(current))

        return f"INC-{current:06d}"

    # ==========================================================
    # CRUD Operations
    # ==========================================================

    def create(
        self,
        title: str,
        target: ClusterTarget,
        severity: Severity,
    ) -> Incident:

        incident = Incident(
            incident_id=self._generate_incident_id(),
            title=title,
            target=target,
            severity=severity,
            status=IncidentStatus.NEW,
        )

        self.repository.save(incident)

        return incident

    def load(
        self,
        incident_id: str,
    ) -> Incident:

        return self.repository.load(incident_id)

    def save(
        self,
        incident: Incident,
    ) -> None:

        incident.touch()

        self.repository.save(incident)

    def delete(
        self,
        incident_id: str,
    ) -> None:

        self.repository.delete(incident_id)

    # ==========================================================
    # Lifecycle Operations
    # ==========================================================

    def inspect(
        self,
        incident: Incident,
    ) -> None:

        incident.set_status(
            IncidentStatus.INSPECTING
        )

        self.save(incident)

    def diagnose(
        self,
        incident: Incident,
        root_cause: str,
        confidence: int,
    ) -> None:

        incident.set_root_cause(
            root_cause,
            confidence,
        )

        incident.set_status(
            IncidentStatus.DIAGNOSED
        )

        self.save(incident)

    def start_repair(
        self,
        incident: Incident,
    ) -> None:

        incident.set_status(
            IncidentStatus.REPAIRING
        )

        self.save(incident)

    def start_validation(
        self,
        incident: Incident,
    ) -> None:

        incident.set_status(
            IncidentStatus.VALIDATED
        )

        self.save(incident)

    def resolve(
        self,
        incident: Incident,
    ) -> None:

        incident.set_status(
            IncidentStatus.RESOLVED
        )

        self.save(incident)

    def close(
        self,
        incident: Incident,
    ) -> None:

        incident.set_status(
            IncidentStatus.CLOSED
        )

        self.save(incident)

    # ==========================================================
    # Repository Helpers
    # ==========================================================

    def exists(
        self,
        incident_id: str,
    ) -> bool:

        return self.repository.exists(
            incident_id
        )

    def latest(self) -> Incident | None:

        return self.repository.latest()

    def list(self) -> list[str]:

        return self.repository.list_incidents()

    def count(self) -> int:

        return self.repository.count()