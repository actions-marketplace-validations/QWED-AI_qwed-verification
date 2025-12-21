---
sidebar_position: 6
---

# Fact Engine

The Fact Engine verifies factual claims using **deterministic methods first**, without requiring LLM calls for most claims.

## Features

- **TF-IDF Semantic Similarity** - No LLM needed!
- **Keyword Overlap Analysis** - Fast and deterministic
- **Entity Matching** - Numbers, dates, names
- **Citation Extraction** - With relevance scoring
- **Negation Detection** - Catch contradictions
- **LLM Fallback** - Only when confidence is low

## Usage

```python
from qwed_sdk import QWEDClient

client = QWEDClient(api_key="qwed_...")

result = client.verify_fact(
    claim="The company was founded in 2020.",
    context="Acme Corp was founded in 2020 by John Smith in San Francisco."
)

print(result.verdict)       # "SUPPORTED"
print(result.confidence)    # 0.95
print(result.citations)     # [{"sentence": "...", "relevance": 0.98}]
print(result.methods_used)  # ["semantic_similarity", "entity_matching"]
```

## Scoring Methods

| Method | What It Checks | Weight |
|--------|----------------|--------|
| Semantic Similarity | TF-IDF cosine distance | 0.25 |
| Keyword Overlap | Shared important words | 0.20 |
| Entity Match | Numbers, dates, names | 0.35 |
| Negation Conflict | Contradicting statements | 0.20 |

## Why Deterministic?

```
BEFORE (v1): 
Claim → LLM → "I think this is supported" 😕

AFTER (v2):
Claim → TF-IDF + Entity Match → SUPPORTED ✅
       (LLM only if confidence < 0.7)
```

No more hallucinated fact checks!

