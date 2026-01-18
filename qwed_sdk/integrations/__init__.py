"""
QWED Framework Integrations.

Import integrations for your favorite agent frameworks.
"""

# LangChain
try:
    from .langchain import QWEDTool
except ImportError:
    pass

# CrewAI
try:
    from .crewai import QWEDVerifiedAgent, VerificationConfig
except ImportError:
    pass

# LlamaIndex
try:
    from .llamaindex import QWEDQueryEngine, VerifiedResponse
except ImportError:
    pass

__all__ = [
    "QWEDTool",
    "QWEDVerifiedAgent", 
    "VerificationConfig",
    "QWEDQueryEngine", 
    "VerifiedResponse"
]
