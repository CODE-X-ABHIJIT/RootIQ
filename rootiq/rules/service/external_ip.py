from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class ServiceExternalIPRule(BaseRule):

    id = "SERVICE-006"

    name = "ServiceExternalIP"

    resource_type = "service"

    def evaluate(self, context: RuleContext):

        

        for service in context.resources:

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

                    context.report(
                            rule=self,
                        
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
                    

                continue

            #
            # Duplicate External IPs
            #

            if len(external_ips) != len(set(external_ips)):

                context.report(
                            rule=self,
                    
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
                

            #
            # Invalid External IPs
            #

            for ip in external_ips:

                if not isinstance(ip, str):

                    context.report(
                            rule=self,
                        
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
                    

        