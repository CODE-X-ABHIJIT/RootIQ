# tests/test_statefulset_collector.py

from rootiq.collectors.statefulset import StatefulSetCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_statefulset_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = StatefulSetCollector()

    result = collector.run(k8s)

    print(result)

    assert result.success is True
    assert result.collector == "StatefulSetCollector"

    metric_names = [metric["metric"] for metric in result.metrics]

    assert "statefulset_count" in metric_names
    assert "desired_replicas" in metric_names
    assert "ready_replicas" in metric_names

    assert isinstance(result.resources, list)
    assert isinstance(result.issues, list)
    assert isinstance(result.logs, list)

    for resource in result.resources:

        assert "name" in resource
        assert "namespace" in resource
        assert "desired_replicas" in resource
        assert "ready_replicas" in resource
        assert "containers" in resource
        assert "volume_claim_templates" in resource
        assert "conditions" in resource


if __name__ == "__main__":
    test_statefulset_collector()