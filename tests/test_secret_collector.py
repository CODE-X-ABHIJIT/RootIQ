from rootiq.collectors.secret import SecretCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_secret_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = SecretCollector()

    result = collector.run(k8s)

    print(result)

    assert result.success
    assert result.collector == "SecretCollector"

    metrics = [m["metric"] for m in result.metrics]

    assert "secret_count" in metrics


if __name__ == "__main__":
    test_secret_collector()