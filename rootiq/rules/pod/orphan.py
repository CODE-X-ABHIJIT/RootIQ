# rootiq/rules/pod/orphan.py

from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule
from rootiq.incident.issue import Issue


class OrphanRule(BaseRule):

    id = "POD-011"

    name = "Orphan Pod"

    description = "Detect pods without a valid workload owner."

    resource_type = "pod"
    
    severity = "medium"

    category = "pod"

    VALID_OWNERS = {
        "ReplicaSet",
        "StatefulSet",
        "DaemonSet",
        "Job",
        "CronJob",
        "Node",  # Static / mirror pods
    }

    def evaluate(self, context: RuleContext):

        for pod in context.resources:

            pod_name = pod["name"]
            namespace = pod["namespace"]

            owner = pod.get("owner")

            #
            # No owner
            #
            if owner is None:

                context.report(
                    
                        rule_id=self.id,
                        severity="medium",
                        title="Pod has no owner",
                        resource=pod_name,
                        namespace=namespace,
                        description=(
                            "Pod does not have an ownerReference."
                        ),
                        recommendation=(
                            "Verify whether this standalone pod is intentional. "
                            "Prefer Deployments, StatefulSets, Jobs or DaemonSets."
                        ),
                        metadata={
                            "owner": None,
                        },
                    )
                

                continue

            #
            # Unknown owner
            #
            if owner not in self.VALID_OWNERS:

                context.report(
                    
                        rule_id=self.id,
                        severity="medium",
                        title="Unknown pod owner",
                        resource=pod_name,
                        namespace=namespace,
                        description=(
                            f"Pod is owned by unsupported resource '{owner}'."
                        ),
                        recommendation=(
                            "Verify the owner resource still exists and "
                            "is managing this pod correctly."
                        ),
                        metadata={
                            "owner": owner,
                        },
                    )
                

            #
            # Completed Job Pods
            #
            if (
                owner == "Job"
                and pod.get("phase") == "Succeeded"
            ):

                context.report(
                    
                        rule_id=self.id,
                        severity="low",
                        title="Completed Job Pod",
                        resource=pod_name,
                        namespace=namespace,
                        description=(
                            "Completed Job pod still exists."
                        ),
                        recommendation=(
                            "Consider enabling TTLAfterFinished "
                            "or cleaning up completed Jobs."
                        ),
                        metadata={
                            "owner": owner,
                            "phase": pod.get("phase"),
                        },
                    )
                

        