import json
from dataclasses import asdict

from rootiq.collectors.pods import PodCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_pod_collector():

    target = ClusterTarget(
        name="FinOps Lab",
        context="kind-finops-lab",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = PodCollector()

    result = collector.run(k8s)

    # Pretty JSON Output
    print(
        json.dumps(
            asdict(result),
            indent=4,
            default=str
        )
    )

    assert result.success is True
    assert result.collector == "PodCollector"

    metric_names = [m["metric"] for m in result.metrics]

    assert "pod_count" in metric_names
    assert "running_pods" in metric_names
    assert "pending_pods" in metric_names
    assert "failed_pods" in metric_names
    assert "succeeded_pods" in metric_names

    assert isinstance(result.resources, list)

    if result.resources:

        pod = result.resources[0]

        assert "containers" in pod
        assert "conditions" in pod
        assert "init_containers" in pod
        assert "qos_class" in pod
        assert "owner" in pod

        if pod["containers"]:

            container = pod["containers"][0]

            assert "state" in container
            assert "last_state" in container
            assert "resources" in container
            assert "readiness_probe" in container
            assert "liveness_probe" in container
            assert "startup_probe" in container
            assert "restart_count" in container
            assert "image" in container


if __name__ == "__main__":
    test_pod_collector()