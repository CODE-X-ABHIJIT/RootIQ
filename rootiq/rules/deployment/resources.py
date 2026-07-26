from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class DeploymentResourcesRule(BaseRule):

    id = "DEPLOYMENT-006"

    name = "Deployment Resource Configuration"

    description = (
        "Detect missing or invalid CPU/Memory requests and limits."
    )

    resource_type = "deployment"

    severity = "medium"

    category = "deployment"

    def evaluate(self, context: RuleContext):

        for deployment in context.resources:

            deployment_name = deployment["name"]
            namespace = deployment["namespace"]

            for container in deployment.get("containers", []):

                resources = container.get("resources", {})

                requests = resources.get("requests", {})
                limits = resources.get("limits", {})

                #
                # No requests AND no limits
                #
                if not requests and not limits:

                    context.report(
                        rule_id=self.id,
                        severity="high",
                        title="Container has no resource configuration",
                        resource=deployment_name,
                        namespace=namespace,
                        description=(
                            f"Container '{container['name']}' has neither "
                            "CPU/Memory requests nor limits configured."
                        ),
                        recommendation=(
                            "Configure CPU and memory requests and limits "
                            "for reliable scheduling and resource isolation."
                        ),
                        metadata={
                            "container": container["name"],
                        },
                    )

                    continue

                #
                # Requests missing
                #
                if not requests:

                    context.report(
                        rule_id=self.id,
                        severity="medium",
                        title="Container has no resource requests",
                        resource=deployment_name,
                        namespace=namespace,
                        description=(
                            f"Container '{container['name']}' has no "
                            "CPU/Memory requests configured."
                        ),
                        recommendation=(
                            "Configure CPU and memory requests."
                        ),
                        metadata={
                            "container": container["name"],
                        },
                    )

                #
                # Limits missing
                #
                if not limits:

                    context.report(
                        rule_id=self.id,
                        severity="medium",
                        title="Container has no resource limits",
                        resource=deployment_name,
                        namespace=namespace,
                        description=(
                            f"Container '{container['name']}' has no "
                            "CPU/Memory limits configured."
                        ),
                        recommendation=(
                            "Configure CPU and memory limits."
                        ),
                        metadata={
                            "container": container["name"],
                        },
                    )

                #
                # Missing individual requests
                #
                if requests:

                    if "cpu" not in requests:

                        context.report(
                            rule_id=self.id,
                            severity="low",
                            title="CPU request missing",
                            resource=deployment_name,
                            namespace=namespace,
                            description=(
                                f"Container '{container['name']}' does not "
                                "define a CPU request."
                            ),
                            recommendation="Configure a CPU request.",
                            metadata={
                                "container": container["name"],
                            },
                        )

                    if "memory" not in requests:

                        context.report(
                            rule_id=self.id,
                            severity="low",
                            title="Memory request missing",
                            resource=deployment_name,
                            namespace=namespace,
                            description=(
                                f"Container '{container['name']}' does not "
                                "define a memory request."
                            ),
                            recommendation="Configure a memory request.",
                            metadata={
                                "container": container["name"],
                            },
                        )

                #
                # Missing individual limits
                #
                if limits:

                    if "cpu" not in limits:

                        context.report(
                            rule_id=self.id,
                            severity="low",
                            title="CPU limit missing",
                            resource=deployment_name,
                            namespace=namespace,
                            description=(
                                f"Container '{container['name']}' does not "
                                "define a CPU limit."
                            ),
                            recommendation="Configure a CPU limit.",
                            metadata={
                                "container": container["name"],
                            },
                        )

                    if "memory" not in limits:

                        context.report(
                            rule_id=self.id,
                            severity="low",
                            title="Memory limit missing",
                            resource=deployment_name,
                            namespace=namespace,
                            description=(
                                f"Container '{container['name']}' does not "
                                "define a memory limit."
                            ),
                            recommendation="Configure a memory limit.",
                            metadata={
                                "container": container["name"],
                            },
                        )

                #
                # Request greater than limit
                #
                cpu_request = requests.get("cpu")
                cpu_limit = limits.get("cpu")

                if cpu_request and cpu_limit:

                    #
                    # TODO (Phase 2):
                    # Parse Kubernetes quantities before comparing.
                    #
                    pass

                memory_request = requests.get("memory")
                memory_limit = limits.get("memory")

                if memory_request and memory_limit:

                    #
                    # TODO (Phase 2):
                    # Parse Kubernetes quantities before comparing.
                    #
                    pass