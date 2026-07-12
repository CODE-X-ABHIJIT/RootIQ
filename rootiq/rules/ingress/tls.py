from rootiq.rules.base import BaseRule
from rootiq.rules.issue import Issue
from rootiq.rules.result import RuleResult


class IngressTLSRule(BaseRule):

    id = "INGRESS-003"

    name = "IngressTLS"

    def evaluate(self, resources):

        result = RuleResult(rule=self.name)

        for ingress in resources:

            namespace = ingress.get("namespace")
            name = ingress.get("name")

            tls = ingress.get("tls", [])
            rules = ingress.get("rules", [])

            #
            # No TLS configured
            #

            if not tls:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Medium",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="Ingress is not using TLS",
                        description=(
                            "No TLS configuration is defined."
                        ),
                        evidence={},
                        recommendation=(
                            "Configure TLS to secure HTTP traffic."
                        ),
                    )
                )

                continue

            #
            # Rule hosts
            #

            rule_hosts = {
                rule.get("host")
                for rule in rules
                if rule.get("host")
            }

            tls_hosts = set()

            for entry in tls:

                hosts = entry.get("hosts", [])
                secret = entry.get("secret_name")

                #
                # Missing Secret
                #

                if not secret:

                    result.issues.append(
                        Issue(
                            id=self.id,
                            severity="High",
                            resource_type="Ingress",
                            resource_name=name,
                            namespace=namespace,
                            title="TLS Secret missing",
                            description=(
                                "TLS entry has no Secret configured."
                            ),
                            evidence={
                                "hosts": hosts,
                            },
                            recommendation=(
                                "Specify a valid TLS Secret."
                            ),
                        )
                    )

                #
                # Missing Hosts
                #

                if not hosts:

                    result.issues.append(
                        Issue(
                            id=self.id,
                            severity="Medium",
                            resource_type="Ingress",
                            resource_name=name,
                            namespace=namespace,
                            title="TLS hosts missing",
                            description=(
                                "TLS configuration does not contain any hosts."
                            ),
                            evidence={
                                "secret_name": secret,
                            },
                            recommendation=(
                                "Specify one or more TLS hosts."
                            ),
                        )
                    )

                tls_hosts.update(hosts)

            #
            # Rules without TLS
            #

            missing_tls = rule_hosts - tls_hosts

            if missing_tls:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Medium",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="Ingress hosts are not protected by TLS",
                        description=(
                            "Some hosts defined in routing rules are not included in TLS."
                        ),
                        evidence={
                            "hosts": sorted(
                                missing_tls
                            ),
                        },
                        recommendation=(
                            "Add every exposed host to the TLS configuration."
                        ),
                    )
                )

            #
            # Duplicate Hosts
            #

            all_hosts = []

            for entry in tls:

                all_hosts.extend(
                    entry.get(
                        "hosts",
                        [],
                    )
                )

            duplicates = {
                h
                for h in all_hosts
                if all_hosts.count(h) > 1
            }

            if duplicates:

                result.issues.append(
                    Issue(
                        id=self.id,
                        severity="Low",
                        resource_type="Ingress",
                        resource_name=name,
                        namespace=namespace,
                        title="Duplicate TLS hosts",
                        description=(
                            "The same host appears in multiple TLS entries."
                        ),
                        evidence={
                            "duplicate_hosts": sorted(
                                duplicates
                            ),
                        },
                        recommendation=(
                            "Remove duplicate TLS host definitions."
                        ),
                    )
                )

        return result