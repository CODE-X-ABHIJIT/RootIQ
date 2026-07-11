from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class IngressAnnotationsRule(BaseRule):

    id = "INGRESS-007"

    name = "IngressAnnotations"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for ingress in resources:

            namespace = ingress.get("namespace")
            name = ingress.get("name")

            annotations = ingress.get(
                "annotations",
                {},
            )

            if not annotations:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Info",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="No annotations configured",
                        description=(
                            "Ingress does not define any annotations."
                        ),
                        evidence={},
                        recommendation=(
                            "Configure annotations if required by the Ingress controller."
                        ),
                    )
                )

                continue

            #
            # SSL Redirect
            #

            ssl_redirect = (
                annotations.get(
                    "nginx.ingress.kubernetes.io/ssl-redirect"
                )
            )

            if (
                ssl_redirect
                and ssl_redirect.lower()
                not in (
                    "true",
                    "false",
                )
            ):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Medium",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="Invalid ssl-redirect value",
                        description=(
                            "ssl-redirect annotation should be true or false."
                        ),
                        evidence={
                            "value": ssl_redirect,
                        },
                        recommendation=(
                            "Use true or false."
                        ),
                    )
                )

            #
            # Rewrite Target
            #

            rewrite = (
                annotations.get(
                    "nginx.ingress.kubernetes.io/rewrite-target"
                )
            )

            if rewrite and not rewrite.startswith("/"):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Medium",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="Invalid rewrite-target",
                        description=(
                            "rewrite-target should begin with '/'."
                        ),
                        evidence={
                            "rewrite_target": rewrite,
                        },
                        recommendation=(
                            "Configure a valid rewrite path."
                        ),
                    )
                )

            #
            # Proxy Body Size
            #

            body_size = (
                annotations.get(
                    "nginx.ingress.kubernetes.io/proxy-body-size"
                )
            )

            if body_size == "0":

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Low",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="Unlimited upload size",
                        description=(
                            "proxy-body-size is configured as unlimited."
                        ),
                        evidence={
                            "proxy_body_size": body_size,
                        },
                        recommendation=(
                            "Limit upload size if not required."
                        ),
                    )
                )

            #
            # Backend Protocol
            #

            backend_protocol = (
                annotations.get(
                    "nginx.ingress.kubernetes.io/backend-protocol"
                )
            )

            if (
                backend_protocol
                and backend_protocol
                not in (
                    "HTTP",
                    "HTTPS",
                    "GRPC",
                    "GRPCS",
                    "AJP",
                    "FCGI",
                )
            ):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Medium",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="Invalid backend protocol",
                        description=(
                            "Unsupported backend protocol configured."
                        ),
                        evidence={
                            "backend_protocol": backend_protocol,
                        },
                        recommendation=(
                            "Use one of the supported backend protocols."
                        ),
                    )
                )

            #
            # Permanent Redirect
            #

            redirect = (
                annotations.get(
                    "nginx.ingress.kubernetes.io/permanent-redirect"
                )
            )

            if redirect:

                if not (
                    redirect.startswith("http://")
                    or redirect.startswith("https://")
                ):

                    result.issues.append(
                        Issue(
                            id=self.id,
                            severity="Medium",
                            resource_type="Ingress",
                            resource_name=name,
                            namespace=namespace,
                            title="Invalid permanent redirect",
                            description=(
                                "Permanent redirect must use a valid URL."
                            ),
                            evidence={
                                "redirect": redirect,
                            },
                            recommendation=(
                                "Use a valid HTTP or HTTPS URL."
                            ),
                        )
                    )

        return result