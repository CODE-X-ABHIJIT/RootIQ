from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class HPACollector(BaseCollector):

    name = "HPACollector"

    def collect(self, k8s):

        result = CollectResult(collector=self.name)

        try:

            api = k8s.custom

            if k8s.target.cluster_wide:

                hpas = api.list_cluster_custom_object(
                    group="autoscaling",
                    version="v2",
                    plural="horizontalpodautoscalers",
                )["items"]

            else:

                hpas = api.list_namespaced_custom_object(
                    group="autoscaling",
                    version="v2",
                    namespace=k8s.target.namespace,
                    plural="horizontalpodautoscalers",
                )["items"]

            result.metrics.append(
                {
                    "metric": "hpa_count",
                    "value": len(hpas),
                }
            )

            for hpa in hpas:

                spec = hpa.get("spec", {})
                status = hpa.get("status", {})

                result.resources.append(
                    {
                        "name": hpa["metadata"]["name"],
                        "namespace": hpa["metadata"]["namespace"],
                        "target": spec.get("scaleTargetRef", {}),
                        "min_replicas": spec.get("minReplicas"),
                        "max_replicas": spec.get("maxReplicas"),
                        "current_replicas": status.get("currentReplicas"),
                        "desired_replicas": status.get("desiredReplicas"),
                    }
                )

        except ApiException as e:

            result.success = False
            result.error = str(e)

        return result