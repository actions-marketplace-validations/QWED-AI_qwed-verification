---
sidebar_position: 3
---

# CrewAI Integration

Use QWED with CrewAI for verified multi-agent systems.

## Installation

```bash
pip install qwed crewai
```

## Quick Start

```python
from crewai import Task, Crew
from qwed_sdk.crewai import QWEDVerifiedAgent

# Create a verified agent
analyst = QWEDVerifiedAgent(
    role="Financial Analyst",
    goal="Perform accurate financial calculations",
    backstory="Expert in financial modeling",
)

# Use in CrewAI workflow
task = Task(
    description="Calculate compound interest for $10,000 at 5% for 10 years",
    agent=analyst.agent
)

crew = Crew(agents=[analyst.agent], tasks=[task])
result = crew.kickoff()
```

## QWEDVerificationTool

Give agents verification capabilities:

```python
from crewai import Agent
from qwed_sdk.crewai import QWEDVerificationTool

agent = Agent(
    role="Data Analyst",
    goal="Verify calculations",
    tools=[QWEDVerificationTool()]
)
```

## Specialized Tools

```python
from qwed_sdk.crewai import QWEDMathTool, QWEDCodeTool, QWEDSQLTool

agent = Agent(
    role="Developer",
    goal="Write secure code",
    tools=[
        QWEDMathTool(),   # Math verification
        QWEDCodeTool(),   # Code security
        QWEDSQLTool(),    # SQL validation
    ]
)
```

## QWEDVerifiedAgent

Agent wrapper with automatic verification:

```python
from qwed_sdk.crewai import QWEDVerifiedAgent, VerificationConfig

analyst = QWEDVerifiedAgent(
    role="Analyst",
    goal="Accurate analysis",
    backstory="...",
    verification_config=VerificationConfig(
        enabled=True,
        verify_math=True,
        verify_code=True,
        auto_correct=False,
        log_results=True,
    )
)

# Check verification summary
print(analyst.verification_summary())
# {"total_outputs": 5, "verified": 4, "failed": 1}
```

## QWEDVerifiedCrew

Verify entire crew outputs:

```python
from qwed_sdk.crewai import QWEDVerifiedCrew

crew = QWEDVerifiedCrew(
    agents=[analyst, writer],
    tasks=[task1, task2],
    verify_final_output=True,
)

result = crew.kickoff()
print(result.verified)  # True/False
print(result.overall_verification_rate)  # 0.95
```

## Task Decorator

```python
from qwed_sdk.crewai import verified_task

@verified_task(verify_output=True)
def process_result(output):
    # Output is verified before this runs
    return output.upper()
```

