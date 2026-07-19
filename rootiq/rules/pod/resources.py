# rootiq/rules/pod/resources.py

from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule
from rootiq.incident.issue import Issue


class ResourcesRule(BaseRule):

    id = "POD-008"

    name = "Resource Configuration"

    description = "Detect resource request and limit misconfigurations."

    resource_type = "pod"
    
    severity = "medium"

    category = "pod"

    def evaluate(self, context: RuleContext):

        for pod in context.resources:

            pod_name = pod["name"]
            namespace = pod["namespace"]

            qos = pod.get("qos_class", "Unknown")

            #
            # BestEffort Pods
            #
            if qos == "BestEffort":

                context.report(
                    
                        rule_id=self.id,
                        severity="medium",
                        title="BestEffort QoS",
                        resource=pod_name,
                        namespace=namespace,
                        description=(
                            "Pod has no CPU or memory requests/limits."
                        ),
                        recommendation=(
                            "Define CPU and memory requests and limits."
                        ),
                        metadata={
                            "qos": qos,
                        },
                    )
                

            #
            # Burstable Pods
            #
            elif qos == "Burstable":

                context.report(
                    
                        rule_id=self.id,
                        severity="low",
                        title="Burstable QoS",
                        resource=pod_name,
                        namespace=namespace,
                        description=(
                            "Pod is using Burstable QoS."
                        ),
                        recommendation=(
                            "Verify that CPU and memory requests are "
                            "properly configured."
                        ),
                        metadata={
                            "qos": qos,
                        },
                    )
                

            #
            # Container-level validation
            #
            for container in pod.get("containers", []):

                resources = container.get("resources", {})

                requests = resources.get("requests", {})
                limits = resources.get("limits", {})

                #
                # Missing CPU Request
                #
                if "cpu" not in requests:

                    context.report(
                        
                            rule_id=self.id,
                            severity="medium",
                            title="CPU request missing",
                            resource=pod_name,
                            namespace=namespace,
                            description=(
                                f"Container '{container['name']}' "
                                "has no CPU request."
                            ),
                            recommendation=(
                                "Configure CPU requests for better scheduling."
                            ),
                            metadata={
                                "container": container["name"]
                            },
                        )
                    

                #
                # Missing Memory Request
                #
                if "memory" not in requests:

                    context.report(
                        
                            rule_id=self.id,
                            severity="medium",
                            title="Memory request missing",
                            resource=pod_name,
                            namespace=namespace,
                            description=(
                                f"Container '{container['name']}' "
                                "has no memory request."
                            ),
                            recommendation=(
                                "Configure memory requests."
                            ),
                            metadata={
                                "container": container["name"]
                            },
                        )
                    

                #
                # Missing CPU Limit
                #
                if "cpu" not in limits:

                    context.report(
                        
                            rule_id=self.id,
                            severity="low",
                            title="CPU limit missing",
                            resource=pod_name,
                            namespace=namespace,
                            description=(
                                f"Container '{container['name']}' "
                                "has no CPU limit."
                            ),
                            recommendation=(
                                "Consider configuring CPU limits."
                            ),
                            metadata={
                                "container": container["name"]
                            },
                        )
                    

                #
                # Missing Memory Limit
                #
                if "memory" not in limits:

                    context.report(
                        
                            rule_id=self.id,
                            severity="high",
                            title="Memory limit missing",
                            resource=pod_name,
                            namespace=namespace,
                            description=(
                                f"Container '{container['name']}' "
                                "has no memory limit."
                            ),
                            recommendation=(
                                "Configure memory limits to avoid node memory exhaustion."
                            ),
                            metadata={
                                "container": container["name"]
                            },
                        )
                    

        