
from rootiq.engine.validation_engine import ValidationEngine


class ValidateOrchestrator:
    """Coordinates read-only Kubernetes validation."""

    name = "ValidateOrchestrator"

    def __init__(self):
        self.engine = ValidationEngine()

    def run(
        self,
        context="kind-finops-lab",
        namespace="default",
        cluster_wide=True,
    ):
        result = self.engine.run(
            context=context,
            namespace=namespace,
            cluster_wide=cluster_wide,
        )

        # Keep the orchestrator name in the CLI response.
        result.engine = self.name
        return result