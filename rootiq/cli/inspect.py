from rootiq.orchestrator.inspect import InspectOrchestrator


def main():

    result = InspectOrchestrator().run()

    incident_id = result.metadata.get("incident_id", "UNKNOWN")

    severity = result.summary.get("severity", {})

    print()
    print("=" * 60)
    print(f" RootIQ Inspection Report")
    print("=" * 60)

    print(f"Incident ID        : {incident_id}")
    print(f"Status             : {result.summary['cluster_status']}")
    print(f"Execution Time     : {result.execution_time:.2f}s")
    print(f"Resources Scanned  : {result.summary['resources_scanned']}")
    print(f"Collectors         : {result.summary['collectors_executed']}")

    print()
    print("Issue Summary")
    print("-------------")
    print(f"Total Issues : {len(result.issues)}")
    print(f"Critical     : {severity.get('CRITICAL',0)}")
    print(f"High         : {severity.get('HIGH',0)}")
    print(f"Medium       : {severity.get('MEDIUM',0)}")
    print(f"Low          : {severity.get('LOW',0)}")
    print(f"Info         : {severity.get('INFO',0)}")

    print()

    if result.issues:

        print("\nTop Issues")
        print("----------")

        for issue in result.issues[:10]:

            severity = issue["severity"]

            if hasattr(severity, "value"):
                severity = severity.value
            print(
                f"[{severity}] "
                f"{issue['id']}  "
                f"{issue['resource']}  "
                f"- {issue['title']}"
            )

        if len(result.issues) > 10:
            print(f"... and {len(result.issues)-10} more issues")

        #print(f"Found {len(result.issues)} issue(s)\n")

        # for issue in result.issues:

        #     print(
        #         f"[{issue['id']}] "
        #         f"{issue['title']} "
        #         f"({issue['severity']})"
        #     )

    else:

        print("✔ No issues found.")

    print()

    print(f"Inspection saved to : incidents/{incident_id}/")
    print("=" * 60)