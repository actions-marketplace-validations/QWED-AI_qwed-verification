---
sidebar_position: 3
---

# Logic Engine

SAT/SMT solving using Z3 for logical constraint verification.

## Overview

The Logic Engine uses [Z3](https://github.com/Z3Prover/z3) SMT solver to provide **mathematical proofs** for:

- Satisfiability (SAT/UNSAT)
- Model finding
- Constraint solving
- Logical inference

## QWED-Logic DSL

QWED uses an S-expression based DSL for logical expressions:

```lisp
(AND (GT x 5) (LT y 10))
```

## Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `AND` | Logical AND | `(AND a b)` |
| `OR` | Logical OR | `(OR a b)` |
| `NOT` | Logical NOT | `(NOT a)` |
| `IMPLIES` | Implication | `(IMPLIES a b)` |
| `EQ` | Equals | `(EQ x 5)` |
| `NE` | Not equals | `(NE x 5)` |
| `GT` | Greater than | `(GT x 5)` |
| `GE` | Greater or equal | `(GE x 5)` |
| `LT` | Less than | `(LT x 10)` |
| `LE` | Less or equal | `(LE x 10)` |

## Usage

```python
# Simple constraint
result = client.verify_logic("(AND (GT x 5) (LT y 10))")
print(result.status)  # "SAT"
print(result.model)   # {"x": 6, "y": 9}

# Unsatisfiable constraint
result = client.verify_logic("(AND (GT x 10) (LT x 5))")
print(result.status)  # "UNSAT"
```

## Complex Constraints

```python
# Multiple variables
expr = """
(AND
  (GT x 0)
  (GT y 0)
  (EQ (PLUS x y) 100)
  (GT x y)
)
"""
result = client.verify_logic(expr)
# Model: {x: 51, y: 49}
```

## Arithmetic in Logic

```lisp
(EQ (PLUS (MULT 2 x) 3) 15)  # 2x + 3 = 15
(GT (DIV x 2) 5)              # x/2 > 5
```

