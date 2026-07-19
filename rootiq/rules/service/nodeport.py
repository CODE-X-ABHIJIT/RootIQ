from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class ServiceNodePortRule(BaseRule):

    id = "SERVICE-005"

    name = "ServiceNodePort"

    resource_type = "service"

    def evaluate(self, ctx: RuleContext):

        

        used_node_ports = {}

        for service in ctx.resources:

            namespace = service.get("namespace")
            name = service.get("name")

            if service.get("type") not in (
                "NodePort",
                "LoadBalancer",
            ):
                continue

            ports = service.get("ports", [])

            #
            # No ports
            #

            if not ports:

                ctx.report(
                            rule=self,
                    
                        id=self.id,
                        severity="High",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="NodePort Service has no ports",
                        description=(
                            "The Service exposes no ports."
                        ),
                        evidence={},
                        recommendation=(
                            "Configure at least one Service port."
                        ),
                    )
                

                continue

            for port in ports:

                node_port = port.get("node_port")

                #
                # Missing NodePort
                #

                if node_port is None:

                    ctx.report(
                            rule=self,
                        
                            id=self.id,
                            severity="Medium",
                            resource_type="Service",
                            resource_name=name,
                            namespace=namespace,
                            title="Missing NodePort",
                            description=(
                                "The Service does not have a nodePort assigned."
                            ),
                            evidence={
                                "port": port.get("port"),
                            },
                            recommendation=(
                                "Allow Kubernetes to allocate a nodePort or specify one."
                            ),
                        )
                    

                    continue

                #
                # Invalid range
                #

                if (
                    node_port < 30000
                    or node_port > 32767
                ):

                    ctx.report(
                            rule=self,
                        
                            id=self.id,
                            severity="High",
                            resource_type="Service",
                            resource_name=name,
                            namespace=namespace,
                            title="Invalid NodePort",
                            description=(
                                "NodePort is outside the default Kubernetes range."
                            ),
                            evidence={
                                "node_port": node_port,
                            },
                            recommendation=(
                                "Use a NodePort between 30000 and 32767 "
                                "unless your cluster is configured differently."
                            ),
                        )
                    

                #
                # Duplicate NodePort
                #

                if node_port in used_node_ports:

                    previous = used_node_ports[node_port]

                    ctx.report(
                            rule=self,
                        
                            id=self.id,
                            severity="Critical",
                            resource_type="Service",
                            resource_name=name,
                            namespace=namespace,
                            title="Duplicate NodePort detected",
                            description=(
                                "Multiple Services are configured to use the same NodePort."
                            ),
                            evidence={
                                "node_port": node_port,
                                "existing_service": previous,
                            },
                            recommendation=(
                                "Assign unique NodePorts to avoid conflicts."
                            ),
                        )
                    

                else:

                    used_node_ports[node_port] = (
                        f"{namespace}/{name}"
                    )

        