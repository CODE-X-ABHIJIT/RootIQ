from kubernetes import client

from rootiq.incident.target import ClusterTarget
from rootiq.kubernetes.config import KubeConfigManager
from rootiq.kubernetes.exceptions import (
    KubernetesAuthenticationError,
    KubernetesConnectionError,
)


class KubernetesClient:
    """
    Central Kubernetes client used throughout RootIQ.

    A single instance is created for a target cluster and
    shared across all collectors.
    """

    def __init__(self, target: ClusterTarget):

        self.target = target

        self.config = KubeConfigManager()

        # Kubernetes API Clients
        self.core = None
        self.apps = None
        self.batch = None
        self.networking = None
        self.storage = None
        self.custom = None
        self.version = None
        self.rbac = None

        self._connect()

    # ==================================================
    # Connection
    # ==================================================

    def _connect(self):

        if not self.config.context_exists(
            self.target.context
        ):

            available = "\n".join(
                f"  • {context}"
                for context in self.config.list_contexts()
            )

            raise KubernetesConnectionError(
                f"\nContext '{self.target.context}' was not found.\n\n"
                f"Available contexts:\n"
                f"{available}"
            )

        try:

            self.config.load_context(
                self.target.context
            )

            self.core = client.CoreV1Api()

            self.apps = client.AppsV1Api()

            self.batch = client.BatchV1Api()

            self.networking = (
                client.NetworkingV1Api()
            )

            self.storage = (
                client.StorageV1Api()
            )

            self.custom = (
                client.CustomObjectsApi()
            )

            self.version = (
                client.VersionApi()
            )

            self.rbac = (
                client.RbacAuthorizationV1Api()
            )

        except KubernetesConnectionError:
            raise

        except Exception as e:

            raise KubernetesAuthenticationError(
                str(e)
            )

    # ==================================================
    # Health
    # ==================================================

    def ping(self) -> bool:

        try:

            self.version.get_code()

            return True

        except Exception:

            return False

    # ==================================================
    # Cluster Information
    # ==================================================

    def cluster_version(self) -> str:

        version = self.version.get_code()

        return (
            f"{version.major}.{version.minor}"
        )

    def api_server(self) -> str:

        configuration = (
            client.Configuration.get_default_copy()
        )

        return configuration.host

    def current_context(self) -> str:

        return self.config.current_context()

    def available_contexts(
        self,
    ) -> list[str]:

        return self.config.list_contexts()

    # ==================================================
    # Nodes
    # ==================================================

    def nodes(self):

        return self.core.list_node().items

    # ==================================================
    # Namespaces
    # ==================================================

    def namespaces(self):

        return (
            self.core
            .list_namespace()
            .items
        )

    # ==================================================
    # Pods
    # ==================================================

    def pods(self):

        if self.target.cluster_wide:

            return (
                self.core
                .list_pod_for_all_namespaces()
                .items
            )

        return (
            self.core
            .list_namespaced_pod(
                self.target.namespace
            )
            .items
        )

    # ==================================================
    # Deployments
    # ==================================================

    def deployments(self):

        if self.target.cluster_wide:

            return (
                self.apps
                .list_deployment_for_all_namespaces()
                .items
            )

        return (
            self.apps
            .list_namespaced_deployment(
                self.target.namespace
            )
            .items
        )

    # ==================================================
    # StatefulSets
    # ==================================================

    def statefulsets(self):

        if self.target.cluster_wide:

            return (
                self.apps
                .list_stateful_set_for_all_namespaces()
                .items
            )

        return (
            self.apps
            .list_namespaced_stateful_set(
                self.target.namespace
            )
            .items
        )

    # ==================================================
    # DaemonSets
    # ==================================================

    def daemonsets(self):

        if self.target.cluster_wide:

            return (
                self.apps
                .list_daemon_set_for_all_namespaces()
                .items
            )

        return (
            self.apps
            .list_namespaced_daemon_set(
                self.target.namespace
            )
            .items
        )

    # ==================================================
    # Jobs
    # ==================================================

    def jobs(self):

        if self.target.cluster_wide:

            return (
                self.batch
                .list_job_for_all_namespaces()
                .items
            )

        return (
            self.batch
            .list_namespaced_job(
                self.target.namespace
            )
            .items
        )