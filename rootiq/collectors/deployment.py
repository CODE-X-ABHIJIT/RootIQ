from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class DeploymentCollector(BaseCollector):

    name = "DeploymentCollector"

    def collect(self, k8s):

        result = CollectResult(
            collector=self.name
        )

        try:
            deployments = k8s.apps.list_deployment_for_all_namespaces().items

        except ApiException as e:
            result.success = False
            result.error = str(e)
            return result

        healthy = 0
        unhealthy = 0
        available = 0
        partial = 0
        failed_rollouts = 0

        for dep in deployments:

            status = dep.status

            name = dep.metadata.name
            namespace = dep.metadata.namespace

            replicas = dep.spec.replicas or 0
            ready_replicas = status.ready_replicas or 0
            available_replicas = status.available_replicas or 0
            updated_replicas = status.updated_replicas or 0
            unavailable_replicas = status.unavailable_replicas or 0

            conditions = []
            if status.conditions:
                conditions = [
                    {
                        "type": c.type,
                        "status": c.status,
                        "reason": c.reason,
                        "message": c.message,
                    }
                    for c in status.conditions
                ]

            images = []
            if dep.spec.template.spec.containers:
                images = [c.image for c in dep.spec.template.spec.containers]

            deployment_resource = {
                "name": name,
                "namespace": namespace,
                "uid": dep.metadata.uid,
                "creation_timestamp": str(dep.metadata.creation_timestamp),

                "replicas": replicas,
                "ready_replicas": ready_replicas,
                "available_replicas": available_replicas,
                "updated_replicas": updated_replicas,
                "unavailable_replicas": unavailable_replicas,

                "generation": dep.metadata.generation,
                "observed_generation": status.observed_generation,

                "strategy": dep.spec.strategy.type if dep.spec.strategy else None,
                "min_ready_seconds": dep.spec.min_ready_seconds,

                "selector": dep.spec.selector.match_labels if dep.spec.selector else None,

                "images": images,
                "conditions": conditions,

                "labels": dep.metadata.labels,
                "annotations": dep.metadata.annotations,
            }

            result.resources.append(deployment_resource)

            # -----------------------------
            # Health evaluation
            # -----------------------------

            if ready_replicas == replicas and replicas > 0:
                healthy += 1
                available += 1

            elif ready_replicas == 0:
                unhealthy += 1
                failed_rollouts += 1

            else:
                partial += 1

            if unavailable_replicas and unavailable_replicas > 0:
                unhealthy += 1

        # -----------------------------
        # Metrics
        # -----------------------------

        result.metrics.extend([
            {"metric": "deployment_count", "value": len(deployments)},
            {"metric": "healthy_deployments", "value": healthy},
            {"metric": "unhealthy_deployments", "value": unhealthy},
            {"metric": "fully_available_deployments", "value": available},
            {"metric": "partially_available_deployments", "value": partial},
            {"metric": "failed_rollouts", "value": failed_rollouts},
        ])

        return result