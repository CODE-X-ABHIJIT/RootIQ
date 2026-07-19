from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class IngressBackendRule(BaseRule):

    id = "INGRESS-002"

    name = "IngressBackend"

    resource_type = "ingress"

    def evaluate(self, context: RuleContext):

        

        for ingress in context.resources:

            namespace = ingress.get("namespace")
            name = ingress.get("name")

            rules = ingress.get("rules", [])

            default_backend = ingress.get(
                "default_backend"
            )

            #
            # No backend at all
            #

            if not rules and not default_backend:

                context.report(
                    
                        id=self.id,
                        severity="Critical",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="Ingress has no backend",
                        description=(
                            "Ingress has neither routing rules nor a default backend."
                        ),
                        evidence={},
                        recommendation=(
                            "Configure at least one backend Service."
                        ),
                    )
            

                continue

            #
            # Validate rule backends
            #

            for rule in rules:

                host = rule.get("host")

                for path in rule.get(
                    "paths",
                    [],
                ):

                    backend = path.get(
                        "backend",
                        {},
                    )

                    service = backend.get(
                        "service"
                    )

                    if not service:

                        context.report(
                            
                                id=self.id,
                                severity="High",
                                resource_type="Ingress",
                                resource_name=name,
                                namespace=namespace,
                                title="Missing backend service",
                                description=(
                                    "Ingress path has no backend service."
                                ),
                                evidence={
                                    "host": host,
                                    "path": path.get(
                                        "path"
                                    ),
                                },
                                recommendation=(
                                    "Configure a backend Service."
                                ),
                            )
                    

                        continue

                    service_name = service.get(
                        "name"
                    )

                    port = service.get(
                        "port"
                    )

                    #
                    # Missing Service name
                    #

                    if not service_name:

                        context.report(
                            
                                id=self.id,
                                severity="High",
                                resource_type="Ingress",
                                resource_name=name,
                                namespace=namespace,
                                title="Backend Service name missing",
                                description=(
                                    "Backend Service name is empty."
                                ),
                                evidence={
                                    "host": host,
                                    "path": path.get(
                                        "path"
                                    ),
                                    "service": service,
                                },
                                recommendation=(
                                    "Specify a valid Service name."
                                ),
                            )
                    

                    #
                    # Missing port
                    #

                    if not port:

                        context.report(
                            
                                id=self.id,
                                severity="High",
                                resource_type="Ingress",
                                resource_name=name,
                                namespace=namespace,
                                title="Backend Service port missing",
                                description=(
                                    "Backend Service port is not configured."
                                ),
                                evidence={
                                    "service": service_name,
                                    "host": host,
                                    "path": path.get(
                                        "path"
                                    ),
                                },
                                recommendation=(
                                    "Specify a Service port."
                                ),
                            )
                    

            #
            # Validate default backend
            #

            if default_backend:

                service = default_backend.get(
                    "service",
                    {},
                )

                if not service.get("name"):

                    context.report(
                        
                            id=self.id,
                            severity="Medium",
                            resource_type="Ingress",
                            resource_name=name,
                            namespace=namespace,
                            title="Default backend Service missing",
                            description=(
                                "Default backend has no Service configured."
                            ),
                            evidence={
                                "default_backend": default_backend,
                            },
                            recommendation=(
                                "Configure a valid default backend."
                            ),
                        )
                

                if not service.get("port"):

                    context.report(
                        
                            id=self.id,
                            severity="Medium",
                            resource_type="Ingress",
                            resource_name=name,
                            namespace=namespace,
                            title="Default backend port missing",
                            description=(
                                "Default backend Service port is missing."
                            ),
                            evidence={
                                "default_backend": default_backend,
                            },
                            recommendation=(
                                "Specify the backend Service port."
                            ),
                        )
                
        