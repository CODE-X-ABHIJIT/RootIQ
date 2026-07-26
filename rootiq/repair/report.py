import json
from datetime import datetime
from pathlib import Path


class RepairReport:

    name = "RepairReport"

    def generate(self, incident_id, execution_results):

        incident_path = Path("incidents") / incident_id

        incident_path.mkdir(
            parents=True,
            exist_ok=True
        )

        report = {

            "incident": incident_id,

            "generated_at":
                datetime.now().isoformat(),

            "total_actions":
                len(execution_results),

            "successful_actions":
                sum(
                    1
                    for result in execution_results
                    if result["success"]
                ),

            "failed_actions":
                sum(
                    1
                    for result in execution_results
                    if not result["success"]
                ),

            "actions":
                execution_results

        }

        report_file = incident_path / "repair.json"

        with open(
            report_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4
            )


        log_file = incident_path / "repair.log"

        with open(
            log_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                f"Repair Report - {incident_id}\n"
            )

            file.write(
                "=" * 60 + "\n\n"
            )


            for index, action in enumerate(execution_results, 1):

                status = (
                    "SUCCESS"
                    if action["success"]
                    else "FAILED"
                )

                file.write(
                    f"[{index}] {status}\n"
                )

                file.write(
                    f"Action : {action['action']}\n"
                )

                file.write(
                    f"Command: {action['command']}\n"
                )

                file.write(
                    f"Time   : {action['execution_time']} sec\n"
                )

                if action["stdout"]:

                    file.write(
                        f"STDOUT : {action['stdout']}\n"
                    )

                if action["stderr"]:

                    file.write(
                        f"STDERR : {action['stderr']}\n"
                    )

                file.write("\n")


        print("\n")
        print("=" * 60)
        print(" Repair Report ")
        print("=" * 60)

        print(
            f"repair.json : {report_file}"
        )

        print(
            f"repair.log  : {log_file}"
        )

        return report