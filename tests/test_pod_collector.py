from rootiq.collectors.pods import PodCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


target = ClusterTarget(
    name="FinOps Lab",
    context="kind-finops-lab",
    cluster_wide=True,
)

k8s = KubernetesClient(target)

collector = PodCollector()

result = collector.run(k8s)

print(result)
