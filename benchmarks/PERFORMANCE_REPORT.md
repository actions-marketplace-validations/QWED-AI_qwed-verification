# QWED Performance Report

**Generated:** 2026-01-16 19:27:29
**Iterations per test:** 50

## Summary

| Engine | Operation | Avg (ms) | Throughput (/s) | Memory (MB) |
|--------|-----------|----------|-----------------|-------------|
| Math | Simple Arithmetic | 1.45 | 690 | 0.05 |
| Math | Complex Expression | 5.03 | 199 | 0.05 |
| Math | Percentage | 0.00 | 257202 | 0.00 |
| DSL | Simple Parse | 0.05 | 19750 | 0.00 |
| DSL | Complex Nested | 0.32 | 3146 | 0.00 |
| DSL | Large Expression (20 clauses) | 1.23 | 814 | 0.01 |
| Symbolic | Simple Code | 0.22 | 4458 | 0.01 |
| Symbolic | Safety Properties | 0.44 | 2279 | 0.01 |

## Performance Analysis

[!] **Slowest Operation:** Math - Complex Expression (5.03ms)
[MEM] **Most Memory:** Math - Simple Arithmetic (0.05MB)

## Recommendations
