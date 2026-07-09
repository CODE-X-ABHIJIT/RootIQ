from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class ConfigMapCollector(BaseCollector):

    name = "ConfigMapCollector"

    def collect(self, k8s):

        result = CollectResult(collector=self.name)

        try:

            if k8s.target.cluster_wide:
                configmaps = k8s.core.list_config_map_for_all_namespaces().items
            else:
                configmaps = k8s.core.list_namespaced_config_map(
                    namespace=k8s.target.namespace
                ).items

        except ApiException as e:

            result.success = False
            result.error = str(e)
            return result

        total_keys = 0

        for cm in configmaps:

            data = cm.data or {}
            binary = cm.binary_data or {}

            total_keys += len(data) + len(binary)

            result.resources.append(
                {
                    "name": cm.metadata.name,
                    "namespace": cm.metadata.namespace,
                    "uid": cm.metadata.uid,
                    "creation_timestamp": str(cm.metadata.creation_timestamp),
                    "labels": cm.metadata.labels or {},
                    "annotations": cm.metadata.annotations or {},
                    "immutable": getattr(cm, "immutable", False),
                    "data_keys": list(data.keys()),
                    "binary_keys": list(binary.keys()),
                    "data_count": len(data),
                    "binary_count": len(binary),
                }
            )

        result.metrics.extend(
            [
                {
                    "metric": "configmap_count",
                    "value": len(configmaps),
                },
                {
                    "metric": "configmap_keys",
                    "value": total_keys,
                },
            ]
        )

        return result