from pprint import pprint

from rootiq.collectors.node import NodeCollector
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


def test_node_collector():

    target = ClusterTarget(
        name="Local",
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    )

    k8s = KubernetesClient(target)

    collector = NodeCollector()

    result = collector.run(k8s)

    pprint(result)


if __name__ == "__main__":
    test_node_collector()