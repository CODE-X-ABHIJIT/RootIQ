from rootiq.rules.base import BaseRule
from rootiq.rules.result import RuleResult
from rootiq.rules.issue import Issue


class DeploymentOrphanRule(BaseRule):

    id = "DEPLOYMENT-008"

    name = "DeploymentOrphan"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for deployment in resources:

            namespace = deployment.get("namespace")
            deployment_name = deployment.get("name")

            desired = deployment.get("desired_replicas", 0)
            replicasets = deployment.get("replicasets", [])
            selector = deployment.get("selector", {})
            containers = deployment.get("containers", [])

            #
            # No ReplicaSet
            #

            if desired > 0 and not replicasets:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="High",
                        resource_type="Deployment",
                        resource_name=deployment_name,
                        namespace=namespace,
                        title="Deployment has no ReplicaSet",
                        description=(
                            "Deployment does not own any ReplicaSet."
                        ),
                        evidence={
                            "desired_replicas": desired,
                            "replicasets": replicasets,
                        },
                        recommendation=(
                            "Verify Deployment controller and rollout status."
                        ),
                    )
                )

            #
            # No Pod Selector
            #

            if not selector:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="High",
                        resource_type="Deployment",
                        resource_name=deployment_name,
                        namespace=namespace,
                        title="Deployment selector missing",
                        description=(
                            "Deployment has no pod selector."
                        ),
                        evidence={
                            "selector": selector,
                        },
                        recommendation=(
                            "Configure a valid matchLabels selector."
                        ),
                    )
                )

            #
            # No Containers
            #

            if not containers:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Critical",
                        resource_type="Deployment",
                        resource_name=deployment_name,
                        namespace=namespace,
                        title="Deployment has no containers",
                        description=(
                            "Deployment template contains no containers."
                        ),
                        evidence={
                            "containers": containers,
                        },
                        recommendation=(
                            "Define at least one application container."
                        ),
                    )
                )

        return result