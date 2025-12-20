---
sidebar_position: 1
---

# Verification Engines

QWED provides **8 specialized verification engines**, each using deterministic methods first and LLM only as fallback.

## Engine Overview

| Engine | Technology | Key Features |
|--------|------------|--------------|
| **Math** | SymPy + Decimal | Calculus, Matrix ops, NPV/IRR, Statistics |
| **Logic** | Z3 Theorem Prover | ForAll/Exists quantifiers, BitVectors, Arrays |
| **Code** | Multi-Lang AST | Python, JavaScript, Java, Go security analysis |
| **SQL** | SQLGlot AST | Complexity limits, Cost estimation, Schema validation |
| **Stats** | Wasm/Docker Sandbox | Secure code execution with AST validation |
| **Fact** | TF-IDF + NLP | Semantic similarity, Entity matching, Citations |
| **Image** | Deterministic + VLM | Metadata extraction, Size verification, Multi-VLM |
| **Reasoning** | Multi-LLM + Cache | Chain-of-thought validation, Result caching |

## Deterministic-First Philosophy

All engines now follow a **deterministic-first** approach:

1. **Try deterministic methods first** (100% reproducible)
2. **Fall back to LLM only when necessary**
3. **Discount LLM confidence** when used

```python
# Example: Fact verification is now deterministic!
result = client.verify_fact(
    claim="Paris is in France",
    context="Paris is the capital of France."
)
# Uses TF-IDF similarity + entity matching
# No LLM needed for most claims!
```

## Engine Selection

QWED auto-detects the appropriate engine:

| Content Pattern | Detected Engine |
|-----------------|-----------------|
| `2+2=4`, `sqrt(16)`, `derivative` | Math |
| `(AND ...)`, `ForAll`, `Exists` | Logic |
| `SELECT`, `INSERT`, `DROP` | SQL |
| ` ```python `, `import`, `function` | Code |
| Claims with context | Fact |
| Image bytes + claim | Image |

Or specify explicitly:

```python
result = client.verify(query, type="math")
```

## Engine Documentation

### Deterministic Engines
- [Math Engine](/docs/engines/math) - Calculus, Matrix, Financial
- [Logic Engine](/docs/engines/logic) - Quantifiers, Theorem Proving
- [Code Engine](/docs/engines/code) - Multi-language Security
- [SQL Engine](/docs/engines/sql) - Complexity Limits

### Data Verification Engines
- [Stats Engine](/docs/engines/stats) - Wasm Sandbox Execution
- [Fact Engine](/docs/engines/fact) - TF-IDF + Citations
- [Image Engine](/docs/engines/image) - Deterministic Verification

### Orchestration Engines
- [Reasoning Engine](/docs/engines/reasoning) - Multi-LLM Validation
- [Consensus Engine](/docs/engines/consensus) - Parallel Execution
