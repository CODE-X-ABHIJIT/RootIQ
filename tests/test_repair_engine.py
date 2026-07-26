from rootiq.repair.loader import IncidentLoader
from rootiq.repair.analyzer import RepairAnalyzer
from rootiq.repair.planner import RepairPlanner


def main():

    print("\nLoading incident...\n")

    incident = IncidentLoader().load_latest()


    print(
        "Incident:",
        incident["incident_id"]
    )


    print(
        "\nIssues Found:",
        len(incident["issues"])
    )


    print("\nAnalyzing root causes...\n")


    causes = RepairAnalyzer().analyze(
        incident
    )


    for cause in causes:

        print("=" * 50)

        print(
            "Root Cause:",
            cause["name"]
        )

        print(
            "Category:",
            cause["category"]
        )

        print(
            "Resources:"
        )


        for resource in cause["resources"]:

            print(
                resource
            )



    print("\nGenerating repair plan...\n")


    plan = RepairPlanner().create_plan(
        causes
    )


    for index, action in enumerate(
        plan,
        1
    ):

        print("=" * 50)

        print(
            "Action:",
            action["action"]
        )

        print(
            "Resource:",
            action["resource"]
        )

        print(
            "Command:",
            action["command"]
        )

        print(
            "Risk:",
            action["risk"]
        )



if __name__ == "__main__":
    main()