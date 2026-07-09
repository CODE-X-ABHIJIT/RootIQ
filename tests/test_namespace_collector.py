from rootiq.collectors.namespace import NamespaceCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_namespace_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = NamespaceCollector()

    result = collector.run(k8s)

    print(result)

    assert result.success is True
    assert result.collector == "NamespaceCollector"

    metrics = [m["metric"] for m in result.metrics]

    assert "namespace_count" in metrics
    assert "active_namespaces" in metrics
    assert "terminating_namespaces" in metrics

    assert isinstance(result.resources, list)

if __name__ == "__main__":
    test_namespace_collector()