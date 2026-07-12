from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class NetworkPolicyTypeRule(BaseRule):

    id = "NETPOL-002"

    name = "NetworkPolicyType"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        valid_types = {
            "Ingress",
            "Egress",
        }

        for policy in resources:

            namespace = policy.get("namespace")
            name = policy.get("name")

            policy_types = policy.get(
                "policy_types",
                [],
            )

            #
            # Missing policyTypes
            #

            if not policy_types:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Medium",
                        resource_type="NetworkPolicy",
                        resource_name=name,
                        namespace=namespace,
                        title="Missing policyTypes",
                        description=(
                            "NetworkPolicy does not explicitly define policyTypes."
                        ),
                        evidence={},
                        recommendation=(
                            "Explicitly configure Ingress and/or Egress policy types."
                        ),
                    )
                )

                continue

            #
            # Duplicate policyTypes
            #

            if len(policy_types) != len(set(policy_types)):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Low",
                        resource_type="NetworkPolicy",
                        resource_name=name,
                        namespace=namespace,
                        title="Duplicate policyTypes",
                        description=(
                            "Duplicate entries found in policyTypes."
                        ),
                        evidence={
                            "policy_types": policy_types,
                        },
                        recommendation=(
                            "Remove duplicate policy types."
                        ),
                    )
                )

            #
            # Invalid policyTypes
            #

            for policy_type in policy_types:

                if policy_type not in valid_types:

                    result.issues.append(
                        Issue(
                            id=self.id,
                            severity="High",
                            resource_type="NetworkPolicy",
                            resource_name=name,
                            namespace=namespace,
                            title="Invalid policyType",
                            description=(
                                "Unsupported NetworkPolicy type configured."
                            ),
                            evidence={
                                "policy_type": policy_type,
                            },
                            recommendation=(
                                "Use only 'Ingress' and/or 'Egress'."
                            ),
                        ),
                    )

        return result