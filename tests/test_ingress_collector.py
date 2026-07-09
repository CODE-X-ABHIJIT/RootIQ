# tests/test_ingress_collector.py

from rootiq.collectors.ingress import IngressCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_ingress_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = IngressCollector()

    result = collector.run(k8s)

    print(result)

    assert result.success is True
    assert result.collector == "IngressCollector"

    metric_names = [metric["metric"] for metric in result.metrics]

    assert "ingress_count" in metric_names
    assert "rule_count" in metric_names
    assert "tls_entries" in metric_names

    assert isinstance(result.resources, list)
    assert isinstance(result.issues, list)
    assert isinstance(result.logs, list)

    for resource in result.resources:

        assert "name" in resource
        assert "namespace" in resource
        assert "uid" in resource
        assert "ingress_class" in resource
        assert "default_backend" in resource
        assert "rules" in resource
        assert "tls" in resource
        assert "addresses" in resource
        assert "labels" in resource
        assert "annotations" in resource
        assert "creation_timestamp" in resource


if __name__ == "__main__":
    test_ingress_collector()