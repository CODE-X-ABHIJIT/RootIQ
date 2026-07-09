# tests/test_daemonset_collector.py

from rootiq.collectors.daemonset import DaemonSetCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_daemonset_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = DaemonSetCollector()

    result = collector.run(k8s)

    print(result)

    assert result.success is True
    assert result.collector == "DaemonSetCollector"

    metric_names = [metric["metric"] for metric in result.metrics]

    assert "daemonset_count" in metric_names
    assert "desired_pods" in metric_names
    assert "ready_pods" in metric_names
    assert "available_pods" in metric_names

    assert isinstance(result.resources, list)
    assert isinstance(result.issues, list)
    assert isinstance(result.logs, list)

    for resource in result.resources:

        assert "name" in resource
        assert "namespace" in resource
        assert "desired_number_scheduled" in resource
        assert "current_number_scheduled" in resource
        assert "number_ready" in resource
        assert "number_available" in resource
        assert "number_unavailable" in resource
        assert "updated_number_scheduled" in resource
        assert "update_strategy" in resource
        assert "containers" in resource
        assert "conditions" in resource


if __name__ == "__main__":
    test_daemonset_collector()