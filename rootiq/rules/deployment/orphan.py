from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class DeploymentOrphanRule(BaseRule):

    id = "DEPLOYMENT-008"

    name = "DeploymentOrphan"

    resource_type = "deployment"

    def evaluate(self, context: RuleContext):

        

        for deployment in context.resources:

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

                context.report(
                    
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
            

            #
            # No Pod Selector
            #

            if not selector:

                context.report(
                    
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
            

            #
            # No Containers
            #

            if not containers:

                context.report(
                    
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
            

        