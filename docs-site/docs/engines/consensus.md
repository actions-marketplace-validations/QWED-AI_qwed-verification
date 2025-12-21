---
sidebar_position: 9
---

# Consensus Engine

The Consensus Engine orchestrates multiple verification engines for high-confidence results with fault tolerance.

## Features

- **Async Parallel Execution** - Run engines concurrently
- **Circuit Breaker** - Auto-disable failing engines
- **Engine Health Monitoring** - Track reliability
- **Weighted Consensus** - Consider engine reliability

## Usage

```python
from qwed_sdk import QWEDClient

client = QWEDClient(api_key="qwed_...")

result = client.verify_with_consensus(
    query="2 + 2 = 4",
    mode="maximum"  # single, high, maximum
)

print(result.final_answer)     # 4
print(result.confidence)       # 0.999
print(result.engines_used)     # 3
print(result.agreement_status) # "unanimous"
```

## Verification Modes

| Mode | Engines | Speed | Confidence |
|------|---------|-------|------------|
| `single` | 1 (SymPy) | ⚡ Fast | Good |
| `high` | 2 (SymPy + Python) | Medium | High |
| `maximum` | 3+ (All applicable) | Slower | Maximum |

## Async Execution

```python
import asyncio

async def verify_many():
    results = await asyncio.gather(
        client.verify_async("2+2=4"),
        client.verify_async("3*3=9"),
        client.verify_async("sqrt(16)=4")
    )
    return results
```

## Circuit Breaker

When an engine fails repeatedly, it's automatically disabled:

```python
# Check engine health
health = client.get_engine_health()

print(health)
# {
#   "SymPy": {"state": "healthy", "failures": 0},
#   "Python": {"state": "healthy", "failures": 0},
#   "Z3": {"state": "degraded", "failures": 2}
# }

# Reset circuit breakers
client.reset_circuit_breakers()
```

## Consensus Calculation

The engine uses weighted voting:

| Engine | Reliability Weight |
|--------|-------------------|
| SymPy | 1.00 |
| Z3 | 0.995 |
| Python | 0.99 |
| Stats | 0.98 |
| Fact | 0.85 |

Final confidence = weighted average of agreeing engines.

