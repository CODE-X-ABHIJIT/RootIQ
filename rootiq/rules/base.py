from abc import ABC, abstractmethod

from rootiq.incident.issue import Issue
from rootiq.incident.severity import Severity


class BaseRule(ABC):

    id = "RULE-000"

    name = "Unnamed Rule"

    resource_type = None

    category = None

    severity = Severity.MEDIUM

    @property
    def resource_type(self):

        return (
            self.category
            if self.category
            else self.__class__.resource_type
        )

    @abstractmethod
    def evaluate(
        self,
        context,
    ):
        """
        Receives RuleContext.
        """
        pass

    def create_issue(
        self,
        resource,
        message,
        severity=None,
    ):

        return Issue(
            id=self.id,
            severity=severity or self.severity,
            message=message,
            resource=resource.get("name"),
            namespace=resource.get("namespace"),
            rule=self.id,
        )