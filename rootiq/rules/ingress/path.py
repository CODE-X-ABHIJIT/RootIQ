from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class IngressPathRule(BaseRule):

    id = "INGRESS-005"

    name = "IngressPath"

    resource_type = "ingress"

    def evaluate(self, context: RuleContext):

        

        for ingress in context.resources:

            namespace = ingress.get("namespace")
            name = ingress.get("name")

            rules = ingress.get("rules", [])

            for rule in rules:

                host = rule.get("host")

                seen_paths = set()

                for path in rule.get(
                    "paths",
                    [],
                ):

                    path_value = path.get("path")

                    path_type = path.get(
                        "path_type"
                    )

                    #
                    # Missing path
                    #

                    if not path_value:

                        context.report(
                            
                                id=self.id,
                                severity="High",
                                resource_type="Ingress",
                                resource_name=name,
                                namespace=namespace,
                                title="Missing path",
                                description=(
                                    "Ingress path is empty."
                                ),
                                evidence={
                                    "host": host,
                                },
                                recommendation=(
                                    "Specify a valid path."
                                ),
                            )
                    

                        continue

                    #
                    # Duplicate path
                    #

                    if path_value in seen_paths:

                        context.report(
                            
                                id=self.id,
                                severity="Medium",
                                resource_type="Ingress",
                                resource_name=name,
                                namespace=namespace,
                                title="Duplicate path",
                                description=(
                                    "Multiple rules define the same path."
                                ),
                                evidence={
                                    "host": host,
                                    "path": path_value,
                                },
                                recommendation=(
                                    "Remove duplicate path definitions."
                                ),
                            )
                    

                    else:

                        seen_paths.add(path_value)

                    #
                    # Path should start with /
                    #

                    if not path_value.startswith("/"):

                        context.report(
                            
                                id=self.id,
                                severity="High",
                                resource_type="Ingress",
                                resource_name=name,
                                namespace=namespace,
                                title="Invalid path",
                                description=(
                                    "Ingress path does not begin with '/'."
                                ),
                                evidence={
                                    "host": host,
                                    "path": path_value,
                                },
                                recommendation=(
                                    "Ingress paths should begin with '/'."
                                ),
                            )
                    

                    #
                    # Invalid pathType
                    #

                    if path_type not in (
                        "Exact",
                        "Prefix",
                        "ImplementationSpecific",
                    ):

                        context.report(
                            
                                id=self.id,
                                severity="Medium",
                                resource_type="Ingress",
                                resource_name=name,
                                namespace=namespace,
                                title="Invalid pathType",
                                description=(
                                    "Unsupported pathType configured."
                                ),
                                evidence={
                                    "host": host,
                                    "path": path_value,
                                    "path_type": path_type,
                                },
                                recommendation=(
                                    "Use Exact, Prefix or ImplementationSpecific."
                                ),
                            )
                    

                    #
                    # Suspicious double slash
                    #

                    if "//" in path_value:

                        context.report(
                            
                                id=self.id,
                                severity="Low",
                                resource_type="Ingress",
                                resource_name=name,
                                namespace=namespace,
                                title="Suspicious path",
                                description=(
                                    "Path contains consecutive '/'."
                                ),
                                evidence={
                                    "path": path_value,
                                },
                                recommendation=(
                                    "Remove duplicate '/' characters."
                                ),
                            )
                    

                    #
                    # Catch-all path
                    #

                    if path_value == "/":

                        context.report(
                            
                                id=self.id,
                                severity="Info",
                                resource_type="Ingress",
                                resource_name=name,
                                namespace=namespace,
                                title="Catch-all path",
                                description=(
                                    "Ingress exposes a root catch-all path."
                                ),
                                evidence={
                                    "host": host,
                                },
                                recommendation=(
                                    "Ensure this does not unintentionally shadow more specific routes."
                                ),
                            )
                    

        