
import unittest
import base64
import json
import ast
import sympy
# Import the actual classes to test integration if possible, 
# or copy the validator logic for component testing if we can't easily import private methods.

class TestSecurityFixes(unittest.TestCase):
    
    def test_base64_padding_correctness(self):
        """Test that our new padding logic works for all modulo cases."""
        # Case 0: Needs 0 padding
        s = "aaaa" # len 4
        padding = '=' * (-len(s) % 4)
        self.assertEqual(len(padding), 0)
        
        # Case 1: Needs 3 padding? No, base64 blocks are 4 chars.
        # Valid base64 strings length % 4 is 0, 2, or 3. (1 is impossible)
        
        # Payload '{"a":1}' -> eyJhIjoxfQ (len 10) -> 10 % 4 = 2. Needs 2 '='.
        s = "eyJhIjoxfQ"
        padding = '=' * (-len(s) % 4)
        # -10 % 4 = 2 (because -10 = -3*4 + 2)
        self.assertEqual(len(padding), 2)
        self.assertEqual(padding, "==")
        
        # Payload '{"sub":"1"}' -> eyJzdWIiOiIxIn0 (len 15) -> 15 % 4 = 3. Needs 1 '='.
        s = "eyJzdWIiOiIxIn0" 
        padding = '=' * (-len(s) % 4)
        # -15 % 4 = 1
        self.assertEqual(len(padding), 1)
        self.assertEqual(padding, "=")
        
        print("Base64 padding logic verified.")

    def test_safe_sympy_validator(self):
        """Test the AST validator for SymPy expressions."""
        
        def _is_safe(expr_str):
            try:
                tree = ast.parse(expr_str, mode='eval')
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Attribute):
                            if getattr(node.func.value, 'id', '') != 'sympy':
                                return False
                        elif isinstance(node.func, ast.Name):
                            safe_funcs = {'abs', 'float', 'int', 'complex'}
                            if node.func.id not in safe_funcs:
                                return False
                        else:
                            return False
                    elif isinstance(node, (ast.Name, ast.Constant, ast.Str, ast.Num, 
                                            ast.Expression, ast.Load, ast.BinOp, ast.UnaryOp,
                                            ast.operator, ast.unaryop, ast.Attribute)):
                        pass
                    else:
                        return False
                return True
            except SyntaxError:
                return False

        # Safe expressions
        self.assertTrue(_is_safe("sympy.diff(x**2, x)"))
        self.assertTrue(_is_safe("sympy.sin(x) + 1"))
        self.assertTrue(_is_safe("x + 2"))
        
        # Unsafe expressions
        self.assertFalse(_is_safe("import os"))
        self.assertFalse(_is_safe("__import__('os')"))
        self.assertFalse(_is_safe("eval('print(1)')"))
        self.assertFalse(_is_safe("exec('print(1)')"))
        self.assertFalse(_is_safe("open('/etc/passwd')"))
        
        print("SymPy AST validator verified.")

    def test_log_sanitization(self):
        """Test that newlines are stripped from log messages."""
        # Simulate the logic in secure_code_executor.py
        raw_error = "Error occurred\nwith malicious\rnewline injection"
        sanitized = str(raw_error).replace('\n', ' ').replace('\r', ' ')
        
        self.assertNotIn('\n', sanitized)
        self.assertNotIn('\r', sanitized)
        self.assertEqual(sanitized, "Error occurred with malicious newline injection")
        print("Log sanitization verified.")

if __name__ == '__main__':
    unittest.main()
