from pprint import pprint

from rootiq.incident.enums import Severity, IncidentStatus
from rootiq.incident.models import Incident
from rootiq.incident.target import ClusterTarget


def test_incident_model():
    print("\n" + "=" * 70)
    print("Testing Incident Model")
    print("=" * 70)

    target = ClusterTarget(
        name="production",
        context="prod-context",
        namespace="payments",
        kubernetes_version="1.31",
        platform="EKS",
    )

    incident = Incident(
        incident_id="INC-000001",
        title="Pods Pending",
        target=target,
        severity=Severity.CRITICAL,
        status=IncidentStatus.NEW,
    )

    incident.add_resource("deployment/payment-api")
    incident.add_resource("pod/payment-api-5c7d4")

    incident.add_recommendation(
        "Verify node resources and scheduler events."
    )

    incident.add_label("team", "payments")
    incident.add_tag("scheduler")

    print("\nIncident")
    print("-" * 70)
    print(incident)

    print("\nSerialized Output")
    print("-" * 70)
    pprint(incident.to_dict())

    print("\nModel Test Passed")


if __name__ == "__main__":
    test_incident_model()