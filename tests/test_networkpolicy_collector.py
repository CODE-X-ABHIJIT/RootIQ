from rootiq.collectors.networkpolicy import NetworkPolicyCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_networkpolicy_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = NetworkPolicyCollector()

    result = collector.run(k8s)

    print(result)

    assert result.success is True
    assert result.collector == "NetworkPolicyCollector"

    metrics = [m["metric"] for m in result.metrics]

    assert "networkpolicy_count" in metrics
    assert "ingress_network_policies" in metrics
    assert "egress_network_policies" in metrics

    assert isinstance(result.resources, list)


if __name__ == "__main__":
    test_networkpolicy_collector()