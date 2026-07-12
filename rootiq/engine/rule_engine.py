import time

from rootiq.engine.result import EngineResult
from rootiq.engine.registry import registry


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

        #
        # Summary
        #

        result.summary.update(
            {
                "resource_type": resource_type,
                "rules_executed": len(rules),
                "resources_scanned": len(resources),
            }
        )

        #
        # Execute Rules
        #

        for rule in rules:

            try:

                rule_result = rule.evaluate(
                    resources
                )

            except Exception as e:

                result.success = False

                result.add_log(
                    "error",
                    (
                        f"{rule.__class__.__name__}: "
                        f"{e}"
                    ),
                )

                continue

            #
            # Issues
            #

            if hasattr(
                rule_result,
                "issues",
            ):

                result.issues.extend(
                    rule_result.issues
                )

            #
            # Logs
            #

            if hasattr(
                rule_result,
                "logs",
            ):

                result.logs.extend(
                    rule_result.logs
                )

            #
            # Metadata
            #

            if hasattr(
                rule_result,
                "metadata",
            ):

                result.metadata.update(
                    rule_result.metadata
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