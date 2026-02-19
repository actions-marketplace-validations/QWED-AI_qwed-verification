
import unittest
import base64
from unittest.mock import patch
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

    def test_create_attestation_full_options(self):
        """Test creating attestation with all options (proof, chain)."""
        result = VerificationResult(status="ok", verified=True, engine="test")
        attestation = self.service.create_attestation(
            result, 
            "query", 
            proof_data="proof123", 
            chain_id="chain1", 
            chain_index=5
        )
        claims = attestation.claims.qwed
        self.assertEqual(claims["proof_hash"], self.service._hash_content("proof123"))
        self.assertEqual(claims["chain_id"], "chain1")
        self.assertEqual(claims["chain_index"], 5)

    def test_verify_expired_token(self):
        """Test verification of expired token."""
        # Create token with short expiry and travel in time
        self.service.validity_days = -1 # Expired immediately
        result = VerificationResult(status="ok", verified=True, engine="test")
        attestation = self.service.create_attestation(result, "query")
        
        is_valid, _, error = self.service.verify_attestation(attestation.jwt_token)
        self.assertFalse(is_valid)
        self.assertIn("expired", error)
        self.service.validity_days = 365 # Reset

    def test_verify_invalid_signature(self):
        """Test verification with tampered signature."""
        result = VerificationResult(status="ok", verified=True, engine="test")
        attestation = self.service.create_attestation(result, "query")
        
        # Tamper with the token (modify last char of signature)
        tampered_token = attestation.jwt_token[:-1] + ("A" if attestation.jwt_token[-1] != "A" else "B")
        
        is_valid, _, error = self.service.verify_attestation(tampered_token)
        # Depending on how the padding/decoding fails, it might be invalid token or format
        self.assertFalse(is_valid)
        
    def test_get_issuer_info(self):
        """Test get_issuer_info returns correct structure."""
        info = self.service.get_issuer_info()
        self.assertEqual(info["did"], "did:test:123")
        self.assertEqual(info["status"], "active")
        self.assertIn("public_keys", info)
        self.assertEqual(len(info["public_keys"]), 1)
        
    def test_key_pair_generation(self):
        """Test internal key pair generation and properties."""
        kp = self.service._ensure_key_pair()
        self.assertIsNotNone(kp.private_key_pem)
        self.assertIsNotNone(kp.public_key_pem)
        jwk = kp.jwk
        self.assertEqual(jwk["kty"], "EC")
        self.assertEqual(jwk["crv"], "P-256")
        self.assertEqual(jwk["kid"], kp.key_id)

if __name__ == '__main__':
    unittest.main()
