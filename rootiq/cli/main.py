import argparse

from rootiq.cli.inspect import main as inspect_main
from rootiq.cli.repair import main as repair_main
from rootiq.cli.validate import main as validate_main
from rootiq.cli.report import main as report_main


def main():

    parser = argparse.ArgumentParser(
        prog="rootiq",
        description="RootIQ Kubernetes Inspection Framework",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser(
        "inspect",
        help="Inspect Kubernetes cluster",
    )

    subparsers.add_parser(
        "repair",
        help="Repair detected issues",
    )

    subparsers.add_parser(
        "validate",
        help="Validate cluster health",
    )

    subparsers.add_parser(
        "report",
        help="Generate inspection report",
    )

    args = parser.parse_args()

    if args.command == "inspect":
        inspect_main()

    elif args.command == "repair":
        repair_main()

    elif args.command == "validate":
        validate_main()

    elif args.command == "report":
        report_main()


if __name__ == "__main__":
    main()