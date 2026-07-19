from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class PVCollector(BaseCollector):

    name = "PVCollector"

    def collect(self, k8s):

        result = CollectResult(collector=self.name)

        try:

            pvs = k8s.core.list_persistent_volume().items

            result.metrics.append(
                {
                    "metric": "pv_count",
                    "value": len(pvs),
                }
            )

            for pv in pvs:

                result.resources.append(
                    {
                        "name": pv.metadata.name,
                        "capacity": (
                            pv.spec.capacity.get("storage")
                            if pv.spec.capacity else None
                        ),
                        "access_modes": pv.spec.access_modes,
                        "reclaim_policy": pv.spec.persistent_volume_reclaim_policy,
                        "status": pv.status.phase,
                        "storage_class": pv.spec.storage_class_name,
                        "claim": (
                            f"{pv.spec.claim_ref.namespace}/{pv.spec.claim_ref.name}"
                            if pv.spec.claim_ref else None
                        ),
                    }
                )

        except ApiException as e:

            result.success = False
            result.error = str(e)

        