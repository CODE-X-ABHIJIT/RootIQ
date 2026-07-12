from rootiq.rules.base import BaseRule
from rootiq.rules.result import RuleResult
from rootiq.rules.issue import Issue


class DeploymentReplicaMismatchRule(BaseRule):

    id = "DEPLOYMENT-004"

    name = "DeploymentReplicaMismatch"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for deployment in resources:

            namespace = deployment.get("namespace")
            name = deployment.get("name")

            desired = deployment.get("desired_replicas", 0)
            ready = deployment.get("ready_replicas", 0)
            available = deployment.get("available_replicas", 0)
            updated = deployment.get("updated_replicas", 0)
            unavailable = deployment.get("unavailable_replicas", 0)

            #
            # Desired != Ready
            #

            if desired != ready:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="High",
                        resource_type="Deployment",
                        resource_name=name,
                        namespace=namespace,
                        title="Deployment replica mismatch",
                        description=(
                            "Ready replicas do not match desired replicas."
                        ),
                        evidence={
                            "desired_replicas": desired,
                            "ready_replicas": ready,
                            "available_replicas": available,
                            "updated_replicas": updated,
                            "unavailable_replicas": unavailable,
                        },
                        recommendation=(
                            "Inspect Pods, ReplicaSets, Events, scheduling, "
                            "container failures and readiness probes."
                        ),
                    )
                )

        return result