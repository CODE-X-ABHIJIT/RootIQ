from dataclasses import dataclass, field

from rootiq.incident.issue import Issue


@dataclass
class Incident:

    cluster: str

    issues: list[Issue] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)

    def add(self, issue: Issue):

        self.issues.append(issue)

    @property
    def total(self):

        return len(self.issues)

    @property
    def critical(self):

        return len(
            [
                i
                for i in self.issues
                if i.severity.value == "CRITICAL"
            ]
        )

    @property
    def high(self):

        return len(
            [
                i
                for i in self.issues
                if i.severity.value == "HIGH"
            ]
        )

    @property
    def medium(self):

        return len(
            [
                i
                for i in self.issues
                if i.severity.value == "MEDIUM"
            ]
        )

    @property
    def low(self):

        return len(
            [
                i
                for i in self.issues
                if i.severity.value == "LOW"
            ]
        )