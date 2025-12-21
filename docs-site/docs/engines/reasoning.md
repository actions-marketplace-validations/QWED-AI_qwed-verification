---
sidebar_position: 8
---

# Reasoning Engine

The Reasoning Engine validates LLM reasoning traces using chain-of-thought parsing and multi-provider verification.

## Features

- **Chain-of-Thought Validation** - Parse and verify reasoning steps
- **Result Caching** - LRU + Redis for repeated queries
- **Multi-Provider Support** - Anthropic, Azure OpenAI, OpenAI
- **Semantic Fact Extraction** - Identify verifiable claims

## Usage

```python
from qwed_sdk import QWEDClient

client = QWEDClient(api_key="qwed_...")

result = client.verify_reasoning(
    query="If all cats are mammals, and all mammals are animals, are all cats animals?",
    enable_caching=True
)

print(result.is_valid)     # True
print(result.confidence)   # 0.95
print(result.reasoning_trace)  # Step-by-step logic
print(result.cached)       # True/False
```

## Multi-Provider Verification

```python
result = client.verify_reasoning(
    query="Complex reasoning task...",
    providers=["anthropic", "openai", "azure"],
    enable_cross_validation=True
)

print(result.provider_agreement)  # 3/3
print(result.per_provider_results)
```

## Caching

The engine caches results to avoid redundant LLM calls:

```python
# First call - hits LLM
result1 = client.verify_reasoning(query, enable_caching=True)
print(result1.cached)  # False

# Second call - from cache
result2 = client.verify_reasoning(query, enable_caching=True)
print(result2.cached)  # True (instant!)
```

## Chain-of-Thought Validation

```python
cot_trace = """
Step 1: All cats are mammals (given)
Step 2: All mammals are animals (given)
Step 3: Therefore, all cats are animals (transitivity)
"""

result = client.validate_cot(
    trace=cot_trace,
    conclusion="All cats are animals"
)

print(result.valid_steps)    # [1, 2, 3]
print(result.invalid_steps)  # []
print(result.conclusion_valid)  # True
```

