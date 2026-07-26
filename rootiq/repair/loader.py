import json
from pathlib import Path


class IncidentLoader:

    name = "IncidentLoader"


    def __init__(self, incident_dir="incidents"):

        self.incident_dir = Path(
            incident_dir
        )


    def load_latest(self):

        latest_file = (
            self.incident_dir /
            "latest.json"
        )


        if not latest_file.exists():

            raise FileNotFoundError(
                "latest.json not found"
            )


        with open(
            latest_file,
            "r"
        ) as file:

            latest = json.load(file)



        incident_id = latest.get(
            "latest"
        )


        if not incident_id:

            raise ValueError(
                "Latest incident id missing"
            )



        inspect_file = (
            self.incident_dir /
            incident_id /
            "inspect.json"
        )


        if not inspect_file.exists():

            raise FileNotFoundError(
                f"Inspect file missing: {inspect_file}"
            )



        with open(
            inspect_file,
            "r"
        ) as file:

            inspect_data = json.load(file)



        return {

            "incident_id":
                incident_id,


            "inspect_path":
                str(inspect_file),


            "issues":
                inspect_data.get(
                    "issues",
                    []
                )
        }