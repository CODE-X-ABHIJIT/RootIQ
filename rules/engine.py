from rootiq.incident.incident import Incident


class RuleEngine:

    def __init__(self, registry):

        self.registry = registry

    def run(self, cluster_name, resources):

        incident = Incident(cluster=cluster_name)

        for resource in resources:

            for rule in self.registry.all():

                issue = rule.check(resource)

                if issue is not None:

                    incident.add(issue)

        return incident