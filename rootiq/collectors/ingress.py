# rootiq/collectors/ingress.py

from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class IngressCollector(BaseCollector):

    name = "IngressCollector"

    def collect(self, k8s):

        result = CollectResult(collector=self.name)

        try:

            if k8s.target.cluster_wide:

                ingresses = (
                    k8s.networking.list_ingress_for_all_namespaces().items
                )

            else:

                ingresses = (
                    k8s.networking.list_namespaced_ingress(
                        namespace=k8s.target.namespace
                    ).items
                )

        except ApiException as e:

            result.success = False
            result.error = str(e)

            return result

        total_rules = 0
        total_tls = 0

        for ingress in ingresses:

            rules = []
            tls = []

            if ingress.spec.rules:

                for rule in ingress.spec.rules:

                    paths = []

                    if (
                        rule.http
                        and rule.http.paths
                    ):

                        for path in rule.http.paths:

                            paths.append(
                                {
                                    "path": path.path,
                                    "path_type": path.path_type,
                                    "service": (
                                        path.backend.service.name
                                        if path.backend.service
                                        else None
                                    ),
                                    "service_port": (
                                        path.backend.service.port.number
                                        if path.backend.service
                                        else None
                                    ),
                                }
                            )

                    rules.append(
                        {
                            "host": rule.host,
                            "paths": paths,
                        }
                    )

                total_rules += len(rules)

            if ingress.spec.tls:

                for item in ingress.spec.tls:

                    tls.append(
                        {
                            "hosts": item.hosts,
                            "secret": item.secret_name,
                        }
                    )

                total_tls += len(tls)

            addresses = []

            if (
                ingress.status.load_balancer
                and ingress.status.load_balancer.ingress
            ):

                for addr in ingress.status.load_balancer.ingress:

                    addresses.append(
                        {
                            "ip": getattr(addr, "ip", None),
                            "hostname": getattr(addr, "hostname", None),
                        }
                    )

            result.resources.append(
                {
                    "name": ingress.metadata.name,
                    "namespace": ingress.metadata.namespace,
                    "uid": ingress.metadata.uid,
                    "ingress_class": ingress.spec.ingress_class_name,
                    "default_backend": (
                        ingress.spec.default_backend.service.name
                        if ingress.spec.default_backend
                        and ingress.spec.default_backend.service
                        else None
                    ),
                    "rules": rules,
                    "tls": tls,
                    "addresses": addresses,
                    "labels": ingress.metadata.labels or {},
                    "annotations": ingress.metadata.annotations or {},
                    "creation_timestamp": (
                        ingress.metadata.creation_timestamp.isoformat()
                        if ingress.metadata.creation_timestamp
                        else None
                    ),
                }
            )

            if not rules:

                result.issues.append(
                    {
                        "severity": "warning",
                        "resource": ingress.metadata.name,
                        "namespace": ingress.metadata.namespace,
                        "message": "Ingress has no routing rules.",
                    }
                )

            if not addresses:

                result.logs.append(
                    {
                        "level": "warning",
                        "message": (
                            f"{ingress.metadata.name} has no external address."
                        ),
                    }
                )

        result.metrics.extend(
            [
                {
                    "metric": "ingress_count",
                    "value": len(ingresses),
                },
                {
                    "metric": "rule_count",
                    "value": total_rules,
                },
                {
                    "metric": "tls_entries",
                    "value": total_tls,
                },
            ]
        )

        return result