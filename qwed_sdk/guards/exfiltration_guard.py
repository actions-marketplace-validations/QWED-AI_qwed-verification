"""
ExfiltrationGuard: Runtime Data Exfiltration Protection.

Prevents compromised agents from sending sensitive data (PII, credentials,
internal documents) to unauthorized endpoints. Acts as a runtime control
policy layer between the agent's tool calls and external APIs.

Addresses the "if the agent does get tricked" scenario — even if an MCP
tool or prompt injection succeeds, the data cannot leave your infrastructure.
"""
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse


# --- PII Detection Patterns ---

_PII_PATTERNS: Dict[str, re.Pattern] = {
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "CREDIT_CARD": re.compile(
        r"\b(?:4[0-9]{12}(?:[0-9]{3})?|"           # Visa
        r"5[1-5][0-9]{14}|"                         # MasterCard
        r"3[47][0-9]{13}|"                          # Amex
        r"6(?:011|5[0-9]{2})[0-9]{12})\b"           # Discover
    ),
    "EMAIL": re.compile(
        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b"
    ),
    "PHONE_US": re.compile(
        r"\b(?:\+1\s?)?(?:\(\d{3}\)|\d{3})[\s.\-]?\d{3}[\s.\-]?\d{4}\b"
    ),
    # PASSPORT: opt-in only — too broad by default (matches version strings etc.)
    # Enable via pii_checks=[..., 'PASSPORT'] in ExfiltrationGuard.__init__
    "PASSPORT": re.compile(r"\b(?:passport\s*(?:no|number|#)?[:\s]+)?[A-Z]{1,2}[0-9]{6,9}\b", re.IGNORECASE),
    "IBAN": re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}(?:[A-Z0-9]?){0,16}\b"),
    "AWS_ACCESS_KEY": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "PRIVATE_KEY": re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
    "JWT": re.compile(r"\beyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+\b"),
    "BEARER_TOKEN": re.compile(r"Bearer\s+[a-zA-Z0-9_.\-]{20,}", re.IGNORECASE),
}


class ExfiltrationGuard:
    """
    Deterministic guard for runtime data exfiltration prevention.

    Verifies outbound agent API calls against:
    1. An endpoint allowlist (blocks calls to unauthorized destinations)
    2. A PII scanner (blocks payloads containing sensitive data)

    Example::

        guard = ExfiltrationGuard(
            allowed_endpoints=["https://api.openai.com", "https://api.anthropic.com"]
        )
        result = guard.verify_outbound_call(
            destination_url="https://evil-server.com/collect",
            payload="User SSN: 123-45-6789"
        )
        # result["verified"] == False, result["risk"] == "DATA_EXFILTRATION"
    """

    def __init__(
        self,
        allowed_endpoints: Optional[List[str]] = None,
        pii_checks: Optional[List[str]] = None,
        custom_pii_patterns: Optional[Dict[str, str]] = None,
    ):
        """
        Args:
            allowed_endpoints: URL prefixes or hostnames that agents are
                permitted to call. Supports prefix matching
                (``"https://api.openai.com"``) or hostname-only
                (``"api.openai.com"``). If None, all endpoints are blocked
                except localhost.
            pii_checks: List of PII type names to check from the built-in
                set. Defaults to all. Options: ``SSN``, ``CREDIT_CARD``,
                ``EMAIL``, ``PHONE_US``, ``PASSPORT``, ``IBAN``,
                ``AWS_ACCESS_KEY``, ``PRIVATE_KEY``, ``JWT``, ``BEARER_TOKEN``.
            custom_pii_patterns: Additional ``{name: regex_string}`` patterns
                to scan for.
        """
        self.allowed_endpoints: List[str] = allowed_endpoints or [
            "https://api.openai.com",
            "https://api.anthropic.com",
            "https://generativelanguage.googleapis.com",
            "http://localhost",
            "http://127.0.0.1",
        ]

        # Build active PII patterns
        # Default checks exclude PASSPORT (too broad, opt-in only)
        _DEFAULT_CHECKS = {k for k in _PII_PATTERNS if k != "PASSPORT"}
        if pii_checks is not None:
            active_pii = {k: v for k, v in _PII_PATTERNS.items() if k in pii_checks}
        else:
            active_pii = {k: v for k, v in _PII_PATTERNS.items() if k in _DEFAULT_CHECKS}
        if custom_pii_patterns:
            for name, pattern_str in custom_pii_patterns.items():
                active_pii[name] = re.compile(pattern_str)
        self._pii_patterns = active_pii

    def _is_allowed_endpoint(self, url: str) -> bool:
        """Check if URL matches any allowed endpoint prefix or hostname."""
        url_lower = url.lower()
        try:
            parsed_host = urlparse(url).hostname or ""
        except ValueError:
            return False

        for allowed in self.allowed_endpoints:
            allowed_lower = allowed.lower()
            # Prefix match — require path boundary to prevent
            # 'https://api.openai.com.evil.com' bypassing the allowlist
            if url_lower.startswith(allowed_lower):
                rest = url_lower[len(allowed_lower):]
                if not rest or rest[0] in ('/', '?', '#', ':'):
                    return True
            # Hostname-only match (e.g. "api.openai.com")
            try:
                allowed_host = urlparse(allowed).hostname or allowed_lower
            except ValueError:
                allowed_host = allowed_lower
            if parsed_host == allowed_host or parsed_host.endswith(f".{allowed_host}"):
                return True
        return False

    def verify_outbound_call(
        self,
        destination_url: str,
        payload: str = "",
        method: str = "POST",
    ) -> Dict[str, Any]:
        """
        Verify an outbound API call before execution.

        Args:
            destination_url: The full URL the agent is attempting to call.
            payload: The request body / payload (string or JSON-encoded).
            method: HTTP method (for logging). Default: ``"POST"``.

        Returns:
            ``{"verified": True, "destination": url}`` on success, or
            ``{"verified": False, "risk": str, "message": str}`` on failure.
        """
        if not destination_url:
            return {
                "verified": False,
                "risk": "EMPTY_DESTINATION",
                "message": "Outbound call has no destination URL.",
            }

        # 1. Endpoint allowlist check
        if not self._is_allowed_endpoint(destination_url):
            return {
                "verified": False,
                "risk": "DATA_EXFILTRATION",
                "destination": destination_url,
                "message": (
                    f"Agent attempted to send data to unauthorized endpoint: "
                    f"{destination_url}. Call blocked by ExfiltrationGuard."
                ),
            }

        # 2. PII scan on payload
        if payload:
            pii_hits = self._scan_payload_for_pii(payload)
            if pii_hits:
                pii_types = ", ".join(hit["type"] for hit in pii_hits)
                return {
                    "verified": False,
                    "risk": "PII_LEAK",
                    "destination": destination_url,
                    "pii_detected": pii_hits,
                    "message": (
                        f"Blocked: Payload destined for '{destination_url}' "
                        f"contains unmasked PII: {pii_types}. "
                        "Mask or redact before sending."
                    ),
                }

        return {
            "verified": True,
            "destination": destination_url,
            "method": method,
            "message": f"Outbound {method} to '{destination_url}' approved.",
        }

    def _scan_payload_for_pii(self, payload: str) -> List[Dict[str, Any]]:
        """Scan payload string for PII matches. Returns list of findings."""
        findings: List[Dict[str, Any]] = []
        for pii_type, pattern in self._pii_patterns.items():
            matches = pattern.findall(payload)
            if matches:
                findings.append({
                    "type": pii_type,
                    "count": len(matches),
                    "message": f"Found {len(matches)} instance(s) of {pii_type}.",
                })
        return findings

    def scan_payload(self, payload: str) -> Dict[str, Any]:
        """
        Standalone PII scan without endpoint check.

        Useful for scanning LLM outputs before storing or forwarding them.

        Args:
            payload: String content to scan.

        Returns:
            ``{"verified": True}`` or
            ``{"verified": False, "risk": "PII_DETECTED", "pii_detected": [...]}``.
        """
        findings = self._scan_payload_for_pii(payload)
        if findings:
            pii_types = ", ".join(f["type"] for f in findings)
            return {
                "verified": False,
                "risk": "PII_DETECTED",
                "pii_detected": findings,
                "message": f"Payload contains unmasked PII: {pii_types}.",
            }
        return {"verified": True, "message": "No PII detected in payload."}
