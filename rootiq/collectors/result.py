from dataclasses import dataclass, field
from typing import Any


@dataclass
class CollectResult:

    collector: str

    success: bool = True

    resources: list[Any] = field(default_factory=list)

    issues: list[dict] = field(default_factory=list)

    metrics: list[dict] = field(default_factory=list)

    logs: list[dict] = field(default_factory=list)

    events: list[dict] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    execution_time: float = 0.0

    error: str | None = None
