from dataclasses import dataclass, field
from typing import Any


@dataclass
class EngineResult:
    """
    Shared result object produced by all RootIQ engines.

    Rule Engine
    Incident Engine
    RCA Engine
    Fix Engine
    Validation Engine
    """

    #
    # Engine Information
    #

    engine: str

    success: bool = True

    execution_time: float = 0.0

    #
    # Data
    #

    issues: list[Any] = field(default_factory=list)

    incidents: list[Any] = field(default_factory=list)

    actions: list[Any] = field(default_factory=list)

    recommendations: list[Any] = field(default_factory=list)

    summary: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)

    logs: list[dict[str, Any]] = field(default_factory=list)

    #
    # Error
    #

    error: str | None = None

    #
    # Helpers
    #

    @property
    def issue_count(self) -> int:

        return len(self.issues)

    @property
    def incident_count(self) -> int:

        return len(self.incidents)

    @property
    def action_count(self) -> int:

        return len(self.actions)

    def add_issue(self, issue):

        self.issues.append(issue)

    def add_incident(self, incident):

        self.incidents.append(incident)

    def add_action(self, action):

        self.actions.append(action)

    def add_log(
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

    def set_summary(
        self,
        **kwargs,
    ):

        self.summary.update(kwargs)