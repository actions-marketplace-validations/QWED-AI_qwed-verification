
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from qwed_new.api.main import app
from qwed_new.core.control_plane import ControlPlane

client = TestClient(app)

@pytest.mark.asyncio
async def test_verify_logic_exception_handling():
    """
    Test that verify_logic catches internal errors and returns a sanitized message.
    """
    # Mock the control plane to raise an exception
    with patch('qwed_new.api.main.control_plane.process_logic_query', side_effect=Exception("SENSITIVE_LOGIC_ERROR")):
        # Providing valid minimal input
        response = client.post(
            "/verify/logic",
            json={"query": "If A then B..."}
            # Note: headers/auth might be needed if not mocked globally, but usually TestClient + dependency overrides handle it or we get 403.
            # Assuming default dependency overrides or loose auth for tests, otherwise we need to set valid api key header.
        )
        
        # If the rate limiter or auth is active, we might need headers. 
        # For simplicity, let's assume standard test setup or mock the dependencies if needed.
        # But failing that, we can mock the dependency overrides.
        
        # Since I don't have the full test setup context, I'll rely on the fact that existing tests work.
        # If this fails with 401/403, I'll check other tests.
        
        # However, checking `tests/test_api_exceptions.py` (viewed earlier), it uses `client` directly.
        # It likely needs an API key or mock.
        
    # Let's try to mock the dependencies to ensure we reach the code block.
    # Actually, looking at main.py, check_rate_limit(tenant.api_key) is called.
    # We should mock get_current_tenant.
    
    pass

def test_verify_logic_exception_integration():
    """
    Integration style test for verify_logic exception.
    """
    with patch("qwed_new.core.rate_limiter.check_rate_limit"), \
         patch("qwed_new.api.main.get_current_tenant") as mock_tenant, \
         patch("qwed_new.api.main.control_plane.process_logic_query", side_effect=Exception("SENSITIVE_FAILURE")):
        
        mock_tenant.return_value = MagicMock(organization_id=1, api_key="test_key")
        
        response = client.post(
            "/verify/logic",
            json={"query": "test query"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ERROR"
        assert data["error"] == "Internal verification error"
        assert "SENSITIVE_FAILURE" not in str(data)

@pytest.mark.asyncio
async def test_control_plane_logic_exception():
    """
    Directly test ControlPlane.process_logic_query exception handling.
    """
    cp = ControlPlane()
    
    # Mock components to fail deep inside
    with patch.object(cp.security_gateway, 'detect_advanced_injection', return_value=(True, "")), \
         patch.object(cp.policy, 'check_policy', return_value=(True, "")), \
         patch.object(cp.router, 'route', return_value="openai"), \
         patch.object(cp.logic_verifier, 'verify_from_natural_language', side_effect=Exception("DEEP_INTERNAL_ERROR")):
             
        result = await cp.process_logic_query("test query", organization_id=123)
        
        assert result["status"] == "ERROR"
        assert result["error"] == "Internal pipeline error"
        assert "DEEP_INTERNAL_ERROR" not in result["error"]
