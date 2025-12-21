---
sidebar_position: 2
---

# Python SDK

The official Python SDK for QWED.

## Installation

```bash
pip install qwed
```

## Quick Start

```python
from qwed_sdk import QWEDClient

client = QWEDClient(api_key="qwed_your_key")

# Basic verification
result = client.verify("Is 2+2=4?")
print(result.verified)  # True
print(result.status)    # "VERIFIED"
```

## Async Client

```python
from qwed_sdk import QWEDAsyncClient
import asyncio

async def main():
    async with QWEDAsyncClient(api_key="qwed_...") as client:
        result = await client.verify("2+2=4")
        print(result.verified)

asyncio.run(main())
```

## Methods

### verify(query)

Auto-detect and verify any claim.

```python
result = client.verify("What is 15% of 200?")
```

### verify_math(expression)

Verify mathematical expressions.

```python
result = client.verify_math("x**2 + 2*x + 1 = (x+1)**2")
```

### verify_logic(query)

Verify logical constraints (QWED-Logic DSL).

```python
result = client.verify_logic("(AND (GT x 5) (LT y 10))")
print(result.model)  # {"x": 6, "y": 9}
```

### verify_code(code, language)

Check code for security vulnerabilities.

```python
result = client.verify_code(code, language="python")
for vuln in result.vulnerabilities:
    print(f"{vuln.severity}: {vuln.message}")
```

### verify_sql(query, schema)

Validate SQL queries.

```python
result = client.verify_sql(
    query="SELECT * FROM users WHERE id = 1",
    schema="CREATE TABLE users (id INT, name TEXT)"
)
```

### verify_batch(items)

Verify multiple items at once.

```python
results = client.verify_batch([
    {"query": "2+2=4", "type": "math"},
    {"query": "3*3=9", "type": "math"},
])
print(results.summary.success_rate)
```

## CLI

```bash
# Verify
qwed verify "2+2=4"

# Verify logic
qwed verify-logic "(AND (GT x 5) (LT y 10))"

# Verify code file
qwed verify-code -f script.py

# Batch verify
qwed batch -f queries.json
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `QWED_API_KEY` | API key |
| `QWED_BASE_URL` | API base URL |

