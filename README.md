# QWED: The Protocol for Verifiable Intelligence 🛡️

> **Version:** 1.2 (Enterprise Beta)  
> **Core:** Python 3.11 + FastAPI + Z3 Solver + PostgreSQL  
> **Architecture:** Hybrid Formal Assurance System (HFAS)

### "Trust, but Verify."
QWED is a **Model-Agnostic Verification Middleware** that acts as a firewall between your LLM and your critical business logic. It translates probabilistic AI hallucinations into deterministic mathematical guarantees.

---

## 🚀 New in v1.2 (The "Beast" Update)

### 1. 🏦 Deterministic Financial Engine
- **Problem:** LLMs use floating-point math, leading to money errors (e.g., `0.1 + 0.2 = 0.300000004`).
- **Solution:** Replaced `float` with **Arbitrary-Precision Decimal Arithmetic**.
- **Unit Safety:** Strict **Currency Awareness**. Throws `UnitMismatchError` if adding incompatible currencies without conversion.

### 2. 🧠 Explainable Logic (XAI)
- **Problem:** Traditional validators just return "False" when a rule breaks.
- **Solution:** Z3 Engine now extracts **Counter-Models**.
- **Impact:** Instead of just blocking, we tell you *why*:
  > *"Rejected. Violation: tax_rate is 12% but 'Electronics' requires 18%."*

### 3. ⚡ High-Concurrency Infrastructure
- **Database:** Migrated from SQLite to **PostgreSQL (Dockerized)**.
- **Scale:** Handles hundreds of concurrent verification requests.

---

## 🧠 The 8 Verification Engines

| # | Engine | Technology | Function |
|---|--------|------------|----------|
| 1 | **Math & Finance** | `SymPy` + `Decimal` | Verifies calculations with infinite precision & unit safety |
| 2 | **Logic & Constraint** | `Z3` + `QWED-DSL` | Proves satisfiability of complex business rules (SMT Solving) |
| 3 | **Statistics** | `Pandas` + `SciPy` | Verifies claims about tabular data |
| 4 | **Fact Checker** | `NLP` | Verifies text claims with exact citations |
| 5 | **Code Security** | `AST` | Static analysis for vulnerabilities & secrets |
| 6 | **SQL Safety** | `SQLGlot` | Parses & sanitizes AI-generated SQL (Anti-Injection) |
| 7 | **Image Verification** | `Vision API` | Verifies image-based claims |
| 8 | **Chain-of-Thought** | `Multi-LLM` | Cross-validates reasoning across providers |

---

## 🛡️ QWED-Logic DSL

A secure S-expression based language for logic verification. Replaces unsafe `eval()` with a whitelist-based parser.

```lisp
; Example: Invoice Validation
(AND
  (EQ (PLUS subtotal tax) total)
  (GT invoice_date "2024-01-01")
  (MATCH gst_number "[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}"))
```

---

## 🛠️ Installation & Setup

### 1. Clone & Install
```bash
git clone https://github.com/rahuldass19/qwed-verification.git
cd qwed-verification
pip install -e .
```

### 2. Start PostgreSQL (Docker)
```bash
docker-compose up -d
```

### 3. Configure Environment
Copy `.env.example` to `.env` and fill in your credentials:
```ini
# Database
DATABASE_URL=postgresql://qwed:qwed_secret@localhost:5432/qwed_db

# LLM Provider (Choose one)
ACTIVE_PROVIDER=anthropic

# Anthropic / Claude
ANTHROPIC_ENDPOINT=https://your-endpoint.azure.com/anthropic/
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_DEPLOYMENT=claude-sonnet-4-5

# OR Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4-turbo
```

### 4. Run the API
```bash
uvicorn qwed_new.api.main:app --reload
```
API Docs: http://localhost:8000/docs

---

## 🛡️ Security Features

- **Prompt Injection Detection**: Pre-flight scan of user inputs
- **PII Redaction**: Automatic scrubbing of sensitive data from logs
- **Sandboxed Execution**: Code verification runs in isolated environments
- **OWASP LLM Top 10 2025**: Full compliance

---

## 📚 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Codebase Structure](architecture/CODEBASE_STRUCTURE.md)

---

*Built with ❤️ for a deterministic future.*
