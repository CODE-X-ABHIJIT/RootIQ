class KubernetesConnectionError(Exception):
    """Raised when RootIQ cannot connect to a Kubernetes cluster."""
    pass


class KubernetesAuthenticationError(Exception):
    """Raised when authentication to the Kubernetes cluster fails."""
    pass