# tests/test_service_collector.py

from rootiq.collectors.service import ServiceCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_service_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = ServiceCollector()

    result = collector.run(k8s)

    print(result)

    assert result.success is True
    assert result.collector == "ServiceCollector"

    metric_names = [metric["metric"] for metric in result.metrics]

    assert "service_count" in metric_names
    assert "clusterip_services" in metric_names
    assert "nodeport_services" in metric_names
    assert "loadbalancer_services" in metric_names
    assert "externalname_services" in metric_names

    assert isinstance(result.resources, list)
    assert isinstance(result.issues, list)
    assert isinstance(result.logs, list)

    for resource in result.resources:

        assert "name" in resource
        assert "namespace" in resource
        assert "uid" in resource
        assert "type" in resource
        assert "cluster_ip" in resource
        assert "external_ips" in resource
        assert "selector" in resource
        assert "session_affinity" in resource
        assert "ip_family_policy" in resource
        assert "ports" in resource
        assert "load_balancer" in resource
        assert "labels" in resource
        assert "annotations" in resource


if __name__ == "__main__":
    test_service_collector()