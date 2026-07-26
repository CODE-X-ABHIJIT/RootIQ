from rootiq.orchestrator.repair import RepairOrchestrator


def main():

    result = RepairOrchestrator().run()

    print(result.summary)

    for log in result.logs:
        print(log)



if __name__ == "__main__":
    main()