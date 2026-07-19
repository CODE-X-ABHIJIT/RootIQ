# rootiq/rules/pod/image_tag.py

from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule
from rootiq.incident.issue import Issue


class ImageTagRule(BaseRule):

    id = "POD-009"

    name = "Image Tag Validation"

    description = "Detect unsafe or mutable container image tags."

    resource_type = "pod"
    
    severity = "medium"

    category = "pod"

    def evaluate(self, context: RuleContext):

        bad_tags = {
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

        for pod in context.resources:

            pod_name = pod["name"]
            namespace = pod["namespace"]

            for container in pod.get("containers", []):

                image = container.get("image", "")

                #
                # No explicit tag
                #
                if ":" not in image:

                    context.report(
                        
                            rule_id=self.id,
                            severity="high",
                            title="Image tag missing",
                            resource=pod_name,
                            namespace=namespace,
                            description=(
                                f"Container '{container['name']}' "
                                "does not specify an image tag."
                            ),
                            recommendation=(
                                "Always use a versioned image tag."
                            ),
                            metadata={
                                "container": container["name"],
                                "image": image,
                            },
                        )
                

                    continue

                tag = image.rsplit(":", 1)[1].lower()

                #
                # Floating tags
                #
                if tag in bad_tags:

                    context.report(
                        
                            rule_id=self.id,
                            severity=self.severity,
                            title="Mutable image tag detected",
                            resource=pod_name,
                            namespace=namespace,
                            description=(
                                f"Container '{container['name']}' "
                                f"uses mutable tag '{tag}'."
                            ),
                            recommendation=(
                                "Use immutable version tags "
                                "(example: v1.2.3)."
                            ),
                            metadata={
                                "container": container["name"],
                                "image": image,
                                "tag": tag,
                            },
                        )
                

                #
                # Latest
                #
                if tag == "latest":

                    context.report(
                        
                            rule_id=self.id,
                            severity="high",
                            title="Image uses latest tag",
                            resource=pod_name,
                            namespace=namespace,
                            description=(
                                f"Container '{container['name']}' "
                                "uses the 'latest' tag."
                            ),
                            recommendation=(
                                "Avoid 'latest'. Use a fixed version."
                            ),
                            metadata={
                                "container": container["name"],
                                "image": image,
                            },
                        )
                

        