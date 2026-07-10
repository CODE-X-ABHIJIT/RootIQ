from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class PodCollector(BaseCollector):

    name = "PodCollector"

    def collect(self, k8s):

        result = CollectResult(collector=self.name)

        pods = k8s.pods()

        for pod in pods:

            pod_data = {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "uid": pod.metadata.uid,
                "node": pod.spec.node_name,
                "phase": pod.status.phase,
                "pod_ip": pod.status.pod_ip,
                "host_ip": pod.status.host_ip,
                "qos_class": pod.status.qos_class,
                "service_account": pod.spec.service_account_name,
                "creation_timestamp": (
                    pod.metadata.creation_timestamp.isoformat()
                    if pod.metadata.creation_timestamp
                    else None
                ),
                "labels": pod.metadata.labels or {},
                "annotations": pod.metadata.annotations or {},
                "owner": (
                    pod.metadata.owner_references[0].kind
                    if pod.metadata.owner_references
                    else None
                ),
                "containers": [],
                "init_containers": [],
                "conditions": [],
            }

            #
            # Build lookup for container specs
            #

            container_specs = {
                c.name: c for c in (pod.spec.containers or [])
            }

            #
            # Container Status
            #

            if pod.status.container_statuses:

                for status in pod.status.container_statuses:

                    spec = container_specs.get(status.name)

                    state = {}
                    last_state = {}

                    #
                    # Current State
                    #

                    if status.state:

                        if status.state.waiting:
                            state = {
                                "waiting": {
                                    "reason": status.state.waiting.reason,
                                    "message": status.state.waiting.message,
                                }
                            }

                        elif status.state.running:
                            state = {
                                "running": {
                                    "started_at": (
                                        status.state.running.started_at.isoformat()
                                        if status.state.running.started_at
                                        else None
                                    )
                                }
                            }

                        elif status.state.terminated:
                            state = {
                                "terminated": {
                                    "reason": status.state.terminated.reason,
                                    "message": status.state.terminated.message,
                                    "exit_code": status.state.terminated.exit_code,
                                    "signal": status.state.terminated.signal,
                                    "finished_at": (
                                        status.state.terminated.finished_at.isoformat()
                                        if status.state.terminated.finished_at
                                        else None
                                    ),
                                }
                            }

                    #
                    # Previous State
                    #

                    if (
                        status.last_state
                        and status.last_state.terminated
                    ):

                        last_state = {
                            "terminated": {
                                "reason": status.last_state.terminated.reason,
                                "message": status.last_state.terminated.message,
                                "exit_code": status.last_state.terminated.exit_code,
                                "signal": status.last_state.terminated.signal,
                                "finished_at": (
                                    status.last_state.terminated.finished_at.isoformat()
                                    if status.last_state.terminated.finished_at
                                    else None
                                ),
                            }
                        }

                    #
                    # Resources
                    #

                    requests = {}
                    limits = {}

                    if spec and spec.resources:

                        requests = spec.resources.requests or {}
                        limits = spec.resources.limits or {}

                    #
                    # Probes
                    #

                    readiness_probe = (
                        spec.readiness_probe.to_dict()
                        if spec and spec.readiness_probe
                        else None
                    )

                    liveness_probe = (
                        spec.liveness_probe.to_dict()
                        if spec and spec.liveness_probe
                        else None
                    )

                    startup_probe = (
                        spec.startup_probe.to_dict()
                        if (
                            spec
                            and hasattr(spec, "startup_probe")
                            and spec.startup_probe
                        )
                        else None
                    )

                    pod_data["containers"].append(
                        {
                            "name": status.name,
                            "ready": status.ready,
                            "started": status.started,
                            "restart_count": status.restart_count,
                            "image": status.image,
                            "image_id": status.image_id,
                            "container_id": status.container_id,
                            "state": state,
                            "last_state": last_state,
                            "resources": {
                                "requests": requests,
                                "limits": limits,
                            },
                            "readiness_probe": readiness_probe,
                            "liveness_probe": liveness_probe,
                            "startup_probe": startup_probe,
                            "image_pull_policy": (
                                spec.image_pull_policy
                                if spec
                                else None
                            ),
                        }
                    )

            #
            # Init Containers
            #

            if pod.spec.init_containers:

                for container in pod.spec.init_containers:

                    pod_data["init_containers"].append(
                        {
                            "name": container.name,
                            "image": container.image,
                            "resources": {
                                "requests": (
                                    container.resources.requests or {}
                                )
                                if container.resources
                                else {},
                                "limits": (
                                    container.resources.limits or {}
                                )
                                if container.resources
                                else {},
                            },
                        }
                    )

            #
            # Conditions
            #

            if pod.status.conditions:

                for condition in pod.status.conditions:

                    pod_data["conditions"].append(
                        {
                            "type": condition.type,
                            "status": condition.status,
                            "reason": condition.reason,
                            "message": condition.message,
                        }
                    )

            result.resources.append(pod_data)

        #
        # Metrics
        #

        result.metrics.extend(
            [
                {
                    "metric": "pod_count",
                    "value": len(result.resources),
                },
                {
                    "metric": "running_pods",
                    "value": sum(
                        1
                        for p in result.resources
                        if p["phase"] == "Running"
                    ),
                },
                {
                    "metric": "pending_pods",
                    "value": sum(
                        1
                        for p in result.resources
                        if p["phase"] == "Pending"
                    ),
                },
                {
                    "metric": "failed_pods",
                    "value": sum(
                        1
                        for p in result.resources
                        if p["phase"] == "Failed"
                    ),
                },
                {
                    "metric": "succeeded_pods",
                    "value": sum(
                        1
                        for p in result.resources
                        if p["phase"] == "Succeeded"
                    ),
                },
            ]
        )

        return result