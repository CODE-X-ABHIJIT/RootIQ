from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class IngressSSLRedirectRule(BaseRule):

    id = "INGRESS-010"

    name = "IngressSSLRedirect"

    resource_type = "ingress"

    def evaluate(self, context: RuleContext):

        

        for ingress in context.resources:

            namespace = ingress.get("namespace")
            name = ingress.get("name")

            annotations = ingress.get(
                "annotations",
                {},
            )

            tls = ingress.get(
                "tls",
                [],
            )

            ssl_redirect = (
                annotations.get(
                    "nginx.ingress.kubernetes.io/ssl-redirect"
                )
            )

            force_ssl = (
                annotations.get(
                    "nginx.ingress.kubernetes.io/force-ssl-redirect"
                )
            )

            #
            # TLS configured but redirects disabled
            #

            if tls:

                if ssl_redirect == "false":

                    context.report(
                        
                            id=self.id,
                            severity="High",
                            resource_type="Ingress",
                            resource_name=name,
                            namespace=namespace,
                            title="SSL redirect disabled",
                            description=(
                                "TLS is configured but SSL redirection is disabled."
                            ),
                            evidence={
                                "ssl_redirect": ssl_redirect,
                            },
                            recommendation=(
                                "Enable ssl-redirect to force HTTPS."
                            ),
                        )
                

                if force_ssl == "false":

                    context.report(
                        
                            id=self.id,
                            severity="Medium",
                            resource_type="Ingress",
                            resource_name=name,
                            namespace=namespace,
                            title="Force SSL redirect disabled",
                            description=(
                                "force-ssl-redirect is explicitly disabled."
                            ),
                            evidence={
                                "force_ssl_redirect": force_ssl,
                            },
                            recommendation=(
                                "Enable force-ssl-redirect for secure traffic."
                            ),
                        )
                

            #
            # Invalid annotation values
            #

            for key, value in {

                "ssl-redirect": ssl_redirect,
                "force-ssl-redirect": force_ssl,

            }.items():

                if (
                    value is not None
                    and value.lower()
                    not in (
                        "true",
                        "false",
                    )
                ):

                    context.report(
                        
                            id=self.id,
                            severity="Medium",
                            resource_type="Ingress",
                            resource_name=name,
                            namespace=namespace,
                            title=f"Invalid {key} value",
                            description=(
                                "SSL redirect annotation contains an invalid value."
                            ),
                            evidence={
                                key: value,
                            },
                            recommendation=(
                                "Use true or false."
                            ),
                        )
                

            #
            # TLS enabled but no redirect annotation
            #

            if (
                tls
                and ssl_redirect is None
                and force_ssl is None
            ):

                context.report(
                    
                        id=self.id,
                        severity="Info",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="SSL redirect not explicitly configured",
                        description=(
                            "TLS is configured but SSL redirect annotations are not explicitly set."
                        ),
                        evidence={},
                        recommendation=(
                            "Explicitly configure SSL redirect behavior."
                        ),
                    )
            

            #
            # Redirect enabled without TLS
            #

            if (
                not tls
                and (
                    ssl_redirect == "true"
                    or force_ssl == "true"
                )
            ):

                context.report(
                    
                        id=self.id,
                        severity="Medium",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="SSL redirect enabled without TLS",
                        description=(
                            "Ingress forces HTTPS but no TLS certificate is configured."
                        ),
                        evidence={
                            "tls": False,
                        },
                        recommendation=(
                            "Configure TLS or disable HTTPS redirection."
                        ),
                    )
            

        