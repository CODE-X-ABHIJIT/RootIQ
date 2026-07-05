from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class PodCollector(BaseCollector):

    name = "PodCollector"

    def collect(self, k8s):

        result = CollectResult(
            collector=self.name
        )

        pods = k8s.pods()

        for pod in pods:

            pod_data = {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "uid": pod.metadata.uid,

                "node": pod.spec.node_name,

                "phase": pod.status.phase,

                "pod_ip": pod.status.pod_ip,

                "host_ip": pod.status.host_ip,

                "qos_class": pod.status.qos_class,

                "service_account": pod.spec.service_account_name,

                "creation_timestamp": (
                    pod.metadata.creation_timestamp.isoformat()
                    if pod.metadata.creation_timestamp
                    else None
                ),

                "labels": pod.metadata.labels or {},

                "annotations": (
                    pod.metadata.annotations or {}
                ),

                "owner": (
                    pod.metadata.owner_references[0].kind
                    if pod.metadata.owner_references
                    else None
                ),

                "containers": [],

                "conditions": [],
            }

            #
            # Container Status
            #

            if pod.status.container_statuses:

                for container in (
                    pod.status.container_statuses
                ):

                    pod_data["containers"].append(
                        {
                            "name": container.name,
                            "ready": container.ready,
                            "restart_count": (
                                container.restart_count
                            ),
                            "image": (
                                container.image
                            ),
                            "image_id": (
                                container.image_id
                            ),
                        }
                    )

            #
            # Conditions
            #

            if pod.status.conditions:

                for condition in (
                    pod.status.conditions
                ):

                    pod_data["conditions"].append(
                        {
                            "type": condition.type,
                            "status": condition.status,
                            "reason": condition.reason,
                            "message": condition.message,
                        }
                    )

            result.resources.append(
                pod_data
            )

        #
        # Metrics
        #

        result.metrics.append(
            {
                "metric": "pod_count",
                "value": len(result.resources),
            }
        )

        return result
