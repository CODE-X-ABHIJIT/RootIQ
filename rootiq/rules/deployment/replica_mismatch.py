from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class DeploymentReplicaMismatchRule(BaseRule):

    id = "DEPLOYMENT-004"

    name = "DeploymentReplicaMismatch"

    resource_type = "deployment"

    def evaluate(self, context: RuleContext):

        

        for deployment in context.resources:

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

                context.report(
                    
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
            

        