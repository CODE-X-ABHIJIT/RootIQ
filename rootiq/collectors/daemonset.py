# rootiq/collectors/daemonset.py

from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class DaemonSetCollector(BaseCollector):

    name = "DaemonSetCollector"

    def collect(self, k8s):

        result = CollectResult(collector=self.name)

        try:

            if k8s.target.cluster_wide:

                daemonsets = (
                    k8s.apps.list_daemon_set_for_all_namespaces().items
                )

            else:

                daemonsets = (
                    k8s.apps.list_namespaced_daemon_set(
                        namespace=k8s.target.namespace
                    ).items
                )

        except ApiException as e:

            result.success = False
            result.error = str(e)
            

        total_desired = 0
        total_ready = 0
        total_available = 0

        for ds in daemonsets:

            desired = ds.status.desired_number_scheduled or 0
            current = ds.status.current_number_scheduled or 0
            ready = ds.status.number_ready or 0
            available = ds.status.number_available or 0
            unavailable = ds.status.number_unavailable or 0
            updated = ds.status.updated_number_scheduled or 0

            total_desired += desired
            total_ready += ready
            total_available += available

            containers = []

            for c in ds.spec.template.spec.containers:

                containers.append(
                    {
                        "name": c.name,
                        "image": c.image,
                    }
                )

            conditions = []

            if ds.status.conditions:

                for cond in ds.status.conditions:

                    conditions.append(
                        {
                            "type": cond.type,
                            "status": cond.status,
                            "reason": cond.reason,
                            "message": cond.message,
                        }
                    )

            owner = None

            if ds.metadata.owner_references:

                owner = ds.metadata.owner_references[0].kind

            result.resources.append(
                {
                    "name": ds.metadata.name,
                    "namespace": ds.metadata.namespace,
                    "uid": ds.metadata.uid,
                    "desired_number_scheduled": desired,
                    "current_number_scheduled": current,
                    "number_ready": ready,
                    "number_available": available,
                    "number_unavailable": unavailable,
                    "updated_number_scheduled": updated,
                    "update_strategy": (
                        ds.spec.update_strategy.type
                        if ds.spec.update_strategy
                        else None
                    ),
                    "min_ready_seconds": ds.spec.min_ready_seconds,
                    "creation_timestamp": (
                        ds.metadata.creation_timestamp.isoformat()
                        if ds.metadata.creation_timestamp
                        else None
                    ),
                    "labels": ds.metadata.labels or {},
                    "annotations": ds.metadata.annotations or {},
                    "owner": owner,
                    "containers": containers,
                    "conditions": conditions,
                }
            )

            if ready < desired:

                context.report(
                    {
                        "severity": "warning",
                        "resource": ds.metadata.name,
                        "namespace": ds.metadata.namespace,
                        "message": f"Ready pods {ready}/{desired}",
                    }
                )

            if unavailable > 0:

                context.report(
                    {
                        "severity": "warning",
                        "resource": ds.metadata.name,
                        "namespace": ds.metadata.namespace,
                        "message": f"{unavailable} unavailable daemon pods.",
                    }
                )

            if updated < desired:

                result.logs.append(
                    {
                        "level": "warning",
                        "message": (
                            f"{ds.metadata.name} rollout is still in progress."
                        ),
                    }
                )

        result.metrics.extend(
            [
                {
                    "metric": "daemonset_count",
                    "value": len(daemonsets),
                },
                {
                    "metric": "desired_pods",
                    "value": total_desired,
                },
                {
                    "metric": "ready_pods",
                    "value": total_ready,
                },
                {
                    "metric": "available_pods",
                    "value": total_available,
                },
            ]
        )

        