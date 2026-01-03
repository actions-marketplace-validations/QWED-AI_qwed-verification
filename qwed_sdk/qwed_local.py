"""
QWEDLocal - Client-side verification without backend server.

Works with ANY LLM:
- Ollama (FREE local models)
- OpenAI
- Anthropic
- Google Gemini
- Any OpenAI-compatible API

Example:
    from qwed import QWEDLocal
    
    # Option 1: Ollama (FREE!)
    client = QWEDLocal(
        base_url="http://localhost:11434/v1",
        model="llama3"
    )
    
    # Option 2: OpenAI
    client = QWEDLocal(
        provider="openai",
        api_key="sk-proj-...",
        model="gpt-4o-mini"
    )
    
    result = client.verify("What is 2+2?")
    print(result.verified)  # True
    print(result.value)  # 4
"""

from typing import Optional, Dict, Any, List
import json
from dataclasses import dataclass

# LLM Clients
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Verifiers (bundled with SDK)
try:
    import sympy
    from sympy.parsing.sympy_parser import parse_expr
except ImportError:
    sympy = None

try:
    from z3 import Solver, sat, Bool, Int, Real
except ImportError:
    Solver = None


@dataclass
class VerificationResult:
    """Result from verification."""
    verified: bool
    value: Any = None
    confidence: float = 0.0
    evidence: Dict[str, Any] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.evidence is None:
            self.evidence = {}


class QWEDLocal:
    """
    Client-side LLM verification without backend server.
    
    Privacy-first: Your API key, your data, your machine.
    QWED NEVER sees your queries or responses.
    
    Attributes:
        provider: LLM provider (openai, anthropic, gemini, or None for custom)
        base_url: Custom API endpoint (for Ollama, LM Studio, etc.)
        model: Model name
        api_key: API key for cloud providers
    """
    
    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        **kwargs
    ):
        """
        Initialize QWEDLocal.
        
        Args:
            provider: 'openai', 'anthropic', 'gemini', or None for custom
            api_key: API key for cloud providers (not needed for Ollama)
            base_url: Custom endpoint (e.g., http://localhost:11434/v1 for Ollama)
            model: Model name (e.g., 'llama3', 'gpt-4o-mini', 'claude-3-opus')
            **kwargs: Additional arguments for LLM client
        
        Examples:
            # Ollama (FREE)
            client = QWEDLocal(
                base_url="http://localhost:11434/v1",
                model="llama3"
            )
            
            # OpenAI
            client = QWEDLocal(
                provider="openai",
                api_key="sk-...",
                model="gpt-4o-mini"
            )
            
            # Anthropic
            client = QWEDLocal(
                provider="anthropic",
                api_key="sk-ant-...",
                model="claude-3-opus"
            )
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        
        # Initialize LLM client
        self._init_llm_client(**kwargs)
        
        # Check verifiers available
        self._check_verifiers()
    
    def _init_llm_client(self, **kwargs):
        """Initialize the appropriate LLM client."""
        
        # Custom endpoint (Ollama, LM Studio, etc.)
        if self.base_url:
            if OpenAI is None:
                raise ImportError("openai package required. Install: pip install openai")
            
            self.llm_client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key or "dummy",  # Ollama doesn't need real key
                **kwargs
            )
            self.client_type = "openai"
        
        # OpenAI
        elif self.provider == "openai":
            if OpenAI is None:
                raise ImportError("openai package required. Install: pip install openai")
            if not self.api_key:
                raise ValueError("api_key required for OpenAI")
            
            self.llm_client = OpenAI(api_key=self.api_key, **kwargs)
            self.client_type = "openai"
        
        # Anthropic
        elif self.provider == "anthropic":
            if Anthropic is None:
                raise ImportError("anthropic package required. Install: pip install anthropic")
            if not self.api_key:
                raise ValueError("api_key required for Anthropic")
            
            self.llm_client = Anthropic(api_key=self.api_key, **kwargs)
            self.client_type = "anthropic"
        
        # Gemini
        elif self.provider == "gemini":
            if genai is None:
                raise ImportError("google-generativeai package required. Install: pip install google-generativeai")
            if not self.api_key:
                raise ValueError("api_key required for Gemini")
            
            genai.configure(api_key=self.api_key)
            self.llm_client = genai.GenerativeModel(self.model)
            self.client_type = "gemini"
        
        else:
            raise ValueError(
                "Must specify either 'provider' (openai/anthropic/gemini) "
                "or 'base_url' for custom endpoints"
            )
    
    def _check_verifiers(self):
        """Check which verifiers are available."""
        self.has_sympy = sympy is not None
        self.has_z3 = Solver is not None
        
        if not self.has_sympy:
            print("⚠️  SymPy not found. Math verification disabled. Install: pip install sympy")
        if not self.has_z3:
            print("⚠️  Z3 not found. Logic verification disabled. Install: pip install z3-solver")
    
    def _call_llm(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Call the LLM with a prompt.
        
        This is the ONLY place where user data touches the LLM.
        No data is sent to QWED servers!
        """
        
        if self.client_type == "openai":
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.0  # Deterministic for verification
            )
            return response.choices[0].message.content
        
        elif self.client_type == "anthropic":
            response = self.llm_client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
                system=system or ""
            )
            return response.content[0].text
        
        elif self.client_type == "gemini":
            response = self.llm_client.generate_content(prompt)
            return response.text
        
        else:
            raise NotImplementedError(f"Client type {self.client_type} not implemented")
    
    def verify(self, query: str) -> VerificationResult:
        """
        Verify any query (auto-detects type).
        
        Args:
            query: Natural language query
        
        Returns:
            VerificationResult with verified status
        
        Example:
            result = client.verify("What is 2+2?")
            print(result.verified)  # True
            print(result.value)  # 4
        """
        # TODO: Auto-detect query type (math, logic, code, etc.)
        # For now, try math verification
        return self.verify_math(query)
    
    def verify_math(self, query: str) -> VerificationResult:
        """
        Verify mathematical query.
        
        Uses SymPy for symbolic verification.
        """
        if not self.has_sympy:
            return VerificationResult(
                verified=False,
                error="SymPy not installed. Run: pip install sympy"
            )
        
        # Step 1: Ask LLM for answer
        prompt = f"""Solve this math problem and respond ONLY with the numerical answer:

{query}

Answer (number only):"""
        
        try:
            llm_response = self._call_llm(prompt)
            llm_answer = llm_response.strip()
            
            # Step 2: Ask LLM for symbolic expression
            expr_prompt = f"""Convert this to a SymPy expression that we can verify:

{query}

Respond with ONLY the Python SymPy code to evaluate this, nothing else.
Example: "sympy.simplify(2+2)" or "sympy.diff(x**2, x)"

SymPy code:"""
            
            llm_expr = self._call_llm(expr_prompt)
            
            # Step 3: Verify with SymPy
            # Parse and evaluate the expression
            # (In production, use safe eval with restricted namespace)
            local_vars = {"sympy": sympy, "x": sympy.Symbol('x')}
            
            try:
                verified_result = eval(llm_expr.strip(), {"__builtins__": {}}, local_vars)
                verified_value = str(verified_result)
                
                # Compare LLM answer with verified result
                is_correct = str(llm_answer) == verified_value
                
                return VerificationResult(
                    verified=is_correct,
                    value=verified_value,
                    confidence=1.0 if is_correct else 0.0,
                    evidence={
                        "llm_answer": llm_answer,
                        "verified_value": verified_value,
                        "sympy_expr": llm_expr.strip(),
                        "method": "sympy_eval"
                    }
                )
            
            except Exception as e:
                return VerificationResult(
                    verified=False,
                    error=f"SymPy verification failed: {str(e)}",
                    evidence={
                        "llm_answer": llm_answer,
                        "llm_expr": llm_expr
                    }
                )
        
        except Exception as e:
            return VerificationResult(
                verified=False,
                error=f"LLM call failed: {str(e)}"
            )
    
    def verify_logic(self, query: str) -> VerificationResult:
        """
        Verify logical query.
        
        Uses Z3 for SAT solving.
        """
        if not self.has_z3:
            return VerificationResult(
                verified=False,
                error="Z3 not installed. Run: pip install z3-solver"
            )
        
        # TODO: Implement Z3 verification
        return VerificationResult(
            verified=False,
            error="Logic verification not yet implemented"
        )
    
    def verify_code(self, code: str, language: str = "python") -> VerificationResult:
        """
        Verify code for security issues.
        
        Uses AST analysis.
        """
        # TODO: Implement AST-based code verification
        return VerificationResult(
            verified=False,
            error="Code verification not yet implemented"
        )


# Convenience function
def verify(query: str, **kwargs) -> VerificationResult:
    """
    Quick verification without creating client.
    
    Uses Ollama by default if available, falls back to requiring API key.
    
    Example:
        result = verify("What is 2+2?")
        print(result.value)  # 4
    """
    # Try Ollama first (FREE!)
    try:
        client = QWEDLocal(
            base_url="http://localhost:11434/v1",
            model=kwargs.get("model", "llama3")
        )
        return client.verify(query)
    except Exception:
        # Ollama not available, require explicit configuration
        raise ValueError(
            "Ollama not running. Either:\n"
            "1. Start Ollama: ollama serve\n"
            "2. Or specify provider explicitly:\n"
            "   verify(query, provider='openai', api_key='sk-...')"
        )
