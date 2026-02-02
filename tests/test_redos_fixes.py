import pytest
from qwed_new.core.fact_verifier import FactVerifier
from qwed_new.core.image_verifier import ImageVerifier, ImageAnalysisResult

def test_fact_verifier_bounded_regex():
    """
    Test that FactVerifier's new bounded regexes correctly extract entities
    and handle long inputs without crashing.
    """
    verifier = FactVerifier(use_llm_fallback=False)
    
    # 1. Normal Input - Should extract numbers correctly
    claim = "The profit was 10.5 million in 2024."
    context = "In 2024, the company reported 10.5 million profit."
    
    # Analyze - this triggers _match_entities which uses the new \d{1,20} regex
    result = verifier.verify_fact(claim, context)
    
    # Verify entity matching logic still works
    assert "2024" in result["reasoning"] or result["scores"]["entity_match"] > 0.5
    
    # 2. Long Input - Should be truncated/handled safely
    # Create valid sentence structure but very long
    base_sentence = "This is a sentence. "
    long_context = base_sentence * 5000  # ~100k chars
    
    # This triggers _segment_sentences with the new safe_pattern
    result = verifier.verify_fact("test", long_context)
    # Should run without timeout/error
    assert result["verdict"] is not None

def test_image_verifier_bounded_regex():
    """
    Test that ImageVerifier's bounded regexes match valid dimensions
    and reject excessively long claims.
    """
    verifier = ImageVerifier(use_llm_fallback=False)
    dummy_meta = ImageAnalysisResult(
        description="test", objects=[], text=[], valid=True,
        width=800, height=600, format="PNG", mode="RGB"
    )
    
    # 1. Valid Dimensions - Should match using the new \d{1,10} regex
    claim_valid = "The image is 800x600 pixels."
    result_valid = verifier._verify_size_claim(claim_valid, dummy_meta)
    
    assert result_valid.verdict == "SUPPORTED"
    assert "Dimensions match" in result_valid.reasoning
    
    # 2. ReDoS Attempt - Should be blocked by length check
    long_claim = "a" * 600
    result_blocked = verifier._verify_size_claim(long_claim, dummy_meta)
    
    assert result_blocked.verdict == "INCONCLUSIVE"
    assert "Claim too long" in result_blocked.reasoning
    
    # 3. Mixed spaces - Should match with bounded \s{0,5}
    claim_spaces = "800   x   600"
    result_spaces = verifier._verify_size_claim(claim_spaces, dummy_meta)
    assert result_spaces.verdict == "SUPPORTED"
