import importlib
import inspect
import pkgutil

from rootiq.collectors import __path__ as collectors_path
from rootiq.collectors.base import BaseCollector


class CollectorManager:
    """
    Discovers and loads all available collectors.
    """

    def __init__(self):

        self._collectors = []

        self.discover()

    # ==================================================
    # Discover Collectors
    # ==================================================

    def discover(self):

        self._collectors.clear()

        for _, module_name, _ in pkgutil.iter_modules(
            collectors_path
        ):

            if module_name in (
                "base",
                "manager",
                "result",
                "__init__",
                "exceptions",
                "registry",
            ):
                continue

            module = importlib.import_module(
                f"rootiq.collectors.{module_name}"
            )

            for _, obj in inspect.getmembers(
                module,
                inspect.isclass,
            ):

                #
                # Must inherit BaseCollector
                #

                if not issubclass(
                    obj,
                    BaseCollector,
                ):
                    continue

                #
                # Skip BaseCollector itself
                #

                if obj is BaseCollector:
                    continue

                #
                # Skip abstract collectors
                #

                if inspect.isabstract(obj):
                    continue

                #
                # Only load enabled collectors
                #

                if not getattr(
                    obj,
                    "enabled",
                    False,
                ):
                    continue

                #
                # Register collector
                #

                self._collectors.append(
                    obj()
                )

    # ==================================================
    # Get Collectors
    # ==================================================

    def all(self):

        return self._collectors

    def count(self):

        return len(
            self._collectors
        )