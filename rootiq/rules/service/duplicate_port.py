from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class ServiceDuplicatePortRule(BaseRule):

    id = "SERVICE-008"

    name = "ServiceDuplicatePort"
    
    resource_type = "service"

    def evaluate(self, ctx: RuleContext):

        

        for service in ctx.resources:

            namespace = service.get("namespace")
            name = service.get("name")

            ports = service.get("ports", [])

            if not ports:
                continue

            seen = {}

            for port in ports:

                protocol = port.get(
                    "protocol",
                    "TCP",
                )

                service_port = port.get("port")

                key = (
                    protocol,
                    service_port,
                )

                #
                # Duplicate Service Port
                #

                if key in seen:

                    ctx.report(

                            rule=self,
                            id=self.id,
                            severity="High",
                            resource_type="Service",
                            resource_name=name,
                            namespace=namespace,
                            title="Duplicate Service port",
                            description=(
                                "Multiple Service ports expose the same protocol and port."
                            ),
                            evidence={
                                "protocol": protocol,
                                "port": service_port,
                                "duplicate": key,
                            },
                            recommendation=(
                                "Remove duplicate Service port definitions."
                            ),
                        )
                    

                else:

                    seen[key] = True

            #
            # Duplicate Port Names
            #

            names = [
                p.get("name")
                for p in ports
                if p.get("name")
            ]

            duplicates = {
                n
                for n in names
                if names.count(n) > 1
            }

            if duplicates:

                ctx.report(
                        rule=self,
                    
                        id=self.id,
                        severity="Medium",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="Duplicate port names",
                        description=(
                            "Multiple Service ports use the same name."
                        ),
                        evidence={
                            "duplicate_names": sorted(
                                duplicates
                            ),
                        },
                        recommendation=(
                            "Ensure every Service port has a unique name."
                        ),
                    )
                

            #
            # Duplicate Target Ports
            #

            target_ports = [
                p.get("target_port")
                for p in ports
                if p.get("target_port") is not None
            ]

            duplicate_targets = {
                p
                for p in target_ports
                if target_ports.count(p) > 1
            }

            if duplicate_targets:

                ctx.report(
                         rule=self,
                    
                        id=self.id,
                        severity="Low",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="Duplicate targetPorts",
                        description=(
                            "Multiple Service ports forward traffic to the same targetPort."
                        ),
                        evidence={
                            "duplicate_target_ports": sorted(
                                duplicate_targets
                            ),
                        },
                        recommendation=(
                            "Verify that duplicate targetPorts are intentional."
                        ),
                    )
                

        