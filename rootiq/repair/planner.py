import json
import shlex
import subprocess

from rootiq.config.config_loader import RootIQConfig


class RepairPlanner:
    SUPPORTED_WORKLOADS = {
        "Deployment",
        "StatefulSet",
        "DaemonSet",
    }

    WORKLOAD_KIND_MAP = {
        "deployment": "Deployment",
        "statefulset": "StatefulSet",
        "daemonset": "DaemonSet",
    }

    CATEGORIES = {
        "IMAGE",
        "RESOURCE",
        "POD_HEALTH",
    }

    def __init__(self):
        self._owner_cache = {}
        self._planned = set()
        self.config = RootIQConfig()

    # ---------------------------------------------------------
    # Configuration helpers
    # ---------------------------------------------------------

    def _repair_config(self):
        config = getattr(self.config, "repair", {}) or {}
        return config if isinstance(config, dict) else {}

    def _configured_replacement_image(self, target, container):
        """
        Find an explicitly configured replacement image.

        Expected configuration key:
            <namespace>/<workload-name>/<container-name>

        Example:
            rootiq-lab/repair-image-test/nginx: <chosen-image>
        """
        if not target or not container:
            return None

        replacements = self._repair_config().get(
            "image_replacements", {}
        )

        if not isinstance(replacements, dict):
            return None

        key = (
            f"{target['namespace']}/"
            f"{target['name']}/"
            f"{container}"
        )

        image = replacements.get(key)

        if isinstance(image, str) and image.strip():
            return image.strip()

        return None

    def _replacement_image(self, resource, target):
        """
        Prefer an explicitly supplied image or configured mapping.
        If neither exists, replace the current image tag with :latest.
        """
        for field in (
            "replacement_image",
            "verified_replacement_image",
        ):
            value = resource.get(field)

            if isinstance(value, str) and value.strip():
                return value.strip()

        configured = self._configured_replacement_image(
            target,
            resource.get("container"),
        )

        if configured:
            return configured

        current_image = resource.get("image")

        if not isinstance(current_image, str) or not current_image.strip():
            return None

        current_image = current_image.strip()

        # Remove an image digest if present.
        repository = current_image.split("@", 1)[0]

        # Remove the existing tag without confusing registry ports
        # such as registry.example.com:5000/myapp:bad-tag.
        last_slash = repository.rfind("/")
        last_colon = repository.rfind(":")

        if last_colon > last_slash:
            repository = repository[:last_colon]

        if not repository:
            return None

        return f"{repository}:latest"
    # ---------------------------------------------------------
    # Kubernetes read helpers
    # ---------------------------------------------------------

    def _kubectl_json(self, *args):
        try:
            result = subprocess.run(
                ["kubectl", *args, "-o", "json"],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None

        if result.returncode != 0:
            return None

        try:
            return json.loads(result.stdout)
        except (json.JSONDecodeError, TypeError):
            return None

    @staticmethod
    def _controller_owner(owner_refs):
        owner_refs = owner_refs or []

        for owner in owner_refs:
            if owner.get("controller") is True:
                return owner

        return owner_refs[0] if owner_refs else None

    def _resolve_workload(self, resource):
        """
        Resolve a Deployment, StatefulSet or DaemonSet directly.

        For Pods, follow the owning controller. Deployment Pods are
        normally owned by a ReplicaSet, which is owned by a Deployment.
        """
        namespace = resource.get("namespace")
        name = resource.get("resource") or resource.get("name")
        kind = resource.get("kind", "")

        if not namespace or not name:
            return None

        actual_kind = self.WORKLOAD_KIND_MAP.get(
            str(kind).lower()
        )

        if actual_kind:
            return {
                "kind": actual_kind,
                "name": name,
                "namespace": namespace,
            }

        cache_key = (namespace, name)

        if cache_key in self._owner_cache:
            return self._owner_cache[cache_key]

        pod = self._kubectl_json(
            "get",
            "pod",
            name,
            "-n",
            namespace,
        )

        if not pod:
            self._owner_cache[cache_key] = None
            return None

        owner = self._controller_owner(
            pod.get("metadata", {}).get("ownerReferences")
        )

        if not owner:
            self._owner_cache[cache_key] = None
            return None

        owner_kind = owner.get("kind")
        owner_name = owner.get("name")

        # Follow Pod -> ReplicaSet -> Deployment.
        if owner_kind == "ReplicaSet":
            replica_set = self._kubectl_json(
                "get",
                "replicaset",
                owner_name,
                "-n",
                namespace,
            )

            if not replica_set:
                self._owner_cache[cache_key] = None
                return None

            owner = self._controller_owner(
                replica_set.get("metadata", {}).get(
                    "ownerReferences"
                )
            )

            if not owner:
                self._owner_cache[cache_key] = None
                return None

            owner_kind = owner.get("kind")
            owner_name = owner.get("name")

        canonical_kind = self.WORKLOAD_KIND_MAP.get(
            str(owner_kind).lower()
        )

        if not canonical_kind or not owner_name:
            self._owner_cache[cache_key] = None
            return None

        resolved = {
            "kind": canonical_kind,
            "name": owner_name,
            "namespace": namespace,
        }

        self._owner_cache[cache_key] = resolved
        return resolved

    @staticmethod
    def _target_args(target):
        return f"{target['kind'].lower()}/{target['name']}"

    @staticmethod
    def _target_key(target):
        return (
            target["kind"],
            target["name"],
            target["namespace"],
        )

    def _get_workload(self, target):
        return self._kubectl_json(
            "get",
            target["kind"].lower(),
            target["name"],
            "-n",
            target["namespace"],
        )

    @staticmethod
    def _get_container(workload_data, container_name):
        containers = (
            workload_data.get("spec", {})
            .get("template", {})
            .get("spec", {})
            .get("containers", [])
        )

        for container in containers:
            if container.get("name") == container_name:
                return container

        return None

    # ---------------------------------------------------------
    # Blocked actions
    # ---------------------------------------------------------

    def _blocked(self, category, resource, reason):
        return {
            "action": f"{category} repair blocked",
            "resource": {
                "kind": resource.get("kind", "Pod"),
                "name": (
                    resource.get("resource")
                    or resource.get("name")
                ),
                "namespace": resource.get("namespace"),
            },
            "reason": reason,
            "command": None,
            "rollback": None,
            "risk": "UNKNOWN",
            "status": "BLOCKED",
        }

    def _blocked_workload(self, category, target, reason):
        return {
            "action": f"{category} repair blocked",
            "resource": target,
            "reason": reason,
            "command": None,
            "rollback": None,
            "risk": "UNKNOWN",
            "status": "BLOCKED",
        }

    # ---------------------------------------------------------
    # IMAGE repair
    # ---------------------------------------------------------

    def _plan_image_action(self, resource, target, replacement_image):
        container_name = resource.get("container")

        if not container_name:
            return self._blocked_workload(
                "IMAGE",
                target,
                "Container name is missing. Image update blocked.",
            )

        if not replacement_image:
            return self._blocked_workload(
                "IMAGE",
                target,
                "No replacement image was configured. Set an explicit "
                "replacement_image or configure repair.image_replacements.",
            )

        workload_data = self._get_workload(target)

        if not workload_data:
            return self._blocked_workload(
                "IMAGE",
                target,
                "Could not read the owning workload from Kubernetes.",
            )

        container_data = self._get_container(
            workload_data,
            container_name,
        )

        if not container_data:
            return self._blocked_workload(
                "IMAGE",
                target,
                f"Container '{container_name}' was not found in "
                "the owning workload.",
            )

        current_image = container_data.get("image")

        # Do not generate a pointless image update.
        if current_image == replacement_image:
            return None

        namespace = target["namespace"]
        workload = self._target_args(target)

        image_assignment = (
            f"{container_name}={replacement_image}"
        )

        command = (
            f"kubectl set image "
            f"{shlex.quote(workload)} "
            f"{shlex.quote(image_assignment)} "
            f"-n {shlex.quote(namespace)}"
        )

        rollback = (
            f"kubectl rollout undo "
            f"{shlex.quote(workload)} "
            f"-n {shlex.quote(namespace)}"
        )

        return {
            "action": "Update container image",
            "resource": target,
            "container": container_name,
            "current_image": current_image,
            "replacement_image": replacement_image,
            "reason": (
                "Replace the failing container image on the owning "
                "workload. Kubernetes will start a new rollout."
            ),
            "command": command,
            "rollback": rollback,
            "risk": "HIGH",
            "status": "PENDING_APPROVAL",
        }

    # ---------------------------------------------------------
    # RESOURCE repair
    # ---------------------------------------------------------

    def _plan_resource_action(self, resource, target):
        container_name = resource.get("container")

        if not container_name:
            return self._blocked_workload(
                "RESOURCE",
                target,
                "Container name is missing. Resource patch blocked.",
            )

        workload_data = self._get_workload(target)

        if not workload_data:
            return self._blocked_workload(
                "RESOURCE",
                target,
                "Could not read the owning workload from Kubernetes.",
            )

        container_data = self._get_container(
            workload_data,
            container_name,
        )

        if not container_data:
            return self._blocked_workload(
                "RESOURCE",
                target,
                f"Container '{container_name}' was not found in "
                "the owning workload.",
            )

        repair_config = self._repair_config()
        profiles = repair_config.get("resource_profiles", {})
        profile = (
            profiles.get("default", {})
            if isinstance(profiles, dict)
            else {}
        )

        profile_requests = profile.get("requests") or {}
        profile_limits = profile.get("limits") or {}

        # Explicit root-cause values override profile defaults.
        requests = {
            **profile_requests,
            **(resource.get("requests") or {}),
        }
        limits = {
            **profile_limits,
            **(resource.get("limits") or {}),
        }

        if not requests and not limits:
            return self._blocked_workload(
                "RESOURCE",
                target,
                "No CPU/memory values were supplied by root-cause "
                "analysis or the default resource profile.",
            )

        current_resources = container_data.get("resources") or {}
        resources_patch = {}

        # Add only missing values. Existing values are not overwritten.
        for field, desired_values in (
            ("requests", requests),
            ("limits", limits),
        ):
            current_values = current_resources.get(field) or {}
            missing_values = {}

            for key, value in desired_values.items():
                current_value = current_values.get(key)

                if current_value is None or current_value == "":
                    missing_values[key] = value

            if missing_values:
                resources_patch[field] = missing_values

        # No unnecessary patch if every desired field already exists.
        if not resources_patch:
            return None

        workload = self._target_args(target)
        namespace = target["namespace"]

        patch = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": container_name,
                            "resources": resources_patch,
                        }]
                    }
                }
            }
        }

        # Strategic merge patch treats null values as deletions.
        # This rollback removes only the fields this action adds.
        rollback_resources = {}

        for field, values in resources_patch.items():
            rollback_resources[field] = {
                key: None for key in values
            }

        rollback_patch = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": container_name,
                            "resources": rollback_resources,
                        }]
                    }
                }
            }
        }

        command = (
            f"kubectl patch {shlex.quote(workload)} "
            f"--type=strategic "
            f"-p {shlex.quote(json.dumps(patch))} "
            f"-n {shlex.quote(namespace)}"
        )

        rollback = (
            f"kubectl patch {shlex.quote(workload)} "
            f"--type=strategic "
            f"-p {shlex.quote(json.dumps(rollback_patch))} "
            f"-n {shlex.quote(namespace)}"
        )

        return {
            "action": "Apply missing resource settings",
            "resource": target,
            "container": container_name,
            "reason": (
                "Add only CPU/memory fields that are missing from "
                "the current workload specification."
            ),
            "command": command,
            "rollback": rollback,
            "risk": "MEDIUM",
            "status": "PENDING_APPROVAL",
        }

    # ---------------------------------------------------------
    # POD HEALTH repair
    # ---------------------------------------------------------

    def _plan_pod_health_action(self, target):
        namespace = target["namespace"]
        workload = self._target_args(target)

        return {
            "action": "Restart workload",
            "resource": target,
            "reason": (
                "Restart the owning workload because a restart-related "
                "issue was detected and no image-pull failure explains it."
            ),
            "command": (
                f"kubectl rollout restart "
                f"{shlex.quote(workload)} "
                f"-n {shlex.quote(namespace)}"
            ),
            "rollback": None,
            "risk": "MEDIUM",
            "status": "PENDING_APPROVAL",
        }

    # ---------------------------------------------------------
    # Grouping helpers
    # ---------------------------------------------------------

    @staticmethod
    def _container_group_key(record):
        target = record["target"]
        container = record["resource"].get("container")

        return (
            target["kind"],
            target["name"],
            target["namespace"],
            container,
        )

    def _merge_resource_inputs(self, records, target):
        """
        Merge duplicate resource findings for one workload/container.

        Conflicting requested values are blocked rather than selected
        arbitrarily.
        """
        merged = dict(records[0]["resource"])
        merged_requests = {}
        merged_limits = {}

        for record in records:
            resource = record["resource"]

            for field, destination in (
                ("requests", merged_requests),
                ("limits", merged_limits),
            ):
                values = resource.get(field) or {}

                for key, value in values.items():
                    if (
                        key in destination
                        and destination[key] != value
                    ):
                        return None, self._blocked_workload(
                            "RESOURCE",
                            target,
                            f"Conflicting {field} values for "
                            f"'{key}' were found. Resolve the "
                            "conflict before applying a patch.",
                        )

                    destination[key] = value

        if merged_requests:
            merged["requests"] = merged_requests

        if merged_limits:
            merged["limits"] = merged_limits

        return merged, None

    # ---------------------------------------------------------
    # Main planner
    # ---------------------------------------------------------

    def create_plan(self, root_causes):
        actions = []

        self._owner_cache.clear()
        self._planned.clear()

        records_by_category = {
            category: []
            for category in self.CATEGORIES
        }

        unresolved_records = []

        # Resolve all targets first. Planning must not depend on the
        # order in which the root-cause engine returned its categories.
        for cause in root_causes:
            category = str(cause.get("category", "")).upper()

            if category not in self.CATEGORIES:
                continue

            for resource in cause.get("resources", []):
                target = self._resolve_workload(resource)

                record = {
                    "category": category,
                    "resource": resource,
                    "target": target,
                }

                if target is None:
                    unresolved_records.append(record)
                else:
                    records_by_category[category].append(record)

        # An image-pull failure already explains the failed rollout.
        # Restarting the same workload will not repair the bad image.
        image_target_keys = {
            self._target_key(record["target"])
            for record in records_by_category["IMAGE"]
        }

        # -----------------------------------------------------
        # Unresolved resource blockers
        # -----------------------------------------------------

        for record in unresolved_records:
            resource = record["resource"]
            category = record["category"]

            key = (
                "UNRESOLVED",
                category,
                resource.get("namespace"),
                resource.get("resource") or resource.get("name"),
            )

            if key in self._planned:
                continue

            self._planned.add(key)

            actions.append(self._blocked(
                category,
                resource,
                "Could not resolve the owning Deployment, "
                "StatefulSet, or DaemonSet. No command generated.",
            ))

        # -----------------------------------------------------
        # IMAGE actions: one per workload/container
        # -----------------------------------------------------

        image_groups = {}

        for record in records_by_category["IMAGE"]:
            key = self._container_group_key(record)
            image_groups.setdefault(key, []).append(record)

        for key, records in image_groups.items():
            target = records[0]["target"]
            container = key[3]

            replacements = set()

            for record in records:
                replacement = self._replacement_image(
                    record["resource"],
                    target,
                )

                if replacement:
                    replacements.add(replacement)

            if not container:
                actions.append(self._blocked_workload(
                    "IMAGE",
                    target,
                    "Container name is missing. Image update blocked.",
                ))
                continue

            if len(replacements) > 1:
                actions.append(self._blocked_workload(
                    "IMAGE",
                    target,
                    "Conflicting replacement images were configured "
                    "for the same workload/container. Choose one "
                    "replacement image before proceeding.",
                ))
                continue

            if not replacements:
                reason = next(
                    (
                        record["resource"].get("blocked_reason")
                        for record in records
                        if record["resource"].get("blocked_reason")
                    ),
                    None,
                )

                actions.append(self._blocked_workload(
                    "IMAGE",
                    target,
                    reason or (
                        "No replacement image was supplied. Configure "
                        "repair.image_replacements or provide an explicit "
                        "replacement_image before execution."
                    ),
                ))
                continue

            replacement_image = next(iter(replacements))

            action_resource = dict(records[0]["resource"])
            action_resource["replacement_image"] = replacement_image

            action = self._plan_image_action(
                action_resource,
                target,
                replacement_image,
            )

            # None means the workload already uses the requested image.
            if action:
                actions.append(action)

        # -----------------------------------------------------
        # RESOURCE actions: one per workload/container
        # -----------------------------------------------------

        resource_groups = {}

        for record in records_by_category["RESOURCE"]:
            key = self._container_group_key(record)
            resource_groups.setdefault(key, []).append(record)

        for key, records in resource_groups.items():
            target = records[0]["target"]

            merged_resource, conflict_action = (
                self._merge_resource_inputs(records, target)
            )

            if conflict_action:
                actions.append(conflict_action)
                continue

            action = self._plan_resource_action(
                merged_resource,
                target,
            )

            if action:
                actions.append(action)

        # -----------------------------------------------------
        # POD_HEALTH actions
        # -----------------------------------------------------

        restart_targets = set()

        for record in records_by_category["POD_HEALTH"]:
            target = record["target"]
            target_key = self._target_key(target)

            # Do not restart a workload while its image-pull failure
            # remains the known cause. The image update itself triggers
            # a new rollout when it is approved and executed.
            if target_key in image_target_keys:
                continue

            if target_key in restart_targets:
                continue

            restart_targets.add(target_key)

            actions.append(
                self._plan_pod_health_action(target)
            )

        return actions