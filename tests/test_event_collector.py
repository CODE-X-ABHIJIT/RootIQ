from rootiq.collectors.event import EventCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_event_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = EventCollector()

    result = collector.run(k8s)

    print(result)

    assert result.success is True
    assert result.collector == "EventCollector"

    metrics = [m["metric"] for m in result.metrics]

    assert "event_count" in metrics
    assert "warning_events" in metrics
    assert "normal_events" in metrics

    assert isinstance(result.resources, list)


if __name__ == "__main__":
    test_event_collector()