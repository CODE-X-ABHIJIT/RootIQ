from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class ServiceEndpointsRule(BaseRule):

    id = "SERVICE-002"

    name = "ServiceEndpoints"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for service in resources:

            namespace = service.get("namespace")
            name = service.get("name")

            service_type = service.get("type")

            endpoints = service.get("endpoints", [])

            #
            # ExternalName services do not have endpoints
            #

            if service_type == "ExternalName":
                continue

            #
            # No endpoints
            #

            if len(endpoints) == 0:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Critical",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="Service has no endpoints",
                        description=(
                            "No Pods are currently backing this Service."
                        ),
                        evidence={
                            "endpoints": endpoints,
                        },
                        recommendation=(
                            "Verify the Service selector, Pod labels, and Pod readiness."
                        ),
                    )
                )

                continue

            #
            # Some endpoints not ready
            #

            not_ready = [
                ep
                for ep in endpoints
                if not ep.get("ready", True)
            ]

            if not_ready:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Medium",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="Service has unhealthy endpoints",
                        description=(
                            "One or more backend Pods are not Ready."
                        ),
                        evidence={
                            "total_endpoints": len(endpoints),
                            "unhealthy_endpoints": len(not_ready),
                            "details": not_ready,
                        },
                        recommendation=(
                            "Investigate Pod readiness probes and application health."
                        ),
                    )
                )

            #
            # Duplicate endpoint IPs
            #

            ips = [
                ep.get("ip")
                for ep in endpoints
                if ep.get("ip")
            ]

            if len(ips) != len(set(ips)):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Low",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="Duplicate endpoints detected",
                        description=(
                            "Duplicate endpoint IPs were found."
                        ),
                        evidence={
                            "endpoint_ips": ips,
                        },
                        recommendation=(
                            "Verify EndpointSlice and Service configuration."
                        ),
                    )
                )

        return result