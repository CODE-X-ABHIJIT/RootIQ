from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class NetworkPolicyRedundantRule(BaseRule):

    id = "NETPOL-010"

    name = "NetworkPolicyRedundant"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for i in range(len(resources)):

            left = resources[i]

            for j in range(i + 1, len(resources)):

                right = resources[j]

                #
                # Compare only within the same namespace
                #

                if (
                    left.get("namespace")
                    != right.get("namespace")
                ):
                    continue

                #
                # Compare selectors
                #

                if (
                    left.get("pod_selector", {})
                    != right.get("pod_selector", {})
                ):
                    continue

                #
                # Compare policy types
                #

                if sorted(
                    left.get("policy_types", [])
                ) != sorted(
                    right.get("policy_types", [])
                ):
                    continue

                #
                # Compare ingress
                #

                if (
                    left.get("ingress", [])
                    != right.get("ingress", [])
                ):
                    continue

                #
                # Compare egress
                #

                if (
                    left.get("egress", [])
                    != right.get("egress", [])
                ):
                    continue

                #
                # Duplicate policy detected
                #

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Low",
                        resource_type="NetworkPolicy",
                        resource_name=left["name"],
                        namespace=left["namespace"],
                        title="Redundant NetworkPolicy",
                        description=(
                            f"NetworkPolicy '{right['name']}' provides identical behavior."
                        ),
                        evidence={
                            "duplicate_policy": right["name"],
                        },
                        recommendation=(
                            "Merge or remove one of the duplicate NetworkPolicies."
                        ),
                    )
                )

        return result