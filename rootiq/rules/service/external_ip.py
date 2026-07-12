from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class ServiceExternalIPRule(BaseRule):

    id = "SERVICE-006"

    name = "ServiceExternalIP"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for service in resources:

            namespace = service.get("namespace")
            name = service.get("name")

            service_type = service.get("type")

            external_ips = service.get("external_ips", [])

            external_name = service.get("external_name")

            #
            # ExternalName Service
            #

            if service_type == "ExternalName":

                if not external_name:

                    result.issues.append(
                        Issue(
                            id=self.id,
                            severity="High",
                            resource_type="Service",
                            resource_name=name,
                            namespace=namespace,
                            title="ExternalName Service has no external name",
                            description=(
                                "ExternalName Service is missing the external DNS name."
                            ),
                            evidence={
                                "external_name": external_name,
                            },
                            recommendation=(
                                "Configure spec.externalName."
                            ),
                        )
                    )

                continue

            #
            # Duplicate External IPs
            #

            if len(external_ips) != len(set(external_ips)):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Medium",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="Duplicate external IPs",
                        description=(
                            "The Service contains duplicate external IP entries."
                        ),
                        evidence={
                            "external_ips": external_ips,
                        },
                        recommendation=(
                            "Remove duplicate external IP addresses."
                        ),
                    )
                )

            #
            # Invalid External IPs
            #

            for ip in external_ips:

                if not isinstance(ip, str):

                    result.issues.append(
                        Issue(
                            id=self.id,
                            severity="Medium",
                            resource_type="Service",
                            resource_name=name,
                            namespace=namespace,
                            title="Invalid external IP",
                            description=(
                                "Service contains an invalid external IP."
                            ),
                            evidence={
                                "external_ip": ip,
                            },
                            recommendation=(
                                "Configure valid IPv4 or IPv6 addresses."
                            ),
                        )
                    )

        return result