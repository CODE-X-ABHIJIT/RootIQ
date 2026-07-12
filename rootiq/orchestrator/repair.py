from rootiq.engine.result import EngineResult


class RepairOrchestrator:

    name = "RepairOrchestrator"

    def run(self, *args, **kwargs):

        result = EngineResult(
            engine=self.name
        )

        result.summary = {
            "status": "Not Implemented"
        }

        result.add_log(
            "info",
            "Repair engine is not implemented yet."
        )

        return result