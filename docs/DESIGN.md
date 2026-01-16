# QWED Design Decisions

**Last updated:** January 2026  
**Purpose:** Document the human architectural decisions, trade-offs, and design thinking behind QWED

---

## Core Philosophy

> **"Don't reduce hallucinations. Make them irrelevant."**

Large Language Models (LLMs) are probabilistic and will always hallucinate. Rather than trying to fix the LLM, QWED verifies its outputs using deterministic solvers. The LLM becomes an **untrusted translator**, not a trusted computer.

---

## Architecture: The Untrusted Translator Pattern

### The Problem

**Traditional approach:** Trust the LLM to compute correctly
- Train it better (fine-tuning)
- Give it more context (RAG)
- Ask it to check itself (LLM-as-judge)

**Why this fails:** LLMs are fundamentally probabilistic. No amount of training guarantees correctness.

### The QWED Solution

**Separation of concerns:**
1. **LLM:** Translates natural language → formal specification
2. **Symbolic Solver:** Verifies the formal specification deterministically

```
User: "What is the derivative of x²?"
  ↓
LLM: Translates to → diff(x**2, x)
  ↓
SymPy: Computes → 2*x (proven correct)
  ↓
QWED: Returns verified result
```

**Key insight:** LLMs are good at translation, terrible at computation. Use them for what they're good at.

---

## Design Decision 1: Multiple Specialized Engines

### The Trade-off

**Option A: Single general-purpose verifier**
- Pros: Simpler architecture, one dependency
- Cons: No general verifier matches domain-specific tools

**Option B: Multiple domain-specific engines** ← **CHOSEN**
- Pros: Each domain uses decades of specialized research
- Cons: More complex architecture, multiple dependencies

### The Decision

**Chosen:** Multiple specialized engines

**Engines:**
- **SymPy** (math): Symbolic algebra, calculus, linear algebra
- **Z3** (logic): SAT/SMT solving, formal verification
- **AST** (code): Static analysis, syntax validation
- **SQLGlot** (SQL): Query parsing and validation
- **NLI + TF-IDF** (facts): Grounding against source documents

**Rationale:** Each domain has specialized tools refined over decades. No general-purpose verifier can match the precision of SymPy for calculus or Z3 for logic. Better to integrate experts than build a generalist.

---

## Design Decision 2: TF-IDF for Fact Grounding

### The Trade-off

**Option A: Vector embeddings (semantic similarity)**
- Pros: Captures semantic meaning, state-of-the-art
- Cons: Probabilistic, can match opposite meanings

**Option B: TF-IDF (lexical matching)** ← **CHOSEN**
- Pros: Deterministic, reproducible, searches for evidence
- Cons: Doesn't capture semantic similarity

### The Decision

**Chosen:** TF-IDF for evidence retrieval

**Example of the problem with embeddings:**
```python
query1 = "The Earth orbits the Sun"
query2 = "The Sun orbits the Earth"

# Embeddings similarity: 0.92 (HIGH!)
# Meaning: Completely opposite
```

**TF-IDF advantage:** Searches for actual word evidence, not "vibes"

**Academic validation:** 10+ papers (2018-2025) from AAAI, ACL, Neurocomputing use TF-IDF for fact verification (FEVER dataset, etc.)

**Use case:** For verification, you need **evidence-based grounding**, not semantic similarity.

---

## Design Decision 3: LLM-as-Translator vs LLM-as-Judge

### The Trade-off

**Option A: LLM-as-judge** (e.g., GPT-4 checks GPT-3.5)
- Pros: Uses latest models, easy to implement
- Cons: Both models probabilistic → recursive hallucination

**Option B: Solver-as-judge** ← **CHOSEN**
- Pros: Deterministic, mathematical proof
- Cons: Limited to verifiable domains

### The Decision

**Chosen:** Symbolic solver as judge

**Comparison:**

| Approach | Judge | Guarantee | Example |
|----------|-------|-----------|---------|
| LLM-as-judge | GPT-4 | Probabilistic | "Probably correct" |
| QWED | SymPy/Z3 | Mathematical proof | "Provably correct" |

**Rationale:** If both judge and generator are probabilistic, errors compound. Need deterministic judge for verification.

**Limitation acknowledged:** Only works for mathematically verifiable domains (math, logic, syntax). Not for creative writing or subjective content.

---

## Design Decision 4: API Design Philosophy

### The Trade-off

**Option A: Low-level API** (expose all solver internals)
- Pros: Maximum flexibility
- Cons: Steep learning curve, users need solver expertise

**Option B: High-level developer-friendly API** ← **CHOSEN**
- Pros: Easy to use, hides complexity
- Cons: Less control over solver behavior

### The Decision

**Chosen:** High-level, developer-friendly API

**Design principles:**
1. **Single method per domain:** `verify_math()`, `verify_logic()`, `verify_code()`
2. **Smart routing:** Auto-detect domain from query
3. **Rich error messages:** Explain what failed and why
4. **Fallback values:** Graceful degradation on verification failure

**Example:**
```python
# User doesn't need to know about SymPy internals
result = client.verify_math("What is 2+2?")
print(result.verified)  # True
print(result.value)  # 4
```

**Rationale:** Developers shouldn't need to learn SymPy, Z3, AST separately. QWED provides a unified interface.

---

## Design Decision 5: Integration Patterns

### The Trade-off

**Option A: Standalone verification service**
- Pros: Clean separation
- Cons: Hard to integrate with existing LLM workflows

**Option B: Framework integrations** ← **CHOSEN**
- Pros: Drops into LangChain, LlamaIndex, etc.
- Cons: More maintenance, framework dependencies

### The Decision

**Chosen:** Native integrations with popular frameworks

**Integrations:**
- **LangChain:** `QWEDTool` as native LangChain tool
- **LlamaIndex:** Query engine wrapper
- **Direct API:** For custom workflows

**Rationale:** Developers already use LangChain/LlamaIndex. QWED should integrate seamlessly rather than forcing workflow changes.

---

## Design Decision 6: Error Handling Philosophy

### The Trade-off

**Option A: Fail fast** (reject on any error)
- Pros: Safe, conservative
- Cons: Breaks user experience

**Option B: Graceful degradation with audit trails** ← **CHOSEN**
- Pros: Better UX, transparent failures
- Cons: Users might miss errors

### The Decision

**Chosen:** Graceful degradation with comprehensive logging

**Pattern:**
```python
try:
    result = verify_math(query, llm_output)
except VerificationError as e:
    log_error(e, audit_trail=True)
    return fallback_value  # User-defined
```

**Features:**
- **Audit trails:** Log every verification attempt
- **Retry with exponential backoff:** Handle transient LLM errors
- **Alert systems:** Notify on repeated failures
- **Fallback values:** User-defined safe defaults

**Rationale:** Production systems need resilience. Total failure is worse than controlled degradation with visibility.

---

## Design Decision 7: PII Masking Strategy

### The Trade-off

**Option A: No PII handling** (user responsibility)
- Pros: Simpler architecture
- Cons: Privacy risk, compliance issues

**Option B: Built-in PII masking** ← **CHOSEN**
- Pros: HIPAA/GDPR compliance, privacy by default
- Cons: Performance overhead, false positives

### The Decision

**Chosen:** Optional built-in PII masking

**Implementation:**
- Uses Microsoft Presidio for entity detection
- Masks before sending to LLM
- Unmasks in verification step
- Logs PII detection events

**Rationale:** Healthcare, finance, legal sectors require PII protection. Making it built-in lowers adoption barrier for regulated industries.

---

## Design Decision 8: Calculator vs Wikipedia Analogy

### The Mental Model

**Why this matters:** Helps users understand QWED's scope

**Calculator (Deterministic):**
- Input: 2 + 2
- Output: 4 (always)
- Verifiable: ✅

**Wikipedia (Knowledge Base):**
- Input: "Who is the president?"
- Output: Depends on edit history
- Verifiable: ❌ (subjective, changes)

**QWED is a calculator, not Wikipedia:**
- ✅ Math: Provable
- ✅ Logic: Provable
- ✅ Code syntax: Provable
- ❌ Opinions: Not provable
- ❌ Creative content: Not provable

---

## What QWED Is NOT

### Rejected Design Paths

**1. Novel Research**
- **Not claiming:** New verification algorithms
- **Claiming:** Practical integration of existing solvers

**2. LLM Improvement**
- **Not claiming:** Making LLMs more accurate
- **Claiming:** Catching LLM errors deterministically

**3. General AI Safety**
- **Not claiming:** Solving jailbreaks, toxicity, bias
- **Claiming:** Verifying mathematical/logical correctness

---

## Development Transparency

### AI Assistance

This project was developed with assistance from generative AI tools:

**Tools used:**
- **Antigravity IDE** with **Claude Sonnet 4.5**
- **Scope:** Code implementation, documentation, test generation

**Human contributions:**
- All architectural decisions documented above
- Trade-off analysis and solver selection
- API design and integration patterns
- Error handling philosophy
- Domain modeling and verification workflows

**Validation:** All AI-generated code was reviewed, tested against benchmarks, and validated through comprehensive testing.

---

## Lessons Learned

### What Worked

1. **Specialized engines:** Better than trying to build one general verifier
2. **Developer-friendly API:** Easier adoption than low-level solver access
3. **TF-IDF for grounding:** Deterministic evidence > semantic vibes
4. **Open development:** Community contributions improved design

### What We'd Change

1. **Earlier framework integrations:** Should have built LangChain support sooner
2. **More domain tutorials:** Users needed more examples per domain
3. **Clearer scope communication:** "Calculator not Wikipedia" analogy should be upfront

---

## References

**Academic validation for design decisions:**

1. **TF-IDF for fact verification:**
   - FEVER Shared Task (2018): Fact verification benchmark
   - AAAI 2019: Combining fact extraction and verification
   - Neurocomputing 2023: Information retrieval for fact-checking

2. **Neurosymbolic AI:**
   - Kautz (2020): The third AI summer
   - Marcus (2020): The next decade in AI

3. **LLM verification challenges:**
   - Ji et al. (2023): Survey of hallucination in NLP
   - OpenAI (2023): GPT-4 technical report

---

## Contributing to Design

Have suggestions on design improvements? Open an issue on GitHub to discuss!

**Questions welcome:**
- Why this solver over alternatives?
- Trade-offs we should reconsider?
- New design patterns?

GitHub Discussions: https://github.com/QWED-AI/qwed-verification/discussions
