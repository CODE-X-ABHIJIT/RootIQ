from dataclasses import dataclass, field


@dataclass
class RuleContext:
    """
    Shared object passed to every rule.
    """

    resources: list

    issues: list = field(default_factory=list)

    logs: list = field(default_factory=list)

    metadata: dict = field(default_factory=dict)

    @property
    def result(self):
        """
        Backward compatibility.

        Older rules expect:
            result.resources
            result.issues

        Returning self satisfies both.
        """
        return self