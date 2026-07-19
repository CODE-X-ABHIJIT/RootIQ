from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class CronJobCollector(BaseCollector):

    name = "CronJobCollector"

    def collect(self, k8s):

        result = CollectResult(collector=self.name)

        try:

            if k8s.target.cluster_wide:

                cronjobs = (
                    k8s.batch.list_cron_job_for_all_namespaces().items
                )

            else:

                cronjobs = (
                    k8s.batch.list_namespaced_cron_job(
                        namespace=k8s.target.namespace
                    ).items
                )

            result.metrics.append(
                {
                    "metric": "cronjob_count",
                    "value": len(cronjobs),
                }
            )

            suspended = 0

            for cj in cronjobs:

                if cj.spec.suspend:
                    suspended += 1

                result.resources.append(
                    {
                        "name": cj.metadata.name,
                        "namespace": cj.metadata.namespace,
                        "schedule": cj.spec.schedule,
                        "timezone": getattr(cj.spec, "time_zone", None),
                        "suspend": cj.spec.suspend,
                        "concurrency_policy": cj.spec.concurrency_policy,
                        "successful_jobs_history_limit": cj.spec.successful_jobs_history_limit,
                        "failed_jobs_history_limit": cj.spec.failed_jobs_history_limit,
                        "last_schedule_time": (
                            cj.status.last_schedule_time.isoformat()
                            if cj.status.last_schedule_time
                            else None
                        ),
                        "active_jobs": len(cj.status.active or []),
                        "creation_timestamp": (
                            cj.metadata.creation_timestamp.isoformat()
                            if cj.metadata.creation_timestamp
                            else None
                        ),
                    }
                )

            result.metrics.append(
                {
                    "metric": "suspended_cronjobs",
                    "value": suspended,
                }
            )

        except ApiException as e:

            result.success = False
            result.error = str(e)

        