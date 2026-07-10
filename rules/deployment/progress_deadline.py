from rootiq.rules.base import BaseRule
from rootiq.rules.result import RuleResult
from rootiq.rules.issue import Issue


class DeploymentProgressDeadlineRule(BaseRule):

    id = "DEPLOYMENT-003"

    name = "DeploymentProgressDeadline"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for deployment in resources:

            namespace = deployment.get("namespace")
            name = deployment.get("name")

            conditions = deployment.get("conditions", [])

            for condition in conditions:

                if (
                    condition.get("type") == "Progressing"
                    and condition.get("status") == "False"
                    and condition.get("reason") == "ProgressDeadlineExceeded"
                ):

                    result.issues.append(
                        Issue(
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
                    )

        return result