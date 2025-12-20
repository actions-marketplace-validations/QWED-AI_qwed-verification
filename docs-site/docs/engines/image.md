---
sidebar_position: 7
---

# Image Engine

The Image Engine verifies claims about images using **deterministic methods first**, with VLM fallback only for complex semantic claims.

## Features

- **Metadata Extraction** - Dimensions, format (PNG, JPEG, GIF, WebP)
- **Size Verification** - 100% accurate dimension claims
- **Claim Classification** - Route to appropriate verifier
- **Multi-VLM Consensus** - Cross-validate semantic claims

## Usage

```python
from qwed_sdk import QWEDClient

client = QWEDClient(api_key="qwed_...")

# Read image
with open("chart.png", "rb") as f:
    image_bytes = f.read()

# Verify claim
result = client.verify_image(
    image=image_bytes,
    claim="The image is 800x600 pixels"
)

print(result.verdict)      # "SUPPORTED" or "REFUTED"
print(result.confidence)   # 1.0 (deterministic!)
print(result.methods_used) # ["metadata_extraction", "size_verification"]
```

## Claim Types

| Claim Type | Method | Deterministic? |
|------------|--------|----------------|
| Size/Dimensions | Metadata parsing | ✅ 100% |
| Format | Header detection | ✅ 100% |
| Color | Pixel sampling | ⚠️ Partial |
| Text | OCR required | ❌ VLM |
| Semantic | Understanding | ❌ VLM |

## Multi-VLM Consensus

For semantic claims, use multiple VLMs:

```python
result = client.verify_image_consensus(
    image=image_bytes,
    claim="The person is smiling",
    min_agreement=2  # At least 2 VLMs must agree
)

print(result.agreement_count)  # 3/3
print(result.vlm_results)      # Individual VLM responses
```
