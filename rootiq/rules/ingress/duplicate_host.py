from collections import defaultdict

from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class IngressDuplicateHostRule(BaseRule):

    id = "INGRESS-009"

    name = "IngressDuplicateHost"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        host_map = defaultdict(list)

        #
        # Build host index
        #

        for ingress in resources:

            namespace = ingress.get("namespace")
            name = ingress.get("name")

            for rule in ingress.get(
                "rules",
                [],
            ):

                host = rule.get("host")

                if not host:
                    continue

                host_map[host].append(
                    {
                        "namespace": namespace,
                        "name": name,
                    }
                )

        #
        # Detect duplicates
        #

        for host, ingresses in host_map.items():

            if len(ingresses) <= 1:
                continue

            result.issues.append(
                Issue(
                    id=self.id,
                    severity="High",
                    resource_type="Ingress",
                    resource_name="Multiple",
                    namespace="Cluster",
                    title="Duplicate Ingress host detected",
                    description=(
                        "The same hostname is configured in multiple Ingress resources."
                    ),
                    evidence={
                        "host": host,
                        "ingresses": ingresses,
                    },
                    recommendation=(
                        "Ensure only one Ingress owns a hostname or intentionally merge the routing rules."
                    ),
                )
            )

        return result