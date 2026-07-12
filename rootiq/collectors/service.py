from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class ServiceCollector(BaseCollector):

    name = "ServiceCollector"
    resource_type = "service"
    
    def collect(self, k8s):

        result = CollectResult(
            collector=self.name
        )

        try:

            if k8s.target.cluster_wide:

                services = (
                    k8s.core
                    .list_service_for_all_namespaces()
                    .items
                )

            else:

                services = (
                    k8s.core
                    .list_namespaced_service(
                        namespace=k8s.target.namespace
                    )
                    .items
                )

        except ApiException as e:

            result.success = False
            result.error = str(e)

            return result

        cluster_ip = 0
        node_port = 0
        load_balancer = 0
        external_name = 0

        for svc in services:

            svc_type = svc.spec.type

            if svc_type == "ClusterIP":
                cluster_ip += 1

            elif svc_type == "NodePort":
                node_port += 1

            elif svc_type == "LoadBalancer":
                load_balancer += 1

            elif svc_type == "ExternalName":
                external_name += 1

            #
            # Ports
            #

            ports = []

            for p in (svc.spec.ports or []):

                ports.append({

                    "name": p.name,

                    "protocol": p.protocol,

                    "port": p.port,

                    "target_port": p.target_port,

                    "node_port": p.node_port,

                    "app_protocol": (
                        getattr(
                            p,
                            "app_protocol",
                            None,
                        )
                    ),
                })

            #
            # LoadBalancer
            #

            ingress_ips = []

            if (
                svc.status.load_balancer
                and svc.status.load_balancer.ingress
            ):

                for lb in (
                    svc.status
                    .load_balancer
                    .ingress
                ):

                    ingress_ips.append({

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
                    })

            #
            # Endpoints
            #

            endpoints = []

            try:

                ep = (
                    k8s.core
                    .read_namespaced_endpoints(
                        svc.metadata.name,
                        svc.metadata.namespace,
                    )
                )

                if ep.subsets:

                    for subset in ep.subsets:

                        #
                        # Ready
                        #

                        for addr in (
                            subset.addresses
                            or []
                        ):

                            endpoints.append({

                                "ip": addr.ip,

                                "node": (
                                    addr.node_name
                                ),

                                "pod": (
                                    addr.target_ref.name
                                    if addr.target_ref
                                    else None
                                ),

                                "ready": True,
                            })

                        #
                        # Not Ready
                        #

                        for addr in (
                            subset.not_ready_addresses
                            or []
                        ):

                            endpoints.append({

                                "ip": addr.ip,

                                "node": (
                                    addr.node_name
                                ),

                                "pod": (
                                    addr.target_ref.name
                                    if addr.target_ref
                                    else None
                                ),

                                "ready": False,
                            })

            except ApiException:
                pass

            #
            # Resource
            #

            result.resources.append({

                "name": svc.metadata.name,

                "namespace": (
                    svc.metadata.namespace
                ),

                "uid": svc.metadata.uid,

                "type": svc_type,

                "cluster_ip": (
                    svc.spec.cluster_ip
                ),

                "external_ip": (
                    ingress_ips[0]["ip"]
                    if ingress_ips
                    else None
                ),

                "external_ips": (
                    svc.spec.external_ips
                    or []
                ),

                "external_name": (
                    svc.spec.external_name
                ),

                "selector": (
                    svc.spec.selector
                    or {}
                ),

                "ports": ports,

                "endpoints": endpoints,

                "load_balancer": {

                    "ingress": ingress_ips
                },

                "session_affinity": (
                    svc.spec.session_affinity
                ),

                "session_affinity_config": (
                    svc.spec
                    .session_affinity_config
                    .to_dict()
                    if (
                        svc.spec
                        .session_affinity_config
                    )
                    else {}
                ),

                "external_traffic_policy": (
                    getattr(
                        svc.spec,
                        "external_traffic_policy",
                        None,
                    )
                ),

                "internal_traffic_policy": (
                    getattr(
                        svc.spec,
                        "internal_traffic_policy",
                        None,
                    )
                ),
                                "health_check_node_port": (
                    getattr(
                        svc.spec,
                        "health_check_node_port",
                        None,
                    )
                ),

                "publish_not_ready_addresses": (
                    svc.spec
                    .publish_not_ready_addresses
                ),

                "ip_family_policy": (
                    svc.spec
                    .ip_family_policy
                ),

                "ip_families": (
                    svc.spec
                    .ip_families
                    or []
                ),

                "allocate_load_balancer_node_ports": (
                    getattr(
                        svc.spec,
                        "allocate_load_balancer_node_ports",
                        None,
                    )
                ),

                "creation_timestamp": (
                    svc.metadata.creation_timestamp.isoformat()
                    if svc.metadata.creation_timestamp
                    else None
                ),

                "labels": (
                    svc.metadata.labels
                    or {}
                ),

                "annotations": (
                    svc.metadata.annotations
                    or {}
                ),
            })

            #
            # Simple warnings
            #

            if (
                svc_type != "ExternalName"
                and not svc.spec.selector
            ):

                result.issues.append({

                    "severity": "warning",

                    "resource": (
                        svc.metadata.name
                    ),

                    "namespace": (
                        svc.metadata.namespace
                    ),

                    "message": (
                        "Service has no selector."
                    ),
                })

            if (
                svc_type == "LoadBalancer"
                and not ingress_ips
            ):

                result.logs.append({

                    "level": "warning",

                    "message": (
                        f"{svc.metadata.name} "
                        "waiting for external IP."
                    ),
                })

        #
        # Metrics
        #

        result.metrics.extend([

            {
                "metric": "service_count",
                "value": len(
                    result.resources
                ),
            },

            {
                "metric": "clusterip_services",
                "value": cluster_ip,
            },

            {
                "metric": "nodeport_services",
                "value": node_port,
            },

            {
                "metric": "loadbalancer_services",
                "value": load_balancer,
            },

            {
                "metric": "externalname_services",
                "value": external_name,
            },

            {
                "metric": "headless_services",
                "value": sum(
                    s["cluster_ip"] == "None"
                    for s in result.resources
                ),
            },

            {
                "metric": "services_without_selector",
                "value": sum(
                    (
                        s["type"] != "ExternalName"
                        and not s["selector"]
                    )
                    for s in result.resources
                ),
            },

            {
                "metric": "services_without_endpoints",
                "value": sum(
                    len(
                        s["endpoints"]
                    ) == 0
                    for s in result.resources
                    if (
                        s["type"]
                        != "ExternalName"
                    )
                ),
            },
        ])

        return result