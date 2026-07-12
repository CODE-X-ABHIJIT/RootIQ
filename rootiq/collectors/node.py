from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class NodeCollector(BaseCollector):
    enabled = True
    name = "NodeCollector"
    resource_type = "node"

    def collect(self, k8s):

        result = CollectResult(
            collector=self.name
        )

        try:

            nodes = k8s.core.list_node().items

        except ApiException as e:

            result.success = False
            result.error = str(e)

            return result

        ready_nodes = 0
        not_ready_nodes = 0
        control_plane_nodes = 0
        worker_nodes = 0
        tainted_nodes = 0

        for node in nodes:

            #
            # Roles
            #

            labels = node.metadata.labels or {}

            roles = []

            if "node-role.kubernetes.io/control-plane" in labels:
                roles.append("control-plane")

            if "node-role.kubernetes.io/master" in labels:
                roles.append("master")

            if not roles:
                roles.append("worker")

            if "worker" in roles:
                worker_nodes += 1
            else:
                control_plane_nodes += 1

            #
            # Conditions
            #

            conditions = []
            ready = False

            for condition in node.status.conditions or []:

                conditions.append(
                    {
                        "type": condition.type,
                        "status": condition.status,
                        "reason": condition.reason,
                        "message": condition.message,
                        "last_transition_time": (
                            condition.last_transition_time.isoformat()
                            if condition.last_transition_time
                            else None
                        ),
                    }
                )

                if condition.type == "Ready":

                    if condition.status == "True":

                        ready = True
                        ready_nodes += 1

                    else:

                        not_ready_nodes += 1

                        result.issues.append(
                            {
                                "severity": "critical",
                                "resource": node.metadata.name,
                                "reason": "Node NotReady",
                            }
                        )

                elif (
                    condition.type == "MemoryPressure"
                    and condition.status == "True"
                ):

                    result.issues.append(
                        {
                            "severity": "high",
                            "resource": node.metadata.name,
                            "reason": "MemoryPressure=True",
                        }
                    )

                elif (
                    condition.type == "DiskPressure"
                    and condition.status == "True"
                ):

                    result.issues.append(
                        {
                            "severity": "high",
                            "resource": node.metadata.name,
                            "reason": "DiskPressure=True",
                        }
                    )

                elif (
                    condition.type == "PIDPressure"
                    and condition.status == "True"
                ):

                    result.issues.append(
                        {
                            "severity": "high",
                            "resource": node.metadata.name,
                            "reason": "PIDPressure=True",
                        }
                    )

            #
            # Taints
            #

            taints = []

            if node.spec.taints:

                tainted_nodes += 1

                for taint in node.spec.taints:

                    taints.append(
                        {
                            "key": taint.key,
                            "value": taint.value,
                            "effect": taint.effect,
                        }
                    )

            #
            # Unschedulable
            #

            if node.spec.unschedulable:

                result.issues.append(
                    {
                        "severity": "medium",
                        "resource": node.metadata.name,
                        "reason": "Node is cordoned",
                    }
                )

            #
            # Addresses
            #

            addresses = []

            for address in node.status.addresses or []:

                addresses.append(
                    {
                        "type": address.type,
                        "address": address.address,
                    }
                )

            #
            # Images
            #

            images = []

            for image in node.status.images or []:

                images.extend(image.names)

            #
            # System Info
            #

            info = node.status.node_info

            system_info = {
                "architecture": info.architecture,
                "operating_system": info.operating_system,
                "os_image": info.os_image,
                "kernel_version": info.kernel_version,
                "container_runtime": info.container_runtime_version,
                "kubelet_version": info.kubelet_version,
                "kube_proxy_version": info.kube_proxy_version,
                "machine_id": info.machine_id,
                "system_uuid": info.system_uuid,
                "boot_id": info.boot_id,
            }

            #
            # Resource
            #

            result.resources.append(
                {
                    "name": node.metadata.name,
                    "uid": node.metadata.uid,
                    "creation_timestamp": (
                        node.metadata.creation_timestamp.isoformat()
                    ),
                    "roles": roles,
                    "ready": ready,
                    "unschedulable": node.spec.unschedulable,
                    "capacity": dict(node.status.capacity or {}),
                    "allocatable": dict(node.status.allocatable or {}),
                    "addresses": addresses,
                    "conditions": conditions,
                    "taints": taints,
                    "system_info": system_info,
                    "labels": labels,
                    "annotations": node.metadata.annotations or {},
                    "images": images,
                }
            )

        #
        # Metrics
        #

        result.metrics.extend(
            [
                {
                    "metric": "node_count",
                    "value": len(nodes),
                },
                {
                    "metric": "ready_nodes",
                    "value": ready_nodes,
                },
                {
                    "metric": "not_ready_nodes",
                    "value": not_ready_nodes,
                },
                {
                    "metric": "control_plane_nodes",
                    "value": control_plane_nodes,
                },
                {
                    "metric": "worker_nodes",
                    "value": worker_nodes,
                },
                {
                    "metric": "tainted_nodes",
                    "value": tainted_nodes,
                },
            ]
        )

        return result