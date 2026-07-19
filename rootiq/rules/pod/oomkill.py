# rootiq/rules/pod/oomkill.py

from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule
from rootiq.incident.issue import Issue


class OOMKillRule(BaseRule):

    id = "POD-004"

    name = "OOMKilled"

    description = "Detect containers terminated because of Out Of Memory."

    resource_type = "pod"
    
    severity = "critical"

    category = "pod"

    def evaluate(self, context: RuleContext):

        for pod in context.resources:

            pod_name = pod["name"]
            namespace = pod["namespace"]

            for container in pod.get("containers", []):

                last_state = container.get("last_state", {})
                terminated = last_state.get("terminated")

                if not terminated:
                    continue

                reason = terminated.get("reason")
                exit_code = terminated.get("exit_code")

                if (
                    reason == "OOMKilled"
                    or exit_code == 137
                ):

                    recommendation = (
                        "Increase memory limit or reduce application "
                        "memory usage. Review memory requests/limits."
                    )

                    if exit_code == 137 and reason != "OOMKilled":
                        recommendation += (
                            " Exit code 137 commonly indicates the process "
                            "was killed because of memory pressure."
                        )

                    context.report(
                        
                            rule_id=self.id,
                            severity=self.severity,
                            title="Container OOMKilled",
                            resource=pod_name,
                            namespace=namespace,
                            description=(
                                f"Container '{container['name']}' "
                                "was terminated due to insufficient memory."
                            ),
                            recommendation=recommendation,
                            metadata={
                                "container": container["name"],
                                "image": container.get("image"),
                                "reason": reason,
                                "exit_code": exit_code,
                                "restart_count": container.get(
                                    "restart_count", 0
                                ),
                            },
                        )
                    

        