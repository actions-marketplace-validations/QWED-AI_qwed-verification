---
sidebar_position: 5
---

# Rate Limits

API rate limiting and quotas.

## Default Limits

| Plan | Requests/min | Requests/day | Batch size |
|------|--------------|--------------|------------|
| **Free** | 60 | 1,000 | 10 |
| **Pro** | 600 | 50,000 | 50 |
| **Enterprise** | Unlimited | Unlimited | 100 |

## Rate Limit Headers

Every response includes rate limit headers:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1703073600
```

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Max requests per window |
| `X-RateLimit-Remaining` | Requests remaining |
| `X-RateLimit-Reset` | Unix timestamp of reset |

## Rate Limit Response

When rate limited, you'll receive:

```json
{
  "error": {
    "code": "QWED-005",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 60,
      "reset_at": "2024-12-20T12:01:00Z",
      "retry_after": 45
    }
  }
}
```

HTTP Status: `429 Too Many Requests`

## Best Practices

### 1. Implement Exponential Backoff

```python
import time

def verify_with_retry(client, query, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.verify(query)
        except RateLimitError as e:
            wait = min(2 ** attempt, 60)
            time.sleep(wait)
    raise Exception("Max retries exceeded")
```

### 2. Use Batch Endpoints

Instead of individual requests:
```python
# ❌ 10 requests
for item in items:
    client.verify(item)

# ✅ 1 request
client.verify_batch(items)
```

### 3. Cache Results

```python
import hashlib

cache = {}

def cached_verify(client, query):
    key = hashlib.sha256(query.encode()).hexdigest()
    if key in cache:
        return cache[key]
    result = client.verify(query)
    cache[key] = result
    return result
```

## Per-Endpoint Limits

Some endpoints have specific limits:

| Endpoint | Limit |
|----------|-------|
| `/verify/batch` | 100 items/request |
| `/agent/register` | 10/hour |
| `/attestation/verify` | 1000/hour |

## Enterprise Options

For higher limits, contact us for:
- Custom rate limits
- Dedicated infrastructure
- SLA guarantees
