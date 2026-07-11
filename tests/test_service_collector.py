import json
from dataclasses import asdict

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
    assert result.collector == "ServiceCollector"

    metric_names = [
        metric["metric"]
        for metric in result.metrics
    ]

    assert "service_count" in metric_names
    assert "clusterip_services" in metric_names
    assert "nodeport_services" in metric_names
    assert "loadbalancer_services" in metric_names
    assert "externalname_services" in metric_names
    assert "headless_services" in metric_names
    assert "services_without_selector" in metric_names
    assert "services_without_endpoints" in metric_names

    assert isinstance(result.resources, list)
    assert isinstance(result.issues, list)
    assert isinstance(result.logs, list)

    if result.resources:

        service = result.resources[0]

        assert "name" in service
        assert "namespace" in service
        assert "uid" in service
        assert "type" in service

        assert "cluster_ip" in service
        assert "external_ip" in service
        assert "external_ips" in service
        assert "external_name" in service

        assert "selector" in service

        assert "ports" in service
        assert "endpoints" in service

        assert "load_balancer" in service

        assert "session_affinity" in service
        assert "session_affinity_config" in service

        assert "external_traffic_policy" in service
        assert "internal_traffic_policy" in service
        assert "health_check_node_port" in service

        assert "publish_not_ready_addresses" in service

        assert "ip_family_policy" in service
        assert "ip_families" in service

        assert (
            "allocate_load_balancer_node_ports"
            in service
        )

        assert "labels" in service
        assert "annotations" in service

        if service["ports"]:

            port = service["ports"][0]

            assert "name" in port
            assert "protocol" in port
            assert "port" in port
            assert "target_port" in port
            assert "node_port" in port
            assert "app_protocol" in port

        if service["load_balancer"]:

            assert "ingress" in service["load_balancer"]


if __name__ == "__main__":
    test_service_collector()