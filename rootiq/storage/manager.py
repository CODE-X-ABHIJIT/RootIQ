import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path


class StorageManager:

    def __init__(self):

        self.base = Path("incidents")

        self.base.mkdir(
            exist_ok=True,
        )

    # ==========================================================
    # Save Inspection
    # ==========================================================

    def save_inspection(
        self,
        result,
    ):

        incident_id = self._next_id()

        incident_dir = (
            self.base
            / incident_id
        )

        incident_dir.mkdir()

        #
        # inspect.json
        #

        with open(
            incident_dir / "inspect.json",
            "w",
        ) as f:

            json.dump(
                asdict(result),
                f,
                indent=4,
            )

        #
        # logs.json
        #

        with open(
            incident_dir / "logs.json",
            "w",
        ) as f:

            json.dump(
                result.logs,
                f,
                indent=4,
            )

        #
        # summary.txt
        #

        with open(
            incident_dir / "summary.txt",
            "w",
        ) as f:

            f.write(
                self._summary(
                    incident_id,
                    result,
                )
            )

        #
        # latest.json
        #

        with open(
            self.base / "latest.json",
            "w",
        ) as f:

            json.dump(
                {
                    "latest": incident_id,
                    "generated_at": datetime.now().isoformat(),
                },
                f,
                indent=4,
            )

        return incident_id

    # ==========================================================
    # Load Latest
    # ==========================================================

    def load_latest(self):

        latest = self.base / "latest.json"

        if not latest.exists():

            return None

        with open(latest) as f:

            data = json.load(f)

        return data["latest"]

    # ==========================================================
    # Load Inspection
    # ==========================================================

    def load(
        self,
        incident_id,
    ):

        file = (
            self.base
            / incident_id
            / "inspect.json"
        )

        if not file.exists():

            return None

        with open(file) as f:

            return json.load(f)

    # ==========================================================
    # Next Incident ID
    # ==========================================================

    def _next_id(self):

        numbers = []

        for folder in self.base.iterdir():

            if (
                folder.is_dir()
                and folder.name.startswith("INC-")
            ):

                try:

                    numbers.append(
                        int(
                            folder.name.split("-")[1]
                        )
                    )

                except:

                    pass

        next_number = (
            max(numbers, default=0)
            + 1
        )

        return f"INC-{next_number:06d}"

    # ==========================================================
    # Summary Builder
    # ==========================================================

    def _summary(
        self,
        incident_id,
        result,
    ):

        severity = result.summary.get("severity", {})

        return (
            f"Incident : {incident_id}\n"
            f"Engine   : {result.engine}\n"
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            f"Issue Summary\n"
            f"-------------\n"
            f"{len(result.issues)} Total Issues\n"
            f" • Critical : {severity.get('CRITICAL', 0)}\n"
            f" • High     : {severity.get('HIGH', 0)}\n"
            f" • Medium   : {severity.get('MEDIUM', 0)}\n"
            f" • Low      : {severity.get('LOW', 0)}\n"
            f" • Info     : {severity.get('INFO', 0)}\n\n"

            f"Resources Scanned : {result.summary.get('resources_scanned', 0)}\n"
            f"Collectors        : {result.summary.get('collectors_executed', 0)}\n"
            f"Execution Time    : {result.execution_time:.2f}s\n"
            f"Status            : {result.summary.get('cluster_status', 'Unknown')}\n"
        )