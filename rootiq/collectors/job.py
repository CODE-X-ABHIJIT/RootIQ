from kubernetes.client.rest import ApiException

from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class JobCollector(BaseCollector):

    name = "JobCollector"

    def collect(self, k8s):

        result = CollectResult(collector=self.name)

        try:

            if k8s.target.cluster_wide:

                jobs = (
                    k8s.batch.list_job_for_all_namespaces().items
                )

            else:

                jobs = (
                    k8s.batch.list_namespaced_job(
                        namespace=k8s.target.namespace
                    ).items
                )

            result.metrics.append(
                {
                    "metric": "job_count",
                    "value": len(jobs),
                }
            )

            successful = 0
            failed = 0
            active = 0

            for job in jobs:

                succeeded = job.status.succeeded or 0
                failed_count = job.status.failed or 0
                active_count = job.status.active or 0

                if succeeded > 0:
                    successful += 1

                if failed_count > 0:
                    failed += 1

                if active_count > 0:
                    active += 1

                result.resources.append(
                    {
                        "name": job.metadata.name,
                        "namespace": job.metadata.namespace,
                        "completions": job.spec.completions,
                        "parallelism": job.spec.parallelism,
                        "active": active_count,
                        "succeeded": succeeded,
                        "failed": failed_count,
                        "completion_mode": job.spec.completion_mode,
                        "backoff_limit": job.spec.backoff_limit,
                        "start_time": (
                            job.status.start_time.isoformat()
                            if job.status.start_time
                            else None
                        ),
                        "completion_time": (
                            job.status.completion_time.isoformat()
                            if job.status.completion_time
                            else None
                        ),
                        "creation_timestamp": (
                            job.metadata.creation_timestamp.isoformat()
                            if job.metadata.creation_timestamp
                            else None
                        ),
                    }
                )

            result.metrics.extend(
                [
                    {
                        "metric": "successful_jobs",
                        "value": successful,
                    },
                    {
                        "metric": "failed_jobs",
                        "value": failed,
                    },
                    {
                        "metric": "active_jobs",
                        "value": active,
                    },
                ]
            )

        except ApiException as e:

            result.success = False
            result.error = str(e)

        