from dataclasses import dataclass

from rootiq.incident.category import Category
from rootiq.incident.evidence import Evidence
from rootiq.incident.severity import Severity


@dataclass(init=False)
class Issue:

    id: str
    title: str
    description: str

    severity: Severity
    category: Category

    resource: str
    namespace: str | None

    recommendation: str |None

    evidence: list[Evidence]

    labels: dict

    #
    # Rule ID Prefix -> Category
    #

    CATEGORY_MAP = {
        "POD": Category.POD,
        "NODE": Category.NODE,
        "DEPLOY": Category.DEPLOYMENT,
        "RS": Category.REPLICASET,
        "STS": Category.STATEFULSET,
        "DS": Category.DAEMONSET,
        "SERVICE": Category.SERVICE,
        "INGRESS": Category.INGRESS,
        "PVC": Category.PVC,
        "PV": Category.PV,
        "SC": Category.STORAGECLASS,
        "CM": Category.CONFIGMAP,
        "SECRET": Category.SECRET,
    }

    def __init__(
        self,
        id=None,
        rule_id=None,
        title="",
        description="",
        severity=Severity.MEDIUM,
        category=None,
        resource="",
        namespace=None,
        recommendation=None,
        evidence=None,
        labels=None,
        metadata=None,
    ):

        #
        # Backward compatibility
        #

        self.id = id or rule_id

        #
        # Severity
        #

        if isinstance(severity, str):
            severity = Severity[severity.upper()]

        self.severity = severity

        #
        # Category
        #

        if category is None:

            rule = (self.id or "").upper()

            category = next(
                (
                    value
                    for prefix, value in self.CATEGORY_MAP.items()
                    if rule.startswith(prefix)
                ),
                Category.CLUSTER,
            )

        elif isinstance(category, str):

            category = Category[
                category.upper()
            ]

        self.category = category

        #
        # Details
        #

        self.title = title
        self.description = description
        self.resource = resource
        self.namespace = namespace
        self.recommendation = recommendation

        self.evidence = evidence or []

        #
        # Backward compatibility
        #

        self.labels = labels or metadata or {}