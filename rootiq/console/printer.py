from collections import Counter


class ConsolePrinter:
    """
    Pretty terminal output for RootIQ.

    Handles only console display.
    """

    # ==================================================
    # Inspection Summary
    # ==================================================

    def print_summary(
        self,
        result,
        incident_id=None,
    ):

        print()

        print("=" * 60)
        print("ROOTIQ INSPECTION COMPLETED")
        print("=" * 60)

        summary = result.summary

        print(
            f"Resources Scanned : {summary.get('resources_scanned', 0)}"
        )

        print(
            f"Issues Found      : {summary.get('issues_found', 0)}"
        )

        print(
            f"Cluster Status    : {summary.get('cluster_status', 'Unknown')}"
        )

        print(
            f"Execution Time    : {result.execution_time:.2f}s"
        )

        #
        # Severity Summary
        #

        if result.issues:

            severity = Counter()

            for issue in result.issues:

                level = (
                    getattr(issue, "severity", "UNKNOWN")
                ).upper()

                severity[level] += 1

            print()
            print("Severity")

            for level in (
                "CRITICAL",
                "HIGH",
                "MEDIUM",
                "LOW",
                "INFO",
            ):

                print(
                    f"  {level:<8}: {severity[level]}"
                )

            print()
            print("Detected Issues")

            for issue in result.issues:

                print(
                    f"[{issue['id']}] "
                    f"{issue['title']} "
                    f"({issue['severity']})"
                )

        else:

            print()
            print("No issues detected.")

        #
        # Saved Location
        #

        if incident_id:

            print()
            print(
                f"Inspection ID : {incident_id}"
            )

            print(
                f"Saved To      : incidents/{incident_id}/inspect.json"
            )

        print("=" * 60)
        print()