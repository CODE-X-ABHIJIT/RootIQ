from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class DeploymentProgressDeadlineRule(BaseRule):

    id = "DEPLOYMENT-003"

    name = "DeploymentProgressDeadline"

    resource_type = "deployment"

    def evaluate(self, context: RuleContext):

        

        for deployment in context.resources:

            namespace = deployment.get("namespace")
            name = deployment.get("name")

            conditions = deployment.get("conditions", [])

            for condition in conditions:

                if (
                    condition.get("type") == "Progressing"
                    and condition.get("status") == "False"
                    and condition.get("reason") == "ProgressDeadlineExceeded"
                ):

                    context.report(
                        
                            id=self.id,
                            severity="Critical",
                            resource_type="Deployment",
                            resource_name=name,
                            namespace=namespace,
                            title="Deployment exceeded progress deadline",
                            description=(
                                "Deployment rollout has exceeded the configured progress deadline."
                            ),
                            evidence={
                                "condition": condition,
                            },
                            recommendation=(
                                "Inspect deployment rollout, ReplicaSets, Pods, "
                                "Events, image pull status, readiness probes "
                                "and application startup logs."
                            ),
                        )
                

        