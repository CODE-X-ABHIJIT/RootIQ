from rootiq.engine.rule_context import RuleContext
from rootiq.rules.base import BaseRule


class ServiceSessionAffinityRule(BaseRule):

    id = "SERVICE-009"

    name = "ServiceSessionAffinity"

    resource_type = "service"

    def evaluate(self, ctx: RuleContext):

        

        for service in ctx.resources:

            namespace = service.get("namespace")
            name = service.get("name")

            session_affinity = service.get(
                "session_affinity",
                "None",
            )

            affinity_config = service.get(
                "session_affinity_config",
                {},
            )

            #
            # Unknown session affinity
            #

            if session_affinity not in (
                "None",
                "ClientIP",
            ):

                ctx.report(
                        rule=self,
                    
                        id=self.id,
                        severity="Medium",
                        resource_type="Service",
                        resource_name=name,
                        namespace=namespace,
                        title="Unknown session affinity",
                        description=(
                            "Service uses an unsupported session affinity."
                        ),
                        evidence={
                            "session_affinity": session_affinity,
                        },
                        recommendation=(
                            "Use None or ClientIP."
                        ),
                    )
                

            #
            # ClientIP without timeout
            #

            if session_affinity == "ClientIP":

                timeout = affinity_config.get(
                    "timeout_seconds"
                )

                if timeout is None:

                    ctx.report(
                            rule=self,
                        
                            id=self.id,
                            severity="Low",
                            resource_type="Service",
                            resource_name=name,
                            namespace=namespace,
                            title="ClientIP timeout not configured",
                            description=(
                                "Session affinity timeout is not configured."
                            ),
                            evidence={},
                            recommendation=(
                                "Configure timeoutSeconds if sticky sessions are required."
                            ),
                        )
                    

                elif timeout < 1 or timeout > 86400:

                    ctx.report(
                            rule=self,
                        
                            id=self.id,
                            severity="Medium",
                            resource_type="Service",
                            resource_name=name,
                            namespace=namespace,
                            title="Invalid ClientIP timeout",
                            description=(
                                "Session affinity timeout is outside the supported range."
                            ),
                            evidence={
                                "timeout_seconds": timeout,
                            },
                            recommendation=(
                                "Use a timeout between 1 and 86400 seconds."
                            ),
                        )
                    

                elif timeout > 10800:

                    ctx.report(
                            rule=self,
                        
                            id=self.id,
                            severity="Info",
                            resource_type="Service",
                            resource_name=name,
                            namespace=namespace,
                            title="Very long session affinity timeout",
                            description=(
                                "Sticky sessions remain active for a long time."
                            ),
                            evidence={
                                "timeout_seconds": timeout,
                            },
                            recommendation=(
                                "Reduce timeout unless long-lived sessions are required."
                            ),
                        )
                    

        