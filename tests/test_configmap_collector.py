from rootiq.collectors.configmap import ConfigMapCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_configmap_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = ConfigMapCollector()

    result = collector.run(k8s)

    print(result)

    assert result.success is True
    assert result.collector == "ConfigMapCollector"

    metric_names = [m["metric"] for m in result.metrics]

    assert "configmap_count" in metric_names
    assert "configmap_keys" in metric_names

    assert isinstance(result.resources, list)


if __name__ == "__main__":
    test_configmap_collector()