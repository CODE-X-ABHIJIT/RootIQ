from rootiq.collectors.job import JobCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_job_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = JobCollector()

    result = collector.run(k8s)

    print(result)

    assert result.success
    assert result.collector == "JobCollector"

    metrics = [m["metric"] for m in result.metrics]

    assert "job_count" in metrics
    assert "successful_jobs" in metrics
    assert "failed_jobs" in metrics
    assert "active_jobs" in metrics

    assert isinstance(result.resources, list)


if __name__ == "__main__":
    test_job_collector()