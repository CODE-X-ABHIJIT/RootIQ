from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class NetworkPolicyPortValidationRule(BaseRule):

    id = "NETPOL-008"

    name = "NetworkPolicyPortValidation"

    resource_type = "networkpolicy"

    VALID_PROTOCOLS = {
        "TCP",
        "UDP",
        "SCTP",
    }

    def evaluate(self, ctx: RuleContext):

        

        for policy in ctx.resources:

            namespace = policy.get("namespace")
            name = policy.get("name")

            for direction in (
                "ingress",
                "egress",
            ):

                rules = policy.get(
                    direction,
                    [],
                )

                for rule_index, rule in enumerate(rules):

                    ports = rule.get(
                        "ports",
                        [],
                    )

                    seen = set()

                    for port_index, port in enumerate(ports):

                        protocol = (
                            port.get("protocol")
                            or "TCP"
                        )

                        port_value = port.get(
                            "port"
                        )

                        #
                        # Protocol validation
                        #

                        if (
                            protocol
                            not in self.VALID_PROTOCOLS
                        ):

                            ctx.report(
                                    rule=self,
                                
                                    id=self.id,
                                    severity="High",
                                    resource_type="NetworkPolicy",
                                    resource_name=name,
                                    namespace=namespace,
                                    title="Invalid protocol",
                                    description=(
                                        "Unsupported protocol configured."
                                    ),
                                    evidence={
                                        "direction": direction,
                                        "rule": rule_index,
                                        "protocol": protocol,
                                    },
                                    recommendation=(
                                        "Use TCP, UDP or SCTP."
                                    ),
                                )
                            

                        #
                        # Port validation
                        #

                        if isinstance(
                            port_value,
                            int,
                        ):

                            if (
                                port_value < 1
                                or port_value > 65535
                            ):

                                ctx.report(
                                        rule=self,
                                    
                                        id=self.id,
                                        severity="High",
                                        resource_type="NetworkPolicy",
                                        resource_name=name,
                                        namespace=namespace,
                                        title="Invalid port number",
                                        description=(
                                            "Port is outside the valid range."
                                        ),
                                        evidence={
                                            "port": port_value,
                                        },
                                        recommendation=(
                                            "Use ports between 1 and 65535."
                                        ),
                                    )
                                

                        elif isinstance(
                            port_value,
                            str,
                        ):

                            if (
                                not port_value
                                or " " in port_value
                            ):

                                ctx.report(
                                        rule=self,
                                    
                                        id=self.id,
                                        severity="Medium",
                                        resource_type="NetworkPolicy",
                                        resource_name=name,
                                        namespace=namespace,
                                        title="Invalid named port",
                                        description=(
                                            "Named port is empty or contains spaces."
                                        ),
                                        evidence={
                                            "port": port_value,
                                        },
                                        recommendation=(
                                            "Use a valid Kubernetes named port."
                                        ),
                                    )
                                

                        elif port_value is not None:

                            ctx.report(
                                    rule=self,
                                
                                    id=self.id,
                                    severity="Medium",
                                    resource_type="NetworkPolicy",
                                    resource_name=name,
                                    namespace=namespace,
                                    title="Unsupported port type",
                                    description=(
                                        "Port must be an integer or a string."
                                    ),
                                    evidence={
                                        "port": port_value,
                                    },
                                    recommendation=(
                                        "Specify a valid port number or named port."
                                    ),
                                )
                            

                        #
                        # Duplicate port
                        #

                        key = (
                            protocol,
                            str(port_value),
                        )

                        if key in seen:

                            ctx.report(
                                    rule=self,
                                
                                    id=self.id,
                                    severity="Low",
                                    resource_type="NetworkPolicy",
                                    resource_name=name,
                                    namespace=namespace,
                                    title="Duplicate port rule",
                                    description=(
                                        "Duplicate protocol/port combination found."
                                    ),
                                    evidence={
                                        "protocol": protocol,
                                        "port": port_value,
                                    },
                                    recommendation=(
                                        "Remove duplicate port entries."
                                    ),
                                )
                            

                        seen.add(key)

        