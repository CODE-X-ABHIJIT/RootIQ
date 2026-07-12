class CollectorRegistry:
    """
    Stores all available collectors.
    """

    def __init__(self):

        self._collectors = []

    # ==========================================
    # Register
    # ==========================================

    def register(
        self,
        collector,
    ):

        self._collectors.append(
            collector
        )

    # ==========================================
    # Get Collectors
    # ==========================================

    def collectors(self):

        return self._collectors

    # ==========================================
    # Count
    # ==========================================

    def count(self):

        return len(
            self._collectors
        )

    # ==========================================
    # Clear
    # ==========================================

    def clear(self):

        self._collectors.clear()

    def __iter__(self):

        return iter(
            self._collectors
        )


registry = CollectorRegistry()