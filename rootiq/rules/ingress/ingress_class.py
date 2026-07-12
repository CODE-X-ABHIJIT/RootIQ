from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class IngressClassRule(BaseRule):

    id = "INGRESS-001"

    name = "IngressClass"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for ingress in resources:

            namespace = ingress.get("namespace")
            name = ingress.get("name")

            ingress_class = ingress.get(
                "ingress_class"
            )

            annotations = ingress.get(
                "annotations",
                {},
            )

            #
            # Determine class
            #

            annotation_class = annotations.get(
                "kubernetes.io/ingress.class"
            )

            if not ingress_class:
                ingress_class = annotation_class

            #
            # Missing IngressClass
            #

            if not ingress_class:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="High",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="Ingress has no IngressClass",
                        description=(
                            "No ingressClassName or ingress.class annotation is configured."
                        ),
                        evidence={
                            "ingress_class": ingress_class,
                        },
                        recommendation=(
                            "Specify spec.ingressClassName or the ingress.class annotation."
                        ),
                    )
                )

                continue

            #
            # Empty value
            #

            if (
                isinstance(ingress_class, str)
                and not ingress_class.strip()
            ):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Medium",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="Empty IngressClass",
                        description=(
                            "IngressClass is defined but empty."
                        ),
                        evidence={
                            "ingress_class": ingress_class,
                        },
                        recommendation=(
                            "Specify a valid IngressClass."
                        ),
                    )
                )

            #
            # Annotation & spec mismatch
            #

            if (
                annotation_class
                and ingress.get("ingress_class")
                and annotation_class
                != ingress.get("ingress_class")
            ):

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Low",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="IngressClass mismatch",
                        description=(
                            "The annotation and spec define different Ingress classes."
                        ),
                        evidence={
                            "annotation": annotation_class,
                            "spec": ingress.get(
                                "ingress_class"
                            ),
                        },
                        recommendation=(
                            "Use a single consistent IngressClass."
                        ),
                    )
                )

        return result