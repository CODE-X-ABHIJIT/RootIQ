from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class DeploymentUnavailableRule(BaseRule):

    id = "DEPLOYMENT-001"

    name = "DeploymentUnavailable"

    resource_type = "deployment"

    def evaluate(self, context: RuleContext):

        

        for deployment in context.resources:

            desired = deployment.get("desired_replicas", 0)
            available = deployment.get("available_replicas", 0)
            namespace = deployment.get("namespace")
            name = deployment.get("name")

            #
            # Deployment unavailable
            #

            if desired > 0 and available < desired:

                unavailable = desired - available

                context.report(
                    
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
                            "readiness probes and node context.resources."
                        ),
                    )
                

        