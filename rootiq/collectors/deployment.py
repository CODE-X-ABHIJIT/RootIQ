from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class DeploymentCollector(BaseCollector):

    name = "DeploymentCollector"

    def collect(self, k8s):

        result = CollectResult(
            collector=self.name
        )

        try:
            deployments = (
                k8s.apps
                .list_deployment_for_all_namespaces()
                .items
            )

        except ApiException as e:

            result.success = False
            result.error = str(e)
            return result

        healthy = 0
        unhealthy = 0
        available = 0
        partial = 0
        failed_rollouts = 0

        for dep in deployments:

            status = dep.status

            name = dep.metadata.name
            namespace = dep.metadata.namespace

            desired_replicas = dep.spec.replicas or 0
            ready_replicas = status.ready_replicas or 0
            available_replicas = status.available_replicas or 0
            updated_replicas = status.updated_replicas or 0
            unavailable_replicas = status.unavailable_replicas or 0

            deployment_resource = {

                #
                # Basic
                #

                "name": name,
                "namespace": namespace,
                "uid": dep.metadata.uid,

                "creation_timestamp": (
                    dep.metadata.creation_timestamp.isoformat()
                    if dep.metadata.creation_timestamp
                    else None
                ),

                #
                # Metadata
                #

                "labels": dep.metadata.labels or {},
                "annotations": dep.metadata.annotations or {},

                #
                # Replica Information
                #

                "desired_replicas": desired_replicas,
                "ready_replicas": ready_replicas,
                "available_replicas": available_replicas,
                "updated_replicas": updated_replicas,
                "unavailable_replicas": unavailable_replicas,

                "generation": dep.metadata.generation,
                "observed_generation": (
                    status.observed_generation
                ),

                #
                # Rollout
                #

                "paused": dep.spec.paused,

                "revision": (
                    dep.metadata.annotations.get(
                        "deployment.kubernetes.io/revision"
                    )
                    if dep.metadata.annotations
                    else None
                ),

                "progress_deadline_seconds": (
                    dep.spec.progress_deadline_seconds
                ),

                "revision_history_limit": (
                    dep.spec.revision_history_limit
                ),

                "min_ready_seconds": (
                    dep.spec.min_ready_seconds
                ),

                #
                # Strategy
                #

                "strategy": {

                    "type": (
                        dep.spec.strategy.type
                        if dep.spec.strategy
                        else None
                    ),

                    "rolling_update": {

                        "max_surge": (
                            dep.spec.strategy
                            .rolling_update.max_surge
                            if (
                                dep.spec.strategy
                                and dep.spec.strategy.rolling_update
                            )
                            else None
                        ),

                        "max_unavailable": (
                            dep.spec.strategy
                            .rolling_update.max_unavailable
                            if (
                                dep.spec.strategy
                                and dep.spec.strategy.rolling_update
                            )
                            else None
                        ),
                    },
                },

                #
                # Selector
                #

                "selector": (
                    dep.spec.selector.match_labels
                    if dep.spec.selector
                    else {}
                ),

                #
                # Pod Template
                #

                "service_account": (
                    dep.spec.template.spec.service_account_name
                ),

                "node_selector": (
                    dep.spec.template.spec.node_selector
                    or {}
                ),

                "affinity": (
                    dep.spec.template.spec.affinity.to_dict()
                    if dep.spec.template.spec.affinity
                    else None
                ),

                "tolerations": [
                    t.to_dict()
                    for t in (
                        dep.spec.template.spec.tolerations
                        or []
                    )
                ],

                "volumes": [
                    v.to_dict()
                    for v in (
                        dep.spec.template.spec.volumes
                        or []
                    )
                ],

                #
                # Collections
                #

                "containers": [],
                "conditions": [],
                "replicasets": [],
                "hpa": None,
            }

            #
            # Containers
            #

            for container in (
                dep.spec.template.spec.containers
                or []
            ):

                deployment_resource["containers"].append({

                    "name": container.name,

                    "image": container.image,

                    "image_pull_policy": (
                        container.image_pull_policy
                    ),

                    "resources": {

                        "requests": (
                            container.resources.requests
                            or {}
                        ),

                        "limits": (
                            container.resources.limits
                            or {}
                        ),
                    },

                    "readiness_probe": (
                        container.readiness_probe.to_dict()
                        if container.readiness_probe
                        else None
                    ),

                    "liveness_probe": (
                        container.liveness_probe.to_dict()
                        if container.liveness_probe
                        else None
                    ),

                    "startup_probe": (
                        container.startup_probe.to_dict()
                        if container.startup_probe
                        else None
                    ),

                    "ports": [
                        p.to_dict()
                        for p in (
                            container.ports or []
                        )
                    ],

                    "env": [
                        e.to_dict()
                        for e in (
                            container.env or []
                        )
                    ],

                    "volume_mounts": [
                        m.to_dict()
                        for m in (
                            container.volume_mounts
                            or []
                        )
                    ],
                })

            #
            # Conditions
            #

            if status.conditions:

                for condition in status.conditions:

                    deployment_resource[
                        "conditions"
                    ].append({

                        "type": condition.type,

                        "status": condition.status,

                        "reason": condition.reason,

                        "message": condition.message,

                        "last_update_time": (
                            condition.last_update_time.isoformat()
                            if condition.last_update_time
                            else None
                        ),

                        "last_transition_time": (
                            condition.last_transition_time.isoformat()
                            if condition.last_transition_time
                            else None
                        ),
                    })
                                #
            # ReplicaSets
            #

            try:

                replicasets = (
                    k8s.apps
                    .list_namespaced_replica_set(
                        namespace=namespace
                    )
                    .items
                )

                deployment_resource["replicasets"] = [

                    rs.metadata.name

                    for rs in replicasets

                    if (
                        rs.metadata.owner_references
                        and rs.metadata.owner_references[0].uid
                        == dep.metadata.uid
                    )
                ]

            except ApiException:
                pass

            #
            # Horizontal Pod Autoscaler
            #

            try:

                hpas = (
                    k8s.autoscaling
                    .list_namespaced_horizontal_pod_autoscaler(
                        namespace=namespace
                    )
                    .items
                )

                for hpa in hpas:

                    target = hpa.spec.scale_target_ref

                    if (
                        target.kind == "Deployment"
                        and target.name == name
                    ):

                        deployment_resource["hpa"] = {

                            "name": hpa.metadata.name,

                            "min_replicas": (
                                hpa.spec.min_replicas
                            ),

                            "max_replicas": (
                                hpa.spec.max_replicas
                            ),

                            "current_replicas": (
                                hpa.status.current_replicas
                            ),

                            "desired_replicas": (
                                hpa.status.desired_replicas
                            ),

                            "target_cpu_utilization": (
                                getattr(
                                    hpa.spec,
                                    "target_cpu_utilization_percentage",
                                    None,
                                )
                            ),
                        }

                        break

            except Exception:
                pass

            result.resources.append(
                deployment_resource
            )

            #
            # Health
            #

            if (
                ready_replicas == desired_replicas
                and desired_replicas > 0
            ):

                healthy += 1
                available += 1

            elif ready_replicas == 0:

                unhealthy += 1
                failed_rollouts += 1

            else:

                partial += 1

            if (
                unavailable_replicas
                and unavailable_replicas > 0
            ):

                unhealthy += 1

        #
        # Metrics
        #

        result.metrics.extend([

            {
                "metric": "deployment_count",
                "value": len(
                    result.resources
                ),
            },

            {
                "metric": "healthy_deployments",
                "value": healthy,
            },

            {
                "metric": "unhealthy_deployments",
                "value": unhealthy,
            },

            {
                "metric": "fully_available_deployments",
                "value": available,
            },

            {
                "metric": "partially_available_deployments",
                "value": partial,
            },

            {
                "metric": "failed_rollouts",
                "value": failed_rollouts,
            },

            {
                "metric": "desired_replicas",
                "value": sum(
                    d["desired_replicas"]
                    for d in result.resources
                ),
            },

            {
                "metric": "ready_replicas",
                "value": sum(
                    d["ready_replicas"]
                    for d in result.resources
                ),
            },

            {
                "metric": "available_replicas",
                "value": sum(
                    d["available_replicas"]
                    for d in result.resources
                ),
            },

            {
                "metric": "updated_replicas",
                "value": sum(
                    d["updated_replicas"]
                    for d in result.resources
                ),
            },

            {
                "metric": "unavailable_replicas",
                "value": sum(
                    d["unavailable_replicas"]
                    for d in result.resources
                ),
            },
        ])

        return result