from dataclasses import dataclass, field, asdict

from rootiq.config.config_loader import RootIQConfig
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

    config: RootIQConfig = field(default_factory=RootIQConfig)

    # ==================================================
    # Backward Compatibility
    # ==================================================

    @property
    def result(self):
        return self

    # ==================================================
    # Exclusion Helpers
    # ==================================================

    def is_excluded(
        self,
        namespace: str,
        resource_name: str,
    ) -> bool:

        scan = self.config.scan

        #
        # Scan everything
        #
        if scan.get("include_system", False):
            return False

        #
        # Namespace exclusion
        #
        if namespace in scan.get(
            "exclude_namespaces",
            [],
        ):
            return True

        #
        # Workload exclusion
        #
        for workload in scan.get(
            "exclude_workloads",
            [],
        ):

            if resource_name.startswith(workload):
                return True

        return False

    # ==================================================
    # Severity Handling
    # ==================================================

    def severity_for(
        self,
        namespace: str,
        resource_name: str,
        severity: str,
    ) -> str:

        if not self.is_excluded(
            namespace,
            resource_name,
        ):
            return severity

        return "info"

    # ==================================================
    # Issue Reporting
    # ==================================================

    def report(self, issue=None, **kwargs):
        """
        Supports:

            context.report(Issue(...))

            context.report({...})

            context.report(
                rule_id="POD-001",
                ...
            )
        """

        #
        # Style 1
        #

        if isinstance(issue, Issue):

            if self.is_excluded(
                issue.namespace,
                issue.resource,
            ):
                return

            self.issues.append(
                asdict(issue)
            )
            return

        #
        # Style 2
        #

        if isinstance(issue, dict):

            if self.is_excluded(
                issue.get("namespace", ""),
                issue.get("resource", ""),
            ):
                return

            self.issues.append(issue)
            return

        #
        # Style 3
        #

        if kwargs:

            if self.is_excluded(
                kwargs.get("namespace"),
                kwargs.get("resource"),
            ):
                return

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
        self.report(issue)

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