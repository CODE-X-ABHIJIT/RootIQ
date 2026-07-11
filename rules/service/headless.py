from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class ServiceHeadlessRule(BaseRule):

    id = "SERVICE-007"

    name = "ServiceHeadless"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for service in resources:

            namespace = service.get("namespace")
            name = service.get("name")

            cluster_ip = service.get("cluster_ip")
            endpoints = service.get("endpoints", [])
            selector = service.get("selector", {})

            #
            # Not a Headless Service
            #

            if cluster_ip != "None":
                continue

            #
            # No endpoints
            #

            if not endpoints:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="High",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="Headless Service has no endpoints",
                        description=(
                            "The Headless Service is not routing to any Pods."
                        ),
                        evidence={
                            "cluster_ip": cluster_ip,
                            "endpoints": endpoints,
                        },
                        recommendation=(
                            "Verify Pod labels and Service selector."
                        ),
                    )
                )

            #
            # Missing selector
            #

            if not selector:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Medium",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="Headless Service has no selector",
                        description=(
                            "The Headless Service does not define a selector."
                        ),
                        evidence={
                            "selector": selector,
                        },
                        recommendation=(
                            "Configure a selector or manage Endpoints manually."
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
                            "Multiple endpoint entries share the same IP."
                        ),
                        evidence={
                            "endpoint_ips": ips,
                        },
                        recommendation=(
                            "Verify EndpointSlice or manually managed Endpoints."
                        ),
                    )
                )

        return result