import json
from dataclasses import asdict

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
    # Basic Validation
    #

    assert result.success is True
    assert result.collector == "IngressCollector"

    metric_names = [
        metric["metric"]
        for metric in result.metrics
    ]

    #
    # Metrics
    #

    assert "ingress_count" in metric_names
    assert "rule_count" in metric_names
    assert "path_count" in metric_names
    assert "tls_entries" in metric_names
    assert "tls_enabled_ingresses" in metric_names
    assert "tls_disabled_ingresses" in metric_names
    assert "ingresses_with_loadbalancer" in metric_names
    assert "ingresses_without_loadbalancer" in metric_names
    assert "nginx_ingress_class" in metric_names
    assert "custom_ingress_class" in metric_names

    #
    # Result Objects
    #

    assert isinstance(result.resources, list)
    assert isinstance(result.issues, list)
    assert isinstance(result.logs, list)

    #
    # Resource Validation
    #

    if result.resources:

        resource = result.resources[0]

        assert "name" in resource
        assert "namespace" in resource
        assert "uid" in resource
        assert "ingress_class" in resource
        assert "default_backend" in resource
        assert "rules" in resource
        assert "tls" in resource
        assert "load_balancer" in resource
        assert "labels" in resource
        assert "annotations" in resource
        assert "creation_timestamp" in resource

        #
        # Rules
        #

        if resource["rules"]:

            rule = resource["rules"][0]

            assert "host" in rule
            assert "paths" in rule

            if rule["paths"]:

                path = rule["paths"][0]

                assert "path" in path
                assert "path_type" in path
                assert "backend" in path

        #
        # Default Backend
        #

        if resource["default_backend"]:

            backend = resource["default_backend"]

            assert "service" in backend

            service = backend["service"]

            assert "name" in service
            assert "port" in service

        #
        # TLS
        #

        if resource["tls"]:

            tls = resource["tls"][0]

            assert "hosts" in tls
            assert "secret_name" in tls

        #
        # LoadBalancer
        #

        if resource["load_balancer"]:

            lb = resource["load_balancer"][0]

            assert "ip" in lb
            assert "hostname" in lb


if __name__ == "__main__":
    test_ingress_collector()