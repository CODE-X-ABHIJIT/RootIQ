from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class IngressCollector(BaseCollector):
    enabled = True
    name = "IngressCollector"
    resource_type = "ingress"

    def collect(self, k8s):

        result = CollectResult(
            collector=self.name
        )

        try:

            ingresses = k8s.ingresses()

        except ApiException as e:

            result.success = False
            result.error = str(e)

            

        ingress_count = len(ingresses)

        total_rules = 0
        total_paths = 0
        total_tls = 0

        ingress_with_tls = 0
        ingress_without_tls = 0

        ingress_with_address = 0
        ingress_without_address = 0

        nginx_class = 0
        custom_class = 0

        for ingress in ingresses:

            spec = ingress.spec
            status = ingress.status

            #
            # Rules
            #

            rules = []

            if spec.rules:

                for rule in spec.rules:

                    paths = []

                    if (
                        rule.http
                        and rule.http.paths
                    ):

                        for path in rule.http.paths:

                            backend = {}

                            if path.backend.service:

                                backend = {
                                    "service": {
                                        "name": (
                                            path.backend
                                            .service
                                            .name
                                        ),
                                        "port": (
                                            path.backend
                                            .service
                                            .port.number
                                            or path.backend
                                            .service
                                            .port.name
                                        ),
                                    }
                                }

                            paths.append(
                                {
                                    "path": path.path,
                                    "path_type": path.path_type,
                                    "backend": backend,
                                }
                            )

                    rules.append(
                        {
                            "host": rule.host,
                            "paths": paths,
                        }
                    )

                    total_paths += len(paths)

            total_rules += len(rules)

            #
            # TLS
            #

            tls = []

            if spec.tls:

                ingress_with_tls += 1

                for item in spec.tls:

                    tls.append(
                        {
                            "secret_name": (
                                item.secret_name
                            ),
                            "hosts": (
                                item.hosts or []
                            ),
                        }
                    )

                total_tls += len(tls)

            else:

                ingress_without_tls += 1

            #
            # Default Backend
            #

            default_backend = None

            if (
                spec.default_backend
                and spec.default_backend.service
            ):

                default_backend = {
                    "service": {
                        "name": (
                            spec.default_backend
                            .service.name
                        ),
                        "port": (
                            spec.default_backend
                            .service.port.number
                            or spec.default_backend
                            .service.port.name
                        ),
                    }
                }

            #
            # LoadBalancer
            #

            load_balancer = []

            if (
                status.load_balancer
                and status.load_balancer.ingress
            ):

                ingress_with_address += 1

                for lb in (
                    status.load_balancer.ingress
                ):

                    load_balancer.append(
                        {
                            "ip": getattr(
                                lb,
                                "ip",
                                None,
                            ),
                            "hostname": getattr(
                                lb,
                                "hostname",
                                None,
                            ),
                        }
                    )

            else:

                ingress_without_address += 1
                            #
            # Ingress Class
            #

            ingress_class = (
                spec.ingress_class_name
            )

            if ingress_class:

                if (
                    ingress_class.lower()
                    == "nginx"
                ):

                    nginx_class += 1

                else:

                    custom_class += 1

            #
            # Resource
            #

            result.resources.append(
                {
                    "name": ingress.metadata.name,
                    "namespace": ingress.metadata.namespace,
                    "uid": ingress.metadata.uid,

                    "ingress_class": ingress_class,

                    "default_backend": (
                        default_backend
                    ),

                    "rules": rules,

                    "tls": tls,

                    "load_balancer": (
                        load_balancer
                    ),

                    "labels": (
                        ingress.metadata.labels
                        or {}
                    ),

                    "annotations": (
                        ingress.metadata.annotations
                        or {}
                    ),

                    "creation_timestamp": (
                        ingress.metadata.creation_timestamp.isoformat()
                        if ingress.metadata.creation_timestamp
                        else None
                    ),
                }
            )

            #
            # Collector Warnings
            #

            if not rules:

                context.report(
                    {
                        "severity": "warning",
                        "resource": ingress.metadata.name,
                        "namespace": ingress.metadata.namespace,
                        "message": (
                            "Ingress has no routing rules."
                        ),
                    }
                )

            if not load_balancer:

                result.logs.append(
                    {
                        "level": "warning",
                        "message": (
                            f"{ingress.metadata.name} has no external LoadBalancer address."
                        ),
                    }
                )

        #
        # Metrics
        #

        result.metrics.extend(
            [
                {
                    "metric": "ingress_count",
                    "value": ingress_count,
                },
                {
                    "metric": "rule_count",
                    "value": total_rules,
                },
                {
                    "metric": "path_count",
                    "value": total_paths,
                },
                {
                    "metric": "tls_entries",
                    "value": total_tls,
                },
                {
                    "metric": "tls_enabled_ingresses",
                    "value": ingress_with_tls,
                },
                {
                    "metric": "tls_disabled_ingresses",
                    "value": ingress_without_tls,
                },
                {
                    "metric": "ingresses_with_loadbalancer",
                    "value": ingress_with_address,
                },
                {
                    "metric": "ingresses_without_loadbalancer",
                    "value": ingress_without_address,
                },
                {
                    "metric": "nginx_ingress_class",
                    "value": nginx_class,
                },
                {
                    "metric": "custom_ingress_class",
                    "value": custom_class,
                },
            ]
        )

        return result