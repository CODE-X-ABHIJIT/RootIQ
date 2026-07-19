# rootiq/rules/pod/pending.py

from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule
from rootiq.incident.issue import Issue


class PendingRule(BaseRule):

    id = "POD-002"

    name = "Pending Pod"

    description = "Detect pods stuck in Pending state."

    resource_type = "pod"
    
    severity = "high"

    category = "pod"

    def evaluate(self, context: RuleContext):

        for pod in context.resources:

            if pod.get("phase") != "Pending":
                continue

            pod_name = pod["name"]
            namespace = pod["namespace"]

            conditions = pod.get("conditions", [])

            scheduled = next(
                (
                    c for c in conditions
                    if c.get("type") == "PodScheduled"
                ),
                None,
            )

            reason = ""
            message = ""

            if scheduled:
                reason = scheduled.get("reason") or ""
                message = scheduled.get("message") or ""

            recommendation = "Describe the pod and inspect scheduler events."

            #
            # CPU
            #
            if "Insufficient cpu" in message.lower():
                recommendation = (
                    "Cluster has insufficient CPU. "
                    "Add worker nodes or reduce CPU requests."
                )

            #
            # Memory
            #
            elif "Insufficient memory" in message.lower():
                recommendation = (
                    "Cluster has insufficient memory. "
                    "Increase node memory or reduce pod requests."
                )

            #
            # PVC
            #
            elif "persistentvolumeclaim" in message.lower():
                recommendation = (
                    "Verify PVC exists and is Bound."
                )

            #
            # Taints
            #
            elif "taint" in message.lower():
                recommendation = (
                    "Add matching tolerations or remove node taints."
                )

            #
            # Node Selector
            #
            elif "node(s) didn't match node selector" in message.lower():
                recommendation = (
                    "Verify nodeSelector labels."
                )

            #
            # Affinity
            #
            elif "affinity" in message.lower():
                recommendation = (
                    "Review node affinity / anti-affinity rules."
                )

            #
            # ResourceQuota
            #
            elif "quota" in message.lower():
                recommendation = (
                    "Namespace ResourceQuota exceeded."
                )

            #
            # LimitRange
            #
            elif "limitrange" in message.lower():
                recommendation = (
                    "Pod violates LimitRange constraints."
                )

            #
            # Unschedulable
            #
            elif reason == "Unschedulable":
                recommendation = (
                    "Scheduler cannot place this pod. "
                    "Review node resources and scheduling constraints."
                )

            context.report(
                
                    rule_id=self.id,
                    severity=self.severity,
                    title="Pod is Pending",
                    resource=pod_name,
                    namespace=namespace,
                    description=message or "Pod remains Pending.",
                    recommendation=recommendation,
                    metadata={
                        "reason": reason,
                        "phase": pod["phase"],
                    },
                )
            

        