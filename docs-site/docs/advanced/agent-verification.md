---
sidebar_position: 2
---

# Agent Verification

Pre-execution verification for AI agents.

## Overview

QWED Agent Verification provides:

- **Pre-execution checks** before agents act
- **Budget enforcement** to limit costs
- **Risk assessment** for each action
- **Activity logging** for audit trails

## Registering an Agent

```python
from qwed_sdk import QWEDClient

client = QWEDClient(api_key="qwed_...")

agent = client.register_agent(
    name="DataAnalyst",
    type="supervised",  # supervised, autonomous, trusted
    principal_id="user_123",
    permissions={
        "allowed_engines": ["math", "logic", "sql"],
        "blocked_tools": ["execute_code"],
    },
    budget={
        "max_daily_cost_usd": 100,
        "max_requests_per_hour": 500,
    }
)

print(agent["agent_id"])     # agent_abc123
print(agent["agent_token"])  # qwed_agent_xyz...
```

## Verifying Actions

Before an agent executes an action:

```python
decision = client.verify_action(
    agent_id="agent_abc123",
    action={
        "type": "execute_sql",
        "query": "SELECT * FROM users"
    },
    context={
        "conversation_id": "conv_xyz",
        "user_intent": "Get user list"
    }
)

if decision["decision"] == "APPROVED":
    execute_query(query)
elif decision["decision"] == "DENIED":
    print("Action blocked:", decision["error"])
elif decision["decision"] == "PENDING":
    request_human_approval()
```

## Trust Levels

| Level | Value | Description |
|-------|-------|-------------|
| UNTRUSTED | 0 | No autonomous actions |
| SUPERVISED | 1 | Low-risk autonomous |
| AUTONOMOUS | 2 | Most actions autonomous |
| TRUSTED | 3 | Full autonomy |

## Risk Assessment

Actions are assessed for risk:

| Risk | Examples |
|------|----------|
| LOW | read_file, database_read |
| MEDIUM | send_email, api_call |
| HIGH | file_write, database_write |
| CRITICAL | execute_code, file_delete, DROP |

## Decision Matrix

| Trust Level | LOW Risk | MEDIUM Risk | HIGH Risk | CRITICAL Risk |
|-------------|----------|-------------|-----------|---------------|
| 0 (Untrusted) | PENDING | DENIED | DENIED | DENIED |
| 1 (Supervised) | APPROVED | PENDING | DENIED | DENIED |
| 2 (Autonomous) | APPROVED | APPROVED | PENDING | DENIED |
| 3 (Trusted) | APPROVED | APPROVED | APPROVED | APPROVED |

## Budget Enforcement

```python
# Check remaining budget
budget = client.get_agent_budget("agent_abc123")
print(budget)
# {
#   "cost": {"max_daily_usd": 100, "current_daily_usd": 45.50},
#   "requests": {"max_per_hour": 500, "current_hour": 123}
# }
```

## Activity Logging

```python
# Get agent activity
activity = client.get_agent_activity("agent_abc123", limit=10)
for entry in activity:
    print(f"{entry['timestamp']}: {entry['action_type']} -> {entry['decision']}")
```

## Framework Integration

### LangChain

```python
from qwed_sdk.langchain import QWEDVerificationCallback

agent = initialize_agent(
    tools=[...],
    callbacks=[QWEDVerificationCallback(agent_id="agent_abc123")]
)
```

### CrewAI

```python
from qwed_sdk.crewai import QWEDVerifiedAgent

analyst = QWEDVerifiedAgent(
    role="Analyst",
    goal="Analyze data",
    agent_id="agent_abc123"
)
```
