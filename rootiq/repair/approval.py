from prompt_toolkit import prompt


class RepairApproval:
    name = "RepairApproval"

    @staticmethod
    def _is_executable(command):
        if not isinstance(command, str) or not command.strip():
            return False

        invalid_values = [
            "<new-image>",
            "None",
            "resources.yaml",
        ]

        return not any(
            value in command for value in invalid_values
        )

    def request(self, actions):
        approved_actions = []
        blocked_count = 0
        skipped_count = 0

        print("\n" + "=" * 60)
        print(" Repair Approval ")
        print("=" * 60)

        for index, action in enumerate(actions, 1):
            resource = action.get("resource") or {}
            command = action.get("command")

            print(f"\n[{index}]")
            print("Action:", action.get("action"))
            print(
                "Target:",
                f"{resource.get('kind', 'Unknown')}/"
                f"{resource.get('namespace', 'default')}/"
                f"{resource.get('name', 'Unknown')}",
            )
            print("Reason:", action.get("reason"))
            print("Risk:", action.get("risk"))
            print("Command:", command)

            if (
                action.get("status") == "BLOCKED"
                or not self._is_executable(command)
            ):
                print("Status: BLOCKED — cannot execute")
                blocked_count += 1
                continue

            while True:
                choice = input(
                    "\n[Y] Execute  [E] Edit command  [N] Skip\n"
                    "Choice: "
                ).strip().lower()

                if choice in {"y", "yes"}:
                    if not self._is_executable(action.get("command")):
                        print(
                            "Command is incomplete. Edit it first "
                            "or skip this action."
                        )
                        continue

                    action["edited"] = False
                    approved_actions.append(action)
                    break

                elif choice in {"e", "edit"}:
                    edited_command = prompt(
                        "New Command: ",
                        default=action.get("command") or "",
                    ).strip()

                    if not self._is_executable(edited_command):
                        print(
                            "Command is still incomplete. "
                            "Please enter a complete command."
                        )
                        continue

                    action["command"] = edited_command
                    action["edited"] = True
                    approved_actions.append(action)
                    break

                elif choice in {"n", "no", ""}:
                    skipped_count += 1
                    break

                else:
                    print("Please choose Y, E or N.")

        print("\n" + "=" * 60)
        print(" Approval Summary ")
        print("=" * 60)
        print("Total Actions:", len(actions))
        print("Approved:", len(approved_actions))
        print("Skipped:", skipped_count)
        print("Blocked:", blocked_count)

        return approved_actions
