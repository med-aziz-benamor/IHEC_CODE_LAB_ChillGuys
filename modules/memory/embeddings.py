"""
Embeddings Module - Text Vectorization with Fallback
=====================================================
Provides embedding generation with automatic fallback to simpler methods.

Primary: sentence-transformers (all-MiniLM-L6-v2)
Fallback: TF-IDF vectorizer (sklearn)
"""

import numpy as np
from typing import List, Optional
import warnings

# Try importing sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    warnings.warn("sentence-transformers not available, will use TF-IDF fallback")

# TF-IDF fallback
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


class EmbeddingProvider:
    """
    Embedding provider with automatic fallback.
    
    Usage:
        provider = EmbeddingProvider()
        embeddings = provider.embed_texts(["text1", "text2"])
        query_emb = provider.embed_query("search query")
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', vector_size: int = 384):
        """
        Initialize embedding provider.
        
        Args:
            model_name: Sentence transformer model name
            vector_size: Expected vector dimension
        """
        self.vector_size = vector_size
        self.model_name = model_name
        self.model = None
        self.tfidf_vectorizer = None
        self.corpus_cache = []
        self.method = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize embedding method (sentence-transformers or TF-IDF)."""
        # Try sentence-transformers first
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                print(f"Loading sentence-transformers model: {self.model_name}...")
                self.model = SentenceTransformer(self.model_name)
                
                # Verify vector size
                test_emb = self.model.encode(["test"], show_progress_bar=False)
                actual_size = test_emb.shape[1]
                
                if actual_size != self.vector_size:
                    print(f"⚠️  Model vector size ({actual_size}) != expected ({self.vector_size})")
                    print(f"   Adjusting vector_size to {actual_size}")
                    self.vector_size = actual_size
                
                self.method = 'sentence-transformers'
                print(f"✅ Sentence-transformers loaded (vector_size={self.vector_size})")
                return
            except Exception as e:
                print(f"⚠️  Failed to load sentence-transformers: {e}")
                print("   Falling back to TF-IDF...")
        
        # Fallback to TF-IDF
        print(f"Initializing TF-IDF vectorizer (vector_size={self.vector_size})...")
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=self.vector_size,
            strip_accents='unicode',
            lowercase=True,
            ngram_range=(1, 2),
            min_df=1
        )
        self.method = 'tfidf'
        print("✅ TF-IDF vectorizer initialized (requires corpus fitting)")
    
    def fit_tfidf(self, corpus: List[str]):
        """
        Fit TF-IDF vectorizer on corpus (only needed for TF-IDF method).
        
        Args:
            corpus: List of text documents
        """
        if self.method == 'sentence-transformers':
            return  # Not needed for sentence-transformers
        
        if not corpus:
            corpus = ["empty corpus placeholder"]
        
        print(f"Fitting TF-IDF on {len(corpus)} documents...")
        self.tfidf_vectorizer.fit(corpus)
        self.corpus_cache = corpus
        print("✅ TF-IDF fitted")
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of text strings
        
        Returns:
            Numpy array of shape (len(texts), vector_size)
        """
        if not texts:
            return np.zeros((0, self.vector_size))
        
        # Sentence-transformers method
        if self.method == 'sentence-transformers':
            embeddings = self.model.encode(
                texts,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            return embeddings
        
        # TF-IDF method
        elif self.method == 'tfidf':
            if self.tfidf_vectorizer is None:
                raise RuntimeError("TF-IDF vectorizer not initialized")
            
            # If not fitted, fit on provided texts
            if not hasattr(self.tfidf_vectorizer, 'vocabulary_'):
                print("⚠️  TF-IDF not fitted, fitting on provided texts...")
                self.fit_tfidf(texts)
            
            # Transform texts
            vectors = self.tfidf_vectorizer.transform(texts).toarray()
            
            # Normalize to unit vectors
            vectors = normalize(vectors, norm='l2')
            
            # Pad or truncate to exact vector_size
            if vectors.shape[1] < self.vector_size:
                # Pad with zeros
                padding = np.zeros((vectors.shape[0], self.vector_size - vectors.shape[1]))
                vectors = np.hstack([vectors, padding])
            elif vectors.shape[1] > self.vector_size:
                # Truncate
                vectors = vectors[:, :self.vector_size]
            
            return vectors
        
        else:
            raise RuntimeError(f"Unknown embedding method: {self.method}")
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a single query.
        
        Args:
            query: Query text
        
        Returns:
            Numpy array of shape (vector_size,)
        """
        embeddings = self.embed_texts([query])
        return embeddings[0]
    
    def get_method(self) -> str:
        """Get current embedding method."""
        return self.method
    
    def get_vector_size(self) -> int:
        """Get vector dimension."""
        return self.vector_size


# Singleton instance
_embedding_provider: Optional[EmbeddingProvider] = None


def get_embedding_provider(force_reload: bool = False) -> EmbeddingProvider:
    """
    Get singleton embedding provider instance.
    
    Args:
        force_reload: Force reinitialization
    
    Returns:
        EmbeddingProvider instance
    """
    global _embedding_provider
    
    if _embedding_provider is None or force_reload:
        _embedding_provider = EmbeddingProvider()
    
    return _embedding_provider


if __name__ == '__main__':
    # Test embedding provider
    print("Testing Embedding Provider")
    print("=" * 50)
    
    provider = EmbeddingProvider()
    print(f"\nMethod: {provider.get_method()}")
    print(f"Vector size: {provider.get_vector_size()}")
    
    # Test texts
    texts = [
        "La Bourse de Tunis a clôturé en hausse",
        "Anomalie détectée sur le titre STB",
        "Recommandation: ACHAT sur ATTIJARI"
    ]
    
    print(f"\nEmbedding {len(texts)} texts...")
    embeddings = provider.embed_texts(texts)
    print(f"Embeddings shape: {embeddings.shape}")
    print(f"Sample embedding (first 10 dims): {embeddings[0][:10]}")
    
    # Test query
    query = "Actualités bancaires"
    print(f"\nEmbedding query: '{query}'")
    query_emb = provider.embed_query(query)
    print(f"Query embedding shape: {query_emb.shape}")
    
    # Compute similarities
    from sklearn.metrics.pairwise import cosine_similarity
    similarities = cosine_similarity([query_emb], embeddings)[0]
    print(f"\nSimilarities to query:")
    for i, (text, sim) in enumerate(zip(texts, similarities)):
        print(f"  {i+1}. {text[:50]}... → {sim:.3f}")
    
    print("\n✅ Embedding provider test complete!")
