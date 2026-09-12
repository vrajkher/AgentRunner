from agent_runner import AgentRunner, FunctionTool, JsonStateStore, StepSpec, TaskSpec, ToolRegistry


def add(a: int, b: int) -> int:
    return a + b


tools = ToolRegistry()
tools.register(FunctionTool("add", add))

runner = AgentRunner(tools, JsonStateStore(".demo_state"))
task = TaskSpec(
    task_id="demo-1",
    goal="Add two numbers",
    steps=[StepSpec(id="s1", tool="add", args={"a": 2, "b": 3})],
)

print(runner.run(task).to_dict())
