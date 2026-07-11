import json
from dataclasses import asdict

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
    assert result.collector == "NetworkPolicyCollector"

    metric_names = [
        metric["metric"]
        for metric in result.metrics
    ]

    assert "networkpolicy_count" in metric_names
    assert "ingress_network_policies" in metric_names
    assert "egress_network_policies" in metric_names
    assert "default_deny_policies" in metric_names
    assert "orphan_network_policies" in metric_names

    assert isinstance(result.resources, list)
    assert isinstance(result.issues, list)
    assert isinstance(result.logs, list)

    #
    # Resource Validation
    #

    for resource in result.resources:

        assert "name" in resource
        assert "namespace" in resource
        assert "uid" in resource

        assert "pod_selector" in resource
        assert "matched_pods" in resource

        assert "policy_types" in resource

        assert "ingress" in resource
        assert "egress" in resource

        assert "labels" in resource
        assert "annotations" in resource

        assert "generation" in resource
        assert "creation_timestamp" in resource

        #
        # Ingress Rules
        #

        for ingress in resource["ingress"]:

            assert "from" in ingress
            assert "ports" in ingress

            for peer in ingress["from"]:

                assert "namespace_selector" in peer
                assert "pod_selector" in peer
                assert "ip_block" in peer

            for port in ingress["ports"]:

                assert "protocol" in port
                assert "port" in port

        #
        # Egress Rules
        #

        for egress in resource["egress"]:

            assert "to" in egress
            assert "ports" in egress

            for peer in egress["to"]:

                assert "namespace_selector" in peer
                assert "pod_selector" in peer
                assert "ip_block" in peer

            for port in egress["ports"]:

                assert "protocol" in port
                assert "port" in port


if __name__ == "__main__":
    test_networkpolicy_collector()