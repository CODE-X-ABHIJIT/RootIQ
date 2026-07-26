from rootiq.orchestrator.repair import RepairOrchestrator


def repair_command():

    RepairOrchestrator().run()


if __name__ == "__main__":

    repair_command()