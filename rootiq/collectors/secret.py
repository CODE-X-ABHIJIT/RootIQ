from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class SecretCollector(BaseCollector):

    name = "SecretCollector"

    def collect(self, k8s):

        result = CollectResult(collector=self.name)

        try:

            if k8s.target.cluster_wide:

                secrets = (
                    k8s.core.list_secret_for_all_namespaces().items
                )

            else:

                secrets = (
                    k8s.core.list_namespaced_secret(
                        namespace=k8s.target.namespace
                    ).items
                )

            result.metrics.append(
                {
                    "metric": "secret_count",
                    "value": len(secrets),
                }
            )

            type_counts = {}

            for secret in secrets:

                secret_type = secret.type or "Unknown"

                type_counts[secret_type] = (
                    type_counts.get(secret_type, 0) + 1
                )

                result.resources.append(
                    {
                        "name": secret.metadata.name,
                        "namespace": secret.metadata.namespace,
                        "type": secret_type,
                        "keys": list((secret.data or {}).keys()),
                        "creation_timestamp": (
                            secret.metadata.creation_timestamp.isoformat()
                            if secret.metadata.creation_timestamp
                            else None
                        ),
                    }
                )

            for secret_type, count in type_counts.items():

                result.metrics.append(
                    {
                        "metric": f"secret_type_{secret_type}",
                        "value": count,
                    }
                )

        except ApiException as e:

            result.success = False
            result.error = str(e)

        return result