import importlib
import inspect
import pkgutil

from rootiq.rules import __path__ as rules_path
from rootiq.rules.base import BaseRule
from rootiq.engine.registry import registry


class RuleManager:
    """
    Discovers and registers all available rules.
    """

    def __init__(self):

        self.discover()

    # ==================================================
    # Discover Rules
    # ==================================================

    def discover(self):

        registry.clear()

        for _, package_name, is_pkg in pkgutil.iter_modules(
            rules_path
        ):

            if not is_pkg:
                continue

            package = importlib.import_module(
                f"rootiq.rules.{package_name}"
            )

            for _, module_name, _ in pkgutil.iter_modules(
                package.__path__
            ):

                module = importlib.import_module(
                    f"rootiq.rules.{package_name}.{module_name}"
                )

                for _, obj in inspect.getmembers(
                    module,
                    inspect.isclass,
                ):

                    if not issubclass(obj, BaseRule):
                        continue

                    if obj is BaseRule:
                        continue

                    if inspect.isabstract(obj):
                        continue

                    rule = obj()

                    resource_type = (
                        getattr(rule, "resource_type", None)
                        or getattr(rule, "category", None)
                    )

                    if resource_type is None:
                        print(
                            f"Skipping {rule.__class__.__name__}: "
                            "resource_type/category not defined."
                        )
                        continue

                    registry.register(
                        resource_type,
                        rule,
                    )