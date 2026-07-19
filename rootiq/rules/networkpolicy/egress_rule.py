from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class NetworkPolicyEgressRule(BaseRule):

    id = "NETPOL-004"

    name = "NetworkPolicyEgress"

    resource_type = "networkpolicy"

    def evaluate(self, ctx: RuleContext):

        

        for policy in ctx.resources:

            namespace = policy.get("namespace")
            name = policy.get("name")

            policy_types = policy.get(
                "policy_types",
                [],
            )

            egress = policy.get(
                "egress",
                [],
            )

            #
            # Egress policy without rules
            #

            if (
                "Egress" in policy_types
                and not egress
            ):

                ctx.report(
                            rule=self,
                    
                        id=self.id,
                        severity="Info",
                        resource_type="NetworkPolicy",
                        resource_name=name,
                        namespace=namespace,
                        title="Egress traffic denied",
                        description=(
                            "Egress policy contains no egress rules. "
                            "This denies all outgoing traffic from selected pods."
                        ),
                        evidence={},
                        recommendation=(
                            "Verify that a default deny policy is intended."
                        ),
                    )
                

            #
            # Validate egress rules
            #

            for index, rule in enumerate(egress):

                peers = rule.get(
                    "to",
                    [],
                )

                ports = rule.get(
                    "ports",
                    [],
                )

                #
                # Rule allows all destinations
                #

                if not peers:

                    ctx.report(
                            rule=self,
                        
                            id=self.id,
                            severity="Low",
                            resource_type="NetworkPolicy",
                            resource_name=name,
                            namespace=namespace,
                            title="Egress rule allows all destinations",
                            description=(
                                "Egress rule has no destination restrictions."
                            ),
                            evidence={
                                "rule": index,
                            },
                            recommendation=(
                                "Restrict allowed destinations where possible."
                            ),
                        )
                    

                #
                # Rule allows all ports
                #

                if not ports:

                    ctx.report(
                            rule=self,
                        
                            id=self.id,
                            severity="Low",
                            resource_type="NetworkPolicy",
                            resource_name=name,
                            namespace=namespace,
                            title="Egress rule allows all ports",
                            description=(
                                "Egress rule has no port restrictions."
                            ),
                            evidence={
                                "rule": index,
                            },
                            recommendation=(
                                "Specify only the required destination ports."
                            ),
                        )
                    

        