"""
RAGGuard: Document-Level Retrieval Mismatch (DRM) Defender.

Verifies that retrieved context chunks in a RAG pipeline originate
from the correct source document, preventing hallucinations caused
by vector databases returning chunks from structurally similar but
semantically wrong documents (e.g., the wrong NDA or Privacy Policy).

Based on research from: "Towards Reliable Retrieval in RAG Systems
for Large Legal Datasets" — DRM is a critical failure mode where
legal/financial documents look structurally identical to embedding
models, causing cross-document contamination of retrieved context.
"""
from typing import List, Dict, Any, Optional


class RAGGuard:
    """
    Deterministic guard for RAG pipeline integrity.

    Ensures retrieved chunks match the expected source document,
    preventing Document-Level Retrieval Mismatch (DRM) hallucinations.

    Example::

        guard = RAGGuard()
        result = guard.verify_retrieval_context(
            target_document_id="contract_nda_v2",
            retrieved_chunks=[
                {"id": "c1", "metadata": {"document_id": "contract_nda_v2"}},
                {"id": "c2", "metadata": {"document_id": "contract_nda_v1"}},  # wrong!
            ]
        )
        # result["verified"] == False, result["drm_rate"] == 0.5
    """

    def __init__(
        self,
        max_drm_rate: float = 0.0,
        require_metadata: bool = True,
    ):
        """
        Args:
            max_drm_rate: Maximum tolerable fraction of mismatched chunks
                (0.0 = zero tolerance, 1.0 = allow all). Default: 0.0.
            require_metadata: If True, chunks missing ``document_id`` in
                metadata are treated as mismatches. Default: True.
        """
        if not 0.0 <= max_drm_rate <= 1.0:
            raise ValueError("max_drm_rate must be between 0.0 and 1.0")
        self.max_drm_rate = max_drm_rate
        self.require_metadata = require_metadata

    def verify_retrieval_context(
        self,
        target_document_id: str,
        retrieved_chunks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Verify that all retrieved chunks belong to the target document.

        Args:
            target_document_id: The expected source document identifier.
            retrieved_chunks: List of chunk dicts. Each chunk should have
                ``metadata.document_id`` set.

        Returns:
            ``{"verified": True, "drm_rate": 0.0}`` on success, or
            ``{"verified": False, "risk": "DOCUMENT_RETRIEVAL_MISMATCH",
            "drm_rate": float, "message": str, "details": [...]}`` on failure.
        """
        if not retrieved_chunks:
            return {
                "verified": True,
                "drm_rate": 0.0,
                "message": "No chunks to verify.",
                "chunks_checked": 0,
            }

        mismatched: List[Dict[str, Any]] = []

        for chunk in retrieved_chunks:
            chunk_id = chunk.get("id", "unknown")
            metadata = chunk.get("metadata") or {}
            chunk_doc_id = metadata.get("document_id")

            if chunk_doc_id is None:
                # Chunk has no metadata at all
                if self.require_metadata:
                    mismatched.append({
                        "chunk_id": chunk_id,
                        "issue": "MISSING_DOCUMENT_ID",
                        "wrong_source": None,
                    })
            elif chunk_doc_id != target_document_id:
                mismatched.append({
                    "chunk_id": chunk_id,
                    "issue": "WRONG_DOCUMENT",
                    "wrong_source": chunk_doc_id,
                })

        total = len(retrieved_chunks)
        drm_rate = len(mismatched) / total

        if drm_rate > self.max_drm_rate:
            return {
                "verified": False,
                "risk": "DOCUMENT_RETRIEVAL_MISMATCH",
                "drm_rate": round(drm_rate, 4),
                "chunks_checked": total,
                "mismatched_count": len(mismatched),
                "message": (
                    f"Blocked RAG injection: {len(mismatched)}/{total} chunks "
                    f"originated from the wrong source document. "
                    f"DRM rate {drm_rate:.1%} exceeds threshold {self.max_drm_rate:.1%}. "
                    "This will cause hallucinations."
                ),
                "details": mismatched,
            }

        return {
            "verified": True,
            "drm_rate": round(drm_rate, 4),
            "chunks_checked": total,
            "message": f"All {total} chunk(s) verified from correct source document.",
        }

    def filter_valid_chunks(
        self,
        target_document_id: str,
        retrieved_chunks: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Return only the chunks that belong to the target document.

        Useful when you want to silently drop mismatched chunks rather
        than raising an error.

        Args:
            target_document_id: The expected source document identifier.
            retrieved_chunks: Full list of retrieved chunks.

        Returns:
            Filtered list containing only matching chunks.
        """
        return [
            chunk for chunk in retrieved_chunks
            if chunk.get("metadata", {}).get("document_id") == target_document_id
        ]
