from rootiq.engine.result import EngineResult

from rootiq.repair.loader import IncidentLoader
from rootiq.repair.rootcause import RootCauseEngine
from rootiq.repair.planner import RepairPlanner
from rootiq.repair.display import RepairPlanDisplay
from rootiq.repair.approval import RepairApproval
from rootiq.repair.executor import RepairExecutor
from rootiq.repair.report import RepairReport


class RepairOrchestrator:

    name = "RepairOrchestrator"

    def run(self, *args, **kwargs):

        result = EngineResult(
            engine=self.name
        )

        print("\nLoading latest inspection...\n")

        incident = IncidentLoader().load_latest()

        print(
            "Incident:",
            incident["incident_id"]
        )

        print(
            "\nAnalyzing issues...\n"
        )

        causes = RootCauseEngine().analyze(
            incident["issues"]
        )

        print(
            "Finding root causes...\n"
        )

        for cause in causes:

            print(
                "✔",
                cause["name"]
            )

        print(
            "\nPreparing repair plan..."
        )

        plan = RepairPlanner().create_plan(
            causes
        )

        RepairPlanDisplay().show(
            plan
        )

        approved_actions = RepairApproval().request(
            plan
        )

        if not approved_actions:

            print("\nNo repair actions approved.")

            result.summary = {

                "status":
                    "Cancelled",

                "total_actions":
                    len(plan),

                "approved_actions":
                    0,

                "executed_actions":
                    0

            }

            return result


        execution_results = RepairExecutor().execute(
            approved_actions
        )


        RepairReport().generate(

            incident_id=incident["incident_id"],

            execution_results=execution_results

        )


        successful = sum(
            1
            for item in execution_results
            if item["success"]
        )


        failed = len(execution_results) - successful


        print("\n")
        print("=" * 60)
        print(" Repair Summary ")
        print("=" * 60)

        print(
            "Approved :",
            len(approved_actions)
        )

        print(
            "Executed :",
            len(execution_results)
        )

        print(
            "Succeeded:",
            successful
        )

        print(
            "Failed   :",
            failed
        )


        result.summary = {

            "status":
                "Completed",

            "incident":
                incident["incident_id"],

            "approved_actions":
                len(approved_actions),

            "executed_actions":
                len(execution_results),

            "successful_actions":
                successful,

            "failed_actions":
                failed

        }

        return result