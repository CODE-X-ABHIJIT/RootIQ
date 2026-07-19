from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class DeploymentStrategyRule(BaseRule):

    id = "DEPLOYMENT-009"

    name = "DeploymentStrategy"

    resource_type = "deployment"

    def evaluate(self, context: RuleContext):

        

        for deployment in context.resources:

            namespace = deployment.get("namespace")
            deployment_name = deployment.get("name")

            strategy = deployment.get("strategy", {})
            strategy_type = strategy.get("type", "RollingUpdate")

            rolling = strategy.get("rolling_update", {})

            max_surge = rolling.get("max_surge")
            max_unavailable = rolling.get("max_unavailable")

            #
            # Recreate strategy
            #

            if strategy_type == "Recreate":

                context.report(
                    
                        id=self.id,
                        severity="Medium",
                        resource_type="Deployment",
                        resource_name=deployment_name,
                        namespace=namespace,
                        title="Deployment uses Recreate strategy",
                        description=(
                            "Deployment replaces all Pods at once, causing downtime."
                        ),
                        evidence={
                            "strategy": strategy_type,
                        },
                        recommendation=(
                            "Use RollingUpdate unless downtime is intentional."
                        ),
                    )
                

            #
            # RollingUpdate without configuration
            #

            if strategy_type == "RollingUpdate":

                if max_surge is None or max_unavailable is None:

                    context.report(
                        
                            id=self.id,
                            severity="Low",
                            resource_type="Deployment",
                            resource_name=deployment_name,
                            namespace=namespace,
                            title="RollingUpdate parameters missing",
                            description=(
                                "RollingUpdate strategy is missing maxSurge or maxUnavailable."
                            ),
                            evidence={
                                "max_surge": max_surge,
                                "max_unavailable": max_unavailable,
                            },
                            recommendation=(
                                "Configure both maxSurge and maxUnavailable."
                            ),
                        )
                

            #
            # Invalid maxUnavailable
            #

            if max_unavailable == "100%" or max_unavailable == 100:

                context.report(
                    
                        id=self.id,
                        severity="High",
                        resource_type="Deployment",
                        resource_name=deployment_name,
                        namespace=namespace,
                        title="maxUnavailable is 100%",
                        description=(
                            "All Pods may become unavailable during rollout."
                        ),
                        evidence={
                            "max_unavailable": max_unavailable,
                        },
                        recommendation=(
                            "Reduce maxUnavailable to avoid service interruption."
                        ),
                    )
            

            #
            # No surge during rollout
            #

            if max_surge == 0 or max_surge == "0%":

                context.report(
                    
                        id=self.id,
                        severity="Low",
                        resource_type="Deployment",
                        resource_name=deployment_name,
                        namespace=namespace,
                        title="No surge Pods allowed",
                        description=(
                            "Deployment cannot create additional Pods during rollout."
                        ),
                        evidence={
                            "max_surge": max_surge,
                        },
                        recommendation=(
                            "Allow a small maxSurge (for example 25%) for smoother updates."
                        ),
                    )
            

        