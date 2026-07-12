from abc import ABC, abstractmethod


class BaseRule(ABC):

    id = "RULE000"

    name = "BaseRule"

    @abstractmethod
    def check(self, resource):

        """
        Return:

            None

        or

            Issue
        """

        pass