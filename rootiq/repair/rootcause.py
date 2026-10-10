from collections import defaultdict


class RootCauseEngine:
    name = "RootCauseEngine"

    def analyze(self, issues):
        grouped = defaultdict(list)

        for issue in issues:
            category = self.detect_category(issue)
            if category != "UNKNOWN":
                grouped[category].append(issue)

        root_causes = []

        for category, items in grouped.items():
            if category == "IMAGE":
                root_causes.append(
                    self.build_image_rootcause(items)
                )

            elif category == "RESOURCE":
                root_causes.append(
                    self.build_resource_rootcause(items)
                )

            elif category == "POD_HEALTH":
                root_causes.append(
                    self.build_restart_rootcause(items)
                )

        return root_causes

    def detect_category(self, issue):
        issue_id = issue.get("id", "")
        title = issue.get("title", "").lower()
        description = issue.get("description", "").lower()
        labels = issue.get("labels") or {}
        reason = str(labels.get("reason", "")).lower()

        # Image-pull failures take priority over restart findings.
        if (
            issue_id == "POD-003"
            or reason == "imagepullbackoff".lower()
            or "imagepullbackoff" in description
            or "errimagepull" in description
        ):
            return "IMAGE"

        if (
            "image" in title
            or issue_id in {"DEPLOYMENT-005", "POD-009"}
        ):
            return "IMAGE"

        if (
            "resource" in title
            or "cpu" in title
            or "memory" in title
            or issue_id == "DEPLOYMENT-006"
        ):
            return "RESOURCE"

        if (
            "restart" in title
            or "crash" in title
            or issue_id in {"POD-001", "POD-002"}
        ):
            return "POD_HEALTH"

        return "UNKNOWN"

    def build_image_rootcause(self, issues):
        resources = []
        evidence = []
        seen = set()

        for issue in issues:
            issue_id = issue.get("id", "")
            labels = issue.get("labels") or {}

            container = labels.get("container")
            image = labels.get("image")
            namespace = issue.get("namespace")
            resource = issue.get("resource")

            if issue_id == "DEPLOYMENT-005":
                # A Deployment-level image issue is already attached
                # to a workload, so it can be used as a repair target.
                key = (
                    "Deployment",
                    resource,
                    namespace,
                    container,
                )

                if key not in seen:
                    resources.append({
                        "resource": resource,
                        "namespace": namespace,
                        "container": container,
                        "image": image,
                        "issue_id": issue_id,
                        "kind": "Deployment",
                        "repair_blocked": False,
                    })
                    seen.add(key)

            elif issue_id == "POD-003":
                # Record the failed Pod as diagnostic evidence.
                evidence.append({
                    "pod": resource,
                    "namespace": namespace,
                    "container": container,
                    "image": image,
                    "reason": labels.get("reason"),
                })

                # Do not invent a replacement image. The planner must
                # resolve the Pod to its owning workload and block the
                # image update until an explicit replacement is supplied.
                key = (
                    "Pod",
                    resource,
                    namespace,
                    container,
                )

                if key not in seen:
                    resources.append({
                        "resource": resource,
                        "namespace": namespace,
                        "container": container,
                        "image": image,
                        "issue_id": issue_id,
                        "kind": "Pod",
                        "repair_blocked": True,
                        "blocked_reason": (
                            "Image pull failed. Supply an explicit, "
                            "verified replacement image before RootIQ "
                            "updates the owning workload."
                        ),
                    })
                    seen.add(key)

            elif issue_id == "POD-009":
                # Supporting image evidence; not an independent
                # replacement-image instruction.
                evidence.append({
                    "pod": resource,
                    "namespace": namespace,
                    "container": container,
                    "image": image,
                })

        return {
            "name": "Container image problem",
            "category": "IMAGE",
            "severity": "HIGH",
            "resources": resources,
            "evidence": evidence,
            "repair": "Verify and correct the container image",
        }

    def build_resource_rootcause(self, issues):
        resources = []
        seen = set()

        for issue in issues:
            issue_id = issue.get("id", "")
            labels = issue.get("labels") or {}

            if issue_id == "DEPLOYMENT-006":
                kind = "Deployment"
            elif issue_id.startswith("POD-"):
                kind = "Pod"
            else:
                kind = issue.get("kind") or "Pod"

            resource = issue.get("resource")
            namespace = issue.get("namespace")
            container = labels.get("container")

            key = (
                kind,
                resource,
                namespace,
                container,
            )

            if key in seen:
                continue

            seen.add(key)

            resources.append({
                "kind": kind,
                "resource": resource,
                "namespace": namespace,
                "container": container,
                "issue_id": issue_id,
            })

        return {
            "name": "Missing resource configuration",
            "category": "RESOURCE",
            "severity": "MEDIUM",
            "resources": resources,
            "repair": "Apply CPU and memory requests/limits",
        }

    def build_restart_rootcause(self, issues):
        resources = []
        seen = set()

        for issue in issues:
            labels = issue.get("labels") or {}
            resource = issue.get("resource")
            namespace = issue.get("namespace")
            container = labels.get("container")

            key = (resource, namespace)

            if key in seen:
                continue

            seen.add(key)

            resources.append({
                "resource": resource,
                "namespace": namespace,
                "container": container,
                "kind": issue.get("kind") or "Pod",
                "issue_id": issue.get("id", ""),
            })

        return {
            "name": "Application instability",
            "category": "POD_HEALTH",
            "severity": "HIGH",
            "resources": resources,
            "repair": "Restart workload",
        }
