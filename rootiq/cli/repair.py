from dataclasses import asdict

from rootiq.orchestrator.repair import RepairOrchestrator
import json

def main():

    result = RepairOrchestrator().run()

    print(
        json.dumps(
            asdict(result),
            indent=4,
            default=str,
        )
    )


if __name__ == "__main__":
    main()