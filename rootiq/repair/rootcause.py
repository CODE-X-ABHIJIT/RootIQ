from collections import defaultdict


class RootCauseEngine:

    name = "RootCauseEngine"


    def analyze(self, issues):

        grouped = defaultdict(list)


        for issue in issues:

            category = self.detect_category(issue)

            grouped[category].append(issue)



        root_causes = []


        for category, items in grouped.items():

            if category == "IMAGE":

                root_causes.append(
                    self.build_image_rootcause(items)
                )


            elif category == "RESOURCE":

                root_causes.append(
                    self.build_resource_rootcause(items)
                )


            elif category == "POD_HEALTH":

                root_causes.append(
                    self.build_restart_rootcause(items)
                )


        return root_causes



    def detect_category(self, issue):

        issue_id = issue.get(
            "id",
            ""
        )


        title = issue.get(
            "title",
            ""
        ).lower()


        if (
            "image" in title
            or issue_id in [
                "DEPLOYMENT-005",
                "POD-009"
            ]
        ):
            return "IMAGE"



        if (
            "resource" in title
            or "cpu" in title
            or "memory" in title
            or issue_id == "DEPLOYMENT-006"
        ):
            return "RESOURCE"



        if (
            "restart" in title
            or "crash" in title
        ):
            return "POD_HEALTH"



        return "UNKNOWN"



    def build_image_rootcause(self, issues):

        resources = []
        evidence = []

        seen = set()


        for issue in issues:

            issue_id = issue.get("id")

            labels = issue.get(
                "labels",
                {}
            )


            container = labels.get(
                "container"
            )


            image = labels.get(
                "image"
            )


            namespace = issue.get(
                "namespace"
            )


            resource = issue.get(
                "resource"
            )


            # Deployment issue = actual repair target
            if issue_id == "DEPLOYMENT-005":


                key = (
                    resource,
                    namespace,
                    container
                )


                if key not in seen:

                    resources.append({

                        "resource":
                            resource,


                        "namespace":
                            namespace,


                        "container":
                            container,


                        "image":
                            image,


                        "issue_id":
                            issue_id

                    })


                    seen.add(key)



            # Pod issue = evidence only
            elif issue_id == "POD-009":

                evidence.append({

                    "pod":
                        resource,


                    "namespace":
                        namespace,


                    "container":
                        container,


                    "image":
                        image

                })



        return {

            "name":
                "Mutable or unversioned container images",


            "category":
                "IMAGE",


            "severity":
                "HIGH",


            "resources":
                resources,


            "evidence":
                evidence,


            "repair":
                "Update container image tag"

        }



    def build_resource_rootcause(self, issues):

        resources=[]


        for issue in issues:

            resources.append({

                "resource":
                    issue.get("resource"),


                "namespace":
                    issue.get("namespace"),


                "container":
                    issue.get("labels", {})
                    .get("container")

            })


        return {

            "name":
                "Missing resource configuration",


            "category":
                "RESOURCE",


            "severity":
                "MEDIUM",


            "resources":
                resources,


            "repair":
                "Apply CPU and memory requests/limits"

        }



    def build_restart_rootcause(self, issues):

        resources=[]


        for issue in issues:

            resources.append({

                "resource":
                    issue.get("resource"),


                "namespace":
                    issue.get("namespace")

            })


        return {

            "name":
                "Application instability",


            "category":
                "POD_HEALTH",


            "severity":
                "HIGH",


            "resources":
                resources,


            "repair":
                "Restart workload"

        }