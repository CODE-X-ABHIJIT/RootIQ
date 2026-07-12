from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class ServiceExternalTrafficPolicyRule(BaseRule):

    id = "SERVICE-010"

    name = "ServiceExternalTrafficPolicy"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for service in resources:

            namespace = service.get("namespace")
            name = service.get("name")

            service_type = service.get("type")

            #
            # Only NodePort and LoadBalancer support this
            #

            if service_type not in (
                "NodePort",
                "LoadBalancer",
            ):
                continue

            policy = service.get(
                "external_traffic_policy",
                "Cluster",
            )

            health_port = service.get(
                "health_check_node_port"
            )

            endpoints = service.get(
                "endpoints",
                [],
            )

            #
            # Invalid policy
            #

            if policy not in (
                "Cluster",
                "Local",
            ):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Medium",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="Invalid externalTrafficPolicy",
                        description=(
                            "Unsupported externalTrafficPolicy value."
                        ),
                        evidence={
                            "external_traffic_policy": policy,
                        },
                        recommendation=(
                            "Use either Cluster or Local."
                        ),
                    )
                )

                continue

            #
            # Local mode but no endpoints
            #

            if (
                policy == "Local"
                and not endpoints
            ):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="High",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="Local traffic policy without endpoints",
                        description=(
                            "Service uses Local routing but has no available endpoints."
                        ),
                        evidence={
                            "external_traffic_policy": policy,
                            "endpoint_count": 0,
                        },
                        recommendation=(
                            "Ensure Pods are running on nodes receiving external traffic."
                        ),
                    )
                )

            #
            # HealthCheckNodePort missing
            #

            if (
                service_type == "LoadBalancer"
                and policy == "Local"
                and not health_port
            ):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Low",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="HealthCheckNodePort not configured",
                        description=(
                            "LoadBalancer using Local policy has no HealthCheckNodePort."
                        ),
                        evidence={
                            "health_check_node_port": health_port,
                        },
                        recommendation=(
                            "Verify the cloud provider or load balancer controller configuration."
                        ),
                    )
                )

            #
            # Invalid HealthCheckNodePort
            #

            if (
                health_port
                and (
                    health_port < 30000
                    or health_port > 32767
                )
            ):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Medium",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="Invalid HealthCheckNodePort",
                        description=(
                            "HealthCheckNodePort is outside the default Kubernetes NodePort range."
                        ),
                        evidence={
                            "health_check_node_port": health_port,
                        },
                        recommendation=(
                            "Use a value between 30000 and 32767 unless your cluster is configured differently."
                        ),
                    )
                )

        return result