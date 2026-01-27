import ast
from typing import Dict, Any, List, Set

class CodeGuard:
    """
    Statically analyzes Python code for security risks using AST.
    Blocks Remote Code Execution (RCE) vectors.
    """
    def __init__(self):
        # Blocklist of dangerous functions and imports
        self.dangerous_functions: Set[str] = {'eval', 'exec', 'compile', 'open', 'system', 'popen'}
        self.dangerous_modules: Set[str] = {'os', 'subprocess', 'sys', 'shutil', 'socket', 'pickle'}

    def verify_safety(self, code_snippet: str) -> Dict[str, Any]:
        """
        Statically analyzes Python code for security risks using AST.
        Source: QWED Core Features
        """
        try:
            tree = ast.parse(code_snippet)
        except SyntaxError as e:
            return {"verified": False, "error": f"Syntax Error: {e}"}

        violations: List[str] = []

        for node in ast.walk(tree):
            # Check for dangerous function calls (e.g., eval())
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in self.dangerous_functions:
                    violations.append(f"Forbidden function call: {node.func.id}()")
            
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
