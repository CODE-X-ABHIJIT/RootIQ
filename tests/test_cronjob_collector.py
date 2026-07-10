from rootiq.collectors.cronjob import CronJobCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_cronjob_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = CronJobCollector()

    result = collector.run(k8s)

    print(result)

    assert result.success
    assert result.collector == "CronJobCollector"

    metrics = [m["metric"] for m in result.metrics]

    assert "cronjob_count" in metrics
    assert "suspended_cronjobs" in metrics

    assert isinstance(result.resources, list)


if __name__ == "__main__":
    test_cronjob_collector()