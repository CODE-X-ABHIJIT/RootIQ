# rootiq/rules/pod/readiness.py

from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule
from rootiq.incident.issue import Issue


class ReadinessRule(BaseRule):

    id = "POD-006"

    name = "Readiness Probe"

    description = "Detect pods failing readiness checks."

    resource_type = "pod"
    
    severity = "high"

    category = "pod"

    def evaluate(self, context: RuleContext):

        for pod in context.resources:

            pod_name = pod["name"]
            namespace = pod["namespace"]

            #
            # Pod conditions
            #
            for condition in pod.get("conditions", []):

                if (
                    condition.get("type") == "Ready"
                    and condition.get("status") != "True"
                ):

                    context.report(
                        
                            rule_id=self.id,
                            severity=self.severity,
                            title="Pod is not Ready",
                            resource=pod_name,
                            namespace=namespace,
                            description=(
                                condition.get("message")
                                or "Pod readiness check failed."
                            ),
                            recommendation=(
                                "Inspect readiness probe configuration, "
                                "application logs and dependent services."
                            ),
                            metadata={
                                "reason": condition.get("reason"),
                                "condition": "Ready",
                            },
                        )
                    

                if (
                    condition.get("type") == "ContainersReady"
                    and condition.get("status") != "True"
                ):

                    context.report(
                        
                            rule_id=self.id,
                            severity=self.severity,
                            title="Containers are not Ready",
                            resource=pod_name,
                            namespace=namespace,
                            description=(
                                condition.get("message")
                                or "One or more containers are not ready."
                            ),
                            recommendation=(
                                "Identify the container failing readiness "
                                "and inspect logs."
                            ),
                            metadata={
                                "reason": condition.get("reason"),
                                "condition": "ContainersReady",
                            },
                        )
                    

            #
            # Container readiness
            #
            for container in pod.get("containers", []):

                if container.get("ready", True):
                    continue

                context.report(
                    
                        rule_id=self.id,
                        severity=self.severity,
                        title="Container is not Ready",
                        resource=pod_name,
                        namespace=namespace,
                        description=(
                            f"Container '{container['name']}' "
                            "is not ready."
                        ),
                        recommendation=(
                            "Verify readiness probe, startup sequence, "
                            "dependencies and application logs."
                        ),
                        metadata={
                            "container": container["name"],
                            "restart_count": container.get(
                                "restart_count", 0
                            ),
                            "image": container.get("image"),
                        },
                    )
                

        