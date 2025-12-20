---
sidebar_position: 4
---

# Error Codes

Complete reference for QWED error codes.

## Error Response Format

```json
{
  "error": {
    "code": "QWED-001",
    "message": "Verification failed",
    "details": {
      "engine": "math",
      "reason": "Invalid expression syntax"
    }
  }
}
```

## General Errors

| Code | HTTP | Message |
|------|------|---------|
| `QWED-001` | 400 | Invalid request format |
| `QWED-002` | 401 | Invalid or missing API key |
| `QWED-003` | 403 | Access denied |
| `QWED-004` | 404 | Resource not found |
| `QWED-005` | 429 | Rate limit exceeded |
| `QWED-006` | 500 | Internal server error |
| `QWED-007` | 503 | Service temporarily unavailable |

## Verification Errors

| Code | Message |
|------|---------|
| `QWED-100` | Unknown verification type |
| `QWED-101` | Query is empty |
| `QWED-102` | Query too long |
| `QWED-103` | Invalid expression syntax |
| `QWED-104` | Engine timeout |
| `QWED-105` | Unsupported language |

## Security Errors

| Code | Message |
|------|---------|
| `QWED-200` | Prompt injection detected |
| `QWED-201` | SQL injection detected |
| `QWED-202` | Dangerous code pattern |
| `QWED-203` | Blocked content |

## Agent Errors

| Code | Message |
|------|---------|
| `QWED-AGENT-001` | Agent not registered |
| `QWED-AGENT-002` | Invalid agent token |
| `QWED-AGENT-003` | Agent suspended |
| `QWED-AGENT-004` | Action not permitted |
| `QWED-AGENT-BUDGET-001` | Daily cost limit exceeded |
| `QWED-AGENT-BUDGET-002` | Hourly rate limit exceeded |

## Attestation Errors

| Code | Message |
|------|---------|
| `QWED-ATT-001` | Invalid attestation format |
| `QWED-ATT-002` | Attestation expired |
| `QWED-ATT-003` | Attestation revoked |
| `QWED-ATT-004` | Untrusted issuer |
| `QWED-ATT-005` | Signature verification failed |

## Handling Errors

### Python

```python
from qwed_sdk import QWEDClient, QWEDError

try:
    result = client.verify("test")
except QWEDError as e:
    print(f"Error {e.code}: {e.message}")
```

### TypeScript

```typescript
import { QWEDError } from '@qwed-ai/sdk';

try {
  const result = await client.verify('test');
} catch (error) {
  if (error instanceof QWEDError) {
    console.log(`Error ${error.code}: ${error.message}`);
  }
}
```
