from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class NetworkPolicyIngressRule(BaseRule):

    id = "NETPOL-003"

    name = "NetworkPolicyIngress"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for policy in resources:

            namespace = policy.get("namespace")
            name = policy.get("name")

            policy_types = policy.get(
                "policy_types",
                [],
            )

            ingress = policy.get(
                "ingress",
                [],
            )

            #
            # Ingress policy without rules
            #

            if (
                "Ingress" in policy_types
                and not ingress
            ):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Info",
                        resource_type="NetworkPolicy",
                        resource_name=name,
                        namespace=namespace,
                        title="Ingress traffic denied",
                        description=(
                            "Ingress policy contains no ingress rules. "
                            "This denies all incoming traffic to selected pods."
                        ),
                        evidence={},
                        recommendation=(
                            "Verify that a default deny policy is intended."
                        ),
                    )
                )

            #
            # Validate ingress rules
            #

            for index, rule in enumerate(ingress):

                peers = rule.get(
                    "from",
                    [],
                )

                ports = rule.get(
                    "ports",
                    [],
                )

                #
                # Rule allows all sources
                #

                if not peers:

                    result.issues.append(
                        Issue(
                            id=self.id,
                            severity="Low",
                            resource_type="NetworkPolicy",
                            resource_name=name,
                            namespace=namespace,
                            title="Ingress rule allows all sources",
                            description=(
                                "Ingress rule has no peer restrictions."
                            ),
                            evidence={
                                "rule": index,
                            },
                            recommendation=(
                                "Restrict the allowed sources where possible."
                            ),
                        )
                    )

                #
                # Rule allows all ports
                #

                if not ports:

                    result.issues.append(
                        Issue(
                            id=self.id,
                            severity="Low",
                            resource_type="NetworkPolicy",
                            resource_name=name,
                            namespace=namespace,
                            title="Ingress rule allows all ports",
                            description=(
                                "Ingress rule has no port restrictions."
                            ),
                            evidence={
                                "rule": index,
                            },
                            recommendation=(
                                "Specify only the required ports."
                            ),
                        )
                    )

        return result