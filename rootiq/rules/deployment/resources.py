from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class DeploymentResourcesRule(BaseRule):

    id = "DEPLOYMENT-006"

    name = "DeploymentResources"

    resource_type = "deployment"

    def evaluate(self, context: RuleContext):

        

        for deployment in context.resources:

            namespace = deployment.get("namespace")
            deployment_name = deployment.get("name")

            for container in deployment.get("containers", []):

                context.resources = container.get("context.resources", {})

                requests = context.resources.get("requests", {})
                limits = context.resources.get("limits", {})

                #
                # Missing Requests
                #

                if not requests:

                    context.report(
                        
                            id=self.id,
                            severity="Medium",
                            resource_type="Deployment",
                            resource_name=deployment_name,
                            namespace=namespace,
                            title="Container has no resource requests",
                            description=(
                                f"Container '{container['name']}' has no CPU/Memory requests."
                            ),
                            evidence={
                                "container": container["name"],
                                "requests": requests,
                            },
                            recommendation=(
                                "Configure CPU and memory requests for proper scheduling."
                            ),
                        )
                

                #
                # Missing Limits
                #

                if not limits:

                    context.report(
                        
                            id=self.id,
                            severity="Medium",
                            resource_type="Deployment",
                            resource_name=deployment_name,
                            namespace=namespace,
                            title="Container has no resource limits",
                            description=(
                                f"Container '{container['name']}' has no CPU/Memory limits."
                            ),
                            evidence={
                                "container": container["name"],
                                "limits": limits,
                            },
                            recommendation=(
                                "Configure CPU and memory limits to prevent resource exhaustion."
                            ),
                        )
                

                #
                # CPU request > limit
                #

                cpu_request = requests.get("cpu")
                cpu_limit = limits.get("cpu")

                if (
                    cpu_request
                    and cpu_limit
                    and cpu_request > cpu_limit
                ):

                    context.report(
                        
                            id=self.id,
                            severity="High",
                            resource_type="Deployment",
                            resource_name=deployment_name,
                            namespace=namespace,
                            title="CPU request exceeds CPU limit",
                            description=(
                                f"Container '{container['name']}' has CPU request greater than CPU limit."
                            ),
                            evidence={
                                "container": container["name"],
                                "cpu_request": cpu_request,
                                "cpu_limit": cpu_limit,
                            },
                            recommendation=(
                                "Ensure CPU request is less than or equal to the CPU limit."
                            ),
                        )
                

                #
                # Memory request > limit
                #

                memory_request = requests.get("memory")
                memory_limit = limits.get("memory")

                if (
                    memory_request
                    and memory_limit
                    and memory_request > memory_limit
                ):

                    context.report(
                        
                            id=self.id,
                            severity="High",
                            resource_type="Deployment",
                            resource_name=deployment_name,
                            namespace=namespace,
                            title="Memory request exceeds memory limit",
                            description=(
                                f"Container '{container['name']}' has memory request greater than memory limit."
                            ),
                            evidence={
                                "container": container["name"],
                                "memory_request": memory_request,
                                "memory_limit": memory_limit,
                            },
                            recommendation=(
                                "Ensure memory request is less than or equal to the memory limit."
                            ),
                        )
                

                #
                # Missing CPU request
                #

                if "cpu" not in requests:

                    context.report(
                        
                            id=self.id,
                            severity="Low",
                            resource_type="Deployment",
                            resource_name=deployment_name,
                            namespace=namespace,
                            title="CPU request not configured",
                            description=(
                                f"Container '{container['name']}' does not define CPU request."
                            ),
                            evidence={
                                "container": container["name"],
                            },
                            recommendation=(
                                "Configure CPU request."
                            ),
                        )
                

                #
                # Missing Memory request
                #

                if "memory" not in requests:

                    context.report(
                        
                            id=self.id,
                            severity="Low",
                            resource_type="Deployment",
                            resource_name=deployment_name,
                            namespace=namespace,
                            title="Memory request not configured",
                            description=(
                                f"Container '{container['name']}' does not define memory request."
                            ),
                            evidence={
                                "container": container["name"],
                            },
                            recommendation=(
                                "Configure memory request."
                            ),
                        )
                

                #
                # Missing CPU limit
                #

                if "cpu" not in limits:

                    context.report(
                        
                            id=self.id,
                            severity="Low",
                            resource_type="Deployment",
                            resource_name=deployment_name,
                            namespace=namespace,
                            title="CPU limit not configured",
                            description=(
                                f"Container '{container['name']}' does not define CPU limit."
                            ),
                            evidence={
                                "container": container["name"],
                            },
                            recommendation=(
                                "Configure CPU limit."
                            ),
                        )
                

                #
                # Missing Memory limit
                #

                if "memory" not in limits:

                    context.report(
                        
                            id=self.id,
                            severity="Low",
                            resource_type="Deployment",
                            resource_name=deployment_name,
                            namespace=namespace,
                            title="Memory limit not configured",
                            description=(
                                f"Container '{container['name']}' does not define memory limit."
                            ),
                            evidence={
                                "container": container["name"],
                            },
                            recommendation=(
                                "Configure memory limit."
                            ),
                        )
                

        