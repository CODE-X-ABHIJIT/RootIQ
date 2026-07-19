# rootiq/rules/pod/crashloop.py

from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule
from rootiq.incident.issue import Issue


class CrashLoopRule(BaseRule):

    id = "POD-001"

    name = "CrashLoopBackOff"

    description = "Detect pods repeatedly crashing."

    resource_type = "pod"

    severity = "critical"

    category = "pod"

    def evaluate(self, context: RuleContext):

        for pod in context.resources:

            pod_name = pod["name"]
            namespace = pod["namespace"]

            for container in pod.get("containers", []):

                state = container.get("state", {})
                waiting = state.get("waiting")

                #
                # CrashLoopBackOff
                #
                if (
                    waiting
                    and waiting.get("reason") == "CrashLoopBackOff"
                ):

                    context.report(
                        
                            rule_id=self.id,
                            severity=self.severity,
                            title="Pod is in CrashLoopBackOff",
                            resource=pod_name,
                            namespace=namespace,
                            description=(
                                f"Container '{container['name']}' "
                                "is repeatedly crashing."
                            ),
                            recommendation=(
                                "Inspect previous logs, "
                                "container exit code, "
                                "environment variables, "
                                "ConfigMaps and Secrets."
                            ),
                            metadata={
                                "container": container["name"],
                                "reason": waiting.get("reason"),
                                "message": waiting.get("message"),
                            },
                        )
                

                #
                # Waiting message contains Back-off
                #
                elif (
                    waiting
                    and waiting.get("message")
                    and "Back-off" in waiting["message"]
                ):

                    context.report(
                        
                            rule_id=self.id,
                            severity=self.severity,
                            title="Container restart back-off detected",
                            resource=pod_name,
                            namespace=namespace,
                            description=waiting["message"],
                            recommendation=(
                                "Check pod logs and investigate "
                                "why the application exits."
                            ),
                            metadata={
                                "container": container["name"]
                            },
                        )
                

                #
                # Restart count unusually high
                #
                elif container.get("restart_count", 0) >= 5:

                    context.report(
                        
                            rule_id=self.id,
                            severity="high",
                            title="Container restarting frequently",
                            resource=pod_name,
                            namespace=namespace,
                            description=(
                                f"Container restarted "
                                f"{container['restart_count']} times."
                            ),
                            recommendation=(
                                "Investigate application logs and "
                                "container health."
                            ),
                            metadata={
                                "container": container["name"],
                                "restart_count": container[
                                    "restart_count"
                                ],
                            },
                        )
                