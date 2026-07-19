# rootiq/collectors/pvc.py

from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class PVCCollector(BaseCollector):

    name = "PVCCollector"

    def collect(self, k8s):

        result = CollectResult(collector=self.name)

        try:

            if k8s.target.cluster_wide:

                pvcs = (
                    k8s.core.list_persistent_volume_claim_for_all_namespaces().items
                )

            else:

                pvcs = (
                    k8s.core.list_namespaced_persistent_volume_claim(
                        namespace=k8s.target.namespace
                    ).items
                )

        except ApiException as e:

            result.success = False
            result.error = str(e)
            

        bound = 0
        pending = 0
        lost = 0

        for pvc in pvcs:

            phase = pvc.status.phase

            if phase == "Bound":
                bound += 1
            elif phase == "Pending":
                pending += 1
            elif phase == "Lost":
                lost += 1

            capacity = {}

            if pvc.status.capacity:

                capacity = dict(pvc.status.capacity)

            requests = {}

            if pvc.spec.resources and pvc.spec.resources.requests:

                requests = dict(pvc.spec.resources.requests)

            access_modes = pvc.status.access_modes or []

            volume_mode = pvc.spec.volume_mode

            result.resources.append(
                {
                    "name": pvc.metadata.name,
                    "namespace": pvc.metadata.namespace,
                    "uid": pvc.metadata.uid,
                    "phase": phase,
                    "volume_name": pvc.spec.volume_name,
                    "storage_class": pvc.spec.storage_class_name,
                    "access_modes": access_modes,
                    "volume_mode": volume_mode,
                    "capacity": capacity,
                    "requests": requests,
                    "labels": pvc.metadata.labels or {},
                    "annotations": pvc.metadata.annotations or {},
                    "creation_timestamp": (
                        pvc.metadata.creation_timestamp.isoformat()
                        if pvc.metadata.creation_timestamp
                        else None
                    ),
                }
            )

            if phase == "Pending":

                context.report(
                    {
                        "severity": "critical",
                        "resource": pvc.metadata.name,
                        "namespace": pvc.metadata.namespace,
                        "message": "PVC is Pending.",
                    }
                )

            if phase == "Lost":

                context.report(
                    {
                        "severity": "critical",
                        "resource": pvc.metadata.name,
                        "namespace": pvc.metadata.namespace,
                        "message": "PVC is Lost.",
                    }
                )

            if not pvc.spec.storage_class_name:

                result.logs.append(
                    {
                        "level": "warning",
                        "message": (
                            f"{pvc.metadata.name} has no StorageClass."
                        ),
                    }
                )

        result.metrics.extend(
            [
                {
                    "metric": "pvc_count",
                    "value": len(pvcs),
                },
                {
                    "metric": "bound_pvcs",
                    "value": bound,
                },
                {
                    "metric": "pending_pvcs",
                    "value": pending,
                },
                {
                    "metric": "lost_pvcs",
                    "value": lost,
                },
            ]
        )

        