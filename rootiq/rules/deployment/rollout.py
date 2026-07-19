from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class DeploymentRolloutRule(BaseRule):

    id = "DEPLOYMENT-002"

    name = "DeploymentRollout"

    resource_type = "deployment"

    def evaluate(self, context: RuleContext):

        

        for deployment in context.resources:

            namespace = deployment.get("namespace")
            name = deployment.get("name")

            desired = deployment.get("desired_replicas", 0)
            updated = deployment.get("updated_replicas", 0)
            available = deployment.get("available_replicas", 0)
            observed = deployment.get("observed_generation", 0)
            generation = deployment.get("generation", 0)

            #
            # Rollout still in progress
            #

            if (
                desired > 0
                and (
                    updated < desired
                    or available < desired
                    or observed < generation
                )
            ):

                context.report(
                    
                        id=self.id,
                        severity="Medium",
                        resource_type="Deployment",
                        resource_name=name,
                        namespace=namespace,
                        title="Deployment rollout is not complete",
                        description=(
                            "Deployment has not finished rolling out."
                        ),
                        evidence={
                            "desired_replicas": desired,
                            "updated_replicas": updated,
                            "available_replicas": available,
                            "generation": generation,
                            "observed_generation": observed,
                        },
                        recommendation=(
                            "Check deployment status, ReplicaSets, Pods, "
                            "Events and rollout history."
                        ),
                    )
                

        