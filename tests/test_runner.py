from pathlib import Path

from agent_runner import AgentRunner, ExecutionStatus, FunctionTool, JsonStateStore, StepSpec, TaskSpec, ToolRegistry


def test_runner_completes_and_checkpoints(tmp_path: Path):
    tools = ToolRegistry()
    tools.register(FunctionTool("echo", lambda text: text))
    runner = AgentRunner(tools, JsonStateStore(str(tmp_path)))
    task = TaskSpec("t1", "echo", [StepSpec("s1", "echo", {"text": "ok"})])

    result = runner.run(task)
    assert result.status == ExecutionStatus.COMPLETED
    assert result.outputs[-1]["value"] == "ok"
    assert runner.state_store.load("t1")["status"] == "completed"


def test_runner_retries(tmp_path: Path):
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("temporary")
        return "done"

    tools = ToolRegistry()
    tools.register(FunctionTool("flaky", flaky))
    runner = AgentRunner(tools, JsonStateStore(str(tmp_path)))
    task = TaskSpec("t2", "retry", [StepSpec("s1", "flaky", max_retries=1)])

    result = runner.run(task)
    assert result.status == ExecutionStatus.COMPLETED
    assert calls["n"] == 2


def test_unknown_tool_fails_closed(tmp_path: Path):
    runner = AgentRunner(ToolRegistry(), JsonStateStore(str(tmp_path)))
    task = TaskSpec("t3", "fail", [StepSpec("s1", "missing")])
    result = runner.run(task)
    assert result.status == ExecutionStatus.FAILED
