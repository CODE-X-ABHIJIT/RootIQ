from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class IngressHostRule(BaseRule):

    id = "INGRESS-004"

    name = "IngressHost"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for ingress in resources:

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

                    result.issues.append(
                        Issue(
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
                    )

                    continue

                #
                # Duplicate Host
                #

                if host in seen_hosts:

                    result.issues.append(
                        Issue(
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
                    )

                else:

                    seen_hosts.add(host)

                #
                # Wildcard Host
                #

                if host.startswith("*."):

                    result.issues.append(
                        Issue(
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

                    result.issues.append(
                        Issue(
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
                    )

                #
                # localhost usage
                #

                if host.lower() == "localhost":

                    result.issues.append(
                        Issue(
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
                    )

        return result