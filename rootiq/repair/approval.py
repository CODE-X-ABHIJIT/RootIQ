class RepairApproval:


    name = "RepairApproval"


    def request(self, actions):

        approved_actions = []


        if not actions:

            print("\nNo repair actions available.")

            return approved_actions


        print("\n")
        print("=" * 60)
        print(" Repair Approval ")
        print("=" * 60)


        for index, action in enumerate(actions, 1):


            resource = action.get(
                "resource",
                {}
            )


            print("\n")
            print(f"[{index}]")

            print("Action:")
            print(action.get("action"))


            print()
            print("Target:")
            print(
                f"{resource.get('kind')}/"
                f"{resource.get('namespace')}/"
                f"{resource.get('name')}"
            )


            if action.get("container"):

                print()
                print("Container:")
                print(action.get("container"))


            print()
            print("Risk:")
            print(action.get("risk"))


            print()
            print("Command:")
            print(action.get("command"))


            print()
            print("[Y] Execute")
            print("[E] Edit command")
            print("[N] Skip")


            while True:

                choice = input(
                    "\nChoice: "
                ).strip().lower()


                if choice in [
                    "",
                    "y",
                    "yes"
                ]:

                    action["edited"] = False

                    approved_actions.append(
                        action
                    )

                    break


                elif choice in [
                    "e",
                    "edit"
                ]:

                    print("\nCurrent Command:")
                    print(action["command"])

                    edited_command = input(
                        "\nNew Command: "
                    ).strip()


                    if edited_command:

                        action["command"] = edited_command


                    action["edited"] = True

                    approved_actions.append(
                        action
                    )

                    break


                elif choice in [
                    "n",
                    "no"
                ]:

                    break


                else:

                    print(
                        "Please choose Y, E or N."
                    )


        print("\n")
        print("=" * 60)
        print(" Approval Summary ")
        print("=" * 60)

        print(
            "Total Actions:",
            len(actions)
        )

        print(
            "Approved:",
            len(approved_actions)
        )

        print(
            "Skipped:",
            len(actions) - len(approved_actions)
        )


        return approved_actions