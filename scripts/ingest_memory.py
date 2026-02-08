"""
Market Memory Ingestion Script
===============================
Ingests historical data into Qdrant for semantic search.

Collections:
- bvmt_news: News articles from cached data
- bvmt_anomalies: Detected anomalies with context
- bvmt_recommendations: Investment recommendations

Usage:
    python scripts/ingest_memory.py [--recreate] [--limit 100]
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.memory.qdrant_store import QdrantStore
from modules.memory.embeddings import get_embedding_provider


def load_news_cache(cache_path: str) -> List[Dict[str, Any]]:
    """
    Load cached news data.
    
    Args:
        cache_path: Path to news_cache.json
    
    Returns:
        List of news items
    """
    if not os.path.exists(cache_path):
        print(f"⚠️  News cache not found: {cache_path}")
        return []
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        
        news_items = []
        for ticker, articles in cache.items():
            if isinstance(articles, list):
                for article in articles:
                    news_items.append({
                        'ticker': ticker,
                        'title': article.get('title', ''),
                        'snippet': article.get('snippet', ''),
                        'url': article.get('url', ''),
                        'date': article.get('date', ''),
                        'source': article.get('source', ''),
                        'language': article.get('language', 'fr')
                    })
        
        print(f"✅ Loaded {len(news_items)} news items from cache")
        return news_items
    
    except Exception as e:
        print(f"❌ Error loading news cache: {e}")
        return []


def load_anomalies_sample(data_path: str, top_tickers: List[str], limit: int = 50) -> List[Dict[str, Any]]:
    """
    Generate sample anomalies from recent price data.
    
    Args:
        data_path: Path to combined CSV
        top_tickers: List of tickers to analyze
        limit: Maximum anomalies to generate
    
    Returns:
        List of anomaly events
    """
    csv_path = os.path.join(data_path, 'histo_cotation_combined_2022_2025.csv')
    
    if not os.path.exists(csv_path):
        print(f"⚠️  Data file not found: {csv_path}")
        return []
    
    try:
        df = pd.read_csv(csv_path)
        
        # Ensure Date column
        if 'Date' not in df.columns and 'date' in df.columns:
            df['Date'] = df['date']
        
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        df = df.sort_values('Date')
        
        # Filter to recent data (last 90 days)
        recent_date = df['Date'].max() - timedelta(days=90)
        df_recent = df[df['Date'] >= recent_date]
        
        anomalies = []
        
        for ticker in top_tickers[:8]:  # Limit to 8 tickers for demo
            ticker_data = df_recent[df_recent['Symbole'] == ticker].copy()
            
            if len(ticker_data) < 20:
                continue
            
            # Calculate returns
            ticker_data['return'] = ticker_data['Prix de clôture'].pct_change()
            
            # Find large moves (> 3% daily change)
            large_moves = ticker_data[abs(ticker_data['return']) > 0.03]
            
            for idx, row in large_moves.head(5).iterrows():
                ret = row['return']
                direction = 'hausse' if ret > 0 else 'baisse'
                severity = 'HIGH' if abs(ret) > 0.05 else 'MEDIUM'
                
                anomaly = {
                    'ticker': ticker,
                    'date': row['Date'].strftime('%Y-%m-%d'),
                    'type': 'price_spike',
                    'direction': direction,
                    'severity': severity,
                    'value': float(row['Prix de clôture']),
                    'change_pct': float(ret * 100),
                    'reason': f"Mouvement important de {abs(ret)*100:.1f}% en {direction}",
                    'description': f"Anomalie détectée sur {ticker}: variation de {ret*100:+.1f}% le {row['Date'].strftime('%d/%m/%Y')}"
                }
                
                anomalies.append(anomaly)
                
                if len(anomalies) >= limit:
                    break
            
            if len(anomalies) >= limit:
                break
        
        print(f"✅ Generated {len(anomalies)} sample anomalies")
        return anomalies
    
    except Exception as e:
        print(f"❌ Error generating anomalies: {e}")
        return []


def generate_recommendations_sample(top_tickers: List[str], limit: int = 30) -> List[Dict[str, Any]]:
    """
    Generate sample investment recommendations.
    
    Args:
        top_tickers: List of tickers
        limit: Maximum recommendations
    
    Returns:
        List of recommendation events
    """
    recommendations = []
    
    actions = ['ACHAT', 'VENTE', 'CONSERVER']
    reasons_achat = [
        "Sous-évaluation par rapport au secteur",
        "Indicateurs techniques haussiers (RSI < 40, MACD positif)",
        "Momentum positif et volume croissant",
        "Résultats financiers solides et perspectives positives"
    ]
    reasons_vente = [
        "Surévaluation par rapport au secteur",
        "Indicateurs techniques baissiers (RSI > 70, MACD négatif)",
        "Risque de correction après forte hausse",
        "Dégradation des fondamentaux"
    ]
    reasons_hold = [
        "Valorisation équilibrée",
        "Attendre confirmation de la tendance",
        "Consolidation en cours",
        "Indicateurs techniques neutres"
    ]
    
    for i, ticker in enumerate(top_tickers[:10]):
        for j, action in enumerate(actions):
            if len(recommendations) >= limit:
                break
            
            # Vary confidence by action
            if action == 'ACHAT':
                confidence = np.random.uniform(0.65, 0.85)
                reasons = np.random.choice(reasons_achat, size=2, replace=False).tolist()
            elif action == 'VENTE':
                confidence = np.random.uniform(0.60, 0.80)
                reasons = np.random.choice(reasons_vente, size=2, replace=False).tolist()
            else:
                confidence = np.random.uniform(0.55, 0.75)
                reasons = np.random.choice(reasons_hold, size=2, replace=False).tolist()
            
            date_offset = (i * 3 + j * 7) % 60
            date = (datetime.now() - timedelta(days=date_offset)).strftime('%Y-%m-%d')
            
            rec = {
                'ticker': ticker,
                'date': date,
                'action': action,
                'confidence': float(confidence),
                'reasons': reasons,
                'horizon': 'Moyen terme (3-6 mois)',
                'target_price': None,
                'description': f"Recommandation {action} sur {ticker} avec confiance {confidence*100:.0f}%"
            }
            
            recommendations.append(rec)
        
        if len(recommendations) >= limit:
            break
    
    print(f"✅ Generated {len(recommendations)} sample recommendations")
    return recommendations


def ingest_news_collection(
    store: QdrantStore,
    embedder,
    news_items: List[Dict[str, Any]],
    collection_name: str = 'bvmt_news',
    recreate: bool = False
):
    """Ingest news into Qdrant."""
    print(f"\n{'='*60}")
    print(f"Ingesting News Collection: {collection_name}")
    print(f"{'='*60}")
    
    if not news_items:
        print("⚠️  No news items to ingest")
        return
    
    # Create collection
    vector_size = embedder.get_vector_size()
    store.create_collection(collection_name, vector_size, recreate=recreate)
    
    # Prepare texts for embedding
    texts = []
    for item in news_items:
        text = f"{item['title']} {item['snippet']}"
        texts.append(text)
    
    # Generate embeddings
    print(f"Generating embeddings for {len(texts)} news items...")
    if embedder.get_method() == 'tfidf':
        embedder.fit_tfidf(texts)
    
    embeddings = embedder.embed_texts(texts)
    
    # Prepare documents
    documents = []
    for i, item in enumerate(news_items):
        doc = {
            'id': f"news_{i}",
            'vector': embeddings[i],
            'text': f"{item['title']} - {item['snippet'][:200]}",
            'ticker': item['ticker'],
            'date': item['date'],
            'type': 'news',
            'language': item['language'],
            'source': item['source'],
            'metadata': {
                'title': item['title'],
                'snippet': item['snippet'],
                'url': item.get('url', '')
            }
        }
        documents.append(doc)
    
    # Upsert to Qdrant
    store.upsert_documents(collection_name, documents)
    
    # Verify
    count = store.count_documents(collection_name)
    print(f"✅ Collection '{collection_name}' has {count} documents")


def ingest_anomalies_collection(
    store: QdrantStore,
    embedder,
    anomalies: List[Dict[str, Any]],
    collection_name: str = 'bvmt_anomalies',
    recreate: bool = False
):
    """Ingest anomalies into Qdrant."""
    print(f"\n{'='*60}")
    print(f"Ingesting Anomalies Collection: {collection_name}")
    print(f"{'='*60}")
    
    if not anomalies:
        print("⚠️  No anomalies to ingest")
        return
    
    # Create collection
    vector_size = embedder.get_vector_size()
    store.create_collection(collection_name, vector_size, recreate=recreate)
    
    # Prepare texts for embedding
    texts = [item['description'] for item in anomalies]
    
    # Generate embeddings
    print(f"Generating embeddings for {len(texts)} anomalies...")
    embeddings = embedder.embed_texts(texts)
    
    # Prepare documents
    documents = []
    for i, item in enumerate(anomalies):
        doc = {
            'id': f"anomaly_{i}",
            'vector': embeddings[i],
            'text': item['description'],
            'ticker': item['ticker'],
            'date': item['date'],
            'type': 'anomaly',
            'language': 'fr',
            'source': 'anomaly_detector',
            'metadata': {
                'anomaly_type': item['type'],
                'direction': item['direction'],
                'severity': item['severity'],
                'value': item['value'],
                'change_pct': item['change_pct'],
                'reason': item['reason']
            }
        }
        documents.append(doc)
    
    # Upsert to Qdrant
    store.upsert_documents(collection_name, documents)
    
    # Verify
    count = store.count_documents(collection_name)
    print(f"✅ Collection '{collection_name}' has {count} documents")


def ingest_recommendations_collection(
    store: QdrantStore,
    embedder,
    recommendations: List[Dict[str, Any]],
    collection_name: str = 'bvmt_recommendations',
    recreate: bool = False
):
    """Ingest recommendations into Qdrant."""
    print(f"\n{'='*60}")
    print(f"Ingesting Recommendations Collection: {collection_name}")
    print(f"{'='*60}")
    
    if not recommendations:
        print("⚠️  No recommendations to ingest")
        return
    
    # Create collection
    vector_size = embedder.get_vector_size()
    store.create_collection(collection_name, vector_size, recreate=recreate)
    
    # Prepare texts for embedding
    texts = []
    for item in recommendations:
        reasons_text = ' | '.join(item['reasons'])
        text = f"{item['action']} {item['ticker']}: {reasons_text}"
        texts.append(text)
    
    # Generate embeddings
    print(f"Generating embeddings for {len(texts)} recommendations...")
    embeddings = embedder.embed_texts(texts)
    
    # Prepare documents
    documents = []
    for i, item in enumerate(recommendations):
        reasons_bullet = '\n'.join([f"• {r}" for r in item['reasons']])
        display_text = f"[{item['action']}] {item['ticker']} - Confiance: {item['confidence']*100:.0f}%\n{reasons_bullet}"
        
        doc = {
            'id': f"rec_{i}",
            'vector': embeddings[i],
            'text': display_text,
            'ticker': item['ticker'],
            'date': item['date'],
            'type': 'recommendation',
            'language': 'fr',
            'source': 'decision_engine',
            'metadata': {
                'action': item['action'],
                'confidence': item['confidence'],
                'reasons': item['reasons'],
                'horizon': item['horizon']
            }
        }
        documents.append(doc)
    
    # Upsert to Qdrant
    store.upsert_documents(collection_name, documents)
    
    # Verify
    count = store.count_documents(collection_name)
    print(f"✅ Collection '{collection_name}' has {count} documents")


def main():
    """Main ingestion pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest market memory data into Qdrant')
    parser.add_argument('--recreate', action='store_true', help='Recreate collections')
    parser.add_argument('--limit', type=int, default=100, help='Limit items per collection')
    args = parser.parse_args()
    
    print("=" * 60)
    print("BVMT Market Memory Ingestion")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Recreate: {args.recreate}")
    print(f"Limit: {args.limit}")
    
    # Initialize Qdrant
    print("\n" + "=" * 60)
    print("Step 1: Initialize Qdrant Connection")
    print("=" * 60)
    store = QdrantStore()
    
    if not store.is_available():
        print("\n❌ Qdrant not available!")
        print("   Start Qdrant with: docker compose up -d qdrant")
        print("   Then run this script again.")
        return 1
    
    # Initialize embeddings
    print("\n" + "=" * 60)
    print("Step 2: Initialize Embedding Provider")
    print("=" * 60)
    embedder = get_embedding_provider()
    print(f"Method: {embedder.get_method()}")
    print(f"Vector size: {embedder.get_vector_size()}")
    
    # Paths
    project_root_path = Path(__file__).parent.parent
    news_cache_path = project_root_path / 'data' / 'sentiment' / 'news_cache.json'
    data_path = project_root_path / 'data'
    
    # Top BVMT tickers
    top_tickers = [
        'BNA', 'ATB', 'BIAT', 'BT', 'STB', 'UIB', 'AMEN',
        'SFBT', 'ZITOUNA', 'BH', 'TUNISAIR', 'TUNTEL'
    ]
    
    # Load data
    print("\n" + "=" * 60)
    print("Step 3: Load Data Sources")
    print("=" * 60)
    
    news_items = load_news_cache(str(news_cache_path))[:args.limit]
    anomalies = load_anomalies_sample(str(data_path), top_tickers, limit=args.limit)
    recommendations = generate_recommendations_sample(top_tickers, limit=args.limit)
    
    print(f"\nData loaded:")
    print(f"  News: {len(news_items)}")
    print(f"  Anomalies: {len(anomalies)}")
    print(f"  Recommendations: {len(recommendations)}")
    
    # Ingest collections
    print("\n" + "=" * 60)
    print("Step 4: Ingest Collections")
    print("=" * 60)
    
    if news_items:
        ingest_news_collection(store, embedder, news_items, recreate=args.recreate)
    
    if anomalies:
        ingest_anomalies_collection(store, embedder, anomalies, recreate=args.recreate)
    
    if recommendations:
        ingest_recommendations_collection(store, embedder, recommendations, recreate=args.recreate)
    
    # Summary
    print("\n" + "=" * 60)
    print("Ingestion Complete!")
    print("=" * 60)
    
    collections = ['bvmt_news', 'bvmt_anomalies', 'bvmt_recommendations']
    for coll in collections:
        info = store.get_collection_info(coll)
        if info:
            print(f"\n{coll}:")
            print(f"  Documents: {info['points_count']}")
            print(f"  Vector size: {info['vector_size']}")
            print(f"  Distance: {info['distance']}")
    
    print("\n✅ Market memory ready for semantic search!")
    print("   Run: streamlit run dashboard/app.py")
    
    return 0


if __name__ == '__main__':
    exit(main())
