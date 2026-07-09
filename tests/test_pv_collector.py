from rootiq.collectors.pv import PVCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_pv_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = PVCollector()

    result = collector.run(k8s)

    print(result)

    assert result.success is True
    assert result.collector == "PVCollector"

    metrics = [m["metric"] for m in result.metrics]

    assert "pv_count" in metrics