from rootiq.collectors.cluster import ClusterCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


target = ClusterTarget(
    name="Local",
    context="kind-finops-lab",
    namespace="default",
    cluster_wide=True,
)

k8s = KubernetesClient(target)

collector = ClusterCollector()

result = collector.run(k8s)

print(result)
