# AgentRunner

Universal execution engine for AI agents.

## Purpose
AgentRunner receives a structured task and optional knowledge packet, selects registered tools, executes steps, checkpoints state, retries transient failures, captures artifacts/results, and emits trace events that can be forwarded to AgentVallet.

## Core flow
`TaskSpec -> Runner -> ToolRegistry -> ToolAdapter -> StateStore -> ExecutionResult`

## Features
- Agent-neutral `TaskSpec` and `ExecutionResult`
- Pluggable tool registry
- Step-by-step execution
- Retry with bounded attempts
- Checkpoint/resume using local JSON state
- Trace events for AgentVallet integration
- Safe default: unknown tools fail closed

## Quick start
```bash
pip install -e .
python examples/basic_run.py
pytest
```

## Scope
This repo is the universal execution layer. Agent selection and multi-agent decomposition belong in AgentOrchestrator. Policy/approval belongs in the later governance layer.
