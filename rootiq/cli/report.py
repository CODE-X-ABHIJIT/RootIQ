from dataclasses import asdict

from rootiq.orchestrator.report import ReportOrchestrator
import json

def main():

    result = ReportOrchestrator().run()

    print(
        json.dumps(
            asdict(result),
            indent=4,
            default=str,
        )
    )


if __name__ == "__main__":
    main()