from dataclasses import asdict

from rootiq.orchestrator.validate import ValidateOrchestrator
import json

def main():

    result = ValidateOrchestrator().run()

    print(
        json.dumps(
            asdict(result),
            indent=4,
            default=str,
        )
    )


if __name__ == "__main__":
    main()