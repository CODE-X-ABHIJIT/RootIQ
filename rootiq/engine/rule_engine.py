import time

from rootiq.engine.result import EngineResult
from rootiq.engine.registry import registry


class RuleEngine:
    """
    Executes all registered rules against
    collector resources.
    """

    name = "RuleEngine"

    def run(
        self,
        resource_type: str,
        resources: list,
    ):

        start = time.perf_counter()

        result = EngineResult(
            engine=self.name
        )

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

            result.execution_time = (
                time.perf_counter()
                - start
            )

            return result

        result.summary.update(
            {
                "resource_type": resource_type,
                "rules_executed": len(rules),
                "resources_scanned": len(resources),
            }
        )

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
            # Merge Issues
            #

            if hasattr(
                rule_result,
                "issues",
            ):

                result.issues.extend(
                    rule_result.issues
                )

            #
            # Merge Logs
            #

            if hasattr(
                rule_result,
                "logs",
            ):

                result.logs.extend(
                    rule_result.logs
                )
                            #
            # Merge Metadata
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
            "Critical": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0,
            "Info": 0,
        }

        for issue in result.issues:

            severity = getattr(
                issue,
                "severity",
                None,
            )

            if severity in severity_summary:

                severity_summary[
                    severity
                ] += 1

        #
        # Update Summary
        #

        result.summary.update(
            {
                "issues_found": len(
                    result.issues
                ),
                "severity": severity_summary,
            }
        )

        #
        # Execution Time
        #

        result.execution_time = (
            time.perf_counter()
            - start
        )

        #
        # Success
        #

        result.success = True

        return result