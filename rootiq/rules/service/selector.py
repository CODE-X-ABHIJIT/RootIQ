from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class ServiceSelectorRule(BaseRule):

    id = "SERVICE-001"

    name = "ServiceSelector"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for service in resources:

            namespace = service.get("namespace")
            name = service.get("name")

            service_type = service.get("type")
            selector = service.get("selector", {})

            #
            # ExternalName services don't require selectors
            #

            if service_type == "ExternalName":
                continue

            #
            # Missing selector
            #

            if not selector:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="High",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="Service has no selector",
                        description=(
                            "The Service does not define a pod selector."
                        ),
                        evidence={
                            "type": service_type,
                            "selector": selector,
                        },
                        recommendation=(
                            "Configure a valid selector that matches the target Pods."
                        ),
                    )
                )

                continue

            #
            # Empty selector values
            #

            empty = [
                key
                for key, value in selector.items()
                if value in ("", None)
            ]

            if empty:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Medium",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="Service selector contains empty values",
                        description=(
                            "One or more selector labels have empty values."
                        ),
                        evidence={
                            "selector": selector,
                            "invalid_labels": empty,
                        },
                        recommendation=(
                            "Ensure every selector label has a valid value."
                        ),
                    )
                )

        return result