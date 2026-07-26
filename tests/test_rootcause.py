from rootiq.repair.rootcause import RootCauseEngine


def main():

    issues = [

        {
            "id": "DEPLOYMENT-005",
            "resource": "deployment/java-app",
            "message": "Image uses latest tag"
        },

        {
            "id": "POD-009",
            "resource": "pod/java-app",
            "message": "Mutable image tag"
        },

        {
            "id": "POD-010",
            "resource": "pod/nginx",
            "message": "Missing CPU memory limits"
        },

        {
            "id": "POD-001",
            "resource": "pod/mysql",
            "message": "CrashLoopBackOff restart count high"
        }

    ]


    engine = RootCauseEngine()

    result = engine.analyze(
        issues
    )


    for item in result:

        print("\nROOT CAUSE")
        print(item["name"])

        print("Issues:")

        for issue in item["issues"]:
            print(
                "-",
                issue["id"]
            )


if __name__ == "__main__":
    main()