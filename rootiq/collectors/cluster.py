from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class ClusterCollector(BaseCollector):

    name = "ClusterCollector"

    def collect(self, k8s):

        result = CollectResult(
            collector=self.name
        )

        # ==========================================
        # Cluster Information
        # ==========================================

        try:

            version = k8s.version.get_code()

            result.metadata = {
                "cluster_name": k8s.target.name,
                "context": k8s.current_context(),
                "namespace": k8s.target.namespace,
                "cluster_wide": k8s.target.cluster_wide,
                "api_server": k8s.api_server(),
                "kubernetes_version": (
                    f"{version.major}.{version.minor}"
                ),
                "platform": k8s.target.platform,
                "provider": k8s.target.provider,
                "environment": k8s.target.environment,
                "region": k8s.target.region,
            }

        except ApiException as e:

            result.success = False
            result.error = str(e)

            return result

        # ==========================================
        # Nodes
        # ==========================================

        try:

            nodes = k8s.nodes()

            result.metrics.append(
                {
                    "metric": "node_count",
                    "value": len(nodes),
                }
            )

            control_planes = 0
            workers = 0

            for node in nodes:

                labels = node.metadata.labels or {}

                if (
                    "node-role.kubernetes.io/control-plane"
                    in labels
                ):
                    control_planes += 1
                else:
                    workers += 1

            result.metrics.extend(
                [
                    {
                        "metric": "control_plane_nodes",
                        "value": control_planes,
                    },
                    {
                        "metric": "worker_nodes",
                        "value": workers,
                    },
                ]
            )

        except Exception as e:

            result.logs.append(
                {
                    "level": "warning",
                    "message": str(e),
                }
            )

        # ==========================================
        # Namespaces
        # ==========================================

        try:

            namespaces = k8s.namespaces()

            result.metrics.append(
                {
                    "metric": "namespace_count",
                    "value": len(namespaces),
                }
            )

        except Exception as e:

            result.logs.append(
                {
                    "level": "warning",
                    "message": str(e),
                }
            )

        return result