from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class DeploymentImageTagRule(BaseRule):

    id = "DEPLOYMENT-005"

    name = "Deployment Image Tag Validation"

    description = (
        "Detect deployments using mutable or missing container image tags."
    )

    resource_type = "deployment"

    severity = "medium"

    category = "deployment"

    def evaluate(self, context: RuleContext):

        mutable_tags = {
            "latest",
            "dev",
            "development",
            "snapshot",
            "test",
            "master",
            "main",
            "edge",
            "nightly",
        }

        for deployment in context.resources:

            deployment_name = deployment["name"]
            namespace = deployment["namespace"]

            for container in deployment.get("containers", []):

                image = container.get("image", "")

                #
                # Image has no explicit tag
                #
                if ":" not in image:

                    context.report(
                        rule_id=self.id,
                        severity="high",
                        title="Container image has no explicit tag",
                        resource=deployment_name,
                        namespace=namespace,
                        description=(
                            f"Container '{container['name']}' uses image "
                            f"'{image}' without an explicit tag."
                        ),
                        recommendation=(
                            "Specify an immutable image tag "
                            "(example: nginx:1.27.2)."
                        ),
                        metadata={
                            "container": container["name"],
                            "image": image,
                        },
                    )

                    continue

                tag = image.rsplit(":", 1)[1].lower()

                #
                # Mutable image tag
                #
                if tag in mutable_tags:

                    context.report(
                        rule_id=self.id,
                        severity="medium",
                        title="Container uses mutable image tag",
                        resource=deployment_name,
                        namespace=namespace,
                        description=(
                            f"Container '{container['name']}' uses the "
                            f"mutable image tag '{tag}'."
                        ),
                        recommendation=(
                            "Use an immutable version tag "
                            "(example: v1.4.2 or 1.27.2) "
                            "to ensure reproducible deployments."
                        ),
                        metadata={
                            "container": container["name"],
                            "image": image,
                            "tag": tag,
                        },
                    )