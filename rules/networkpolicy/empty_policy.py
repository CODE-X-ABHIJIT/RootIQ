from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class NetworkPolicyEmptyRule(BaseRule):

    id = "NETPOL-005"

    name = "NetworkPolicyEmpty"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for policy in resources:

            namespace = policy.get("namespace")
            name = policy.get("name")

            ingress = policy.get(
                "ingress",
                [],
            )

            egress = policy.get(
                "egress",
                [],
            )

            policy_types = policy.get(
                "policy_types",
                [],
            )

            #
            # Completely empty NetworkPolicy
            #

            if (
                not ingress
                and not egress
                and not policy_types
            ):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="High",
                        resource_type="NetworkPolicy",
                        resource_name=name,
                        namespace=namespace,
                        title="Empty NetworkPolicy",
                        description=(
                            "NetworkPolicy does not define policyTypes, ingress rules, or egress rules."
                        ),
                        evidence={},
                        recommendation=(
                            "Configure at least one policy type and the required ingress or egress rules."
                        ),
                    )
                )

            #
            # PolicyTypes present but no rules
            #

            elif (
                not ingress
                and not egress
            ):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Info",
                        resource_type="NetworkPolicy",
                        resource_name=name,
                        namespace=namespace,
                        title="Default deny NetworkPolicy",
                        description=(
                            "The NetworkPolicy contains policyTypes but no ingress or egress rules."
                        ),
                        evidence={
                            "policy_types": policy_types,
                        },
                        recommendation=(
                            "Verify that a default deny policy is intentional."
                        ),
                    )
                )

        return result