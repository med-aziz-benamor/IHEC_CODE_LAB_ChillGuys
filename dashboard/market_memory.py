"""
Market Memory Dashboard Integration
====================================
UI components for semantic search and evidence retrieval.
"""

import streamlit as st
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from modules.memory.qdrant_store import QdrantStore
    from modules.memory.embeddings import get_embedding_provider
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False


def get_memory_store() -> Optional[QdrantStore]:
    """
    Get or initialize Qdrant store (cached in session state).
    
    Returns:
        QdrantStore instance or None if unavailable
    """
    if not MEMORY_AVAILABLE:
        return None
    
    if 'memory_store' not in st.session_state:
        store = QdrantStore()
        if store.is_available():
            st.session_state.memory_store = store
        else:
            st.session_state.memory_store = None
    
    return st.session_state.memory_store


def get_embedding_provider_cached():
    """
    Get embedding provider (cached in session state).
    
    Returns:
        EmbeddingProvider instance or None
    """
    if not MEMORY_AVAILABLE:
        return None
    
    if 'embedding_provider' not in st.session_state:
        from modules.memory.embeddings import get_embedding_provider
        st.session_state.embedding_provider = get_embedding_provider()
    
    return st.session_state.embedding_provider


def search_market_memory(
    query: str,
    collection: str = 'bvmt_news',
    top_k: int = 5,
    filters: Optional[Dict[str, Any]] = None,
    score_threshold: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Search market memory for relevant information.
    
    Args:
        query: Search query
        collection: Collection to search (bvmt_news, bvmt_anomalies, bvmt_recommendations)
        top_k: Number of results
        filters: Metadata filters
        score_threshold: Minimum similarity score
    
    Returns:
        List of results
    """
    store = get_memory_store()
    embedder = get_embedding_provider_cached()
    
    if not store or not embedder:
        return []
    
    try:
        # Generate query embedding
        query_vector = embedder.embed_query(query)
        
        # Search
        results = store.search(
            collection_name=collection,
            query_vector=query_vector,
            top_k=top_k,
            score_threshold=score_threshold,
            filters=filters
        )
        
        return results
    
    except Exception as e:
        st.error(f"Erreur de recherche: {e}")
        return []


def render_memory_search_widget(
    placeholder: str = "Posez une question sur le marché...",
    collections: List[str] = None,
    default_collection: str = 'bvmt_news',
    filters: Optional[Dict[str, Any]] = None
):
    """
    Render market memory search widget.
    
    Args:
        placeholder: Search box placeholder text
        collections: Available collections to search
        default_collection: Default collection
        filters: Metadata filters
    """
    if not MEMORY_AVAILABLE:
        st.info("💡 **Market Memory** n'est pas disponible. Démarrez Qdrant avec: `docker compose up -d qdrant`")
        return
    
    store = get_memory_store()
    if not store:
        st.warning("⚠️ Qdrant non disponible. Démarrez avec: `docker compose up -d qdrant`")
        st.caption("La recherche sémantique nécessite Qdrant pour fonctionner.")
        return
    
    st.markdown("---")
    st.markdown("### 🔎 Market Memory - Recherche Sémantique")
    
    # Collection selector
    if collections is None:
        collections = ['bvmt_news', 'bvmt_anomalies', 'bvmt_recommendations']
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Recherche",
            placeholder=placeholder,
            key='memory_search_query'
        )
    
    with col2:
        selected_collection = st.selectbox(
            "Source",
            options=collections,
            format_func=lambda x: {
                'bvmt_news': '📰 Actualités',
                'bvmt_anomalies': '⚠️ Anomalies',
                'bvmt_recommendations': '💡 Recommandations'
            }.get(x, x),
            index=collections.index(default_collection) if default_collection in collections else 0,
            key='memory_search_collection'
        )
    
    if query:
        with st.spinner("Recherche en cours..."):
            results = search_market_memory(
                query=query,
                collection=selected_collection,
                top_k=5,
                filters=filters,
                score_threshold=0.25
            )
        
        if results:
            st.success(f"✅ {len(results)} résultat(s) trouvé(s)")
            
            for i, result in enumerate(results):
                score = result['score']
                text = result['text']
                ticker = result.get('ticker', '')
                date = result.get('date', '')
                result_type = result.get('type', '')
                metadata = result.get('metadata', {})
                
                # Determine icon
                if result_type == 'news':
                    icon = '📰'
                elif result_type == 'anomaly':
                    icon = '⚠️'
                elif result_type == 'recommendation':
                    icon = '💡'
                else:
                    icon = '📄'
                
                # Render result card
                with st.expander(f"{icon} [{ticker}] {text[:100]}... (Score: {score:.2f})"):
                    st.markdown(f"**Texte complet:**")
                    st.write(text)
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.caption(f"**Ticker:** {ticker}")
                    with col_b:
                        st.caption(f"**Date:** {date}")
                    with col_c:
                        st.caption(f"**Score:** {score:.3f}")
                    
                    if metadata:
                        with st.expander("🔍 Métadonnées"):
                            st.json(metadata)
        else:
            st.info("Aucun résultat trouvé. Essayez une autre requête.")
    else:
        st.info("💡 Posez une question pour rechercher dans la mémoire du marché.")


def render_similar_items_widget(
    reference_text: str,
    collection: str,
    title: str = "🔗 Éléments Similaires",
    top_k: int = 3,
    filters: Optional[Dict[str, Any]] = None
):
    """
    Render similar items widget (for finding related news/anomalies).
    
    Args:
        reference_text: Reference text to find similar items
        collection: Collection to search
        title: Widget title
        top_k: Number of results
        filters: Metadata filters
    """
    if not MEMORY_AVAILABLE or not reference_text:
        return
    
    store = get_memory_store()
    if not store:
        return
    
    st.markdown(f"### {title}")
    
    with st.spinner("Recherche d'éléments similaires..."):
        results = search_market_memory(
            query=reference_text,
            collection=collection,
            top_k=top_k,
            filters=filters,
            score_threshold=0.3
        )
    
    if results:
        for result in results:
            text = result['text']
            ticker = result.get('ticker', '')
            date = result.get('date', '')
            score = result['score']
            
            st.markdown(f"""
            <div style='padding: 10px; border-left: 3px solid #1E40AF; background: #F3F4F6; margin-bottom: 10px;'>
                <strong>[{ticker}]</strong> {text[:150]}...<br>
                <small>Date: {date} | Similarité: {score:.2f}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("Aucun élément similaire trouvé.")


def get_memory_evidence(
    ticker: str,
    context: str,
    top_k: int = 3
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get market memory evidence for a specific ticker and context.
    
    Args:
        ticker: Stock ticker
        context: Context description (e.g., "price increase", "anomaly detected")
        top_k: Results per collection
    
    Returns:
        Dict with keys 'news', 'anomalies', 'recommendations'
    """
    if not MEMORY_AVAILABLE:
        return {}
    
    store = get_memory_store()
    if not store:
        return {}
    
    query = f"{ticker} {context}"
    filters = {'ticker': ticker}
    
    evidence = {}
    
    # Search each collection
    for collection in ['bvmt_news', 'bvmt_anomalies', 'bvmt_recommendations']:
        results = search_market_memory(
            query=query,
            collection=collection,
            top_k=top_k,
            filters=filters,
            score_threshold=0.25
        )
        
        key = collection.replace('bvmt_', '')
        evidence[key] = results
    
    return evidence


def render_memory_status_badge():
    """Render market memory availability status badge."""
    if not MEMORY_AVAILABLE:
        return
    
    store = get_memory_store()
    
    if store and store.is_available():
        # Get collection stats
        collections_info = []
        for coll in ['bvmt_news', 'bvmt_anomalies', 'bvmt_recommendations']:
            count = store.count_documents(coll)
            collections_info.append(f"{coll.replace('bvmt_', '')}: {count}")
        
        status_text = " | ".join(collections_info)
        st.sidebar.success(f"🧠 Market Memory: ✅ Actif")
        st.sidebar.caption(status_text)
    else:
        st.sidebar.warning("🧠 Market Memory: ⚠️ Inactif")
        st.sidebar.caption("Démarrez avec: `docker compose up -d qdrant`")


if __name__ == '__main__':
    # Test widget
    st.set_page_config(page_title="Market Memory Test", layout="wide")
    
    st.title("🧠 Market Memory - Test Interface")
    
    render_memory_status_badge()
    
    st.markdown("## Recherche Sémantique")
    render_memory_search_widget()
    
    st.markdown("## Recherche d'Éléments Similaires")
    render_similar_items_widget(
        reference_text="Anomalie détectée sur BNA avec hausse de 5%",
        collection='bvmt_anomalies',
        title="🔗 Anomalies Similaires"
    )
    
    st.markdown("## Evidence pour BNA")
    evidence = get_memory_evidence('BNA', 'hausse des prix')
    st.json(evidence)
