from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class NetworkPolicyCollector(BaseCollector):
    enabled = True
    name = "NetworkPolicyCollector"
    resource_type = "networkpolicy"

    def collect(self, k8s):

        result = CollectResult(
            collector=self.name
        )

        try:

            policies = k8s.networkpolicies()

            pods = k8s.pods()

        except ApiException as e:

            result.success = False
            result.error = str(e)

            

        ingress_count = 0
        egress_count = 0

        default_deny = 0
        orphan_policies = 0

        for policy in policies:

            pod_selector = {}

            if (
                policy.spec.pod_selector
                and policy.spec.pod_selector.match_labels
            ):

                pod_selector = (
                    policy.spec.pod_selector.match_labels
                )

            #
            # Match Pods
            #

            matched_pods = []

            for pod in pods:

                if (
                    pod.metadata.namespace
                    != policy.metadata.namespace
                ):
                    continue

                labels = (
                    pod.metadata.labels
                    or {}
                )

                if all(
                    labels.get(k) == v
                    for k, v in pod_selector.items()
                ):

                    matched_pods.append(
                        pod.metadata.name
                    )

            if (
                pod_selector
                and not matched_pods
            ):

                orphan_policies += 1

            policy_types = (
                policy.spec.policy_types
                or []
            )

            if "Ingress" in policy_types:
                ingress_count += 1

            if "Egress" in policy_types:
                egress_count += 1

            if (
                policy_types
                and not policy.spec.ingress
                and not policy.spec.egress
            ):

                default_deny += 1

            #
            # Ingress
            #

            ingress_rules = []

            if policy.spec.ingress:

                for rule in policy.spec.ingress:

                    peers = []

                    if rule._from:

                        for peer in rule._from:

                            peers.append(
                                {
                                    "namespace_selector": (
                                        peer.namespace_selector.match_labels
                                        if (
                                            peer.namespace_selector
                                            and peer.namespace_selector.match_labels
                                        )
                                        else {}
                                        if peer.namespace_selector
                                        else None
                                    ),
                                    "pod_selector": (
                                        peer.pod_selector.match_labels
                                        if (
                                            peer.pod_selector
                                            and peer.pod_selector.match_labels
                                        )
                                        else {}
                                        if peer.pod_selector
                                        else None
                                    ),
                                    "ip_block": (
                                        {
                                            "cidr": peer.ip_block.cidr,
                                            "except": (
                                                peer.ip_block._except
                                                or []
                                            ),
                                        }
                                        if peer.ip_block
                                        else None
                                    ),
                                }
                            )

                    ports = []

                    if rule.ports:

                        for port in rule.ports:

                            ports.append(
                                {
                                    "protocol": port.protocol,
                                    "port": port.port,
                                }
                            )

                    ingress_rules.append(
                        {
                            "from": peers,
                            "ports": ports,
                        }
                    )
                                #
            # Egress
            #

            egress_rules = []

            if policy.spec.egress:

                for rule in policy.spec.egress:

                    peers = []

                    if rule.to:

                        for peer in rule.to:

                            peers.append(
                                {
                                    "namespace_selector": (
                                        peer.namespace_selector.match_labels
                                        if (
                                            peer.namespace_selector
                                            and peer.namespace_selector.match_labels
                                        )
                                        else {}
                                        if peer.namespace_selector
                                        else None
                                    ),
                                    "pod_selector": (
                                        peer.pod_selector.match_labels
                                        if (
                                            peer.pod_selector
                                            and peer.pod_selector.match_labels
                                        )
                                        else {}
                                        if peer.pod_selector
                                        else None
                                    ),
                                    "ip_block": (
                                        {
                                            "cidr": peer.ip_block.cidr,
                                            "except": (
                                                peer.ip_block._except
                                                or []
                                            ),
                                        }
                                        if peer.ip_block
                                        else None
                                    ),
                                }
                            )

                    ports = []

                    if rule.ports:

                        for port in rule.ports:

                            ports.append(
                                {
                                    "protocol": port.protocol,
                                    "port": port.port,
                                }
                            )

                    egress_rules.append(
                        {
                            "to": peers,
                            "ports": ports,
                        }
                    )

            result.resources.append(
                {
                    "name": policy.metadata.name,
                    "namespace": policy.metadata.namespace,
                    "uid": policy.metadata.uid,

                    "creation_timestamp": (
                        policy.metadata.creation_timestamp.isoformat()
                        if policy.metadata.creation_timestamp
                        else None
                    ),

                    "generation": (
                        policy.metadata.generation
                    ),

                    "labels": (
                        policy.metadata.labels
                        or {}
                    ),

                    "annotations": (
                        policy.metadata.annotations
                        or {}
                    ),

                    "pod_selector": pod_selector,

                    "matched_pods": matched_pods,

                    "policy_types": policy_types,

                    "ingress": ingress_rules,

                    "egress": egress_rules,
                }
            )

        #
        # Metrics
        #

        result.metrics.extend(
            [
                {
                    "metric": "networkpolicy_count",
                    "value": len(policies),
                },
                {
                    "metric": "ingress_network_policies",
                    "value": ingress_count,
                },
                {
                    "metric": "egress_network_policies",
                    "value": egress_count,
                },
                {
                    "metric": "default_deny_policies",
                    "value": default_deny,
                },
                {
                    "metric": "orphan_network_policies",
                    "value": orphan_policies,
                },
            ]
        )

        #
        # Logs
        #

        if orphan_policies:

            result.logs.append(
                {
                    "level": "warning",
                    "message": (
                        f"{orphan_policies} NetworkPolicies do not match any Pods."
                    ),
                }
            )

        if default_deny:

            result.logs.append(
                {
                    "level": "info",
                    "message": (
                        f"{default_deny} default deny NetworkPolicies detected."
                    ),
                }
            )

        return result