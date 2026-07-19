from collections import defaultdict

from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class IngressDuplicateHostRule(BaseRule):

    id = "INGRESS-009"

    name = "IngressDuplicateHost"

    resource_type = "ingress"

    def evaluate(self, context: RuleContext):

        

        host_map = defaultdict(list)

        #
        # Build host index
        #

        for ingress in context.resources:

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

            context.report(
                
                    id=self.id,
                    severity="High",
                    resource_type="Ingress",
                    resource_name="Multiple",
                    namespace="Cluster",
                    title="Duplicate Ingress host detected",
                    description=(
                        "The same hostname is configured in multiple Ingress context.resources."
                    ),
                    evidence={
                        "host": host,
                        "ingresses": ingresses,
                    },
                    recommendation=(
                        "Ensure only one Ingress owns a hostname or intentionally merge the routing rules."
                    ),
                )
            

        