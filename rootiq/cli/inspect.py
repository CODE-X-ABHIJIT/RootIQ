from rootiq.orchestrator.inspect import InspectOrchestrator


def main():

    result = InspectOrchestrator().run()

    print()

    if result.issues:

        print(f"Found {len(result.issues)} issue(s)\n")

        # for issue in result.issues:

        #     print(
        #         f"[{issue['id']}] "
        #         f"{issue['title']} "
        #         f"({issue['severity']})"
        #     )

    else:

        print("✔ No issues found.")

    print()

    print(
        "Inspection:",
        result.metadata["incident_id"],
    )