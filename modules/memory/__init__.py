"""
Memory Module - Market Memory Layer with Qdrant
================================================
Semantic storage and retrieval for market intelligence.

Provides:
- Vector database integration (Qdrant)
- Embeddings generation (sentence-transformers + TF-IDF fallback)
- Semantic search for news, anomalies, recommendations
"""

from .qdrant_store import QdrantStore
from .embeddings import EmbeddingProvider

__all__ = ['QdrantStore', 'EmbeddingProvider']
