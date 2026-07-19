from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class ReplicaSetCollector(BaseCollector):

    name = "ReplicaSetCollector"

    def collect(self, k8s):

        result = CollectResult(
            collector=self.name
        )

        try:
            replicasets = k8s.apps.list_replica_set_for_all_namespaces().items

            result.metadata = {
                "cluster_name": k8s.target.name,
                "context": k8s.target.context,
                "namespace": k8s.target.namespace,
                "cluster_wide": k8s.target.cluster_wide,
            }

            result.metrics.append({
                "metric": "replicaset_count",
                "value": len(replicasets),
            })

            total_replicas = 0
            ready_replicas = 0

            for rs in replicasets:
                spec_replicas = rs.spec.replicas or 0
                status_ready = rs.status.ready_replicas or 0

                total_replicas += spec_replicas
                ready_replicas += status_ready

                result.resources.append({
                    "name": rs.metadata.name,
                    "namespace": rs.metadata.namespace,
                    "desired_replicas": spec_replicas,
                    "ready_replicas": status_ready,
                    "available_replicas": getattr(rs.status, "available_replicas", 0),
                    "labels": rs.metadata.labels,
                })

            result.metrics.extend([
                {
                    "metric": "total_desired_replicas",
                    "value": total_replicas,
                },
                {
                    "metric": "total_ready_replicas",
                    "value": ready_replicas,
                },
            ])

        except ApiException as e:
            result.success = False
            result.error = str(e)

            

        except Exception as e:
            result.success = False
            result.error = str(e)

            

        