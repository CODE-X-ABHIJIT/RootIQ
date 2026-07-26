# rootiq/rules/pod/qos.py

from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class QoSRule(BaseRule):

    id = "POD-010"

    name = "BestEffort QoS"

    description = (
        "Detect pods running without CPU or memory requests and limits."
    )

    resource_type = "pod"

    severity = "high"

    category = "pod"

    SYSTEM_NAMESPACES = {
        "kube-system",
        "kube-public",
        "kube-node-lease",
    }

    def evaluate(self, context: RuleContext):

        for pod in context.resources:

            namespace = pod["namespace"]

            #
            # Ignore Kubernetes system components
            #
            if namespace in self.SYSTEM_NAMESPACES:
                continue

            qos = pod.get("qos_class", "Unknown")
            pod_name = pod["name"]

            #
            # Only BestEffort is considered an incident.
            #
            if qos != "BestEffort":
                continue

            context.report(
                rule_id=self.id,
                severity="high",
                title="Pod is running as BestEffort",
                resource=pod_name,
                namespace=namespace,
                description=(
                    "The pod has no CPU or memory requests/limits and "
                    "is classified as BestEffort."
                ),
                recommendation=(
                    "Configure CPU and memory requests and limits to "
                    "improve scheduling stability and reduce eviction risk."
                ),
                metadata={
                    "qos": qos,
                },
            )