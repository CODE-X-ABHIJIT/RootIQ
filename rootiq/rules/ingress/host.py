from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class IngressHostRule(BaseRule):

    id = "INGRESS-004"

    name = "IngressHost"

    resource_type = "ingress"

    def evaluate(self, context: RuleContext):

        

        for ingress in context.resources:

            namespace = ingress.get("namespace")
            name = ingress.get("name")

            rules = ingress.get("rules", [])

            if not rules:

                continue

            seen_hosts = set()

            for rule in rules:

                host = rule.get("host")

                #
                # Missing Host
                #

                if not host:

                    context.report(
                        
                            id=self.id,
                            severity="Medium",
                            resource_type="Ingress",
                            resource_name=name,
                            namespace=namespace,
                            title="Ingress rule has no host",
                            description=(
                                "The Ingress rule does not specify a host."
                            ),
                            evidence={
                                "rule": rule,
                            },
                            recommendation=(
                                "Specify a hostname unless a catch-all rule is intended."
                            ),
                        )
                    

                    continue

                #
                # Duplicate Host
                #

                if host in seen_hosts:

                    context.report(
                        
                            id=self.id,
                            severity="Medium",
                            resource_type="Ingress",
                            resource_name=name,
                            namespace=namespace,
                            title="Duplicate host",
                            description=(
                                "The same host appears multiple times in the Ingress."
                            ),
                            evidence={
                                "host": host,
                            },
                            recommendation=(
                                "Merge duplicate host rules."
                            ),
                        )
                    
                else:

                    seen_hosts.add(host)

                #
                # Wildcard Host
                #

                if host.startswith("*."):

                    context.report(
                        
                            id=self.id,
                            severity="Info",
                            resource_type="Ingress",
                            resource_name=name,
                            namespace=namespace,
                            title="Wildcard host detected",
                            description=(
                                "Ingress uses a wildcard hostname."
                            ),
                            evidence={
                                "host": host,
                            },
                            recommendation=(
                                "Verify wildcard routing is intentional."
                            ),
                        )
                    

                #
                # Invalid hostname
                #

                if (
                    " " in host
                    or host.startswith(".")
                    or host.endswith(".")
                    or ".." in host
                ):

                    context.report(
                        
                            id=self.id,
                            severity="High",
                            resource_type="Ingress",
                            resource_name=name,
                            namespace=namespace,
                            title="Invalid hostname",
                            description=(
                                "Ingress contains an invalid hostname."
                            ),
                            evidence={
                                "host": host,
                            },
                            recommendation=(
                                "Use a valid RFC-compliant DNS hostname."
                            ),
                        )
                    

                #
                # localhost usage
                #

                if host.lower() == "localhost":

                    context.report(
                        
                            id=self.id,
                            severity="Low",
                            resource_type="Ingress",
                            resource_name=name,
                            namespace=namespace,
                            title="Localhost host configured",
                            description=(
                                "Ingress routes traffic for localhost."
                            ),
                            evidence={
                                "host": host,
                            },
                            recommendation=(
                                "Avoid localhost in production environments."
                            ),
                        )
                    

        