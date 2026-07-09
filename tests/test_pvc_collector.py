# tests/test_pvc_collector.py

from rootiq.collectors.pvc import PVCCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_pvc_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = PVCCollector()

    result = collector.run(k8s)

    print(result)

    assert result.success is True
    assert result.collector == "PVCCollector"

    metric_names = [m["metric"] for m in result.metrics]

    assert "pvc_count" in metric_names
    assert "bound_pvcs" in metric_names
    assert "pending_pvcs" in metric_names
    assert "lost_pvcs" in metric_names

    assert isinstance(result.resources, list)
    assert isinstance(result.issues, list)
    assert isinstance(result.logs, list)

    for resource in result.resources:

        assert "name" in resource
        assert "namespace" in resource
        assert "phase" in resource
        assert "volume_name" in resource
        assert "storage_class" in resource
        assert "access_modes" in resource
        assert "volume_mode" in resource
        assert "capacity" in resource
        assert "requests" in resource


if __name__ == "__main__":
    test_pvc_collector()