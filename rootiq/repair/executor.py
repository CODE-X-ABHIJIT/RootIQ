import shlex
import subprocess
import time


class RepairExecutor:

    name = "RepairExecutor"

    def execute(self, actions):

        results = []

        if not actions:
            return results

        print("\n")
        print("=" * 60)
        print(" Executing Repair Actions ")
        print("=" * 60)

        for index, action in enumerate(actions, 1):

            command = action["command"]

            print(f"\n[{index}/{len(actions)}]")
            print(command)

            start = time.time()

            try:

                process = subprocess.run(
                    shlex.split(command),
                    capture_output=True,
                    text=True
                )

                duration = round(
                    time.time() - start,
                    3
                )

                success = process.returncode == 0

                if success:
                    print("✔ Success")
                else:
                    print("✘ Failed")

                results.append({

                    "action":
                        action["action"],

                    "resource":
                        action["resource"],

                    "command":
                        command,

                    "rollback":
                        action.get("rollback"),

                    "risk":
                        action["risk"],

                    "success":
                        success,

                    "return_code":
                        process.returncode,

                    "stdout":
                        process.stdout.strip(),

                    "stderr":
                        process.stderr.strip(),

                    "execution_time":
                        duration

                })

            except Exception as ex:

                print("✘ Exception")

                results.append({

                    "action":
                        action["action"],

                    "resource":
                        action["resource"],

                    "command":
                        command,

                    "rollback":
                        action.get("rollback"),

                    "risk":
                        action["risk"],

                    "success":
                        False,

                    "return_code":
                        -1,

                    "stdout":
                        "",

                    "stderr":
                        str(ex),

                    "execution_time":
                        0

                })

        return results