# rootiq/rules/pod/liveness.py

from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class LivenessRule(BaseRule):

    id = "POD-007"

    name = "Liveness Probe Failure"

    description = (
        "Detect pods reporting liveness or probe-related failures."
    )

    resource_type = "pod"

    severity = "critical"

    category = "pod"

    SYSTEM_NAMESPACES = {
        "kube-system",
        "kube-public",
        "kube-node-lease",
    }

    PROBE_REASONS = {
        "ProbeError",
        "ContainersNotReady",
    }

    def evaluate(self, context: RuleContext):

        for pod in context.resources:

            namespace = pod["namespace"]

            #
            # Ignore Kubernetes system components
            #
            if namespace in self.SYSTEM_NAMESPACES:
                continue

            pod_name = pod["name"]

            for condition in pod.get("conditions", []):

                if condition.get("type") != "Ready":
                    continue

                if condition.get("status") == "True":
                    continue

                reason = condition.get("reason", "")

                if reason not in self.PROBE_REASONS:
                    continue

                context.report(
                    rule_id=self.id,
                    severity=self.severity,
                    title="Possible probe failure detected",
                    resource=pod_name,
                    namespace=namespace,
                    description=(
                        condition.get("message")
                        or "The pod reports a probe-related readiness failure."
                    ),
                    recommendation=(
                        "Inspect pod events using "
                        "'kubectl describe pod' and verify "
                        "liveness/readiness probe configuration, "
                        "startup time and application logs."
                    ),
                    metadata={
                        "condition": "Ready",
                        "reason": reason,
                    },
                )

                #
                # Prevent duplicate reports for the same pod
                #
                break