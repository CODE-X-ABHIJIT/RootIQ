from rootiq.engine.result import EngineResult


class ValidateOrchestrator:

    name = "ValidateOrchestrator"

    def run(self, *args, **kwargs):

        result = EngineResult(
            engine=self.name
        )

        result.summary = {
            "status": "Not Implemented"
        }

        result.add_log(
            "info",
            "Validation engine is not implemented yet."
        )

        return result