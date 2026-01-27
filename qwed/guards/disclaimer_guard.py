from typing import Dict, Any

class DisclaimerGuard:
    """
    Enforces ethical safety by requiring liability disclaimers in high-stakes domains.
    Prevents authorized advice simulation.
    """
    def __init__(self):
        self.required_phrases = [
            "not a substitute for professional advice",
            "consult a qualified",
            "for informational purposes only",
            "not legal advice",
            "not financial advice",
            "not medical advice"
        ]

    def verify_compliance(self, text: str, domain: str) -> Dict[str, Any]:
        """
        Ensures output contains necessary ethical disclaimers.
        Source: Sri Lanka Legal AI Report.
        """
        if domain.lower() not in ["legal", "medical", "finance"]:
            return {"verified": True}

        text_lower = text.lower()
        has_disclaimer = any(phrase in text_lower for phrase in self.required_phrases)

        if not has_disclaimer:
            return {
                "verified": False,
                "error": "MISSING_DISCLAIMER",
                "message": f"High-stakes output in '{domain}' domain requires a clear liability disclaimer (e.g., 'Not professional advice')."
            }
        
        return {"verified": True}
