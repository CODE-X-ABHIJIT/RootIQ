from pprint import pprint

from rootiq.incident.enums import Severity
from rootiq.incident.service import IncidentService
from rootiq.incident.target import ClusterTarget


def test_incident_service():

    print("\n" + "=" * 70)
    print("Testing Incident Service")
    print("=" * 70)

    target = ClusterTarget(
        name="production",
        context="prod-context",
        namespace="payments",
        kubernetes_version="1.31",
        platform="EKS",
    )

    service = IncidentService()

    incident = service.create(
        title="Pods Pending",
        target=target,
        severity=Severity.CRITICAL,
    )

    print("\nIncident Created")
    print("-" * 70)
    pprint(incident.to_dict())

    print("\nLifecycle Demonstration")
    print("-" * 70)

    service.inspect(incident)
    print(f"Inspect   -> {incident.status.value}")

    service.diagnose(
        incident,
        root_cause="Insufficient CPU resources",
        confidence=95,
    )
    print(f"Diagnose  -> {incident.status.value}")

    service.start_repair(incident)
    print(f"Repair    -> {incident.status.value}")

    service.start_validation(incident)
    print(f"Validate  -> {incident.status.value}")

    service.resolve(incident)
    print(f"Resolve   -> {incident.status.value}")

    service.close(incident)
    print(f"Close     -> {incident.status.value}")

    print("\nRepository Information")
    print("-" * 70)
    print(f"Incident Exists : {service.exists(incident.incident_id)}")
    print(f"Total Incidents : {service.count()}")
    print(f"Incident List   : {service.list()}")

    latest = service.latest()

    print("\nLatest Incident")
    print("-" * 70)
    pprint(latest.to_dict())

    print("\nService Test Passed")


if __name__ == "__main__":
    test_incident_service()