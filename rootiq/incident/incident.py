from dataclasses import dataclass, field
from datetime import datetime

from rootiq.incident.issue import Issue


@dataclass
class Incident:
    """
    Represents a correlated incident in a Kubernetes cluster.
    """

    id: str

    cluster: str

    title: str

    severity: str

    status: str = "OPEN"

    category: str = "General"

    root_cause: str | None = None

    recommendation: str | None = None

    issues: list[Issue] = field(default_factory=list)

    affected_resources: list[dict] = field(default_factory=list)

    evidence: list[dict] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.utcnow)

    updated_at: datetime = field(default_factory=datetime.utcnow)

    # ==========================================
    # Helpers
    # ==========================================

    def add_issue(
        self,
        issue: Issue,
    ):

        self.issues.append(issue)

        self.updated_at = datetime.utcnow()

    def add_resource(
        self,
        resource: dict,
    ):

        self.affected_resources.append(resource)

    def add_evidence(
        self,
        evidence: dict,
    ):

        self.evidence.append(evidence)

    @property
    def total_issues(self):

        return len(self.issues)