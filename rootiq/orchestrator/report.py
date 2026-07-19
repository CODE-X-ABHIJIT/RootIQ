from rootiq.engine.result import EngineResult


class ReportOrchestrator:

    name = "ReportOrchestrator"

    def run(self, *args, **kwargs):

        result = EngineResult(
            engine=self.name
        )

        result.summary = {
            "status": "Not Implemented"
        }

        result.add_log(
            "info",
            "Report engine is not implemented yet."
        )

        