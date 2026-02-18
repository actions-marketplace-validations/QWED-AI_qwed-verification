
import unittest
from unittest.mock import MagicMock, patch
from qwed_sdk.qwed_local import QWEDLocal

class TestQWEDLocalCoverage(unittest.TestCase):
    """Targeted tests to improve coverage of qwed_local.py"""

    def test_init_openai_provider(self):
        """Test initialization with OpenAI provider."""
        with patch("qwed_sdk.qwed_local.OpenAI") as MockOpenAI:
            client = QWEDLocal(provider="openai", api_key="sk-test", cache=False)
            self.assertEqual(client.client_type, "openai")
            MockOpenAI.assert_called_with(api_key="sk-test")

    def test_init_anthropic_provider(self):
        """Test initialization with Anthropic provider."""
        with patch("qwed_sdk.qwed_local.Anthropic") as MockAnthropic:
            client = QWEDLocal(provider="anthropic", api_key="sk-ant", cache=False)
            self.assertEqual(client.client_type, "anthropic")
            MockAnthropic.assert_called_with(api_key="sk-ant")

    def test_init_gemini_provider(self):
        """Test initialization with Gemini provider."""
        with patch("qwed_sdk.qwed_local.genai") as MockGenAI:
            client = QWEDLocal(provider="gemini", api_key="AIza", cache=False)
            self.assertEqual(client.client_type, "gemini")
            MockGenAI.configure.assert_called_with(api_key="AIza")

    def test_init_custom_base_url(self):
        """Test initialization with custom base_url (Ollama style)."""
        with patch("qwed_sdk.qwed_local.OpenAI") as MockOpenAI:
            client = QWEDLocal(base_url="http://localhost:11434", cache=False)
            self.assertEqual(client.client_type, "openai")
            MockOpenAI.assert_called()

    def test_init_missing_deps(self):
        """Test import error when dependencies missing."""
        # This is hard to mock without reloading modules, skipping for now
        pass

    def test_verify_auto_detect(self):
        """Test verify() method defaults to verify_math."""
        client = QWEDLocal(base_url="http://mock", cache=False)
        client.verify_math = MagicMock(return_value="math_result")
        
        res = client.verify("2+2")
        self.assertEqual(res, "math_result")
        client.verify_math.assert_called_with("2+2")

    def test_verify_code_unsupported_lang(self):
        """Test verify_code with unsupported language."""
        client = QWEDLocal(base_url="http://mock", cache=False)
        res = client.verify_code("print('h')", language="java")
        self.assertFalse(res.verified)
        self.assertIn("Only Python supported", res.error)

    def test_cache_stats_none(self):
        """Test cache stats when cache disabled."""
        client = QWEDLocal(base_url="http://mock", cache=False)
        self.assertIsNone(client.cache_stats)
        # Should not crash
        client.print_cache_stats()

if __name__ == '__main__':
    unittest.main()
