from kubernetes import config
from kubernetes.config.kube_config import (
    list_kube_config_contexts,
)
from kubernetes.config.config_exception import (
    ConfigException,
)

from rootiq.kubernetes.exceptions import (
    KubernetesConnectionError,
)


class KubeConfigManager:
    """
    Handles all kubeconfig-related operations.

    Responsibilities:
        - Discover available contexts
        - Get current context
        - Validate contexts
        - Load kubeconfig
        - Discover clusters and users
    """

    def __init__(self):

        self._contexts = None
        self._current = None

        self.refresh()

    # ==================================================
    # Internal
    # ==================================================

    def refresh(self):

        try:

            contexts, current = (
                list_kube_config_contexts()
            )

            self._contexts = contexts or []
            self._current = current

        except ConfigException as e:

            raise KubernetesConnectionError(
                str(e)
            )

    # ==================================================
    # Contexts
    # ==================================================

    def list_contexts(self) -> list[str]:

        return [
            context["name"]
            for context in self._contexts
        ]

    def current_context(self) -> str | None:

        if self._current:

            return self._current["name"]

        return None

    def context_exists(
        self,
        context_name: str,
    ) -> bool:

        return context_name in self.list_contexts()

    # ==================================================
    # Clusters
    # ==================================================

    def cluster_names(self) -> list[str]:

        return list(
            {
                context["context"]["cluster"]
                for context in self._contexts
            }
        )

    # ==================================================
    # Users
    # ==================================================

    def users(self) -> list[str]:

        return list(
            {
                context["context"]["user"]
                for context in self._contexts
            }
        )

    # ==================================================
    # Namespace
    # ==================================================

    def namespace(
        self,
        context_name: str,
    ) -> str | None:

        for context in self._contexts:

            if context["name"] == context_name:

                return (
                    context["context"]
                    .get(
                        "namespace",
                        "default",
                    )
                )

        return None

    # ==================================================
    # Load
    # ==================================================

    def load_context(
        self,
        context_name: str,
    ):

        if not self.context_exists(
            context_name
        ):

            available = ", ".join(
                self.list_contexts()
            )

            raise KubernetesConnectionError(
                f"Context '{context_name}' not found.\n"
                f"Available contexts: {available}"
            )

        try:

            config.load_kube_config(
                context=context_name
            )

        except ConfigException as e:

            raise KubernetesConnectionError(
                str(e)
            )