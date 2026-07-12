from dataclasses import asdict

from rootiq.orchestrator.inspect import InspectOrchestrator
import json

def main():

    result = InspectOrchestrator().run()

    print(
    json.dumps(
        asdict(result),
        indent=4,
        default=str,
    )
)

if __name__ == "__main__":
    main()