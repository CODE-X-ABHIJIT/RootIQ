# rootiq/rules/pod/restart.py

from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class RestartRule(BaseRule):

    id = "POD-005"

    name = "High Restart Count"

    description = "Detect application containers restarting frequently."

    resource_type = "pod"

    severity = "high"

    category = "pod"

    RESTART_THRESHOLD = 5

    CRITICAL_THRESHOLD = 20

    # Ignore infrastructure namespaces in Phase 1
    IGNORED_NAMESPACES = {
        "kube-system",
        "kube-public",
        "kube-node-lease",
        "local-path-storage",
        "monitoring",
    }

    def evaluate(self, context: RuleContext):

        for pod in context.resources:

            namespace = pod["namespace"]

            if namespace in self.IGNORED_NAMESPACES:
                continue

            pod_name = pod["name"]

            phase = str(
                pod.get("phase", "")
            ).lower()

            # Ignore completed pods
            if phase in ("succeeded", "completed"):
                continue

            containers = pod.get("containers", [])

            for container in containers:

                # Ignore init containers
                if container.get("is_init_container", False):
                    continue

                restart_count = int(
                    container.get("restart_count", 0)
                )

                if restart_count < self.RESTART_THRESHOLD:
                    continue

                severity = "high"

                if restart_count >= self.CRITICAL_THRESHOLD:
                    severity = "critical"

                recommendation = (
                    "Inspect the previous logs using "
                    "'kubectl logs --previous'. "
                    "Review probe failures, application logs, "
                    "resource limits, OOMKills, and recent deployments."
                )

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