from rootiq.rules.base import BaseRule
from rootiq.rules.result import RuleResult
from rootiq.rules.issue import Issue


class DeploymentUnavailableRule(BaseRule):

    id = "DEPLOYMENT-001"

    name = "DeploymentUnavailable"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for deployment in resources:

            desired = deployment.get("desired_replicas", 0)
            available = deployment.get("available_replicas", 0)
            namespace = deployment.get("namespace")
            name = deployment.get("name")

            #
            # Deployment unavailable
            #

            if desired > 0 and available < desired:

                unavailable = desired - available

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="High",
                        resource_type="Deployment",
                        resource_name=name,
                        namespace=namespace,
                        title="Deployment has unavailable replicas",
                        description=(
                            f"{unavailable} replica(s) are unavailable."
                        ),
                        evidence={
                            "desired_replicas": desired,
                            "available_replicas": available,
                            "unavailable_replicas": unavailable,
                        },
                        recommendation=(
                            "Inspect deployment rollout, pods, events, "
                            "readiness probes and node resources."
                        ),
                    )
                )

        return result