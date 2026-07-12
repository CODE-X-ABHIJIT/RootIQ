from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class NetworkPolicyOrphanRule(BaseRule):

    id = "NETPOL-009"

    name = "NetworkPolicyOrphan"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for policy in resources:

            namespace = policy.get(
                "namespace"
            )

            name = policy.get(
                "name"
            )

            selector = policy.get(
                "pod_selector",
                {},
            )

            matched_pods = policy.get(
                "matched_pods",
                [],
            )

            #
            # Empty selector intentionally
            # matches every pod
            #

            if selector == {}:
                continue

            #
            # Invalid selector
            #

            if not isinstance(
                selector,
                dict,
            ):
                continue

            #
            # No matching pods
            #

            if len(matched_pods) == 0:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Medium",
                        resource_type="NetworkPolicy",
                        resource_name=name,
                        namespace=namespace,
                        title="NetworkPolicy matches no Pods",
                        description=(
                            "The podSelector does not match any Pods in the namespace."
                        ),
                        evidence={
                            "pod_selector": selector,
                        },
                        recommendation=(
                            "Verify the selector labels or remove the unused NetworkPolicy."
                        ),
                    )
                )

        return result