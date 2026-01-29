import ast
from typing import Dict, Any, List, Set

class CodeGuard:
    """
    Statically analyzes Python code for security risks using AST.
    Blocks Remote Code Execution (RCE) vectors.
    """
    def __init__(self):
        # Blocklist of dangerous functions and imports
        self.dangerous_functions: Set[str] = {'eval', 'exec', 'compile', 'open', 'system', 'popen', '__import__', 'spawn'}
        self.dangerous_modules: Set[str] = {'os', 'subprocess', 'sys', 'shutil', 'socket', 'pickle', 'pty'}

    def verify_safety(self, code_snippet: str, language: str = "python") -> Dict[str, Any]:
        """
        Statically analyzes code for security risks.
        Supports: Python (AST), Bash (Regex/Heuristics)
        """
        # Normalize language
        lang = language.lower()

        if lang in ["bash", "sh", "shell"]:
            return self._verify_bash(code_snippet)
        
        # Default to Python AST
        try:
            tree = ast.parse(code_snippet)
        except SyntaxError as e:
            # If it looks like bash but was passed as python, give a hint
            if "curl" in code_snippet or "wget" in code_snippet:
                return {"verified": False, "error": "Syntax Error: Code appears to be Shell/Bash but parsed as Python. Specify language='bash'."}
            return {"verified": False, "error": f"Syntax Error: {e}"}

        violations: List[str] = []

        for node in ast.walk(tree):
            # Check for dangerous function calls (e.g., eval())
            if isinstance(node, ast.Call):
                # Direct calls: eval()
                if isinstance(node.func, ast.Name) and node.func.id in self.dangerous_functions:
                    violations.append(f"Forbidden function call: {node.func.id}()")
                # Method calls: os.system()
                elif isinstance(node.func, ast.Attribute) and node.func.attr in self.dangerous_functions:
                    violations.append(f"Forbidden method call: .{node.func.attr}()")
            
            # Check for dangerous imports (e.g., import os)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.dangerous_modules:
                        violations.append(f"Forbidden import: {alias.name}")
            
            # Check for dangerous 'from X import Y'
            elif isinstance(node, ast.ImportFrom):
                if node.module in self.dangerous_modules:
                    violations.append(f"Forbidden import from: {node.module}")
        
        if violations:
            return {
                "verified": False,
                "risk": "SECURITY_VULNERABILITY",
                "violations": violations,
                "message": f"Security Violations Found: {', '.join(violations)}"
            }

        return {
            "verified": True,
            "scan_method": "AST_STATIC_ANALYSIS",
            "message": "Code structure verified safe (No dangerous imports/functions)."
        }

    def _verify_bash(self, code: str) -> Dict[str, Any]:
        """Verify Bash/Shell commands using regex patterns."""
        import re
        
        dangerous_patterns = [
            (r"(?:curl|wget)\s+.*(?:\||&&|;)\s*(?:bash|sh|python|perl|ruby|php)", "Remote Code Execution (RCE) chain detected"),
            (r"rm\s+-rf", "Destructive command (rm -rf)"),
            (r":\(\)\{\s*:\|:\&\s*\}\;", "Fork Bomb detected"),
            (r"nc\s+", "Netcat usage detected (Data Exfiltration/Reverse Shell Risk)"),
            (r"netcat\s+", "Netcat usage detected"),
            (r"/dev/tcp/", "Direct TCP connection (Reverse Shell Risk)"),
            (r"/etc/passwd", "Sensitive file access (/etc/passwd)"),
            (r"/etc/shadow", "Sensitive file access (/etc/shadow)"),
            (r"id_rsa", "SSH Private Key access detected"),
            (r"printenv", "Environment Variable Dumping detected"),
            (r"grep\s+.*(?:pass|token|key|secret)", "Credential Hunting (grep for secrets) detected"),
            (r"base64\s+-d", "Base64 Decoding (Obfuscation Risk)"),
            (r"chmod\s+777", "Insecure permissions (chmod 777)"),
            (r"sudo\s+", "Privilege Escalation attempt (sudo)"),
        ]

        violations = []
        for pattern, desc in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                violations.append(desc)
        
        if violations:
            return {
                "verified": False,
                "risk": "SHELL_INJECTION_RISK",
                "violations": violations,
                "message": f"Shell Violations: {', '.join(violations)}"
            }
            
        return {
            "verified": True,
            "scan_method": "REGEX_HEURISTICS",
            "message": "Shell command verified safe."
        }
