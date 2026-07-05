from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any

from rootiq.incident.enums import Severity, IncidentStatus
from rootiq.incident.target import ClusterTarget


# --------------------------------------------------
# Evidence
# --------------------------------------------------

@dataclass
class Evidence:
    logs: list[Any] = field(default_factory=list)
    events: list[Any] = field(default_factory=list)
    metrics: list[Any] = field(default_factory=list)
    resources: list[Any] = field(default_factory=list)


# --------------------------------------------------
# Repair History
# --------------------------------------------------

@dataclass
class RepairAction:
    action: str
    command: str
    status: str
    duration: str
    timestamp: str


# --------------------------------------------------
# Validation Result
# --------------------------------------------------

@dataclass
class ValidationResult:
    checks: dict[str, str] = field(default_factory=dict)
    overall_status: str = "UNKNOWN"


# --------------------------------------------------
# Incident
# --------------------------------------------------

@dataclass
class Incident:

    # ---------- Basic Information ----------

    incident_id: str
    title: str
    target: ClusterTarget

    severity: Severity
    status: IncidentStatus

    # ---------- Timeline ----------

    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    updated_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    # ---------- Diagnosis ----------

    root_cause: str = ""
    confidence: int = 0

    # ---------- Kubernetes Resources ----------

    affected_resources: list[str] = field(default_factory=list)

    # ---------- Collected Evidence ----------

    evidence: Evidence = field(default_factory=Evidence)

    # ---------- Recovery ----------

    repairs: list[RepairAction] = field(default_factory=list)

    validation: ValidationResult = field(
        default_factory=ValidationResult
    )

    recommendations: list[str] = field(default_factory=list)

    # ---------- Metadata ----------

    labels: dict[str, str] = field(default_factory=dict)

    annotations: dict[str, str] = field(default_factory=dict)

    tags: list[str] = field(default_factory=list)

    # ==========================================================
    # Business Methods
    # ==========================================================

    def set_status(self, status: IncidentStatus):
        self.status = status
        self.touch()

    def set_root_cause(
        self,
        cause: str,
        confidence: int,
    ):
        self.root_cause = cause
        self.confidence = confidence
        self.touch()

    def add_resource(self, resource: str):
        if resource not in self.affected_resources:
            self.affected_resources.append(resource)
            self.touch()

    def add_recommendation(self, recommendation: str):
        if recommendation not in self.recommendations:
            self.recommendations.append(recommendation)
            self.touch()

    def add_repair(self, repair: RepairAction):
        self.repairs.append(repair)
        self.touch()

    def add_log(self, log: Any):
        self.evidence.logs.append(log)
        self.touch()

    def add_event(self, event: Any):
        self.evidence.events.append(event)
        self.touch()

    def add_metric(self, metric: Any):
        self.evidence.metrics.append(metric)
        self.touch()

    def add_resource_evidence(self, resource: Any):
        self.evidence.resources.append(resource)
        self.touch()

    def add_label(self, key: str, value: str):
        self.labels[key] = value
        self.touch()

    def add_annotation(self, key: str, value: str):
        self.annotations[key] = value
        self.touch()

    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)
            self.touch()

    def touch(self):
        self.updated_at = datetime.now().isoformat()

    # ==========================================================
    # Serialization
    # ==========================================================

    def to_dict(self) -> dict:

        data = asdict(self)

        data["severity"] = self.severity.value
        data["status"] = self.status.value

        return data