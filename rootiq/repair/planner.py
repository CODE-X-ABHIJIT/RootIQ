class RepairPlanner:


    def create_plan(self, root_causes):

        actions = []


        for cause in root_causes:


            for resource in cause["resources"]:


                if cause["category"] == "IMAGE":


                    actions.append({

                        "action":
                            "Update container image",


                        "resource": {

                            "kind":
                                "Deployment",

                            "name":
                                resource.get("resource"),

                            "namespace":
                                resource.get("namespace")

                        },


                        "container":
                            resource.get("container"),


                        "current_image":
                            resource.get("image"),


                        "reason":
                            (
                                "Container image does not "
                                "use an explicit immutable tag"
                            ),


                        "command":
                            (
                                "kubectl set image deployment/"
                                f"{resource.get('resource')} "
                                f"{resource.get('container')}=<new-image> "
                                f"-n {resource.get('namespace')}"
                            ),


                        "rollback":
                            (
                                "kubectl rollout undo deployment/"
                                f"{resource.get('resource')} "
                                f"-n {resource.get('namespace')}"
                            ),


                        "risk":
                            "LOW"

                    })



                elif cause["category"] == "RESOURCE":


                    actions.append({

                        "action":
                            "Apply resource limits",


                        "resource": {

                            "kind":
                                "Deployment",

                            "name":
                                resource.get("resource"),

                            "namespace":
                                resource.get("namespace")

                        },


                        "container":
                            resource.get("container"),


                        "reason":
                            (
                                "Container has missing "
                                "CPU or memory configuration"
                            ),


                        "command":
                            (
                                "kubectl patch deployment "
                                f"{resource.get('resource')} "
                                "--patch-file resources.yaml "
                                f"-n {resource.get('namespace')}"
                            ),


                        "rollback":
                            (
                                "kubectl rollout undo deployment/"
                                f"{resource.get('resource')} "
                                f"-n {resource.get('namespace')}"
                            ),


                        "risk":
                            "MEDIUM"

                    })



                elif cause["category"] == "POD_HEALTH":


                    actions.append({

                        "action":
                            "Restart workload",


                        "resource": {

                            "kind":
                                "Deployment",

                            "name":
                                resource.get("resource"),

                            "namespace":
                                resource.get("namespace")

                        },


                        "reason":
                            (
                                "Application shows "
                                "restart or crash behaviour"
                            ),


                        "command":
                            (
                                "kubectl rollout restart deployment "
                                f"{resource.get('resource')} "
                                f"-n {resource.get('namespace')}"
                            ),


                        "rollback":
                            (
                                "kubectl rollout undo deployment/"
                                f"{resource.get('resource')} "
                                f"-n {resource.get('namespace')}"
                            ),


                        "risk":
                            "LOW"

                    })


        return actions