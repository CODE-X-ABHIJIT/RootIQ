# rootiq/rules/pod/qos.py

from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule
from rootiq.incident.issue import Issue


class QoSRule(BaseRule):

    id = "POD-010"

    name = "QoS Classification"

    description = "Detect pods using non-optimal QoS classes."

    resource_type = "pod"
    
    severity = "medium"

    category = "pod"

    def evaluate(self, context: RuleContext):

        for pod in context.resources:

            qos = pod.get("qos_class", "Unknown")
            pod_name = pod["name"]
            namespace = pod["namespace"]

            #
            # BestEffort
            #
            if qos == "BestEffort":

                context.report(
                    
                        rule_id=self.id,
                        severity="high",
                        title="BestEffort Pod",
                        resource=pod_name,
                        namespace=namespace,
                        description=(
                            "Pod belongs to BestEffort QoS class."
                        ),
                        recommendation=(
                            "Configure CPU and memory requests and limits "
                            "to improve scheduling and reduce eviction risk."
                        ),
                        metadata={
                            "qos": qos,
                        },
                    )
                

            #
            # Burstable
            #
            elif qos == "Burstable":

                context.report(
                    
                        rule_id=self.id,
                        severity="low",
                        title="Burstable Pod",
                        resource=pod_name,
                        namespace=namespace,
                        description=(
                            "Pod belongs to Burstable QoS class."
                        ),
                        recommendation=(
                            "Verify resource requests and limits are "
                            "appropriate for the workload."
                        ),
                        metadata={
                            "qos": qos,
                        },
                    )
                

            #
            # Guaranteed
            #
            elif qos == "Guaranteed":

                continue

            #
            # Unknown
            #
            else:

                context.report(
                    
                        rule_id=self.id,
                        severity="medium",
                        title="Unknown QoS Class",
                        resource=pod_name,
                        namespace=namespace,
                        description=(
                            "Unable to determine pod QoS classification."
                        ),
                        recommendation=(
                            "Verify pod resource configuration."
                        ),
                        metadata={
                            "qos": qos,
                        },
                    )
                

        