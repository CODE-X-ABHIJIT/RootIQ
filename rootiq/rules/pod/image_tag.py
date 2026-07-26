# rootiq/rules/pod/image_tag.py

from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class ImageTagRule(BaseRule):

    id = "POD-009"

    name = "Image Tag Validation"

    description = "Detect mutable or unversioned container image tags."

    resource_type = "pod"

    severity = "medium"

    category = "pod"

    SYSTEM_NAMESPACES = {
        "kube-system",
        "kube-public",
        "kube-node-lease",
    }

    MUTABLE_TAGS = {
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

    def evaluate(self, context: RuleContext):

        for pod in context.resources:

            namespace = pod["namespace"]

            #
            # Ignore Kubernetes system components
            #
            if namespace in self.SYSTEM_NAMESPACES:
                continue

            pod_name = pod["name"]

            for container in pod.get("containers", []):

                image = container.get("image", "")
                container_name = container["name"]

                #
                # No explicit tag -> Docker assumes :latest
                #
                if ":" not in image:

                    context.report(
                        rule_id=self.id,
                        severity="high",
                        title="Image uses implicit latest tag",
                        resource=pod_name,
                        namespace=namespace,
                        description=(
                            f"Container '{container_name}' does not specify "
                            "an image tag. Docker defaults this to 'latest'."
                        ),
                        recommendation=(
                            "Specify an immutable image version "
                            "(example: nginx:1.29.1)."
                        ),
                        metadata={
                            "container": container_name,
                            "image": image,
                            "tag": "latest",
                        },
                    )

                    continue

                tag = image.rsplit(":", 1)[1].lower()

                #
                # Explicit latest
                #
                if tag == "latest":

                    context.report(
                        rule_id=self.id,
                        severity="high",
                        title="Image uses latest tag",
                        resource=pod_name,
                        namespace=namespace,
                        description=(
                            f"Container '{container_name}' uses the mutable "
                            "'latest' tag."
                        ),
                        recommendation=(
                            "Use a fixed image version instead of 'latest'."
                        ),
                        metadata={
                            "container": container_name,
                            "image": image,
                            "tag": tag,
                        },
                    )

                    continue

                #
                # Other mutable tags
                #
                if tag in self.MUTABLE_TAGS:

                    context.report(
                        rule_id=self.id,
                        severity="medium",
                        title="Mutable image tag detected",
                        resource=pod_name,
                        namespace=namespace,
                        description=(
                            f"Container '{container_name}' uses mutable tag "
                            f"'{tag}'."
                        ),
                        recommendation=(
                            "Use an immutable version tag "
                            "(example: v1.2.3)."
                        ),
                        metadata={
                            "container": container_name,
                            "image": image,
                            "tag": tag,
                        },
                    )