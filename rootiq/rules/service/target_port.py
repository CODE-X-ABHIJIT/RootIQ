from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class ServiceTargetPortRule(BaseRule):

    id = "SERVICE-003"

    name = "ServiceTargetPort"

    resource_type = "service"

    def evaluate(self, ctx: RuleContext):

        

        for service in ctx.resources:

            namespace = service.get("namespace")
            name = service.get("name")

            ports = service.get("ports", [])

            #
            # No ports defined
            #

            if not ports:

                ctx.report(
                        rule=self,
                    
                        id=self.id,
                        severity="Critical",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="Service has no ports",
                        description=(
                            "The Service does not expose any ports."
                        ),
                        evidence={},
                        recommendation=(
                            "Define at least one Service port."
                        ),
                    )
                

                continue

            #
            # Validate each port
            #

            for port in ports:

                service_port = port.get("port")
                target_port = port.get("target_port")
                protocol = port.get("protocol")

                #
                # Missing targetPort
                #

                if target_port in (None, ""):

                    ctx.report(
                            rule=self,
                        
                            id=self.id,
                            severity="High",
                            resource_type="Service",
                            resource_name=name,
                            namespace=namespace,
                            title="Missing targetPort",
                            description=(
                                "A Service port does not specify a targetPort."
                            ),
                            evidence={
                                "port": service_port,
                                "target_port": target_port,
                            },
                            recommendation=(
                                "Configure a valid targetPort."
                            ),
                        )
                    

                #
                # Invalid numeric targetPort
                #

                if (
                    isinstance(target_port, int)
                    and (
                        target_port < 1
                        or target_port > 65535
                    )
                ):

                    ctx.report(
                            rule=self,
                        
                            id=self.id,
                            severity="High",
                            resource_type="Service",
                            resource_name=name,
                            namespace=namespace,
                            title="Invalid targetPort",
                            description=(
                                "targetPort is outside the valid TCP/UDP port range."
                            ),
                            evidence={
                                "target_port": target_port,
                            },
                            recommendation=(
                                "Use a port between 1 and 65535."
                            ),
                        )
                    

                #
                # Invalid Service port
                #

                if (
                    isinstance(service_port, int)
                    and (
                        service_port < 1
                        or service_port > 65535
                    )
                ):

                    ctx.report(
                            rule=self,
                        
                            id=self.id,
                            severity="High",
                            resource_type="Service",
                            resource_name=name,
                            namespace=namespace,
                            title="Invalid Service port",
                            description=(
                                "Service port is outside the valid range."
                            ),
                            evidence={
                                "port": service_port,
                            },
                            recommendation=(
                                "Use a port between 1 and 65535."
                            ),
                        )
                    

                #
                # Unsupported protocol
                #

                if protocol not in (
                    "TCP",
                    "UDP",
                    "SCTP",
                ):

                    ctx.report(
                            rule=self,
                        
                            id=self.id,
                            severity="Low",
                            resource_type="Service",
                            resource_name=name,
                            namespace=namespace,
                            title="Unknown Service protocol",
                            description=(
                                "The Service uses an unsupported protocol."
                            ),
                            evidence={
                                "protocol": protocol,
                            },
                            recommendation=(
                                "Use TCP, UDP, or SCTP."
                            ),
                        )
                    

        