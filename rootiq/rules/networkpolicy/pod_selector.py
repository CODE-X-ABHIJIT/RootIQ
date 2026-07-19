from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class NetworkPolicyPodSelectorRule(BaseRule):

    id = "NETPOL-001"

    name = "NetworkPolicyPodSelector"

    resource_type = "networkpolicy"

    def evaluate(self, ctx: RuleContext):

        

        for policy in ctx.resources:

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

                ctx.report(
                        rule=self,
                    
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
                

            #
            # Invalid selector
            #

            elif not isinstance(selector, dict):

                ctx.report(
                        rule=self,
                    
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
                

        