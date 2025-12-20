---
sidebar_position: 3
---

# Authentication

How to authenticate with the QWED API.

## API Keys

All requests require an API key.

### Header Authentication

```bash
curl -H "X-API-Key: qwed_your_key" https://api.qwed.ai/v1/health
```

### SDK Authentication

```python
from qwed_sdk import QWEDClient

client = QWEDClient(api_key="qwed_your_key")
```

## Environment Variables

Set your API key as an environment variable:

```bash
export QWED_API_KEY=qwed_your_key
```

Then the SDK will auto-detect it:

```python
client = QWEDClient()  # Uses QWED_API_KEY env var
```

## API Key Format

| Prefix | Type |
|--------|------|
| `qwed_` | Standard API key |
| `qwed_test_` | Test/sandbox key |
| `qwed_agent_` | Agent token |

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** in production
3. **Rotate keys regularly** using the dashboard
4. **Set IP allowlists** for production keys
5. **Use test keys** for development

## Agent Authentication

For AI agent tokens:

```python
# Register agent
response = client.register_agent(name="MyBot", ...)
agent_token = response["agent_token"]  # qwed_agent_...

# Use agent token for actions
client.verify_action(
    agent_id=response["agent_id"],
    action={...}
)
```

## Scopes

API keys can have restricted scopes:

| Scope | Access |
|-------|--------|
| `verify:read` | Verification endpoints |
| `agent:write` | Agent management |
| `attestation:read` | Attestation queries |
| `admin:all` | Full access |
