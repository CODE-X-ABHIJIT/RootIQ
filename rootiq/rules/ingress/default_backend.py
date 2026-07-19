from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class IngressDefaultBackendRule(BaseRule):

    id = "INGRESS-006"

    name = "IngressDefaultBackend"

    resource_type = "ingress"

    def evaluate(self, context: RuleContext):

        

        for ingress in context.resources:

            namespace = ingress.get("namespace")
            name = ingress.get("name")

            backend = ingress.get(
                "default_backend"
            )

            #
            # No default backend
            #

            if not backend:

                context.report(
                    
                        id=self.id,
                        severity="Info",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="No default backend configured",
                        description=(
                            "Ingress relies entirely on host/path rules."
                        ),
                        evidence={},
                        recommendation=(
                            "Configure a default backend if unmatched requests should be handled."
                        ),
                    )
            

                continue

            service = backend.get(
                "service",
                {},
            )

            service_name = service.get(
                "name"
            )

            service_port = service.get(
                "port"
            )

            #
            # Missing Service
            #

            if not service_name:

                context.report(
                    
                        id=self.id,
                        severity="High",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="Default backend Service missing",
                        description=(
                            "Default backend does not specify a Service."
                        ),
                        evidence={
                            "default_backend": backend,
                        },
                        recommendation=(
                            "Specify a backend Service."
                        ),
                    )
            

            #
            # Missing Port
            #

            if service_port is None:

                context.report(
                    
                        id=self.id,
                        severity="High",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="Default backend port missing",
                        description=(
                            "Default backend Service has no port configured."
                        ),
                        evidence={
                            "service": service_name,
                        },
                        recommendation=(
                            "Specify a Service port."
                        ),
                    )
            

            #
            # Invalid Port
            #

            elif (
                isinstance(service_port, int)
                and (
                    service_port < 1
                    or service_port > 65535
                )
            ):

                context.report(
                    
                        id=self.id,
                        severity="High",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="Invalid backend port",
                        description=(
                            "Default backend Service port is outside the valid range."
                        ),
                        evidence={
                            "port": service_port,
                        },
                        recommendation=(
                            "Use a port between 1 and 65535."
                        ),
                    )
            

            #
            # Suspicious Port
            #

            elif (
                isinstance(service_port, int)
                and service_port > 1024
            ):

                context.report(
                    
                        id=self.id,
                        severity="Info",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="Non-standard backend port",
                        description=(
                            "Default backend uses a non-standard Service port."
                        ),
                        evidence={
                            "port": service_port,
                        },
                        recommendation=(
                            "Verify the configured Service port is intentional."
                        ),
                    )
            

        