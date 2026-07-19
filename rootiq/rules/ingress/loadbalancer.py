from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class IngressLoadBalancerRule(BaseRule):

    id = "INGRESS-008"

    name = "IngressLoadBalancer"

    resource_type = "ingress"

    def evaluate(self, context: RuleContext):

        

        for ingress in context.resources:

            namespace = ingress.get("namespace")
            name = ingress.get("name")

            lb = ingress.get(
                "load_balancer",
                [],
            )

            #
            # No LoadBalancer assigned
            #

            if not lb:

                context.report(
                    
                        id=self.id,
                        severity="Medium",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="Ingress has no LoadBalancer address",
                        description=(
                            "The Ingress has not yet been assigned an external IP or hostname."
                        ),
                        evidence={},
                        recommendation=(
                            "Verify the Ingress Controller is running and the cloud provider or LoadBalancer implementation is functioning correctly."
                        ),
                    )
            

                continue

            seen = set()

            for item in lb:

                ip = item.get("ip")
                hostname = item.get("hostname")

                #
                # Empty entry
                #

                if not ip and not hostname:

                    context.report(
                        
                            id=self.id,
                            severity="Low",
                            resource_type="Ingress",
                            resource_name=name,
                            namespace=namespace,
                            title="Empty LoadBalancer entry",
                            description=(
                                "LoadBalancer entry contains neither IP nor hostname."
                            ),
                            evidence={
                                "entry": item,
                            },
                            recommendation=(
                                "Verify the LoadBalancer status."
                            ),
                        )
                

                #
                # Duplicate address
                #

                key = ip or hostname

                if key:

                    if key in seen:

                        context.report(
                            
                                id=self.id,
                                severity="Low",
                                resource_type="Ingress",
                                resource_name=name,
                                namespace=namespace,
                                title="Duplicate LoadBalancer address",
                                description=(
                                    "The same LoadBalancer address appears multiple times."
                                ),
                                evidence={
                                    "address": key,
                                },
                                recommendation=(
                                    "Remove duplicate status entries."
                                ),
                            )
                    

                    else:

                        seen.add(key)

                #
                # localhost address
                #

                if ip in (
                    "127.0.0.1",
                    "0.0.0.0",
                ):

                    context.report(
                        
                            id=self.id,
                            severity="High",
                            resource_type="Ingress",
                            resource_name=name,
                            namespace=namespace,
                            title="Invalid external IP",
                            description=(
                                "Ingress is exposing a localhost or wildcard address."
                            ),
                            evidence={
                                "ip": ip,
                            },
                            recommendation=(
                                "Assign a valid external IP."
                            ),
                        )
                

                #
                # localhost hostname
                #

                if (
                    hostname
                    and hostname.lower()
                    == "localhost"
                ):

                    context.report(
                        
                            id=self.id,
                            severity="High",
                            resource_type="Ingress",
                            resource_name=name,
                            namespace=namespace,
                            title="Invalid external hostname",
                            description=(
                                "Ingress hostname is localhost."
                            ),
                            evidence={
                                "hostname": hostname,
                            },
                            recommendation=(
                                "Use a publicly resolvable hostname."
                            ),
                        )
                

        