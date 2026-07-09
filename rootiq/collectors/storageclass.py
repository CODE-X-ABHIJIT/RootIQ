from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class StorageClassCollector(BaseCollector):

    name = "StorageClassCollector"

    def collect(self, k8s):

        result = CollectResult(collector=self.name)

        try:

            storage_classes = (
                k8s.storage.list_storage_class().items
            )

            result.metrics.append(
                {
                    "metric": "storageclass_count",
                    "value": len(storage_classes),
                }
            )

            for sc in storage_classes:

                result.resources.append(
                    {
                        "name": sc.metadata.name,
                        "provisioner": sc.provisioner,
                        "reclaim_policy": sc.reclaim_policy,
                        "volume_binding_mode": sc.volume_binding_mode,
                        "allow_volume_expansion": sc.allow_volume_expansion,
                        "is_default": (
                            sc.metadata.annotations.get(
                                "storageclass.kubernetes.io/is-default-class"
                            )
                            == "true"
                            if sc.metadata.annotations
                            else False
                        ),
                        "parameters": sc.parameters or {},
                    }
                )

        except ApiException as e:

            result.success = False
            result.error = str(e)

        return result