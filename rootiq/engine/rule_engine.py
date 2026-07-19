import time

from rootiq.engine.result import EngineResult
from rootiq.engine.registry import registry
from rootiq.engine.rule_context import RuleContext


class RuleEngine:
    """
    Executes registered rules against
    collected Kubernetes resources.
    """

    name = "RuleEngine"

    # ==================================================
    # Run Rules
    # ==================================================

    def run(
        self,
        resource_type: str,
        resources: list,
    ):

        start = time.perf_counter()

        result = EngineResult(
            engine=self.name
        )

        #
        # Fetch rules
        #

        rules = registry.get_rules(
            resource_type
        )

        if not rules:

            result.add_log(
                "warning",
                (
                    f"No rules registered "
                    f"for '{resource_type}'."
                ),
            )

            result.summary.update(
                {
                    "resource_type": resource_type,
                    "rules_executed": 0,
                    "resources_scanned": len(
                        resources
                    ),
                    "issues_found": 0,
                }
            )

            result.execution_time = (
                time.perf_counter()
                - start
            )
            return result

            
        context = RuleContext(
            resources=resources,
        )

        for rule in rules:

            try:

                rule.evaluate(context)

            except Exception as e:

                result.success = False

                result.add_log(
                    "error",
                    f"{rule.__class__.__name__}: {e}",
                )

                continue

        #
        # Merge everything produced by rules
        #

        result.issues.extend(
            context.issues
        )

        result.logs.extend(
            context.logs
        )

        result.metadata.update(
            context.metadata
        )
        #
        # Summary
        #

        result.summary.update(
            {
                "resource_type": resource_type,
                "rules_executed": len(rules),
                "resources_scanned": len(resources),
                "issues_found": len(context.issues),
            }
        )

       
        #
        # Severity Summary
        #

        severity_summary = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "INFO": 0,
        }

        for issue in result.issues:

            severity = getattr(
                issue,
                "severity",
                None,
            )

            if hasattr(
                severity,
                "value",
            ):

                severity = severity.value

            if severity:

                severity = severity.upper()

                if severity in severity_summary:

                    severity_summary[
                        severity
                    ] += 1

        #
        # Final Summary
        #

        result.summary.update(
            {
                "issues_found": len(
                    result.issues
                ),
                "severity": severity_summary,
            }
        )

        result.execution_time = (
            time.perf_counter()
            - start
        )

        result.success = True
        return result
        