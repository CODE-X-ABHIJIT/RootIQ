from rootiq.collectors.hpa import HPACollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_hpa_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = HPACollector()

    result = collector.run(k8s)

    print(result)

    assert result.success
    assert result.collector == "HPACollector"

    metrics = [m["metric"] for m in result.metrics]

    assert "hpa_count" in metrics


if __name__ == "__main__":
    test_hpa_collector()