from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Callable

from .models import ExecutionResult, ExecutionStatus, TaskSpec
from .state import JsonStateStore
from .tools import ToolRegistry


TraceSink = Callable[[dict[str, Any]], None]


class AgentRunner:
    def __init__(
        self,
        tools: ToolRegistry,
        state_store: JsonStateStore | None = None,
        trace_sink: TraceSink | None = None,
    ):
        self.tools = tools
        self.state_store = state_store or JsonStateStore()
        self.trace_sink = trace_sink

    def _emit(self, result: ExecutionResult, event: str, **data: Any) -> None:
        item = {
            "time": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **data,
        }
        result.trace.append(item)
        if self.trace_sink:
            self.trace_sink(item)

    def _checkpoint(self, result: ExecutionResult) -> None:
        self.state_store.save(result.task_id, result.to_dict())

    def run(self, task: TaskSpec, resume: bool = True) -> ExecutionResult:
        existing = self.state_store.load(task.task_id) if resume else None
        completed = list(existing.get("completed_step_ids", [])) if existing else []
        outputs = list(existing.get("outputs", [])) if existing else []
        errors = list(existing.get("errors", [])) if existing else []

        result = ExecutionResult(
            task_id=task.task_id,
            status=ExecutionStatus.RUNNING,
            outputs=outputs,
            errors=errors,
            completed_step_ids=completed,
        )
        self._emit(result, "task_started", goal=task.goal, resumed=bool(existing))
        self._checkpoint(result)

        for step in task.steps:
            if step.id in result.completed_step_ids:
                self._emit(result, "step_skipped", step_id=step.id, reason="already_completed")
                continue

            try:
                tool = self.tools.get(step.tool)
            except Exception as exc:
                result.status = ExecutionStatus.FAILED
                result.errors.append(str(exc))
                self._emit(result, "step_failed", step_id=step.id, error=str(exc))
                self._checkpoint(result)
                return result

            attempts = 0
            last_error: Exception | None = None
            while attempts <= step.max_retries:
                attempts += 1
                self._emit(result, "step_attempt", step_id=step.id, tool=step.tool, attempt=attempts)
                try:
                    value = tool.execute(**step.args)
                    result.outputs.append({"step_id": step.id, "value": value})
                    result.completed_step_ids.append(step.id)
                    self._emit(result, "step_completed", step_id=step.id, attempt=attempts)
                    self._checkpoint(result)
                    last_error = None
                    break
                except Exception as exc:
                    last_error = exc
                    self._emit(result, "step_error", step_id=step.id, attempt=attempts, error=str(exc))

            if last_error is not None:
                result.status = ExecutionStatus.FAILED
                result.errors.append(f"{step.id}: {last_error}")
                self._emit(result, "task_failed", step_id=step.id, error=str(last_error))
                self._checkpoint(result)
                return result

        result.status = ExecutionStatus.COMPLETED
        self._emit(result, "task_completed")
        self._checkpoint(result)
        return result
