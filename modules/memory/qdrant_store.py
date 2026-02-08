"""
Qdrant Store - Vector Database Integration
===========================================
Manages semantic storage and retrieval using Qdrant.

Collections:
- bvmt_news: News articles and headlines
- bvmt_anomalies: Detected anomalies with context
- bvmt_recommendations: Investment recommendations with rationale
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import warnings

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        PointStruct, VectorParams, Distance,
        Filter, FieldCondition, MatchValue, Range
    )
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    warnings.warn("qdrant-client not installed. Install with: pip install qdrant-client")


class QdrantStore:
    """
    Qdrant vector database wrapper for market memory.
    
    Usage:
        store = QdrantStore(host='localhost', port=6333)
        store.create_collection('bvmt_news', vector_size=384)
        store.upsert_documents('bvmt_news', docs)
        results = store.search('bvmt_news', query_vector, top_k=5)
    """
    
    def __init__(self, host: str = 'localhost', port: int = 6333):
        """
        Initialize Qdrant client.
        
        Args:
            host: Qdrant server host
            port: Qdrant server port
        """
        self.host = host
        self.port = port
        self.client = None
        self.available = False
        
        if not QDRANT_AVAILABLE:
            print("⚠️  Qdrant client not available (install qdrant-client)")
            return
        
        try:
            self.client = QdrantClient(host=host, port=port)
            # Test connection
            self.client.get_collections()
            self.available = True
            print(f"✅ Connected to Qdrant at {host}:{port}")
        except Exception as e:
            print(f"⚠️  Cannot connect to Qdrant: {e}")
            print(f"   Make sure Qdrant is running: docker compose up -d qdrant")
            self.available = False
    
    def is_available(self) -> bool:
        """Check if Qdrant is available."""
        return self.available
    
    def create_collection(
        self,
        name: str,
        vector_size: int = 384,
        distance: str = "Cosine",
        recreate: bool = False
    ) -> bool:
        """
        Create a Qdrant collection.
        
        Args:
            name: Collection name
            vector_size: Vector dimension
            distance: Distance metric (Cosine, Euclidean, Dot)
            recreate: Delete existing collection first
        
        Returns:
            True if successful
        """
        if not self.available:
            return False
        
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(col.name == name for col in collections)
            
            if exists:
                if recreate:
                    print(f"Deleting existing collection: {name}")
                    self.client.delete_collection(name)
                else:
                    print(f"Collection '{name}' already exists")
                    return True
            
            # Map distance string to enum
            distance_map = {
                "Cosine": Distance.COSINE,
                "Euclidean": Distance.EUCLID,
                "Dot": Distance.DOT
            }
            distance_metric = distance_map.get(distance, Distance.COSINE)
            
            # Create collection
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance_metric
                )
            )
            
            print(f"✅ Created collection: {name} (vector_size={vector_size}, distance={distance})")
            return True
            
        except Exception as e:
            print(f"❌ Error creating collection '{name}': {e}")
            return False
    
    def upsert_documents(
        self,
        collection_name: str,
        documents: List[Dict[str, Any]]
    ) -> bool:
        """
        Upsert documents to collection.
        
        Each document should have:
        - id: Unique identifier (auto-generated if missing)
        - vector: Embedding vector (required)
        - text: Original text (required for metadata)
        - metadata: Dict with ticker, date, type, language, etc.
        
        Args:
            collection_name: Target collection
            documents: List of document dicts
        
        Returns:
            True if successful
        """
        if not self.available:
            return False
        
        if not documents:
            print("⚠️  No documents to upsert")
            return True
        
        try:
            points = []
            
            for doc in documents:
                # Generate ID if missing
                doc_id = doc.get('id', str(uuid.uuid4()))
                
                # Extract vector
                vector = doc.get('vector')
                if vector is None:
                    print(f"⚠️  Skipping document without vector: {doc_id}")
                    continue
                
                # Ensure vector is a list
                if hasattr(vector, 'tolist'):
                    vector = vector.tolist()
                
                # Build payload (metadata)
                payload = {
                    'text': doc.get('text', ''),
                    'ticker': doc.get('ticker', ''),
                    'date': doc.get('date', ''),
                    'type': doc.get('type', 'unknown'),
                    'language': doc.get('language', 'fr'),
                    'source': doc.get('source', ''),
                    'metadata': doc.get('metadata', {})
                }
                
                # Add any extra metadata
                for key, value in doc.items():
                    if key not in ['id', 'vector', 'text', 'ticker', 'date', 'type', 'language', 'source', 'metadata']:
                        payload['metadata'][key] = value
                
                points.append(PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload=payload
                ))
            
            # Batch upsert (Qdrant handles batching automatically)
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            print(f"✅ Upserted {len(points)} documents to '{collection_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Error upserting documents to '{collection_name}': {e}")
            return False
    
    def search(
        self,
        collection_name: str,
        query_vector: Any,
        top_k: int = 5,
        score_threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search in collection.
        
        Args:
            collection_name: Collection to search
            query_vector: Query embedding vector
            top_k: Number of results
            score_threshold: Minimum similarity score
            filters: Metadata filters (ticker, date, type, etc.)
        
        Returns:
            List of result dicts with 'id', 'score', 'text', 'metadata'
        """
        if not self.available:
            return []
        
        try:
            # Ensure vector is a list
            if hasattr(query_vector, 'tolist'):
                query_vector = query_vector.tolist()
            
            # Build filters if provided
            query_filter = None
            if filters:
                conditions = []
                
                for key, value in filters.items():
                    if isinstance(value, (list, tuple)):
                        # Multiple values (OR condition)
                        for v in value:
                            conditions.append(
                                FieldCondition(key=key, match=MatchValue(value=v))
                            )
                    elif isinstance(value, dict) and ('gte' in value or 'lte' in value):
                        # Range condition
                        conditions.append(
                            FieldCondition(
                                key=key,
                                range=Range(
                                    gte=value.get('gte'),
                                    lte=value.get('lte')
                                )
                            )
                        )
                    else:
                        # Single value
                        conditions.append(
                            FieldCondition(key=key, match=MatchValue(value=value))
                        )
                
                if conditions:
                    query_filter = Filter(should=conditions)
            
            # Search
            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=query_filter
            )
            
            # Format results
            results = []
            for hit in search_results:
                result = {
                    'id': hit.id,
                    'score': hit.score,
                    'text': hit.payload.get('text', ''),
                    'ticker': hit.payload.get('ticker', ''),
                    'date': hit.payload.get('date', ''),
                    'type': hit.payload.get('type', ''),
                    'language': hit.payload.get('language', ''),
                    'source': hit.payload.get('source', ''),
                    'metadata': hit.payload.get('metadata', {})
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ Error searching '{collection_name}': {e}")
            return []
    
    def delete_collection(self, name: str) -> bool:
        """
        Delete a collection.
        
        Args:
            name: Collection name
        
        Returns:
            True if successful
        """
        if not self.available:
            return False
        
        try:
            self.client.delete_collection(name)
            print(f"✅ Deleted collection: {name}")
            return True
        except Exception as e:
            print(f"❌ Error deleting collection '{name}': {e}")
            return False
    
    def get_collection_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get collection information.
        
        Args:
            name: Collection name
        
        Returns:
            Dict with collection info or None
        """
        if not self.available:
            return None
        
        try:
            info = self.client.get_collection(name)
            return {
                'name': info.name,
                'vector_size': info.config.params.vectors.size,
                'distance': info.config.params.vectors.distance.name,
                'points_count': info.points_count,
                'status': info.status.name
            }
        except Exception as e:
            print(f"⚠️  Cannot get info for '{name}': {e}")
            return None
    
    def count_documents(self, collection_name: str) -> int:
        """
        Count documents in collection.
        
        Args:
            collection_name: Collection name
        
        Returns:
            Number of documents
        """
        info = self.get_collection_info(collection_name)
        return info['points_count'] if info else 0


if __name__ == '__main__':
    # Test Qdrant store
    import numpy as np
    
    print("Testing Qdrant Store")
    print("=" * 50)
    
    store = QdrantStore()
    
    if not store.is_available():
        print("\n❌ Qdrant not available. Start with:")
        print("   docker compose up -d qdrant")
        exit(1)
    
    # Create test collection
    collection_name = 'test_collection'
    vector_size = 384
    
    print(f"\nCreating test collection: {collection_name}")
    store.create_collection(collection_name, vector_size, recreate=True)
    
    # Create test documents
    test_docs = [
        {
            'id': 'doc1',
            'vector': np.random.rand(vector_size),
            'text': 'La Bourse de Tunis clôture en hausse',
            'ticker': 'BVMT',
            'date': '2025-02-08',
            'type': 'news',
            'language': 'fr'
        },
        {
            'id': 'doc2',
            'vector': np.random.rand(vector_size),
            'text': 'Anomalie détectée sur STB',
            'ticker': 'STB',
            'date': '2025-02-08',
            'type': 'anomaly',
            'language': 'fr',
            'metadata': {'severity': 'HIGH'}
        }
    ]
    
    print(f"\nUpserting {len(test_docs)} test documents...")
    store.upsert_documents(collection_name, test_docs)
    
    # Test search
    print(f"\nSearching with random query vector...")
    query_vec = np.random.rand(vector_size)
    results = store.search(collection_name, query_vec, top_k=2)
    
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results):
        print(f"  {i+1}. [{result['type']}] {result['text']}")
        print(f"      Score: {result['score']:.3f}, Ticker: {result['ticker']}")
    
    # Get collection info
    print(f"\nCollection info:")
    info = store.get_collection_info(collection_name)
    if info:
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    # Cleanup
    print(f"\nCleaning up test collection...")
    store.delete_collection(collection_name)
    
    print("\n✅ Qdrant store test complete!")
