from pprint import pprint

from rootiq.incident.enums import Severity, IncidentStatus
from rootiq.incident.models import Incident
from rootiq.incident.repository import IncidentRepository
from rootiq.incident.target import ClusterTarget


def test_repository():
    print("\n" + "=" * 70)
    print("Testing Incident Repository")
    print("=" * 70)

    repository = IncidentRepository()

    target = ClusterTarget(
        name="production",
        context="prod-context",
        namespace="payments",
        kubernetes_version="1.31",
        platform="EKS",
    )

    incident = Incident(
        incident_id="INC-TEST-001",
        title="Pods Pending",
        target=target,
        severity=Severity.CRITICAL,
        status=IncidentStatus.NEW,
    )

    print("\nSaving Incident...")
    repository.save(incident)
    print("Incident saved successfully.")

    print("\nChecking Incident Exists...")
    exists = repository.exists(incident.incident_id)
    print(f"Exists: {exists}")

    print("\nLoading Incident...")
    loaded = repository.load(incident.incident_id)

    print("-" * 70)
    pprint(loaded.to_dict())

    print("\nListing Incidents...")
    incidents = repository.list_incidents()
    pprint(incidents)

    print("\nTotal Incidents...")
    print(repository.count())

    print("\nLatest Incident...")
    latest = repository.latest()
    pprint(latest.to_dict())

    print("\nDeleting Incident...")
    repository.delete(incident.incident_id)

    print(f"Exists After Delete: {repository.exists(incident.incident_id)}")

    print("\nRepository Test Passed")


if __name__ == "__main__":
    test_repository()