---
sidebar_position: 2
---

# Math Engine

Deterministic verification of mathematical expressions using SymPy.

## Overview

The Math Engine uses [SymPy](https://www.sympy.org/) for symbolic computation to provide **100% accurate** verification of:

- Arithmetic expressions
- Algebraic identities
- Calculus (derivatives, integrals)
- Trigonometric functions
- Complex numbers

## Usage

```python
result = client.verify_math("x**2 + 2*x + 1 = (x+1)**2")
print(result.verified)  # True (identity verified)
```

## Supported Operations

| Category | Examples |
|----------|----------|
| Arithmetic | `2+2=4`, `15*3=45` |
| Algebra | `x^2 - 1 = (x-1)(x+1)` |
| Calculus | `derivative of x^2 = 2x` |
| Trigonometry | `sin(pi/2) = 1` |
| Logarithms | `log(e) = 1` |

## Identity Verification

```python
# Verify algebraic identities
result = client.verify_math("(a+b)^2 = a^2 + 2*a*b + b^2")
# Verified: True

# Catch incorrect identities
result = client.verify_math("(a+b)^2 = a^2 + b^2")
# Verified: False, Message: "Missing 2ab term"
```

## Expression Evaluation

```python
result = client.verify_math("sqrt(16) + 3^2")
# Result: 13.0
```

## Error Correction

```python
result = client.verify("15% of 200 is 40")
# Status: CORRECTED
# Message: "15% of 200 is 30, not 40"
```
