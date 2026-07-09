from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class NetworkPolicyCollector(BaseCollector):

    name = "NetworkPolicyCollector"

    def collect(self, k8s):

        result = CollectResult(collector=self.name)

        try:

            if k8s.target.cluster_wide:

                policies = (
                    k8s.networking.list_network_policy_for_all_namespaces().items
                )

            else:

                policies = (
                    k8s.networking.list_namespaced_network_policy(
                        namespace=k8s.target.namespace
                    ).items
                )

            result.metrics.append(
                {
                    "metric": "networkpolicy_count",
                    "value": len(policies),
                }
            )

            ingress_count = 0
            egress_count = 0

            for policy in policies:

                policy_types = policy.spec.policy_types or []

                if "Ingress" in policy_types:
                    ingress_count += 1

                if "Egress" in policy_types:
                    egress_count += 1

                result.resources.append(
                    {
                        "name": policy.metadata.name,
                        "namespace": policy.metadata.namespace,
                        "pod_selector": (
                            policy.spec.pod_selector.match_labels or {}
                            if policy.spec.pod_selector
                            else {}
                        ),
                        "policy_types": policy_types,
                        "ingress_rules": len(policy.spec.ingress or []),
                        "egress_rules": len(policy.spec.egress or []),
                        "creation_timestamp": (
                            policy.metadata.creation_timestamp.isoformat()
                            if policy.metadata.creation_timestamp
                            else None
                        ),
                    }
                )

            result.metrics.extend(
                [
                    {
                        "metric": "ingress_network_policies",
                        "value": ingress_count,
                    },
                    {
                        "metric": "egress_network_policies",
                        "value": egress_count,
                    },
                ]
            )

        except ApiException as e:

            result.success = False
            result.error = str(e)

        return result