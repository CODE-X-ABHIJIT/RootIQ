import time
from rootiq.rules.manager import RuleManager
from rootiq import collectors
from rootiq.collectors.manager import CollectorManager

from rootiq.engine.result import EngineResult
from rootiq.engine.rule_engine import RuleEngine

from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.client import KubernetesClient
from rules import registry


class InspectOrchestrator:
    """
    Coordinates the complete inspection workflow.

        CLI
         │
         ▼
    Kubernetes Client
         │
         ▼
      Collectors
         │
         ▼
     Rule Engine
         │
         ▼
    Aggregated Result
    """

    name = "InspectOrchestrator"

    def __init__(self):
        #
        # Discover Rules Once
        #

        RuleManager()
        print(
            "TOTAL RULES:",
            registry.rule_count()
        )

        print(
            "RULE TYPES:",
            registry.resource_types()
        )

        #
        # Rule Executor
        #

        self.rule_engine = RuleEngine()

        #
        # Built-in Collectors
        #

        self.collectors = CollectorManager().all()

    # ==================================================
    # Run Inspection
    # ==================================================

    def run(
        self,
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    ):

        start = time.perf_counter()

        #
        # Connect to Kubernetes
        #

        target = ClusterTarget(
            name="Local",
            context=context,
            namespace=namespace,
            cluster_wide=cluster_wide,
        )

        k8s = KubernetesClient(target)

        #
        # Engine Result
        #

        result = EngineResult(
            engine=self.name,
        )

        collector_summary = []

        #
        # Execute Collectors
        #

        for collector in self.collectors:

            collector_start = time.perf_counter()

            try:

                collect_result = collector.run(k8s)

            except Exception as e:

                result.success = False

                result.add_log(
                    "error",
                    f"{collector.name}: {e}",
                )

                continue

            #
            # Collector Summary
            #

            collector_summary.append(
                {
                    "collector": collector.name,
                    "resource_type": collector.resource_type,
                    "resources": len(
                        collect_result.resources
                    ),
                    "execution_time": round(
                        collect_result.execution_time,
                        4,
                    ),
                }
            )

            #
            # Merge Collector Logs
            #

            result.logs.extend(
                collect_result.logs
            )

            #
            # Execute Rules
            #

            engine_result = self.rule_engine.run(
                collector.resource_type,
                collect_result.resources,
            )

            #
            # Merge Rule Results
            #

            result.issues.extend(
                engine_result.issues
            )

            result.logs.extend(
                engine_result.logs
            )

            result.metadata[
                collector.resource_type
            ] = {
                "collector": collector.name,
                "resource_count": len(
                    collect_result.resources
                ),
                "metrics": collect_result.metrics,
                "execution_time": round(
                    time.perf_counter()
                    - collector_start,
                    4,
                ),
            }

        #
        # Summary
        #

        result.summary = {
            "collectors_executed": len(
                collector_summary
            ),
            "resources_scanned": sum(
                item["resources"]
                for item in collector_summary
            ),
            "issues_found": len(
                result.issues
            ),
            "cluster_status": (
                "Healthy"
                if not result.issues
                else "Issues Detected"
            ),
        }

        result.metadata[
            "collectors"
        ] = collector_summary

        result.execution_time = round(
            time.perf_counter() - start,
            4,
        )

        return result