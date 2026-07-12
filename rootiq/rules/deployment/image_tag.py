from rootiq.rules.base import BaseRule
from rootiq.rules.result import RuleResult
from rootiq.rules.issue import Issue


class DeploymentImageTagRule(BaseRule):

    id = "DEPLOYMENT-005"

    name = "DeploymentImageTag"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for deployment in resources:

            namespace = deployment.get("namespace")
            deployment_name = deployment.get("name")

            for container in deployment.get("containers", []):

                image = container.get("image", "")

                #
                # No tag specified
                #

                if ":" not in image:

                    result.issues.append(
                        Issue(
                            id=self.id,
                            severity="Medium",
                            resource_type="Deployment",
                            resource_name=deployment_name,
                            namespace=namespace,
                            title="Container image has no explicit tag",
                            description=(
                                f"Container '{container.get('name')}' uses image '{image}' without a tag."
                            ),
                            evidence={
                                "container": container.get("name"),
                                "image": image,
                            },
                            recommendation=(
                                "Specify an immutable image tag instead of relying on the registry default."
                            ),
                        )
                    )

                    continue

                tag = image.rsplit(":", 1)[1]

                #
                # latest tag
                #

                if tag.lower() == "latest":

                    result.issues.append(
                        Issue(
                            id=self.id,
                            severity="Medium",
                            resource_type="Deployment",
                            resource_name=deployment_name,
                            namespace=namespace,
                            title="Container uses latest image tag",
                            description=(
                                f"Container '{container.get('name')}' uses the 'latest' tag."
                            ),
                            evidence={
                                "container": container.get("name"),
                                "image": image,
                                "tag": tag,
                            },
                            recommendation=(
                                "Use a fixed version tag (for example v1.4.2) to ensure reproducible deployments."
                            ),
                        )
                    )

        return result