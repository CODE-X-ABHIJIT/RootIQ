from rootiq.repair.loader import IncidentLoader
from rootiq.repair.rootcause import RootCauseEngine
from rootiq.repair.planner import RepairPlanner
from rootiq.repair.display import RepairPlanDisplay
from rootiq.engine.result import EngineResult
from rootiq.repair.approval import RepairApproval


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

        result.summary = {

            "status":
                "Approval completed",

            "total_actions":
                len(plan),

            "approved_actions":
                len(approved_actions),

            "skipped_actions":
                len(plan) - len(approved_actions)

        }


        return result