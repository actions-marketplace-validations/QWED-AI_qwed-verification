import sympy
from sympy.parsing.sympy_parser import parse_expr
from typing import Any, Dict, Optional
from decimal import Decimal, ROUND_HALF_UP

class VerificationEngine:
    """
    The deterministic core. It does not guess. It calculates.
    Uses Symbolic Math (SymPy) to verify mathematical assertions.
    
    Updated: Now uses Decimal for financial precision.
    """
    
    def verify_math(
        self, 
        expression: str, 
        expected_value: float, 
        tolerance: float = 1e-6,
        use_decimal: bool = True
    ) -> Dict[str, Any]:
        """
        Verifies if a mathematical expression evaluates to the expected value.
        
        Args:
            expression: The math string (e.g., "2 * (5 + 10)")
            expected_value: The value the LLM claims it is (e.g., 30)
            tolerance: Floating point tolerance
            use_decimal: If True, use Decimal for exact arithmetic (financial)
            
        Returns:
            Dict containing is_correct, calculated_value, and error_margin.
        """
        try:
            # 1. Parse the expression safely
            expr = parse_expr(expression)
            
            # 2. Evaluate deterministically
            if use_decimal:
                # Use Decimal for financial precision
                # Convert to string first to avoid float precision loss
                raw_value = expr.evalf()
                calculated_value = Decimal(str(raw_value)).quantize(
                    Decimal("0.000001"),  # 6 decimal places
                    rounding=ROUND_HALF_UP
                )
                expected_decimal = Decimal(str(expected_value))
                
                # 3. Compare with Decimal
                diff = abs(calculated_value - expected_decimal)
                is_correct = diff <= Decimal(str(tolerance))
                
                return {
                    "is_correct": is_correct,
                    "calculated_value": float(calculated_value),  # Convert back for API
                    "calculated_precise": str(calculated_value),  # Keep precision
                    "claimed_value": expected_value,
                    "diff": float(diff),
                    "precision_mode": "decimal",
                    "status": "VERIFIED" if is_correct else "CORRECTION_NEEDED"
                }
            else:
                # Legacy float mode
                calculated_value = float(expr.evalf())
                diff = abs(calculated_value - expected_value)
                is_correct = diff <= tolerance
                
                return {
                    "is_correct": is_correct,
                    "calculated_value": calculated_value,
                    "claimed_value": expected_value,
                    "diff": diff,
                    "precision_mode": "float",
                    "status": "VERIFIED" if is_correct else "CORRECTION_NEEDED"
                }
            
        except Exception as e:
            return {
                "is_correct": False,
                "error": str(e),
                "status": "SYNTAX_ERROR"
            }

    def verify_logic_rule(self, rule: str, context: Dict[str, Any]) -> bool:
        """
        Placeholder for logical verification (e.g., "If Age < 18, Risk = High")
        """
        # This would use a logic solver like Z3 in the future
        pass
