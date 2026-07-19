import ipaddress

from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class NetworkPolicyIPBlockRule(BaseRule):

    id = "NETPOL-007"

    name = "NetworkPolicyIPBlock"

    resource_type = "networkpolicy"

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

                peer_key = (
                    "from"
                    if direction == "ingress"
                    else "to"
                )

                for rule_index, rule in enumerate(rules):

                    peers = rule.get(
                        peer_key,
                        [],
                    )

                    cidrs = set()

                    for peer_index, peer in enumerate(peers):

                        ip_block = peer.get(
                            "ip_block"
                        )

                        if not ip_block:
                            continue

                        cidr = ip_block.get(
                            "cidr"
                        )

                        except_list = ip_block.get(
                            "except",
                            [],
                        )

                        #
                        # Missing CIDR
                        #

                        if not cidr:

                            ctx.report(
                                        rule=self,
                                
                                    id=self.id,
                                    severity="High",
                                    resource_type="NetworkPolicy",
                                    resource_name=name,
                                    namespace=namespace,
                                    title="Missing CIDR",
                                    description=(
                                        "ipBlock is missing a CIDR."
                                    ),
                                    evidence={
                                        "direction": direction,
                                        "rule": rule_index,
                                        "peer": peer_index,
                                    },
                                    recommendation=(
                                        "Specify a valid CIDR."
                                    ),
                                )
                        

                            continue

                        #
                        # Duplicate CIDR
                        #

                        if cidr in cidrs:

                            ctx.report(
                                        rule=self,
                                
                                    id=self.id,
                                    severity="Low",
                                    resource_type="NetworkPolicy",
                                    resource_name=name,
                                    namespace=namespace,
                                    title="Duplicate CIDR",
                                    description=(
                                        "Duplicate CIDR found in the same rule."
                                    ),
                                    evidence={
                                        "cidr": cidr,
                                    },
                                    recommendation=(
                                        "Remove duplicate CIDR entries."
                                    ),
                                )
                        

                        cidrs.add(cidr)

                        #
                        # Validate CIDR
                        #

                        try:

                            network = (
                                ipaddress.ip_network(
                                    cidr,
                                    strict=False,
                                )
                            )

                        except ValueError:

                            ctx.report(
                                        rule=self,
                                
                                    id=self.id,
                                    severity="High",
                                    resource_type="NetworkPolicy",
                                    resource_name=name,
                                    namespace=namespace,
                                    title="Invalid CIDR",
                                    description=(
                                        "ipBlock contains an invalid CIDR."
                                    ),
                                    evidence={
                                        "cidr": cidr,
                                    },
                                    recommendation=(
                                        "Use a valid IPv4 or IPv6 CIDR."
                                    ),
                                )
                        

                            continue

                        #
                        # Open to entire Internet
                        #

                        if str(network) in (
                            "0.0.0.0/0",
                            "::/0",
                        ):

                            ctx.report(
                                        rule=self,
                                
                                    id=self.id,
                                    severity="High",
                                    resource_type="NetworkPolicy",
                                    resource_name=name,
                                    namespace=namespace,
                                    title="Open CIDR",
                                    description=(
                                        "NetworkPolicy allows traffic from or to the entire Internet."
                                    ),
                                    evidence={
                                        "cidr": cidr,
                                    },
                                    recommendation=(
                                        "Restrict the CIDR to trusted networks."
                                    ),
                                )
                        

                        #
                        # Validate except list
                        #

                        for excluded in except_list:

                            try:

                                excluded_net = (
                                    ipaddress.ip_network(
                                        excluded,
                                        strict=False,
                                    )
                                )

                            except ValueError:

                                ctx.report(
                                        rule=self,
                                    
                                        id=self.id,
                                        severity="Medium",
                                        resource_type="NetworkPolicy",
                                        resource_name=name,
                                        namespace=namespace,
                                        title="Invalid exception CIDR",
                                        description=(
                                            "An invalid CIDR exists in the except list."
                                        ),
                                        evidence={
                                            "cidr": excluded,
                                        },
                                        recommendation=(
                                            "Correct or remove the invalid CIDR."
                                        ),
                                    )
                            

                                continue

                            if not excluded_net.subnet_of(network):

                                ctx.report(
                                        rule=self,
                                    
                                        id=self.id,
                                        severity="Medium",
                                        resource_type="NetworkPolicy",
                                        resource_name=name,
                                        namespace=namespace,
                                        title="Exception outside CIDR",
                                        description=(
                                            "The exception CIDR is not contained within the parent CIDR."
                                        ),
                                        evidence={
                                            "cidr": cidr,
                                            "except": excluded,
                                        },
                                        recommendation=(
                                            "Ensure exception CIDRs are subsets of the main CIDR."
                                        ),
                                    )
                            

        