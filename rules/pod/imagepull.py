# rootiq/rules/pod/imagepull.py

from rootiq.rules.base import BaseRule
from rootiq.incident.issue import Issue


class ImagePullRule(BaseRule):

    id = "POD-003"

    name = "Image Pull Failure"

    description = "Detect container image pull failures."

    severity = "critical"

    category = "pod"

    IMAGE_PULL_REASONS = {
        "ImagePullBackOff",
        "ErrImagePull",
        "RegistryUnavailable",
        "InvalidImageName",
        "ErrImageNeverPull",
    }

    def evaluate(self, result):

        for pod in result.resources:

            pod_name = pod["name"]
            namespace = pod["namespace"]

            for container in pod.get("containers", []):

                state = container.get("state", {})
                waiting = state.get("waiting")

                if not waiting:
                    continue

                reason = waiting.get("reason")
                message = waiting.get("message", "")

                if (
                    reason not in self.IMAGE_PULL_REASONS
                    and "pull" not in message.lower()
                    and "manifest" not in message.lower()
                    and "registry" not in message.lower()
                ):
                    continue

                recommendation = (
                    "Verify image name, image tag, registry connectivity "
                    "and imagePullSecrets."
                )

                lower = message.lower()

                #
                # Image not found
                #
                if (
                    "not found" in lower
                    or "manifest unknown" in lower
                ):
                    recommendation = (
                        "Image or tag does not exist. "
                        "Verify repository and tag."
                    )

                #
                # Authentication
                #
                elif (
                    "unauthorized" in lower
                    or "authentication required" in lower
                    or "denied" in lower
                ):
                    recommendation = (
                        "Configure imagePullSecrets or registry credentials."
                    )

                #
                # DNS
                #
                elif (
                    "no such host" in lower
                    or "lookup" in lower
                ):
                    recommendation = (
                        "Check DNS resolution and network connectivity."
                    )

                #
                # Timeout
                #
                elif (
                    "timeout" in lower
                    or "deadline exceeded" in lower
                ):
                    recommendation = (
                        "Registry unreachable. Verify network connectivity."
                    )

                #
                # Rate Limit
                #
                elif (
                    "toomanyrequests" in lower
                    or "rate limit" in lower
                ):
                    recommendation = (
                        "DockerHub rate limit exceeded. "
                        "Authenticate or use another registry."
                    )

                #
                # TLS
                #
                elif (
                    "certificate" in lower
                    or "x509" in lower
                ):
                    recommendation = (
                        "Registry TLS certificate validation failed."
                    )

                result.issues.append(
                    Issue(
                        rule_id=self.id,
                        severity=self.severity,
                        title="Image pull failed",
                        resource=pod_name,
                        namespace=namespace,
                        description=message or reason,
                        recommendation=recommendation,
                        metadata={
                            "container": container["name"],
                            "image": container.get("image"),
                            "reason": reason,
                        },
                    )
                )

        return result