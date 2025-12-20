---
sidebar_position: 5
---

# Stats Engine

The Stats Engine executes statistical queries on tabular data using secure sandboxed execution.

## Features

- **Wasm Sandbox** - Portable, secure execution anywhere
- **Docker Sandbox** - Full isolation for production
- **Restricted Executor** - AST-validated Python subset (fallback)
- **Security Validation** - Pre-execution code analysis

## Usage

```python
import pandas as pd
from qwed_sdk import QWEDClient

client = QWEDClient(api_key="qwed_...")

# Create sample data
df = pd.DataFrame({
    "product": ["A", "B", "C"],
    "sales": [100, 200, 150]
})

# Verify statistical claim
result = client.verify_stats(
    query="What is the average sales?",
    data=df
)
print(result.answer)  # 150.0
```

## Sandbox Options

| Sandbox | Security | Portability | Speed |
|---------|----------|-------------|-------|
| Docker | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Wasm | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Restricted | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

## Direct Operations

For simple operations, bypass code generation:

```python
result = client.compute_statistics(
    data=df,
    column="sales",
    operation="mean"  # mean, median, std, var, sum, count, min, max
)
```
