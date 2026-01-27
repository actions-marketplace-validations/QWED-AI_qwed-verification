# 🛡️ QWED Privacy Shield (PII Masking)

QWED is designed for **Enterprise Privacy**. We ensure that sensitive data never leaves your secure environment inadvertently.

## How It Works

The **Privacy Shield** (Phase 19) intercepts all prompts *before* they are sent to any LLM provider (OpenAI, Anthropic, or even local models). It identifies and redacts Personally Identifiable Information (PII) using Microsoft Presidio.

### Supported Entities
*   **Credit Cards**: Replaced with `<CREDIT_CARD>`
*   **US SSN**: Replaced with `<US_SSN>`
*   **Email Addresses**: Replaced with `<EMAIL_ADDRESS>`
*   **Phone Numbers**: Replaced with `<PHONE_NUMBER>`
*   **IBAN Codes**: Replaced with `<IBAN_CODE>`

## Usage

Enable the Privacy Shield when initializing `QWEDLocal` or `QWEDClient`.

### Python SDK

```python
from qwed import QWEDLocal

# Initialize with mask_pii=True
client = QWEDLocal(
    mask_pii=True,
    model="gpt-4o"
)

# Sensitive query
query = "Check this transaction: Credit Card 4111-2222-3333-4444 expired."

result = client.verify(query)

# Console Output:
# 🛡️ Privacy Shield Active: 1 PII entities masked
# LLM receives: "Check this transaction: Credit Card <CREDIT_CARD> expired."
```

## Configuration

Install the required dependencies:

```bash
pip install "qwed[pii]"
python -m spacy download en_core_web_lg
```

## Security Note

While we use state-of-the-art NLP models (Presidio/SpaCy) to detect PII, no system is 100% perfect. We recommend manual review for highly sensitive environments and using **Local LLMs (Ollama)** for data that absolutely cannot leave your premises.
