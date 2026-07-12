from collections import defaultdict


class RuleRegistry:
    """
    Stores rules grouped by resource type.

    Example:

    pod
        POD-001
        POD-002
        ...

    deployment
        DEPLOY-001
        ...

    service
        ...
    """

    def __init__(self):

        self._rules = defaultdict(list)

    # ==========================================
    # Register
    # ==========================================

    def register(
        self,
        resource_type: str,
        rule,
    ):

        self._rules[
            resource_type.lower()
        ].append(rule)

    # ==========================================
    # Get Rules
    # ==========================================

    def get_rules(
        self,
        resource_type: str,
    ):

        return self._rules.get(
            resource_type.lower(),
            [],
        )

    # ==========================================
    # Get Resource Types
    # ==========================================

    def resource_types(self):

        return sorted(
            self._rules.keys()
        )

    # ==========================================
    # Count
    # ==========================================

    def rule_count(self):

        return sum(
            len(v)
            for v in self._rules.values()
        )

    # ==========================================
    # Clear
    # ==========================================

    def clear(self):

        self._rules.clear()

    # ==========================================
    # Iterator
    # ==========================================

    def __iter__(self):

        return iter(
            self._rules.items()
        )


#
# Global Registry
#

registry = RuleRegistry()