from dataclasses import dataclass, field
from dataclasses import asdict
from rootiq.incident.issue import Issue


@dataclass
class RuleContext:
    """
    Shared object passed to every rule.
    """

    resources: list

    issues: list = field(default_factory=list)

    logs: list = field(default_factory=list)

    metadata: dict = field(default_factory=dict)

    # ==================================================
    # Backward Compatibility
    # ==================================================

    @property
    def result(self):
        return self

    # ==================================================
    # Issue Reporting
    # ==================================================

    def report(self, issue=None, **kwargs):
        """
        Supports both styles:

        context.report(Issue(...))

        and

        context.report(
            rule_id="POD-001",
            title="...",
            severity="HIGH",
            ...
        )
        """

        #
        # Style 1:
        # context.report(Issue(...))
        #

        if isinstance(issue, Issue):

            self.issues.append(asdict(issue))
            return

        #
        # Style 2:
        # context.report({...})
        #

        if isinstance(issue, dict):

            self.issues.append(issue)
            return

        #
        # Style 3:
        # context.report(rule_id=..., ...)
        #

        if kwargs:

            self.issues.append(
                asdict(
                    Issue(**kwargs)
                )
            )
            return

        raise TypeError(
            "report() expects an Issue, dict or keyword arguments."
        )
    def add_issue(self, issue):
        self.report(
        issue
        )

    # ==================================================
    # Logging
    # ==================================================

    def log(
        self,
        level: str,
        message: str,
    ):
        self.logs.append(
            {
                "level": level,
                "message": message,
            }
        )

    def add_log(
        self,
        level: str,
        message: str,
    ):
        self.log(level, message)

    # ==================================================
    # Metadata
    # ==================================================

    def set_metadata(
        self,
        key: str,
        value,
    ):
        self.metadata[key] = value