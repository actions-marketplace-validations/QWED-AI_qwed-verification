---
sidebar_position: 1
---

# Cryptographic Attestations

Generate and verify cryptographic proofs of verification.

## What are Attestations?

An **attestation** is a cryptographically signed proof that a verification occurred. It:

- Uses **ES256 (ECDSA P-256)** signatures
- Is formatted as a **JWT**
- Can be verified independently
- Can be stored on-chain

## Requesting Attestations

```python
result = client.verify(
    "2+2=4",
    include_attestation=True
)

print(result.attestation)
# eyJhbGciOiJFUzI1NiIsInR5cCI6InF3ZWQtYXR0ZXN...
```

## Attestation Structure

### Header

```json
{
  "alg": "ES256",
  "typ": "qwed-attestation+jwt",
  "kid": "did:qwed:node:production#signing-key-2024"
}
```

### Payload

```json
{
  "iss": "did:qwed:node:production",
  "sub": "sha256:abc123...",
  "iat": 1703073600,
  "exp": 1734609600,
  "jti": "att_xyz789",
  "qwed": {
    "version": "1.0",
    "result": {
      "status": "VERIFIED",
      "verified": true,
      "engine": "math",
      "confidence": 1.0
    },
    "query_hash": "sha256:def456...",
    "proof_hash": "sha256:ghi789..."
  }
}
```

## Verifying Attestations

### Using the API

```python
valid, claims, error = client.verify_attestation(jwt)
if valid:
    print(f"Verified by: {claims['iss']}")
```

### Using the SDK

```python
from qwed_sdk import verify_attestation

is_valid = verify_attestation(
    jwt="eyJhbGci...",
    trusted_issuers=["did:qwed:node:production"]
)
```

## Trust Anchors

QWED maintains a registry of trusted attestation issuers:

| Issuer DID | Name | Status |
|------------|------|--------|
| `did:qwed:node:production` | QWED Production | ✅ Active |
| `did:qwed:node:staging` | QWED Staging | ✅ Active |

## Attestation Chains

Link multiple attestations together:

```python
attestation1 = client.verify("step1", include_attestation=True)
attestation2 = client.verify(
    "step2",
    include_attestation=True,
    chain_id="chain_abc",
    chain_index=1,
    previous_attestation=attestation1.jti
)
```

## Use Cases

1. **Audit Trails** - Prove AI outputs were verified
2. **Compliance** - Regulatory verification records
3. **Blockchain** - Anchor proofs on-chain
4. **Badges** - Show verification status in UIs

## Badge Integration

Embed attestation badges:

```markdown
![Verified](https://api.qwed.ai/badge/attestation/att_xyz789)
```

