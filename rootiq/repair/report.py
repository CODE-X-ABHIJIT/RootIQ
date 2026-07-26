import json
from pathlib import Path


class RepairReport:


    def generate(
        self,
        incident_id,
        data
    ):

        report_path = (
            Path("incidents")
            / incident_id
            / "repair.json"
        )


        with open(
            report_path,
            "w"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )


        return {

            "status":
                "generated",

            "path":
                str(report_path)

        }