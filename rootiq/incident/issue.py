from dataclasses import dataclass, field

from rootiq.incident.category import Category
from rootiq.incident.evidence import Evidence
from rootiq.incident.severity import Severity


@dataclass
class Issue:

    id: str

    title: str

    description: str

    severity: Severity

    category: Category

    resource: str

    namespace: str | None = None

    recommendation: str | None = None

    evidence: list[Evidence] = field(default_factory=list)

    labels: dict = field(default_factory=dict)