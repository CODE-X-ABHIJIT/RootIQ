from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class NamespaceCollector(BaseCollector):

    name = "NamespaceCollector"

    def collect(self, k8s):

        result = CollectResult(collector=self.name)

        try:

            namespaces = k8s.core.list_namespace().items

            result.metrics.append(
                {
                    "metric": "namespace_count",
                    "value": len(namespaces),
                }
            )

            active = 0
            terminating = 0

            for ns in namespaces:

                if ns.status.phase == "Active":
                    active += 1
                else:
                    terminating += 1

                result.resources.append(
                    {
                        "name": ns.metadata.name,
                        "status": ns.status.phase,
                        "creation_timestamp": (
                            ns.metadata.creation_timestamp.isoformat()
                            if ns.metadata.creation_timestamp
                            else None
                        ),
                        "labels": ns.metadata.labels or {},
                        "annotations": ns.metadata.annotations or {},
                    }
                )

            result.metrics.extend(
                [
                    {
                        "metric": "active_namespaces",
                        "value": active,
                    },
                    {
                        "metric": "terminating_namespaces",
                        "value": terminating,
                    },
                ]
            )

        except ApiException as e:

            result.success = False
            result.error = str(e)

        