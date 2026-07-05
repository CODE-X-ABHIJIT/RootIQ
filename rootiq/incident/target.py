from dataclasses import dataclass, field


@dataclass
class ClusterTarget:
    """
    Represents the Kubernetes target against which
    RootIQ performs inspection, diagnosis, repair,
    validation and reporting.
    """

    # --------------------------------------------------
    # Cluster Identity
    # --------------------------------------------------

    name: str
    context: str

    # --------------------------------------------------
    # Scope
    # --------------------------------------------------

    namespace: str = "default"
    cluster_wide: bool = False

    # --------------------------------------------------
    # Kubernetes Information
    # --------------------------------------------------

    api_server: str = ""
    user: str = ""

    kubernetes_version: str = ""
    platform: str = ""

    # --------------------------------------------------
    # Optional Metadata
    # --------------------------------------------------

    environment: str = ""
    region: str = ""
    provider: str = ""

    labels: dict[str, str] = field(default_factory=dict)

    # ==================================================
    # Helper Methods
    # ==================================================

    def is_cluster_scope(self) -> bool:
        return self.cluster_wide

    def is_namespace_scope(self) -> bool:
        return not self.cluster_wide

    def set_namespace(self, namespace: str):
        self.namespace = namespace

    def enable_cluster_scope(self):
        self.cluster_wide = True

    def disable_cluster_scope(self):
        self.cluster_wide = False

    def add_label(self, key: str, value: str):
        self.labels[key] = value

    @property
    def scope(self) -> str:
        return "Cluster" if self.cluster_wide else f"Namespace ({self.namespace})"

    @property
    def display_name(self) -> str:
        return f"{self.name} [{self.context}]"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "context": self.context,
            "namespace": self.namespace,
            "cluster_wide": self.cluster_wide,
            "api_server": self.api_server,
            "user": self.user,
            "kubernetes_version": self.kubernetes_version,
            "platform": self.platform,
            "environment": self.environment,
            "region": self.region,
            "provider": self.provider,
            "labels": self.labels,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)