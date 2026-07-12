from abc import ABC, abstractmethod
from time import perf_counter

from rootiq.collectors.result import CollectResult
from rootiq.collectors.exceptions import (
    CollectorExecutionError,
)


class BaseCollector(ABC):
    """
    Base class for every RootIQ collector.
    """
    enabled = False
    name = "BaseCollector"
    resource_type = None

    def run(self, k8s):

        start = perf_counter()

        try:

            result = self.collect(k8s)

            result.execution_time = (
                perf_counter() - start
            )

            return result

        except Exception as e:

            result = CollectResult(
                collector=self.name,
                success=False,
                error=str(e),
            )

            result.execution_time = (
                perf_counter() - start
            )

            return result

    @abstractmethod
    def collect(self, k8s):

        """
        Every collector must implement this.
        """

        raise NotImplementedError
