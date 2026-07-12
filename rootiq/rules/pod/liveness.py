# rootiq/rules/pod/liveness.py

from rootiq.rules.base import BaseRule
from rootiq.incident.issue import Issue


class LivenessRule(BaseRule):

    id = "POD-007"

    name = "Liveness Probe"

    description = "Detect containers failing liveness probes."

    resource_type = "pod"
    
    severity = "critical"

    category = "pod"

    def evaluate(self, result):

        for pod in result.resources:

            pod_name = pod["name"]
            namespace = pod["namespace"]

            #
            # Pod Conditions
            #
            for condition in pod.get("conditions", []):

                if (
                    condition.get("type") == "Ready"
                    and condition.get("status") != "True"
                    and condition.get("reason")
                    in (
                        "ContainersNotReady",
                        "ProbeError",
                    )
                ):

                    result.issues.append(
                        Issue(
                            rule_id=self.id,
                            severity=self.severity,
                            title="Liveness probe failure detected",
                            resource=pod_name,
                            namespace=namespace,
                            description=(
                                condition.get("message")
                                or "Container failed liveness probe."
                            ),
                            recommendation=(
                                "Verify the liveness probe endpoint, "
                                "application startup time, timeoutSeconds, "
                                "failureThreshold and container logs."
                            ),
                            metadata={
                                "condition": "Ready",
                                "reason": condition.get("reason"),
                            },
                        )
                    )

            #
            # Frequent restart may indicate liveness failures
            #
            for container in pod.get("containers", []):

                restart_count = container.get(
                    "restart_count", 0
                )

                if restart_count < 5:
                    continue

                result.issues.append(
                    Issue(
                        rule_id=self.id,
                        severity="high",
                        title="Possible liveness probe restart",
                        resource=pod_name,
                        namespace=namespace,
                        description=(
                            f"Container '{container['name']}' "
                            f"has restarted {restart_count} times."
                        ),
                        recommendation=(
                            "Inspect events using "
                            "'kubectl describe pod' to confirm "
                            "whether liveness probes are causing restarts."
                        ),
                        metadata={
                            "container": container["name"],
                            "restart_count": restart_count,
                            "image": container.get("image"),
                        },
                    )
                )

        return result