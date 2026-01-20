# Changelog

All notable changes to the QWED Protocol will be documented in this file.

## [2.4.1] - 2026-01-20
### 🚀 The Reasoning Engine & Enterprise Docker Support

#### New Features
- **Optimization Engine (`verify_optimization`)**: Added `LogicVerifier` support for Z3's `Optimize` context.
- **Vacuity Checker (`check_vacuity`)**: Added logical proof to detect "Vacuous Truths".

#### Enterprise Updates
- **Dockerized GitHub Action**: The main `qwed-verification` action now runs in a Docker container.


#### Fixes & Improvements
- Updated `logic_verifier.py` with additive, non-breaking methods.
- Replaced shell-based `action_entrypoint.sh` with robust Python handler `action_entrypoint.py`.
