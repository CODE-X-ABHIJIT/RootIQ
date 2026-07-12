from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class IngressBackendRule(BaseRule):

    id = "INGRESS-002"

    name = "IngressBackend"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for ingress in resources:

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

                result.issues.append(
                    Issue(
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

                        result.issues.append(
                            Issue(
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

                        result.issues.append(
                            Issue(
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
                        )

                    #
                    # Missing port
                    #

                    if not port:

                        result.issues.append(
                            Issue(
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

                    result.issues.append(
                        Issue(
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
                    )

                if not service.get("port"):

                    result.issues.append(
                        Issue(
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
                    )
        return result