from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class EventCollector(BaseCollector):

    name = "EventCollector"

    def collect(self, k8s):

        result = CollectResult(collector=self.name)

        try:

            if k8s.target.cluster_wide:

                events = k8s.core.list_event_for_all_namespaces().items

            else:

                events = k8s.core.list_namespaced_event(
                    namespace=k8s.target.namespace
                ).items

            result.metrics.append(
                {
                    "metric": "event_count",
                    "value": len(events),
                }
            )

            warning_count = 0
            normal_count = 0

            for event in events:

                if event.type == "Warning":
                    warning_count += 1
                else:
                    normal_count += 1

                result.resources.append(
                    {
                        "name": event.metadata.name,
                        "namespace": event.metadata.namespace,
                        "type": event.type,
                        "reason": event.reason,
                        "message": event.message,
                        "count": event.count,
                        "first_timestamp": (
                            event.first_timestamp.isoformat()
                            if event.first_timestamp
                            else None
                        ),
                        "last_timestamp": (
                            event.last_timestamp.isoformat()
                            if event.last_timestamp
                            else None
                        ),
                        "object": (
                            event.involved_object.kind
                            + "/"
                            + event.involved_object.name
                        ),
                    }
                )

            result.metrics.extend(
                [
                    {
                        "metric": "warning_events",
                        "value": warning_count,
                    },
                    {
                        "metric": "normal_events",
                        "value": normal_count,
                    },
                ]
            )

        except ApiException as e:

            result.success = False
            result.error = str(e)

        return result