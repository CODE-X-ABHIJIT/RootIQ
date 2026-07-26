class RepairPlanDisplay:


    def show(self, actions):

        print("\n")
        print("=" * 60)
        print(" Repair Plan ")
        print("=" * 60)


        for index, action in enumerate(actions, 1):

            resource = action["resource"]


            print("\n")
            print(f"[{index}]")
            print()


            print("Action:")
            print(action["action"])


            print()


            print("Target:")

            print(
                f"{resource['kind']}/"
                f"{resource['namespace']}/"
                f"{resource['name']}"
            )


            if "container" in action:

                print()

                print("Container:")
                print(action["container"])



            if "current_image" in action:

                print()

                print("Current Image:")
                print(action["current_image"])



            print()

            print("Reason:")
            print(action["reason"])


            print()

            print("Command:")
            print(action["command"])


            print()

            print("Rollback:")
            print(action["rollback"])


            print()

            print("Risk:")
            print(action["risk"])


            print("-" * 60)