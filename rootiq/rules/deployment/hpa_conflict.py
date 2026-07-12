from rootiq.rules.base import BaseRule
from rootiq.rules.result import RuleResult
from rootiq.rules.issue import Issue


class DeploymentHPAConflictRule(BaseRule):

    id = "DEPLOYMENT-007"

    name = "DeploymentHPAConflict"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for deployment in resources:

            namespace = deployment.get("namespace")
            deployment_name = deployment.get("name")

            replicas = deployment.get("desired_replicas", 1)

            hpa = deployment.get("hpa")

            #
            # No HPA attached
            #

            if not hpa:
                continue

            min_replicas = hpa.get("min_replicas")
            max_replicas = hpa.get("max_replicas")

            #
            # Desired replicas outside HPA range
            #

            if (
                min_replicas is not None
                and replicas < min_replicas
            ):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Medium",
                        resource_type="Deployment",
                        resource_name=deployment_name,
                        namespace=namespace,
                        title="Deployment replicas below HPA minimum",
                        description=(
                            "Deployment replica count is lower than the configured HPA minimum."
                        ),
                        evidence={
                            "desired_replicas": replicas,
                            "min_replicas": min_replicas,
                            "max_replicas": max_replicas,
                        },
                        recommendation=(
                            "Verify HPA configuration and deployment replica count."
                        ),
                    )
                )

            if (
                max_replicas is not None
                and replicas > max_replicas
            ):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Medium",
                        resource_type="Deployment",
                        resource_name=deployment_name,
                        namespace=namespace,
                        title="Deployment replicas exceed HPA maximum",
                        description=(
                            "Deployment replica count is greater than the configured HPA maximum."
                        ),
                        evidence={
                            "desired_replicas": replicas,
                            "min_replicas": min_replicas,
                            "max_replicas": max_replicas,
                        },
                        recommendation=(
                            "Verify HPA configuration or reduce the deployment replica count."
                        ),
                    )
                )

            #
            # Invalid HPA configuration
            #

            if (
                min_replicas is not None
                and max_replicas is not None
                and min_replicas > max_replicas
            ):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="High",
                        resource_type="Deployment",
                        resource_name=deployment_name,
                        namespace=namespace,
                        title="Invalid HPA configuration",
                        description=(
                            "HPA minimum replicas is greater than maximum replicas."
                        ),
                        evidence={
                            "min_replicas": min_replicas,
                            "max_replicas": max_replicas,
                        },
                        recommendation=(
                            "Correct the HPA configuration so that minReplicas is less than or equal to maxReplicas."
                        ),
                    )
                )

        return result