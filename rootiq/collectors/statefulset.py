# rootiq/collectors/statefulset.py

from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class StatefulSetCollector(BaseCollector):

    name = "StatefulSetCollector"

    def collect(self, k8s):

        result = CollectResult(collector=self.name)

        try:

            if k8s.target.cluster_wide:

                statefulsets = (
                    k8s.apps.list_stateful_set_for_all_namespaces().items
                )

            else:

                statefulsets = (
                    k8s.apps.list_namespaced_stateful_set(
                        namespace=k8s.target.namespace
                    ).items
                )

        except ApiException as e:

            result.success = False
            result.error = str(e)

            

        total_desired = 0
        total_ready = 0

        for sts in statefulsets:

            desired = sts.spec.replicas or 0
            ready = sts.status.ready_replicas or 0
            current = sts.status.current_replicas or 0
            updated = sts.status.updated_replicas or 0

            total_desired += desired
            total_ready += ready

            containers = []

            for container in sts.spec.template.spec.containers:

                containers.append(
                    {
                        "name": container.name,
                        "image": container.image,
                    }
                )

            pvc_templates = []

            for pvc in sts.spec.volume_claim_templates:

                pvc_templates.append(
                    {
                        "name": pvc.metadata.name,
                        "storage_class": pvc.spec.storage_class_name,
                        "access_modes": pvc.spec.access_modes,
                    }
                )

            conditions = []

            if sts.status.conditions:

                for condition in sts.status.conditions:

                    conditions.append(
                        {
                            "type": condition.type,
                            "status": condition.status,
                            "reason": condition.reason,
                            "message": condition.message,
                        }
                    )

            owner = None

            if sts.metadata.owner_references:

                owner = sts.metadata.owner_references[0].kind

            result.resources.append(
                {
                    "name": sts.metadata.name,
                    "namespace": sts.metadata.namespace,
                    "uid": sts.metadata.uid,
                    "service_name": sts.spec.service_name,
                    "desired_replicas": desired,
                    "ready_replicas": ready,
                    "current_replicas": current,
                    "updated_replicas": updated,
                    "update_strategy": (
                        sts.spec.update_strategy.type
                        if sts.spec.update_strategy
                        else None
                    ),
                    "pod_management_policy": sts.spec.pod_management_policy,
                    "revision_history_limit": (
                        sts.spec.revision_history_limit
                    ),
                    "creation_timestamp": (
                        sts.metadata.creation_timestamp.isoformat()
                        if sts.metadata.creation_timestamp
                        else None
                    ),
                    "labels": sts.metadata.labels or {},
                    "annotations": sts.metadata.annotations or {},
                    "owner": owner,
                    "containers": containers,
                    "volume_claim_templates": pvc_templates,
                    "conditions": conditions,
                }
            )

            if ready < desired:

                context.report(
                    {
                        "severity": "warning",
                        "resource": sts.metadata.name,
                        "namespace": sts.metadata.namespace,
                        "message": (
                            f"Ready replicas {ready}/{desired}"
                        ),
                    }
                )

            if not sts.spec.service_name:

                context.report(
                    {
                        "severity": "warning",
                        "resource": sts.metadata.name,
                        "namespace": sts.metadata.namespace,
                        "message": "No Headless Service configured.",
                    }
                )

            if updated < desired:

                result.logs.append(
                    {
                        "level": "warning",
                        "message": (
                            f"{sts.metadata.name} rollout not fully updated."
                        ),
                    }
                )

        result.metrics.extend(
            [
                {
                    "metric": "statefulset_count",
                    "value": len(statefulsets),
                },
                {
                    "metric": "desired_replicas",
                    "value": total_desired,
                },
                {
                    "metric": "ready_replicas",
                    "value": total_ready,
                },
            ]
        )

        