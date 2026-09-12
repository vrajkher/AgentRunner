from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    FAILED = "failed"
    COMPLETED = "completed"


@dataclass
class StepSpec:
    id: str
    tool: str
    args: dict[str, Any] = field(default_factory=dict)
    max_retries: int = 1


@dataclass
class TaskSpec:
    task_id: str
    goal: str
    steps: list[StepSpec]
    inputs: dict[str, Any] = field(default_factory=dict)
    knowledge_packet: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    task_id: str
    status: ExecutionStatus
    outputs: list[Any] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    completed_step_ids: list[str] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data
