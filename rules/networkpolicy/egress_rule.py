from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class NetworkPolicyEgressRule(BaseRule):

    id = "NETPOL-004"

    name = "NetworkPolicyEgress"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for policy in resources:

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

                result.issues.append(
                    Issue(
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

                    result.issues.append(
                        Issue(
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
                    )

        return result