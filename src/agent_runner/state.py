import json
from pathlib import Path
from typing import Any


class JsonStateStore:
    def __init__(self, directory: str = ".agent_runner_state"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, task_id: str) -> Path:
        safe = "".join(c for c in task_id if c.isalnum() or c in "-_" )
        if not safe:
            raise ValueError("Invalid task_id")
        return self.directory / f"{safe}.json"

    def save(self, task_id: str, state: dict[str, Any]) -> None:
        path = self._path(task_id)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")
        tmp.replace(path)

    def load(self, task_id: str) -> dict[str, Any] | None:
        path = self._path(task_id)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def clear(self, task_id: str) -> None:
        path = self._path(task_id)
        if path.exists():
            path.unlink()
