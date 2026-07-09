from rootiq.collectors.storageclass import StorageClassCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_storageclass_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = StorageClassCollector()

    result = collector.run(k8s)

    print(result)

    assert result.success is True
    assert result.collector == "StorageClassCollector"

    metrics = [m["metric"] for m in result.metrics]

    assert "storageclass_count" in metrics

    assert isinstance(result.resources, list)
    
if __name__ == "__main__":
    test_storageclass_collector()