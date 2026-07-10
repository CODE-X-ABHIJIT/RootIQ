import json
from dataclasses import asdict

from rootiq.collectors.deployment import DeploymentCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_deployment_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = DeploymentCollector()

    result = collector.run(k8s)

    #
    # Pretty JSON Output
    #

    print(
        json.dumps(
            asdict(result),
            indent=4,
            default=str,
        )
    )

    #
    # Assertions
    #

    assert result.success is True
    assert result.collector == "DeploymentCollector"

    metric_names = [m["metric"] for m in result.metrics]

    assert "deployment_count" in metric_names
    assert "healthy_deployments" in metric_names
    assert "unhealthy_deployments" in metric_names
    assert "fully_available_deployments" in metric_names
    assert "partially_available_deployments" in metric_names
    assert "failed_rollouts" in metric_names
    assert "desired_replicas" in metric_names
    assert "ready_replicas" in metric_names
    assert "available_replicas" in metric_names
    assert "updated_replicas" in metric_names
    assert "unavailable_replicas" in metric_names

    assert isinstance(result.resources, list)

    if result.resources:

        deployment = result.resources[0]

        assert "containers" in deployment
        assert "conditions" in deployment
        assert "strategy" in deployment
        assert "selector" in deployment
        assert "replicasets" in deployment
        assert "hpa" in deployment
        assert "desired_replicas" in deployment
        assert "ready_replicas" in deployment
        assert "available_replicas" in deployment

        if deployment["containers"]:

            container = deployment["containers"][0]

            assert "name" in container
            assert "image" in container
            assert "resources" in container
            assert "readiness_probe" in container
            assert "liveness_probe" in container
            assert "startup_probe" in container
            assert "ports" in container
            assert "env" in container
            assert "volume_mounts" in container


if __name__ == "__main__":
    test_deployment_collector()