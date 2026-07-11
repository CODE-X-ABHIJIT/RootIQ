from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class NetworkPolicyPodSelectorRule(BaseRule):

    id = "NETPOL-001"

    name = "NetworkPolicyPodSelector"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for policy in resources:

            namespace = policy.get("namespace")
            name = policy.get("name")

            selector = policy.get(
                "pod_selector",
                {}
            )

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
                        title="Policy applies to all pods",
                        description=(
                            "An empty podSelector matches every pod in the namespace."
                        ),
                        evidence={},
                        recommendation=(
                            "Verify this broad scope is intentional."
                        ),
                    )
                )

            #
            # Invalid selector
            #

            elif not isinstance(selector, dict):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="High",
                        resource_type="NetworkPolicy",
                        resource_name=name,
                        namespace=namespace,
                        title="Invalid podSelector",
                        description=(
                            "podSelector should be a dictionary of labels."
                        ),
                        evidence={
                            "pod_selector": selector,
                        },
                        recommendation=(
                            "Configure podSelector using valid label key/value pairs."
                        ),
                    )
                )

        return result