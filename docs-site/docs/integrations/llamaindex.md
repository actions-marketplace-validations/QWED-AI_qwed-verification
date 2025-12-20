---
sidebar_position: 2
---

# LlamaIndex Integration

Use QWED with LlamaIndex for verified RAG pipelines.

## Installation

```bash
pip install qwed-new llama-index
```

## Quick Start

```python
from qwed_sdk.llamaindex import QWEDQueryEngine

# Wrap any query engine with verification
verified_engine = QWEDQueryEngine(base_engine)

response = verified_engine.query("What is 15% of 200?")
print(response.verified)  # True/False
print(response.response)  # The answer
```

## QWEDQueryEngine

Wraps any LlamaIndex query engine to add verification:

```python
from llama_index.core import VectorStoreIndex
from qwed_sdk.llamaindex import QWEDQueryEngine

# Create base engine
index = VectorStoreIndex.from_documents(documents)
base_engine = index.as_query_engine()

# Wrap with QWED
verified_engine = QWEDQueryEngine(
    base_engine,
    api_key="qwed_...",
    verify_math=True,
    verify_facts=True,
    auto_correct=False,
)

response = verified_engine.query("Calculate the total cost")
print(response.verified)
```

## QWEDVerificationTransform

Node postprocessor that verifies retrieved content:

```python
from qwed_sdk.llamaindex import QWEDVerificationTransform

engine = index.as_query_engine(
    node_postprocessors=[
        QWEDVerificationTransform(
            verify_math=True,
            verify_code=True,
        )
    ]
)
```

## QWEDCallbackHandler

Track verification across all operations:

```python
from llama_index.core import Settings
from qwed_sdk.llamaindex import QWEDCallbackHandler

Settings.callback_manager.add_handler(
    QWEDCallbackHandler(log_all=True)
)
```

## QWEDVerifyTool

For LlamaIndex agents:

```python
from llama_index.core.agent import ReActAgent
from qwed_sdk.llamaindex import QWEDVerifyTool

tools = [QWEDVerifyTool()]
agent = ReActAgent.from_tools(tools, llm=llm)
```

## VerifiedResponse

```python
@dataclass
class VerifiedResponse:
    response: str
    verified: bool
    status: str
    confidence: float
    attestation: Optional[str]
    source_nodes: List[Any]
```
