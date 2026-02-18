
import unittest
import base64
from unittest.mock import patch, MagicMock
from src.qwed_new.core.attestation import AttestationService, VerificationResult, create_verification_attestation, HAS_CRYPTO

class TestAttestationCoverage(unittest.TestCase):
    """Targeted tests to improve coverage of attestation.py"""

    def setUp(self):
        if not HAS_CRYPTO:
            self.skipTest("Cryptography not available")
        self.service = AttestationService(issuer_did="did:test:123", key_suffix="test")

    def test_invalid_token_format_not_json(self):
        """Test handling of tokens with non-JSON payloads."""
        # Create a malformed token: header.payload.signature
        # Payload is base64 encoded "not json"
        header = "eyJhbGciOiJFUzI1NiJ9" # {"alg":"ES256"}
        payload = base64.urlsafe_b64encode(b"not json").decode().rstrip("=")
        token = f"{header}.{payload}.signature"
        
        is_valid, _, error = self.service.verify_attestation(token)
        self.assertFalse(is_valid)
        self.assertIn("Invalid token format", error)

    def test_untrusted_issuer(self):
        """Test verification with an untrusted issuer."""
        # We need a valid JWT structure but with a diff issuer
        # Function internal logic checks issuer before signature, so we can mock the decode
        
        # 1. Create a token with a different issuer
        other_service = AttestationService(issuer_did="did:malicious:999", key_suffix="evil")
        result = VerificationResult(status="fake", verified=True, engine="fake")
        attestation = other_service.create_attestation(result, "query")
        
        # 2. Verify with our service (which trusts "did:test:123" by default)
        is_valid, _, error = self.service.verify_attestation(attestation.jwt_token)
        
        self.assertFalse(is_valid)
        self.assertIn("Untrusted issuer", error)

    def test_revoked_attestation(self):
        """Test verification of a revoked attestation."""
        result = VerificationResult(status="ok", verified=True, engine="test")
        attestation = self.service.create_attestation(result, "query")
        
        # Revoke it
        self.service.revoke_attestation(attestation.claims.jti)
        
        # Verify
        is_valid, _, error = self.service.verify_attestation(attestation.jwt_token)
        self.assertFalse(is_valid)
        self.assertIn("revoked", error)

    def test_create_verification_attestation_helper(self):
        """Test the convenience function."""
        # Mock get_attestation_service to return our service
        with patch("src.qwed_new.core.attestation.get_attestation_service", return_value=self.service):
            token = create_verification_attestation(
                status="verified",
                verified=True, 
                engine="test_engine",
                query="test query"
            )
            self.assertIsNotNone(token)
            
            # Verify it's valid
            is_valid, claims, _ = self.service.verify_attestation(token)
            self.assertTrue(is_valid)
            self.assertEqual(claims["qwed"]["result"]["engine"], "test_engine")

    def test_create_verification_attestation_helper_failure(self):
        """Test the convenience function handles exceptions."""
        with patch("src.qwed_new.core.attestation.get_attestation_service", side_effect=Exception("Boom")):
            token = create_verification_attestation("s", True, "e", "q")
            self.assertIsNone(token)

if __name__ == '__main__':
    unittest.main()
