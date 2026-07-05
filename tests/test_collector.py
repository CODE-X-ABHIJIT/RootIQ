from rootiq.collectors.base import BaseCollector
from rootiq.collectors.result import CollectResult


class DummyCollector(BaseCollector):

    name = "Dummy"

    def collect(self, k8s):

        return CollectResult(
            collector=self.name,
            resources=["pod-1", "pod-2"],
        )


collector = DummyCollector()

result = collector.run(None)

print(result)
