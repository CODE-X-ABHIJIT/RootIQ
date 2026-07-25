from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class NetworkPolicyRedundantRule(BaseRule):

    id = "NETPOL-010"

    name = "NetworkPolicyRedundant"

    resource_type = "networkpolicy"

    def evaluate(self, context: RuleContext):

        

        for i in range(len(context.resources)):

            left = context.resources[i]

            for j in range(i + 1, len(context.resources)):

                right = context.resources[j]

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

                context.report(
                        rule=self,
                    
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
                

        