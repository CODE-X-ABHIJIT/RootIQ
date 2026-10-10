
import time

from rootiq.engine.result import EngineResult
from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient


class ValidationEngine:
    """Read-only validation of Kubernetes deployments and pods."""

    name = "ValidationEngine"

    def run(
        self,
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    ):
        start = time.perf_counter()

        result = EngineResult(engine=self.name)

        try:
            target = ClusterTarget(
                name="Local",
                context=context,
                namespace=namespace,
                cluster_wide=cluster_wide,
            )
            k8s = KubernetesClient(target)

            
            deployments = k8s.deployments()
            pods = k8s.pods()

            # Ignore Kubernetes infrastructure namespaces.
            system_namespaces = {
                "kube-system",
                "kube-public",
                "kube-node-lease",
                "local-path-storage",
            }

            deployments = [
                deployment
                for deployment in deployments
                if deployment.metadata.namespace not in system_namespaces
            ]

            pods = [
                pod
                for pod in pods
                if pod.metadata.namespace not in system_namespaces
            ]

            checks = []

            def add_check(name, passed, details):
                checks.append({
                    "check": name,
                    "status": "PASS" if passed else "FAIL",
                    "details": details,
                })

            for deployment in deployments:
                dep_name = deployment.metadata.name
                dep_namespace = deployment.metadata.namespace
                spec = deployment.spec
                status = deployment.status

                desired = spec.replicas or 0
                ready = status.ready_replicas or 0
                updated = status.updated_replicas or 0
                observed = status.observed_generation or 0
                generation = deployment.metadata.generation or 0

                prefix = f"{dep_namespace}/{dep_name}"

                add_check(
                    f"{prefix}: rollout",
                    observed >= generation
                    and updated == desired
                    and ready == desired,
                    f"desired={desired}, ready={ready}, "
                    f"updated={updated}, generation={generation}, "
                    f"observed_generation={observed}",
                )

                for container in spec.template.spec.containers or []:
                    resources = container.resources
                    requests = resources.requests or {} if resources else {}
                    limits = resources.limits or {} if resources else {}

                    missing = []
                    for key in ("cpu", "memory"):
                        if not requests.get(key):
                            missing.append(f"request.{key}")
                        if not limits.get(key):
                            missing.append(f"limit.{key}")

                    add_check(
                        f"{prefix}: container {container.name} resources",
                        not missing,
                        "All CPU/memory requests and limits are present"
                        if not missing
                        else "Missing: " + ", ".join(missing),
                    )

                selector = spec.selector.match_labels or {}
                matching_pods = [
                    pod for pod in pods
                    if pod.metadata.namespace == dep_namespace
                    and all(
                        (pod.metadata.labels or {}).get(key) == value
                        for key, value in selector.items()
                    )
                ]

                healthy_pods = [
                    pod for pod in matching_pods
                    if pod.status.phase == "Running"
                    and all(
                        container.ready
                        for container in (pod.status.container_statuses or [])
                    )
                    and len(pod.status.container_statuses or [])
                    == len(pod.spec.containers or [])
                ]

                add_check(
                    f"{prefix}: pod health",
                    len(healthy_pods) >= desired,
                    f"healthy={len(healthy_pods)}, desired={desired}, "
                    f"matching_pods={len(matching_pods)}",
                )

            if not deployments:
                add_check(
                    "Deployments discovered",
                    False,
                    "No Deployments were found in the selected scope.",
                )

            result.issues = [
                check for check in checks
                if check["status"] == "FAIL"
            ]
            result.success = all(
                check["status"] == "PASS" for check in checks
            )
            result.summary = {
                "status": "PASS" if result.success else "FAIL",
                "checks_total": len(checks),
                "checks_passed": sum(
                    check["status"] == "PASS" for check in checks
                ),
                "checks_failed": len(result.issues),
                "checks": checks,
            }

            result.add_log(
                "info" if result.success else "warning",
                f"Validation completed: {result.summary['checks_passed']}"
                f"/{result.summary['checks_total']} checks passed.",
            )

        except Exception as exc:
            result.success = False
            result.error = str(exc)
            result.summary = {"status": "ERROR"}
            result.add_log("error", f"Validation failed: {exc}")

        result.execution_time = round(
            time.perf_counter() - start, 4
        )
        return result