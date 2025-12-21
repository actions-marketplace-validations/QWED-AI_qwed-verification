---
sidebar_position: 5
---

# SQL Engine

SQL query validation and injection detection.

## Overview

The SQL Engine validates queries for:

- SQL injection patterns
- Destructive operations
- Schema compliance
- Syntax correctness

## Usage

```python
result = client.verify_sql(
    query="SELECT * FROM users WHERE id = 1",
    schema="CREATE TABLE users (id INT, name TEXT)"
)
print(result.verified)  # True
```

## Injection Detection

```python
# SQL injection pattern
result = client.verify_sql("SELECT * FROM users; DROP TABLE users; --")
print(result.status)  # "BLOCKED"
print(result.vulnerabilities)
# [{"type": "injection", "message": "Chained DROP statement"}]
```

## Detected Patterns

| Pattern | Risk | Example |
|---------|------|---------|
| Comment injection | Critical | `; --` |
| OR injection | Critical | `' OR '1'='1` |
| UNION injection | Critical | `UNION SELECT` |
| Chained DROP | Critical | `; DROP TABLE` |

## Destructive Operations

```python
# Destructive query
result = client.verify_sql("DELETE FROM users")
print(result.status)  # "FAILED"
print(result.vulnerabilities)
# [{"type": "destructive_delete", "severity": "high"}]
```

| Operation | Severity |
|-----------|----------|
| DROP | Critical |
| DELETE | High |
| TRUNCATE | High |
| UPDATE | High |

## Supported Dialects

- PostgreSQL
- MySQL
- SQLite
- SQL Server
- BigQuery

```python
result = client.verify_sql(query, schema, dialect="postgresql")
```

