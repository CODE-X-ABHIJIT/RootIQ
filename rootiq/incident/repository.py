import json
from pathlib import Path

from rootiq.incident.enums import (
    Severity,
    IncidentStatus,
)
from rootiq.incident.models import (
    Incident,
    Evidence,
    RepairAction,
    ValidationResult,
)
from rootiq.incident.target import ClusterTarget
from rootiq.incident.exceptions import IncidentNotFoundError


class IncidentRepository:
    """
    Repository responsible for persisting and
    retrieving Incident objects.
    """

    def __init__(self, base_path: str = "incidents"):

        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    # ==========================================================
    # Directory Management
    # ==========================================================

    def create_incident_directory(
        self,
        incident_id: str,
    ) -> Path:

        incident_path = self.base_path / incident_id

        incident_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Future directories

        (incident_path / "evidence").mkdir(
            exist_ok=True
        )

        (incident_path / "repair").mkdir(
            exist_ok=True
        )

        (incident_path / "validation").mkdir(
            exist_ok=True
        )

        (incident_path / "reports").mkdir(
            exist_ok=True
        )

        return incident_path

    # ==========================================================
    # CRUD Operations
    # ==========================================================

    def save(self, incident: Incident) -> None:

        incident_path = self.create_incident_directory(
            incident.incident_id
        )

        file_path = incident_path / "incident.json"

        with open(
            file_path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                incident.to_dict(),
                f,
                indent=4,
            )

    def load(
        self,
        incident_id: str,
    ) -> Incident:

        file_path = (
            self.base_path
            / incident_id
            / "incident.json"
        )

        if not file_path.exists():
            raise IncidentNotFoundError(
                f"Incident '{incident_id}' not found."
            )

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as f:

            data = json.load(f)

        target = ClusterTarget(
            **data["target"]
        )

        evidence = Evidence(
            **data["evidence"]
        )

        validation = ValidationResult(
            **data["validation"]
        )

        repairs = [
            RepairAction(**repair)
            for repair in data["repairs"]
        ]

        incident = Incident(
            incident_id=data["incident_id"],
            title=data["title"],
            target=target,
            severity=Severity(data["severity"]),
            status=IncidentStatus(data["status"]),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            root_cause=data["root_cause"],
            confidence=data["confidence"],
            affected_resources=data["affected_resources"],
            evidence=evidence,
            repairs=repairs,
            validation=validation,
            recommendations=data["recommendations"],
            labels=data.get("labels", {}),
            annotations=data.get("annotations", {}),
            tags=data.get("tags", []),
        )

        return incident

    def delete(
        self,
        incident_id: str,
    ) -> None:

        incident_path = self.base_path / incident_id

        if not incident_path.exists():
            raise IncidentNotFoundError(
                f"Incident '{incident_id}' not found."
            )

        for item in incident_path.rglob("*"):

            if item.is_file():
                item.unlink()

        for item in sorted(
            incident_path.rglob("*"),
            reverse=True,
        ):

            if item.is_dir():
                item.rmdir()

        incident_path.rmdir()

    # ==========================================================
    # Query Operations
    # ==========================================================

    def exists(
        self,
        incident_id: str,
    ) -> bool:

        return (
            self.base_path
            / incident_id
            / "incident.json"
        ).exists()

    def count(self) -> int:

        return len(
            [
                item
                for item in self.base_path.iterdir()
                if item.is_dir()
                and item.name.startswith("INC-")
            ]
        )

    def list_incidents(self) -> list[str]:

        incidents = [
            item.name
            for item in self.base_path.iterdir()
            if item.is_dir()
            and item.name.startswith("INC-")
        ]

        incidents.sort()

        return incidents

    def latest(self) -> Incident | None:

        incidents = self.list_incidents()

        if not incidents:
            return None

        return self.load(incidents[-1])