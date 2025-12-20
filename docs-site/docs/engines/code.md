---
sidebar_position: 4
---

# Code Engine

Security analysis of code using AST parsing and pattern detection.

## Overview

The Code Engine uses **static analysis** to detect security vulnerabilities:

- Dangerous function calls
- Code injection risks
- Unsafe imports
- Security anti-patterns

## Supported Languages

| Language | Detection |
|----------|-----------|
| Python | Full AST + patterns |
| JavaScript | Pattern matching |
| Shell | Pattern matching |

## Usage

```python
code = """
import os
os.system('rm -rf /')
"""

result = client.verify_code(code, language="python")
print(result.verified)  # False
print(result.status)    # "BLOCKED"

for vuln in result.vulnerabilities:
    print(f"{vuln.severity}: {vuln.message}")
    # CRITICAL: Shell command execution (os.system)
```

## Detection Categories

### Critical

| Pattern | Risk |
|---------|------|
| `eval()` | Code execution |
| `exec()` | Code execution |
| `os.system()` | Shell execution |
| `subprocess.*` | Process spawning |

### High

| Pattern | Risk |
|---------|------|
| `pickle.load()` | Deserialization |
| `__import__()` | Dynamic import |
| `open(..., 'w')` | File overwrite |

### Medium

| Pattern | Risk |
|---------|------|
| `requests.get()` | External request |
| `sqlite3.connect()` | Database access |

## Response Format

```python
{
    "status": "BLOCKED",
    "verified": False,
    "vulnerabilities": [
        {
            "type": "os.system",
            "severity": "critical",
            "line": 2,
            "message": "Shell command execution"
        }
    ]
}
```

## Safe Code Example

```python
good_code = """
def calculate_sum(a, b):
    return a + b

result = calculate_sum(5, 10)
print(f"Sum: {result}")
"""

result = client.verify_code(good_code)
print(result.verified)  # True
print(result.status)    # "VERIFIED"
```
