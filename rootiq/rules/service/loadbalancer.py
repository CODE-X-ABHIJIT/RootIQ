from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class ServiceLoadBalancerRule(BaseRule):

    id = "SERVICE-004"

    name = "ServiceLoadBalancer"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for service in resources:

            namespace = service.get("namespace")
            name = service.get("name")

            if service.get("type") != "LoadBalancer":
                continue

            external_ip = service.get("external_ip")
            load_balancer = service.get("load_balancer", {})
            annotations = service.get("annotations", {})

            #
            # No external IP assigned
            #

            if not external_ip:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="High",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="LoadBalancer has no external IP",
                        description=(
                            "The LoadBalancer Service is waiting for an external IP."
                        ),
                        evidence={
                            "external_ip": external_ip,
                        },
                        recommendation=(
                            "Verify your cloud provider, MetalLB, or load balancer controller."
                        ),
                    )
                )

            #
            # No ingress
            #

            ingress = load_balancer.get("ingress", [])

            if not ingress:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Medium",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="LoadBalancer ingress unavailable",
                        description=(
                            "No LoadBalancer ingress has been provisioned."
                        ),
                        evidence={
                            "ingress": ingress,
                        },
                        recommendation=(
                            "Check cloud provider events or MetalLB logs."
                        ),
                    )
                )

            #
            # Pending status
            #

            if (
                not external_ip
                and not ingress
            ):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Critical",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="LoadBalancer provisioning pending",
                        description=(
                            "The Service has not yet been provisioned by the load balancer."
                        ),
                        evidence={
                            "type": "Pending",
                        },
                        recommendation=(
                            "Verify the LoadBalancer controller is running."
                        ),
                    )
                )

            #
            # Internal LoadBalancer
            #

            internal = any(
                "internal" in key.lower()
                for key in annotations.keys()
            )

            if internal:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Info",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="Internal LoadBalancer detected",
                        description=(
                            "The Service is configured as an internal LoadBalancer."
                        ),
                        evidence={
                            "annotations": annotations,
                        },
                        recommendation=(
                            "Ensure internal exposure is intended."
                        ),
                    )
                )

        return result