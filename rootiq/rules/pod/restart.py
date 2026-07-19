# rootiq/rules/pod/restart.py

from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule
from rootiq.incident.issue import Issue


class RestartRule(BaseRule):

    id = "POD-005"

    name = "High Restart Count"

    description = "Detect containers restarting frequently."

    resource_type = "pod"
    
    severity = "high"

    category = "pod"

    RESTART_THRESHOLD = 5

    def evaluate(self, context: RuleContext):

        for pod in context.resources:

            pod_name = pod["name"]
            namespace = pod["namespace"]

            for container in pod.get("containers", []):

                restart_count = container.get(
                    "restart_count", 0
                )

                if restart_count < self.RESTART_THRESHOLD:
                    continue

                recommendation = (
                    "Inspect previous container logs using "
                    "'kubectl logs --previous'. "
                    "Review application logs, probes, "
                    "resource limits and recent deployments."
                )

                severity = "high"

                if restart_count >= 20:
                    severity = "critical"

                context.report(
                    
                        rule_id=self.id,
                        severity=severity,
                        title="Container restarting frequently",
                        resource=pod_name,
                        namespace=namespace,
                        description=(
                            f"Container '{container['name']}' has restarted "
                            f"{restart_count} times."
                        ),
                        recommendation=recommendation,
                        metadata={
                            "container": container["name"],
                            "restart_count": restart_count,
                            "image": container.get("image"),
                        },
                    )
            

        