from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class NetworkPolicyNamespaceSelectorRule(BaseRule):

    id = "NETPOL-006"

    name = "NetworkPolicyNamespaceSelector"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for policy in resources:

            namespace = policy.get("namespace")
            name = policy.get("name")

            #
            # Check both ingress and egress peers
            #

            for direction in ("ingress", "egress"):

                rules = policy.get(
                    direction,
                    [],
                )

                peer_key = (
                    "from"
                    if direction == "ingress"
                    else "to"
                )

                for rule_index, rule in enumerate(rules):

                    peers = rule.get(
                        peer_key,
                        [],
                    )

                    for peer_index, peer in enumerate(peers):

                        selector = peer.get(
                            "namespace_selector"
                        )

                        if selector is None:
                            continue

                        #
                        # Empty selector
                        #

                        if selector == {}:

                            result.issues.append(
                                Issue(
                                    id=self.id,
                                    severity="Info",
                                    resource_type="NetworkPolicy",
                                    resource_name=name,
                                    namespace=namespace,
                                    title="Namespace selector matches all namespaces",
                                    description=(
                                        "An empty namespaceSelector matches every namespace."
                                    ),
                                    evidence={
                                        "direction": direction,
                                        "rule": rule_index,
                                        "peer": peer_index,
                                    },
                                    recommendation=(
                                        "Verify that allowing all namespaces is intentional."
                                    ),
                                )
                            )

                        #
                        # Invalid selector type
                        #

                        elif not isinstance(
                            selector,
                            dict,
                        ):

                            result.issues.append(
                                Issue(
                                    id=self.id,
                                    severity="High",
                                    resource_type="NetworkPolicy",
                                    resource_name=name,
                                    namespace=namespace,
                                    title="Invalid namespace selector",
                                    description=(
                                        "namespaceSelector must be a dictionary."
                                    ),
                                    evidence={
                                        "direction": direction,
                                        "rule": rule_index,
                                        "peer": peer_index,
                                        "namespace_selector": selector,
                                    },
                                    recommendation=(
                                        "Use valid Kubernetes label selectors."
                                    ),
                                )
                            )

        return result