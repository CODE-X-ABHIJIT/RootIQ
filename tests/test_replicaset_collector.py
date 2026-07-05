from rootiq.collectors.replicaset import ReplicaSetCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_replicaset_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True
    )

    k8s = KubernetesClient(target)

    collector = ReplicaSetCollector()

    result = collector.run(k8s)

    print(result)

    assert result.success is True
    assert result.collector == "ReplicaSetCollector"

    # must have metric
    metric_names = [m["metric"] for m in result.metrics]

    assert "replicaset_count" in metric_names
    assert "total_desired_replicas" in metric_names
    assert "total_ready_replicas" in metric_names

    # resources should exist if cluster has workloads
    assert isinstance(result.resources, list)

if __name__ == "__main__":
    test_replicaset_collector()